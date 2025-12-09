import os
from typing import Type, TypeVar
import anthropic
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class AnthropicClient:
    """LLM client for Anthropic Claude models."""
    
    def __init__(
        self, 
        model: str = 'claude-sonnet-4-5',
        api_key: str | None = None
    ):
        """
        Initialize the Anthropic client.
        
        Args:
            model: The model to use (default: 'claude-sonnet-4-5')
            api_key: Anthropic API key (optional, uses ANTHROPIC_API_KEY environment variable if not provided)
        """
        self.model = model
        
        # Get the API key from parameter or environment
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "Anthropic API key not provided. Set ANTHROPIC_API_KEY environment variable."
            )
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def generate(self, prompt: str, output_class: Type[T]) -> T:
        """
        Generate a structured response from the LLM.
        
        Args:
            prompt: The input text prompt for the LLM
            output_class: The Pydantic model class to structure the output
            
        Returns:
            An instance of the output_class with the LLM's structured response
        """
        response = self.client.beta.messages.parse(
            model=self.model,
            betas=["structured-outputs-2025-11-13"],
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
            output_format=output_class,
        )
        
        if not response.parsed_output:
            raise ValueError("No structured output received from the model")
        
        return response.parsed_output

