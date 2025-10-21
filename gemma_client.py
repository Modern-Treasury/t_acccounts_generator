from typing import Type, TypeVar
from ollama import chat
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class GemmaClient:
    """LLM client for Gemma models via Ollama."""
    
    def __init__(self, model: str = 'gemma3', temperature: float = 0):
        """
        Initialize the Gemma client.
        
        Args:
            model: The Gemma model to use (default: 'gemma3')
            temperature: The temperature setting for generation (default: 0)
        """
        self.model = model
        self.temperature = temperature
    
    def generate(self, prompt: str, output_class: Type[T]) -> T:
        """
        Generate a structured response from the Gemma LLM.
        
        Args:
            prompt: The input text prompt for the LLM
            output_class: The Pydantic model class to structure the output
            
        Returns:
            An instance of the output_class with the LLM's structured response
        """
        response = chat(
            model=self.model,
            messages=[{'role': 'user', 'content': prompt}],
            format=output_class.model_json_schema(),
            options={'temperature': self.temperature},
        )
        
        return output_class.model_validate_json(response.message.content)
