"""Public API wrapper for the interactive selector.

Provides simple static helpers without bloating the main orchestrator module.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Generic, TypeVar

from flow.cli.ui.components.models import SelectionItem

if TYPE_CHECKING:  # Avoid import cycle at module import time
    from rich.console import Console

T = TypeVar("T")


class Selector(Generic[T]):
    """Public API for the interactive selector."""

    @staticmethod
    def select(
        items: list[SelectionItem[T]],
        title: str = "Select an item",
        subtitle: str | None = None,
        multiselect: bool = False,
        preview_formatter: Callable[[SelectionItem[T]], str] | None = None,
        status_filter: str | None = None,
        console: Console | None = None,
    ) -> T | None | list[T]:
        """Run an interactive selection."""
        # Local import to avoid circular import at module import time
        from flow.cli.ui.components.selector import InteractiveSelector

        selector = InteractiveSelector(
            items=items,
            title=title,
            subtitle=subtitle,
            console=console,
            multiselect=multiselect,
            preview_formatter=preview_formatter,
            status_filter=status_filter,
        )
        return selector.run()

    @staticmethod
    def select_one(
        items: list[SelectionItem[T]],
        title: str = "Select an item",
        subtitle: str | None = None,
        preview_formatter: Callable[[SelectionItem[T]], str] | None = None,
        console: Console | None = None,
    ) -> T | None:
        result = Selector.select(
            items=items,
            title=title,
            subtitle=subtitle,
            multiselect=False,
            preview_formatter=preview_formatter,
            console=console,
        )
        return result if not isinstance(result, list) else None

    @staticmethod
    def select_many(
        items: list[SelectionItem[T]],
        title: str = "Select items",
        subtitle: str | None = None,
        preview_formatter: Callable[[SelectionItem[T]], str] | None = None,
        console: Console | None = None,
    ) -> list[T]:
        result = Selector.select(
            items=items,
            title=title,
            subtitle=subtitle,
            multiselect=True,
            preview_formatter=preview_formatter,
            console=console,
        )
        if isinstance(result, list):
            return result
        return [] if result is None else [result]
