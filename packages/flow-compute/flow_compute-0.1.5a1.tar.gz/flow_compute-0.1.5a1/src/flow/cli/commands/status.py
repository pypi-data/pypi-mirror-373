"""Status command - list and monitor GPU compute tasks.

Provides task listings with filtering and display options for monitoring
execution and resource usage.

Examples:
    # Check your active tasks (running/pending)
    $ flow status

    # Monitor a specific task by name or ID
    $ flow status my-training-job

    # Show only running tasks with costs
    $ flow status --state running

Command Usage:
    flow status [TASK_ID_OR_NAME] [OPTIONS]

Status values:
- pending: Task submitted, waiting for resources
- running: Task actively executing on GPU
- preempting: Task running but will be terminated soon by provider
- completed: Task finished successfully
- failed: Task terminated with error
- cancelled: Task cancelled by user

The command will:
- Query tasks from the configured provider
- Apply status and time filters
- Format output in a readable table
- Show task IDs, status, GPU type, and timing
- Display creation and completion timestamps

Output includes:
- Task ID (shortened for readability)
- Current status with color coding
- GPU type allocated
- Creation timestamp
- Duration or completion time

Note:
    By default, shows only active tasks (running or pending). If no active
    tasks exist, shows recent tasks from the last 24 hours. Use --all to
    see the complete task history.
"""

import logging
import os
from datetime import datetime

import click

from flow.cli.commands.base import BaseCommand, console
from flow.cli.ui.presentation.animated_progress import AnimatedEllipsisProgress

# Avoid importing heavy UI modules at import time; import lazily inside the command
from flow.cli.utils.error_handling import cli_error_guard
from flow.errors import AuthenticationError, FlowError

# Back-compat: expose Flow for tests that patch flow.cli.commands.status.Flow
from flow.sdk.client import Flow as Flow
from flow.sdk.factory import create_client


