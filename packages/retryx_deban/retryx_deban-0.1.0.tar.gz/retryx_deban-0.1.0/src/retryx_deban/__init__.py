import asyncio
import functools
import random
import time
from typing import Callable, Any


def retry(max_attempts: int = 3, backoff: str = "fixed", delay: float = 1.0, jitter: bool = False):
    """
    Retry decorator for sync and async functions.
    Args:
        max_attempts (int): Maximum retry attempts.
        backoff (str): "fixed" or "exponential".
        delay (float): Base delay in seconds.
        jitter (bool): Add random jitter to delay.
    """

    def decorator(func: Callable):
        is_coroutine = asyncio.iscoroutinefunction(func)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        raise
                    sleep_time = _calculate_delay(delay, attempt, backoff, jitter)
                    print(f"[retryx] Attempt {attempt} failed: {e}. Retrying in {sleep_time:.2f}s")
                    time.sleep(sleep_time)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        raise
                    sleep_time = _calculate_delay(delay, attempt, backoff, jitter)
                    print(f"[retryx] Attempt {attempt} failed: {e}. Retrying in {sleep_time:.2f}s")
                    await asyncio.sleep(sleep_time)

        return async_wrapper if is_coroutine else sync_wrapper

    return decorator


def _calculate_delay(base: float, attempt: int, backoff: str, jitter: bool) -> float:
    if backoff == "exponential":
        delay = base * (2 ** (attempt - 1))
    else:
        delay = base
    if jitter:
        delay += random.uniform(0, base)
    return delay
