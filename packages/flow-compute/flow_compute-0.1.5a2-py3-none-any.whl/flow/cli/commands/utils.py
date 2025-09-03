"""Shared utilities for CLI commands.

This module centralizes small helpers used across multiple CLI commands.
"""

import os
import sys
import time
from typing import Any

from flow.cli.ui.facade import TerminalAdapter
from flow.cli.ui.presentation.table_styles import create_flow_table, wrap_table_in_panel
from flow.cli.utils.theme_manager import theme_manager
from flow.domain.pricing import calculator as pricing_core
from flow.sdk.client import Flow

console = theme_manager.create_console()


def env_items_to_dict(
    items: tuple[tuple[str, str], ...] | list[tuple[str, str]] | None,
) -> dict[str, str]:
    """Convert repeated EnvItem tuples into a dictionary.

    Example: [("FOO", "bar"), ("A", "B")] -> {"FOO": "bar", "A": "B"}
    """
    env: dict[str, str] = {}
    for key, value in items or ():  # type: ignore[assignment]
        env[str(key)] = str(value)
    return env


def display_config(
    config: dict[str, Any], show_pricing: bool = False, compact: bool = False
) -> None:
    """Display task configuration in a responsive table."""
    layout = TerminalAdapter.get_responsive_layout()

    table = create_flow_table(
        title=None, show_borders=layout["show_borders"], padding=1, expand=False
    )
    table.show_header = False
    table.add_column("Setting", style=theme_manager.get_color("accent"), no_wrap=True)
    table.add_column("Value", style=theme_manager.get_color("default"))

    # Name
    if "name" in config:
        table.add_row("Name", f"[bold]{config.get('name')}[/bold]")

    # Command (compact if very long)
    command = config.get("command", "N/A")
    if isinstance(command, list):
        command = " ".join(command)
    max_cmd_len = 80 if layout["density"].value != "compact" else 50
    if isinstance(command, str) and len(command) > max_cmd_len:
        from flow.cli.ui.facade import TerminalAdapter as TA

        command = TA.intelligent_truncate(command, max_cmd_len, "middle")
    table.add_row("Command", f"[dim]{command}[/dim]")

    # Image
    if not compact:
        image = config.get("image")
        if image:
            table.add_row("Image", image)

    # Instance type and count
    instance_type = config.get("instance_type", "N/A")
    num_instances = int(config.get("num_instances", 1) or 1)
    if num_instances > 1:
        table.add_row("Instances", f"{num_instances} × {instance_type}")
    else:
        table.add_row("Instance Type", instance_type)

    # Region if present
    if not compact:
        region = config.get("region")
        if region:
            table.add_row("Region", region)

    # Priority (always visible)
    priority = (config.get("priority") or "med").lower()
    table.add_row("Priority", priority.capitalize())

    # Pricing (hidden by default; shown when --pricing flag is set)
    if show_pricing:
        if config.get("max_price_per_hour"):
            per_instance_price = float(config["max_price_per_hour"]) or 0.0
            table.add_row("Max Price/Instance", f"${per_instance_price:.2f}/hr")
            if num_instances > 1:
                total_price = per_instance_price * num_instances
                table.add_row("Max Price/Job", f"${total_price:.2f}/hr ({num_instances} instances)")
        else:
            # Priority-based limit pricing summary
            def _extract_gpu_info(inst: str) -> tuple[str, int]:
                s = (inst or "").lower()
                gpu_type = "default"
                for t in ("h100", "a100", "a10", "t4"):
                    if t in s:
                        gpu_type = t
                        break
                count = 1
                try:
                    if "x" in s:
                        parts = s.split("x", 1)
                        if parts[0].isdigit():
                            count = max(1, int(parts[0]))
                except Exception:
                    count = 1
                return gpu_type, count

            instance_type_lower = (instance_type or "").lower()
            try:
                from flow.resources import get_gpu_pricing as _get_pricing_data

                pricing_table = pricing_core.get_pricing_table(
                    overrides=_get_pricing_data().get("gpu_pricing", {})
                )
            except Exception:
                pricing_table = {}

            gpu_type, gpu_count = _extract_gpu_info(instance_type_lower)
            default_table = pricing_table.get("default", {"med": 4.0})
            per_gpu_price = pricing_table.get(gpu_type, pricing_table.get("default", {})).get(
                priority, default_table.get("med", 4.0)
            )
            instance_price = per_gpu_price * max(gpu_count, 1)
            table.add_row("Limit Price/GPU", f"${per_gpu_price:.2f}/hr")
            table.add_row(
                "Limit Price/Instance",
                f"${instance_price:.2f}/hr ({gpu_count} GPU{'s' if gpu_count > 1 else ''})",
            )

            # Optional: fetch live market price from provider when available
            try:
                from flow.sdk.factory import create_client as _create_client

                _client = _create_client(auto_init=True)
                _prov = getattr(_client, "provider", None)
                # Only attempt when provider exposes helper and a region/spec are available
                if _prov and hasattr(_prov, "get_market_price"):
                    region_val = config.get("region") or None
                    market = _prov.get_market_price(instance_type, region_val)
                    if isinstance(market, (int, float)) and market > 0:
                        table.add_row("Market Price/Instance", f"${market:.2f}/hr")
                        # Also show per-GPU market price when sensible
                        if gpu_count > 1:
                            table.add_row(
                                "Market Price/GPU", f"${(market/max(gpu_count,1)):.2f}/hr"
                            )
            except Exception:
                # Non-fatal; pricing view continues without live market data
                pass
            if num_instances > 1:
                table.add_row(
                    "Limit Price/Job",
                    f"${instance_price * num_instances:.2f}/hr ({num_instances} instances)",
                )

    # Upload strategy/timeout
    if not compact and ("upload_strategy" in config or "upload_timeout" in config):
        strategy = config.get("upload_strategy", "auto")
        timeout = int(config.get("upload_timeout", 600))
        table.add_row("Code Upload", f"{strategy} (timeout {timeout}s)")

    # SSH keys count
    if not compact:
        ssh_keys = config.get("ssh_keys") or []
        if isinstance(ssh_keys, (list, tuple)) and len(ssh_keys) > 0:
            shown = ", ".join(ssh_keys[:2]) + (" …" if len(ssh_keys) > 2 else "")
            table.add_row("SSH Keys", shown)

    # Mounts summary
    if not compact and "mounts" in config and config["mounts"]:
        mount_strs = []
        for mount in config["mounts"]:
            if isinstance(mount, dict):
                source = mount.get("source", "")
                target = mount.get("target", "")
                mount_strs.append(f"{target} → {source}")
        if mount_strs:
            table.add_row(
                "Mounts", "\n".join(mount_strs[:5] + (["…"] if len(mount_strs) > 5 else []))
            )

    # Resources (if present)
    if not compact and "resources" in config:
        resources = config["resources"] or {}
        vcpus = resources.get("vcpus")
        mem = resources.get("memory")
        gpus = resources.get("gpus")
        if vcpus:
            table.add_row("vCPUs", str(vcpus))
        if mem:
            table.add_row("Memory", f"{mem} GB")
        if gpus:
            table.add_row("GPUs", str(gpus))

    # Print within a panel title
    wrap_table_in_panel(table, "Task Configuration", console)


