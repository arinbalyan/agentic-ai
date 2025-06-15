import os
import google.generativeai as genai
from dotenv import load_dotenv

class GeneralQAAgent:
    """Agent for handling general questions and knowledge queries."""
    
    def __init__(self):
        """Initialize the General Q&A Agent with Google Generative AI."""
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        else:
            print("Warning: GOOGLE_API_KEY not found. GeneralQAAgent will use mock responses.")
            self.model = None
    
    def process(self, input_data):
        """Process the input data and return a response.
        
        Args:
            input_data (dict): The input data containing the user's goal and any other relevant information.
            
        Returns:
            dict: The response containing the answer to the general question.
        """
        goal = input_data.get("goal", "")
        question = self._extract_question(goal, input_data)
        
        if self.model:
            answer = self._get_answer_from_model(question)
        else:
            answer = self._generate_mock_answer(question)
        
        return {
            "general_qa": {
                "question": question,
                "answer": answer
            }
        }
    
    def _extract_question(self, goal, input_data):
        """Extract the main question from the goal and other input data.
        
        Args:
            goal (str): The user's goal or query.
            input_data (dict): Additional input data that might contain relevant information.
            
        Returns:
            str: The extracted question.
        """
        # For general Q&A, we can often use the goal directly as the question
        # But we can also check if there's more context from other agents
        question = goal
        
        # Add context from other agents if available
        context = ""
        
        if "spacex" in input_data:
            spacex_data = input_data["spacex"]
            if spacex_data.get("next_launch"):
                context += f"SpaceX context: {spacex_data['next_launch']['mission_name']} mission. "
        
        if "weather" in input_data:
            weather_data = input_data["weather"]
            if weather_data.get("forecast"):
                context += f"Weather context: {weather_data['forecast']}. "
        
        if "wikipedia" in input_data:
            wiki_data = input_data["wikipedia"]
            if wiki_data.get("summary"):
                context += f"Wikipedia context: {wiki_data['summary']}. "
        
        if context:
            question = f"{question}\n\nAdditional context: {context}"
        
        return question
    
    def _get_answer_from_model(self, question):
        """Get an answer from the Google Generative AI model.
        
        Args:
            question (str): The question to ask the model.
            
        Returns:
            str: The model's response.
        """
        try:
            response = self.model.generate_content(question)
            return response.text
        except Exception as e:
            print(f"Error getting response from model: {e}")
            return self._generate_mock_answer(question)
    
    def _generate_mock_answer(self, question):
        """Generate a mock answer when the model is not available.
        
        Args:
            question (str): The question that was asked.
            
        Returns:
            str: A mock answer.
        """
        return ("I'm sorry, I don't have access to the generative AI model right now. "
                "Please make sure your GOOGLE_API_KEY is set correctly in the .env file, "
                "or try again later.")