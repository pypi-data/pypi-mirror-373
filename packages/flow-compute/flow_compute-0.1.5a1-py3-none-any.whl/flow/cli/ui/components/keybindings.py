"""Keyboard event handlers for interactive selection."""

from __future__ import annotations

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys


class SelectionKeyBindings:
    """Manages keyboard bindings for the interactive selector."""

    def __init__(self, handler):
        """Initialize with a handler that will process key events.

        Args:
            handler: Object with methods for handling different key events.
                     Expected methods: on_up, on_down, on_page_up, on_page_down,
                     on_home, on_end, on_enter, on_space, on_escape, on_quit,
                     on_select_all, on_deselect_all, on_help, on_backspace
        """
        self.handler = handler
        self.kb = KeyBindings()
        self._setup_bindings()

    def _setup_bindings(self):
        """Set up all keyboard bindings."""
        kb = self.kb

        # Navigation
        kb.add(Keys.Up)(lambda event: self.handler.on_up())
        kb.add("k")(lambda event: self.handler.on_up())

        kb.add(Keys.Down)(lambda event: self.handler.on_down())
        kb.add("j")(lambda event: self.handler.on_down())

        kb.add(Keys.PageUp)(lambda event: self.handler.on_page_up())
        kb.add(Keys.ControlB)(lambda event: self.handler.on_page_up())

        kb.add(Keys.PageDown)(lambda event: self.handler.on_page_down())
        kb.add(Keys.ControlF)(lambda event: self.handler.on_page_down())

        kb.add(Keys.Home)(lambda event: self.handler.on_home())
        kb.add("g")(lambda event: self.handler.on_home())

        kb.add(Keys.End)(lambda event: self.handler.on_end())
        kb.add("G")(lambda event: self.handler.on_end())

        # Selection
        kb.add(Keys.Enter)(lambda event: self.handler.on_enter())
        kb.add(Keys.Space)(lambda event: self.handler.on_space())

        # Multi-selection shortcuts
        kb.add(Keys.ControlA)(lambda event: self.handler.on_select_all())
        kb.add(Keys.ControlD)(lambda event: self.handler.on_deselect_all())

        # Exit/Cancel
        kb.add(Keys.Escape)(lambda event: self.handler.on_escape())
        kb.add(Keys.ControlC)(lambda event: self.handler.on_quit())
        kb.add("q")(lambda event: self.handler.on_quit())

        # Help
        kb.add("?")(lambda event: self.handler.on_help())
        kb.add("h")(lambda event: self.handler.on_help())

        # Backspace for text input
        kb.add(Keys.Backspace)(lambda event: self.handler.on_backspace())

        # Any other key for filtering
        kb.add(Keys.Any)(lambda event: self.handler.on_text_input(event.data))

    def get_bindings(self) -> KeyBindings:
        """Return the configured key bindings."""
        return self.kb


def get_help_text(allow_multiple: bool = False, allow_back: bool = False) -> list[tuple[str, str]]:
    """Get compact, Codex-style key hints.

    Args:
        allow_multiple: Whether multiple selection is enabled
        allow_back: Whether back navigation is enabled

    Returns:
        List of (key, description) tuples
    """
    items: list[tuple[str, str]] = []

    # Primary actions first
    enter_label = "Confirm" if allow_multiple else "Select"
    items.append(("⏎", enter_label))
    items.append(("/", "Search"))

    # Navigation
    items.append(("j/k, ↑/↓", "Move"))
    items.append(("PgUp/PgDn", "Page"))
    items.append(("g/G, Home/End", "First/Last"))
    items.append(("1–9", "Jump"))

    # Multi-select controls
    if allow_multiple:
        items.extend(
            [
                ("Space", "Toggle"),
                ("Ctrl+A", "All"),
                ("Ctrl+D", "None"),
            ]
        )

    # Exit/Cancel
    items.append(("Ctrl+C", "Quit"))
    if allow_back:
        items.append(("Esc", "Back"))
    else:
        items.append(("Esc, q", "Cancel"))

    # Help + editing
    items.append(("?", "Help"))
    items.append(("Backspace", "Edit"))

    return items


# --- Compatibility shim expected by orchestrator ---
class KeyHandler:
    """Minimal key handler stub to satisfy orchestrator expectations.

    The orchestrator uses an instance to retrieve help text. This shim exposes
    a compatible method delegating to get_help_text().
    """

    def get_help_text(self) -> list[str]:  # type: ignore[override]
        items = get_help_text()
        return [f"{k}: {v}" for k, v in items]
