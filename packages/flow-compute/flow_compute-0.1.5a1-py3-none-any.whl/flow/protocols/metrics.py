from __future__ import annotations

from typing import Protocol


class MetricsProtocol(Protocol):
    """Lightweight metrics interface (no-op by default)."""

    def increment(self, name: str, value: float = 1.0, **tags: str) -> None: ...

    def timing(self, name: str, ms: float, **tags: str) -> None: ...
