"""Tests for type definitions"""

import pytest
from pydantic import ValidationError

from llama_search.types.search import (
    SearchSource,
    WebSearchResult,
    SearchTypeInfo,
    SearchTypesResponse,
)


class TestSearchSource:
    """Tests for SearchSource model"""

    def test_create_search_source(self):
        """Test creating a SearchSource"""
        source = SearchSource(
            url="https://example.com", content="Test content", full_content="Full test content"
        )
        assert source.url == "https://example.com"
        assert source.content == "Test content"
        assert source.full_content == "Full test content"

    def test_search_source_defaults(self):
        """Test SearchSource with default values"""
        source = SearchSource(url="https://example.com", content="Test content")
        assert source.full_content == ""

    def test_search_source_required_fields(self):
        """Test SearchSource requires url and content"""
        with pytest.raises(ValidationError):
            SearchSource(url="https://example.com")  # Missing content

        with pytest.raises(ValidationError):
            SearchSource(content="Test content")  # Missing url


class TestWebSearchResult:
    """Tests for WebSearchResult model"""

    def test_create_web_search_result(self):
        """Test creating a WebSearchResult"""
        sources = [SearchSource(url="https://example.com", content="Test content")]

        result = WebSearchResult(
            success=True,
            sources=sources,
            error_message="",
            id="search_123",
            query="test query",
            credits_consumed=8,
            processing_time_ms=1500,
            status="completed",
        )

        assert result.success is True
        assert len(result.sources) == 1
        assert result.sources[0].url == "https://example.com"
        assert result.credits_consumed == 8
        assert result.query == "test query"

    def test_web_search_result_defaults(self):
        """Test WebSearchResult with default values"""
        result = WebSearchResult(
            success=True,
            sources=[],
            query="test query",
            credits_consumed=8,
            processing_time_ms=1500,
            status="completed",
        )

        assert result.error_message == ""
        assert result.id is None

    def test_web_search_result_required_fields(self):
        """Test WebSearchResult requires essential fields"""
        with pytest.raises(ValidationError):
            WebSearchResult()  # Missing required fields


class TestSearchTypeInfo:
    """Tests for SearchTypeInfo model"""

    def test_create_search_type_info(self):
        """Test creating a SearchTypeInfo"""
        info = SearchTypeInfo(
            type="intelligent",
            name="Intelligent Search",
            description="AI-powered search",
            credits=8,
        )

        assert info.type == "intelligent"
        assert info.name == "Intelligent Search"
        assert info.description == "AI-powered search"
        assert info.credits == 8

    def test_search_type_info_required_fields(self):
        """Test SearchTypeInfo requires all fields"""
        with pytest.raises(ValidationError):
            SearchTypeInfo(name="Test", description="Test desc", credits=8)  # Missing type


class TestSearchTypesResponse:
    """Tests for SearchTypesResponse model"""

    def test_create_search_types_response(self):
        """Test creating a SearchTypesResponse"""
        search_types = [
            SearchTypeInfo(
                type="intelligent",
                name="Intelligent Search",
                description="AI-powered search",
                credits=8,
            )
        ]

        response = SearchTypesResponse(search_types=search_types)

        assert len(response.search_types) == 1
        assert response.search_types[0].type == "intelligent"

    def test_search_types_response_empty_list(self):
        """Test SearchTypesResponse with empty list"""
        response = SearchTypesResponse(search_types=[])
        assert len(response.search_types) == 0
