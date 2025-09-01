"""Tests for error handling and resilience features"""

import asyncio
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
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
    CircuitBreakerError,
    RetryExhaustedError,
)
from llama_search._retry import (
    RetryConfig,
    RetryPolicy,
    CircuitBreakerConfig,
    RetryManager,
    CircuitBreaker,
    CircuitBreakerState,
)
from llama_search._logging import RequestLogger


class TestEnhancedExceptions:
    """Tests for enhanced exception hierarchy"""

    def test_llama_search_error_base(self):
        """Test base LlamaSearchError properties"""
        error = LlamaSearchError("Test error", error_code="TEST_ERROR")
        assert str(error) == "Test error"
        assert error.error_code == "TEST_ERROR"
        assert isinstance(error.timestamp, datetime)

    def test_authentication_error(self):
        """Test AuthenticationError with defaults"""
        error = AuthenticationError()
        assert str(error) == "Invalid API key"
        assert error.error_code == "AUTH_FAILED"

    def test_insufficient_credits_error_with_details(self):
        """Test InsufficientCreditsError with credit details"""
        error = InsufficientCreditsError(
            "Not enough credits", credits_required=10, credits_available=5
        )
        assert error.credits_required == 10
        assert error.credits_available == 5
        assert error.error_code == "INSUFFICIENT_CREDITS"

    def test_rate_limit_error_with_retry_after(self):
        """Test RateLimitError with retry-after information"""
        error = RateLimitError(retry_after=120)
        assert error.retry_after == 120
        assert isinstance(error.retry_after_datetime, datetime)

        # Check that retry_after_datetime is approximately 2 minutes from now
        expected_time = datetime.now() + timedelta(seconds=120)
        time_diff = abs((error.retry_after_datetime - expected_time).total_seconds())
        assert time_diff < 2  # Allow 2 second tolerance

    def test_validation_error_with_field(self):
        """Test ValidationError with field information"""
        error = ValidationError("Invalid query", field="query")
        assert error.field == "query"
        assert error.error_code == "VALIDATION_ERROR"

    def test_server_error_with_status_code(self):
        """Test ServerError with status code"""
        error = ServerError("Internal server error", status_code=500)
        assert error.status_code == 500
        assert error.error_code == "SERVER_ERROR"

    def test_network_error_with_original_error(self):
        """Test NetworkError with original exception"""
        original = ConnectionError("Connection failed")
        error = NetworkError("Network error", original_error=original)
        assert error.original_error == original
        assert error.error_code == "NETWORK_ERROR"

    def test_timeout_error_with_duration(self):
        """Test TimeoutError with timeout duration"""
        error = TimeoutError(timeout_duration=30.0)
        assert error.timeout_duration == 30.0
        assert error.error_code == "TIMEOUT"

    def test_circuit_breaker_error_with_details(self):
        """Test CircuitBreakerError with failure details"""
        next_attempt = datetime.now() + timedelta(minutes=5)
        error = CircuitBreakerError(failure_count=5, next_attempt_time=next_attempt)
        assert error.failure_count == 5
        assert error.next_attempt_time == next_attempt

    def test_retry_exhausted_error_with_details(self):
        """Test RetryExhaustedError with retry details"""
        original_error = NetworkError("Connection failed")
        error = RetryExhaustedError("All retries exhausted", attempts=3, last_error=original_error)
        assert error.attempts == 3
        assert error.last_error == original_error


class TestRetryConfig:
    """Tests for retry configuration"""

    def test_default_retry_config(self):
        """Test default retry configuration"""
        config = RetryConfig()
        assert config.max_retries == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0
        assert config.policy == RetryPolicy.EXPONENTIAL_BACKOFF
        assert config.jitter is True
        assert NetworkError in config.retry_on
        assert RateLimitError in config.no_retry_on

    def test_custom_retry_config(self):
        """Test custom retry configuration"""
        config = RetryConfig(
            max_retries=5,
            base_delay=2.0,
            policy=RetryPolicy.LINEAR_BACKOFF,
            jitter=False,
            retry_on=[NetworkError],
            no_retry_on=[ServerError, RateLimitError],
        )
        assert config.max_retries == 5
        assert config.base_delay == 2.0
        assert config.policy == RetryPolicy.LINEAR_BACKOFF
        assert config.jitter is False
        assert config.retry_on == [NetworkError]
        assert ServerError in config.no_retry_on