class StatusCommand(BaseCommand):
    """List tasks with optional filtering."""

    def __init__(self):
        """Initialize command with task presenter.

        Avoid creating Flow() at import time to prevent environment-dependent
        side effects during module import (e.g., smoke import or docs build).
        The presenter will lazily create a Flow client on first use.
        """
        super().__init__()
        self.task_presenter = None  # type: ignore[assignment]

    @property
    def name(self) -> str:
        return "status"

    @property
    def help(self) -> str:
        return "List and monitor GPU compute tasks - filter by status, name, or time"

    def get_command(self) -> click.Command:
        from flow.cli.ui.runtime.shell_completion import complete_task_ids as _complete_task_ids

        def _dbg(msg: str) -> None:
            try:
                if os.environ.get("FLOW_STATUS_DEBUG"):
                    logging.getLogger("flow.status.cli").info(msg)
            except Exception:
                pass

        @click.command(name=self.name, help=self.help)
        @click.argument("task_identifier", required=False, shell_complete=_complete_task_ids)
        @click.option(
            "--all", "show_all", is_flag=True, help="Show all tasks (default: active tasks only)"
        )
        # Demo toggle disabled for initial release
        # @click.option("--demo/--no-demo", default=None, help="Override demo mode for this command (mock provider, no real provisioning)")
        @click.option(
            "--state",
            "-s",
            type=click.Choice(
                ["pending", "running", "paused", "preempting", "completed", "failed", "cancelled"]
            ),
            help="Filter by state",
        )
        @click.option("--limit", default=20, help="Maximum number of tasks to show")
        @click.option(
            "--force-refresh",
            is_flag=True,
            help="Bypass local caches and fetch fresh task data from provider",
        )
        @click.option("--json", "output_json", is_flag=True, help="Output JSON for automation")
        @click.option(
            "--since",
            type=str,
            help="Only tasks created since time (e.g., '2h', '2025-08-07T10:00:00Z')",
        )
        @click.option(
            "--until", type=str, help="Only tasks created until time (same formats as --since)"
        )
        @click.option(
            "--verbose",
            "-v",
            is_flag=True,
            help="Show detailed status information and filtering examples",
        )
        @click.option("--watch", "-w", is_flag=True, help="Live update the status display")
        @click.option("--compact", is_flag=True, help="Compact allocation view")
        @click.option(
            "--refresh-rate",
            default=3.0,
            type=float,
            help="Refresh rate in seconds for watch mode (default: 3)",
        )
        @click.option(
            "--project",
            type=str,
            required=False,
            help="Filter to a specific project/workspace (provider dependent)",
        )
        @click.option(
            "--no-origin-group", is_flag=True, help="Disable Flow/Other grouping in main view"
        )
        @click.option(
            "--show-reservations",
            is_flag=True,
            help="Show an additional Reservations panel (upcoming and active)",
            hidden=True,
        )
        @click.option(
            "--interactive/--no-interactive",
            default=None,
            help="When ambiguous identifier matches multiple tasks: open selector (default: auto if TTY)",
        )
        # @demo_aware_command(flag_param="demo")
        @cli_error_guard(self)
        def status(
            task_identifier: str | None,
            show_all: bool,
            state: str | None,
            limit: int,
            output_json: bool,
            since: str | None,
            until: str | None,
            verbose: bool,
            watch: bool,
            compact: bool,
            refresh_rate: float,
            project: str | None,
            no_origin_group: bool,
            show_reservations: bool,
            # demo: bool | None,
            force_refresh: bool,
            interactive: bool | None,
        ):
            """List active tasks or show details for a specific task.

            \b
            Examples:
                flow status                  # Active tasks (running/pending)
                flow status my-training      # Find task by name
                flow status --state running  # Only running tasks
                flow status --all            # Show all tasks
                flow status --watch          # Live updating display
                flow status -w --refresh-rate 1  # Update every second

            Use 'flow status --verbose' for advanced filtering and monitoring patterns.
            """
            # Ensure --project affects any Flow() created below by setting env early
            from flow.cli.services.status_setup import apply_project_env

            apply_project_env(project)
            _dbg(
                f"status: args project={project} show_all={show_all} state={state} limit={limit} "
                f"since={since} until={until} json={output_json} watch={watch} compact={compact}"
            )
            _dbg(
                "status: env FLOW_PROVIDER="
                + str(os.environ.get("FLOW_PROVIDER"))
                + " MITHRIL_PROJECT="
                + str(os.environ.get("MITHRIL_PROJECT"))
                + " MITHRIL_PROJECT_ID="
                + str(os.environ.get("MITHRIL_PROJECT_ID"))
            )

            if force_refresh:
                # Clear prefetch caches before proceeding
                from flow.cli.services.status_setup import apply_force_refresh

                _dbg("status: force-refresh requested → clearing caches")
                apply_force_refresh()

            # Create a single Flow client for this command execution and reuse it
            # across all downstream calls to avoid repeated provider initialization.
            client = None

            # Lazily construct presenter now that imports are resolved
            if self.task_presenter is None:
                try:
                    from flow.cli.ui.facade.views import TaskPresenter as _TaskPresenter

                    self.task_presenter = _TaskPresenter(console)
                except Exception:
                    # Leave presenter as None; we will fall back to a simple renderer below
                    self.task_presenter = None  # type: ignore[assignment]

            if verbose and not task_identifier:
                try:
                    from flow.cli.ui.facade.views import render_verbose_help as _render_verbose_help

                    _render_verbose_help(console)
                    return
                except Exception:
                    console.print(
                        "[dim]Verbose help unavailable (UI components missing). Proceeding with basic status view.[/dim]"
                    )

            # Demo mode already applied by decorator

            # Specific task: delegate to actions with interactive fallback on ambiguity
            if (not output_json) and task_identifier and (not watch):
                _dbg("status: path=single-task (no watch/json)")
                from flow.cli.services.status_actions import present_single_or_interactive

                if client is None:
                    client = create_client(auto_init=True)
                handled = present_single_or_interactive(
                    console,
                    task_identifier,
                    state=state,
                    interactive=interactive,
                    flow_client=client,
                )
                if handled:
                    return

            # Default snapshot view: fetch under AEP, render after closing spinner
            if (not output_json) and (not task_identifier) and (not watch):
                _dbg("status: path=snapshot (no id/json/watch)")
                try:
                    if client is None:
                        client = create_client(auto_init=True)

                    # Build presenter and options; fetch tasks while AEP is active
                    from flow.cli.ui.presentation.status_presenter import (
                        StatusDisplayOptions as _SDO,
                    )
                    from flow.cli.ui.presentation.status_presenter import (
                        StatusPresenter as _Presenter,
                    )

                    options = _SDO(
                        show_all=(show_all or since or until),
                        limit=limit,
                        group_by_origin=(not no_origin_group),
                        status_filter=(state or None),
                    )

                    presenter = _Presenter(console, flow_client=client)
                    with AnimatedEllipsisProgress(
                        console, "Fetching tasks", start_immediately=True
                    ):
                        # Use the presenter's fetcher to avoid printing under AEP
                        tasks = presenter.fetcher.fetch_for_display(
                            show_all=options.show_all,
                            status_filter=options.status_filter,
                            limit=options.limit,
                        )

                    # Now render outside the AEP to avoid Live/print interleaving
                    presenter.present(options, tasks=tasks)
                except Exception:
                    _dbg("status: snapshot UI unavailable → fallback to simple list")
                    # Minimal fallback when UI components are unavailable
                    self._render_simple_list(
                        show_all=(show_all or since or until),
                        state=state,
                        limit=limit,
                        since=since,
                        until=until,
                        flow_client=client,
                    )
                return

            _dbg("status: path=execute (json/watch or simple modes)")
            self._execute(
                task_identifier,
                show_all,
                state,
                limit,
                output_json,
                since,
                until,
                watch,
                compact,
                refresh_rate,
                flow_client=client,
            )

        return status

    def _derive_priority(self, task) -> str | None:
        """Best-effort derivation of priority tier for a task.

        Prefers explicit config priority when attached; otherwise infers from
        provider metadata (e.g., limit price vs per‑GPU pricing) when feasible.
        Falls back to 'med' when nothing is available, matching SDK defaults.
        """
        try:
            # 1) From attached config if present
            cfg = getattr(task, "config", None)
            prio = getattr(cfg, "priority", None) if cfg is not None else None
            if prio:
                return str(prio)

            # 2) Infer from provider metadata and instance_type (optional)
            meta = getattr(task, "provider_metadata", {}) or {}
            limit_price_str = meta.get("limit_price")
            instance_type = getattr(task, "instance_type", None)
            if isinstance(limit_price_str, str) and instance_type:
                # Normalize: "$12.34" -> 12.34
                try:
                    from flow.resources import get_gpu_pricing as get_pricing_data

                    def _parse_price(s: str) -> float:
                        try:
                            return float(s.strip("$"))
                        except Exception:
                            return 0.0

                    def _extract_gpu_info(inst: str) -> tuple[str, int]:
                        try:
                            s = (inst or "").lower()
                            if "x" in s:
                                count, rest = s.split("x", 1)
                                return rest, max(1, int(count))
                            return s, 1
                        except Exception:
                            return s, 1

                    price_val = _parse_price(limit_price_str)
                    gpu_type, gpu_count = _extract_gpu_info(instance_type)
                    pricing = get_pricing_data().get("gpu_pricing", {})
                    table = pricing.get(gpu_type, pricing.get("default", {}))
                    med_per_gpu = table.get("med", 4.0)
                    med_total = med_per_gpu * max(1, gpu_count)
                    if price_val <= med_total * 0.75:
                        return "low"
                    if price_val >= med_total * 1.5:
                        return "high"
                    return "med"
                except Exception:
                    pass

            # 3) Default
            return "med"
        except Exception:
            return "med"

    def _parse_timespec(self, value: str | None) -> datetime | None:
        from flow.cli.utils.time_spec import parse_timespec

        return parse_timespec(value)

    def _execute(
        self,
        task_identifier: str | None,
        show_all: bool,
        status: str | None,
        limit: int,
        output_json: bool,
        since: str | None,
        until: str | None,
        watch: bool = False,
        compact: bool = False,
        refresh_rate: float = 3.0,
        flow_client=None,
    ) -> None:
        """Execute the status command."""
        # Cannot use watch mode with JSON output or specific task identifier
        if watch and (output_json or task_identifier):
            if output_json:
                console.print("[error]Error:[/error] Cannot use --watch with --json")
            else:
                console.print(
                    "[error]Error:[/error] Cannot use --watch when viewing a specific task"
                )
            return

        # JSON output mode - no animation
        if output_json:
            from flow.cli.services.status_queries import StatusQuery, parse_timespec
            from flow.cli.utils.json_output import error_json, print_json, task_to_json

            client = flow_client or create_client(auto_init=True)
            if task_identifier:
                try:
                    task = client.get_task(task_identifier)
                    print_json(task_to_json(task))
                except FlowError as e:
                    print_json(error_json(str(e)))
                return
            else:
                query = StatusQuery(
                    task_identifier=None,
                    show_all=show_all,
                    state=status,
                    limit=limit,
                    since=parse_timespec(since),
                    until=parse_timespec(until),
                )
                try:
                    from flow.sdk.models import TaskStatus as _TS

                    status_enum = _TS(query.state) if query.state else None
                except (ValueError, TypeError):
                    status_enum = None
                tasks = client.list_tasks(status=status_enum, limit=query.limit)
                if query.since or query.until:
                    from flow.cli.services.status_queries import filter_by_time

                    tasks = filter_by_time(tasks, query.since, query.until)
                print_json([task_to_json(t) for t in tasks])
                return

        # Check if we're in watch mode
        if watch:
            # If compact is requested, use alloc-like live view; else keep existing live table
            try:
                if compact:
                    from flow.cli.ui.facade.views import run_live_compact as _run_live_compact

                    _run_live_compact(
                        console,
                        show_all=show_all,
                        status_filter=status,
                        limit=limit,
                        refresh_rate=refresh_rate,
                        flow_client=flow_client,
                    )
                else:
                    from flow.cli.ui.facade.views import run_live_table as _run_live_table

                    _run_live_table(
                        console,
                        show_all=show_all,
                        status_filter=status,
                        limit=limit,
                        refresh_rate=refresh_rate,
                        flow_client=flow_client,
                    )
            except Exception:
                console.print(
                    "[error]Live view unavailable (UI components missing). Showing static list instead.[/error]"
                )
                self._render_simple_list(
                    show_all=show_all,
                    state=status,
                    limit=limit,
                    since=since,
                    until=until,
                    flow_client=flow_client,
                )
            return

        # Start animation immediately for instant feedback
        progress = AnimatedEllipsisProgress(
            console,
            "Fetching tasks" if not task_identifier else "Looking up task",
            start_immediately=True,
        )

        try:
            # Handle specific task request
            if task_identifier:
                with progress:
                    from flow.cli.services.status_presenter_flow import present_single_task

                    if not present_single_task(
                        console, self.task_presenter, task_identifier, flow_client=flow_client
                    ):
                        return
            else:
                # Present task list with optional time filtering via helper
                with progress:
                    try:
                        from flow.cli.ui.facade.views import present_snapshot as _present_snapshot

                        _present_snapshot(
                            console,
                            show_all=show_all,
                            state=status,
                            limit=limit,
                            group_by_origin=True,
                            flow_client=(flow_client or create_client(auto_init=True)),
                        )
                        summary = None
                    except Exception:
                        self._render_simple_list(
                            show_all=show_all,
                            state=status,
                            limit=limit,
                            since=None,
                            until=None,
                            flow_client=flow_client,
                        )
                        summary = None

                # Show context-aware recommendations based on task states
                if summary:
                    from flow.cli.services.status_presenter_flow import (
                        build_recommendations_from_summary,
                    )

                    recommendations = build_recommendations_from_summary(summary, limit=limit)
                    if recommendations:
                        self.show_next_actions(recommendations[:3])

        except AuthenticationError:
            self.handle_auth_error()
        except click.exceptions.Exit:
            # Ensure we don't print error messages twice
            raise
        except Exception as e:
            self.handle_error(e)

    # Live mode helpers now delegated via presentation.status_view

    def _render_simple_list(
        self,
        *,
        show_all: bool,
        state: str | None,
        limit: int,
        since: str | None,
        until: str | None,
        flow_client=None,
    ) -> None:
        """Render a minimal task list without rich UI dependencies."""
        try:
            from flow.cli.services.status_queries import StatusQuery, filter_by_time, parse_timespec
            from flow.sdk.models import TaskStatus as _TS
        except Exception:
            console.print(
                "[error]Unable to load status helpers. Please reinstall the package or run with --json.[/error]"
            )
            return

        client = flow_client or create_client(auto_init=True)
        try:
            status_enum = _TS(state) if state else None
        except (ValueError, TypeError):
            status_enum = None

        tasks = client.list_tasks(status=status_enum, limit=limit)
        qs = StatusQuery(
            task_identifier=None,
            show_all=show_all,
            state=state,
            limit=limit,
            since=parse_timespec(since),
            until=parse_timespec(until),
        )
        if qs.since or qs.until:
            tasks = filter_by_time(tasks, qs.since, qs.until)

        if not tasks:
            console.print("No tasks found. Run 'flow run' to submit a job.")
            return

        console.print("Tasks (minimal):")
        for t in tasks:
            tid = getattr(t, "task_id", "")
            name = getattr(t, "name", "")
            status_val = getattr(getattr(t, "status", None), "value", "")
            itype = getattr(t, "instance_type", "")
            created = getattr(t, "created_at", None)
            created_str = getattr(created, "isoformat", lambda: str(created))()
            console.print(f"- {name} [{status_val}] id={tid} gpu={itype} created={created_str}")


# Export command instance
command = StatusCommand()
