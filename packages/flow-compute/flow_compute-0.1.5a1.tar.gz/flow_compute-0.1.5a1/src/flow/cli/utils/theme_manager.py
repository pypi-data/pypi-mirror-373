"""Theme management system for Flow CLI.

Provides automatic terminal theme detection, theme loading, and theme-aware
console creation for consistent visual presentation across different terminal
environments.
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from rich.console import Console
from rich.theme import Theme as RichTheme


@dataclass
class FlowTheme:
    """Flow theme definition."""

    name: str
    colors: dict[str, str]
    is_dark: bool = True

    def to_rich_theme(self) -> RichTheme:
        """Convert Flow theme to Rich theme."""
        return RichTheme(self.colors)


class ThemeManager:
    """Manages theme detection, loading, and application for Flow CLI."""

    # Built-in themes
    THEMES = {
        "dark": FlowTheme(
            name="dark",
            is_dark=True,
            colors={
                # Base colors
                "default": "white",
                "muted": "bright_black",
                "border": "bright_black",
                # Use a softer accent to avoid overly bright cyan on dark backgrounds
                "accent": "dark_cyan",
                # Map common markup color tags to theme accent for consistency
                "cyan": "dark_cyan",
                "blue": "blue",
                # Align basic named colors with semantic palette for consistency
                # so ad-hoc [green]/[yellow]/[red] markup matches theme intent
                "green": "green",
                "yellow": "yellow",
                "red": "red",
                "magenta": "dark_cyan",
                # Repr highlighter styles: make paths/URLs use link/accent hues
                "repr.url": "underline dark_cyan",
                "repr.path": "dark_cyan",
                "repr.filename": "dark_cyan",
                # Make hyperlinks use the accent color rather than terminal-default blue
                # for better legibility across dark backgrounds
                "link": "underline dark_cyan",
                "selected": "dark_cyan",
                "selected_arrow": "dark_cyan",
                # Softer, low-contrast selection background for dark terminals
                "selected_bg": "bright_black",
                "selected_fg": "white",
                "selected_muted_fg": "bright_white",
                "shortcut_key": "dark_cyan",
                # Status colors
                "success": "green",
                "warning": "yellow",
                "error": "red",
                "info": "blue",
                # Task status colors
                "status.pending": "yellow",
                "status.starting": "blue",
                "status.preparing": "blue",
                "status.running": "green",
                "status.paused": "dark_cyan",
                "status.preempting": "yellow",
                "status.completed": "green",
                "status.failed": "red",
                "status.cancelled": "bright_black",
                # Table elements: headers use a single accent without dimming
                "table.header": "bold dark_cyan",
                # Subtle border to reduce visual noise
                "table.border": "bright_black",
                "table.row": "white",
                "table.row.dim": "bright_black",
                # Semantic elements
                "task.name": "white",
                "task.id": "dark_cyan",
                "task.gpu": "white",
                "task.ip": "dark_cyan",
                "task.time": "bright_black",
                "task.duration": "bright_black",
            },
        ),
        "light": FlowTheme(
            name="light",
            is_dark=False,
            colors={
                # Core neutrals
                "default": "#0F172A",  # ink / primary text
                "muted": "#64748B",  # captions / muted
                "secondary": "#475569",  # secondary text
                "border": "#D1D5DB",  # rules / dividers (slightly darker for visibility)
                # Surfaces (not directly used by Rich but available for renderers)
                "surface": "#FAFBFC",
                "panel": "#FFFFFF",
                "code.bg": "#F6F8FA",
                # Accent & links
                "accent": "#2563EB",
                # Map common markup color tags to brand accent
                "cyan": "#2563EB",
                "blue": "#2563EB",
                "accent-hover": "#1D4ED8",
                "accent.tint": "#EFF6FF",
                "link": "underline #2563EB",
                # Selection and shortcuts
                "selected": "#2563EB",
                "selected_arrow": "#2563EB",
                "selected_bg": "#EFF6FF",  # subtle accent tint background
                "selected_fg": "#0F172A",  # readable ink over tint
                "selected_muted_fg": "#475569",
                "shortcut_key": "#2563EB",
                # Focus ring (for TUI components that support it)
                # Rich doesn't support 8-digit hex (with alpha) in styles; use dim accent
                "focus.ring": "dim #2563EB",
                # Status colors (text/ink by default)
                "success": "#0F6D31",
                "success.icon": "#13AE5C",
                "success.bg": "#E9F7EF",
                "success.border": "#B7E4C7",
                "info": "#1D4ED8",
                "info.icon": "#1E66F5",
                "info.bg": "#E8F0FE",
                "info.border": "#C7DAFE",
                "warning": "#92400E",
                "warning.icon": "#DC7900",
                "warning.bg": "#FFF7ED",
                "warning.border": "#FBD38D",
                "error": "#B91C1C",  # also used as danger-ink
                "error.icon": "#D92D20",
                "error.bg": "#FEECEC",
                "error.border": "#F5B4B0",
                # Task status colors (used for table statuses)
                "status.pending": "#DC7900",  # warning icon hue
                "status.starting": "#1D4ED8",  # info ink
                "status.preparing": "#1D4ED8",  # info ink
                "status.running": "#13AE5C",  # success bright for dot+text
                "status.paused": "#0E7490",  # darker teal for readability
                "status.preempting": "#DC7900",  # warning
                "status.completed": "#13AE5C",  # success
                "status.failed": "#D92D20",  # error icon hue
                "status.cancelled": "#64748B",  # muted
                # Table elements: headers use a single accent without dimming
                "table.header": "bold #2563EB",
                "table.border": "#D1D5DB",
                "table.row": "#0F172A",
                "table.row.dim": "#64748B",
                # Semantic elements
                "task.name": "#0F172A",
                "task.id": "#2563EB",
                "task.gpu": "#0F172A",
                "task.ip": "#1D4ED8",
                "task.time": "#64748B",
                "task.duration": "#64748B",
            },
        ),
        "high_contrast": FlowTheme(
            name="high_contrast",
            is_dark=True,
            colors={
                # Base colors - maximum contrast
                "default": "bright_white",
                "muted": "white",
                "border": "bright_white",
                "accent": "bright_cyan",
                "cyan": "bright_cyan",
                "blue": "bright_cyan",
                # Align basic names with semantic palette
                "green": "bright_green",
                "yellow": "bright_yellow",
                "red": "bright_red",
                "magenta": "bright_cyan",
                # Repr highlighter styles
                "repr.url": "underline bright_cyan",
                "repr.path": "bright_cyan",
                "repr.filename": "bright_cyan",
                # Ensure hyperlinks follow the accent color and are underlined
                "link": "underline bright_cyan",
                "selected": "bright_cyan",
                "selected_arrow": "bright_cyan",
                # Avoid overly saturated blue blocks that reduce text readability; use dim slate
                # which keeps strong contrast while not overpowering the foreground text
                "selected_bg": "bright_black",
                "selected_fg": "white",
                "selected_muted_fg": "bright_white",
                "shortcut_key": "bright_cyan",
                # Status colors - bright variants
                "success": "bright_green",
                "warning": "bright_yellow",
                "error": "bright_red",
                "info": "bright_blue",
                # Task status colors
                "status.pending": "bright_yellow",
                "status.starting": "bright_blue",
                "status.preparing": "bright_blue",
                "status.running": "bright_green",
                "status.paused": "bright_cyan",
                "status.preempting": "bright_yellow",
                "status.completed": "bright_green",
                "status.failed": "bright_red",
                "status.cancelled": "white",
                # Table elements
                "table.header": "bold bright_cyan",
                "table.border": "bright_cyan",
                "table.row": "bright_white",
                "table.row.dim": "white",
                # Semantic elements
                "task.name": "bright_white",
                "task.id": "bright_cyan",
                "task.gpu": "bright_white",
                "task.ip": "bright_cyan",
                "task.time": "white",
                "task.duration": "white",
            },
        ),
        # A subdued modern dark theme with muted borders and a bright cyan accent for links.
        "modern": FlowTheme(
            name="modern",
            is_dark=True,
            colors={
                # Base colors
                "default": "#D1D5DB",  # soft light gray text
                "muted": "#9CA3AF",  # muted gray
                "border": "#4B5563",  # slate/gray border
                # Softer, more neutral blue accent (less saturated than cyan)
                "accent": "#8AB4F8",
                # Map [cyan] to accent so help/hints use the brand accent
                "cyan": "#8AB4F8",
                "blue": "#8AB4F8",
                # Align basic named colors with semantic palette for consistency
                # so ad-hoc [green]/[yellow]/[red]/[magenta] map to theme shades
                "green": "#55B68D",  # match success
                "yellow": "#D0A54D",  # match warning
                "red": "#E06A6A",  # match error
                "magenta": "#8AB4F8",  # avoid purple drift; use accent
                # Repr highlighter styles: unify path/URL highlighting
                "repr.url": "underline #8AB4F8",
                "repr.path": "#8AB4F8",
                "repr.filename": "#8AB4F8",
                # Unify hyperlink styling with accent color for tasteful, legible links
                "link": "underline #8AB4F8",
                "selected": "#334155",
                "selected_arrow": "#8AB4F8",
                # Subtle slate highlight with readable foreground
                "selected_bg": "bright_black",
                "selected_fg": "white",
                "selected_muted_fg": "bright_white",
                "shortcut_key": "#8AB4F8",
                # Status colors
                "success": "#55B68D",  # muted green
                "warning": "#D0A54D",  # muted amber
                "error": "#E06A6A",  # muted red
                "info": "#78A9EE",  # muted blue
                # Task status colors
                "status.pending": "#D0A54D",
                "status.starting": "#78A9EE",
                "status.preparing": "#78A9EE",
                "status.running": "#55B68D",
                # Muted cyan/teal for paused state
                "status.paused": "#6FB8CB",
                "status.preempting": "#D0A54D",
                "status.completed": "#55B68D",
                "status.failed": "#E06A6A",
                "status.cancelled": "#6B7280",
                # Table elements: headers use a single accent without dimming
                "table.header": "bold #8AB4F8",
                "table.border": "#4B5563",
                "table.row": "#D1D5DB",
                "table.row.dim": "#9CA3AF",
                # Semantic elements
                "task.name": "#D1D5DB",
                "task.id": "#8AB4F8",
                "task.gpu": "#D1D5DB",
                "task.ip": "#8AB4F8",
                "task.time": "#9CA3AF",
                "task.duration": "#9CA3AF",
            },
        ),
        # A light variant that keeps the modern aesthetic but optimized for
        # light backgrounds. It mirrors spacing/contrast choices of
        # the dark "modern" while using ink-on-paper neutrals.
        "modern_light": FlowTheme(
            name="modern_light",
            is_dark=False,
            colors={
                # Base colors
                "default": "#0F172A",  # primary ink
                "muted": "#64748B",  # captions / muted
                "border": "#D1D5DB",  # subtle dividers, slightly darker
                # Accent tuned for legibility on light backgrounds
                "accent": "#2563EB",
                "cyan": "#2563EB",
                "blue": "#2563EB",
                # Align basic named colors with semantic palette
                "green": "#10B981",  # match success
                "yellow": "#F59E0B",  # match warning
                "red": "#EF4444",  # match error
                "magenta": "#2563EB",  # keep within brand accent family
                # Repr highlighter styles
                "repr.url": "underline #2563EB",
                "repr.path": "#2563EB",
                "repr.filename": "#2563EB",
                # Hyperlinks use the accent and are underlined
                "link": "underline #2563EB",
                # Selection styling keeps a subtle accent tint
                "selected": "#2563EB",
                "selected_arrow": "#2563EB",
                "selected_bg": "#EFF6FF",
                "selected_fg": "#0F172A",
                "selected_muted_fg": "#475569",
                "shortcut_key": "#2563EB",
                # Status colors
                "success": "#10B981",
                "warning": "#F59E0B",
                "error": "#EF4444",
                "info": "#2563EB",
                # Task status colors
                "status.pending": "#F59E0B",
                "status.starting": "#2563EB",
                "status.preparing": "#2563EB",
                "status.running": "#10B981",
                "status.paused": "#0E7490",
                "status.preempting": "#F59E0B",
                "status.completed": "#10B981",
                "status.failed": "#EF4444",
                "status.cancelled": "#64748B",
                # Table elements: headers use a single accent without dimming
                "table.header": "bold #2563EB",
                "table.border": "#D1D5DB",
                "table.row": "#0F172A",
                "table.row.dim": "#64748B",
                # Semantic elements
                "task.name": "#0F172A",
                "task.id": "#2563EB",
                "task.gpu": "#0F172A",
                "task.ip": "#2563EB",
                "task.time": "#64748B",
                "task.duration": "#64748B",
            },
        ),
    }

    def __init__(self):
        """Initialize theme manager."""
        self.current_theme_name = None
        self.current_theme = None
        self.custom_themes_dir = Path.home() / ".flow" / "themes"
        self._console_cache = {}

    def detect_terminal_theme(self) -> str:
        """Auto-detect terminal theme.

        Returns:
            "modern_light" when a light background is detected; otherwise "modern".
        """
        # Check environment variables first
        if os.environ.get("FLOW_THEME"):
            return os.environ["FLOW_THEME"]

        # Check persisted config (~/.flow/config.yaml)
        try:
            from pathlib import Path

            import yaml

            config_path = Path.home() / ".flow" / "config.yaml"
            if config_path.exists():
                with open(config_path) as f:
                    cfg = yaml.safe_load(f) or {}
                    if isinstance(cfg, dict) and cfg.get("theme"):
                        return str(cfg.get("theme"))
        except Exception:
            # Ignore config errors and fall back to detection
            pass

        # Check common terminal theme indicators
        if os.environ.get("COLORFGBG"):
            # Format: "foreground;background"
            colors = os.environ["COLORFGBG"].split(";")
            if len(colors) >= 2:
                try:
                    bg = int(colors[1])
                    # Common light backgrounds: 7 (white), 15 (bright white)
                    if bg in [7, 15]:
                        return "modern_light"
                except ValueError:
                    pass

        # Check terminal-specific environment variables
        if os.environ.get("ITERM_PROFILE"):
            # iTerm2 specific
            profile = os.environ["ITERM_PROFILE"].lower()
            if any(light in profile for light in ["light", "solarized-light", "papercolor"]):
                return "modern_light"

        # Check if running in light mode terminals
        if os.environ.get("TERMINAL_EMULATOR") == "JetBrains-JediTerm":
            # IntelliJ IDEA terminal often uses light themes
            return "modern_light"

        # Default to modern (dark) theme
        return "modern"

    def load_theme(self, theme_name: str | None = None) -> FlowTheme:
        """Load theme by name or auto-detect.

        Args:
            theme_name: Theme name to load, or None to auto-detect

        Returns:
            Loaded theme
        """
        if theme_name is None:
            theme_name = self.detect_terminal_theme()

        # If user asked for modern explicitly but terminal looks light, use
        # modern_light to avoid low-contrast output. If they explicitly chose
        # "light", keep it as-is.
        if theme_name == "modern":
            detected = self.detect_terminal_theme()
            if detected == "modern_light":
                theme_name = "modern_light"

        # Check built-in themes first
        if theme_name in self.THEMES:
            self.current_theme_name = theme_name
            self.current_theme = self.THEMES[theme_name]
            return self.current_theme

        # Try to load custom theme
        custom_theme = self._load_custom_theme(theme_name)
        if custom_theme:
            self.current_theme_name = theme_name
            self.current_theme = custom_theme
            return custom_theme

        # Fallback to default (modern)
        self.current_theme_name = "modern"
        self.current_theme = self.THEMES["modern"]
        return self.current_theme

    def _load_custom_theme(self, theme_name: str) -> FlowTheme | None:
        """Load custom theme from file.

        Args:
            theme_name: Name of custom theme

        Returns:
            Loaded theme or None if not found
        """
        if not self.custom_themes_dir.exists():
            return None

        # Try YAML first, then JSON
        for ext in [".yaml", ".yml", ".json"]:
            theme_file = self.custom_themes_dir / f"{theme_name}{ext}"
            if theme_file.exists():
                try:
                    with open(theme_file) as f:
                        if ext == ".json":
                            data = json.load(f)
                        else:
                            data = yaml.safe_load(f)

                    return FlowTheme(
                        name=data.get("name", theme_name),
                        colors=data.get("colors", {}),
                        is_dark=data.get("is_dark", True),
                    )
                except Exception:
                    # Invalid theme file
                    pass

        return None

    def create_console(
        self, force_color: bool | None = None, no_color: bool | None = None, **kwargs
    ) -> Console:
        """Create theme-aware Rich Console instance.

        Args:
            force_color: Force color output
            no_color: Disable color output
            **kwargs: Additional arguments for Console

        Returns:
            Configured Console instance
        """
        # Load theme if not already loaded
        if self.current_theme is None:
            self.load_theme()

        # Handle color forcing via args and environment
        flow_color = (os.environ.get("FLOW_COLOR") or "").lower().strip()
        if flow_color not in {"auto", "always", "never", ""}:
            flow_color = "auto"

        if no_color or os.environ.get("NO_COLOR") or flow_color == "never":
            kwargs["no_color"] = True
        elif force_color or flow_color == "always":
            kwargs["force_terminal"] = True

        # Basic color-system detection with graceful degradation
        if "color_system" not in kwargs:
            colorterm = (os.environ.get("COLORTERM") or "").lower()
            term = (os.environ.get("TERM") or "").lower()
            if any(k in colorterm for k in ("truecolor", "24bit")):
                kwargs["color_system"] = "truecolor"
            elif "256color" in term:
                kwargs["color_system"] = "256"

        # Apply theme
        kwargs["theme"] = self.current_theme.to_rich_theme()

        # Create console
        console = Console(**kwargs)

        return console

    def is_color_enabled(self) -> bool:
        """Return True if color output should be enabled based on env and defaults."""
        flow_color = (os.environ.get("FLOW_COLOR") or "").lower().strip()
        if os.environ.get("NO_COLOR") or flow_color == "never":
            return False
        # If explicitly requested always, or auto/default, consider enabled
        return True

    def get_color(self, color_key: str) -> str:
        """Get color value for a given key.

        Args:
            color_key: Color key (e.g., "status.running")

        Returns:
            Color value or default
        """
        if self.current_theme is None:
            self.load_theme()

        # Special-case: provide a theme-aware default for AEP accent without
        # requiring every theme to define it explicitly.
        if color_key == "aep.accent":
            # Use explicit theme value when provided; otherwise a dark/light default
            if "aep.accent" in self.current_theme.colors:
                return self.current_theme.colors["aep.accent"]
            return "#a8d7e8" if getattr(self.current_theme, "is_dark", True) else "#003366"

        return self.current_theme.colors.get(color_key, "default")

    def list_themes(self) -> list[str]:
        """List all available themes.

        Returns:
            List of theme names
        """
        themes = list(self.THEMES.keys())

        # Add custom themes
        if self.custom_themes_dir.exists():
            for theme_file in self.custom_themes_dir.glob("*.{yaml,yml,json}"):
                theme_name = theme_file.stem
                if theme_name not in themes:
                    themes.append(theme_name)

        return sorted(themes)


# Global theme manager instance
theme_manager = ThemeManager()
