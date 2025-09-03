"""Visual feedback utilities for CLI commands.

Abstractions for success/error messages and visual feedback built on Rich.
"""

import os

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from flow.cli.utils.theme_manager import theme_manager


class FeedbackStyle:
    """Configurable styles for feedback messages."""

    # Success styles (semantic: readable ink for text, bright icon for symbol)
    SUCCESS_COLOR = theme_manager.get_color("success")
    SUCCESS_ICON = "✓"
    SUCCESS_BORDER = theme_manager.get_color("success.border") or theme_manager.get_color("success")

    # Error styles
    ERROR_COLOR = theme_manager.get_color("error")
    ERROR_ICON = "✗"
    ERROR_BORDER = theme_manager.get_color("error.border") or theme_manager.get_color("error")

    # Info styles
    INFO_COLOR = theme_manager.get_color("info")
    INFO_ICON = "ℹ"
    INFO_BORDER = theme_manager.get_color("info.border") or theme_manager.get_color("info")

    # Preferred minimum panel width; actual width adapts to terminal
    PANEL_MIN_WIDTH = 56


class Feedback:
    """Provides visual feedback for CLI operations."""

    def __init__(self, console: Console | None = None):
        """Initialize feedback with optional console override."""
        # Use theme-aware console for consistent styling
        self.console = console or theme_manager.create_console()
        self.style = FeedbackStyle()
        # Simple mode for CI/CD or minimal output preference
        self.simple_mode = os.environ.get("FLOW_SIMPLE_OUTPUT", "").lower() in ("1", "true", "yes")

    def success(
        self,
        message: str,
        title: str | None = None,
        subtitle: str | None = None,
    ) -> None:
        """Display a success message with visual styling."""
        self._display_feedback(
            message=message,
            title=title or "Success",
            subtitle=subtitle,
            icon=self.style.SUCCESS_ICON,
            color=self.style.SUCCESS_COLOR,
            border_style=self.style.SUCCESS_BORDER,
        )

    def error(
        self,
        message: str,
        title: str | None = None,
        subtitle: str | None = None,
    ) -> None:
        """Display an error message with visual styling."""
        self._display_feedback(
            message=message,
            title=title or "Error",
            subtitle=subtitle,
            icon=self.style.ERROR_ICON,
            color=self.style.ERROR_COLOR,
            border_style=self.style.ERROR_BORDER,
        )

    def info(
        self,
        message: str,
        title: str | None = None,
        subtitle: str | None = None,
        *,
        neutral_body: bool = False,
        title_color: str | None = None,
    ) -> None:
        """Display an informational message with visual styling."""
        self._display_feedback(
            message=message,
            title=title or "Info",
            subtitle=subtitle,
            icon=self.style.INFO_ICON,
            color=self.style.INFO_COLOR,
            border_style=self.style.INFO_BORDER,
            title_color=title_color,
            neutral_body=neutral_body,
        )

    def _display_feedback(
        self,
        message: str,
        title: str,
        icon: str,
        color: str,
        border_style: str,
        subtitle: str | None = None,
        *,
        title_color: str | None = None,
        neutral_body: bool = False,
    ) -> None:
        """Internal method to display formatted feedback."""
        if self.simple_mode:
            # Simple output for CI/CD environments
            self.console.print(f"{icon} {title}: {message}", style=color)
            return

        # Build title with icon
        title_text = Text()
        _title_color = title_color or color
        title_text.append(f"{icon} ", style=f"bold {_title_color}")
        title_text.append(title, style=f"bold {_title_color}")

        # Build content (preserve any existing markup). Optionally avoid tinting
        # the body so it uses the default readable ink, while keeping the title
        # and border semantically colored.
        content = Text.from_markup(message)
        # Apply overall tint only if content has no explicit style and
        # neutral_body is False. When neutral_body is True, enforce default ink.
        if not content.spans:
            if neutral_body:
                try:
                    default_color = theme_manager.get_color("default")
                    content.stylize(default_color)
                except Exception:
                    pass
            else:
                content.stylize(color)

        # Compute responsive panel width, biased to content so panels don't look overly wide
        try:
            from flow.cli.ui.presentation.terminal_adapter import TerminalAdapter

            term_width = TerminalAdapter.get_terminal_width()
        except Exception:
            term_width = 100

        # Measure content width (plain text, per line)
        try:
            content_plain = content.plain
            max_line_len = max((len(line) for line in content_plain.splitlines()), default=0)
        except Exception:
            max_line_len = 0

        subtitle_len = len(subtitle or "")
        content_target = max(max_line_len, subtitle_len) + 6  # padding buffer

        # Clamp to elegant bounds: never below min, never above a modest cap
        # Prefer 56–84 columns for a modern, compact card-like appearance
        base_width = max(self.style.PANEL_MIN_WIDTH, content_target)
        cap = min(84, max(48, term_width - 10))
        max_allowed = max(32, term_width - 6)
        target_width = min(base_width, cap, max_allowed)

        # Create panel
        # Use border tints when available; fall back to ink
        panel = Panel(
            Align.left(content),
            title=title_text,
            subtitle=subtitle,
            border_style=border_style,
            width=target_width,
            padding=(1, 2),
        )

        # Display with spacing; left-align panel for a consistent CLI rhythm
        self.console.print()
        self.console.print(panel)
        self.console.print()


# Global feedback instance for convenience
feedback = Feedback()
