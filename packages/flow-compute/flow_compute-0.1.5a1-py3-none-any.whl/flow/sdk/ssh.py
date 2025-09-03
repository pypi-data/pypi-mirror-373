"""SDK SSH facade (re-export).

Provides a stable import path for SSH helpers used by SDK/CLI without importing
adapter packages directly.
"""

from __future__ import annotations

from flow.adapters.transport.ssh.ssh_stack import SshStack as SshStack

__all__ = ["SshStack"]
