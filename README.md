# T-Accounts Generator

A Python project for generating structured financial ledger accounts using LLMs with Ollama.

## Features

- Multiple LLM client implementations with a unified interface
- Support for Ollama's native API (GemmaClient)
- Support for OpenAI-compatible API via Ollama (OpenAIClient)
- Structured output using Pydantic models
- Type-safe generation of financial ledger accounts

## Installation

This project uses `uv` for dependency management. Install dependencies with:

```bash
uv sync
```

## LLM Clients

### GemmaClient

Uses Ollama's native API to interact with Gemma models.

```python
from models import LedgerAccount
from gemma_client import GemmaClient

# Initialize client
client = GemmaClient(model='gemma3', temperature=0)

# Generate structured output
account = client.generate(
    "Generate a ledger account for a primary bank account",
    LedgerAccount
)
```

### OpenAIClient

Uses Ollama's OpenAI-compatible API endpoint, allowing you to use any open-source model available in Ollama with the OpenAI SDK.

```python
from models import LedgerAccount
from openai_client import OpenAIClient

# Initialize client with Ollama's OpenAI-compatible endpoint
client = OpenAIClient(
    model='llama3',  # Any model available in Ollama
    temperature=0,
    base_url='http://localhost:11434/v1',  # Default Ollama OpenAI endpoint
    api_key='ollama'  # Ollama doesn't require authentication
)

# Generate structured output
account = client.generate(
    "Generate a ledger account for a primary bank account",
    LedgerAccount
)
```

**Supported Models (via Ollama):**
- `llama3`
- `mistral`
- `phi`
- `gemma`
- Any other OpenAI-compatible model available in Ollama

## Usage Examples

### Using GemmaClient

```bash
python main.py
```

### Using OpenAIClient

```bash
python example_openai.py
```

## Models

### LedgerAccount

A Pydantic model representing a financial ledger account with the following fields:

- `name`: Short name of the account
- `description`: Longer description of how the account is intended to be used
- `currency`: The currency of the account
- `normal_balance`: Whether the account is credit-normal or debit-normal ("credit" or "debit")

## Requirements

- Python >= 3.14
- Ollama running locally (default: http://localhost:11434)
- Dependencies:
  - ollama >= 0.6.0
  - openai >= 1.0.0
  - pydantic >= 2.12.3

## Architecture

Both clients follow the same interface pattern:

```python
class LLMClient:
    def __init__(self, model: str, temperature: float, ...):
        """Initialize the client with model configuration."""
        
    def generate(self, prompt: str, output_class: Type[T]) -> T:
        """Generate structured output matching the Pydantic model."""
```

This design allows you to easily swap between different LLM backends while maintaining the same API.

