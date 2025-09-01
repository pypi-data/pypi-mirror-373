"""Advanced retry logic with exponential backoff and circuit breaker"""

import asyncio
import random
from typing import List, Optional, Callable, Type
from enum import Enum
import logging


from ._exceptions import (
    NetworkError,
    ServerError,
    RateLimitError,
    TimeoutError,
    RetryExhaustedError,
)

logger = logging.getLogger(__name__)


class RetryPolicy(Enum):
    """Retry policy types"""

    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_INTERVAL = "fixed_interval"
    NO_RETRY = "no_retry"


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


class RetryManager:
    """Manages retry logic"""

    def __init__(self, retry_config: RetryConfig):
        self.retry_config = retry_config

    async def execute_with_retry(self, operation: Callable, *args, **kwargs):  # type: ignore
        """Execute an operation with retry logic"""

        last_exception = None

        for attempt in range(self.retry_config.max_retries + 1):
            try:
                result = await operation(*args, **kwargs)
                return result

            except Exception as e:
                last_exception = e

                # Check if we should retry this exception
                if not self._should_retry(e, attempt):
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

    return RetryManager(retry_config)


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

    return RetryManager(retry_config)


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

    return RetryManager(retry_config)
