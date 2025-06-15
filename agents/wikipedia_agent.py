import os
import wikipedia
from typing import Dict, Any

class WikipediaAgent:
    """Agent for fetching information from Wikipedia.
    
    This agent uses the Wikipedia API to get general knowledge information
    on various topics based on the user's query.
    """
    
    def __init__(self):
        """Initialize the Wikipedia agent."""
        # Set language to English
        wikipedia.set_lang("en")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data to get Wikipedia information.
        
        Args:
            input_data (dict): Input data containing the user's goal
            
        Returns:
            dict: Enriched data with Wikipedia information
        """
        print("Wikipedia Agent: Fetching information...")
        
        # Create a copy of the input data to avoid modifying the original
        result = input_data.copy()
        
        try:
            # Extract search terms from the user's goal
            search_terms = self._extract_search_terms(input_data)
            
            # Get Wikipedia information for each search term
            wiki_results = {}
            for term in search_terms:
                try:
                    # Search for the term
                    search_results = wikipedia.search(term, results=3)
                    
                    if search_results:
                        # Get the most relevant page
                        page_title = search_results[0]
                        
                        # Get the page summary
                        summary = wikipedia.summary(page_title, sentences=5)
                        
                        # Get the page URL
                        page = wikipedia.page(page_title)
                        url = page.url
                        
                        wiki_results[term] = {
                            "title": page_title,
                            "summary": summary,
                            "url": url
                        }
                    else:
                        wiki_results[term] = {
                            "error": f"No Wikipedia results found for '{term}'"
                        }
                except wikipedia.exceptions.DisambiguationError as e:
                    # If there are multiple matches, use the first option
                    try:
                        page_title = e.options[0]
                        summary = wikipedia.summary(page_title, sentences=5)
                        page = wikipedia.page(page_title)
                        url = page.url
                        
                        wiki_results[term] = {
                            "title": page_title,
                            "summary": summary,
                            "url": url,
                            "note": f"Disambiguation: selected '{page_title}' from multiple options"
                        }
                    except Exception as inner_e:
                        wiki_results[term] = {
                            "error": f"Disambiguation error for '{term}': {str(inner_e)}"
                        }
                except Exception as e:
                    wiki_results[term] = {
                        "error": f"Error fetching Wikipedia data for '{term}': {str(e)}"
                    }
            
            # Add Wikipedia data to result
            result["wikipedia_data"] = {
                "results": wiki_results,
                "search_terms": search_terms
            }
            
            print(f"Wikipedia Agent: Found information for {len(wiki_results)} terms")
        
        except Exception as e:
            result["wikipedia_data"] = {"error": f"Failed to get Wikipedia data: {str(e)}"}
            print(f"Wikipedia Agent: Error - {str(e)}")
        
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
            
            # Simple keyword extraction (can be improved with NLP)
            # Remove common words and punctuation
            import re
            from collections import Counter
            
            # Convert to lowercase and split into words
            words = re.findall(r'\b\w+\b', goal.lower())
            
            # Remove common stop words
            stop_words = {
                'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what',
                'when', 'where', 'how', 'why', 'which', 'who', 'whom', 'this', 'that',
                'these', 'those', 'then', 'just', 'so', 'than', 'such', 'both', 'through',
                'about', 'for', 'is', 'of', 'while', 'during', 'to', 'from', 'in', 'out',
                'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
                'there', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
                'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
                'too', 'very', 's', 't', 'can', 'will', 'don', 'should', 'now', 'find',
                'get', 'make', 'know', 'take', 'see', 'come', 'go', 'do', 'be', 'have',
                'may', 'would', 'could', 'should', 'shall', 'might', 'must', 'need',
                'try', 'want', 'use', 'work', 'seem', 'like', 'ask', 'show', 'tell'
            }
            
            filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
            
            # Count word frequency
            word_counts = Counter(filtered_words)
            
            # Get the most common words (up to 3)
            common_words = [word for word, count in word_counts.most_common(3)]
            
            # Add individual common words as search terms
            search_terms.extend(common_words)
            
            # Also add the full goal as a search term if it's not too long
            if len(goal.split()) <= 6:
                search_terms.append(goal)
        
        # If we have data from other agents, extract relevant terms
        if "spacex_data" in input_data and "error" not in input_data.get("spacex_data", {}):
            spacex_data = input_data["spacex_data"]
            mission_name = spacex_data.get("mission_name")
            if mission_name and mission_name != "Unknown":
                search_terms.append(mission_name)
        
        # Ensure we have at least one search term
        if not search_terms:
            search_terms.append("general knowledge")
        
        return search_terms