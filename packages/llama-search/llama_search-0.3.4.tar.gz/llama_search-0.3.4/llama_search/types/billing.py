"""Billing and credit purchase related type definitions"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class CreditPackage(BaseModel):
    """Available credit package for purchase"""

    id: str = Field(description="Package identifier")
    name: str = Field(description="Package display name")
    credits: int = Field(description="Number of credits in package")
    price_cents: int = Field(description="Price in cents (USD)")
    price_display: str = Field(description="Formatted price for display")
    popular: bool = Field(default=False, description="Whether this is a popular package")
    bonus_credits: int = Field(default=0, description="Bonus credits included")


class CreditPackagesResponse(BaseModel):
    """Response containing available credit packages"""

    packages: List[CreditPackage] = Field(description="Available credit packages")
    currency: str = Field(default="USD", description="Currency for prices")


class PurchaseHistory(BaseModel):
    """User's credit purchase history"""

    purchases: List["PurchaseHistoryItem"] = Field(description="List of purchases")
    total_spent_cents: int = Field(description="Total amount spent in cents")
    total_credits_purchased: int = Field(description="Total credits purchased")


class PurchaseHistoryItem(BaseModel):
    """Individual purchase record"""

    id: str = Field(description="Purchase ID")
    package_name: str = Field(description="Name of purchased package")
    credits: int = Field(description="Credits purchased")
    price_cents: int = Field(description="Amount paid in cents")
    status: str = Field(description="Purchase status")
    created_at: datetime = Field(description="When purchase was initiated")
    completed_at: Optional[datetime] = Field(default=None, description="When purchase completed")
    session_id: Optional[str] = Field(default=None, description="Stripe session ID")
