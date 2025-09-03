"""Legacy frontend adapters (deprecated).

Kept for compatibility while frontends move under the plugin system.
Prefer discovery via ``flow.plugins.registry``.
"""

from __future__ import annotations

import warnings as _warnings

# Public re-exports for frontend adapters (deprecated)
from flow.adapters.frontends.base import BaseFrontendAdapter
from flow.adapters.frontends.registry import FrontendRegistry

_warnings.warn(
    "flow.adapters.frontends is deprecated; use flow.plugins.registry for discovery",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["BaseFrontendAdapter", "FrontendRegistry"]
