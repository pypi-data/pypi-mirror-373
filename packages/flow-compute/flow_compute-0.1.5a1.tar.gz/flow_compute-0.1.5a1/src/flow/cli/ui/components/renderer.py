"""Terminal rendering logic for interactive selection."""

from __future__ import annotations

import html as _html
import os
import re
import shutil as _shutil
from typing import TYPE_CHECKING

from flow.cli.ui.components.formatters import TaskFormatter
from flow.cli.utils.theme_manager import theme_manager

if TYPE_CHECKING:
    from flow.cli.ui.components.models import SelectionItem, SelectionState


def _html_escape(text: str) -> str:
    """Escape text for prompt_toolkit HTML (do not escape quotes to keep output compact)."""
    try:
        return _html.escape(text, quote=False)
    except Exception:
        return text


# Regexes used in helpers
_CSI_PATTERN = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")
_HTML_TAG_PATTERN = re.compile(r"<[^>]+>")

# Extracted color constants for easy testing and reuse
DEFAULT_THEME_KEYS = {
    "accent": "accent",
    "dim": "muted",
    "success": "success",
    "warning": "warning",
    "error": "error",
    "info": "info",
}

# Minimal ANSI palette for nearest-color mapping
ANSI_PALETTE: list[tuple[str, tuple[int, int, int]]] = [
    ("ansiblack", (0, 0, 0)),
    ("ansired", (205, 0, 0)),
    ("ansigreen", (0, 205, 0)),
    ("ansiyellow", (205, 205, 0)),
    ("ansiblue", (0, 0, 205)),
    ("ansimagenta", (205, 0, 205)),
    ("ansicyan", (0, 205, 205)),
    ("ansiwhite", (229, 229, 229)),
    ("ansibrightblack", (127, 127, 127)),
    ("ansibrightred", (255, 85, 85)),
    ("ansibrightgreen", (85, 255, 85)),
    ("ansibrightyellow", (255, 255, 85)),
    ("ansibrightblue", (85, 85, 255)),
    ("ansibrightmagenta", (255, 85, 255)),
    ("ansibrightcyan", (85, 255, 255)),
    ("ansiwhite", (255, 255, 255)),
]


def _strip_ansi(text: str) -> str:
    """Remove ANSI/CSI escape sequences (e.g., CPR: ESC[36;1R) from text."""
    try:
        return _CSI_PATTERN.sub("", text)
    except Exception:
        return text


def _visible_length(text: str) -> int:
    """Compute on-screen length by stripping ANSI and HTML tags.

    This helps us fit UI hints within the current terminal width.
    """
    try:
        no_ansi = _strip_ansi(text)
        no_tags = _HTML_TAG_PATTERN.sub("", no_ansi)
        return len(no_tags)
    except Exception:
        return len(text)


def _get_terminal_width(default: int = 80) -> int:
    """Best-effort terminal width detection.

    Falls back to environment and then a sensible default.
    """
    # Primary: shutil
    try:
        cols = int(getattr(_shutil.get_terminal_size((default, 24)), "columns", default))
        if cols > 0:
            return cols
    except Exception:
        pass
    # Env fallbacks
    for env_var in ("COLUMNS", "TERM_COLS"):
        try:
            cols = int(os.environ.get(env_var, "0"))
            if cols > 0:
                return cols
        except Exception:
            continue
    return default


