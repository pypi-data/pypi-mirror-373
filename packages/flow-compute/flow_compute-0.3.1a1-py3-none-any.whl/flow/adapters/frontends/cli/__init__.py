"""CLI frontend adapter for Flow SDK (deprecated import path).

Prefer using the canonical CLI under ``flow.cli``. This module remains a thin
shim for backward compatibility and will be removed in a future release.
"""

from __future__ import annotations

import warnings

from flow.adapters.frontends.cli.adapter import CLIFrontendAdapter

warnings.warn(
    "flow.adapters.frontends.cli is deprecated; use flow.cli for the CLI entrypoints",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["CLIFrontendAdapter"]
