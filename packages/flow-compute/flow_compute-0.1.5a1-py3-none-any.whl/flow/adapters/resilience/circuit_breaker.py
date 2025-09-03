"""Circuit breaker pattern for resilient API calls.

Simple implementation following Google's SRE practices for
preventing cascading failures in distributed systems.
"""

import logging
import threading
import time
from collections.abc import Callable
from typing import TypeVar

from flow.errors import ResourceNotAvailableError

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitBreaker:
    """Thread-safe circuit breaker for API calls.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Failures exceeded threshold, requests fail fast
    - HALF_OPEN: Testing if service recovered
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exceptions: tuple = (Exception,),
    ):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before testing recovery
            expected_exceptions: Exceptions that count as failures
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exceptions = expected_exceptions

        self._failure_count = 0
        self._last_failure_time: float | None = None
        self._state = "CLOSED"
        self._lock = threading.Lock()

    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function with circuit breaker protection."""
        with self._lock:
            if self._state == "OPEN":
                if self._should_attempt_reset():
                    self._state = "HALF_OPEN"
                    logger.debug(f"Circuit breaker entering HALF_OPEN state for {func.__name__}")
                else:
                    raise ResourceNotAvailableError(
                        "Service temporarily unavailable",
                        suggestions=[
                            f"Circuit breaker is open after {self._failure_count} failures",
                            f"Retry after {self._time_until_reset():.0f} seconds",
                            "Check service status or try a different region",
                        ],
                    )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exceptions:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time passed to try recovery."""
        return (
            self._last_failure_time is not None
            and time.time() - self._last_failure_time >= self.recovery_timeout
        )

    def _time_until_reset(self) -> float:
        """Time remaining until circuit can reset."""
        if self._last_failure_time is None:
            return 0.0
        elapsed = time.time() - self._last_failure_time
        return max(0.0, self.recovery_timeout - elapsed)

    def _on_success(self):
        """Record successful call."""
        with self._lock:
            if self._state == "HALF_OPEN":
                logger.info("Circuit breaker recovered, returning to CLOSED state")
            self._failure_count = 0
            self._state = "CLOSED"

    def _on_failure(self):
        """Record failed call."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()

            if self._failure_count >= self.failure_threshold:
                if self._state != "OPEN":
                    logger.warning(f"Circuit breaker opened after {self._failure_count} failures")
                self._state = "OPEN"
