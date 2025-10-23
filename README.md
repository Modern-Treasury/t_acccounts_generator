# Chart of Accounts Generator

A Python project for generating and analyzing structured financial charts of accounts using multiple LLMs through Ollama. Compare how different AI models approach financial accounting problems.

## Features

- **Multiple LLM Support**: OpenAI-compatible, Gemma, and DeepSeek models
- **Structured Output**: Type-safe generation using Pydantic models
- **Comparative Analysis**: Run the same prompts across multiple models and compare results
- **Flexible Test Framework**: Plain text test cases with automatic model comparison
- **Rich Statistics**: Account counts, balance distributions, and performance metrics
- **Local Execution**: All models run locally via Ollama (no API keys required for most models)

## Installation

This project uses `uv` for dependency management. Install dependencies with:

```bash
uv sync
```

## Quick Start

Run the analysis system to compare all available models:

```bash
uv run python test_clients.py
```

This will test all initialized LLM clients against the test cases and show comparative results.

## LLM Clients

### OpenAIClient
Uses Ollama's OpenAI-compatible API endpoint, supporting various open-source models.

```python
from models import ChartOfAccounts
from clients import OpenAIClient

client = OpenAIClient(model='gpt-oss:20b')
chart = client.generate(
    "Generate a chart of accounts for a digital wallet platform",
    ChartOfAccounts
)
```

### GemmaClient
Uses Ollama's native API for Gemma models with built-in structured output support.

```python
from models import ChartOfAccounts
from clients import GemmaClient

client = GemmaClient(model='gemma3')
chart = client.generate(
    "Generate a chart of accounts for a digital wallet platform", 
    ChartOfAccounts
)
```

### DeepSeekClient
Uses DeepSeek reasoning models through Ollama for sophisticated financial analysis.

```python
from models import ChartOfAccounts
from clients import DeepSeekClient

client = DeepSeekClient(model='deepseek-r1:8b')
chart = client.generate(
    "Generate a chart of accounts for a digital wallet platform",
    ChartOfAccounts
)
```

## Data Models

### LedgerAccount
Represents a single financial account:
- `name`: Short name of the account
- `description`: Detailed description of the account's purpose
- `currency`: Account currency (e.g., "USD")
- `normal_balance`: Either "debit" or "credit"

### ChartOfAccounts
Contains a collection of related ledger accounts:
- `accounts`: List of `LedgerAccount` objects

## Test Cases

Add new test scenarios by creating `.txt` files in the `test_cases/` directory:

```
test_cases/
├── digital_wallet_chart_of_accounts.txt
└── your_new_test_case.txt
```

Each file contains a plain text prompt that will be sent to all available models for comparison.

## Analysis Output

The system provides rich comparative analysis:

```
📊 Statistics:
  • Debit accounts: 4
  • Credit accounts: 3  
  • Currencies: {'USD': 7}

📋 Account Details:
  Account 1: Cash
    Description: Primary cash account for operations
    Currency: USD | Normal Balance: debit
```

## Supported Models

Ensure these models are available in Ollama:

```bash
# OpenAI-compatible models
ollama pull gpt-oss:20b

# Gemma models  
ollama pull gemma3

# DeepSeek models
ollama pull deepseek-r1:8b
```

## Requirements

- Python >= 3.14
- Ollama running locally (http://localhost:11434)
- Dependencies:
  - ollama >= 0.6.0
  - openai >= 1.0.0 
  - pydantic >= 2.12.3

## Architecture

All clients implement the same interface:

```python
class LLMClient:
    def generate(self, prompt: str, output_class: Type[T]) -> T:
        """Generate structured output matching the Pydantic model."""
```

This unified interface enables easy comparison across different LLM backends while maintaining consistent structured output generation.

## Adding New Models

1. Create a new client class following the existing pattern
2. Add it to the `LLM_CLIENTS` registry in `test_clients.py`:

```python
LLM_CLIENTS: Dict[str, Type] = {
    "OpenAIClient": OpenAIClient,
    "GemmaClient": GemmaClient, 
    "DeepSeekClient": DeepSeekClient,
    "YourNewClient": YourNewClient,  # Add here
}
```

The system will automatically detect and test the new client against all test cases.