import os
import requests
import json
import random
from dotenv import load_dotenv

class RecipeAgent:
    """Agent for fetching recipe and food information."""
    
    def __init__(self):
        """Initialize the Recipe Agent with Spoonacular API."""
        load_dotenv()
        self.api_key = os.getenv("SPOONACULAR_API_KEY")
        self.base_url = "https://api.spoonacular.com"
        
        if not self.api_key:
            print("Warning: SPOONACULAR_API_KEY not found. RecipeAgent will use mock data.")
    
    def process(self, input_data):
        """Process the input data and return recipe information.
        
        Args:
            input_data (dict): The input data containing the user's goal and any other relevant information.
            
        Returns:
            dict: The recipe information.
        """
        goal = input_data.get("goal", "")
        search_terms = self._extract_search_terms(goal, input_data)
        
        if self.api_key:
            recipe_data = self._search_recipes(search_terms)
        else:
            recipe_data = self._generate_mock_recipe_data(search_terms)
        
        return {
            "recipe": recipe_data
        }
    
    def _extract_search_terms(self, goal, input_data):
        """Extract search terms from the goal and input data.
        
        Args:
            goal (str): The user's goal or query.
            input_data (dict): Additional input data that might contain relevant information.
            
        Returns:
            str: The search terms for recipe search.
        """
        goal_lower = goal.lower()
        
        # Common food-related keywords to look for
        food_keywords = [
            "recipe", "food", "meal", "dish", "cook", "bake", "breakfast", 
            "lunch", "dinner", "dessert", "snack", "appetizer", "cuisine",
            "vegetarian", "vegan", "gluten-free", "keto", "paleo", "low-carb"
        ]
        
        # Check if any food keywords are in the goal
        food_related = any(keyword in goal_lower for keyword in food_keywords)
        
        if food_related:
            # Remove common question phrases to get the core search terms
            search_terms = goal_lower
            for phrase in ["how to make", "how do i make", "recipe for", "how to cook", 
                          "tell me about", "what is", "find me", "i want", "can you give me"]:
                search_terms = search_terms.replace(phrase, "")
            
            # Clean up the search terms
            search_terms = search_terms.strip()
            return search_terms
        else:
            # If no food keywords found, use a generic term based on the goal
            return goal
    
    def _search_recipes(self, query):
        """Search for recipes using the Spoonacular API.
        
        Args:
            query (str): The search query.
            
        Returns:
            dict: The recipe data.
        """
        try:
            # Search for recipes
            search_endpoint = f"{self.base_url}/recipes/complexSearch"
            params = {
                "apiKey": self.api_key,
                "query": query,
                "number": 3,  # Limit to 3 recipes
                "addRecipeInformation": True,
                "fillIngredients": True
            }
            
            response = requests.get(search_endpoint, params=params)
            response.raise_for_status()
            search_data = response.json()
            
            recipes = []
            for recipe in search_data.get("results", []):
                recipe_info = {
                    "id": recipe.get("id"),
                    "title": recipe.get("title"),
                    "image": recipe.get("image"),
                    "readyInMinutes": recipe.get("readyInMinutes"),
                    "servings": recipe.get("servings"),
                    "summary": recipe.get("summary"),
                    "sourceUrl": recipe.get("sourceUrl"),
                    "ingredients": []
                }
                
                # Extract ingredients
                for ingredient in recipe.get("extendedIngredients", []):
                    recipe_info["ingredients"].append({
                        "name": ingredient.get("name"),
                        "amount": ingredient.get("amount"),
                        "unit": ingredient.get("unit")
                    })
                
                # Get recipe instructions
                if recipe.get("analyzedInstructions"):
                    steps = []
                    for instruction in recipe["analyzedInstructions"]:
                        for step in instruction.get("steps", []):
                            steps.append(step.get("step"))
                    recipe_info["instructions"] = steps
                
                recipes.append(recipe_info)
            
            return {
                "query": query,
                "recipes": recipes
            }
            
        except Exception as e:
            print(f"Error searching recipes: {e}")
            return self._generate_mock_recipe_data(query)
    
    def _generate_mock_recipe_data(self, query):
        """Generate mock recipe data when the API is not available.
        
        Args:
            query (str): The search query.
            
        Returns:
            dict: Mock recipe data.
        """
        mock_recipes = [
            {
                "id": 1,
                "title": f"Mock {query.title()} Recipe",
                "image": "https://spoonacular.com/recipeImages/mock-image.jpg",
                "readyInMinutes": random.randint(15, 60),
                "servings": random.randint(2, 6),
                "summary": f"A delicious {query} recipe that's perfect for any occasion. This is mock data as the Spoonacular API key is not available.",
                "sourceUrl": "https://example.com/mock-recipe",
                "ingredients": [
                    {"name": "ingredient 1", "amount": 2, "unit": "cups"},
                    {"name": "ingredient 2", "amount": 1, "unit": "tablespoon"},
                    {"name": "ingredient 3", "amount": 3, "unit": "ounces"}
                ],
                "instructions": [
                    "Step 1: Prepare the ingredients.",
                    "Step 2: Mix everything together.",
                    "Step 3: Cook until done.",
                    "Step 4: Serve and enjoy!"
                ]
            },
            {
                "id": 2,
                "title": f"Easy {query.title()}",
                "image": "https://spoonacular.com/recipeImages/mock-image-2.jpg",
                "readyInMinutes": random.randint(15, 60),
                "servings": random.randint(2, 6),
                "summary": f"A quick and easy {query} that anyone can make. This is mock data as the Spoonacular API key is not available.",
                "sourceUrl": "https://example.com/mock-recipe-2",
                "ingredients": [
                    {"name": "ingredient A", "amount": 1, "unit": "cup"},
                    {"name": "ingredient B", "amount": 2, "unit": "teaspoons"},
                    {"name": "ingredient C", "amount": 4, "unit": "ounces"}
                ],
                "instructions": [
                    "Step 1: Gather all ingredients.",
                    "Step 2: Combine in a bowl.",
                    "Step 3: Cook according to preference.",
                    "Step 4: Garnish and serve."
                ]
            }
        ]
        
        return {
            "query": query,
            "recipes": mock_recipes,
            "note": "This is mock data. To get real recipe information, please add your Spoonacular API key to the .env file."
        }