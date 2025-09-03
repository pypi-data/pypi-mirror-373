"""Helpers for InteractiveSelector keybindings and layout.

These functions are extracted from the selector orchestrator to keep it slim.
They operate on a selector instance passed in, without importing adapters.
"""

from __future__ import annotations

import html as _html
from typing import TYPE_CHECKING

from prompt_toolkit.formatted_text.html import HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import HSplit, Layout, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl

if TYPE_CHECKING:
    from flow.cli.ui.components.selector import InteractiveSelector


def bind_navigation(selector: InteractiveSelector, kb: KeyBindings) -> None:
    @kb.add("down")
    @kb.add("j")
    def move_down(event):
        selector.state_machine.move_down()
        selector._trigger_on_change()

    @kb.add("up")
    @kb.add("k")
    def move_up(event):
        selector.state_machine.move_up()
        selector._trigger_on_change()

    @kb.add("pagedown")
    @kb.add("c-f")
    def page_down(event):
        selector.state_machine.page_down()
        selector._trigger_on_change()

    @kb.add("pageup")
    @kb.add("c-b")
    def page_up(event):
        selector.state_machine.page_up()
        selector._trigger_on_change()

    @kb.add("home")
    @kb.add("g", "g")
    def go_home(event):
        selector.state_machine.go_to_top()
        selector._trigger_on_change()

    @kb.add("end")
    @kb.add("G")
    def go_end(event):
        selector.state_machine.go_to_bottom()
        selector._trigger_on_change()


def bind_selection(selector: InteractiveSelector, kb: KeyBindings) -> None:
    from prompt_toolkit.filters import Condition

    @kb.add("enter")
    @kb.add("space", filter=Condition(lambda: selector.multiselect))
    def select_item(event):
        if selector.multiselect and event.key == "space":
            selector.state_machine.toggle_selection()
        else:
            selector._confirm_selection()
            event.app.exit(result=selector.result)

    # Quick numeric navigation: press 1-9 to choose the Nth item
    for _digit in list("123456789"):

        @kb.add(_digit)
        def _pick_by_number(event, _d=_digit):  # type: ignore[misc]
            try:
                idx = int(_d) - 1
                items = getattr(selector.state_machine, "filtered_items", []) or []
                if 0 <= idx < len(items):
                    selector.state.selected_index = idx
                    # Ensure the viewport follows the new index
                    try:
                        selector.state_machine._update_viewport()
                    except Exception:
                        pass
                    selector._trigger_on_change()
                    # Optional: immediate selection if enabled via env
                    if getattr(selector, "_numkey_immediate", False):
                        selector._confirm_selection()
                        event.app.exit(result=selector.result)
            except Exception:
                pass

    if selector.multiselect:

        @kb.add("a")
        def select_all(event):
            selector.state_machine.select_all()

        @kb.add("A")
        def deselect_all(event):
            selector.state_machine.deselect_all()


def bind_search(selector: InteractiveSelector, kb: KeyBindings) -> None:
    @kb.add("/")
    def start_search(event):
        selector.state_machine.start_search()
        # Ensure the UI reflects search mode immediately
        try:
            event.app.invalidate()
        except Exception:
            pass

    @kb.add("n")
    def next_match(event):
        if selector.state.search_mode:
            selector.state_machine.next_match()

    @kb.add("N")
    def prev_match(event):
        if selector.state.search_mode:
            selector.state_machine.previous_match()

    @kb.add("escape")
    def clear_search(event):
        if selector.state.search_mode:
            selector.state_machine.clear_search()
        else:
            event.app.exit(result=selector.BACK_SENTINEL if selector.allow_back else None)

    # Type-to-filter when in search mode
    from prompt_toolkit.filters import Condition

    @kb.add(Keys.Any, filter=Condition(lambda: selector.state.search_mode))
    def text_input(event):
        try:
            ch = getattr(event, "data", "")
        except Exception:
            ch = ""
        if not ch:
            return
        text = getattr(selector.state, "filter_text", "") or ""
        selector.state_machine.update_filter(text + ch)
        try:
            event.app.invalidate()
        except Exception:
            pass

    @kb.add("backspace", filter=Condition(lambda: selector.state.search_mode))
    def backspace(event):
        text = getattr(selector.state, "filter_text", "") or ""
        if text:
            selector.state_machine.update_filter(text[:-1])
        else:
            selector.state_machine.clear_search()
        try:
            event.app.invalidate()
        except Exception:
            pass

    # Quick clear of filter input
    @kb.add("c-u", filter=Condition(lambda: selector.state.search_mode))
    def clear_line(event):
        selector.state_machine.update_filter("")
        try:
            event.app.invalidate()
        except Exception:
            pass


