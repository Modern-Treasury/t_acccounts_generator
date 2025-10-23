#!/usr/bin/env python3
"""
Test script for LLM clients using test cases from test_cases folder.
Tests all registered LLM clients against expected results.
"""

from pathlib import Path
from typing import Any, Dict, List, Type
from clients import OpenAIClient, GemmaClient, DeepSeekClient
from models import ChartOfAccounts

# Registry of available LLM clients
LLM_CLIENTS: Dict[str, Type] = {
    "OpenAIClient": OpenAIClient,
    "GemmaClient": GemmaClient,
    "DeepSeekClient": DeepSeekClient,
}


def load_test_cases() -> List[Dict[str, Any]]:
    """Load all test cases from the test_cases folder."""
    test_cases = []
    test_cases_dir = Path("test_cases")
    
    if not test_cases_dir.exists():
        print("❌ test_cases directory not found!")
        return []
    
    # Find all text files in the test_cases directory
    txt_files = list(test_cases_dir.glob("*.txt"))
    
    if not txt_files:
        print("❌ No text test files found in test_cases directory!")
        return []
    
    print(f"📁 Found {len(txt_files)} test file(s)")
    
    for txt_file in sorted(txt_files):
        try:
            with open(txt_file, 'r') as f:
                prompt = f.read().strip()
                test_case = {
                    'prompt': prompt,
                    'filename': txt_file.name
                }
                test_cases.append(test_case)
                print(f"  ✅ Loaded: {txt_file.name}")
        except Exception as e:
            print(f"  ❌ Failed to load {txt_file.name}: {e}")
    
    return test_cases


def analyze_chart_of_accounts(result: ChartOfAccounts) -> Dict[str, Any]:
    """
    Analyze ChartOfAccounts result and return statistics.
    
    Args:
        result: The ChartOfAccounts object returned by the LLM
    
    Returns:
        Dictionary with analysis statistics
    """
    stats = {}
    
    accounts = result.accounts
    stats['total_accounts'] = len(accounts)
    
    # Count by normal balance
    debit_accounts = [a for a in accounts if a.normal_balance == 'debit']
    credit_accounts = [a for a in accounts if a.normal_balance == 'credit']
    stats['debit_accounts'] = len(debit_accounts)
    stats['credit_accounts'] = len(credit_accounts)
    
    # Count by currency
    currencies = {}
    for account in accounts:
        currency = account.currency
        currencies[currency] = currencies.get(currency, 0) + 1
    stats['currencies'] = currencies
    
    return stats


def run_client_test(client_name: str, client, prompt: str, test_name: str) -> Dict[str, Any]:
    """
    Run test for a specific LLM client and return results.
    
    Args:
        client_name: Name of the client for display
        client: The client instance to test
        prompt: The prompt to send to the client
        test_name: Name of the test case
    
    Returns:
        Dictionary with result and statistics
    """
    print(f"\n--- {client_name} [{test_name}] ---")
    
    try:
        # Generate result using the client
        result = client.generate(prompt, ChartOfAccounts)
        
        # Analyze the result
        stats = analyze_chart_of_accounts(result)
        
        print(f"Generated ChartOfAccounts with {stats['total_accounts']} account(s):")
        print(f"  📊 Statistics:")
        print(f"    • Debit accounts: {stats['debit_accounts']}")
        print(f"    • Credit accounts: {stats['credit_accounts']}")
        print(f"    • Currencies: {dict(stats['currencies'])}")
        
        print(f"\n  📋 Account Details:")
        for i, account in enumerate(result.accounts):
            print(f"    Account {i+1}: {account.name}")
            print(f"      Description: {account.description}")
            print(f"      Currency: {account.currency} | Normal Balance: {account.normal_balance}")
            print()
        
        return {
            'success': True,
            'result': result,
            'stats': stats
        }
        
    except Exception as e:
        print(f"❌ ERROR: {client_name} failed with exception: {e}")
        return {
            'success': False,
            'error': str(e),
            'stats': None
        }


def run_test_case(test_case: Dict[str, Any], clients: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run a single test case against all registered clients.
    
    Args:
        test_case: Dictionary containing prompt and filename
        clients: Dictionary mapping client names to client instances
    
    Returns:
        Dictionary with results for each client
    """
    test_name = test_case['filename']
    prompt = test_case["prompt"]
    
    print(f"\n{'='*60}")
    print(f"🧪 Running Test Case: {test_name}")
    print(f"{'='*60}")
    print(f"Prompt: {prompt}")
    
    # Run tests for all clients
    results = {}
    for client_name, client_instance in clients.items():
        client_result = run_client_test(client_name, client_instance, prompt, test_name)
        results[client_name] = client_result
    
    return results


def main():
    """Main test runner."""
    print("🧪 Starting LLM Client Analysis")
    print("=" * 60)
    
    # Load all test cases
    test_cases = load_test_cases()
    
    if not test_cases:
        print("❌ No test cases loaded. Exiting.")
        return
    
    print(f"\n🔧 Initializing {len(LLM_CLIENTS)} LLM clients...")
    clients = {}
    for client_name, client_class in LLM_CLIENTS.items():
        try:
            clients[client_name] = client_class()
            print(f"  ✅ {client_name} initialized successfully")
        except Exception as e:
            print(f"  ⚠️  {client_name} initialization failed: {e}")
            print(f"    (Skipping {client_name} for this run)")
    
    if not clients:
        print("❌ No clients initialized successfully. Exiting.")
        return

    for test_case in test_cases:
        run_test_case(test_case, clients)


if __name__ == "__main__":
    main()
