"""Data models for interactive selection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
__all__ = [
    "SelectionItem",
    "SelectionState",
]


@dataclass
class SelectionItem(Generic[T]):
    """Wrapper for selectable items with display information.

    Attributes:
        value: Original item value.
        id: Stable identifier used for selection tracking.
        title: Primary label.
        subtitle: Secondary information shown inline.
        status: Status string or enum name for rendering.
        extra: Optional metadata for renderer hints.
    """

    value: T
    id: str
    title: str
    subtitle: str | None
    status: str | object | None
    extra: dict | None = None


@dataclass
class SelectionState:
    """Encapsulates the mutable state during selection.

    This separates state management from rendering and input handling.
    """

    # Full list of items and basic configuration
    items: list[SelectionItem[T]] | None = None
    multiselect: bool = False
    status_filter: str | None = None

    # UI/selection state
    selected_index: int = 0
    selected_ids: set[str] | None = None
    filter_text: str = ""
    viewport_start: int = 0
    show_help: bool = False

    # Optional search mode (compat with orchestrator expectations)
    search_mode: bool = False
    search_query: str = ""

    def __post_init__(self):
        if self.selected_ids is None:
            self.selected_ids = set()
        if self.items is None:
            self.items = []
