import json
from typing import Type, TypeVar
from openai import OpenAI
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class OpenAIClient:
    """LLM client for OpenAI-compatible models via Ollama."""
    
    def __init__(
        self, 
        model: str = 'gpt-oss:20b',
        base_url: str = 'http://localhost:11434/v1',
        api_key: str = 'ollama'  # Ollama doesn't require a real API key
    ):
        """
        Initialize the OpenAI client.
        
        Args:
            model: The model to use (default: 'gpt-oss:20b')
            base_url: The base URL for the OpenAI-compatible API (default: Ollama's endpoint)
            api_key: API key (default: 'ollama' - Ollama doesn't require authentication)
        """
        self.model = model
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )
    
    def generate(self, prompt: str, output_class: Type[T]) -> T:
        """
        Generate a structured response from the LLM.
        
        Args:
            prompt: The input text prompt for the LLM
            output_class: The Pydantic model class to structure the output
            
        Returns:
            An instance of the output_class with the LLM's structured response
        """
        schema = output_class.model_json_schema()
        enhanced_prompt = f"""{prompt}

You must respond with valid JSON that matches this schema:
{json.dumps(schema, indent=2)}

Respond ONLY with valid JSON, no other text."""
        
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {'role': 'user', 'content': enhanced_prompt}
            ],
            temperature=0
        )
        
        message_content = completion.choices[0].message.content
        if not message_content:
            raise ValueError("No response content received from the model")
        
        return output_class.model_validate_json(message_content)
