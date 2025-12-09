import os
from typing import Type, TypeVar
from google import genai
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class GeminiClient:
    """LLM client for Google Gemini models."""
    
    def __init__(
        self, 
        model: str = 'gemini-2.5-flash',
        api_key: str | None = None
    ):
        """
        Initialize the Gemini client.
        
        Args:
            model: The model to use (default: 'gemini-2.5-flash')
            api_key: Gemini API key (optional, uses GEMINI_API_KEY environment variable if not provided)
        """
        self.model = model
        
        # Get the API key from parameter or environment
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "Gemini API key not provided. Set GEMINI_API_KEY environment variable."
            )
        
        self.client = genai.Client(api_key=self.api_key)
    
    def generate(self, prompt: str, output_class: Type[T]) -> T:
        """
        Generate a structured response from the LLM.
        
        Args:
            prompt: The input text prompt for the LLM
            output_class: The Pydantic model class to structure the output
            
        Returns:
            An instance of the output_class with the LLM's structured response
        """
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": output_class.model_json_schema(),
            },
        )
        
        if not response.text:
            raise ValueError("No response received from the model")
        
        return output_class.model_validate_json(response.text)

