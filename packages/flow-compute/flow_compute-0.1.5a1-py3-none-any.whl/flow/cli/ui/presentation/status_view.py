"""Status command presentation wrappers.

Thin wrappers around existing presenter and live helpers so the command
module remains a small orchestrator.
"""

from __future__ import annotations

from rich.console import Console

from flow.sdk.contracts import IClient
from flow.sdk.factory import create_client


def present_snapshot(
    console: Console,
    *,
    show_all: bool,
    state: str | None,
    limit: int,
    group_by_origin: bool = True,
    flow_client: object | None = None,
) -> None:
    """Render the snapshot table view for tasks.

    Uses the existing StatusPresenter and display options.
    """
    # New presenter lives under application layer post-refactor
    from flow.cli.ui.presentation.status_presenter import (
        StatusDisplayOptions as _SDO,
    )
    from flow.cli.ui.presentation.status_presenter import (
        StatusPresenter as _Presenter,
    )

    client = flow_client or create_client(auto_init=True)
    presenter = _Presenter(console, flow_client=client)  # type: ignore[call-arg]
    options = _SDO(
        show_all=show_all,
        limit=limit,
        group_by_origin=group_by_origin,
        status_filter=(state or None),
    )
    presenter.present(options)


def present_single_task(console: Console, task_identifier: str) -> bool:
    """Present a single task using the shared presenter flow.

    Returns True if handled, False to indicate fallback.
    """
    from flow.cli.services.status_presenter_flow import present_single_task as _present_single

    return _present_single(console, None, task_identifier)


def run_live_table(
    console: Console,
    *,
    show_all: bool,
    status_filter: str | None,
    limit: int,
    refresh_rate: float,
    flow_client: IClient | None = None,
) -> None:
    from flow.cli.ui.presentation.status_live import safe_run_live_table

    safe_run_live_table(
        console,
        flow_client or create_client(auto_init=True),
        show_all=show_all,
        status_filter=status_filter,
        limit=limit,
        refresh_rate=refresh_rate,
    )


def run_live_compact(
    console: Console,
    *,
    show_all: bool,
    status_filter: str | None,
    limit: int,
    refresh_rate: float,
    flow_client: IClient | None = None,
) -> None:
    from flow.cli.ui.presentation.status_live import safe_run_live_compact

    safe_run_live_compact(
        console,
        flow_client or create_client(auto_init=True),
        show_all=show_all,
        status_filter=status_filter,
        limit=limit,
        refresh_rate=refresh_rate,
    )
