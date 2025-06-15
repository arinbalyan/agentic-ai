import os
import json
from dotenv import load_dotenv
from langchain.agents import AgentExecutor
from langchain_core.messages import HumanMessage

# Import agents
from agents.planner_agent import PlannerAgent
from agents.spacex_agent import SpaceXAgent
from agents.weather_agent import WeatherAgent
from agents.news_agent import NewsAgent
from agents.summary_agent import SummaryAgent
from agents.wikipedia_agent import WikipediaAgent
from agents.movies_agent import MoviesAgent
from agents.crypto_agent import CryptoAgent
from agents.general_qa_agent import GeneralQAAgent
from agents.recipe_agent import RecipeAgent

# Load environment variables
load_dotenv()

class MultiAgentSystem:
    """Multi-agent system that processes user goals through a chain of specialized agents."""
    
    def __init__(self):
        """Initialize the multi-agent system with specialized agents."""
        self.planner_agent = PlannerAgent()
        self.spacex_agent = SpaceXAgent()
        self.weather_agent = WeatherAgent()
        self.news_agent = NewsAgent()
        self.summary_agent = SummaryAgent()
        self.wikipedia_agent = WikipediaAgent()
        self.movies_agent = MoviesAgent()
        self.crypto_agent = CryptoAgent()
        self.general_qa_agent = GeneralQAAgent()
        self.recipe_agent = RecipeAgent()
        
        # Map of available agents
        self.agents = {
            "spacex": self.spacex_agent,
            "weather": self.weather_agent,
            "news": self.news_agent,
            "wikipedia": self.wikipedia_agent,
            "movies": self.movies_agent,
            "crypto": self.crypto_agent,
            "general_qa": self.general_qa_agent,
            "recipe": self.recipe_agent,
            "summary": self.summary_agent
        }
    
    def process_goal(self, goal):
        """Process a user goal through the multi-agent system.
        
        Args:
            goal (str): The user's goal or query
            
        Returns:
            dict: The final result after processing through all relevant agents
        """
        # Step 1: Use planner agent to create a plan
        plan = self.planner_agent.create_plan(goal)
        print(f"\nPlan created: {json.dumps(plan, indent=2)}")
        
        # Step 2: Execute the plan by routing between agents
        current_result = {"goal": goal}
        
        for step in plan["steps"]:
            agent_name = step["agent"]
            if agent_name in self.agents:
                print(f"\nExecuting {agent_name} agent...")
                agent = self.agents[agent_name]
                current_result = agent.process(current_result)
                print(f"Result: {json.dumps(current_result, indent=2)}")
            else:
                print(f"Unknown agent: {agent_name}")
        
        # Step 3: Check if goal is satisfied, iterate if needed
        if not self.planner_agent.is_goal_satisfied(goal, current_result):
            print("\nGoal not fully satisfied. Refining result...")
            # Add refinement logic here if needed
            current_result = self.summary_agent.refine(current_result)
        
        return current_result

def main():
    """Main entry point for the application."""
    system = MultiAgentSystem()
    
    # Get user input for the goal
    print("Welcome to the Multi-Agent System!")
    print("You can ask questions about SpaceX launches, weather, news, general knowledge, movies, cryptocurrencies, and more.")
    print("Examples:")
    print("  - Find the next SpaceX launch and check the weather at that location")
    print("  - What is the current price of Bitcoin?")
    print("  - Tell me about the latest Marvel movie")
    print("  - What is quantum computing?")
    print("\nEnter your question or type 'exit' to quit:")
    
    while True:
        user_input = input("> ")
        
        if user_input.lower() in ["exit", "quit", "q"]:
            print("Goodbye!")
            break
        
        if not user_input.strip():
            print("Please enter a question or type 'exit' to quit.")
            continue
        
        goal = user_input
        
        print(f"\nProcessing goal: {goal}")
        result = system.process_goal(goal)
        
        print("\nFinal result:")
        print(json.dumps(result, indent=2))
        print("\nEnter another question or type 'exit' to quit:")

# For ADK web UI compatibility
def process_query(query):
    """Process a query for the ADK web UI."""
    system = MultiAgentSystem()
    result = system.process_goal(query)
    return result

if __name__ == "__main__":
    main()