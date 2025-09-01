"""Advanced retry logic with exponential backoff and circuit breaker"""

import asyncio
import random
import time
from datetime import datetime, timedelta
from typing import List, Optional, Callable, Type, Union
from enum import Enum
import logging

from ._exceptions import (
    LlamaSearchError,
    NetworkError,
    ServerError,
    RateLimitError,
    TimeoutError,
    CircuitBreakerError,
    RetryExhaustedError,
)

logger = logging.getLogger(__name__)


class RetryPolicy(Enum):
    """Retry policy types"""

    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_INTERVAL = "fixed_interval"
    NO_RETRY = "no_retry"


class CircuitBreakerState(Enum):
    """Circuit breaker states"""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class RetryConfig:
    """Configuration for retry behavior"""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        policy: RetryPolicy = RetryPolicy.EXPONENTIAL_BACKOFF,
        jitter: bool = True,
        retry_on: Optional[List[Type[Exception]]] = None,
        no_retry_on: Optional[List[Type[Exception]]] = None,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.policy = policy
        self.jitter = jitter
        self.retry_on = retry_on or [NetworkError, ServerError, TimeoutError]
        self.no_retry_on = no_retry_on or [RateLimitError]  # Don't retry rate limits by default


class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior"""

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        success_threshold: int = 1,
        monitor_failures: bool = True,
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout  # How long to wait before trying again
        self.success_threshold = success_threshold  # Successes needed to close circuit
        self.monitor_failures = monitor_failures


class CircuitBreaker:
    """Circuit breaker implementation"""

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.next_attempt_time: Optional[datetime] = None

    def can_execute(self) -> bool:
        """Check if execution is allowed"""
        if self.state == CircuitBreakerState.CLOSED:
            return True

        if self.state == CircuitBreakerState.OPEN:
            if self.next_attempt_time and datetime.now() >= self.next_attempt_time:
                self.state = CircuitBreakerState.HALF_OPEN
                return True
            return False

        # HALF_OPEN state
        return True

    def record_success(self):
        """Record a successful operation"""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self._close_circuit()
        else:
            self.failure_count = max(0, self.failure_count - 1)

    def record_failure(self):
        """Record a failed operation"""
        self.failure_count += 1
        self.success_count = 0
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.config.failure_threshold:
            self._open_circuit()

    def _close_circuit(self):
        """Close the circuit breaker"""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.next_attempt_time = None
        logger.info("Circuit breaker closed")

    def _open_circuit(self):
        """Open the circuit breaker"""
        self.state = CircuitBreakerState.OPEN
        self.next_attempt_time = datetime.now() + timedelta(seconds=self.config.timeout)
        logger.warning(
            f"Circuit breaker opened after {self.failure_count} failures. "
            f"Next attempt allowed at {self.next_attempt_time}"
        )


class RetryManager:
    """Manages retry logic with circuit breaker support"""

    def __init__(
        self,
        retry_config: RetryConfig,
        circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
    ):
        self.retry_config = retry_config
        self.circuit_breaker = (
            CircuitBreaker(circuit_breaker_config) if circuit_breaker_config else None
        )

    async def execute_with_retry(self, operation: Callable, *args, **kwargs):
        """Execute an operation with retry and circuit breaker logic"""

        # Check circuit breaker first
        if self.circuit_breaker and not self.circuit_breaker.can_execute():
            raise CircuitBreakerError(
                message="Circuit breaker is open",
                failure_count=self.circuit_breaker.failure_count,
                next_attempt_time=self.circuit_breaker.next_attempt_time,
            )

        last_exception = None

        for attempt in range(self.retry_config.max_retries + 1):
            try:
                result = await operation(*args, **kwargs)

                # Record success in circuit breaker
                if self.circuit_breaker:
                    self.circuit_breaker.record_success()

                return result

            except Exception as e:
                last_exception = e

                # Check if we should retry this exception
                if not self._should_retry(e, attempt):
                    if self.circuit_breaker:
                        self.circuit_breaker.record_failure()
                    raise e

                # Don't retry on the last attempt
                if attempt >= self.retry_config.max_retries:
                    break

                # Calculate delay and wait
                delay = self._calculate_delay(attempt)

                logger.debug(
                    f"Attempt {attempt + 1} failed with {type(e).__name__}: {e}. "
                    f"Retrying in {delay:.2f}s"
                )

                await asyncio.sleep(delay)

        # All retries exhausted
        if self.circuit_breaker:
            self.circuit_breaker.record_failure()

        raise RetryExhaustedError(
            message=f"All retry attempts exhausted after {self.retry_config.max_retries + 1} attempts",
            attempts=self.retry_config.max_retries + 1,
            last_error=last_exception,
        )

    def _should_retry(self, exception: Exception, attempt: int) -> bool:
        """Determine if an exception should be retried"""

        # Check no-retry list first
        for no_retry_type in self.retry_config.no_retry_on:
            if isinstance(exception, no_retry_type):
                return False

        # Handle special case for rate limits with retry-after
        if isinstance(exception, RateLimitError) and exception.retry_after:
            # Only retry rate limits if we have retry-after info and it's reasonable
            return exception.retry_after <= 300  # Max 5 minutes

        # Check retry list
        for retry_type in self.retry_config.retry_on:
            if isinstance(exception, retry_type):
                return True

        return False

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for the given attempt"""
        if self.retry_config.policy == RetryPolicy.NO_RETRY:
            return 0

        elif self.retry_config.policy == RetryPolicy.FIXED_INTERVAL:
            delay = self.retry_config.base_delay

        elif self.retry_config.policy == RetryPolicy.LINEAR_BACKOFF:
            delay = self.retry_config.base_delay * (attempt + 1)

        elif self.retry_config.policy == RetryPolicy.EXPONENTIAL_BACKOFF:
            delay = self.retry_config.base_delay * (2**attempt)

        else:
            delay = self.retry_config.base_delay

        # Apply max delay limit
        delay = min(delay, self.retry_config.max_delay)

        # Add jitter to avoid thundering herd
        if self.retry_config.jitter:
            jitter_factor = random.uniform(0.8, 1.2)
            delay *= jitter_factor

        return delay


