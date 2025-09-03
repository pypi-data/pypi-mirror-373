from __future__ import annotations

"""Compatibility wrapper for SSH waiter.

Delegates to the shared adapters transport implementation.
"""

from flow.adapters.transport.ssh import ExponentialBackoffSSHWaiter

__all__ = ["ExponentialBackoffSSHWaiter"]
