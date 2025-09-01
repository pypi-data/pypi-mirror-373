"""Tests for account management functionality"""

import pytest
from datetime import datetime
from unittest.mock import patch
import httpx

from llama_search import AsyncLlamaSearch, LlamaSearch
from llama_search._exceptions import ValidationError, LlamaSearchError
from llama_search.types.account import UsageStats, SearchHistory, SearchHistoryItem, CreditBalance


class TestAccountManagement:
    """Tests for account management methods"""

    @pytest.mark.asyncio
    async def test_get_usage_stats_success(self):
        """Test successful get_usage_stats"""
        client = AsyncLlamaSearch(api_key="test_key")

        mock_response = httpx.Response(
            status_code=200,
            json={
                "total_searches": 45,
                "credits_used": 360,
                "credits_remaining": 140,
                "searches_this_month": 12,
            },
        )

        with patch.object(client, "_request", return_value=mock_response) as mock_request:
            result = await client.get_usage_stats()

            mock_request.assert_called_once_with("GET", "/search/usage-stats")

            assert isinstance(result, UsageStats)
            assert result.total_searches == 45
            assert result.credits_used == 360
            assert result.credits_remaining == 140
            assert result.searches_this_month == 12

    @pytest.mark.asyncio
    async def test_get_search_history_success(self):
        """Test successful get_search_history"""
        client = AsyncLlamaSearch(api_key="test_key")

        mock_response = httpx.Response(
            status_code=200,
            json={
                "searches": [
                    {
                        "id": "search_123",
                        "query": "Tesla Model 3 specs",
                        "search_type": "intelligent",
                        "credits_consumed": 8,
                        "processing_time_ms": 1500,
                        "status": "completed",
                        "created_at": "2024-01-15T10:30:00Z",
                    },
                    {
                        "id": "search_124",
                        "query": "Python async tutorial",
                        "search_type": "intelligent",
                        "credits_consumed": 5,
                        "processing_time_ms": 1200,
                        "status": "completed",
                        "created_at": "2024-01-15T09:15:00Z",
                    },
                ],
                "total": 2,
            },
        )

        with patch.object(client, "_request", return_value=mock_response) as mock_request:
            result = await client.get_search_history(limit=20)

            mock_request.assert_called_once_with("GET", "/search/history", params={"limit": 20})

            assert isinstance(result, SearchHistory)
            assert result.total == 2
            assert len(result.searches) == 2

            # Check first search item
            first_search = result.searches[0]
            assert isinstance(first_search, SearchHistoryItem)
            assert first_search.id == "search_123"
            assert first_search.query == "Tesla Model 3 specs"
            assert first_search.credits_consumed == 8
            assert first_search.status == "completed"

    @pytest.mark.asyncio
    async def test_get_search_history_default_limit(self):
        """Test get_search_history with default limit"""
        client = AsyncLlamaSearch(api_key="test_key")

        mock_response = httpx.Response(status_code=200, json={"searches": [], "total": 0})

        with patch.object(client, "_request", return_value=mock_response) as mock_request:
            await client.get_search_history()

            mock_request.assert_called_once_with("GET", "/search/history", params={"limit": 10})

    @pytest.mark.asyncio
    async def test_get_search_history_invalid_limit_zero(self):
        """Test get_search_history with invalid limit (0)"""
        client = AsyncLlamaSearch(api_key="test_key")

        with pytest.raises(ValidationError, match="Limit must be greater than 0"):
            await client.get_search_history(limit=0)

    @pytest.mark.asyncio
    async def test_get_search_history_invalid_limit_negative(self):
        """Test get_search_history with invalid limit (negative)"""
        client = AsyncLlamaSearch(api_key="test_key")

        with pytest.raises(ValidationError, match="Limit must be greater than 0"):
            await client.get_search_history(limit=-5)

    @pytest.mark.asyncio
    async def test_get_search_history_invalid_limit_too_large(self):
        """Test get_search_history with invalid limit (too large)"""
        client = AsyncLlamaSearch(api_key="test_key")

        with pytest.raises(ValidationError, match="Limit cannot exceed 100"):
            await client.get_search_history(limit=101)

    @pytest.mark.asyncio
    async def test_get_credit_balance_success(self):
        """Test successful get_credit_balance"""
        client = AsyncLlamaSearch(api_key="test_key")

        mock_response = httpx.Response(
            status_code=200,
            json={"balance": 250, "total_purchased": 500, "last_updated": "2024-01-15T10:30:00Z"},
        )

        with patch.object(client, "_request", return_value=mock_response) as mock_request:
            result = await client.get_credit_balance()

            mock_request.assert_called_once_with("GET", "/billing/credits")

            assert isinstance(result, CreditBalance)
            assert result.balance == 250
            assert result.total_purchased == 500
            assert isinstance(result.last_updated, datetime)

    @pytest.mark.asyncio
    async def test_get_usage_stats_parse_error(self):
        """Test get_usage_stats with response parsing error"""
        client = AsyncLlamaSearch(api_key="test_key")

        mock_response = httpx.Response(
            status_code=200,
            json={"invalid": "data"},  # Missing required fields
        )

        with patch.object(client, "_request", return_value=mock_response):
            with pytest.raises(LlamaSearchError, match="Failed to parse response"):
                await client.get_usage_stats()

    @pytest.mark.asyncio
    async def test_get_search_history_parse_error(self):
        """Test get_search_history with response parsing error"""
        client = AsyncLlamaSearch(api_key="test_key")

        mock_response = httpx.Response(
            status_code=200,
            json={"searches": ["invalid"], "total": 1},  # Invalid search format
        )

        with patch.object(client, "_request", return_value=mock_response):
            with pytest.raises(LlamaSearchError, match="Failed to parse response"):
                await client.get_search_history()

    @pytest.mark.asyncio
    async def test_get_credit_balance_parse_error(self):
        """Test get_credit_balance with response parsing error"""
        client = AsyncLlamaSearch(api_key="test_key")

        mock_response = httpx.Response(
            status_code=200,
            json={"balance": "invalid"},  # Invalid balance type
        )

        with patch.object(client, "_request", return_value=mock_response):
            with pytest.raises(LlamaSearchError, match="Failed to parse response"):
                await client.get_credit_balance()


