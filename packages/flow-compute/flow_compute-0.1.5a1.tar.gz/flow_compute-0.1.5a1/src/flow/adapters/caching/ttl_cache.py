"""DEPRECATED: moved to `flow.utils.cache`.

This module remains for backward compatibility and re-exports the canonical
implementations from `flow.utils.cache`. Prefer importing from
`flow.utils.cache` going forward.
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "flow.adapters.caching.ttl_cache is deprecated; use flow.utils.cache",
    DeprecationWarning,
    stacklevel=2,
)
