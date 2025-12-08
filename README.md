# Chart of Accounts & Fund Flow Generator

A Python project for generating and analyzing structured financial charts of accounts and fund flows using multiple LLMs. Compare how different AI models approach financial accounting problems with a two-step workflow: first generating a chart of accounts, then creating fund flows based on those accounts.

## Features

- **Multiple LLM Support**: OpenAI-compatible, Gemma, DeepSeek, and Amazon Bedrock models
- **Structured Output**: Type-safe generation using Pydantic models
- **Two-Step Workflow**: Generate ChartOfAccounts, then FundFlow transactions based on those accounts
- **YAML Test Cases**: Structured test cases with separate prompts for each step
- **Flexible Test Framework**: Run specific test cases with command-line arguments
- **Rich Output**: Detailed account and transaction information with balance tracking
- **Flexible Deployment**: Local execution via Ollama or cloud-based via Amazon Bedrock

## Installation

This project uses `uv` for dependency management. Install dependencies with:

```bash
uv sync
```

## Quick Start

The test script uses Amazon Bedrock with the gpt-oss-120b model (us-east-1 region):

```bash
# Set the API key as an environment variable
export AWS_BEARER_TOKEN_BEDROCK=your_api_key

# Run test cases
uv run python test_clients.py test_cases/digital_wallet.yaml
uv run python test_clients.py test_cases/payroll.yaml
uv run python test_clients.py test_cases/payroll_simple.yaml

# View help
uv run python test_clients.py --help
```

The script performs a two-step process:
1. **Step 1**: Generates a `ChartOfAccounts` from the first prompt
2. **Step 2**: Generates a `FundFlow` using the chart of accounts from step 1

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

### BedrockClient
Uses Amazon Bedrock's unified Converse API for access to all foundation models, including Claude, Llama, Nova, and OpenAI models through cross-region inference.

```python
import os
from models import ChartOfAccounts
from clients import BedrockClient

# Set API key via environment variable
os.environ['AWS_BEARER_TOKEN_BEDROCK'] = 'your_api_key'

# Basic usage (uses environment variable)
client = BedrockClient(
    model='gpt-oss-120b',
    region_name='us-east-1'
)
chart = client.generate(
    "Generate a chart of accounts for a digital wallet platform",
    ChartOfAccounts
)
```

**Prerequisites for BedrockClient:**
- Bedrock API key (set via `AWS_BEARER_TOKEN_BEDROCK` environment variable)
- Access to Bedrock in your AWS region
- Model access granted for specific models

**Example Model IDs:**
- Anthropic: `anthropic.claude-3-5-sonnet-20241022-v2:0`, `anthropic.claude-3-haiku-20240307-v1:0`
- Meta Llama: `us.meta.llama3-3-70b-instruct-v1:0`, `us.meta.llama3-2-3b-instruct-v1:0`
- Amazon Nova: `us.amazon.nova-lite-v1:0`, `us.amazon.nova-pro-v1:0`
- Mistral: `mistral.mistral-large-2407-v1:0`
- OpenAI (cross-region): Check Bedrock console for available OpenAI models in your region

Note: The client uses Bedrock's unified Converse API, which works with all models without model-specific code.

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

### LedgerEntry
Represents a single entry in a transaction:
- `account_id`: The account affected by this entry
- `amount`: The amount of the entry
- `currency`: The currency of the entry

### LedgerTransaction
Represents a complete financial transaction:
- `description`: Description of the transaction
- `entries`: List of `LedgerEntry` objects (must balance)

### FundFlow
Represents a business process as a series of transactions:
- `transactions`: List of `LedgerTransaction` objects

## Test Cases

Test cases are defined in YAML format in the `test_cases/` directory:

```
test_cases/
├── digital_wallet.yaml
├── payroll.yaml
└── your_new_test_case.yaml
```

### Test Case Format

Each YAML file must contain two prompts:

```yaml
chart_of_accounts_prompt: |
  Generate a chart of accounts for a digital wallet platform that holds user funds in USD.
  Include accounts that represent the user funds held in an FBO account and accounts that represent user liabilities.
  Create the minimum number of accounts to satisfy the requirements.

fund_flow_prompt: |
  Given the following chart of accounts, generate a FundFlow that represents the business process of a user depositing funds into their digital wallet.
  The FundFlow should show the ledger transactions needed to record a $100 USD deposit.
```

### Creating New Test Cases

1. Create a new `.yaml` file in `test_cases/`
2. Add both `chart_of_accounts_prompt` and `fund_flow_prompt` keys
3. Run the test: `uv run python test_clients.py test_cases/your_new_test_case.yaml`

## Output

The system provides detailed output for both generation steps:

### Step 1: Chart of Accounts
```
📋 Account Details:
  Account 1: FBO Bank Account
    Description: Bank account where user funds are held on behalf of users
    Currency: USD | Normal Balance: debit
  Account 2: User 1 Liability
    Description: Liability to User 1 for funds held in the platform
    Currency: USD | Normal Balance: credit
```

### Step 2: Fund Flow
```
💸 Transaction Details:
  Transaction 1: User 1 deposits $100 into digital wallet
    Entry 1: Account=FBO Bank Account, Direction=debit, Amount=100 USD
    Entry 2: Account=User 1 Liability, Direction=credit, Amount=100 USD
  Transaction 2: User 1 sends $5 to User 2
    Entry 1: Account=User 1 Liability, Direction=debit, Amount=5 USD
    Entry 2: Account=User 2 Liability, Direction=credit, Amount=5 USD
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
- Ollama running locally (http://localhost:11434) for OpenAI/Gemma/DeepSeek clients
- AWS account with Bedrock access (optional, for BedrockClient only)
- Dependencies:
  - boto3 >= 1.40.69
  - ollama >= 0.6.0
  - openai >= 1.0.0 
  - pydantic >= 2.12.3
  - pyyaml >= 6.0.0

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

The system will automatically test the new client when running test cases.

## Workflow

The test framework implements a two-step workflow that mimics real accounting processes:

1. **Define the Chart of Accounts**: The LLM generates appropriate accounts for the business scenario
2. **Generate Fund Flows**: Using the defined accounts, the LLM creates realistic transaction flows

This approach ensures that fund flows reference valid accounts from the chart, creating more realistic and testable outputs.