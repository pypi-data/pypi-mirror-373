"""Tests for error handling and resilience features"""

import pytest
from unittest.mock import patch, MagicMock
import httpx

from llama_search import AsyncLlamaSearch
from llama_search._exceptions import (
    LlamaSearchError,
    AuthenticationError,
    InsufficientCreditsError,
    RateLimitError,
    ValidationError,
    ServerError,
    NetworkError,
    TimeoutError,
    RetryExhaustedError,
)
from llama_search._retry import (
    RetryConfig,
    RetryPolicy,
    RetryManager,
)
from llama_search._logging import RequestLogger


class TestEnhancedExceptions:
    """Tests for enhanced exception hierarchy"""

    def test_llama_search_error_base(self):
        """Test base exception class"""
        error = LlamaSearchError("Test error", "TEST_001")
        assert str(error) == "Test error"
        assert error.error_code == "TEST_001"

    def test_authentication_error(self):
        """Test authentication error with details"""
        error = AuthenticationError("Invalid API key", "AUTH_001")
        assert "Invalid API key" in str(error)
        assert error.error_code == "AUTH_001"

    def test_insufficient_credits_error(self):
        """Test insufficient credits error with credit info"""
        error = InsufficientCreditsError(
            "Not enough credits", credits_required=10, credits_available=3
        )
        assert error.credits_required == 10
        assert error.credits_available == 3
        assert "Not enough credits" in str(error)

    def test_rate_limit_error_with_retry_after(self):
        """Test rate limit error with retry-after information"""
        error = RateLimitError("Rate limit exceeded", retry_after=30)
        assert error.retry_after == 30
        assert "Rate limit exceeded" in str(error)

    def test_timeout_error_with_duration(self):
        """Test timeout error with duration information"""
        error = TimeoutError("Request timed out", timeout_duration=5.0)
        assert error.timeout_duration == 5.0
        assert "Request timed out" in str(error)

    def test_server_error_with_status_code(self):
        """Test server error with HTTP status code"""
        error = ServerError("Internal server error", status_code=500)
        assert error.status_code == 500
        assert "Internal server error" in str(error)

    def test_network_error_with_original_error(self):
        """Test network error with original exception"""
        original = ConnectionError("Connection refused")
        error = NetworkError("Network error", original_error=original)
        assert error.original_error is original
        assert "Network error" in str(error)

    def test_validation_error_with_field(self):
        """Test validation error with field information"""
        error = ValidationError("Invalid query", field="query")
        assert error.field == "query"
        assert "Invalid query" in str(error)

    def test_retry_exhausted_error(self):
        """Test retry exhausted error with attempt count"""
        original = NetworkError("Connection failed")
        error = RetryExhaustedError("All retries failed", attempts=3, last_error=original)
        assert error.attempts == 3
        assert error.last_error is original
        assert "All retries failed" in str(error)


class TestRetryConfig:
    """Tests for retry configuration"""

    def test_retry_config_defaults(self):
        """Test default retry configuration"""
        config = RetryConfig()
        assert config.max_retries == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0
        assert config.policy == RetryPolicy.EXPONENTIAL_BACKOFF
        assert config.jitter is True

    def test_retry_config_custom_values(self):
        """Test custom retry configuration"""
        config = RetryConfig(
            max_retries=5,
            base_delay=2.0,
            max_delay=120.0,
            policy=RetryPolicy.LINEAR_BACKOFF,
            jitter=False,
        )
        assert config.max_retries == 5
        assert config.base_delay == 2.0
        assert config.max_delay == 120.0
        assert config.policy == RetryPolicy.LINEAR_BACKOFF
        assert config.jitter is False

    def test_retry_config_exception_types(self):
        """Test retry configuration with custom exception types"""
        config = RetryConfig(retry_on=[NetworkError, TimeoutError], no_retry_on=[ValidationError])
        assert NetworkError in config.retry_on
        assert TimeoutError in config.retry_on
        assert ValidationError in config.no_retry_on


