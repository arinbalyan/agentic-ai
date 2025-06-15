import os
import requests
from typing import Dict, Any
from datetime import datetime, timedelta

class WeatherAgent:
    """Agent for fetching weather information for specific locations.
    
    This agent uses the OpenWeatherMap API to get weather forecasts for
    locations, particularly for SpaceX launch sites.
    """
    
    def __init__(self):
        """Initialize the Weather agent with API key and endpoint."""
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.api_url = "https://api.openweathermap.org/data/2.5"
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data to get weather information for a location.
        
        Args:
            input_data (dict): Input data containing SpaceX launch information
            
        Returns:
            dict: Enriched data with weather information
        """
        print("Weather Agent: Fetching weather information...")
        
        # Create a copy of the input data to avoid modifying the original
        result = input_data.copy()
        
        # Check if we have SpaceX data with launch site coordinates
        if "spacex_data" not in result or "error" in result["spacex_data"]:
            result["weather_data"] = {"error": "No SpaceX launch data available"}
            print("Weather Agent: No SpaceX launch data available")
            return result
        
        try:
            # Get launch site coordinates
            launch_site = result["spacex_data"]["launch_site"]
            latitude = launch_site.get("latitude")
            longitude = launch_site.get("longitude")
            
            if not latitude or not longitude:
                result["weather_data"] = {"error": "Launch site coordinates not available"}
                print("Weather Agent: Launch site coordinates not available")
                return result
            
            # Get launch date
            launch_date_str = result["spacex_data"].get("launch_date", "")
            
            # Determine if we need current weather or forecast
            if launch_date_str and launch_date_str != "Unknown":
                try:
                    launch_date = datetime.strptime(launch_date_str, "%Y-%m-%d %H:%M:%S UTC")
                    current_date = datetime.utcnow()
                    days_until_launch = (launch_date - current_date).days
                    
                    # If launch is within 5 days, get forecast, otherwise get current weather
                    if 0 <= days_until_launch <= 5:
                        weather_data = self._get_forecast(latitude, longitude, days_until_launch)
                    else:
                        weather_data = self._get_current_weather(latitude, longitude)
                        weather_data["note"] = "Launch date is more than 5 days away, showing current weather only"
                except ValueError:
                    # If date parsing fails, get current weather
                    weather_data = self._get_current_weather(latitude, longitude)
                    weather_data["note"] = "Could not parse launch date, showing current weather only"
            else:
                # If no launch date, get current weather
                weather_data = self._get_current_weather(latitude, longitude)
                weather_data["note"] = "No launch date available, showing current weather only"
            
            # Add weather information to result
            result["weather_data"] = weather_data
            
            # Add weather assessment for launch
            result["weather_data"]["launch_assessment"] = self._assess_launch_conditions(weather_data)
            
            print(f"Weather Agent: Weather data retrieved for {launch_site.get('name', 'launch site')}")
        
        except Exception as e:
            result["weather_data"] = {"error": f"Failed to get weather data: {str(e)}"}
            print(f"Weather Agent: Error - {str(e)}")
        
        return result
    
    def _get_current_weather(self, latitude: float, longitude: float) -> dict:
        """Get current weather for a location.
        
        Args:
            latitude (float): Latitude of the location
            longitude (float): Longitude of the location
            
        Returns:
            dict: Current weather information
        """
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": self.api_key,
            "units": "metric"
        }
        
        response = requests.get(f"{self.api_url}/weather", params=params)
        response.raise_for_status()
        data = response.json()
        
        return {
            "type": "current",
            "temperature": data.get("main", {}).get("temp"),
            "feels_like": data.get("main", {}).get("feels_like"),
            "humidity": data.get("main", {}).get("humidity"),
            "pressure": data.get("main", {}).get("pressure"),
            "wind_speed": data.get("wind", {}).get("speed"),
            "wind_direction": data.get("wind", {}).get("deg"),
            "weather_condition": data.get("weather", [{}])[0].get("main"),
            "weather_description": data.get("weather", [{}])[0].get("description"),
            "clouds": data.get("clouds", {}).get("all"),
            "visibility": data.get("visibility"),
            "timestamp": datetime.utcfromtimestamp(data.get("dt", 0)).strftime("%Y-%m-%d %H:%M:%S UTC")
        }
    
    def _get_forecast(self, latitude: float, longitude: float, days_ahead: int) -> dict:
        """Get weather forecast for a location.
        
        Args:
            latitude (float): Latitude of the location
            longitude (float): Longitude of the location
            days_ahead (int): Number of days ahead to forecast
            
        Returns:
            dict: Weather forecast information
        """
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": self.api_key,
            "units": "metric"
        }
        
        response = requests.get(f"{self.api_url}/forecast", params=params)
        response.raise_for_status()
        data = response.json()
        
        # Calculate target date (days_ahead from now)
        target_date = datetime.utcnow() + timedelta(days=days_ahead)
        target_date_str = target_date.strftime("%Y-%m-%d")
        
        # Find forecast entries for the target date
        target_forecasts = []
        for item in data.get("list", []):
            forecast_time = datetime.utcfromtimestamp(item.get("dt", 0))
            if forecast_time.strftime("%Y-%m-%d") == target_date_str:
                target_forecasts.append(item)
        
        if not target_forecasts:
            return {"error": f"No forecast available for {days_ahead} days ahead"}
        
        # Aggregate forecast data for the target date
        temps = [item.get("main", {}).get("temp", 0) for item in target_forecasts]
        avg_temp = sum(temps) / len(temps) if temps else None
        
        wind_speeds = [item.get("wind", {}).get("speed", 0) for item in target_forecasts]
        max_wind = max(wind_speeds) if wind_speeds else None
        
        # Get the most common weather condition
        weather_conditions = [item.get("weather", [{}])[0].get("main") for item in target_forecasts]
        weather_condition = max(set(weather_conditions), key=weather_conditions.count) if weather_conditions else None
        
        return {
            "type": "forecast",
            "forecast_date": target_date_str,
            "days_ahead": days_ahead,
            "avg_temperature": avg_temp,
            "max_wind_speed": max_wind,
            "weather_condition": weather_condition,
            "forecast_entries": len(target_forecasts),
            "detailed_forecast": [
                {
                    "time": datetime.utcfromtimestamp(item.get("dt", 0)).strftime("%H:%M UTC"),
                    "temperature": item.get("main", {}).get("temp"),
                    "weather_condition": item.get("weather", [{}])[0].get("main"),
                    "weather_description": item.get("weather", [{}])[0].get("description"),
                    "wind_speed": item.get("wind", {}).get("speed"),
                    "clouds": item.get("clouds", {}).get("all"),
                    "precipitation_probability": item.get("pop", 0) * 100
                }
                for item in target_forecasts[:3]  # Include only first 3 entries for brevity
            ]
        }
    
    def _assess_launch_conditions(self, weather_data: dict) -> dict:
        """Assess weather conditions for a rocket launch.
        
        Args:
            weather_data (dict): Weather data for the launch site
            
        Returns:
            dict: Assessment of launch conditions
        """
        # Initialize assessment
        assessment = {
            "favorable": True,
            "concerns": [],
            "summary": ""
        }
        
        # Check for error in weather data
        if "error" in weather_data:
            assessment["favorable"] = False
            assessment["concerns"].append("Weather data unavailable")
            assessment["summary"] = "Cannot assess launch conditions due to unavailable weather data"
            return assessment
        
        # Extract relevant weather parameters
        weather_type = weather_data.get("type")
        
        if weather_type == "current":
            wind_speed = weather_data.get("wind_speed")
            weather_condition = weather_data.get("weather_condition")
            visibility = weather_data.get("visibility")
        else:  # forecast
            wind_speed = weather_data.get("max_wind_speed")
            weather_condition = weather_data.get("weather_condition")
            visibility = None  # Forecast doesn't typically include visibility
        
        # Check wind conditions (> 30 km/h or ~8.3 m/s is concerning)
        if wind_speed and wind_speed > 8.3:
            assessment["favorable"] = False
            assessment["concerns"].append(f"High winds ({wind_speed} m/s)")
        
        # Check weather conditions
        unfavorable_conditions = ["Thunderstorm", "Rain", "Snow", "Tornado", "Hurricane", "Storm"]
        if weather_condition and any(cond.lower() in weather_condition.lower() for cond in unfavorable_conditions):
            assessment["favorable"] = False
            assessment["concerns"].append(f"Unfavorable weather condition: {weather_condition}")
        
        # Check visibility (< 10km is concerning)
        if visibility and visibility < 10000:
            assessment["favorable"] = False
            assessment["concerns"].append(f"Low visibility ({visibility/1000} km)")
        
        # Generate summary
        if assessment["favorable"]:
            assessment["summary"] = "Weather conditions appear favorable for launch"
        else:
            concerns_text = ", ".join(assessment["concerns"])
            assessment["summary"] = f"Weather conditions may cause launch delays: {concerns_text}"
        
        return assessment