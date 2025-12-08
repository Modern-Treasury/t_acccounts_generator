import json
import os
from typing import Type, TypeVar
import boto3
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class BedrockClient:
    """LLM client for Amazon Bedrock models using the unified Converse API."""
    
    def __init__(
        self, 
        model: str = 'arn:aws:bedrock:us-west-2:362891051831:inference-profile/global.anthropic.claude-sonnet-4-5-20250929-v1:0',
        region_name: str = 'us-west-2'
    ):
        """
        Initialize the Amazon Bedrock client.
        
        Args:
            model: The Bedrock model ID to use (e.g., 'openai.gpt-oss-120b-1:0', 
                   'anthropic.claude-3-sonnet-20240229-v1:0',
                   'us.meta.llama3-3-70b-instruct-v1:0', 'us.amazon.nova-lite-v1:0')
            region_name: The AWS region name (default: 'us-west-2')
        """
        self.model = model
        self.region_name = region_name
        
        # Get the API key from environment
        self.api_key = os.environ.get('AWS_BEARER_TOKEN_BEDROCK')
        
        if not self.api_key:
            raise ValueError(
                "Bedrock API key not provided. Set AWS_BEARER_TOKEN_BEDROCK environment variable."
            )
        
        # Create the boto3 client
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name=region_name
        )
        
        # Register event handler to inject the bearer token
        self.client.meta.events.register('before-sign', self._inject_bearer_token)
    
    def _inject_bearer_token(self, request, **kwargs):
        """Inject the bearer token into the request headers."""
        request.headers['Authorization'] = f'Bearer {self.api_key}'
    
    def generate(self, prompt: str, output_class: Type[T]) -> T:
        """
        Generate a structured response from the Amazon Bedrock LLM using the Converse API.
        
        Args:
            prompt: The input text prompt for the LLM
            output_class: The Pydantic model class to structure the output
            
        Returns:
            An instance of the output_class with the LLM's structured response
        """
        schema = output_class.model_json_schema()
        enhanced_prompt = f"""{prompt}

You must respond with valid JSON that matches this exact schema:
{json.dumps(schema, indent=2)}

Respond ONLY with valid JSON, no other text or explanations."""
        
        # Use the unified Converse API (works across all Bedrock models)
        response = self.client.converse(
            modelId=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": enhanced_prompt}]
                }
            ],
            inferenceConfig={
                "temperature": 0,
                "maxTokens": 4096
            }
        )
        
        # Extract the response text from the unified response format
        # Handle different response structures
        try:
            content_blocks = response['output']['message']['content']
            
            # OpenAI reasoning models return multiple content blocks:
            # - reasoningContent with the model's thinking process
            # - text with the actual output
            # We need to find the text block, not the reasoning
            
            message_content = None
            
            for block in content_blocks:
                # Try to find the actual text output (not reasoning)
                if 'text' in block:
                    message_content = block['text']
                    break
                elif isinstance(block, str):
                    message_content = block
                    break
            
            # If we didn't find text in any block, debug
            if not message_content:
                import pprint
                print("\n🔍 Debug: All content blocks:")
                pprint.pprint(content_blocks)
                raise ValueError(f"Could not find text output in {len(content_blocks)} content blocks")
                
        except (KeyError, IndexError, TypeError) as e:
            # Debug: print the actual response structure
            import pprint
            print("\n🔍 Debug: Response structure:")
            pprint.pprint(response)
            raise ValueError(f"Failed to extract response content: {e}")
        
        if not message_content:
            raise ValueError("No response content received from Bedrock model")
        
        # Clean up any potential markdown formatting
        message_content = message_content.strip()
        if message_content.startswith('```json'):
            message_content = message_content.replace('```json', '').replace('```', '').strip()
        elif message_content.startswith('```'):
            message_content = message_content.replace('```', '').strip()
        
        return output_class.model_validate_json(message_content)