def wait_for_task(
    flow_client: Flow,
    task_id: str,
    watch: bool = False,
    json_output: bool = False,
    task_name: str | None = None,
    show_submission_message: bool = True,
    *,
    progress_adapter: object | None = None,
) -> str:
    """Wait for a task to reach running state with progress indication.

    Args:
        flow_client: Flow client instance
        task_id: Task ID to wait for
        watch: Whether to watch task progress
        json_output: Whether to output JSON
        task_name: Optional task name for better display
        show_submission_message: Whether to show "Task submitted" message (default: True)

    Returns:
        Final task status
    """
    if json_output:
        # For JSON output, just poll without visual progress
        while True:
            status = flow_client.status(task_id)
            if status not in ["pending", "preparing"]:
                return status
            time.sleep(2)

    if watch:
        # Use animated progress for watching mode
        if progress_adapter is not None:
            # Adapter-managed loop without local progress UI
            while True:
                status = flow_client.status(task_id)
                if status == "running":
                    return status
                if status in ["completed", "failed", "cancelled"]:
                    return status
                try:
                    if hasattr(progress_adapter, "tick"):
                        progress_adapter.tick()
                except Exception:
                    pass
                time.sleep(1)
        else:
            from flow.cli.ui.presentation.animated_progress import AnimatedEllipsisProgress

            if show_submission_message:
                if task_name:
                    console.print(f"Task submitted: [accent]{task_name}[/accent]")
                else:
                    console.print(f"Task submitted with ID: [accent]{task_id}[/accent]")
            console.print("[dim]Watching task progress...[/dim]\n")

            with AnimatedEllipsisProgress(
                console, "Waiting for task to start", transient=True
            ) as progress:
                while True:
                    status = flow_client.status(task_id)

                    if status == "running":
                        console.print("[success]✓[/success] Task is running")
                        task_ref = task_name or task_id
                        from flow.cli.commands.messages import print_next_actions as _pna

                        _pna(console, [f"Stream logs: [accent]flow logs {task_ref} -f[/accent]"])
                        return status
                    elif status in ["completed", "failed", "cancelled"]:
                        return status

                    time.sleep(2)
    else:
        # Simple waiting mode with animated progress
        if progress_adapter is not None:
            # Adapter-managed loop without local progress UI
            if show_submission_message and task_name is None:
                # Suppress by design for adapter-driven UX
                pass

            ALLOCATION_TIMEOUT_SECONDS = 120
            start_ts = time.time()
            while True:
                status = flow_client.status(task_id)
                if status not in ["pending", "preparing"]:
                    return status
                if time.time() - start_ts > ALLOCATION_TIMEOUT_SECONDS:
                    return status
                try:
                    if hasattr(progress_adapter, "tick"):
                        progress_adapter.tick()
                except Exception:
                    pass
                time.sleep(1)
        else:
            from flow.cli.ui.presentation.animated_progress import AnimatedEllipsisProgress

            if show_submission_message:
                if task_name:
                    console.print(f"Task submitted: [accent]{task_name}[/accent]")
                else:
                    console.print(f"Task submitted with ID: [accent]{task_id}[/accent]")

            # Instance allocation is typically much faster than full provisioning
            # Allocation = getting assigned a GPU (usually <2 minutes)
            # Provisioning = boot + configure + SSH ready (up to 12-20 minutes)
            ALLOCATION_TIMEOUT_SECONDS = 120  # 2 minutes for GPU allocation from pool

            with AnimatedEllipsisProgress(
                console,
                "Waiting for instance allocation",
                transient=True,
                show_progress_bar=True,
                estimated_seconds=ALLOCATION_TIMEOUT_SECONDS,
            ) as progress:
                # Soft timeout after allocation window; fall back to background provisioning UX
                start_ts = time.time()
                while True:
                    status = flow_client.status(task_id)

                    if status not in ["pending", "preparing"]:
                        return status

                    if time.time() - start_ts > ALLOCATION_TIMEOUT_SECONDS:
                        # Stop waiting; let caller present non-blocking guidance
                        return status

                    time.sleep(2)


