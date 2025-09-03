"""Main selector orchestrator that combines all interaction components."""

from __future__ import annotations

import logging
import os
import re
import sys
import threading
import time
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Generic, TypeVar, overload

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout

from flow.cli.ui.components.keybindings import KeyHandler
from flow.cli.ui.components.models import SelectionItem, SelectionState
from flow.cli.ui.components.renderer import Renderer
from flow.cli.ui.components.state_machine import SelectionStateMachine as StateMachine

if TYPE_CHECKING:
    from collections.abc import Callable

    from rich.console import Console

T = TypeVar("T")


S = TypeVar("S")


class InteractiveSelector(Generic[T]):
    """Interactive selector that orchestrates all UI components."""

    # Legacy/back-compat: sentinel returned when user presses Esc and back is allowed
    BACK_SENTINEL: object = object()

    @overload
    def __init__(
        self,
        items: Iterable[SelectionItem[T]],
        title: str = "Select an item",
        subtitle: str | None = None,
        console: Console | None = None,
        multiselect: bool = False,
        preview_formatter: Callable[[SelectionItem[T]], str] | None = None,
        status_filter: str | None = None,
        on_change: Callable[[SelectionItem[T] | None], None] | None = None,
        show_keybindings: bool = True,
        compact_mode: bool = False,
        # --- Compatibility args used by older call sites ---
        item_to_selection: None = None,
        allow_multiple: bool | None = None,
        allow_back: bool | None = None,
        show_preview: bool | None = None,
        breadcrumbs: list[str] | None = None,
        extra_header_html: str | None = None,
        preferred_viewport_size: int | None = None,
        preview_renderer: Callable[[SelectionItem[T]], str] | None = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        items: Iterable[S],
        title: str = "Select an item",
        subtitle: str | None = None,
        console: Console | None = None,
        multiselect: bool = False,
        preview_formatter: Callable[[SelectionItem[T]], str] | None = None,
        status_filter: str | None = None,
        on_change: Callable[[SelectionItem[T] | None], None] | None = None,
        show_keybindings: bool = True,
        compact_mode: bool = False,
        # --- Compatibility args used by older call sites ---
        item_to_selection: Callable[[S], SelectionItem[T]] | None = None,
        allow_multiple: bool | None = None,
        allow_back: bool | None = None,
        show_preview: bool | None = None,
        breadcrumbs: list[str] | None = None,
        extra_header_html: str | None = None,
        preferred_viewport_size: int | None = None,
        preview_renderer: Callable[[SelectionItem[T]], str] | None = None,
    ) -> None: ...

    def __init__(
        self,
        items,
        title: str = "Select an item",
        subtitle: str | None = None,
        console: Console | None = None,
        multiselect: bool = False,
        preview_formatter: Callable[[SelectionItem[T]], str] | None = None,
        status_filter: str | None = None,
        on_change: Callable[[SelectionItem[T] | None], None] | None = None,
        show_keybindings: bool = True,
        compact_mode: bool = False,
        # --- Compatibility args used by older call sites ---
        item_to_selection: Callable[[object], SelectionItem[T]] | None = None,
        allow_multiple: bool | None = None,
        allow_back: bool | None = None,
        show_preview: bool | None = None,
        breadcrumbs: list[str] | None = None,
        extra_header_html: str | None = None,
        preferred_viewport_size: int | None = None,
        preview_renderer: Callable[[SelectionItem[T]], str] | None = None,
    ) -> None:
        """Initialize the interactive selector.

        Args:
            items: List of items to select from
            title: Title to display
            subtitle: Optional subtitle
            console: Rich console for output
            multiselect: Allow multiple selection
            preview_formatter: Function to format preview pane
            status_filter: Filter items by status
            on_change: Callback when selection changes
            show_keybindings: Show keyboard shortcuts
            compact_mode: Use compact display mode
        """
        # Import here to avoid circular imports
        from rich.console import Console as RichConsole

        self.items = items
        self.title = title
        self.subtitle = subtitle
        self.console = console or RichConsole()
        self.multiselect = bool(allow_multiple) if allow_multiple is not None else multiselect
        # Prefer preview_renderer (legacy name) when provided
        effective_preview = preview_renderer or preview_formatter
        if show_preview is False:
            effective_preview = None
        self.preview_formatter = effective_preview
        self.status_filter = status_filter
        self.on_change = on_change
        self.show_keybindings = show_keybindings
        self.compact_mode = compact_mode
        self.allow_back = bool(allow_back)
        self._breadcrumbs = breadcrumbs or []
        self._extra_header_html = extra_header_html

        # Initialize components
        if item_to_selection is not None:
            mapped_items: list[SelectionItem[T]] = [item_to_selection(it) for it in items]  # type: ignore[arg-type]
        else:
            mapped_items = list(items)  # type: ignore[arg-type]

        self.state = SelectionState(
            items=mapped_items,
            multiselect=self.multiselect,
            status_filter=status_filter,
        )
        # Default viewport size heuristic; could be computed from terminal size
        viewport = int(preferred_viewport_size) if preferred_viewport_size else 20
        self.state_machine = StateMachine(
            items=mapped_items,
            state=self.state,
            viewport_size=viewport,
            allow_multiple=self.multiselect,
        )
        # Respect global spacing and persistent-nav preferences
        try:
            from flow.cli.ui.presentation.visual_constants import SPACING
        except Exception:
            SPACING = {"item_gap": 0}  # type: ignore[assignment]

        try:
            persistent_nav = os.environ.get("FLOW_PERSISTENT_NAV", "1").strip() not in {
                "0",
                "false",
                "False",
            }
        except Exception:
            persistent_nav = True

        self.renderer = Renderer(
            title=title,
            subtitle=subtitle,
            compact_mode=compact_mode,
            show_keybindings=show_keybindings,
            row_spacing=int(SPACING.get("item_gap", 0)),  # type: ignore[arg-type]
            persistent_nav=persistent_nav,
        )
        self.key_handler = KeyHandler()

        # Numeric key behavior: highlight (default) or immediate select via env
        try:
            self._numkey_immediate = os.environ.get(
                "FLOW_NUMKEY_SELECT", "highlight"
            ).strip().lower() in {"immediate", "true", "1", "yes"}
        except Exception:
            self._numkey_immediate = False

        # Application state
        self.app: Application[T | None | list[T]] | None = None
        self.result: T | None | list[T] = None
        self._monitoring = False
        self._monitor_thread: threading.Thread | None = None
        self._dev_tty_handle: object | None = None

        # Precompile ANSI/CSI pattern for stripping from rendered text
        try:
            self._csi_pattern = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")
        except Exception:
            self._csi_pattern = None

    def _check_terminal_compatibility(self) -> bool:
        """Check if terminal supports interactive mode."""
        logger = logging.getLogger(__name__)
        # Allow explicit override for CI/non-tty environments
        if os.environ.get("FLOW_FORCE_INTERACTIVE"):
            return True
        if os.environ.get("FLOW_DEBUG"):
            logger.debug(
                "Checking terminal compatibility... TERM=%s TTY=%s",
                os.environ.get("TERM", "not set"),
                sys.stdin.isatty(),
            )

        # Check if we have a TTY
        if not sys.stdin.isatty():
            # Try to bind to /dev/tty when available
            try:
                with open("/dev/tty"):
                    if os.environ.get("FLOW_DEBUG"):
                        logger.debug("Using /dev/tty for interactive mode")
                    return True
            except Exception:
                if os.environ.get("FLOW_DEBUG"):
                    logger.warning("No TTY detected; falling back to non-interactive mode")
                return False

        # Check terminal type
        term = os.environ.get("TERM", "").lower()
        if term in {"dumb", "unknown", ""}:
            if os.environ.get("FLOW_DEBUG"):
                logger.warning("Unsupported terminal: %s", term)
            return False

        return True

    def _create_application(self) -> Application[T | None | list[T]]:
        """Create the prompt_toolkit application via app wiring module."""
        from flow.cli.ui.components.app import create_selector_application

        # Delegate to app wiring for construction
        app = create_selector_application(self)
        return app  # type: ignore[return-value]

    # --- Keybinding helper groups ---
    def _bind_navigation(self, kb: KeyBindings) -> None:
        from flow.cli.ui.components.app_helpers import bind_navigation

        bind_navigation(self, kb)

    def _bind_selection(self, kb: KeyBindings) -> None:
        from flow.cli.ui.components.app_helpers import bind_selection

        bind_selection(self, kb)

    def _bind_search(self, kb: KeyBindings) -> None:
        from flow.cli.ui.components.app_helpers import bind_search

        bind_search(self, kb)

    def _bind_exit_and_help(self, kb: KeyBindings) -> None:
        from flow.cli.ui.components.app_helpers import bind_exit_and_help

        bind_exit_and_help(self, kb)

    def _create_layout(self) -> Layout:
        """Create the layout via app helper module."""
        from flow.cli.ui.components.app_helpers import create_layout

        return create_layout(self)

    def _render_preview(self) -> str:
        from flow.cli.ui.components.app_helpers import render_preview

        return render_preview(self)

    def _render_help(self) -> str:
        from flow.cli.ui.components.app_helpers import render_help

        return render_help(self)

    def _trigger_on_change(self):
        """Trigger the on_change callback if set."""
        if self.on_change:
            current_item = self.state_machine.get_current_item()
            from contextlib import suppress

            with suppress(Exception):
                self.on_change(current_item)

    def _confirm_selection(self):
        """Confirm the current selection."""
        if self.multiselect:
            selected_items = self.state_machine.get_selected_items()
            self.result = [item.value for item in selected_items] if selected_items else []
        else:
            current_item = self.state_machine.get_current_item()
            self.result = current_item.value if current_item else None

    def _start_monitoring(self):
        """Start monitoring for item updates."""
        if self._monitoring:
            return

        self._monitoring = True

        def monitor_loop():
            while self._monitoring:
                # Check for updates (implement based on your needs)
                time.sleep(1)

                # Trigger refresh if needed
                if self.app and self.app.is_running:
                    self.app.invalidate()

        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()

    def _stop_monitoring(self):
        """Stop monitoring for updates."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1)
            self._monitor_thread = None

    def run(self) -> T | None | list[T]:
        """Run the interactive selector and return the result."""
        # Check terminal compatibility
        if not self._check_terminal_compatibility():
            # Fallback to non-interactive mode
            if self.items:
                if self.multiselect:
                    return [item.value for item in self.items]
                else:
                    return self.items[0].value
            return None

        # Create and run application
        try:
            from flow.cli.ui.components.app import run_selector

            result = run_selector(self)
            return result  # type: ignore[return-value]
        except KeyboardInterrupt:
            return None
        except Exception as e:
            if os.environ.get("FLOW_DEBUG"):
                self.console.print(f"[error]Error in interactive selector: {e}[/error]")
            return None
        finally:
            self._stop_monitoring()
            self.app = None
            # Close any opened /dev/tty handle
            try:
                if self._dev_tty_handle is not None:
                    from contextlib import suppress

                    with suppress(Exception):
                        self._dev_tty_handle.close()  # type: ignore[attr-defined]
                    self._dev_tty_handle = None
            except Exception:
                pass

    # Legacy convenience API used by existing call sites
    def select(self) -> T | None | list[T]:
        return self.run()

    # Allow external default selection index to be set/get
    @property
    def selected_index(self) -> int:
        return self.state.selected_index

    @selected_index.setter
    def selected_index(self, value: int) -> None:
        try:
            self.state.selected_index = int(value)
        except Exception:
            self.state.selected_index = 0
