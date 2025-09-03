"""Compatibility shim: re-export domain SSH resolver under core path.

The implementation lives in ``flow.domain.ssh.resolver`` to keep the domain
logic independent of providers and CLI layers. This module preserves the
historical import path used throughout the codebase.
"""

from flow.domain.ssh.resolver import SSHKeyReference, SmartSSHKeyResolver  # noqa: F401

__all__ = ["SSHKeyReference", "SmartSSHKeyResolver"]