def maybe_show_auto_status(
    *,
    focus: str | None = None,
    reason: str | None = None,
    show_all: bool | None = None,
    limit: int = 10,
) -> None:
    """Optionally show a compact status table after a state-changing command.

    Behavior:
    - Enabled by default; disable with env `FLOW_AUTO_STATUS=0`.
    - Suppressed when stdout is not a TTY (unless `FLOW_AUTO_STATUS=1` explicitly).
    - Shows active tasks by default, limited to a small number to avoid noise.

    Args:
        focus: Optional task identifier to mention in a heading.
        reason: Optional reason label to show in a dim header.
        show_all: If True, show recent tasks; default is active-only.
        limit: Maximum number of tasks to display (default: 10).
    """
    try:
        pref = os.environ.get("FLOW_AUTO_STATUS", "").strip().lower()
        if pref in {"0", "false", "no", "off"}:
            return
        # If not an interactive terminal and not explicitly opted in, skip
        if not sys.stdout.isatty() and pref not in {"1", "true", "yes", "on"}:
            return

        # Import lazily to avoid heavyweight imports during CLI bootstrap
        from flow.cli.ui.facade.views import (  # type: ignore
            DisplayOptions,
            TaskPresenter,
        )

        opts = DisplayOptions(
            show_all=bool(show_all) if show_all is not None else False,
            status_filter=None,
            limit=max(1, int(limit or 10)),
            show_details=False,
            # Important: mark as non-caching so we don't overwrite the user's
            # index cache (used by 1, 1-3 selections) after state-changing commands.
            # TaskPresenter.present_task_list() only saves indices when json_output is False.
            json_output=True,
        )

        header_bits: list[str] = []
        if reason:
            header_bits.append(reason)
        header_bits.append("status")
        if focus:
            header_bits.append(f"for {focus}")
        header_text = " ".join(header_bits).strip()
        if header_text:
            console.print(f"[dim]— {header_text} —[/dim]")

        presenter = TaskPresenter(console)
        presenter.present_task_list(opts)
    except Exception:
        # Never fail a primary command due to status rendering
        return