class TestCircuitBreaker:
    """Tests for circuit breaker functionality"""

    def test_circuit_breaker_initial_state(self):
        """Test circuit breaker starts in closed state"""
        config = CircuitBreakerConfig(failure_threshold=3)
        circuit_breaker = CircuitBreaker(config)

        assert circuit_breaker.state == CircuitBreakerState.CLOSED
        assert circuit_breaker.can_execute() is True
        assert circuit_breaker.failure_count == 0

    def test_circuit_breaker_opens_after_failures(self):
        """Test circuit breaker opens after threshold failures"""
        config = CircuitBreakerConfig(failure_threshold=3, timeout=60.0)
        circuit_breaker = CircuitBreaker(config)

        # Record failures up to threshold
        for i in range(3):
            circuit_breaker.record_failure()

        assert circuit_breaker.state == CircuitBreakerState.OPEN
        assert circuit_breaker.can_execute() is False
        assert isinstance(circuit_breaker.next_attempt_time, datetime)

    def test_circuit_breaker_half_open_after_timeout(self):
        """Test circuit breaker moves to half-open after timeout"""
        config = CircuitBreakerConfig(failure_threshold=2, timeout=0.1)  # 100ms timeout
        circuit_breaker = CircuitBreaker(config)

        # Open the circuit
        circuit_breaker.record_failure()
        circuit_breaker.record_failure()
        assert circuit_breaker.state == CircuitBreakerState.OPEN

        # Wait for timeout and check
        import time

        time.sleep(0.2)  # Wait longer than timeout
        assert circuit_breaker.can_execute() is True
        # The can_execute() call should have moved it to HALF_OPEN
        assert circuit_breaker.state == CircuitBreakerState.HALF_OPEN

    def test_circuit_breaker_closes_after_success(self):
        """Test circuit breaker closes after successful operations in half-open state"""
        config = CircuitBreakerConfig(failure_threshold=2, success_threshold=1)
        circuit_breaker = CircuitBreaker(config)

        # Open the circuit
        circuit_breaker.record_failure()
        circuit_breaker.record_failure()

        # Move to half-open manually
        circuit_breaker.state = CircuitBreakerState.HALF_OPEN

        # Record success
        circuit_breaker.record_success()

        assert circuit_breaker.state == CircuitBreakerState.CLOSED
        assert circuit_breaker.failure_count == 0


class TestRetryManager:
    """Tests for retry manager functionality"""

    @pytest.mark.asyncio
    async def test_retry_manager_success_no_retry(self):
        """Test successful operation requires no retry"""
        config = RetryConfig(max_retries=3)
        retry_manager = RetryManager(config)

        async def successful_operation():
            return "success"

        result = await retry_manager.execute_with_retry(successful_operation)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_retry_manager_retries_network_error(self):
        """Test retry manager retries network errors"""
        config = RetryConfig(max_retries=2, base_delay=0.01)  # Very short delay for testing
        retry_manager = RetryManager(config)

        attempt_count = 0

        async def failing_operation():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise NetworkError("Network error")
            return "success"

        result = await retry_manager.execute_with_retry(failing_operation)
        assert result == "success"
        assert attempt_count == 3  # 1 initial + 2 retries

    @pytest.mark.asyncio
    async def test_retry_manager_no_retry_on_auth_error(self):
        """Test retry manager doesn't retry authentication errors"""
        config = RetryConfig(max_retries=3, no_retry_on=[AuthenticationError])
        retry_manager = RetryManager(config)

        async def auth_failing_operation():
            raise AuthenticationError("Invalid API key")

        with pytest.raises(AuthenticationError):
            await retry_manager.execute_with_retry(auth_failing_operation)

    @pytest.mark.asyncio
    async def test_retry_manager_exhausted_retries(self):
        """Test retry manager raises RetryExhaustedError after all attempts"""
        config = RetryConfig(max_retries=2, base_delay=0.01)
        retry_manager = RetryManager(config)

        async def always_failing_operation():
            raise NetworkError("Always fails")

        with pytest.raises(RetryExhaustedError) as exc_info:
            await retry_manager.execute_with_retry(always_failing_operation)

        error = exc_info.value
        assert error.attempts == 3  # 1 initial + 2 retries
        assert isinstance(error.last_error, NetworkError)

    @pytest.mark.asyncio
    async def test_retry_manager_with_circuit_breaker(self):
        """Test retry manager with circuit breaker integration"""
        retry_config = RetryConfig(max_retries=2)
        cb_config = CircuitBreakerConfig(failure_threshold=2, timeout=0.1)
        retry_manager = RetryManager(retry_config, cb_config)

        async def failing_operation():
            raise NetworkError("Network error")

        # First call should exhaust retries and open circuit
        with pytest.raises(RetryExhaustedError):
            await retry_manager.execute_with_retry(failing_operation)

        # Second call should be rejected by circuit breaker
        with pytest.raises(CircuitBreakerError):
            await retry_manager.execute_with_retry(failing_operation)


