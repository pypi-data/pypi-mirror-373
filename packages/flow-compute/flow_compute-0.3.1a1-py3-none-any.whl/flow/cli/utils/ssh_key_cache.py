"""CLI shim for SSHKeyCache.

Re-exports the core utility so CLI code can retain its import path
while adapters and other layers import from core.
"""

from flow.core.utils.ssh_key_cache import SSHKeyCache  # noqa: F401

__all__ = ["SSHKeyCache"]
