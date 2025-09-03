"""Performance timing utilities.

Provides a decorator to warn when operations exceed a threshold.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import TypeVar

T = TypeVar("T")


def track_performance(
    threshold_seconds: float = 1.0, *, logger: logging.Logger | None = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to log a warning when a function exceeds a duration threshold."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                duration = time.perf_counter() - start
                if duration > threshold_seconds:
                    try:
                        (logger or logging.getLogger(__name__)).warning(
                            f"Slow operation: {func.__name__} took {duration:.2f}s "
                            f"(threshold: {threshold_seconds}s)"
                        )
                    except Exception:
                        pass

        return wrapper

    return decorator
