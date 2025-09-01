"""Custom exceptions for the Llama Search SDK"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class LlamaSearchError(Exception):
    """Base exception for all Llama Search SDK errors"""

    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message)
        self.error_code = error_code
        self.timestamp = datetime.now()


class AuthenticationError(LlamaSearchError):
    """Invalid API key or authentication failure"""

    def __init__(self, message: str = "Invalid API key", error_code: str = "AUTH_FAILED"):
        super().__init__(message, error_code)


class InsufficientCreditsError(LlamaSearchError):
    """Not enough credits to perform the operation"""

    def __init__(
        self,
        message: str,
        credits_required: Optional[int] = None,
        credits_available: Optional[int] = None,
        error_code: str = "INSUFFICIENT_CREDITS",
    ):
        super().__init__(message, error_code)
        self.credits_required = credits_required
        self.credits_available = credits_available


class RateLimitError(LlamaSearchError):
    """Rate limit exceeded"""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        error_code: str = "RATE_LIMITED",
    ):
        super().__init__(message, error_code)
        self.retry_after = retry_after
        self.retry_after_datetime = (
            datetime.now() + timedelta(seconds=retry_after) if retry_after else None
        )


class ValidationError(LlamaSearchError):
    """Invalid request parameters"""

    def __init__(
        self, message: str, field: Optional[str] = None, error_code: str = "VALIDATION_ERROR"
    ):
        super().__init__(message, error_code)
        self.field = field


class ServerError(LlamaSearchError):
    """Internal server errors (5xx responses)"""

    def __init__(
        self, message: str, status_code: Optional[int] = None, error_code: str = "SERVER_ERROR"
    ):
        super().__init__(message, error_code)
        self.status_code = status_code


class NetworkError(LlamaSearchError):
    """Network connection issues"""

    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        error_code: str = "NETWORK_ERROR",
    ):
        super().__init__(message, error_code)
        self.original_error = original_error


class TimeoutError(LlamaSearchError):
    """Request timeout"""

    def __init__(
        self,
        message: str = "Request timed out",
        timeout_duration: Optional[float] = None,
        error_code: str = "TIMEOUT",
    ):
        super().__init__(message, error_code)
        self.timeout_duration = timeout_duration


class CircuitBreakerError(LlamaSearchError):
    """Circuit breaker is open, requests are being rejected"""

    def __init__(
        self,
        message: str = "Circuit breaker is open",
        failure_count: Optional[int] = None,
        next_attempt_time: Optional[datetime] = None,
        error_code: str = "CIRCUIT_BREAKER_OPEN",
    ):
        super().__init__(message, error_code)
        self.failure_count = failure_count
        self.next_attempt_time = next_attempt_time


class RetryExhaustedError(LlamaSearchError):
    """All retry attempts have been exhausted"""

    def __init__(
        self,
        message: str,
        attempts: int = 0,
        last_error: Optional[Exception] = None,
        error_code: str = "RETRY_EXHAUSTED",
    ):
        super().__init__(message, error_code)
        self.attempts = attempts
        self.last_error = last_error


class PaymentError(LlamaSearchError):
    """Payment processing error"""

    def __init__(
        self, message: str, session_id: Optional[str] = None, error_code: str = "PAYMENT_ERROR"
    ):
        super().__init__(message, error_code)
        self.session_id = session_id


class PaymentCancelledError(PaymentError):
    """Payment was cancelled by user"""

    def __init__(
        self,
        message: str = "Payment was cancelled",
        session_id: Optional[str] = None,
        error_code: str = "PAYMENT_CANCELLED",
    ):
        super().__init__(message, session_id, error_code)


class PaymentFailedError(PaymentError):
    """Payment processing failed"""

    def __init__(
        self,
        message: str = "Payment failed",
        session_id: Optional[str] = None,
        failure_reason: Optional[str] = None,
        error_code: str = "PAYMENT_FAILED",
    ):
        super().__init__(message, session_id, error_code)
        self.failure_reason = failure_reason