class TestRequestLogger:
    """Tests for request logging functionality"""

    def test_request_logger_basic(self):
        """Test basic request logging"""
        logger = RequestLogger(debug=False)

        with patch.object(logger.logger, "info") as mock_info:
            request_id = logger.log_request(
                method="POST",
                url="https://api.llamasearch.ai/search/web",
                headers={"Authorization": "Bearer test_key"},
                body={"query": "test"},
            )

            assert request_id.startswith("req_")
            mock_info.assert_called_once()

    def test_request_logger_debug_mode(self):
        """Test request logging in debug mode"""
        logger = RequestLogger(debug=True)

        with patch.object(logger.logger, "debug") as mock_debug:
            logger.log_request(
                method="POST",
                url="https://api.llamasearch.ai/search/web",
                headers={"Authorization": "Bearer test_key"},
                body={"query": "test"},
            )

            mock_debug.assert_called_once()

    def test_request_logger_sanitizes_headers(self):
        """Test request logger sanitizes sensitive headers"""
        logger = RequestLogger(debug=True)

        headers = {
            "Authorization": "Bearer very_long_secret_key_12345",
            "Content-Type": "application/json",
        }

        sanitized = logger._sanitize_headers(headers)
        assert sanitized["Authorization"] == "Bearer v..."
        assert sanitized["Content-Type"] == "application/json"

    def test_response_logging(self):
        """Test response logging"""
        logger = RequestLogger(debug=False)

        # Mock httpx response
        response = MagicMock()
        response.status_code = 200
        response.headers = {"content-type": "application/json"}

        with patch.object(logger.logger, "info") as mock_info:
            logger.log_response("req_123", response, 150)
            mock_info.assert_called_once()

    def test_error_logging(self):
        """Test error logging"""
        logger = RequestLogger(debug=False)
        error = NetworkError("Connection failed")

        with patch.object(logger.logger, "warning") as mock_warning:
            logger.log_error("req_123", error, 500)
            mock_warning.assert_called_once()


class TestClientResilience:
    """Integration tests for client resilience features"""

    @pytest.mark.asyncio
    async def test_client_with_debug_logging(self):
        """Test client with debug logging enabled"""
        with patch("llama_search.client.setup_logging") as mock_setup:
            client = AsyncLlamaSearch(api_key="test_key", debug=True)
            mock_setup.assert_called_once_with(level="DEBUG", enable_debug=True)
            assert client._debug is True
            await client.close()

    @pytest.mark.asyncio
    async def test_client_with_custom_retry_config(self):
        """Test client with custom retry configuration"""
        retry_config = RetryConfig(max_retries=5, base_delay=0.5, policy=RetryPolicy.LINEAR_BACKOFF)

        client = AsyncLlamaSearch(api_key="test_key", retry_config=retry_config)

        assert client._retry_manager.retry_config.max_retries == 5
        assert client._retry_manager.retry_config.base_delay == 0.5
        assert client._retry_manager.retry_config.policy == RetryPolicy.LINEAR_BACKOFF
        await client.close()

    @pytest.mark.asyncio
    async def test_client_without_circuit_breaker(self):
        """Test client with circuit breaker disabled"""
        client = AsyncLlamaSearch(api_key="test_key", enable_circuit_breaker=False)

        # Client should still have retry manager but no circuit breaker
        assert client._retry_manager is None
        await client.close()

    @pytest.mark.asyncio
    async def test_enhanced_error_handling(self):
        """Test enhanced HTTP error handling"""
        client = AsyncLlamaSearch(api_key="test_key", enable_circuit_breaker=False)

        # Mock a 429 response with retry-after header
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {"retry-after": "60"}

        with pytest.raises(RateLimitError) as exc_info:
            client._handle_http_errors(mock_response)

        error = exc_info.value
        assert error.retry_after == 60
        assert isinstance(error.retry_after_datetime, datetime)

        await client.close()

    @pytest.mark.asyncio
    async def test_timeout_error_handling(self):
        """Test timeout error handling"""
        client = AsyncLlamaSearch(api_key="test_key", timeout=0.001)  # Very short timeout

        with patch.object(client._client, "request") as mock_request:
            mock_request.side_effect = httpx.TimeoutException("Request timed out")

            with pytest.raises(TimeoutError) as exc_info:
                await client.web_search("test query")

            error = exc_info.value
            assert error.timeout_duration == 0.001
            assert "timed out" in str(error)

        await client.close()
