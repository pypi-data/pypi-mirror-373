"""Protocol for locating local SSH private keys that correspond to platform keys.

This protocol keeps domain logic decoupled from provider-specific key managers.
Adapters implement this to provide platform-aware local key lookup.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol


class SSHKeyLocatorProtocol(Protocol):
    """Capability to locate local private keys for platform SSH keys."""

    def find_matching_local_key(
        self, api_key_id: str
    ) -> Path | None:  # pragma: no cover - protocol
        """Return local private key path for a platform SSH key ID, if available."""
        ...

    def list_keys(self) -> list[object]:  # pragma: no cover - protocol
        """Optional: list platform keys for context; shape is implementation-defined."""
        ...
