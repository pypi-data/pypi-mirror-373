"""Unified view adapters for CLI UI imports.

This module re-exports commonly used presentation-layer utilities so callsites
can import from a single stable path:

    from flow.cli.ui.components.views import TerminalAdapter, TaskPresenter, ...
"""

from __future__ import annotations

# Health renderer (GPUd checks and fleet health)
from flow.cli.ui.presentation.health_renderer import HealthRenderer

# Verbose help renderer for status command
from flow.cli.ui.presentation.status_help import render_verbose_help

# Status command presentation wrappers and live helpers
from flow.cli.ui.presentation.status_view import (
    present_snapshot,
    run_live_compact,
    run_live_table,
)

# Shared table/panel helpers
from flow.cli.ui.presentation.table_styles import (
    create_flow_table,
    wrap_table_in_panel,
)

# High-level presenters (moved during refactor)
from flow.cli.ui.presentation.task_presenter import (
    DisplayOptions,
    TaskPresenter,
)

# Terminal responsiveness helpers
from flow.cli.ui.presentation.terminal_adapter import (
    TerminalAdapter,
    TerminalBreakpoints,
)

__all__ = [
    # Terminal helpers
    "TerminalAdapter",
    "TerminalBreakpoints",
    # Table/panel helpers
    "create_flow_table",
    "wrap_table_in_panel",
    # Presenters
    "DisplayOptions",
    "TaskPresenter",
    # Status view helpers
    "present_snapshot",
    "run_live_table",
    "run_live_compact",
    "render_verbose_help",
    # Health renderer
    "HealthRenderer",
]
