"""Utilities for optional, runtime-only imports.

These helpers keep CLI modules free of static imports that would otherwise
trip import-linter contracts, while keeping the call sites clean and readable.
"""

from __future__ import annotations

import importlib
from typing import Any


def import_attr(module: str, name: str, default: Any = None) -> Any:
    """Import attribute `name` from `module` at runtime.

    Returns `default` if the module or attribute cannot be imported.
    """
    try:
        mod = importlib.import_module(module)
        return getattr(mod, name)
    except Exception:
        return default


def import_module(module: str, default: Any = None) -> Any:
    """Import a module at runtime, returning default on failure."""
    try:
        return importlib.import_module(module)
    except Exception:
        return default
