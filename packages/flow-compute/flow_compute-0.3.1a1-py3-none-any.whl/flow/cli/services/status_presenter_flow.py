"""Helpers for presenting task lists via TaskPresenter, with time filtering.

This keeps the status command thin while reusing the existing presenter.
"""

from __future__ import annotations

from datetime import timezone

from flow.sdk.client import Flow  # noqa: F401  # retain symbol for tests that patch it
from flow.sdk.factory import create_client


def present_task_list_with_optional_time_filter(
    console,
    task_presenter,
    *,
    show_all: bool,
    status: str | None,
    limit: int,
    since: str | None,
    until: str | None,
    flow_client=None,
):
    """Present task list using TaskPresenter; optionally apply time-range filter.

    Returns the presenter's summary (or None). Does not raise.
    """
    from flow.cli.ui.presentation.task_presenter import DisplayOptions

    display_options = DisplayOptions(
        show_all=(show_all or since or until),
        status_filter=status,
        limit=limit,
        show_details=True,
    )

    # Ensure presenter has a Flow-like client (tests may patch via contracts)
    try:
        if not getattr(task_presenter, "flow_client", None):
            task_presenter.flow_client = flow_client or create_client(auto_init=True)
    except Exception:
        pass

    tasks = None
    if since or until:
        from flow.cli.utils.task_fetcher import TaskFetcher
        from flow.cli.utils.time_spec import parse_timespec

        fetcher = TaskFetcher(flow_client or create_client(auto_init=True))
        tasks = fetcher.fetch_for_display(show_all=True, status_filter=status, limit=limit)
        since_dt = parse_timespec(since)
        until_dt = parse_timespec(until)
        if since_dt or until_dt:

            def _in_range(t):
                ts = getattr(t, "created_at", None)
                if not ts:
                    return False
                if getattr(ts, "tzinfo", None) is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                if since_dt and ts < since_dt:
                    return False
                if until_dt and ts > until_dt:
                    return False
                return True

            tasks = [t for t in tasks if _in_range(t)]

    try:
        return task_presenter.present_task_list(display_options, tasks=tasks)
    except Exception:
        # Never propagate errors from presentation
        return None


def build_recommendations_from_summary(summary, *, limit: int) -> list[str]:
    """Create context-aware next-step recommendations from a presenter summary."""
    if not summary:
        return []
    recommendations: list[str] = []
    task_count = min(getattr(summary, "total_shown", 0), limit)
    index_help = f"1-{task_count}" if task_count > 1 else "1"

    has_running = getattr(summary, "running_tasks", 0) > 0
    has_pending = getattr(summary, "pending_tasks", 0) > 0
    has_paused = getattr(summary, "paused_tasks", 0) > 0
    has_failed = getattr(summary, "failed_tasks", 0) > 0

    if has_running:
        recommendations.append(
            f"[accent][bold]flow[/bold][/accent] ssh {index_help} [muted]— SSH into task (by index)[/muted]"
        )
        recommendations.append(
            "[accent][bold]flow[/bold][/accent] ssh [task.name]<task-name>[/task.name] [muted]— SSH into task (by name)[/muted]"
        )
        recommendations.append(
            f"[accent][bold]flow[/bold][/accent] logs {index_help} [muted]— View logs (by index)[/muted]"
        )
        recommendations.append(
            "[accent][bold]flow[/bold][/accent] logs [task.name]<task-name>[/task.name] [muted]— View logs (by name)[/muted]"
        )

    if has_pending:
        recommendations.append(
            "[accent][bold]flow[/bold][/accent] status [task.name]<task-name>[/task.name] [muted]— Check pending task details[/muted]"
        )
        if has_pending and not has_running:
            recommendations.append(
                "[accent][bold]flow[/bold][/accent] status --all [muted]— View all available resources[/muted]"
            )

    if has_paused:
        recommendations.append(
            "[accent][bold]flow[/bold][/accent] grab [task.name]<task-name>[/task.name] [muted]— Resume paused task[/muted]"
        )

    if has_failed:
        recommendations.append(
            "[accent][bold]flow[/bold][/accent] logs [task.name]<failed-task-name>[/task.name] [muted]— Debug failed task[/muted]"
        )

    try:
        from flow.cli.ui.presentation.next_steps import build_generic_recommendations

        recs = build_generic_recommendations(
            index_help=index_help, active_tasks=getattr(summary, "active_tasks", 0)
        )
        recommendations = recs + recommendations
    except Exception:
        pass
    return recommendations


def present_single_task(console, task_presenter, task_identifier: str, *, flow_client=None):
    """Present a single task using TaskPresenter, ensuring Flow client exists.

    Returns the presenter's return value; Falsey means the caller should stop.
    """
    try:
        if not getattr(task_presenter, "flow_client", None):
            task_presenter.flow_client = flow_client or create_client(auto_init=True)
    except Exception:
        pass
    try:
        return task_presenter.present_single_task(task_identifier)
    except Exception:
        return False
