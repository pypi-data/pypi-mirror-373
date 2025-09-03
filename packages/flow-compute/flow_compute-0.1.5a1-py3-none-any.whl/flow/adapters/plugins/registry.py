from __future__ import annotations

from collections.abc import Iterable
from importlib.metadata import entry_points
from typing import Any


def load_entry_point(group: str, name: str) -> Any:
    """Load a specific entry point by group and name.

    Falls back gracefully if the group/name is not present.
    """
    eps = entry_points()
    candidates: Iterable[Any] = getattr(eps, "select", lambda **kw: [])(
        group=group
    )  # py3.10 compat
    for ep in candidates:
        if getattr(ep, "name", None) == name:
            return ep.load()
    return None


def iter_entry_points(group: str) -> list[Any]:
    eps = entry_points()
    candidates: Iterable[Any] = getattr(eps, "select", lambda **kw: [])(group=group)
    return list(candidates)
