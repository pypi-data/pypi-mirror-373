from __future__ import annotations

"""Interactive menu selector with graceful fallbacks."""

import os
import sys
from collections.abc import Callable

from rich.console import Console

from flow.cli.ui.components import InteractiveSelector, SelectionItem
from flow.core.setup_wizard.prompter import readline_sanitized


def interactive_menu_select(
    options: list,
    title: str = "Select an option",
    default_index: int = 0,
    extra_header_html: str | None = None,
    breadcrumbs: list[str] | None = None,
    preview_renderer: Callable[[SelectionItem[str]], str] | None = None,
) -> str | None:
    """Interactive menu selector using arrow keys with graceful fallback.

    Args:
        options: List of tuples (value, display_text, description)
        title: Menu title
        default_index: Index of default selection
    Returns:
        Selected value or None if cancelled
    """
    try:
        # Non-interactive guard
        if os.environ.get("FLOW_NONINTERACTIVE"):
            return _fallback_menu_select(options, title, default_index)

        # Determine TTY capability
        stdio_is_tty = sys.stdin.isatty() and sys.stdout.isatty()
        term_is_dumb = os.environ.get("TERM") == "dumb"
        ci_env = os.environ.get("CI") is not None

        if not stdio_is_tty or term_is_dumb or ci_env:
            try:
                with open("/dev/tty"):
                    os.environ.setdefault("FLOW_FORCE_INTERACTIVE", "true")
            except Exception:
                return _fallback_menu_select(options, title, default_index)

        # Build menu items
        menu_items = []
        for i, (value, display_text, description) in enumerate(options):
            menu_items.append(
                {"value": value, "name": display_text, "id": value, "description": description}
            )

        def menu_to_selection(item: dict) -> SelectionItem[str]:
            return SelectionItem(
                value=item["value"],
                id=item["id"],
                title=item["name"],
                subtitle=item["description"],
                status="",
            )

        selector = InteractiveSelector(
            items=menu_items,
            item_to_selection=menu_to_selection,
            title=title,
            allow_multiple=False,
            allow_back=True,
            show_preview=bool(preview_renderer),
            extra_header_html=extra_header_html,
            breadcrumbs=breadcrumbs,
            preview_renderer=preview_renderer,
        )
        # Ensure prompt_toolkit never shows the terminal caret in our inline UI
        import os as _os

        _os.environ.setdefault("PROMPT_TOOLKIT_HIDE_CURSOR", "1")
        if 0 <= default_index < len(menu_items):
            selector.selected_index = default_index

        result = selector.select()
        if result is InteractiveSelector.BACK_SENTINEL:
            return None
        # If interactive UI fails and returns None, fall back to numbered menu
        if result is None:
            return _fallback_menu_select(options, title, default_index)
        return result
    except KeyboardInterrupt:
        raise
    except Exception:
        return _fallback_menu_select(options, title, default_index)


def _fallback_menu_select(options: list, title: str, default_index: int = 0) -> str | None:
    """Fallback numbered menu selection."""
    console = Console()
    console.print(f"\n[bold]{title}[/bold]")

    max_width = max(len(opt[1]) for opt in options) if options else 30
    for i, (value, display_text, description) in enumerate(options):
        if display_text.strip().startswith("[") and "]" in display_text:
            prefix = "  "
        else:
            prefix = f"  {i + 1}. "
        if description:
            console.print(f"{prefix}{display_text:<{max_width}} • {description}")
        else:
            console.print(f"{prefix}{display_text}")

    try:
        os.system("stty sane 2>/dev/null || true")
    except Exception:
        pass

    while True:
        try:
            default_num = str(default_index + 1)
            prompt = f"Select [1-{len(options)}] ({default_num}): "
            response = readline_sanitized(prompt)
            if response is None:
                console.print("\n[warning]Cancelled[/warning]")
                return None
            response = response.strip()
            if not response:
                return options[default_index][0]
            choice_num = int(response)
            if 1 <= choice_num <= len(options):
                return options[choice_num - 1][0]
            console.print("Please enter a valid number")
        except KeyboardInterrupt:
            console.print("\n\n[warning]Setup cancelled[/warning]")
            sys.exit(0)
        except ValueError:
            console.print("\n[error]Please enter a number[/error]")
            continue
