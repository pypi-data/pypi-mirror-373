"""Lightweight progress reporting protocol.

This protocol enables headless SDK code to receive optional progress updates
from UI layers (e.g., CLI) without importing UI dependencies.

Design:
- Minimal surface: callers may implement only `update_eta()` for SSH waits.
- No lifecycle requirements: callers manage context; SDK does not start/close.
"""

from __future__ import annotations

from typing import Protocol


class ProgressAdapter(Protocol):
    """Optional progress adapter used by long-running operations.

    Implementations may be context-managed by the caller. The SDK will not
    attempt to start or close adapters; it may call `update_eta()` to provide
    a best-effort ETA hint or to nudge UI refresh.
    """

    def update_eta(self, eta: str | None = None) -> None:  # pragma: no cover - protocol
        ...
