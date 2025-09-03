from __future__ import annotations

"""SSH facet: remote operations access and discovery.

This complements `flow.protocols.remote_operations`, allowing providers to
expose how to obtain a remote-ops handle when applicable.
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class SSHProtocol(Protocol):
    """Access to provider-specific remote operations interface."""

    def get_remote_operations(self) -> Any | None: ...