class TestSyncAccountManagement:
    """Tests for synchronous account management methods"""

    @patch("asyncio.run")
    def test_get_usage_stats_calls_async(self, mock_asyncio_run):
        """Test sync get_usage_stats calls async version"""
        client = LlamaSearch(api_key="test_key")
        mock_result = UsageStats(
            total_searches=10, credits_used=80, credits_remaining=20, searches_this_month=5
        )
        mock_asyncio_run.return_value = mock_result

        result = client.get_usage_stats()

        assert mock_asyncio_run.called
        assert result == mock_result

    @patch("asyncio.run")
    def test_get_search_history_calls_async(self, mock_asyncio_run):
        """Test sync get_search_history calls async version"""
        client = LlamaSearch(api_key="test_key")
        mock_result = SearchHistory(searches=[], total=0)
        mock_asyncio_run.return_value = mock_result

        result = client.get_search_history(limit=25)

        assert mock_asyncio_run.called
        assert result == mock_result

    @patch("asyncio.run")
    def test_get_credit_balance_calls_async(self, mock_asyncio_run):
        """Test sync get_credit_balance calls async version"""
        client = LlamaSearch(api_key="test_key")
        mock_result = CreditBalance(balance=100, total_purchased=200, last_updated=datetime.now())
        mock_asyncio_run.return_value = mock_result

        result = client.get_credit_balance()

        assert mock_asyncio_run.called
        assert result == mock_result


class TestAccountTypes:
    """Tests for account-related type definitions"""

    def test_usage_stats_creation(self):
        """Test creating UsageStats model"""
        stats = UsageStats(
            total_searches=50, credits_used=400, credits_remaining=100, searches_this_month=15
        )

        assert stats.total_searches == 50
        assert stats.credits_used == 400
        assert stats.credits_remaining == 100
        assert stats.searches_this_month == 15

    def test_search_history_item_creation(self):
        """Test creating SearchHistoryItem model"""
        created_at = datetime.now()
        item = SearchHistoryItem(
            id="search_123",
            query="test query",
            search_type="intelligent",
            credits_consumed=8,
            processing_time_ms=1500,
            status="completed",
            created_at=created_at,
        )

        assert item.id == "search_123"
        assert item.query == "test query"
        assert item.credits_consumed == 8
        assert item.created_at == created_at

    def test_search_history_item_optional_fields(self):
        """Test SearchHistoryItem with optional fields"""
        item = SearchHistoryItem(
            id="search_123",
            query="test query",
            search_type="intelligent",
            credits_consumed=8,
            status="completed",
            created_at=datetime.now(),
        )

        assert item.processing_time_ms is None

    def test_search_history_creation(self):
        """Test creating SearchHistory model"""
        items = [
            SearchHistoryItem(
                id="search_123",
                query="test query",
                search_type="intelligent",
                credits_consumed=8,
                status="completed",
                created_at=datetime.now(),
            )
        ]

        history = SearchHistory(searches=items, total=1)

        assert len(history.searches) == 1
        assert history.total == 1
        assert history.searches[0].id == "search_123"

    def test_credit_balance_creation(self):
        """Test creating CreditBalance model"""
        last_updated = datetime.now()
        balance = CreditBalance(balance=150, total_purchased=300, last_updated=last_updated)

        assert balance.balance == 150
        assert balance.total_purchased == 300
        assert balance.last_updated == last_updated
