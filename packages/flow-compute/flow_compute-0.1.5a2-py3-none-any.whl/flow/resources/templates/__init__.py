"""Canonical Jinja2 templates and helpers.

This module exposes utilities for working with packaged templates in a
zip-safe way (using importlib.resources), plus optional Jinja2 helpers.
"""

from __future__ import annotations

from collections.abc import Iterable
from contextlib import ExitStack
from importlib.resources import as_file, files
from pathlib import Path
from typing import Any

try:  # Optional import; Jinja is a runtime dependency already
    import jinja2 as _jinja2
except Exception:  # pragma: no cover - optional at import time
    _jinja2 = None  # type: ignore[assignment]


def package_dir(package: str) -> Path:
    """Return a real filesystem path for a package (zip-safe).

    Converts importlib.resources traversable to a real Path usable by libraries
    that require on-disk paths (e.g., Jinja FileSystemLoader).
    """
    res = files(package)
    with as_file(res) as p:
        return Path(p)


def template_search_paths(*packages: str) -> Iterable[Path]:
    """Yield real filesystem paths for given template packages in order.

    Each package should point at a templates subpackage, e.g.:
      - "flow.resources.templates"
      - "flow.adapters.providers.builtin.mithril.runtime.startup.templates"
    Missing packages are ignored for resilience.
    """
    with ExitStack() as stack:
        for pkg in packages:
            try:
                res = files(pkg)
            except ModuleNotFoundError:
                continue
            yield stack.enter_context(as_file(res))


def jinja_env(provider_pkg: str | None = None) -> Any:
    """Create a Jinja2 Environment with provider overlays.

    If provider_pkg is provided, it takes precedence for overrides.
    """
    if _jinja2 is None:
        raise RuntimeError("Jinja2 is not available")

    pkgs: list[str] = []
    if provider_pkg:
        pkgs.append(provider_pkg)
    # Canonical templates location
    pkgs.append("flow.resources.templates")
    paths = [str(p) for p in template_search_paths(*pkgs)]
    return _jinja2.Environment(loader=_jinja2.ChoiceLoader([_jinja2.FileSystemLoader(paths)]))
