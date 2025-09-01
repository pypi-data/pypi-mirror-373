"""Tests for billing functionality"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from llama_search import AsyncLlamaSearch
from llama_search._exceptions import (
    PaymentError,
    PaymentCancelledError,
    PaymentFailedError,
    ValidationError,
    LlamaSearchError,
)
from llama_search.types.billing import (
    CreditPackage,
    CreditPackagesResponse,
    PurchaseSession,
    PaymentStatus,
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

    def test_purchase_session_model(self):
        """Test PurchaseSession model validation"""
        expires_at = datetime.now() + timedelta(hours=1)
        session = PurchaseSession(
            session_id="cs_123",
            checkout_url="https://checkout.stripe.com/pay/cs_123",
            expires_at=expires_at,
            package_id="basic_100",
            credits=100,
            price_cents=999,
        )

        assert session.session_id == "cs_123"
        assert session.checkout_url == "https://checkout.stripe.com/pay/cs_123"
        assert session.expires_at == expires_at
        assert session.package_id == "basic_100"
        assert session.credits == 100
        assert session.price_cents == 999

    def test_payment_status_model(self):
        """Test PaymentStatus model validation"""
        completed_at = datetime.now()
        status = PaymentStatus(
            session_id="cs_123",
            status="completed",
            credits_added=100,
            completed_at=completed_at,
            error_message=None,
        )

        assert status.session_id == "cs_123"
        assert status.status == "completed"
        assert status.credits_added == 100
        assert status.completed_at == completed_at
        assert status.error_message is None

    def test_payment_status_failed(self):
        """Test PaymentStatus model with failure"""
        status = PaymentStatus(
            session_id="cs_123",
            status="failed",
            credits_added=None,
            completed_at=None,
            error_message="Card declined",
        )

        assert status.status == "failed"
        assert status.credits_added is None
        assert status.error_message == "Card declined"

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

        client = AsyncLlamaSearch(api_key="test_key", enable_circuit_breaker=False)

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
    async def test_create_purchase_session_success(self):
        """Test successful purchase session creation"""
        expires_at = datetime.now() + timedelta(hours=1)
        mock_response_data = {
            "session_id": "cs_123456789",
            "checkout_url": "https://checkout.stripe.com/pay/cs_123456789#fidkdWxOYHwnPyd1blppbHNgWjA0PUxicHdrcHM9dDJKVW1dTzRnT3w9Y2lhN0RpZ3pRRE5VZG5hRXVLME5HTTRCfHZKZkdCY0pKXUJKNTZTZ318ZXQ%3D",
            "expires_at": expires_at.isoformat(),
            "package_id": "basic_100",
            "credits": 100,
            "price_cents": 999,
        }

        client = AsyncLlamaSearch(api_key="test_key", enable_circuit_breaker=False)

        with patch.object(client, "_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response

            result = await client.create_purchase_session(
                package_id="basic_100",
                success_url="https://app.com/success",
                cancel_url="https://app.com/cancel",
            )

            assert isinstance(result, PurchaseSession)
            assert result.session_id == "cs_123456789"
            assert result.package_id == "basic_100"
            assert result.credits == 100
            assert result.price_cents == 999
            assert "checkout.stripe.com" in result.checkout_url

            mock_request.assert_called_once_with(
                "POST",
                "/billing/purchase",
                json={
                    "package_id": "basic_100",
                    "success_url": "https://app.com/success",
                    "cancel_url": "https://app.com/cancel",
                },
            )

        await client.close()

    @pytest.mark.asyncio
    async def test_create_purchase_session_validation_errors(self):
        """Test purchase session creation with validation errors"""
        client = AsyncLlamaSearch(api_key="test_key", enable_circuit_breaker=False)

        # Empty package_id
        with pytest.raises(ValidationError) as exc_info:
            await client.create_purchase_session("", "https://success.com", "https://cancel.com")
        assert exc_info.value.field == "package_id"

        # Empty success_url
        with pytest.raises(ValidationError) as exc_info:
            await client.create_purchase_session("pkg_123", "", "https://cancel.com")
        assert exc_info.value.field == "success_url"

        # Empty cancel_url
        with pytest.raises(ValidationError) as exc_info:
            await client.create_purchase_session("pkg_123", "https://success.com", "")
        assert exc_info.value.field == "cancel_url"

        await client.close()

    @pytest.mark.asyncio
    async def test_get_payment_status_success(self):
        """Test successful payment status retrieval"""
        completed_at = datetime.now()
        mock_response_data = {
            "session_id": "cs_123456789",
            "status": "completed",
            "credits_added": 100,
            "completed_at": completed_at.isoformat(),
            "error_message": None,
        }

        client = AsyncLlamaSearch(api_key="test_key", enable_circuit_breaker=False)

        with patch.object(client, "_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response

            result = await client.get_payment_status("cs_123456789")

            assert isinstance(result, PaymentStatus)
            assert result.session_id == "cs_123456789"
            assert result.status == "completed"
            assert result.credits_added == 100
            assert result.error_message is None

            mock_request.assert_called_once_with(
                "GET", "/billing/status", params={"session_id": "cs_123456789"}
            )

        await client.close()

    @pytest.mark.asyncio
    async def test_get_payment_status_failed(self):
        """Test payment status for failed payment"""
        mock_response_data = {
            "session_id": "cs_123456789",
            "status": "failed",
            "credits_added": None,
            "completed_at": None,
            "error_message": "Your card was declined.",
        }

        client = AsyncLlamaSearch(api_key="test_key", enable_circuit_breaker=False)

        with patch.object(client, "_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response

            result = await client.get_payment_status("cs_123456789")

            assert result.status == "failed"
            assert result.credits_added is None
            assert result.error_message == "Your card was declined."

        await client.close()

    @pytest.mark.asyncio
    async def test_get_payment_status_validation_error(self):
        """Test payment status with empty session ID"""
        client = AsyncLlamaSearch(api_key="test_key", enable_circuit_breaker=False)

        with pytest.raises(ValidationError) as exc_info:
            await client.get_payment_status("")
        assert exc_info.value.field == "session_id"

        with pytest.raises(ValidationError) as exc_info:
            await client.get_payment_status("   ")
        assert exc_info.value.field == "session_id"

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

        client = AsyncLlamaSearch(api_key="test_key", enable_circuit_breaker=False)

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
        client = AsyncLlamaSearch(api_key="test_key", enable_circuit_breaker=False)

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
        client = AsyncLlamaSearch(api_key="test_key", enable_circuit_breaker=False)

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

    def test_sync_create_purchase_session(self):
        """Test sync version of create_purchase_session"""
        from llama_search import LlamaSearch

        expires_at = datetime.now() + timedelta(hours=1)
        mock_response_data = {
            "session_id": "cs_123",
            "checkout_url": "https://checkout.stripe.com/pay/cs_123",
            "expires_at": expires_at.isoformat(),
            "package_id": "basic_100",
            "credits": 100,
            "price_cents": 999,
        }

        with patch("asyncio.run") as mock_run:
            mock_run.return_value = PurchaseSession.model_validate(mock_response_data)

            client = LlamaSearch(api_key="test_key")
            result = client.create_purchase_session(
                "basic_100", "https://success.com", "https://cancel.com"
            )

            assert isinstance(result, PurchaseSession)
            assert result.session_id == "cs_123"
            mock_run.assert_called_once()

    def test_sync_get_payment_status(self):
        """Test sync version of get_payment_status"""
        from llama_search import LlamaSearch

        mock_response_data = {
            "session_id": "cs_123",
            "status": "completed",
            "credits_added": 100,
            "completed_at": datetime.now().isoformat(),
            "error_message": None,
        }

        with patch("asyncio.run") as mock_run:
            mock_run.return_value = PaymentStatus.model_validate(mock_response_data)

            client = LlamaSearch(api_key="test_key")
            result = client.get_payment_status("cs_123")

            assert isinstance(result, PaymentStatus)
            assert result.status == "completed"
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
