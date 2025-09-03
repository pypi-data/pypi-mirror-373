"""State management for interactive selection."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flow.cli.ui.components.models import SelectionItem, SelectionState


class SelectionStateMachine:
    """Manages state transitions for the interactive selector."""

    def __init__(
        self,
        items: list[SelectionItem],
        state: SelectionState,
        viewport_size: int,
        allow_multiple: bool = False,
    ):
        """Initialize the state machine.

        Args:
            items: List of selectable items
            state: Current selection state
            viewport_size: Number of items visible at once
            allow_multiple: Whether multiple selection is allowed
        """
        self.items = items
        self.state = state
        self.viewport_size = viewport_size
        self.allow_multiple = allow_multiple
        self.filtered_items = items

    def update_filter(self, filter_text: str) -> None:
        """Update the filter and recalculate visible items.

        Args:
            filter_text: New filter text
        """
        self.state.filter_text = filter_text

        if not filter_text:
            self.filtered_items = self.items
        else:
            # Simple case-insensitive filtering
            lower_filter = filter_text.lower()
            self.filtered_items = [
                item
                for item in self.items
                if lower_filter in (item.id + item.title + (item.subtitle or "")).lower()
            ]

        # Always jump to first visible match when the filter changes
        self.state.selected_index = 0
        self.state.viewport_start = 0

    # --- Compatibility methods expected by orchestrator ---
    # Provide thin wrappers with names used in the orchestrator.

    def page_down(self) -> None:
        self.move_page_down()

    def page_up(self) -> None:
        self.move_page_up()

    def go_to_top(self) -> None:
        self.move_to_first()

    def go_to_bottom(self) -> None:
        self.move_to_last()

    # Basic search-mode stubs for compatibility (no-op filtering UI)
    def start_search(self) -> None:
        if hasattr(self.state, "search_mode"):
            self.state.search_mode = True
            self.state.search_query = ""

    def next_match(self) -> None:  # pragma: no cover - simple stub
        pass

    def previous_match(self) -> None:  # pragma: no cover - simple stub
        pass

    def clear_search(self) -> None:
        if hasattr(self.state, "search_mode"):
            self.state.search_mode = False
            self.state.search_query = ""

    def move_up(self) -> None:
        """Move selection up by one item."""
        if not self.filtered_items:
            return

        if self.state.selected_index > 0:
            self.state.selected_index -= 1
            self._update_viewport()

    def move_down(self) -> None:
        """Move selection down by one item."""
        if not self.filtered_items:
            return

        if self.state.selected_index < len(self.filtered_items) - 1:
            self.state.selected_index += 1
            self._update_viewport()

    def move_page_up(self) -> None:
        """Move selection up by one page."""
        if not self.filtered_items:
            return

        self.state.selected_index = max(0, self.state.selected_index - self.viewport_size)
        self._update_viewport()

    def move_page_down(self) -> None:
        """Move selection down by one page."""
        if not self.filtered_items:
            return

        max_index = len(self.filtered_items) - 1
        self.state.selected_index = min(max_index, self.state.selected_index + self.viewport_size)
        self._update_viewport()

    def move_to_first(self) -> None:
        """Move selection to first item."""
        if not self.filtered_items:
            return

        self.state.selected_index = 0
        self.state.viewport_start = 0

    def move_to_last(self) -> None:
        """Move selection to last item."""
        if not self.filtered_items:
            return

        self.state.selected_index = len(self.filtered_items) - 1
        self._update_viewport()

    def toggle_selection(self) -> None:
        """Toggle selection of current item (for multi-select)."""
        if not self.allow_multiple or not self.filtered_items:
            return

        current_item = self.filtered_items[self.state.selected_index]
        if current_item.id in self.state.selected_ids:
            self.state.selected_ids.discard(current_item.id)
        else:
            self.state.selected_ids.add(current_item.id)

    def select_all(self) -> None:
        """Select all filtered items (for multi-select)."""
        if not self.allow_multiple:
            return

        for item in self.filtered_items:
            self.state.selected_ids.add(item.id)

    def deselect_all(self) -> None:
        """Deselect all items (for multi-select)."""
        if not self.allow_multiple:
            return

        self.state.selected_ids.clear()

    def get_current_item(self) -> SelectionItem | None:
        """Get the currently highlighted item."""
        if not self.filtered_items or self.state.selected_index >= len(self.filtered_items):
            return None
        return self.filtered_items[self.state.selected_index]

    def get_selected_items(self) -> list[SelectionItem]:
        """Get all selected items (for multi-select)."""
        if not self.allow_multiple:
            current = self.get_current_item()
            return [current] if current else []

        return [item for item in self.items if item.id in self.state.selected_ids]

    def get_visible_items(self) -> list[SelectionItem]:
        """Get items currently visible in the viewport."""
        if not self.filtered_items:
            return []

        start = self.state.viewport_start
        end = min(start + self.viewport_size, len(self.filtered_items))
        return self.filtered_items[start:end]

    def _update_viewport(self) -> None:
        """Update viewport to ensure selected item is visible."""
        if not self.filtered_items:
            return

        # Scroll up if selected item is above viewport
        if self.state.selected_index < self.state.viewport_start:
            self.state.viewport_start = self.state.selected_index

        # Scroll down if selected item is below viewport
        elif self.state.selected_index >= self.state.viewport_start + self.viewport_size:
            self.state.viewport_start = self.state.selected_index - self.viewport_size + 1

        # Ensure viewport doesn't go past the end
        max_start = max(0, len(self.filtered_items) - self.viewport_size)
        self.state.viewport_start = min(self.state.viewport_start, max_start)
