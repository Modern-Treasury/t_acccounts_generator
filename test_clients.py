#!/usr/bin/env python3
"""
Test script for LLM clients using test cases from test_cases folder.
Tests all registered LLM clients against expected results.
"""

import yaml
from pathlib import Path
from typing import Any, Dict, List, Type
from clients import OpenAIClient, GemmaClient, DeepSeekClient
from models import ChartOfAccounts, FundFlow

# Registry of available LLM clients
LLM_CLIENTS: Dict[str, Type] = {
    "OpenAIClient": OpenAIClient,
    # "GemmaClient": GemmaClient,
    # "DeepSeekClient": DeepSeekClient,
}


def load_test_cases() -> List[Dict[str, Any]]:
    """Load all test cases from the test_cases folder."""
    test_cases = []
    test_cases_dir = Path("test_cases")
    
    if not test_cases_dir.exists():
        print("❌ test_cases directory not found!")
        return []
    
    # Find all YAML files in the test_cases directory
    yaml_files = list(test_cases_dir.glob("*.yaml")) + list(test_cases_dir.glob("*.yml"))
    
    if not yaml_files:
        print("❌ No YAML test files found in test_cases directory!")
        return []
    
    print(f"📁 Found {len(yaml_files)} test file(s)")
    
    for yaml_file in sorted(yaml_files):
        try:
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                test_case = {
                    'chart_of_accounts_prompt': data['chart_of_accounts_prompt'].strip(),
                    'fund_flow_prompt': data['fund_flow_prompt'].strip(),
                    'filename': yaml_file.name
                }
                test_cases.append(test_case)
                print(f"  ✅ Loaded: {yaml_file.name}")
        except Exception as e:
            print(f"  ❌ Failed to load {yaml_file.name}: {e}")
    
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


def analyze_fund_flow(result: FundFlow) -> Dict[str, Any]:
    """
    Analyze FundFlow result and return statistics.
    
    Args:
        result: The FundFlow object returned by the LLM
    
    Returns:
        Dictionary with analysis statistics
    """
    stats = {}
    
    transactions = result.transactions
    stats['total_transactions'] = len(transactions)
    
    total_entries = sum(len(tx.entries) for tx in transactions)
    stats['total_entries'] = total_entries
    
    return stats


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
        Dictionary with results and statistics for both prompts
    """
    print(f"\n--- {client_name} [{test_name}] ---")
    
    try:
        # Step 1: Generate ChartOfAccounts
        print(f"  🔹 Step 1: Generating ChartOfAccounts...")
        chart_of_accounts = client.generate(chart_of_accounts_prompt, ChartOfAccounts)
        
        # Analyze the ChartOfAccounts
        chart_stats = analyze_chart_of_accounts(chart_of_accounts)
        
        print(f"  Generated ChartOfAccounts with {chart_stats['total_accounts']} account(s):")
        print(f"    📊 Statistics:")
        print(f"      • Debit accounts: {chart_stats['debit_accounts']}")
        print(f"      • Credit accounts: {chart_stats['credit_accounts']}")
        print(f"      • Currencies: {dict(chart_stats['currencies'])}")
        
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
        
        # Analyze the FundFlow
        flow_stats = analyze_fund_flow(fund_flow)
        
        print(f"  Generated FundFlow with {flow_stats['total_transactions']} transaction(s):")
        print(f"    📊 Statistics:")
        print(f"      • Total entries: {flow_stats['total_entries']}")
        
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
            'chart_stats': chart_stats,
            'flow_stats': flow_stats
        }
        
    except Exception as e:
        print(f"❌ ERROR: {client_name} failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e),
            'chart_stats': None,
            'flow_stats': None
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
    test_name = test_case['filename']
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
