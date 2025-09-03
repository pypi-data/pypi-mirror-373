"""DEPRECATED: use flow.adapters.resilience.retry.

This module provides backward-compatible wrappers and emits DeprecationWarning.
"""

from __future__ import annotations

import logging
import random
import time
import warnings
from collections.abc import Callable
from functools import wraps
from typing import TypeVar

from flow.adapters.resilience.retry import (
    ExponentialBackoffPolicy,
)
from flow.adapters.resilience.retry import (
    with_retry as _with_retry,
)
from flow.errors import NetworkError, TimeoutError

logger = logging.getLogger(__name__)
T = TypeVar("T")


def with_retry(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retriable_exceptions: tuple[type[Exception], ...] = (NetworkError, TimeoutError),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Deprecated wrapper; use adapters.resilience.retry.with_retry.

    Jitter is approximated via policy delays; exact jitter is no longer applied here.
    """
    warnings.warn(
        "flow.adapters.resilience.retry.with_retry is deprecated; use "
        "flow.adapters.resilience.retry.with_retry",
        DeprecationWarning,
        stacklevel=2,
    )
    policy = ExponentialBackoffPolicy(
        max_attempts=max_attempts,
        initial_delay=initial_delay,
        max_delay=max_delay,
        exponential_base=exponential_base,
    )
    # jitter is not modeled in the new helper; callers relying on jitter can introduce it in call-site
    return _with_retry(policy=policy, retryable_exceptions=retriable_exceptions)


class RetryableOperation:
    """Deprecated context manager; consider using with_retry instead."""

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

        self.attempt = 0
        self.succeeded = False
        self.last_exception = None
        self.total_delay = 0.0

        warnings.warn(
            "RetryableOperation is deprecated; prefer with_retry decorator",
            DeprecationWarning,
            stacklevel=2,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.succeeded and self.last_exception:
            raise self.last_exception

    def should_retry(self) -> bool:
        return self.attempt < self.max_attempts and not self.succeeded

    def success(self):
        self.succeeded = True

    def failure(self, exception: Exception):
        self.last_exception = exception
        self.attempt += 1
        if self.attempt < self.max_attempts:
            delay = self._calculate_delay()
            logger.debug(
                f"Retry {self.attempt}/{self.max_attempts} after {delay:.1f}s: {exception}"
            )
            time.sleep(delay)
            self.total_delay += delay

    def _calculate_delay(self) -> float:
        delay = min(
            self.initial_delay * (self.exponential_base ** (self.attempt - 1)), self.max_delay
        )
        if self.jitter:
            delay *= 0.5 + random.random()
        return delay


def retry_on_network_error(func: Callable[..., T]) -> Callable[..., T]:
    """Deprecated; forwards to with_retry with network exceptions."""
    warnings.warn(
        "retry_on_network_error is deprecated; use with_retry(policy=..., retryable_exceptions=...)",
        DeprecationWarning,
        stacklevel=2,
    )
    return with_retry(
        max_attempts=3,
        initial_delay=1.0,
        retriable_exceptions=(NetworkError, ConnectionError, TimeoutError),
    )(func)


def retry_with_logging(
    logger, level: str = "warning"
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Deprecated; implements logging using RetryableOperation shim."""

    warnings.warn(
        "retry_with_logging is deprecated; wrap with with_retry and add logging at call-sites",
        DeprecationWarning,
        stacklevel=2,
    )

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            with RetryableOperation() as retry:
                while retry.should_retry():
                    try:
                        result = func(*args, **kwargs)
                        retry.success()
                        if retry.attempt > 1:
                            getattr(logger, level)(
                                f"{func.__name__} succeeded after {retry.attempt} attempts "
                                f"({retry.total_delay:.1f}s total delay)"
                            )
                        return result
                    except Exception as e:
                        retry.failure(e)
                        if retry.attempt < retry.max_attempts:
                            getattr(logger, level)(
                                f"{func.__name__} attempt {retry.attempt} failed: {e}"
                            )
                        else:
                            logger.error(
                                f"{func.__name__} failed after {retry.attempt} attempts: {e}"
                            )
                            raise

        return wrapper

    return decorator
