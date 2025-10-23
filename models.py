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
