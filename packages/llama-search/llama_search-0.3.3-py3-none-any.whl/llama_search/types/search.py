"""Search-related type definitions"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class SearchSource(BaseModel):
    """A single search result source"""

    url: str
    content: str
    full_content: str = ""


class WebSearchResult(BaseModel):
    """Result from web search operation"""

    success: bool
    sources: List[SearchSource]
    error_message: str = ""
    id: Optional[str] = None
    query: str
    credits_consumed: int
    processing_time_ms: int
    status: str

    model_config = ConfigDict(from_attributes=True)


class SearchTypeInfo(BaseModel):
    """Information about a search type"""

    type: str
    name: str
    description: str
    credits: int


class SearchTypesResponse(BaseModel):
    """Response containing available search types"""

    search_types: List[SearchTypeInfo]
