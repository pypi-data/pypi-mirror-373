"""DEPRECATED: use flow.domain.parsers.gpu_parser.GPUParser.

This module remains for backward compatibility only and re-exports the domain parser.
"""

from __future__ import annotations

import warnings as _warnings

from flow.domain.parsers.gpu_parser import GPUParser as GPUParser  # re-export

_warnings.warn(
    "flow.core.resources.parser.GPUParser is deprecated; use flow.domain.parsers.gpu_parser.GPUParser",
    DeprecationWarning,
    stacklevel=2,
)
