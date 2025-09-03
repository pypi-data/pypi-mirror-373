"""SSH transport (stable facade).

Provides a stable import surface for SSH transport utilities by re-exporting
the concrete implementations from sibling modules. This allows internal
refactors without breaking external imports such as
``flow.adapters.transport.ssh`` or ``flow.adapters.transport.ssh.ssh_stack``.
"""

from __future__ import annotations

from .client import (
    ExponentialBackoffSSHWaiter,
    ISSHWaiter,
    SSHConnectionInfo,
)
from .ssh_stack import SshStack
from .tunnel import (
    SSHTunnel,
    SSHTunnelManager,
)

__all__ = [
    "SshStack",
    "SSHConnectionInfo",
    "ISSHWaiter",
    "ExponentialBackoffSSHWaiter",
    "SSHTunnel",
    "SSHTunnelManager",
]