def bind_exit_and_help(selector: InteractiveSelector, kb: KeyBindings) -> None:
    @kb.add("q")
    @kb.add("c-c")
    def quit_app(event):
        event.app.exit(result=None)

    @kb.add("?")
    @kb.add("h")
    def show_help(event):
        selector.state.show_help = not selector.state.show_help


def create_layout(selector: InteractiveSelector) -> Layout:
    """Create the layout for the application."""
    # Main list window
    list_window = Window(
        content=FormattedTextControl(
            text=lambda: HTML(selector.renderer.render_list(selector.state)),
            focusable=True,
            show_cursor=False,  # Hide cursor in interactive selector
        ),
        wrap_lines=False,
    )

    # Preview window (if formatter provided)
    if selector.preview_formatter:
        preview_window = Window(
            content=FormattedTextControl(
                text=lambda: HTML(render_preview(selector)),
                focusable=False,
            ),
            wrap_lines=True,
        )

        # Create split view
        # Use ASCII-safe split bar when requested
        import os as _os

        _ascii = str(_os.environ.get("FLOW_ASCII_ONLY", "0")).strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        _split_char = "|" if _ascii else "│"
        content = VSplit(
            [
                list_window,
                Window(width=1, char=_split_char),
                preview_window,
            ]
        )
    else:
        content = list_window

    # Status bar
    status_window = Window(
        content=FormattedTextControl(
            text=lambda: HTML(selector.renderer.render_status_bar(selector.state)),
            focusable=False,
        ),
        height=1,
    )

    # Persistent navigation footer with key hints when enabled
    nav_window = None
    if selector.show_keybindings and getattr(selector.renderer, "_persistent_nav", False):
        try:
            nav_text = selector.renderer.render_nav(selector.multiselect, selector.allow_back)
        except Exception:
            nav_text = ""
        nav_window = Window(
            content=FormattedTextControl(
                text=lambda: HTML(nav_text),
                focusable=False,
            ),
            height=1,
        )

    # Help overlay (if active)
    if selector.show_keybindings:
        help_window = Window(
            content=FormattedTextControl(
                text=lambda: HTML(render_help(selector)),
                focusable=False,
            ),
            height=lambda: (
                len(selector.key_handler.get_help_text()) + 2 if selector.state.show_help else 0
            ),
        )

        root = HSplit(
            [
                content,
                status_window,
                *([nav_window] if nav_window is not None else []),
                help_window,
            ]
        )
    else:
        root = HSplit(
            [
                content,
                status_window,
                *([nav_window] if nav_window is not None else []),
            ]
        )

    return Layout(root)


def render_preview(selector: InteractiveSelector) -> str:
    """Render the preview pane."""
    if not selector.preview_formatter:
        return ""

    current_item = selector.state_machine.get_current_item()
    if not current_item:
        return "<dim>No item selected</dim>"

    try:
        preview_text = str(selector.preview_formatter(current_item))
        # Strip ANSI/CSI sequences and escape for HTML
        csi_pattern = getattr(selector, "_csi_pattern", None)
        if csi_pattern is not None:
            from contextlib import suppress

            with suppress(Exception):
                preview_text = csi_pattern.sub("", preview_text)
        safe_text = _html.escape(preview_text, quote=False)
        return f"<pre>{safe_text}</pre>"
    except Exception as e:
        return f"<red>Error rendering preview: {e}</red>"


def render_help(selector: InteractiveSelector) -> str:
    """Render help overlay."""
    if not selector.state.show_help:
        return ""

    help_lines = selector.key_handler.get_help_text()
    help_text = "\n".join(f"  {line}" for line in help_lines)
    return f"<reverse> Keyboard Shortcuts </reverse>\n{help_text}"