def create_default_retry_manager() -> RetryManager:
    """Create a retry manager with sensible defaults"""
    retry_config = RetryConfig(
        max_retries=3,
        base_delay=1.0,
        max_delay=30.0,
        policy=RetryPolicy.EXPONENTIAL_BACKOFF,
        jitter=True,
        retry_on=[NetworkError, ServerError, TimeoutError],
        no_retry_on=[RateLimitError],  # Handle rate limits specially
    )

    circuit_breaker_config = CircuitBreakerConfig(
        failure_threshold=5,
        timeout=60.0,
        success_threshold=1,
    )

    return RetryManager(retry_config, circuit_breaker_config)


def create_aggressive_retry_manager() -> RetryManager:
    """Create a retry manager with more aggressive retry settings"""
    retry_config = RetryConfig(
        max_retries=5,
        base_delay=0.5,
        max_delay=60.0,
        policy=RetryPolicy.EXPONENTIAL_BACKOFF,
        jitter=True,
        retry_on=[NetworkError, ServerError, TimeoutError, RateLimitError],
        no_retry_on=[],
    )

    circuit_breaker_config = CircuitBreakerConfig(
        failure_threshold=10,
        timeout=30.0,
        success_threshold=2,
    )

    return RetryManager(retry_config, circuit_breaker_config)


def create_conservative_retry_manager() -> RetryManager:
    """Create a retry manager with conservative settings"""
    retry_config = RetryConfig(
        max_retries=2,
        base_delay=2.0,
        max_delay=20.0,
        policy=RetryPolicy.LINEAR_BACKOFF,
        jitter=False,
        retry_on=[NetworkError],
        no_retry_on=[ServerError, RateLimitError, TimeoutError],
    )

    # No circuit breaker for conservative approach
    return RetryManager(retry_config, None)
