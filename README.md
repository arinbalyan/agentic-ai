# Multi-Agent AI System Using Google ADK

This project implements a multi-agent system using Google's Agent Development Kit (ADK) that processes user goals through a chain of specialized agents. Each agent enriches the output of the previous one until the goal is achieved.

## Overview

The system takes a user goal, creates a plan, then routes data between agents, with each agent enriching the output of the previous one. The agents decide the order of operations, pass results between each other, and iterate if the goal isn't met.

### Example Goals

```
"Find the next SpaceX launch, check weather at that location, then summarize if it may be delayed."
"What is the current price of Bitcoin?"
"Find a recipe for chocolate chip cookies."
"Tell me about the latest Marvel movie."
"What is quantum computing?"
```

## Architecture

The system consists of the following components:

1. **Planner Agent**: Parses user goals, creates execution plans, and determines which specialized agents to call and in what order.

2. **Enrichment Agents**:
   - **SpaceX Agent**: Fetches information about upcoming SpaceX launches using the SpaceX API.
   - **Weather Agent**: Gets weather data for launch locations using the OpenWeatherMap API.
   - **News Agent**: Retrieves relevant news articles using the NewsAPI.
   - **Wikipedia Agent**: Gets general knowledge information from Wikipedia.
   - **Movies Agent**: Gets information about movies and TV shows using the OMDB API.
   - **Crypto Agent**: Gets information about cryptocurrencies using the CoinGecko API.
   - **Recipe Agent**: Gets recipes and food information using the Spoonacular API.
   - **General QA Agent**: Handles general questions and knowledge queries using Google's Generative AI.
   - **Summary Agent**: Synthesizes information from all previous agents and provides a comprehensive response.

### Data Flow

1. User submits a goal
2. Planner Agent creates an execution plan
3. System routes between specialized agents according to the plan
4. Each agent processes and enriches the output of the previous agent
5. Summary Agent provides the final response
6. System evaluates if the goal is satisfied and refines if necessary

## Setup

### Prerequisites

- Python 3.8 or higher
- API keys for:
  - Google API (for Gemini models)
  - OpenWeatherMap API
  - NewsAPI
  - OMDB API (for movie information)
  - Spoonacular API (for recipe information)

### Installation

1. Clone the repository

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - `.env`
     ```
     GOOGLE_API_KEY=your_google_api_key
     OPENWEATHER_API_KEY=your_openweather_api_key
     NEWSAPI_API_KEY=your_newsapi_api_key
     OMDB_API_KEY=your_omdb_api_key
     SPOONACULAR_API_KEY=your_spoonacular_api_key
     ```

### Running the System

```
python main.py
```

## Evaluation

The system includes evaluation mechanisms to test goal satisfaction and agent trajectory:

1. **Goal Satisfaction**: The Planner Agent evaluates if the final result satisfies the original user goal.

2. **Agent Trajectory**: The system logs the execution path through different agents and the data enrichment at each step.

3. **Iterative Refinement**: If the goal isn't fully satisfied, the system can refine the result through additional processing.

You can run the evaluation script to test the system with predefined goals:

```
python evaluate.py
```

## APIs Used

1. **SpaceX API**: Provides information about SpaceX launches, including dates, locations, and mission details.
   - Documentation: https://github.com/r-spacex/SpaceX-API

2. **OpenWeatherMap API**: Provides weather data for specific locations.
   - Documentation: https://openweathermap.org/api

3. **NewsAPI**: Provides access to news articles from various sources.
   - Documentation: https://newsapi.org/

4. **Wikipedia API**: Provides access to Wikipedia articles and information.
   - Documentation: https://pypi.org/project/wikipedia/

5. **OMDB API**: Provides information about movies and TV shows.
   - Documentation: http://www.omdbapi.com/

6. **CoinGecko API**: Provides cryptocurrency market data.
   - Documentation: https://www.coingecko.com/api/documentation

7. **Spoonacular API**: Provides recipe and food information.
   - Documentation: https://spoonacular.com/food-api/docs

8. **Google Generative AI**: Provides natural language processing capabilities.
   - Documentation: https://ai.google.dev/

## Project Structure

```
.
├── .env                  # Environment variables (API keys)
├── .env.local           # Local environment variables (your API keys)
├── main.py              # Entry point for the application
├── evaluate.py          # Evaluation script for testing the system
├── requirements.txt     # Project dependencies
├── agents/              # Agent implementations
│   ├── planner_agent.py # Planner agent implementation
│   ├── spacex_agent.py  # SpaceX agent implementation
│   ├── weather_agent.py # Weather agent implementation
│   ├── news_agent.py    # News agent implementation
│   ├── wikipedia_agent.py # Wikipedia agent implementation
│   ├── movies_agent.py  # Movies agent implementation
│   ├── crypto_agent.py  # Cryptocurrency agent implementation
│   ├── recipe_agent.py  # Recipe agent implementation
│   ├── general_qa_agent.py # General QA agent implementation
│   └── summary_agent.py # Summary agent implementation
```

## Extending the System

To add new agents to the system:

1. Create a new agent class in the `agents/` directory
2. Implement the `process()` method that takes input data and returns enriched data
3. Add the new agent to the `agents` dictionary in the `MultiAgentSystem` class in `main.py`

## License

This project is licensed under the MIT License - see the LICENSE file for details.