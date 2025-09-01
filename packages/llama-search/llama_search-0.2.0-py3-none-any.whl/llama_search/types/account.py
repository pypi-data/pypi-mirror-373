"""Account management type definitions"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class UsageStats(BaseModel):
    """User's usage statistics"""

    total_searches: int
    credits_used: int
    credits_remaining: int
    searches_this_month: int


class SearchHistoryItem(BaseModel):
    """Individual search history entry"""

    id: str
    query: str
    search_type: str
    credits_consumed: int
    processing_time_ms: Optional[int] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SearchHistory(BaseModel):
    """Search history response"""

    searches: List[SearchHistoryItem]
    total: int


class CreditBalance(BaseModel):
    """Credit balance information"""

    balance: int
    total_purchased: int
    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)
