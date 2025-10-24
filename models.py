from pydantic import BaseModel, Field
from typing import Literal, List


class LedgerAccount(BaseModel):
    """A Ledger Account for tracking financial transactions."""
    
    # Short name of the account
    name: str = Field(..., description="Short name of the account")
    
    # Longer description of how the account is intended to be used
    description: str = Field(..., description="Longer description of how the account is intended to be used")
    
    # The currency of the account
    currency: str = Field(..., description="The currency of the account")
    
    # Whether the account is credit-normal or debit-normal
    normal_balance: Literal["credit", "debit"] = Field(..., description="Whether the account is credit-normal or debit-normal. Acceptable values are either credit or debit.")


class ChartOfAccounts(BaseModel):
    """A Chart of Accounts containing multiple Ledger Accounts."""
    
    # List of ledger accounts
    accounts: List[LedgerAccount] = Field(..., description="List of ledger accounts in the chart of accounts")

class LedgerEntry(BaseModel):
    """A Ledger Entry representing a balance change in a ledger account."""
    
    # The account that the entry is for
    account_id: str = Field(..., description="The account that the transaction is for")

    # The direction of the entry
    direction: Literal["debit", "credit"] = Field(..., description="The direction of the entry. Acceptable values are either debit or credit.")
    
    # The amount of the entry
    amount: int = Field(..., description="The amount of the transaction")
    
    # The currency of the entry
    currency: str = Field(..., description="The currency of the transaction")

class LedgerTransaction(BaseModel):
    """A Ledger Transaction for tracking financial transactions."""
    # The description of the transaction
    description: str = Field(..., description="The description of the transaction")
    
    # The entries in the transaction
    entries: List[LedgerEntry] = Field(..., description="The entries in the transaction")

class FundFlow(BaseModel):
    """A group of Ledger Transactations that represent a business process."""

    # The entries in the transaction
    transactions: List[LedgerTransaction] = Field(..., description="The entries in the transaction")