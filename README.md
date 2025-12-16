# Chart of Accounts & Fund Flow Generator

A Python project for generating structured financial charts of accounts and fund flows using multiple LLMs. Compare how different AI models approach financial accounting problems with a two-step workflow: first generating a chart of accounts, then creating fund flows based on those accounts.

*Disclaimer*: This code is for experimentation and is mostly AI-generated. It should not be used in production.

## Installation

This project uses `uv` for dependency management. Install dependencies with:

```bash
uv sync
```

## Usage

The test script uses Amazon Bedrock with the gpt-oss-120b model (us-east-1 region):

```bash
# Optionally set API keys (not needed for open source models)
export AWS_BEARER_TOKEN_BEDROCK=your_api_key
export OPENAI_API_KEY=your_api_key
export GEMINI_API_KEY=your_api_key
export ANTHROPIC_API_KEY=your_api_key

# Run test cases
uv run python test_clients.py gpt-oss-20b test_cases/simple_digital_wallet.yaml
uv run python test_clients.py gpt-oss-20b test_cases/digital_wallet.yaml
uv run python test_clients.py gpt-oss-20b test_cases/payroll.yaml
uv run python test_clients.py gpt-oss-20b test_cases/simple_payroll.yaml

# View help
uv run python test_clients.py --help
```

The script performs a two-step process:
1. **Step 1**: Generates a `ChartOfAccounts` from the first prompt
2. **Step 2**: Generates a `FundFlow` using the chart of accounts from step 1

## Test Cases

Test cases are defined in YAML format in the `test_cases/` directory:

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
3. Run the test: `uv run python test_clients.py model_name test_cases/your_new_test_case.yaml`

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
