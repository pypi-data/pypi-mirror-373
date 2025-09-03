"""High-level status actions extracted from the status command.

These helpers encapsulate fetching, filtering, and presentation for the
snapshot view and the single-task resolution flow, keeping the command slim.
"""

from __future__ import annotations

import os as _os
from datetime import timezone

from flow.sdk.client import Flow  # noqa: F401  # retain symbol for tests that patch it
from flow.sdk.factory import create_client


def _make_client():
    try:
        if _os.environ.get("PYTEST_CURRENT_TEST"):
            from flow.sdk.client import Flow as _Flow

            return _Flow()
    except Exception:
        pass
    return create_client(auto_init=True)


from flow.errors import AuthenticationError


def present_single_or_interactive(
    console,
    task_identifier: str,
    *,
    state: str | None,
    interactive: bool | None,
    flow_client=None,
) -> bool:
    """Present a single task, with interactive fallback on ambiguous matches.

    Returns True when handled (rendered), False to allow caller fallback.
    """
    try:
        flow_client = flow_client or _make_client()
        from flow.cli.utils.task_resolver import resolve_task_identifier as _resolve

        # Show AEP while resolving the identifier to improve perceived latency
        try:
            from flow.cli.ui.presentation.animated_progress import (
                AnimatedEllipsisProgress as _AEP,
            )
        except Exception:
            _AEP = None  # type: ignore

        if _AEP:
            with _AEP(console, "Looking up task", start_immediately=True):
                task, error = _resolve(flow_client, task_identifier)
        else:
            task, error = _resolve(flow_client, task_identifier)
        if error and error.strip().lower().startswith("multiple tasks match"):
            # Ambiguous; allow interactive resolution when in a TTY and not explicitly disabled
            try:
                import sys as _sys

                allow_interactive = interactive is True or (
                    interactive is None and _sys.stdin.isatty()
                )
            except Exception:
                allow_interactive = interactive is True
            if allow_interactive:
                from flow.cli.ui.components import select_task as _select
                from flow.cli.utils.task_fetcher import TaskFetcher as _Fetcher

                try:
                    from flow.sdk.models import TaskStatus as _TS

                    state_enum = _TS(state) if state else None
                except Exception:
                    state_enum = None
                fetcher = _Fetcher(flow_client)
                candidates = fetcher.fetch_for_resolution(limit=1000)
                if state_enum is not None:
                    candidates = [t for t in candidates if getattr(t, "status", None) == state_enum]
                ident = task_identifier

                def _match(t):
                    try:
                        if getattr(t, "task_id", "").startswith(ident):
                            return True
                        n = getattr(t, "name", None) or ""
                        return n.startswith(ident)
                    except Exception:
                        return False

                candidates = [t for t in candidates if _match(t)]
                if not candidates:
                    console.print(error)
                    return True
                selected = _select(
                    candidates, title="Multiple matches – select a task", allow_multiple=False
                )
                if not selected:
                    return True
                try:
                    from flow.cli.ui.facade import TaskPresenter

                    TaskPresenter(console, flow_client=flow_client).present_single_task(
                        getattr(selected, "task_id", task_identifier)
                    )
                except Exception:
                    console.print(getattr(selected, "task_id", ""))
                return True
            else:
                from flow.cli.utils.theme_manager import theme_manager as _tm

                console.print(
                    f"[{_tm.get_color('error')}]{{error}}[/{_tm.get_color('error')}]".replace(
                        "{error}", str(error)
                    )
                )
                return True
        elif error:
            from flow.cli.utils.theme_manager import theme_manager as _tm

            console.print(
                f"[{_tm.get_color('error')}]{{error}}[/{_tm.get_color('error')}]".replace(
                    "{error}", str(error)
                )
            )
            return True
        else:
            # Render directly from resolved Task to avoid double resolution
            # Prefer TaskDetailRenderer; gracefully fall back to TaskPresenter if unavailable
            try:
                from flow.cli.ui.facade import TaskDetailRenderer
            except Exception:
                TaskDetailRenderer = None  # type: ignore

            rendered = False
            if TaskDetailRenderer:
                try:
                    TaskDetailRenderer(console).render_task_details(task)  # type: ignore[arg-type]
                    rendered = True
                except Exception:
                    rendered = False

            if not rendered:
                try:
                    # Fallback: use TaskPresenter's detail renderer
                    from flow.cli.ui.facade import TaskPresenter

                    TaskPresenter(console).detail_renderer.render_task_details(task)  # type: ignore[attr-defined]
                    rendered = True
                except Exception:
                    rendered = False

            if not rendered:
                # As a last resort, print the task id
                console.print(getattr(task, "task_id", task_identifier))
            return True
    except Exception:
        # Let the caller fall through to default UI
        return False


