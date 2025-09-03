"""Task formatting utilities for CLI output (delegates to shared)."""

from __future__ import annotations

from flow.cli.ui.formatters.shared_task import TaskFormatter as TaskFormatter
from flow.cli.ui.formatters.shared_task import format_task_duration as format_task_duration
from flow.sdk.models import Task


def format_task_summary(task: Task) -> str:
    name = task.name or "unnamed"
    if len(name) > 25:
        name = name[:22] + "..."
    return name


def get_capability_warnings(task: Task) -> list[str]:
    warnings: list[str] = []
    try:
        status_val = getattr(
            getattr(task, "status", None), "value", str(getattr(task, "status", "")).lower()
        )
        if status_val in ["running", "completed", "failed"]:
            if not task.has_ssh_access and not getattr(task, "ssh_keys_configured", False):
                warnings.append("No SSH access - task was submitted without SSH keys")
            elif not task.has_ssh_access and getattr(task, "ssh_keys_configured", False):
                warnings.append("SSH keys configured but access not yet available")
        elif status_val == "pending" and not getattr(task, "ssh_keys_configured", False):
            warnings.append("No SSH keys configured - logs won't be available")
    except Exception:
        pass
    return warnings


def format_capabilities(task: Task) -> str:
    caps = getattr(task, "capabilities", {}) or {}
    icons = {"ssh": "🔐" if caps.get("ssh") else "🚫", "logs": "📋" if caps.get("logs") else "🚫"}
    return f"SSH: {icons['ssh']}  Logs: {icons['logs']}"


def format_post_submit_info(task: Task) -> list[str]:
    lines: list[str] = []
    task_ref = task.name or task.task_id
    from flow.cli.utils.theme_manager import theme_manager as _tm

    ok = _tm.get_color("success")
    lines.append(f"[{ok}]✓[/{ok}] Task submitted: {task_ref}")
    warnings = get_capability_warnings(task)
    if warnings:
        lines.append("")
        warn = _tm.get_color("warning")
        lines.append(f"[{warn}]⚠ Warning:[/{warn}]")
        for w in warnings:
            lines.append(f"  {w}")
        lines.append("  Run 'flow init' to configure SSH keys for future tasks")
    else:
        lines += [
            "",
            "Commands:",
            f"  [accent]flow status {task_ref}[/accent]",
            f"  [accent]flow logs {task_ref}[/accent] [--follow]",
            f"  [accent]flow ssh {task_ref}[/accent]",
        ]
    return lines


def format_post_submit_commands(task: Task) -> list[str]:
    task_ref = task.name or task.task_id
    return [
        f"  [accent]flow status {task_ref}[/accent]",
        f"  [accent]flow logs {task_ref} -f[/accent]",
        f"  [accent]flow ssh {task_ref}[/accent]",
    ]
