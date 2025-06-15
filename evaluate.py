import json
import os
from datetime import datetime
from main import MultiAgentSystem

def evaluate_system():
    """Evaluate the multi-agent system with a set of predefined goals."""
    system = MultiAgentSystem()
    
    # Define test goals covering all agents
    test_goals = [
        # SpaceX and Weather Agent goals
        "Find the next SpaceX launch and check the weather at the launch site.",
        "When is the next SpaceX launch and will the weather be good for launch?",
        
        # News Agent goals
        "Find the latest news about SpaceX launches.",
        "What are the recent news articles about artificial intelligence?",
        
        # Wikipedia Agent goals
        "What is quantum computing?",
        "Tell me about the history of space exploration.",
        
        # Movies Agent goals
        "What is the latest Marvel movie?",
        "Tell me about the movie Inception.",
        
        # Crypto Agent goals
        "What is the current price of Bitcoin?",
        "How has Ethereum performed over the last week?",
        
        # Recipe Agent goals
        "Find a recipe for chocolate chip cookies.",
        "What are some easy dinner recipes?",
        
        # General QA Agent goals
        "What is the capital of France?",
        "How does photosynthesis work?",
        
        # Complex multi-agent goals
        "Find the next SpaceX launch, check weather at that location, then summarize if it may be delayed.",
        "Tell me about Bitcoin and summarize recent news about cryptocurrency."
    ]
    
    results = []
    
    for goal in test_goals:
        print(f"\nEvaluating goal: {goal}")
        try:
            # Process the goal
            response = system.process_goal(goal)
            
            # Record the result
            result = {
                "goal": goal,
                "response": response,
                "agent_trajectory": system.agent_trajectory,
                "success": True  # Assuming success if no exception
            }
        except Exception as e:
            # Record failure
            result = {
                "goal": goal,
                "error": str(e),
                "agent_trajectory": system.agent_trajectory if hasattr(system, "agent_trajectory") else [],
                "success": False
            }
            print(f"Error processing goal: {e}")
        
        results.append(result)
        print(f"Agent trajectory: {system.agent_trajectory}")
        print(f"Response: {response if 'response' in locals() else 'Failed'}")
    
    # Save results to a file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"evaluation_results_{timestamp}.json"
    
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nEvaluation complete. Results saved to {results_file}")
    
    # Calculate success rate
    success_count = sum(1 for result in results if result["success"])
    success_rate = (success_count / len(results)) * 100
    print(f"Success rate: {success_rate:.2f}% ({success_count}/{len(results)})")
    
    return results

def analyze_results(results):
    """Analyze the evaluation results to identify patterns and issues."""
    # Count goals by agent type
    agent_counts = {}
    for result in results:
        if "agent_trajectory" in result:
            for agent in result["agent_trajectory"]:
                if agent not in agent_counts:
                    agent_counts[agent] = 0
                agent_counts[agent] += 1
    
    print("\nAgent usage statistics:")
    for agent, count in agent_counts.items():
        print(f"{agent}: {count} times")
    
    # Identify common failure patterns
    if any(not result["success"] for result in results):
        print("\nFailure analysis:")
        for result in results:
            if not result["success"]:
                print(f"Goal: {result['goal']}")
                print(f"Error: {result['error']}")
                print(f"Agent trajectory: {result['agent_trajectory']}")
                print("---")

if __name__ == "__main__":
    results = evaluate_system()
    analyze_results(results)