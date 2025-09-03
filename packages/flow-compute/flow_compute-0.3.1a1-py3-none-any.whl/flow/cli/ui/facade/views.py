"""View facade re-exports.

Prefer components-based views, fallback to presentation implementations.
"""

from __future__ import annotations

from flow.cli.utils.lazy_imports import import_attr

TerminalAdapter = import_attr(
    "flow.cli.ui.presentation.terminal_adapter",
    "TerminalAdapter",
    import_attr("flow.cli.ui.components.views", "TerminalAdapter"),
)

TaskPresenter = import_attr(
    "flow.cli.ui.presentation.task_presenter",
    "TaskPresenter",
    import_attr("flow.cli.ui.components.views", "TaskPresenter"),
)

TaskDetailRenderer = import_attr(
    "flow.cli.ui.presentation.task_renderer",
    "TaskDetailRenderer",
    None,
)

HealthRenderer = import_attr(
    "flow.cli.ui.presentation.health_renderer",
    "HealthRenderer",
    import_attr("flow.cli.ui.components.views", "HealthRenderer"),
)

create_flow_table = import_attr(
    "flow.cli.ui.presentation.table_styles",
    "create_flow_table",
    import_attr("flow.cli.ui.components.views", "create_flow_table"),
)

# Status view helpers
present_snapshot = import_attr(
    "flow.cli.ui.presentation.status_view",
    "present_snapshot",
    import_attr("flow.cli.ui.components.views", "present_snapshot"),
)
run_live_compact = import_attr(
    "flow.cli.ui.presentation.status_view",
    "run_live_compact",
    import_attr("flow.cli.ui.components.views", "run_live_compact"),
)
run_live_table = import_attr(
    "flow.cli.ui.presentation.status_view",
    "run_live_table",
    import_attr("flow.cli.ui.components.views", "run_live_table"),
)
render_verbose_help = import_attr(
    "flow.cli.ui.presentation.status_help",
    "render_verbose_help",
    import_attr("flow.cli.ui.components.views", "render_verbose_help"),
)

__all__ = [
    "TerminalAdapter",
    "TaskPresenter",
    "TaskDetailRenderer",
    "HealthRenderer",
    "create_flow_table",
    "present_snapshot",
    "run_live_compact",
    "run_live_table",
    "render_verbose_help",
]