class TestRetryManager:
    """Tests for retry manager functionality"""

    @pytest.mark.asyncio
    async def test_retry_manager_success_on_first_try(self):
        """Test successful operation on first attempt"""
        config = RetryConfig(max_retries=2)
        retry_manager = RetryManager(config)

        async def successful_operation():
            return "success"

        result = await retry_manager.execute_with_retry(successful_operation)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_retry_manager_success_after_retries(self):
        """Test successful operation after some failures"""
        config = RetryConfig(max_retries=2, base_delay=0.01)  # Fast for testing
        retry_manager = RetryManager(config)

        call_count = 0

        async def eventually_successful_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise NetworkError("Network error")
            return "success"

        result = await retry_manager.execute_with_retry(eventually_successful_operation)
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_manager_exhaust_retries(self):
        """Test retry manager when all retries are exhausted"""
        config = RetryConfig(max_retries=2, base_delay=0.01)
        retry_manager = RetryManager(config)

        async def failing_operation():
            raise NetworkError("Network error")

        with pytest.raises(RetryExhaustedError) as exc_info:
            await retry_manager.execute_with_retry(failing_operation)

        error = exc_info.value
        assert error.attempts == 3  # max_retries + 1
        assert isinstance(error.last_error, NetworkError)

    @pytest.mark.asyncio
    async def test_retry_manager_no_retry_exception(self):
        """Test retry manager doesn't retry certain exceptions"""
        config = RetryConfig(max_retries=2, no_retry_on=[ValidationError])
        retry_manager = RetryManager(config)

        async def validation_error_operation():
            raise ValidationError("Invalid input")

        with pytest.raises(ValidationError):
            await retry_manager.execute_with_retry(validation_error_operation)


class TestRequestLogger:
    """Tests for request logging functionality"""

    def test_request_logger_basic(self):
        """Test basic request logger functionality"""
        logger = RequestLogger(debug=False)
        assert logger.debug is False

    def test_request_logger_debug_mode(self):
        """Test request logger in debug mode"""
        logger = RequestLogger(debug=True)
        assert logger.debug is True

    def test_request_logger_sanitizes_headers(self):
        """Test request logger sanitizes sensitive headers"""
        logger = RequestLogger(debug=True)
        headers = {"Authorization": "Bearer secret", "Content-Type": "application/json"}
        sanitized = logger._sanitize_headers(headers)
        assert sanitized["Authorization"] == "Bearer s..."
        assert sanitized["Content-Type"] == "application/json"

    def test_response_logging(self):
        """Test response logging"""
        logger = RequestLogger(debug=True)
        response = MagicMock()
        response.status_code = 200
        response.headers = {"Content-Type": "application/json"}
        response.json.return_value = {"result": "success"}

        # Should not raise exception
        logger.log_response("test-id", response, 100)

    def test_error_logging(self):
        """Test error logging"""
        logger = RequestLogger(debug=True)
        error = NetworkError("Connection failed")

        # Should not raise exception
        logger.log_error("test-id", error, 100)


class TestClientResilience:
    """Tests for client resilience features"""

    @pytest.mark.asyncio
    async def test_client_with_debug_logging(self):
        """Test client with debug logging enabled"""
        client = AsyncLlamaSearch(api_key="test_key", debug=True)
        assert client._debug is True
        await client.close()

    @pytest.mark.asyncio
    async def test_client_with_custom_retry_config(self):
        """Test client with custom retry configuration"""
        retry_config = RetryConfig(max_retries=5, base_delay=2.0)
        client = AsyncLlamaSearch(api_key="test_key", retry_config=retry_config)

        assert client._retry_manager is not None
        assert client._retry_manager.retry_config.max_retries == 5
        assert client._retry_manager.retry_config.base_delay == 2.0

        await client.close()

    @pytest.mark.asyncio
    async def test_enhanced_error_handling(self):
        """Test enhanced error handling with detailed error messages"""
        client = AsyncLlamaSearch(api_key="test_key", timeout=0.001)  # Very short timeout

        with patch.object(client._client, "request") as mock_request:
            # Test different error scenarios - create a proper mock response
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.headers = {}
            mock_request.return_value = mock_response

            with pytest.raises(RetryExhaustedError):
                await client.web_search("test query")

        await client.close()

    @pytest.mark.asyncio
    async def test_timeout_error_handling(self):
        """Test timeout error handling"""
        client = AsyncLlamaSearch(api_key="test_key", timeout=0.001)  # Very short timeout

        with patch.object(client._client, "request") as mock_request:
            mock_request.side_effect = httpx.TimeoutException("Request timed out")

            with pytest.raises(RetryExhaustedError) as exc_info:
                await client.web_search("test query")

            error = exc_info.value
            # Check that the last error was a TimeoutError
            assert isinstance(error.last_error, TimeoutError)
            assert error.last_error.timeout_duration == 0.001
            assert "timed out" in str(error.last_error)

        await client.close()
