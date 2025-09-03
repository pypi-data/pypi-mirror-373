"""Shared table styling utilities for consistent CLI output.

Provides helpers to create tables and panels with Flow's default styles.
"""

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from flow.cli.utils.theme_manager import theme_manager

try:
    from flow.cli.ui.presentation.terminal_adapter import TerminalAdapter as _TA
except Exception:
    _TA = None  # type: ignore


def create_flow_table(
    title: str | None = None,
    show_borders: bool = True,
    padding: int = 1,
    *,
    expand: bool = False,
) -> Table:
    """Create a table with Flow's standard styling.

    Args:
        title: Optional table title
        show_borders: Whether to show table borders
        padding: Column padding (0-2)

    Returns:
        Configured Rich Table instance with Flow styling
    """
    # Simple output mode trims chrome; prefer no borders, tighter padding, no expansion
    simple = False
    try:
        if _TA and hasattr(_TA, "is_simple_output"):
            simple = bool(_TA.is_simple_output())
    except Exception:
        simple = False

    # Use rounded box style unless in simple mode
    effective_borders = False if simple else show_borders
    # Always keep at least 1 space between columns; simple mode still gets a gap
    effective_padding = max(1, (0 if simple else padding))
    effective_expand = False if simple else expand
    effective_title = None if simple else title
    box_style = box.ROUNDED if effective_borders else None

    table = Table(
        title=effective_title,
        box=box_style,
        header_style="bold",
        border_style=(
            theme_manager.get_color("table.border")
            if effective_borders
            else theme_manager.get_color("muted")
        ),
        title_style=(f"bold {theme_manager.get_color('accent')}" if effective_title else None),
        show_lines=False,  # Clean look without horizontal lines
        padding=(0, effective_padding),
        # Preserve at least one space between columns (avoid merged headers like "#Name")
        collapse_padding=False,
        expand=effective_expand,  # Do not expand by default; most tables render better compact
        pad_edge=False,  # Reduce side padding for tighter alignment in panels
    )

    return table


def wrap_table_in_panel(table: Table, title: str, console: Console) -> None:
    """Wrap table in a panel with centered title, matching flow status style.

    Args:
        table: The table to wrap
        title: Panel title
        console: Rich console for output
    """
    accent = theme_manager.get_color("accent")
    border = theme_manager.get_color("table.border")
    panel = Panel(
        table,
        title=f"[bold {accent}]{title}[/bold {accent}]",
        title_align="left",  # Prefer left-aligned titles for consistent CLI rhythm
        border_style=border,
        padding=(1, 2),  # Match wizard panel padding
        expand=False,  # Don't expand panel beyond table content
    )
    console.print(panel)


def add_centered_column(
    table: Table,
    name: str,
    style: str | None = None,
    width: int | None = None,
    min_width: int | None = None,
    max_width: int | None = None,
    ratio: float | None = None,
    overflow: str = "fold",
) -> None:
    """Add a column with centered alignment and consistent header style.

    Args:
        table: Table to add column to
        name: Column name
        style: Optional column style
        width: Optional fixed column width
        min_width: Optional minimum column width
        max_width: Optional maximum column width
        ratio: Optional width ratio for proportional sizing
        overflow: How to handle overflow text (fold, crop, ellipsis)
    """
    table.add_column(
        name,
        style=style or theme_manager.get_color("default"),
        width=width,
        min_width=min_width,
        max_width=max_width,
        ratio=ratio,
        header_style=theme_manager.get_color("table.header"),
        justify="center",
        overflow=overflow,
    )


def add_left_aligned_column(
    table: Table,
    name: str,
    style: str | None = None,
    width: int | None = None,
    min_width: int | None = None,
    max_width: int | None = None,
    ratio: float | None = None,
    overflow: str = "fold",
) -> None:
    """Add a column with left alignment and consistent header style.

    Mirrors add_centered_column API to keep callsites simple.
    """
    table.add_column(
        name,
        style=style or theme_manager.get_color("default"),
        width=width,
        min_width=min_width,
        max_width=max_width,
        ratio=ratio,
        header_style=theme_manager.get_color("table.header"),
        justify="left",
        overflow=overflow,
    )


def add_right_aligned_column(
    table: Table,
    name: str,
    style: str | None = None,
    width: int | None = None,
    min_width: int | None = None,
    max_width: int | None = None,
    ratio: float | None = None,
    overflow: str = "fold",
) -> None:
    """Add a column with right alignment and consistent header style.

    Useful for index and numeric/status columns intended to sit flush right.
    """
    table.add_column(
        name,
        style=style or theme_manager.get_color("default"),
        width=width,
        min_width=min_width,
        max_width=max_width,
        ratio=ratio,
        header_style=theme_manager.get_color("table.header"),
        justify="right",
        overflow=overflow,
    )
