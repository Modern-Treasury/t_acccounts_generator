from gemma_client import GemmaClient
from models import LedgerAccount
from openai_client import OpenAIClient


def main():
    # Create LLM client
    llm_client = GemmaClient()
    
    # Generate structured output
    account = llm_client.generate(
        "Generate a ledger account for a primary bank account that holds user funds for a digital wallet in USD.",
        LedgerAccount
    )
    
    print(f"Account: {account.model_dump_json(indent=2)}")


if __name__ == "__main__":
    main()
