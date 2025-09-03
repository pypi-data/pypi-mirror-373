"""Tiny styling helpers for consistent, theme-aware markup.

Use Rich style names defined in the theme (e.g., 'accent', 'link', 'shortcut_key').
Keep this module lightweight to avoid over-abstracting presentation.
"""

from __future__ import annotations

import re

from rich.markup import escape


def apply_style(style: str, text: str) -> str:
    """Wrap text in a Rich style tag.

    Assumes 'style' is a theme-defined style name (e.g., 'accent', 'link').
    """
    return f"[{style}]{escape(text)}[/]"


def accent(text: str) -> str:
    return apply_style("accent", text)


def link(text: str) -> str:
    return apply_style("link", text)


def key(text: str) -> str:
    return apply_style("shortcut_key", text)


def cmd(text: str) -> str:
    """Preferred wrapper for CLI commands in docs/output."""
    return accent(text)


_INLINE_CODE_RE = re.compile(r"(`+)([^`]+?)\1")


def style_inline_code(text: str) -> str:
    """Convert Markdown-style `inline code` to themed accent markup.

    Keeps everything else untouched. Useful when building user-facing strings
    where only backticked segments should be highlighted.
    """

    def _replace(match: re.Match) -> str:
        content = match.group(2)
        return cmd(content)

    return _INLINE_CODE_RE.sub(_replace, text)
