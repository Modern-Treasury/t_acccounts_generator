#!/usr/bin/env python3
"""
Test script for LLM clients using test cases from test_cases folder.
Tests all registered LLM clients against expected results.
"""

import argparse
import yaml
from pathlib import Path
from typing import Any, Dict, Type
from clients import OpenAIClient, OllamaClient, GemmaClient, DeepSeekClient, BedrockClient
from models import ChartOfAccounts, FundFlow

# Model registry: maps short model names to (client_class, full_model_id)
MODELS: Dict[str, tuple[Type, str]] = {
    # OpenAI models
    "gpt-5-nano": (OpenAIClient, "gpt-5-nano"),
    # Anthropic models (Bedrock)
    "claude-sonnet": (BedrockClient, "anthropic.claude-3-5-sonnet-20241022-v2:0"),
    "claude-haiku": (BedrockClient, "anthropic.claude-3-haiku-20240307-v1:0"),
    # Meta Llama models (Bedrock)
    "llama-70b": (BedrockClient, "us.meta.llama3-3-70b-instruct-v1:0"),
    "llama-3b": (BedrockClient, "us.meta.llama3-2-3b-instruct-v1:0"),
    # Mistral models (Bedrock)
    "mistral-large": (BedrockClient, "mistral.mistral-large-2407-v1:0"),
    # Local Ollama models
    "gemma3": (GemmaClient, "gemma3"),
    "deepseek-r1": (DeepSeekClient, "deepseek-r1:8b"),
    "gpt-oss-20b": (OllamaClient, "gpt-oss:20b"),
}


def load_test_case(file_path: str) -> Dict[str, Any]:
    """Load a test case from a YAML file.
    
    Args:
        file_path: Path to the YAML test case file
        
    Returns:
        Dictionary containing the test case data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        yaml.YAMLError: If the file is not valid YAML
        KeyError: If required keys are missing
    """
    test_file = Path(file_path)
    
    if not test_file.exists():
        raise FileNotFoundError(f"Test case file not found: {file_path}")
    
    print(f"📁 Loading test case: {test_file.name}")
    
    with open(test_file, 'r') as f:
        data = yaml.safe_load(f)
    
    # Validate required keys
    required_keys = ['chart_of_accounts_prompt', 'fund_flow_prompt']
    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        raise KeyError(f"Missing required keys in test case: {', '.join(missing_keys)}")
    
    test_case = {
        'chart_of_accounts_prompt': data['chart_of_accounts_prompt'].strip(),
        'fund_flow_prompt': data['fund_flow_prompt'].strip(),
        'filename': test_file.name
    }
    
    print(f"  ✅ Loaded: {test_file.name}")
    return test_case


def run_client_test(client_name: str, client, chart_of_accounts_prompt: str, fund_flow_prompt: str, test_name: str) -> Dict[str, Any]:
    """
    Run test for a specific LLM client with two prompts and return results.
    
    Args:
        client_name: Name of the client for display
        client: The client instance to test
        chart_of_accounts_prompt: The prompt to generate ChartOfAccounts
        fund_flow_prompt: The prompt to generate FundFlow
        test_name: Name of the test case
    
    Returns:
        Dictionary with results for both prompts
    """
    print(f"\n--- {client_name} [{test_name}] ---")
    
    try:
        # Step 1: Generate ChartOfAccounts
        print(f"  🔹 Step 1: Generating ChartOfAccounts...")
        chart_of_accounts = client.generate(chart_of_accounts_prompt, ChartOfAccounts)
        
        print(f"\n    📋 Account Details:")
        for i, account in enumerate(chart_of_accounts.accounts):
            print(f"      Account {i+1}: {account.name}")
            print(f"        Description: {account.description}")
            print(f"        Currency: {account.currency} | Normal Balance: {account.normal_balance}")
        
        # Step 2: Generate FundFlow using the ChartOfAccounts
        print(f"\n  🔹 Step 2: Generating FundFlow...")
        
        # Format the chart of accounts for the prompt
        accounts_text = "\n".join([
            f"- {account.name}: {account.description} (Currency: {account.currency}, Normal Balance: {account.normal_balance})"
            for account in chart_of_accounts.accounts
        ])
        
        full_prompt2 = f"{fund_flow_prompt}\n\nChart of Accounts:\n{accounts_text}"
        
        fund_flow = client.generate(full_prompt2, FundFlow)
        
        print(f"\n    💸 Transaction Details:")
        for i, transaction in enumerate(fund_flow.transactions):
            print(f"      Transaction {i+1}: {transaction.description}")
            for j, entry in enumerate(transaction.entries):
                print(f"        Entry {j+1}: Account={entry.account_id}, Direction={entry.direction}, Amount={entry.amount} {entry.currency}")
        print()
        
        return {
            'success': True,
            'chart_of_accounts': chart_of_accounts,
            'fund_flow': fund_flow,
        }
        
    except Exception as e:
        print(f"❌ ERROR: {client_name} failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }


def run_test_case(test_case: Dict[str, Any], clients: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run a single test case against all registered clients.
    
    Args:
        test_case: Dictionary containing chart_of_accounts_prompt, fund_flow_prompt, and filename
        clients: Dictionary mapping client names to client instances
    
    Returns:
        Dictionary with results for each client
    """
    test_name = test_case["filename"]
    chart_of_accounts_prompt = test_case["chart_of_accounts_prompt"]
    fund_flow_prompt = test_case["fund_flow_prompt"]
    
    print(f"\n{'='*60}")
    print(f"🧪 Running Test Case: {test_name}")
    print(f"{'='*60}")
    print(f"Prompt 1 (ChartOfAccounts): {chart_of_accounts_prompt[:100]}...")
    print(f"Prompt 2 (FundFlow): {fund_flow_prompt[:100]}...")
    
    # Run tests for all clients
    results = {}
    for client_name, client_instance in clients.items():
        client_result = run_client_test(client_name, client_instance, chart_of_accounts_prompt, fund_flow_prompt, test_name)
        results[client_name] = client_result
    
    return results


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(
        description="Test LLM clients with a specific test case YAML file"
    )
    parser.add_argument(
        "model",
        type=str,
        choices=list(MODELS.keys()),
        help=f"Model to use. Available: {', '.join(MODELS.keys())}"
    )
    parser.add_argument(
        "test_case",
        type=str,
        help="Path to the test case YAML file (e.g., test_cases/digital_wallet.yaml)"
    )
    
    args = parser.parse_args()
    
    print("🧪 Starting LLM Client Analysis")
    print("=" * 60)
    
    # Load the specified test case
    try:
        test_case = load_test_case(args.test_case)
    except (FileNotFoundError, yaml.YAMLError, KeyError) as e:
        print(f"❌ Error loading test case: {e}")
        return 1
    
    # Get model configuration
    client_class, model_id = MODELS[args.model]
    
    # Initialize the client with the model
    client = client_class(model=model_id)
    
    clients = {
        args.model: client
    }
    
    print(f"🔧 Using {client_class.__name__} with model: {model_id}")
    if client_class == BedrockClient:
        print(f"🌍 Region: {client.region_name}")
        print(f"🔑 Using AWS_BEARER_TOKEN_BEDROCK environment variable")
    elif client_class == OpenAIClient:
        print(f"🔑 Using OPENAI_API_KEY environment variable")
    
    # Run the test case
    run_test_case(test_case, clients)
    
    return 0


if __name__ == "__main__":
    exit(main())
