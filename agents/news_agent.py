import os
import requests
from typing import Dict, Any
from datetime import datetime, timedelta

class NewsAgent:
    """Agent for fetching relevant news articles.
    
    This agent uses the NewsAPI to get news articles related to space launches,
    weather events, and other relevant topics based on previous agent outputs.
    """
    
    def __init__(self):
        """Initialize the News agent with API key and endpoint."""
        self.api_key = os.getenv("NEWSAPI_API_KEY")
        self.api_url = "https://newsapi.org/v2"
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data to get relevant news articles.
        
        Args:
            input_data (dict): Input data containing SpaceX and weather information
            
        Returns:
            dict: Enriched data with relevant news articles
        """
        print("News Agent: Fetching relevant news articles...")
        
        # Create a copy of the input data to avoid modifying the original
        result = input_data.copy()
        
        try:
            # Generate search queries based on input data
            queries = self._generate_search_queries(input_data)
            
            # Get news articles for each query
            all_articles = []
            for query in queries:
                articles = self._search_news(query)
                all_articles.extend(articles)
            
            # Remove duplicates based on title
            unique_articles = []
            seen_titles = set()
            for article in all_articles:
                title = article.get("title")
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    unique_articles.append(article)
            
            # Sort by relevance (assuming more recent articles are more relevant)
            unique_articles.sort(key=lambda x: x.get("publishedAt", ""), reverse=True)
            
            # Limit to top 5 articles
            top_articles = unique_articles[:5]
            
            # Format articles for output
            formatted_articles = []
            for article in top_articles:
                formatted_articles.append({
                    "title": article.get("title"),
                    "source": article.get("source", {}).get("name"),
                    "published_at": article.get("publishedAt"),
                    "url": article.get("url"),
                    "description": article.get("description")
                })
            
            # Add news articles to result
            result["news_data"] = {
                "articles": formatted_articles,
                "query_terms": queries
            }
            
            print(f"News Agent: Found {len(formatted_articles)} relevant news articles")
        
        except Exception as e:
            result["news_data"] = {"error": f"Failed to get news data: {str(e)}"}
            print(f"News Agent: Error - {str(e)}")
        
        return result
    
    def _generate_search_queries(self, input_data: Dict[str, Any]) -> list:
        """Generate search queries based on input data.
        
        Args:
            input_data (dict): Input data containing SpaceX and weather information
            
        Returns:
            list: List of search queries
        """
        queries = []
        
        # Add SpaceX-related queries
        if "spacex_data" in input_data and "error" not in input_data["spacex_data"]:
            spacex_data = input_data["spacex_data"]
            mission_name = spacex_data.get("mission_name")
            launch_site = spacex_data.get("launch_site", {}).get("name")
            
            if mission_name and mission_name != "Unknown":
                queries.append(f"SpaceX {mission_name} launch")
            
            queries.append("SpaceX upcoming launch")
            
            if launch_site and launch_site != "Unknown":
                queries.append(f"SpaceX {launch_site}")
        
        # Add weather-related queries
        if "weather_data" in input_data and "error" not in input_data["weather_data"]:
            weather_data = input_data["weather_data"]
            weather_condition = weather_data.get("weather_condition")
            launch_assessment = weather_data.get("launch_assessment", {})
            
            if weather_condition:
                if "spacex_data" in input_data and "launch_site" in input_data["spacex_data"]:
                    location = input_data["spacex_data"]["launch_site"].get("location")
                    if location and location != "Unknown":
                        queries.append(f"{weather_condition} weather {location}")
            
            if not launch_assessment.get("favorable", True):
                queries.append("rocket launch weather delay")
        
        # Add general space-related queries
        queries.append("space launch conditions")
        
        return queries
    
    def _search_news(self, query: str) -> list:
        """Search for news articles using the NewsAPI.
        
        Args:
            query (str): Search query
            
        Returns:
            list: List of news articles
        """
        # Calculate date range (last 7 days)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        params = {
            "q": query,
            "from": start_date.strftime("%Y-%m-%d"),
            "to": end_date.strftime("%Y-%m-%d"),
            "language": "en",
            "sortBy": "relevancy",
            "apiKey": self.api_key
        }
        
        # If API key is not available, return mock data for testing
        if not self.api_key:
            print("News Agent: No API key available, using mock data")
            return self._get_mock_articles(query)
        
        response = requests.get(f"{self.api_url}/everything", params=params)
        response.raise_for_status()
        data = response.json()
        
        return data.get("articles", [])
    
    def _get_mock_articles(self, query: str) -> list:
        """Generate mock news articles for testing when API key is not available.
        
        Args:
            query (str): Search query
            
        Returns:
            list: List of mock news articles
        """
        current_time = datetime.utcnow().isoformat()
        
        return [
            {
                "source": {"id": "mock-source", "name": "Space News"},
                "author": "Mock Author",
                "title": f"Latest updates on {query}",
                "description": f"This is a mock article about {query} for testing purposes.",
                "url": "https://example.com/mock-article-1",
                "urlToImage": "https://example.com/mock-image-1.jpg",
                "publishedAt": current_time,
                "content": f"Detailed content about {query}..."
            },
            {
                "source": {"id": "mock-source", "name": "Launch Times"},
                "author": "Another Author",
                "title": f"Analysis: {query} implications",
                "description": f"A detailed analysis of {query} and its implications for future missions.",
                "url": "https://example.com/mock-article-2",
                "urlToImage": "https://example.com/mock-image-2.jpg",
                "publishedAt": current_time,
                "content": f"In-depth analysis of {query}..."
            }
        ]