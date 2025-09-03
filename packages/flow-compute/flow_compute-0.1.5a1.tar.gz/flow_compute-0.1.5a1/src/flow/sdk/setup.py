"""SDK setup utilities (provider registry helpers).

Surgical shim to expose provider discovery to CLI without creating
static CLI→core dependencies. Uses lazy imports under the hood.
"""

from __future__ import annotations

import importlib
from typing import Any


def _import_attr(module: str, name: str, default: Any = None) -> Any:
    try:
        mod = importlib.import_module(module)
        return getattr(mod, name)
    except Exception:
        return default


def register_providers() -> None:
    """Register providers into the core registry, if available."""
    reg = _import_attr("flow.core.setup_registry", "register_providers", default=None)
    try:
        if reg:
            reg()
    except Exception:
        # Best-effort only
        pass


def list_providers() -> list[str]:
    """Return list of available provider names (best effort)."""
    try:
        register_providers()
        SetupRegistry = _import_attr("flow.core.setup_registry", "SetupRegistry", default=None)
        if SetupRegistry:
            return list(SetupRegistry.list_adapters())  # type: ignore[no-any-return]
    except Exception:
        pass
    return []


def get_adapter(name: str) -> Any | None:
    """Return the provider adapter for a given name (or None)."""
    try:
        register_providers()
        SetupRegistry = _import_attr("flow.core.setup_registry", "SetupRegistry", default=None)
        if SetupRegistry:
            return SetupRegistry.get_adapter(name)
    except Exception:
        pass
    return None
