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


class PurchaseSession(BaseModel):
    """Credit purchase session details"""

    session_id: str = Field(description="Stripe checkout session ID")
    checkout_url: str = Field(description="URL to redirect user for payment")
    expires_at: datetime = Field(description="When the checkout session expires")
    package_id: str = Field(description="ID of the package being purchased")
    credits: int = Field(description="Number of credits being purchased")
    price_cents: int = Field(description="Total price in cents")


class PaymentStatus(BaseModel):
    """Payment status information"""

    session_id: str = Field(description="Checkout session ID")
    status: str = Field(description="Payment status (pending, completed, failed, expired)")
    credits_added: Optional[int] = Field(default=None, description="Credits added if completed")
    completed_at: Optional[datetime] = Field(default=None, description="When payment completed")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")


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
