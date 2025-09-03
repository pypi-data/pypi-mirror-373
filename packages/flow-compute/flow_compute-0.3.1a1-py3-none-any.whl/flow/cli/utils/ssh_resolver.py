from __future__ import annotations

"""Compatibility shim for SSH resolver used by CLI.

This module provides a stable import path for CLI layers and defers to the
core implementation at runtime. Keeping the import here avoids tighter
coupling to core internals from multiple CLI commands.
"""

from typing import Any


class SmartSSHKeyResolver:  # pragma: no cover - thin shim
    def __init__(self, ssh_key_manager: Any):
        from flow.domain.ssh.resolver import SmartSSHKeyResolver as _R

        self._resolver = _R(ssh_key_manager)

    def __getattr__(self, name: str):
        return getattr(self._resolver, name)
