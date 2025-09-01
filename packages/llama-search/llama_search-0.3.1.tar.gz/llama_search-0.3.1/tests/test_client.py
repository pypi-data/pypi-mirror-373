"""Tests for the Llama Search SDK client"""

import pytest
from unittest.mock import patch
import httpx

from llama_search import AsyncLlamaSearch, LlamaSearch
from llama_search._exceptions import (
    AuthenticationError,
    InsufficientCreditsError,
    ValidationError,
    RetryExhaustedError,
)
from llama_search.types.search import WebSearchResult, SearchTypesResponse


class TestAsyncLlamaSearch:
    """Tests for AsyncLlamaSearch client"""

    def test_init_with_valid_api_key(self):
        """Test client initialization with valid API key"""
        client = AsyncLlamaSearch(api_key="llasea_test_key")
        assert client._api_key == "llasea_test_key"
        assert client._base_url == "https://llama-search.com"

    def test_init_with_empty_api_key(self):
        """Test client initialization with empty API key raises error"""
        with pytest.raises(ValueError, match="API key is required"):
            AsyncLlamaSearch(api_key="")

    @pytest.mark.asyncio
    async def test_web_search_success(self):
        """Test successful web search"""
        client = AsyncLlamaSearch(api_key="test_key")

        mock_response = httpx.Response(
            status_code=200,
            json={
                "success": True,
                "sources": [
                    {"url": "https://example.com", "content": "Test content", "full_content": ""}
                ],
                "error_message": "",
                "id": "search_123",
                "query": "test query",
                "credits_consumed": 8,
                "processing_time_ms": 1500,
                "status": "completed",
            },
        )

        with patch.object(client, "_request", return_value=mock_response) as mock_request:
            result = await client.web_search("test query")

            # Verify the request was made correctly
            mock_request.assert_called_once_with(
                "POST",
                "/search/web",
                json={
                    "query": "test query",
                    "search_depth": "standard",
                    "domain": "",
                    "with_full_content": False,
                },
            )

            # Verify the response
            assert isinstance(result, WebSearchResult)
            assert result.success is True
            assert len(result.sources) == 1
            assert result.sources[0].url == "https://example.com"
            assert result.credits_consumed == 8

    @pytest.mark.asyncio
    async def test_web_search_empty_query(self):
        """Test web search with empty query raises ValidationError"""
        client = AsyncLlamaSearch(api_key="test_key")

        with pytest.raises(ValidationError, match="Query cannot be empty"):
            await client.web_search("")

    @pytest.mark.asyncio
    async def test_web_search_long_query(self):
        """Test web search with too long query raises ValidationError"""
        client = AsyncLlamaSearch(api_key="test_key")
        long_query = "a" * 501

        with pytest.raises(ValidationError, match="Query too long"):
            await client.web_search(long_query)

    @pytest.mark.asyncio
    async def test_get_search_types_success(self):
        """Test successful get search types"""
        client = AsyncLlamaSearch(api_key="test_key")

        mock_response = httpx.Response(
            status_code=200,
            json={
                "search_types": [
                    {
                        "type": "intelligent",
                        "name": "Intelligent Search",
                        "description": "AI-powered search",
                        "credits": 8,
                    }
                ]
            },
        )

        with patch.object(client, "_request", return_value=mock_response) as mock_request:
            result = await client.get_search_types()

            mock_request.assert_called_once_with("GET", "/search/types")

            assert isinstance(result, SearchTypesResponse)
            assert len(result.search_types) == 1
            assert result.search_types[0].name == "Intelligent Search"
            assert result.search_types[0].credits == 8

    @pytest.mark.asyncio
    async def test_authentication_error(self):
        """Test authentication error handling"""
        client = AsyncLlamaSearch(api_key="invalid_key")

        with patch.object(client._client, "request") as mock_request:
            mock_request.return_value = httpx.Response(status_code=401)

            with pytest.raises(AuthenticationError, match="Invalid API key"):
                await client.web_search("test query")

    @pytest.mark.asyncio
    async def test_insufficient_credits_error(self):
        """Test insufficient credits error handling"""
        client = AsyncLlamaSearch(api_key="test_key")

        with patch.object(client._client, "request") as mock_request:
            mock_request.return_value = httpx.Response(
                status_code=402,
                json={
                    "message": "Insufficient credits",
                    "credits_required": 8,
                    "credits_available": 3,
                },
            )

            with pytest.raises(InsufficientCreditsError) as exc_info:
                await client.web_search("test query")

            assert exc_info.value.credits_required == 8
            assert exc_info.value.credits_available == 3

    @pytest.mark.asyncio
    async def test_server_error_with_retry(self):
        """Test server error with retry logic"""
        client = AsyncLlamaSearch(api_key="test_key", max_retries=2)

        with patch.object(client._client, "request") as mock_request:
            mock_request.return_value = httpx.Response(status_code=500)

            with pytest.raises(RetryExhaustedError):
                await client.web_search("test query")

            # Should retry max_retries + 1 times (initial + retries)
            assert mock_request.call_count == 3

    @pytest.mark.asyncio
    async def test_network_error_with_retry(self):
        """Test network error with retry logic"""
        client = AsyncLlamaSearch(api_key="test_key", max_retries=1)

        with patch.object(client._client, "request") as mock_request:
            mock_request.side_effect = httpx.ConnectError("Connection failed")

            with pytest.raises(RetryExhaustedError):
                await client.web_search("test query")

            assert mock_request.call_count == 2  # initial + 1 retry

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager usage"""
        async with AsyncLlamaSearch(api_key="test_key") as client:
            assert client._api_key == "test_key"


class TestLlamaSearch:
    """Tests for synchronous LlamaSearch client"""

    def test_init(self):
        """Test sync client initialization"""
        client = LlamaSearch(api_key="test_key")
        assert client._async_client._api_key == "test_key"

    @patch("asyncio.run")
    def test_web_search_calls_async(self, mock_asyncio_run):
        """Test sync web_search calls async version"""
        client = LlamaSearch(api_key="test_key")
        mock_result = WebSearchResult(
            success=True,
            sources=[],
            query="test",
            credits_consumed=8,
            processing_time_ms=1000,
            status="completed",
        )
        mock_asyncio_run.return_value = mock_result

        result = client.web_search("test query")

        assert mock_asyncio_run.called
        assert result == mock_result

    @patch("asyncio.run")
    def test_get_search_types_calls_async(self, mock_asyncio_run):
        """Test sync get_search_types calls async version"""
        client = LlamaSearch(api_key="test_key")
        mock_result = SearchTypesResponse(search_types=[])
        mock_asyncio_run.return_value = mock_result

        result = client.get_search_types()

        assert mock_asyncio_run.called
        assert result == mock_result

    def test_context_manager(self):
        """Test sync context manager usage"""
        with LlamaSearch(api_key="test_key") as client:
            assert client._async_client._api_key == "test_key"
