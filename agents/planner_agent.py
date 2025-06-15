import os
from typing import Dict, List, Any
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

class PlannerAgent:
    """Agent responsible for planning the execution of user goals.
    
    This agent breaks down complex user goals into steps, determines which
    specialized agents to call and in what order, and evaluates if the goal
    has been satisfied.
    """
    
    def __init__(self):
        """Initialize the planner agent with a language model."""
        # Initialize language model
        self.llm = ChatGoogleGenerativeAI(model="gemma-3n-e4b-it")
        
        # Define planning prompt template
        self.planning_template = PromptTemplate.from_template(
            """You are a planning agent for a multi-agent system. Your job is to break down 
            user goals into steps that can be executed by specialized agents.
            
            Available agents:
            - spacex: Gets information about SpaceX launches
            - weather: Gets weather information for specific locations
            - news: Gets relevant news articles
            - wikipedia: Gets general knowledge information from Wikipedia
            - movies: Gets information about movies and TV shows
            - crypto: Gets information about cryptocurrencies
            - recipe: Gets recipes and food information
            - general_qa: Handles general questions and knowledge queries
            - summary: Synthesizes information and provides final output
            
            User goal: {goal}
            
            Create a plan with the following format:
            {{
                "goal": "The original user goal",
                "steps": [
                    {{
                        "agent": "Name of the agent to call",
                        "purpose": "What this agent should accomplish"
                    }},
                    ...
                ]
            }}
            
            Important: Only include agents that are relevant to the user's goal. Always include the summary agent as the final step.
            
            Return only the JSON plan without any additional text.
            """
        )
        
        # Define goal satisfaction prompt template
        self.goal_satisfaction_template = PromptTemplate.from_template(
            """You are evaluating whether a user's goal has been satisfied based on the 
            final result from a multi-agent system.
            
            User goal: {goal}
            
            Final result: {result}
            
            Has the goal been fully satisfied? Answer with only 'yes' or 'no'.
            """
        )
    
    def create_plan(self, goal: str) -> Dict[str, Any]:
        """Create a plan for executing a user goal.
        
        Args:
            goal (str): The user's goal or query
            
        Returns:
            dict: A plan with steps for executing the goal
        """
        # Format the planning prompt
        planning_prompt = self.planning_template.format(goal=goal)
        
        # Get response from language model
        response = self.llm.invoke([HumanMessage(content=planning_prompt)])
        
        # Parse the response as JSON
        try:
            # Extract JSON from the response
            response_text = response.content
            import json
            plan = json.loads(response_text)
            return plan
        except Exception as e:
            print(f"Error parsing plan: {e}")
            # Return a default plan if parsing fails
            # Determine which agents to include based on keywords in the goal
            default_steps = []
            
            # Check for keywords to determine relevant agents
            goal_lower = goal.lower()
            
            if any(keyword in goal_lower for keyword in ["spacex", "space", "rocket", "launch"]):
                default_steps.append({"agent": "spacex", "purpose": "Get SpaceX launch information"})
            
            if any(keyword in goal_lower for keyword in ["weather", "temperature", "forecast", "rain", "snow", "climate"]):
                default_steps.append({"agent": "weather", "purpose": "Get weather information"})
            
            if any(keyword in goal_lower for keyword in ["news", "article", "recent", "latest", "update"]):
                default_steps.append({"agent": "news", "purpose": "Get relevant news articles"})
            
            if any(keyword in goal_lower for keyword in ["what is", "who is", "when did", "where is", "why", "how", "information", "about", "explain", "definition"]):
                default_steps.append({"agent": "wikipedia", "purpose": "Get general knowledge information"})
            
            if any(keyword in goal_lower for keyword in ["movie", "film", "tv", "show", "actor", "actress", "director", "watch", "streaming"]):
                default_steps.append({"agent": "movies", "purpose": "Get movie or TV show information"})
            
            if any(keyword in goal_lower for keyword in ["crypto", "bitcoin", "ethereum", "coin", "blockchain", "price", "market"]):
                default_steps.append({"agent": "crypto", "purpose": "Get cryptocurrency information"})
            
            # Check for general knowledge questions
            general_qa_indicators = [
                "how", "why", "when", "where", "which", "can you", "could you", 
                "tell me", "explain", "describe", "what's", "whats", "help me understand"
            ]
            
            # If it's a general question, use general_qa
            if any(term in goal_lower for term in general_qa_indicators):
                default_steps.append({"agent": "general_qa", "purpose": "Answer general knowledge questions"})
            
            # If no specific agents were identified, use general_qa as a fallback
            if not default_steps:
                default_steps.append({"agent": "general_qa", "purpose": "Answer general knowledge questions"})
            
            # Always include summary agent as the final step
            default_steps.append({"agent": "summary", "purpose": "Synthesize information and provide final answer"})
            
            return {
                "goal": goal,
                "steps": default_steps
            }
    
    def is_goal_satisfied(self, goal: str, result: Dict[str, Any]) -> bool:
        """Check if the user's goal has been satisfied by the final result.
        
        Args:
            goal (str): The user's original goal
            result (dict): The final result after processing through agents
            
        Returns:
            bool: True if the goal is satisfied, False otherwise
        """
        # Format the goal satisfaction prompt
        satisfaction_prompt = self.goal_satisfaction_template.format(
            goal=goal,
            result=str(result)
        )
        
        # Get response from language model
        response = self.llm.invoke([HumanMessage(content=satisfaction_prompt)])
        
        # Check if the response indicates the goal is satisfied
        response_text = response.content.lower().strip()
        return response_text == "yes"