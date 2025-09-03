"""Plugin namespace for optional integrations.

Extensible namespace package that hosts provider and frontend plugins. Flow
discovers plugins primarily via entry points (``flow.providers`` and
``flow.frontends``), but third parties may also contribute importable modules
under ``flow.plugins.*``.

Notes:
  - This package is intentionally extensible across distributions. We use
    ``pkgutil.extend_path`` to remain namespace-friendly while providing a
    clear docstring for tooling and readers.
  - Prefer discovery through ``flow.plugins.registry``.
"""

from __future__ import annotations

from pkgutil import extend_path as _extend_path

__path__ = _extend_path(__path__, __name__)  # type: ignore[name-defined]

__all__: list[str] = []
