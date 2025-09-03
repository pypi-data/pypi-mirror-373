"""Retry policy configuration for Flow tasks."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class Retries(BaseModel):
    """Retry policy with fixed or exponential backoff."""

    max_retries: int = Field(3, ge=0, le=10, description="Maximum retry attempts (0-10)")
    backoff_coefficient: float = Field(
        2.0, ge=1.0, le=10.0, description="Delay multiplier between retries"
    )
    initial_delay: float = Field(
        1.0, ge=0.1, le=300.0, description="Initial delay in seconds before first retry"
    )
    max_delay: float | None = Field(
        None, ge=1.0, le=3600.0, description="Maximum delay between retries (seconds)"
    )

    @model_validator(mode="after")
    def validate_delays(self) -> Retries:
        """Ensure max_delay is greater than initial_delay if set."""
        if self.max_delay is not None and self.max_delay < self.initial_delay:
            raise ValueError(
                f"max_delay ({self.max_delay}s) must be >= initial_delay ({self.initial_delay}s)"
            )
        return self

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for a given retry attempt.

        Args:
            attempt: Retry attempt number (1-based)

        Returns:
            Delay in seconds before this retry attempt
        """
        if attempt <= 0:
            return 0.0

        # Calculate exponential backoff
        delay = self.initial_delay * (self.backoff_coefficient ** (attempt - 1))

        # Apply max_delay cap if set
        if self.max_delay is not None:
            delay = min(delay, self.max_delay)

        return delay

    @classmethod
    def fixed(cls, retries: int = 3, delay: float = 5.0) -> Retries:
        """Create fixed-interval retry configuration.

        Args:
            retries: Number of retry attempts
            delay: Fixed delay between retries (seconds)

        Returns:
            Retries with fixed intervals

        Example:
            >>> retry = Retries.fixed(retries=5, delay=10.0)
            # Retries every 10 seconds, up to 5 times
        """
        return cls(max_retries=retries, backoff_coefficient=1.0, initial_delay=delay)

    @classmethod
    def exponential(
        cls,
        retries: int = 3,
        initial: float = 1.0,
        multiplier: float = 2.0,
        max_delay: float | None = None,
    ) -> Retries:
        """Create exponential backoff retry configuration.

        Args:
            retries: Number of retry attempts
            initial: Initial delay (seconds)
            multiplier: Backoff multiplier
            max_delay: Maximum delay cap (seconds)

        Returns:
            Retries with exponential backoff

        Example:
            >>> retry = Retries.exponential(retries=5, initial=2.0, multiplier=3.0)
            # Delays: 2s, 6s, 18s, 54s, 162s
        """
        return cls(
            max_retries=retries,
            initial_delay=initial,
            backoff_coefficient=multiplier,
            max_delay=max_delay,
        )

    @classmethod
    def none(cls) -> Retries:
        """Create no-retry configuration.

        Returns:
            Retries with no retry attempts

        Example:
            >>> retry = Retries.none()
            # Task will not be retried on failure
        """
        return cls(max_retries=0)
