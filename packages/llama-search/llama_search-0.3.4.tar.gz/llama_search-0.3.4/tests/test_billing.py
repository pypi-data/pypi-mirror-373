"""Tests for billing functionality"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from llama_search import AsyncLlamaSearch
from llama_search._exceptions import (
    PaymentError,
    PaymentCancelledError,
    PaymentFailedError,
    ValidationError,
)
from llama_search.types.billing import (
    CreditPackage,
    CreditPackagesResponse,
    PurchaseHistory,
    PurchaseHistoryItem,
)


class TestBillingTypes:
    """Tests for billing type definitions"""

    def test_credit_package_model(self):
        """Test CreditPackage model validation"""
        package = CreditPackage(
            id="basic_100",
            name="Basic Pack",
            credits=100,
            price_cents=999,
            price_display="$9.99",
            popular=True,
            bonus_credits=10,
        )

        assert package.id == "basic_100"
        assert package.name == "Basic Pack"
        assert package.credits == 100
        assert package.price_cents == 999
        assert package.price_display == "$9.99"
        assert package.popular is True
        assert package.bonus_credits == 10

    def test_credit_packages_response_model(self):
        """Test CreditPackagesResponse model validation"""
        response = CreditPackagesResponse(
            packages=[
                CreditPackage(
                    id="basic_100",
                    name="Basic",
                    credits=100,
                    price_cents=999,
                    price_display="$9.99",
                )
            ],
            currency="USD",
        )

        assert len(response.packages) == 1
        assert response.currency == "USD"
        assert response.packages[0].id == "basic_100"

    def test_purchase_history_model(self):
        """Test PurchaseHistory model validation"""
        created_at = datetime.now() - timedelta(days=1)
        completed_at = datetime.now() - timedelta(hours=23)

        purchase = PurchaseHistoryItem(
            id="pur_123",
            package_name="Basic Pack",
            credits=100,
            price_cents=999,
            status="completed",
            created_at=created_at,
            completed_at=completed_at,
            session_id="cs_123",
        )

        history = PurchaseHistory(
            purchases=[purchase], total_spent_cents=999, total_credits_purchased=100
        )

        assert len(history.purchases) == 1
        assert history.total_spent_cents == 999
        assert history.total_credits_purchased == 100
        assert history.purchases[0].id == "pur_123"


class TestBillingExceptions:
    """Tests for billing-specific exceptions"""

    def test_payment_error(self):
        """Test PaymentError exception"""
        error = PaymentError("Payment processing failed", session_id="cs_123")

        assert str(error) == "Payment processing failed"
        assert error.session_id == "cs_123"
        assert error.error_code == "PAYMENT_ERROR"
        assert isinstance(error.timestamp, datetime)

    def test_payment_cancelled_error(self):
        """Test PaymentCancelledError exception"""
        error = PaymentCancelledError(session_id="cs_123")

        assert str(error) == "Payment was cancelled"
        assert error.session_id == "cs_123"
        assert error.error_code == "PAYMENT_CANCELLED"

    def test_payment_failed_error(self):
        """Test PaymentFailedError exception"""
        error = PaymentFailedError(
            "Payment failed", session_id="cs_123", failure_reason="Card declined"
        )

        assert str(error) == "Payment failed"
        assert error.session_id == "cs_123"
        assert error.failure_reason == "Card declined"
        assert error.error_code == "PAYMENT_FAILED"


class TestBillingClient:
    """Tests for billing client functionality"""

    @pytest.mark.asyncio
    async def test_get_credit_packages_success(self):
        """Test successful credit packages retrieval"""
        mock_response_data = {
            "packages": [
                {
                    "id": "basic_100",
                    "name": "Basic Pack",
                    "credits": 100,
                    "price_cents": 999,
                    "price_display": "$9.99",
                    "popular": False,
                    "bonus_credits": 0,
                },
                {
                    "id": "pro_500",
                    "name": "Pro Pack",
                    "credits": 500,
                    "price_cents": 4999,
                    "price_display": "$49.99",
                    "popular": True,
                    "bonus_credits": 50,
                },
            ],
            "currency": "USD",
        }

        client = AsyncLlamaSearch(
            api_key="test_key",
        )

        with patch.object(client, "_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response

            result = await client.get_credit_packages()

            assert isinstance(result, CreditPackagesResponse)
            assert len(result.packages) == 2
            assert result.currency == "USD"
            assert result.packages[0].id == "basic_100"
            assert result.packages[1].popular is True

            mock_request.assert_called_once_with("GET", "/billing/packages")

        await client.close()

    @pytest.mark.asyncio
    async def test_get_purchase_history_success(self):
        """Test successful purchase history retrieval"""
        created_at = datetime.now() - timedelta(days=2)
        completed_at = datetime.now() - timedelta(days=2, hours=1)

        mock_response_data = {
            "purchases": [
                {
                    "id": "pur_123",
                    "package_name": "Basic Pack",
                    "credits": 100,
                    "price_cents": 999,
                    "status": "completed",
                    "created_at": created_at.isoformat(),
                    "completed_at": completed_at.isoformat(),
                    "session_id": "cs_123",
                },
                {
                    "id": "pur_124",
                    "package_name": "Pro Pack",
                    "credits": 500,
                    "price_cents": 4999,
                    "status": "completed",
                    "created_at": (created_at - timedelta(days=1)).isoformat(),
                    "completed_at": (completed_at - timedelta(days=1)).isoformat(),
                    "session_id": "cs_124",
                },
            ],
            "total_spent_cents": 5998,
            "total_credits_purchased": 600,
        }

        client = AsyncLlamaSearch(
            api_key="test_key",
        )

        with patch.object(client, "_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response

            result = await client.get_purchase_history(limit=20)

            assert isinstance(result, PurchaseHistory)
            assert len(result.purchases) == 2
            assert result.total_spent_cents == 5998
            assert result.total_credits_purchased == 600
            assert result.purchases[0].id == "pur_123"
            assert result.purchases[0].status == "completed"

            mock_request.assert_called_once_with("GET", "/billing/history", params={"limit": 20})

        await client.close()

    @pytest.mark.asyncio
    async def test_get_purchase_history_validation_errors(self):
        """Test purchase history with invalid limit values"""
        client = AsyncLlamaSearch(
            api_key="test_key",
        )

        # Limit too low
        with pytest.raises(ValidationError) as exc_info:
            await client.get_purchase_history(limit=0)
        assert exc_info.value.field == "limit"

        # Limit too high
        with pytest.raises(ValidationError) as exc_info:
            await client.get_purchase_history(limit=100)
        assert exc_info.value.field == "limit"

        await client.close()

    @pytest.mark.asyncio
    async def test_payment_error_handling_in_http_errors(self):
        """Test payment error handling in _handle_http_errors"""
        client = AsyncLlamaSearch(
            api_key="test_key",
        )

        # Test payment cancelled error
        mock_response = MagicMock()
        mock_response.status_code = 402
        mock_response.json.return_value = {
            "error_type": "payment_error",
            "message": "Payment was cancelled by user",
            "session_id": "cs_123",
        }

        with pytest.raises(PaymentCancelledError) as exc_info:
            client._handle_http_errors(mock_response)

        error = exc_info.value
        assert error.session_id == "cs_123"
        assert "cancelled" in str(error).lower()

        # Test payment failed error
        mock_response.json.return_value = {
            "error_type": "payment_error",
            "message": "Payment failed due to insufficient funds",
            "session_id": "cs_124",
            "failure_reason": "insufficient_funds",
        }

        with pytest.raises(PaymentFailedError) as exc_info:
            client._handle_http_errors(mock_response)

        error = exc_info.value
        assert error.session_id == "cs_124"
        assert error.failure_reason == "insufficient_funds"

        # Test generic payment error
        mock_response.json.return_value = {
            "error_type": "payment_error",
            "message": "Payment processing error",
            "session_id": "cs_125",
        }

        with pytest.raises(PaymentError) as exc_info:
            client._handle_http_errors(mock_response)

        error = exc_info.value
        assert error.session_id == "cs_125"

        await client.close()


class TestSyncBillingClient:
    """Tests for synchronous billing client"""

    def test_sync_get_credit_packages(self):
        """Test sync version of get_credit_packages"""
        from llama_search import LlamaSearch

        mock_response_data = {
            "packages": [
                {
                    "id": "basic_100",
                    "name": "Basic Pack",
                    "credits": 100,
                    "price_cents": 999,
                    "price_display": "$9.99",
                    "popular": False,
                    "bonus_credits": 0,
                }
            ],
            "currency": "USD",
        }

        with patch("asyncio.run") as mock_run:
            mock_run.return_value = CreditPackagesResponse.model_validate(mock_response_data)

            client = LlamaSearch(api_key="test_key")
            result = client.get_credit_packages()

            assert isinstance(result, CreditPackagesResponse)
            assert len(result.packages) == 1
            mock_run.assert_called_once()

    def test_sync_get_purchase_history(self):
        """Test sync version of get_purchase_history"""
        from llama_search import LlamaSearch

        mock_response_data = {"purchases": [], "total_spent_cents": 0, "total_credits_purchased": 0}

        with patch("asyncio.run") as mock_run:
            mock_run.return_value = PurchaseHistory.model_validate(mock_response_data)

            client = LlamaSearch(api_key="test_key")
            result = client.get_purchase_history(limit=10)

            assert isinstance(result, PurchaseHistory)
            assert len(result.purchases) == 0
            mock_run.assert_called_once()
