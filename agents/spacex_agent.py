import os
import requests
from typing import Dict, Any
from datetime import datetime

class SpaceXAgent:
    """Agent for fetching information about SpaceX launches.
    
    This agent uses the SpaceX API to get information about upcoming launches,
    including launch dates, locations, and mission details.
    """
    
    def __init__(self):
        """Initialize the SpaceX agent with API endpoints."""
        self.api_url = "https://api.spacexdata.com/v4"
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data to get SpaceX launch information.
        
        Args:
            input_data (dict): Input data containing the user goal and any previous results
            
        Returns:
            dict: Enriched data with SpaceX launch information
        """
        print("SpaceX Agent: Fetching next launch information...")
        
        # Create a copy of the input data to avoid modifying the original
        result = input_data.copy()
        
        try:
            # Get upcoming launches
            launches = self._get_upcoming_launches()
            
            if launches and len(launches) > 0:
                # Get the next launch (first in the list)
                next_launch = launches[0]
                
                # Get launch pad information
                launchpad_id = next_launch.get("launchpad")
                launchpad = self._get_launchpad(launchpad_id) if launchpad_id else {}
                
                # Format launch date
                launch_date = next_launch.get("date_utc")
                if launch_date:
                    date_obj = datetime.fromisoformat(launch_date.replace("Z", "+00:00"))
                    formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S UTC")
                else:
                    formatted_date = "Unknown"
                
                # Add launch information to result
                result["spacex_data"] = {
                    "mission_name": next_launch.get("name", "Unknown"),
                    "launch_date": formatted_date,
                    "launch_site": {
                        "name": launchpad.get("name", "Unknown"),
                        "location": launchpad.get("locality", "Unknown"),
                        "region": launchpad.get("region", "Unknown"),
                        "latitude": launchpad.get("latitude"),
                        "longitude": launchpad.get("longitude")
                    },
                    "rocket": next_launch.get("rocket", "Unknown"),
                    "details": next_launch.get("details", "No details available"),
                    "flight_number": next_launch.get("flight_number")
                }
                
                print(f"SpaceX Agent: Found next launch: {result['spacex_data']['mission_name']}")
            else:
                result["spacex_data"] = {"error": "No upcoming launches found"}
                print("SpaceX Agent: No upcoming launches found")
        
        except Exception as e:
            result["spacex_data"] = {"error": f"Failed to get SpaceX data: {str(e)}"}
            print(f"SpaceX Agent: Error - {str(e)}")
        
        return result
    
    def _get_upcoming_launches(self) -> list:
        """Get a list of upcoming SpaceX launches.
        
        Returns:
            list: List of upcoming launches sorted by date
        """
        response = requests.get(f"{self.api_url}/launches/upcoming")
        response.raise_for_status()
        launches = response.json()
        
        # Sort launches by date
        launches.sort(key=lambda x: x.get("date_utc", ""))
        
        return launches
    
    def _get_launchpad(self, launchpad_id: str) -> dict:
        """Get information about a specific launch pad.
        
        Args:
            launchpad_id (str): ID of the launch pad
            
        Returns:
            dict: Launch pad information
        """
        response = requests.get(f"{self.api_url}/launchpads/{launchpad_id}")
        response.raise_for_status()
        return response.json()