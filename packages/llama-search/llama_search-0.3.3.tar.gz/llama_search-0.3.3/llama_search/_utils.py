"""Utility functions for the Llama Search SDK"""

import asyncio
from typing import List


def get_retry_delays(max_retries: int, base_delay: float = 1.0) -> List[float]:
    """Generate exponential backoff delays"""
    return [base_delay * (2**i) for i in range(max_retries)]


async def sleep_with_jitter(delay: float, jitter_factor: float = 0.1) -> None:
    """Sleep with random jitter to avoid thundering herd"""
    import random

    jitter = random.uniform(-jitter_factor, jitter_factor)
    actual_delay = delay * (1 + jitter)
    await asyncio.sleep(actual_delay)
