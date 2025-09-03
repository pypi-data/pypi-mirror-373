"""Shared visual constants for CLI styling.

Defines colors, typography, and UI patterns used across the Flow CLI for
consistent presentation.
"""

import os
from dataclasses import dataclass

from flow.cli.utils.theme_manager import theme_manager
from flow.resources.loader import DataLoader

# Status indicators from data file with safe defaults
_loader = DataLoader()
_visual = _loader.cli_visual if hasattr(_loader, "cli_visual") else {}
STATUS_INDICATORS = _visual.get(
    "status_indicators",
    {
        "configured": "●",
        "missing": "○",
        "invalid": "◐",
        "optional": "○",
        "active": "●",
        "inactive": "○",
        "selected": ">",
        "unselected": " ",
    },
)


@dataclass(frozen=True)
class DensityConfig:
    """Global UI density configuration resolved once per process.

    Values derive from environment variables with sensible defaults and can be
    used across components to keep spacing consistent.
    """

    mode: str  # compact | comfortable | auto
    selector_item_gap: int  # blank lines between items in interactive selector
    table_row_vpad: int  # vertical padding for table rows


def _resolve_density() -> DensityConfig:
    # Global density: FLOW_DENSITY has precedence; selector-specific override allowed
    mode = (os.environ.get("FLOW_DENSITY", "auto") or "auto").strip().lower()
    if mode not in {"compact", "comfortable", "auto"}:
        mode = "auto"

    # Selector-specific direct override for power users
    selector_override = (os.environ.get("FLOW_SELECTOR_DENSITY", "") or "").strip().lower()
    selector_mode = selector_override if selector_override in {"compact", "comfortable"} else mode

    # Defaults for gaps/padding by mode (from data with fallback)
    density_cfg = _visual.get("density", {})
    selector_item_gap = (
        int(density_cfg.get("selector_compact_item_gap", 0))
        if selector_mode == "compact"
        else int(density_cfg.get("selector_comfortable_item_gap", 1))
    )
    # Tables should be dense by default; only expand when explicitly comfortable
    if mode in {"compact", "auto"}:
        table_row_vpad = int(density_cfg.get("table_row_vpad_compact", 0))
    else:  # comfortable
        table_row_vpad = int(density_cfg.get("table_row_vpad_comfortable", 1))

    return DensityConfig(
        mode=mode, selector_item_gap=selector_item_gap, table_row_vpad=table_row_vpad
    )


DENSITY = _resolve_density()

# Interactive element spacing (defaults; components can interpret with DENSITY)
_spacing_cfg = _visual.get("spacing", {})
SPACING = {
    "section_gap": int(_spacing_cfg.get("section_gap", 1)),
    # Default selector gap; may be clamped based on list length/terminal height
    "item_gap": DENSITY.selector_item_gap,
    "panel_width": int(_spacing_cfg.get("panel_width", 60)),
    "menu_width": int(_spacing_cfg.get("menu_width", 50)),
}


def get_colors() -> dict[str, str]:
    """Get theme-aware color mapping.

    Returns:
        Dictionary of color names to values
    """
    return {
        # Primary colors
        "primary": theme_manager.get_color("default"),
        "accent": theme_manager.get_color("accent"),
        "muted": theme_manager.get_color("muted"),
        # Status colors
        "success": theme_manager.get_color("success"),
        "warning": theme_manager.get_color("warning"),
        "error": theme_manager.get_color("error"),
        "info": theme_manager.get_color("info"),
        # UI element colors
        "border": theme_manager.get_color("border"),
        "highlight": "reverse",
    }


def get_typography() -> dict[str, str]:
    """Get theme-aware typography styles.

    Returns:
        Dictionary of style templates
    """
    colors = get_colors()
    return {
        "title": f"[bold {colors['primary']}]",
        "subtitle": f"[bold {colors['accent']}]",
        # Keep standard body copy neutral for readability
        "body": f"[{colors['primary']}]",
        "muted": f"[{colors['muted']}]",
        "success": f"[{colors['success']}]",
        "warning": f"[{colors['warning']}]",
        "error": f"[{colors['error']}]",
    }


def get_panel_styles() -> dict[str, dict]:
    """Get theme-aware panel styles for consistent UI.

    Returns:
        Dictionary of panel style configurations
    """
    from flow.cli.utils.theme_manager import theme_manager

    # Use theme manager colors for consistency
    return {
        "main": {
            # Use accent for primary/welcome panels to reflect brand theme
            "border_style": theme_manager.get_color("accent"),
            "title_align": "center",
            "padding": (1, 2),
            "box": "ROUNDED",  # Standard box style
        },
        "secondary": {
            "border_style": theme_manager.get_color("muted"),
            "title_align": "left",
            "padding": (0, 1),
            "box": "ROUNDED",
        },
        "success": {
            "border_style": theme_manager.get_color("success"),
            "title_align": "center",
            "padding": (1, 2),
            "box": "ROUNDED",
        },
        "error": {
            "border_style": theme_manager.get_color("error"),
            "title_align": "center",
            "padding": (1, 2),
            "box": "ROUNDED",
        },
        "info": {
            "border_style": theme_manager.get_color("info"),
            "title_align": "center",
            "padding": (1, 2),
            "box": "ROUNDED",
        },
    }


def get_status_display(status: str, text: str, *, icon_style: str = "dot") -> str:
    """Get consistently formatted status display.

    Args:
        status: Status type (configured, missing, etc.)
        text: Status text to display
        icon_style: Visual style for the status icon. Supported:
            - "dot" (default): solid/outlined dots
            - "check": check/cross icons for stronger semantics

    Returns:
        Formatted status string with icon and color
    """
    # Choose icon by style without changing existing default behavior
    if icon_style == "check":
        # Strong semantics for accessibility (do not rely on color alone)
        check_icons = {
            "configured": "✓",
            "missing": "✖",
            "invalid": "⚠",
            "optional": "•",
            "active": "✓",
            "inactive": "✖",
            "detected": "ℹ",
            "info": "ℹ",
        }
        icon = check_icons.get(status, "•")
    else:
        icon = STATUS_INDICATORS.get(status, "○")

    colors = get_colors()
    # Use darker ink for readable text; bright color for the icon when available
    # Default mapping aligns with semantic palette guidance
    if status == "configured":
        icon_color = theme_manager.get_color("accent")
        text_color = theme_manager.get_color("accent")
    elif status in ("error", "danger"):
        icon_color = theme_manager.get_color("error.icon") or colors["error"]
        text_color = theme_manager.get_color("error")
    elif status in ("missing", "invalid", "warning"):
        icon_color = theme_manager.get_color("warning.icon") or colors["warning"]
        text_color = theme_manager.get_color("warning")
    elif status in ("detected", "info"):
        icon_color = theme_manager.get_color("info.icon") or colors["info"]
        text_color = theme_manager.get_color("info")
    elif status == "optional":
        icon_color = colors["muted"]
        text_color = colors["muted"]
    else:
        icon_color = colors["accent"]
        text_color = colors["accent"]

    return f"[{icon_color}]{icon}[/{icon_color}] [{text_color}]{text}[/{text_color}]"


def format_text(style: str, text: str) -> str:
    """Apply consistent text styling.

    Args:
        style: Style key from TYPOGRAPHY
        text: Text to format

    Returns:
        Formatted text string
    """
    typography = get_typography()
    colors = get_colors()
    template = typography.get(style, f"[{colors['accent']}]")

    # Always close with a reset tag to avoid mismatches (e.g. "[bold accent]" -> "[/]")
    return f"{template}{text}[/]"
