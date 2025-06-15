import os
import json
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain.prompts import PromptTemplate

class SummaryAgent:
    """Agent for synthesizing information and providing final output.
    
    This agent takes the outputs from all previous agents and creates a
    comprehensive summary that addresses the user's original goal.
    """
    
    def __init__(self):
        """Initialize the Summary agent with a language model."""
        # Initialize language model
        self.llm = ChatGoogleGenerativeAI(model="gemma-3n-e4b-it")
        
        # Define summary prompt template
        self.summary_template = PromptTemplate.from_template(
            """You are a summary agent for a multi-agent system. Your job is to synthesize 
            information from multiple specialized agents and provide a comprehensive response 
            to the user's original goal.
            
            User goal: {goal}
            
            SpaceX launch information:
            {spacex_info}
            
            Weather information:
            {weather_info}
            
            News information:
            {news_info}
            
            Based on all this information, provide a comprehensive summary that addresses 
            the user's goal. Focus on the most important and relevant information. If there 
            are any potential issues or concerns (like weather conditions that might delay 
            a launch), be sure to highlight them.
            
            Your summary should be well-structured, informative, and directly address the 
            user's goal.
            """
        )
        
        # Define refinement prompt template
        self.refinement_template = PromptTemplate.from_template(
            """You are refining a summary to better address the user's goal. The current 
            summary may be incomplete or may not fully address the user's goal.
            
            User goal: {goal}
            
            Current summary:
            {current_summary}
            
            All available information:
            {all_info}
            
            Please refine the summary to better address the user's goal. Make sure to 
            include any important information that might be missing and ensure that 
            the summary directly answers the user's query.
            """
        )
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data to create a comprehensive summary.
        
        Args:
            input_data (dict): Input data containing information from all previous agents
            
        Returns:
            dict: Result with added summary
        """
        print("Summary Agent: Creating comprehensive summary...")
        
        # Create a copy of the input data to avoid modifying the original
        result = input_data.copy()
        
        try:
            # Extract information from input data
            goal = input_data.get("goal", "")
            
            # Format SpaceX information
            spacex_info = "No SpaceX information available"
            if "spacex_data" in input_data and "error" not in input_data["spacex_data"]:
                spacex_data = input_data["spacex_data"]
                spacex_info = f"Mission: {spacex_data.get('mission_name', 'Unknown')}\n"
                spacex_info += f"Launch Date: {spacex_data.get('launch_date', 'Unknown')}\n"
                
                launch_site = spacex_data.get("launch_site", {})
                site_name = launch_site.get("name", "Unknown")
                site_location = launch_site.get("location", "Unknown")
                site_region = launch_site.get("region", "Unknown")
                
                spacex_info += f"Launch Site: {site_name}, {site_location}, {site_region}\n"
                spacex_info += f"Details: {spacex_data.get('details', 'No details available')}"
            
            # Format Weather information
            weather_info = "No weather information available"
            if "weather_data" in input_data and "error" not in input_data["weather_data"]:
                weather_data = input_data["weather_data"]
                weather_type = weather_data.get("type", "")
                
                if weather_type == "current":
                    weather_info = "Current Weather:\n"
                    weather_info += f"Temperature: {weather_data.get('temperature')}°C\n"
                    weather_info += f"Condition: {weather_data.get('weather_condition', 'Unknown')} - {weather_data.get('weather_description', '')}\n"
                    weather_info += f"Wind Speed: {weather_data.get('wind_speed')} m/s\n"
                    weather_info += f"Humidity: {weather_data.get('humidity')}%\n"
                else:  # forecast
                    weather_info = f"Weather Forecast for {weather_data.get('forecast_date', 'upcoming launch')}:\n"
                    weather_info += f"Average Temperature: {weather_data.get('avg_temperature')}°C\n"
                    weather_info += f"Weather Condition: {weather_data.get('weather_condition', 'Unknown')}\n"
                    weather_info += f"Maximum Wind Speed: {weather_data.get('max_wind_speed')} m/s\n"
                
                # Add launch assessment
                launch_assessment = weather_data.get("launch_assessment", {})
                weather_info += "\nLaunch Conditions Assessment:\n"
                weather_info += f"Favorable: {launch_assessment.get('favorable', False)}\n"
                
                concerns = launch_assessment.get("concerns", [])
                if concerns:
                    weather_info += "Concerns:\n"
                    for concern in concerns:
                        weather_info += f"- {concern}\n"
                
                weather_info += f"Summary: {launch_assessment.get('summary', '')}"
            
            # Format News information
            news_info = "No relevant news articles available"
            if "news_data" in input_data and "error" not in input_data["news_data"]:
                news_data = input_data["news_data"]
                articles = news_data.get("articles", [])
                
                if articles:
                    news_info = "Relevant News Articles:\n"
                    for i, article in enumerate(articles, 1):
                        news_info += f"{i}. {article.get('title')}\n"
                        news_info += f"   Source: {article.get('source')}\n"
                        news_info += f"   Published: {article.get('published_at')}\n"
                        news_info += f"   Description: {article.get('description')}\n\n"
            
            # Generate summary using language model
            summary_prompt = self.summary_template.format(
                goal=goal,
                spacex_info=spacex_info,
                weather_info=weather_info,
                news_info=news_info
            )
            
            response = self.llm.invoke([HumanMessage(content=summary_prompt)])
            summary = response.content
            
            # Add summary to result
            result["summary"] = summary
            
            print("Summary Agent: Comprehensive summary created")
        
        except Exception as e:
            result["summary"] = f"Failed to create summary: {str(e)}"
            print(f"Summary Agent: Error - {str(e)}")
        
        return result
    
    def refine(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Refine the current summary to better address the user's goal.
        
        Args:
            input_data (dict): Input data containing the current summary and all information
            
        Returns:
            dict: Result with refined summary
        """
        print("Summary Agent: Refining summary...")
        
        # Create a copy of the input data to avoid modifying the original
        result = input_data.copy()
        
        try:
            # Extract information from input data
            goal = input_data.get("goal", "")
            current_summary = input_data.get("summary", "")
            
            # Combine all information for context
            all_info = json.dumps(input_data, indent=2)
            
            # Generate refined summary using language model
            refinement_prompt = self.refinement_template.format(
                goal=goal,
                current_summary=current_summary,
                all_info=all_info
            )
            
            response = self.llm.invoke([HumanMessage(content=refinement_prompt)])
            refined_summary = response.content
            
            # Update summary in result
            result["summary"] = refined_summary
            result["refined"] = True
            
            print("Summary Agent: Summary refined")
        
        except Exception as e:
            result["refinement_error"] = f"Failed to refine summary: {str(e)}"
            print(f"Summary Agent: Refinement error - {str(e)}")
        
        return result