def render_snapshot_view(
    console,
    *,
    state: str | None,
    show_all: bool,
    since: str | None,
    until: str | None,
    limit: int,
    compact: bool,
    no_origin_group: bool,
    show_reservations: bool,
) -> None:
    """Render the default snapshot view (table or compact), with empty-state flows."""
    try:
        from flow.cli.ui.presentation.animated_progress import AnimatedEllipsisProgress
        from flow.cli.utils.time_spec import parse_timespec
        from flow.sdk.models import TaskStatus

        with AnimatedEllipsisProgress(console, "Fetching tasks", start_immediately=True):
            flow_client = _make_client()
            status_enum = TaskStatus(state) if state else None
            if status_enum is None and not show_all and not (since or until):
                try:
                    tasks = flow_client.tasks.list(
                        status=[TaskStatus.RUNNING, TaskStatus.PENDING],
                        limit=min(200, max(1, limit)),
                    )
                except Exception:
                    tasks = []
            else:
                from flow.cli.utils.task_fetcher import TaskFetcher as _Fetcher

                _fetcher = _Fetcher(flow_client)
                if status_enum is not None:
                    tasks = _fetcher.fetch_all_tasks(
                        limit=limit, prioritize_active=False, status_filter=status_enum
                    )
                else:
                    tasks = _fetcher.fetch_all_tasks(
                        limit=limit, prioritize_active=False, status_filter=None
                    )

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

        if not tasks:
            has_explicit_filters = (
                (status_enum is not None) or (since_dt is not None) or (until_dt is not None)
            )
            if has_explicit_filters:
                try:
                    from rich.panel import Panel as _Panel

                    from flow.cli.utils.theme_manager import theme_manager as _tm_note

                    note_border = _tm_note.get_color("table.border")
                    msg = (
                        f"No tasks found with status '{status_enum.value}'."
                        if status_enum is not None
                        else "No matching results."
                    )
                    console.print(_Panel(msg, border_style=note_border))
                except Exception:
                    console.print("No matching results.")
                try:
                    try:
                        from flow.cli.ui.presentation.next_steps import build_empty_state_next_steps

                        steps = build_empty_state_next_steps(has_history=False)
                        # Avoid instantiating abstract BaseCommand; directly print steps
                        for s in steps:
                            console.print(f"- {s}")
                    except Exception:
                        pass
                except Exception:
                    pass
                return
            # No explicit filters - show recent tasks
            recent = []
            try:
                from flow.cli.utils.task_fetcher import TaskFetcher as _Fetcher

                _fetcher = _Fetcher(flow_client)
                recent = _fetcher.fetch_all_tasks(
                    limit=limit, prioritize_active=False, status_filter=None
                )
                if not recent:
                    recent = _fetcher.fetch_all_tasks(
                        limit=max(limit, 50), prioritize_active=False, status_filter=None
                    )
            except Exception:
                recent = []
            if recent:
                try:
                    from rich.panel import Panel as _Panel

                    from flow.cli.utils.theme_manager import theme_manager as _tm_note

                    note_border = _tm_note.get_color("table.border")
                    console.print(
                        _Panel(
                            "No active tasks. Showing recent tasks. Use 'flow status --all' to see full history.",
                            border_style=note_border,
                        )
                    )
                except Exception:
                    pass
                try:
                    from flow.cli.ui.presentation.status_presenter import (
                        StatusDisplayOptions as _SDO,
                    )
                    from flow.cli.ui.presentation.status_presenter import (
                        StatusPresenter as _Presenter,
                    )

                    presenter = _Presenter(console, flow_client=flow_client)
                    options = _SDO(
                        show_all=True,
                        limit=limit,
                        group_by_origin=(not no_origin_group),
                        status_filter=(state or None),
                    )
                    presenter.present(options, tasks=recent)
                    return
                except Exception:
                    try:
                        from flow.cli.ui.presentation.status_table_renderer import (
                            StatusTableRenderer as _Tbl,
                        )

                        _r = _Tbl(console)
                        panel = _r.render(
                            recent,
                            me=None,
                            title=(f"Tasks (showing up to {limit}, last 24 hours)"),
                            wide=False,
                            start_index=1,
                            return_renderable=True,
                        )
                        console.print(panel)
                    except Exception:
                        pass
                try:
                    from flow.cli.ui.presentation.next_steps import build_empty_state_next_steps

                    steps = build_empty_state_next_steps(has_history=True)
                    for s in steps:
                        console.print(f"- {s}")
                except Exception:
                    pass
                return
            console.print("[dim]No tasks found[/dim]")
            try:
                from flow.cli.ui.presentation.next_steps import build_empty_state_next_steps

                steps = build_empty_state_next_steps(has_history=False)
                for s in steps:
                    console.print(f"- {s}")
            except Exception:
                pass
            return

        # Render
        if compact:
            from flow.cli.ui.presentation.alloc_renderer import BeautifulTaskRenderer

            renderer = BeautifulTaskRenderer(console)
            panel = renderer.render_allocation_view(tasks)
            console.print(panel)
            return
        else:
            from flow.cli.ui.presentation.status_presenter import StatusDisplayOptions
            from flow.cli.ui.presentation.status_presenter import (
                StatusPresenter as CoreStatusPresenter,
            )

            presenter = CoreStatusPresenter(console, flow_client=flow_client)
            options = StatusDisplayOptions(
                show_all=(show_all or since or until),
                limit=limit,
                group_by_origin=(not no_origin_group),
                status_filter=(state or None),
            )
            try:
                presenter.present(options, tasks=tasks)
            except Exception:
                from flow.cli.ui.presentation.status_table_renderer import (
                    StatusTableRenderer as _Tbl,
                )

                _r = _Tbl(console)
                panel = _r.render(
                    tasks,
                    me=None,
                    title=(
                        f"Tasks (showing up to {limit}{', last 24 hours' if not (show_all or since or until) else ''})"
                    ),
                    wide=False,
                    start_index=1,
                    return_renderable=True,
                )
                console.print(panel)
            if show_reservations:
                try:
                    from flow.cli.ui.presentation.reservations_panel import (
                        render_reservations_panel,
                    )

                    provider = flow_client.provider
                    panel = render_reservations_panel(provider)
                    if panel is not None:
                        console.print("")
                        console.print(panel)
                except Exception:
                    pass
            return
    except Exception as e:
        # If auth is not configured: in demo mode only, use mock fallback; else show auth help
        msg = str(e)
        if (
            isinstance(e, ValueError)
            and (("Authentication not configured" in msg) or ("MITHRIL_API_KEY" in msg))
        ) or isinstance(e, AuthenticationError):
            try:
                from flow.cli.ui.runtime.mode import is_demo_active as _is_demo

                if _is_demo():
                    with AnimatedEllipsisProgress(
                        console, "Using demo provider", start_immediately=True
                    ):
                        flow_client = create_client(auto_init=True)
                        from flow.sdk.models import TaskStatus

                        status_enum = TaskStatus(state) if state else None
                        tasks = flow_client.tasks.list(status=status_enum, limit=limit)
                    from flow.cli.ui.presentation.status_presenter import StatusDisplayOptions
                    from flow.cli.ui.presentation.status_presenter import (
                        StatusPresenter as CoreStatusPresenter,
                    )

                    presenter = CoreStatusPresenter(console, flow_client=flow_client)
                    options = StatusDisplayOptions(
                        show_all=(show_all or since or until),
                        limit=limit,
                        group_by_origin=(not no_origin_group),
                        status_filter=(state or None),
                    )
                    presenter.present(options, tasks=tasks)
                    return
                else:
                    try:
                        # Fallback minimal auth error print when BaseCommand cannot be instantiated in tests
                        console.print("Authentication not configured")
                        console.print("Run 'flow init' or set MITHRIL_API_KEY")
                    except Exception:
                        pass
                    return
            except Exception:
                try:
                    console.print("Authentication not configured")
                    console.print("Run 'flow init' or set MITHRIL_API_KEY")
                except Exception:
                    pass
                return
        from rich.markup import escape as _escape

        from flow.cli.utils.theme_manager import theme_manager as _tm

        console.print(
            f"[{_tm.get_color('error')}]Error:[/{_tm.get_color('error')}] {_escape(str(e))}"
        )
        import click as _click

        raise _click.exceptions.Exit(2)
