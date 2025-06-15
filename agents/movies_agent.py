import os
import requests
from typing import Dict, Any
from datetime import datetime

class MoviesAgent:
    """Agent for fetching information about movies and TV shows.
    
    This agent uses the OMDb API to get information about movies and TV shows
    based on the user's query.
    """
    
    def __init__(self):
        """Initialize the Movies agent with API key and endpoint."""
        # OMDb API requires an API key, but we'll handle the case where it's not available
        self.api_key = os.getenv("OMDB_API_KEY")
        self.api_url = "http://www.omdbapi.com/"
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data to get movie information.
        
        Args:
            input_data (dict): Input data containing the user's goal
            
        Returns:
            dict: Enriched data with movie information
        """
        print("Movies Agent: Fetching movie information...")
        
        # Create a copy of the input data to avoid modifying the original
        result = input_data.copy()
        
        try:
            # Extract search terms from the user's goal
            search_terms = self._extract_search_terms(input_data)
            
            # Get movie information for each search term
            movie_results = {}
            for term in search_terms:
                movie_info = self._search_movies(term)
                movie_results[term] = movie_info
            
            # Add movie data to result
            result["movie_data"] = {
                "results": movie_results,
                "search_terms": search_terms
            }
            
            print(f"Movies Agent: Found information for {len(movie_results)} terms")
        
        except Exception as e:
            result["movie_data"] = {"error": f"Failed to get movie data: {str(e)}"}
            print(f"Movies Agent: Error - {str(e)}")
        
        return result
    
    def _extract_search_terms(self, input_data: Dict[str, Any]) -> list:
        """Extract search terms from the input data.
        
        Args:
            input_data (dict): Input data containing the user's goal
            
        Returns:
            list: List of search terms
        """
        search_terms = []
        
        # Extract from the user's goal
        if "goal" in input_data:
            goal = input_data["goal"]
            
            # Check if the goal is related to movies or TV shows
            movie_keywords = [
                "movie", "film", "cinema", "actor", "actress", "director",
                "tv show", "television", "series", "episode", "season",
                "watch", "streaming", "netflix", "hulu", "amazon prime",
                "disney+", "hbo", "box office", "imdb", "rating", "review",
                "plot", "cast", "character", "genre", "award", "oscar", "emmy"
            ]
            
            # Check if any movie keyword is in the goal
            if any(keyword in goal.lower() for keyword in movie_keywords):
                # Extract potential movie titles (simple approach)
                import re
                
                # Look for quoted text as potential titles
                quoted_titles = re.findall(r'"([^"]+)"', goal)
                if quoted_titles:
                    search_terms.extend(quoted_titles)
                else:
                    # If no quoted titles, use the whole goal as a search term
                    # Remove common question words and movie-related terms
                    cleaned_goal = goal.lower()
                    for word in ["what", "when", "where", "who", "how", "why", "is", "are", "was", "were", "movie", "film", "show", "about"]:
                        cleaned_goal = cleaned_goal.replace(f" {word} ", " ")
                    
                    search_terms.append(cleaned_goal.strip())
        
        # Ensure we have at least one search term
        if not search_terms:
            search_terms.append("popular movies")
        
        return search_terms
    
    def _search_movies(self, query: str) -> Dict[str, Any]:
        """Search for movie information using the OMDb API.
        
        Args:
            query (str): Search query
            
        Returns:
            dict: Movie information
        """
        # If API key is not available, return mock data for testing
        if not self.api_key:
            print("Movies Agent: No API key available, using mock data")
            return self._get_mock_movie_data(query)
        
        params = {
            "s": query,  # Search by title
            "apikey": self.api_key,
            "type": "movie",  # Limit to movies
            "r": "json"  # Response format
        }
        
        # First, search for movies matching the query
        response = requests.get(self.api_url, params=params)
        response.raise_for_status()
        search_data = response.json()
        
        if search_data.get("Response") == "True" and "Search" in search_data:
            # Get the first (most relevant) result
            first_result = search_data["Search"][0]
            movie_id = first_result.get("imdbID")
            
            # Get detailed information for this movie
            detail_params = {
                "i": movie_id,  # IMDb ID
                "apikey": self.api_key,
                "plot": "full",  # Get full plot
                "r": "json"  # Response format
            }
            
            detail_response = requests.get(self.api_url, params=detail_params)
            detail_response.raise_for_status()
            movie_details = detail_response.json()
            
            if movie_details.get("Response") == "True":
                return {
                    "title": movie_details.get("Title"),
                    "year": movie_details.get("Year"),
                    "rated": movie_details.get("Rated"),
                    "released": movie_details.get("Released"),
                    "runtime": movie_details.get("Runtime"),
                    "genre": movie_details.get("Genre"),
                    "director": movie_details.get("Director"),
                    "actors": movie_details.get("Actors"),
                    "plot": movie_details.get("Plot"),
                    "awards": movie_details.get("Awards"),
                    "poster": movie_details.get("Poster"),
                    "ratings": movie_details.get("Ratings"),
                    "imdb_rating": movie_details.get("imdbRating"),
                    "box_office": movie_details.get("BoxOffice"),
                    "production": movie_details.get("Production"),
                    "website": movie_details.get("Website")
                }
        
        return {"error": f"No movie information found for '{query}'"}
    
    def _get_mock_movie_data(self, query: str) -> Dict[str, Any]:
        """Generate mock movie data for testing when API key is not available.
        
        Args:
            query (str): Search query
            
        Returns:
            dict: Mock movie data
        """
        # Return different mock data based on the query to simulate different searches
        if "popular" in query.lower():
            return {
                "title": "The Avengers",
                "year": "2012",
                "rated": "PG-13",
                "released": "04 May 2012",
                "runtime": "143 min",
                "genre": "Action, Adventure, Sci-Fi",
                "director": "Joss Whedon",
                "actors": "Robert Downey Jr., Chris Evans, Scarlett Johansson",
                "plot": "Earth's mightiest heroes must come together and learn to fight as a team if they are going to stop the mischievous Loki and his alien army from enslaving humanity.",
                "awards": "Nominated for 1 Oscar. 38 wins & 80 nominations total",
                "poster": "https://m.media-amazon.com/images/M/MV5BNDYxNjQyMjAtNTdiOS00NGYwLWFmNTAtNThmYjU5ZGI2YTI1XkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_SX300.jpg",
                "imdb_rating": "8.0",
                "box_office": "$623,357,910",
                "production": "Marvel Studios",
                "note": "This is mock data for testing purposes"
            }
        else:
            return {
                "title": f"Mock Movie: {query}",
                "year": "2023",
                "rated": "PG-13",
                "released": "01 Jan 2023",
                "runtime": "120 min",
                "genre": "Drama, Comedy",
                "director": "Mock Director",
                "actors": "Actor One, Actor Two, Actor Three",
                "plot": f"This is a mock plot for a movie about {query}. The story follows the main character as they navigate through various challenges and adventures.",
                "awards": "None",
                "poster": "https://example.com/mock-poster.jpg",
                "imdb_rating": "7.5",
                "box_office": "$100,000,000",
                "production": "Mock Studios",
                "note": "This is mock data for testing purposes"
            }