def _nearest_ansi_from_hex(hex_color: str) -> str:
    """Map a hex color like "#8AB4F8" to closest ANSI color name.

    Returns one of: ansiblack, ansiwhite, ansired, ansigreen, ansiyellow,
    ansiblue, ansimagenta, ansicyan and their bright variants.
    """
    try:
        hex_color = hex_color.strip()
        if not hex_color.startswith("#") or len(hex_color) not in (4, 7):
            return "ansiwhite"
        # Expand shorthand like #abc -> #aabbcc
        if len(hex_color) == 4:
            hex_color = "#" + "".join(ch * 2 for ch in hex_color[1:])
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        palette = ANSI_PALETTE

        def dist2(c1: tuple[int, int, int], c2: tuple[int, int, int]) -> int:
            return (c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2

        best = min(palette, key=lambda p: dist2((r, g, b), p[1]))
        return best[0]
    except Exception:
        return "ansiwhite"


def map_rich_to_prompt_toolkit_color(rich_color: str) -> str:
    """Map Rich color names to prompt_toolkit color names.

    Rich and prompt_toolkit have different interpretations of standard color names.
    This function ensures consistent color rendering between the two libraries.

    Args:
        rich_color: Color name from Rich/theme manager

    Returns:
        Equivalent color name for prompt_toolkit
    """
    # Map standard ANSI colors to their prompt_toolkit equivalents
    color_map = {
        "green": "ansigreen",  # Rich's green -> PT's ansigreen for softer appearance
        "red": "ansired",
        "yellow": "ansiyellow",
        "blue": "ansiblue",
        "cyan": "ansicyan",
        "magenta": "ansimagenta",
        "white": "ansiwhite",
        "black": "ansiblack",
        # Bright variants
        "bright_green": "ansibrightgreen",
        "bright_red": "ansibrightred",
        "bright_yellow": "ansibrightyellow",
        "bright_blue": "ansibrightblue",
        "bright_cyan": "ansibrightcyan",
        "bright_magenta": "ansibrightmagenta",
        # Some PT versions don't accept ansibrightwhite/ansibrightblack; map to base
        "bright_white": "ansiwhite",
        "bright_black": "ansiblack",
        # Dark variants
        "dark_green": "darkgreen",
        "dark_red": "darkred",
        "dark_blue": "darkblue",
        # Other colors remain as-is
    }

    # Normalize a couple of problematic variants first
    if rich_color in {"ansibrightwhite", "brightwhite"}:
        return "ansiwhite"
    if rich_color in {"ansibrightblack", "brightblack"}:
        return "ansiblack"

    # Reduce composite strings like "underline #2563EB" to last token
    token = rich_color.strip()
    try:
        if " " in token:
            token = token.split()[-1]
    except Exception:
        pass

    # Translate a few aliases with underscore into prompt_toolkit names
    token = token.replace("bright_", "ansibright").replace("dark_", "dark")
    token = token.replace("_", "")  # e.g., dark_cyan -> darkcyan

    # Map known simple names via color_map
    mapped = color_map.get(token, token)
    # Guard against invalid style names like "ansibrightwhite" when themes
    # pass through composite values (e.g., "bold white", "underline #RRGGBB").
    try:
        # Convert hex colors to nearest ANSI name
        if mapped.startswith("#"):
            return _nearest_ansi_from_hex(mapped)
        # Normalize a few common aliases
        if mapped == "bright_white" or mapped == "ansibrightwhite":
            return "ansiwhite"
        if mapped == "bright_black" or mapped == "ansibrightblack":
            return "ansiblack"
    except Exception:
        pass
    return mapped


def style(text: str, fg: str | None = None, bg: str | None = None) -> str:
    """Apply color styling to text for prompt_toolkit rendering.

    Args:
        text: Text to style
        fg: Foreground color
        bg: Background color

    Returns:
        HTML-styled text for prompt_toolkit
    """
    # Remove any ANSI/CSI sequences, then escape
    text = _strip_ansi(text)
    # Do not emit empty <style> tags; prompt_toolkit will render them literally
    if text == "":
        return ""
    if not fg and not bg:
        return _html_escape(text)

    style_parts = []
    if fg:
        style_parts.append(f"fg='{map_rich_to_prompt_toolkit_color(fg)}'")
    if bg:
        style_parts.append(f"bg='{map_rich_to_prompt_toolkit_color(bg)}'")

    style_str = " ".join(style_parts)
    # Use single quotes for attributes for prompt_toolkit HTML compatibility
    return f"<style {style_str}>{_html_escape(text)}</style>"


def highlight_matches(text: str, query: str, color_name: str) -> str:
    """Highlight matching parts of text based on search query.

    Args:
        text: Text to highlight
        query: Search query
        color_name: Color to use for highlighting

    Returns:
        HTML-formatted text with highlights
    """
    # Sanitize input text first
    text = _strip_ansi(text)
    if not query:
        return _html_escape(text)

    # Simple case-insensitive highlighting
    lower_text = text.lower()
    lower_query = query.lower()

    result = []
    last_end = 0

    start = lower_text.find(lower_query)
    while start != -1:
        # Add text before match
        if start > last_end:
            result.append(_html_escape(text[last_end:start]))

        # Add highlighted match
        end = start + len(query)
        result.append(style(text[start:end], fg=color_name))

        last_end = end
        start = lower_text.find(lower_query, end)

    # Add remaining text
    if last_end < len(text):
        result.append(_html_escape(text[last_end:]))

    return "".join(result)


class SelectionRenderer:
    """Handles rendering of selection UI components."""

    def __init__(self):
        """Initialize the renderer."""
        # Ensure theme loaded, then use color keys directly
        theme_manager.load_theme()
        # For compatibility, store a simple mapping of color keys
        self.theme = {k: theme_manager.get_color(v) for k, v in DEFAULT_THEME_KEYS.items()}
        self.console = theme_manager.create_console()

    def render_header(
        self,
        title: str,
        breadcrumbs: list[str],
        extra_html: str | None,
        filter_text: str,
        item_count: int,
        filtered_count: int,
        show_help: bool,
        allow_multiple: bool,
        allow_back: bool,
    ) -> str:
        """Render the header section of the selector.

        Args:
            title: Main title
            breadcrumbs: Navigation breadcrumbs
            extra_html: Additional HTML to display
            filter_text: Current filter text
            item_count: Total number of items
            filtered_count: Number of filtered items
            show_help: Whether to show help text
            allow_multiple: Whether multiple selection is enabled
            allow_back: Whether back navigation is enabled

        Returns:
            HTML-formatted header string
        """
        lines = []

        # Title and breadcrumbs
        if breadcrumbs:
            breadcrumb_text = " > ".join(breadcrumbs)
            lines.append(style(breadcrumb_text, fg=self.theme["dim"]))

        lines.append(style(title, fg=self.theme["accent"]))

        # Extra header content
        if extra_html:
            lines.append(extra_html)

        # Filter/search line
        if filter_text:
            lines.append(
                f"{style('Filter:', fg=self.theme['dim'])} "
                f"{style(filter_text, fg=self.theme['info'])}"
            )

        # Item count
        if filtered_count < item_count:
            count_text = f"Showing {filtered_count} of {item_count} items"
        else:
            count_text = f"{item_count} items"
        lines.append(style(count_text, fg=self.theme["dim"]))

        # Help text
        if show_help:
            from flow.cli.ui.components.keybindings import get_help_text

            help_items = get_help_text(allow_multiple, allow_back)
            help_lines = []
            for key, desc in help_items:
                help_lines.append(f"{style(key, fg=self.theme['info'])}: {desc}")
            lines.append("")
            lines.append(style("Keyboard shortcuts:", fg=self.theme["dim"]))
            lines.extend(help_lines)

        return "\n".join(lines)

    def render_item(
        self,
        item: SelectionItem,
        is_selected: bool,
        is_current: bool,
        is_checked: bool,
        highlight_query: str,
    ) -> str:
        """Render a single selection item.

        Args:
            item: The item to render
            is_selected: Whether this is the currently highlighted item (unused, kept for compatibility)
            is_current: Whether cursor is on this item
            is_checked: Whether item is checked (for multi-select)
            highlight_query: Query string for highlighting

        Returns:
            HTML-formatted item string
        """
        # Note: is_selected parameter kept for backward compatibility but not used
        # Build item display (multi-line when stacked=True)
        left_pad_normal = "  "  # indent for non-current rows
        left_pad_current = ""  # outdent for hovered row

        # Selection indicator with proper indentation (ASCII-safe fallbacks)
        import os as _os

        _ascii = str(_os.environ.get("FLOW_ASCII_ONLY", "0")).strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        _arrow = ">" if _ascii else "▸"
        _check = "*" if _ascii else "✓"
        if is_current:
            prefix = f"{left_pad_current}{_arrow}"
        elif is_checked:
            prefix = f"{left_pad_normal}{_check}"
        else:
            prefix = f"{left_pad_normal} "

        # Title (line 1)
        if is_current:
            title_line = f"{prefix} {item.title}"
        else:
            # Use accent for search highlights for consistency with other UI cues
            title_highlight = highlight_matches(item.title, highlight_query, self.theme["accent"])
            title_line = f"{prefix} {title_highlight}"

        lines = [title_line]

        # Subtitle (line 2 when stacked, inline otherwise)
        subtitle_line = ""
        if item.subtitle:
            if is_current:
                # Avoid nested styles when current row is wrapped later
                sub_render = item.subtitle
            else:
                sub_render = style(
                    highlight_matches(item.subtitle, highlight_query, self.theme["accent"]),
                    fg=self.theme["dim"],
                )
            if getattr(self, "_stacked", False):
                # Align stacked metadata under the title
                lines.append(f"{left_pad_normal}   {sub_render}")
            else:
                # Minimal separator before subtitle (ASCII-safe)
                bullet = "-" if _ascii else "·"
                subtitle_line = f" {bullet} {sub_render}"

        # Status (line 3 when stacked, inline otherwise)
        status_frag = ""
        if item.status:
            # Normalize enum-like values such as "TaskStatus.RUNNING" → "Running"
            raw_status = str(item.status)
            clean = raw_status.replace("TaskStatus.", "").replace("_", " ").strip()
            display_status = clean[:1].upper() + clean[1:].lower() if clean else ""

            # Use centralized status config for symbol and color
            cfg = TaskFormatter.get_status_config(display_status)
            symbol = cfg.get("symbol", "")
            color = cfg.get("color", theme_manager.get_color("muted"))

            # ASCII-only fallback for status symbol
            if _ascii:
                ascii_map = {
                    "●": "*",
                    "○": "o",
                    "⏸": "||",
                    "✓": "*",
                    "✖": "x",
                }
                symbol = ascii_map.get(symbol, symbol)

            text = f"{symbol} {display_status}".strip()

            status_frag = text if is_current else style(text, fg=color)

        if not getattr(self, "_stacked", False):
            # Inline layout: title + optional subtitle + status, with a subtle
            # middle-dot separator between subtitle and status when present.
            inline = lines[0]
            if subtitle_line:
                inline = inline + subtitle_line
                if status_frag:
                    sep_char = "." if _ascii else "•"
                    # Use plain separator to avoid leaking markup when HTML styling
                    # isn't supported by the current terminal/renderer context.
                    sep = f" {sep_char} "
                    inline = inline + sep + status_frag
            else:
                if status_frag:
                    inline = inline + " " + status_frag
            line = inline
            # Apply selection background/foreground to the whole line for the current row
            if is_current:
                try:
                    selected_bg = theme_manager.get_color("selected_bg")
                    selected_fg = theme_manager.get_color("selected_fg")
                    return style(line, fg=selected_fg, bg=selected_bg)
                except Exception:
                    return line
            return line

        # Stacked layout: title, subtitle, status on their own lines
        if status_frag:
            lines.append(f"{left_pad_normal}   {status_frag}")

        if is_current:
            # To avoid nested <style> tags rendering literally, apply selection
            # styling per-line rather than wrapping the whole block.
            try:
                selected_bg = theme_manager.get_color("selected_bg")
                selected_fg = theme_manager.get_color("selected_fg")
                styled_lines = [style(ln, fg=selected_fg, bg=selected_bg) for ln in lines]
                return "\n".join(styled_lines)
            except Exception:
                return "\n".join(lines)

        return "\n".join(lines)

    def _get_status_color(self, status: str) -> str:
        """Get color for a status string."""
        status_lower = status.lower()

        if "running" in status_lower or "active" in status_lower:
            return self.theme["info"]
        elif "success" in status_lower or "completed" in status_lower:
            return self.theme["success"]
        elif "failed" in status_lower or "error" in status_lower:
            return self.theme["error"]
        elif "pending" in status_lower or "waiting" in status_lower:
            return self.theme["warning"]
        else:
            return self.theme["dim"]


# --- Compatibility facade expected by orchestrator ---
class Renderer(SelectionRenderer):
    """Backwards-compatible renderer wrapper.

    Provides the minimal methods used by the orchestrator: render_list() and
    render_status_bar().
    """

    def __init__(
        self,
        title: str | None = None,
        subtitle: str | None = None,
        compact_mode: bool = False,
        show_keybindings: bool = True,
        *,
        row_spacing: int = 0,
        stacked: bool = False,
        persistent_nav: bool = False,
    ) -> None:
        super().__init__()
        # Store, in case future header rendering needs them
        self._title = title
        self._subtitle = subtitle
        self._compact_mode = compact_mode
        self._show_keybindings = show_keybindings
        # New layout knobs (kept backward-compatible)
        try:
            self._row_spacing = max(0, int(row_spacing))
        except Exception:
            self._row_spacing = 0
        self._stacked = bool(stacked)
        self._persistent_nav = bool(persistent_nav)

    def render_list(self, state: SelectionState) -> str:
        # Render visible items into a single HTML string
        from flow.cli.ui.components.state_machine import SelectionStateMachine

        # Compute viewport size from terminal height and layout characteristics
        try:
            term_lines = int(getattr(_shutil.get_terminal_size((80, 24)), "lines", 24))
        except Exception:
            term_lines = 24

        # Reserve lines for status + nav; help is toggled and will expand on demand
        reserved_lines = 2
        available_lines = max(4, term_lines - reserved_lines)

        # Optional top padding between top and first item
        # Default to tasteful breathing room; keep env override for power users
        try:
            import os as _os

            top_pad = int(_os.environ.get("FLOW_LIST_TOP_PADDING", "2"))
            top_pad = max(0, min(3, top_pad))
        except Exception:
            top_pad = 2

        # Estimate per-item height (stacked uses ~3 lines: title, subtitle, status)
        # When terminal height is constrained, prefer inline to maximize items shown
        effective_stacked = False if term_lines <= 20 else getattr(self, "_stacked", False)
        self._stacked = bool(effective_stacked)
        per_item_lines = 3 if self._stacked else 1
        viewport_size = max(1, (available_lines - top_pad) // max(1, per_item_lines))
        machine = SelectionStateMachine(
            items=state.items or [],
            state=state,
            viewport_size=viewport_size,
            allow_multiple=getattr(state, "multiselect", False),
        )
        # Make filtering reflect current state without mutating selection/viewport
        try:
            filter_text = getattr(state, "filter_text", "") or ""
            if filter_text:
                lower = filter_text.lower()
                machine.filtered_items = [
                    it
                    for it in (state.items or [])
                    if lower in (it.id + it.title + (it.subtitle or "")).lower()
                ]
            else:
                machine.filtered_items = state.items or []
        except Exception:
            machine.filtered_items = state.items or []
        lines: list[str] = []
        # Insert top padding lines
        if top_pad:
            lines.extend([""] * top_pad)
        visible = machine.get_visible_items()
        for idx, item in enumerate(visible):
            is_current = (state.viewport_start + idx) == state.selected_index
            is_checked = item.id in state.selected_ids
            is_selected = is_current
            block = self.render_item(
                item,
                is_selected=is_selected,
                is_current=is_current,
                is_checked=is_checked,
                highlight_query=getattr(state, "filter_text", ""),
            )
            # Subtle numeric jump hints for first 1–9 visible items
            try:
                import os as _os

                _show_hints = str(
                    _os.environ.get("FLOW_NUMKEY_HINTS", "1")
                ).strip().lower() not in {"0", "false", "no", "off"}
            except Exception:
                _show_hints = True
            if _show_hints and idx < 9:
                hint = str(idx + 1)
                hint_styled = style(hint, fg=self.theme["dim"]) + " "
                parts = block.split("\n")
                if parts:
                    pad = " " * (len(hint) + 1)
                    first = f"{hint_styled}{parts[0]}"
                    rest = [pad + p for p in parts[1:]]
                    block = "\n".join([first] + rest)
            lines.append(block)
            # Optional vertical spacing between rows (without affecting selection logic)
            if getattr(self, "_row_spacing", 0) > 0 and idx < len(visible) - 1:
                lines.extend([""] * int(getattr(self, "_row_spacing", 0)))
        return "\n".join(lines)

    def render_status_bar(self, state: SelectionState) -> str:
        total = len(state.items or [])
        filter_text = getattr(state, "filter_text", "") or ""
        if filter_text:
            lower = filter_text.lower()
            filtered = sum(
                1
                for it in (state.items or [])
                if lower in (it.id + it.title + (it.subtitle or "")).lower()
            )
        else:
            filtered = total

        # Build base parts
        title_part = style(self._title or "Select", fg=self.theme["accent"])
        # Current position among filtered items (1-based)
        try:
            pos_cur = min(
                max(0, int(getattr(state, "selected_index", 0))), max(0, filtered - 1)
            ) + (1 if filtered else 0)
        except Exception:
            pos_cur = 0
        pos_part = f"{style('Pos:', fg=self.theme['dim'])} {pos_cur}/{filtered or 0}"
        count_part = f"{style('Items:', fg=self.theme['dim'])} {filtered}/{total}"
        # Friendly placeholder when in search mode with empty filter
        placeholder = "type to search…"
        try:
            import os as _os

            if str(_os.environ.get("FLOW_ASCII_ONLY", "0")).strip().lower() in {
                "1",
                "true",
                "yes",
                "on",
            }:
                placeholder = "type to search..."
        except Exception:
            pass
        filter_label = style("Filter:", fg=self.theme["dim"])
        filter_value = (
            _html_escape(filter_text)
            if filter_text
            else (
                style(placeholder, fg=self.theme["dim"])
                if getattr(state, "search_mode", False)
                else ""
            )
        )
        filter_part = f"{filter_label} {filter_value}".rstrip()

        # Progressive compaction to fit terminal width
        term_width = _get_terminal_width(80)
        sep = "  "

        # Candidate variants from most verbose to shortest
        variants = [
            f"{title_part}{sep}{pos_part}{sep}{count_part}{sep}{filter_part}",
            f"{title_part}{sep}{pos_part}{sep}{count_part}",
            f"{title_part}{sep}{pos_part}",
            f"{title_part}{sep}{count_part}",
            f"{title_part}",
        ]

        chosen = variants[-1]
        for candidate in variants:
            if _visible_length(candidate) <= term_width:
                chosen = candidate
                break

        # Append a minimal help affordance when there is room and help is hidden
        if not getattr(state, "show_help", False):
            hint = style(" [?]", fg=self.theme["info"])
            if _visible_length(chosen + hint) <= term_width:
                chosen = chosen + hint
        return chosen

    def render_nav(self, allow_multiple: bool, allow_back: bool) -> str:
        """Always-visible navigation footer that adapts to terminal width.

        It collapses or truncates hint items to ensure the footer fits in one line.
        """
        from flow.cli.ui.components.keybindings import get_help_text

        items = get_help_text(allow_multiple=allow_multiple, allow_back=allow_back)
        term_width = _get_terminal_width(80)

        def fmt(key: str, desc: str) -> str:
            return f"{style(key, fg=self.theme['info'])} {desc}"

        sep = style(" • ", fg=self.theme["dim"])

        # Start with full items; progressively fall back
        full_parts = [fmt(k, v) for k, v in items]
        base = "  "

        def join(parts: list[str]) -> str:
            return base + sep.join(parts)

        # 1) Try full text
        footer = join(full_parts)
        if _visible_length(footer) <= term_width:
            return footer

        # 2) Try shortened descriptions (first word or abbreviation)
        short_parts: list[str] = []
        for k, v in items:
            first = v.split()[0] if v else v
            short_parts.append(fmt(k, first))
        footer = join(short_parts)
        if _visible_length(footer) <= term_width:
            return footer

        # 3) Keys only
        keys_only = [style(k, fg=self.theme["info"]) for k, _ in items]
        footer = join(keys_only)
        if _visible_length(footer) <= term_width:
            return footer

        # 4) Truncate with ellipsis to last possible fit
        # Build as many keys as fit, then add an ellipsis token
        parts: list[str] = []
        for token in keys_only:
            next_candidate = join(parts + [token])
            if _visible_length(next_candidate) <= term_width:
                parts.append(token)
            else:
                break
        ellipsis = style(" …", fg=self.theme["dim"]) if parts else ""
        return (
            join(parts)[: term_width - 1] + ellipsis
            if _visible_length(join(parts)) > term_width
            else join(parts) + ellipsis
        )
