import os
from typing import Type, TypeVar
from openai import OpenAI
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class OpenAIClient:
    """LLM client for OpenAI models."""
    
    def __init__(
        self, 
        model: str = 'gpt-5-nano',
        api_key: str | None = None
    ):
        """
        Initialize the OpenAI client.
        
        Args:
            model: The model to use (default: 'gpt-5-nano')
            api_key: OpenAI API key (optional, uses OPENAI_API_KEY environment variable if not provided)
        """
        self.model = model
        
        # Get the API key from parameter or environment
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment variable."
            )
        
        self.client = OpenAI(api_key=self.api_key)
    
    def generate(self, prompt: str, output_class: Type[T]) -> T:
        """
        Generate a structured response from the LLM.
        
        Args:
            prompt: The input text prompt for the LLM
            output_class: The Pydantic model class to structure the output
            
        Returns:
            An instance of the output_class with the LLM's structured response
        """
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {'role': 'user', 'content': prompt}
            ],
            text_format=output_class,
        )
        
        if not response.output_parsed:
            raise ValueError("No structured output received from the model")
        
        return response.output_parsed

