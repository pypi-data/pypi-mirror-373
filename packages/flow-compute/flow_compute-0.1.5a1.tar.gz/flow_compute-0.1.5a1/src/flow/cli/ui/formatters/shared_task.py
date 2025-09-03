"""Shared task formatting utilities for CLI UI.

Single source of truth used by both presentation and components layers.
"""

from __future__ import annotations

from datetime import datetime, timezone

from flow.cli.utils.theme_manager import theme_manager
from flow.sdk.models import Task


class TaskFormatter:
    """Handles task-related formatting for consistent display across CLI commands."""

    @staticmethod
    def format_task_display(task: Task) -> str:
        if task.name:
            if task.task_id and not task.task_id.startswith("bid_"):
                return f"{task.name} ({task.task_id})"
            return task.name
        return task.task_id

    @staticmethod
    def format_short_task_id(task_id: str, length: int = 16) -> str:
        if len(task_id) <= length:
            return task_id
        return task_id[:length] + "..."

    @staticmethod
    def get_status_config(status: str) -> dict[str, str]:
        status_configs = {
            "pending": {
                "symbol": "○",
                "color": theme_manager.get_color("status.pending"),
                "style": "",
            },
            "starting": {
                "symbol": "●",
                "color": theme_manager.get_color("status.starting"),
                "style": "",
            },
            "preparing": {
                "symbol": "●",
                "color": theme_manager.get_color("status.preparing"),
                "style": "",
            },
            "running": {
                "symbol": "●",
                "color": theme_manager.get_color("status.running"),
                "style": "",
            },
            "paused": {
                "symbol": "⏸",
                "color": theme_manager.get_color("status.paused"),
                "style": "",
            },
            "preempting": {
                "symbol": "●",
                "color": theme_manager.get_color("status.preempting"),
                "style": "",
            },
            "completed": {
                "symbol": "●",
                "color": theme_manager.get_color("status.completed"),
                "style": "",
            },
            "failed": {
                "symbol": "●",
                "color": theme_manager.get_color("status.failed"),
                "style": "",
            },
            "cancelled": {
                "symbol": "○",
                "color": theme_manager.get_color("status.cancelled"),
                "style": "",
            },
            "unknown": {"symbol": "○", "color": theme_manager.get_color("muted"), "style": ""},
            # Extra labels used by selection/presentation views
            "available": {"symbol": "✓", "color": theme_manager.get_color("success"), "style": ""},
            "unavailable": {"symbol": "✖", "color": theme_manager.get_color("error"), "style": ""},
            "enabled": {"symbol": "✓", "color": theme_manager.get_color("success"), "style": ""},
            "disabled": {"symbol": "○", "color": theme_manager.get_color("muted"), "style": ""},
        }
        return status_configs.get(
            status.lower(),
            {"symbol": "?", "color": theme_manager.get_color("default"), "style": ""},
        )

    @staticmethod
    def get_status_style(status: str) -> str:
        return TaskFormatter.get_status_config(status)["color"]

    @staticmethod
    def format_status_with_color(status: str) -> str:
        config = TaskFormatter.get_status_config(status)
        try:
            if hasattr(theme_manager, "is_color_enabled") and not theme_manager.is_color_enabled():
                codes = {
                    "running": "RUN",
                    "pending": "PEN",
                    "failed": "ERR",
                    "completed": "OK",
                    "starting": "ST",
                    "preparing": "PRP",
                    "paused": "PAU",
                    "preempting": "PRM",
                    "cancelled": "CAN",
                    "unknown": "UNK",
                }
                code = codes.get(str(status).lower(), str(status).upper()[:3])
                return f"{config['symbol']} {code}"
        except Exception:
            pass
        style_parts = [config["color"]]
        if config["style"]:
            style_parts.append(config["style"])
        style = " ".join(style_parts)
        return f"[{style}]{config['symbol']} {status}[/{style}]"

    @staticmethod
    def format_compact_status(status: str) -> str:
        config = TaskFormatter.get_status_config(status)
        try:
            if hasattr(theme_manager, "is_color_enabled") and not theme_manager.is_color_enabled():
                codes = {
                    "running": "RUN",
                    "pending": "PEN",
                    "failed": "ERR",
                    "completed": "OK",
                    "starting": "ST",
                    "preparing": "PRP",
                    "paused": "PAU",
                    "preempting": "PRM",
                    "cancelled": "CAN",
                    "unknown": "UNK",
                }
                code = codes.get(str(status).lower(), str(status).upper()[:3])
                return f"{config['symbol']} {code}"
        except Exception:
            pass
        style_parts = [config["color"]]
        if config["style"]:
            style_parts.append(config["style"])
        style = " ".join(style_parts)
        return f"[{style}]{config['symbol']}[/{style}]"

    @staticmethod
    def get_display_status(task: Task) -> str:
        """Derive a user-facing status with practical 'starting' semantics.

        Rules:
        - Terminal states never change.
        - 'pending' remains pending regardless of provider hints.
        - 'starting' applies only when ALL are true:
            • Task reports RUNNING, and
            • No SSH endpoint is known yet, and
            • Provider instance_status hints an early boot OR the instance age
              is within a small window after start.
          Otherwise show 'running'. This prioritizes observable readiness over
          stale provider metadata and avoids long "starting" periods.
        - Presence of ``ssh_host`` immediately classifies as 'running'.
        - 'STATUS_SCHEDULED' maps to pending only when not RUNNING.
        """
        status_value = getattr(
            getattr(task, "status", None),
            "value",
            str(getattr(task, "status", "unknown")).lower(),
        )

        # 1) Terminal states are authoritative
        if status_value in {"completed", "failed", "cancelled"}:
            return status_value

        # 2) Pending stays pending (do not reclassify as starting)
        if status_value == "pending":
            return "pending"

        # 3) For RUNNING tasks, show 'starting' only in a very short window
        instance_status = getattr(task, "instance_status", None)
        started_at = getattr(task, "started_at", None)
        # Use instance age when available (resets on preemption); fallback to task age
        try:
            age_seconds = getattr(task, "instance_age_seconds", None)
        except Exception:
            age_seconds = None

        # Bound the 'starting' classification to a tighter window to avoid
        # mislabeling long-running tasks when provider metadata lags.
        # We keep this conservative (3–5 minutes) and prefer observable signals.
        STARTING_WINDOW_SECONDS = 5 * 60  # 5 minutes

        if status_value == "running":
            starting_like = {
                "STATUS_STARTING",
                "STATUS_INITIALIZING",
                "STATUS_PENDING",
                "STATUS_NEW",
                "STATUS_CONFIRMED",
            }

            # If provider says RUNNING, trust it immediately
            if instance_status == "STATUS_RUNNING":
                return "running"

            # If we already have an SSH host/IP, consider it running even if
            # provider metadata still says 'starting' — the machine is up.
            if getattr(task, "ssh_host", None):
                return "running"

            # Only call it 'starting' when provider hints early boot OR
            # started_at is missing AND the instance age is within the short window
            is_early_boot = instance_status in starting_like
            is_very_young = (age_seconds is None) or (age_seconds < STARTING_WINDOW_SECONDS)
            # Only show 'starting' when the instance is very young and either
            # the provider hints early boot or we don't have a started_at yet.
            if (is_early_boot or not started_at) and is_very_young:
                return "starting"
            # Otherwise, treat as fully running even if instance_status lingers
            return "running"

        # 4) Map scheduled to pending only if not running
        if instance_status == "STATUS_SCHEDULED":
            return "pending"

        # Default: return the underlying status value
        return status_value


def format_task_duration(task: Task) -> str:
    """Format task duration or time since creation."""
    try:
        if task.started_at:
            start = task.started_at
            end = task.completed_at or datetime.now(timezone.utc)
            prefix = ""
        else:
            start = task.created_at
            end = datetime.now(timezone.utc)
            prefix = "created "
        if not isinstance(start, datetime):
            start = datetime.fromisoformat(str(start).replace("Z", "+00:00"))
        if not isinstance(end, datetime):
            end = datetime.fromisoformat(str(end).replace("Z", "+00:00"))
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
        duration = end - start
        if duration.days > 0:
            return f"{prefix}{duration.days}d {duration.seconds // 3600}h ago"
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        if hours > 0:
            return f"{prefix}{hours}h {minutes}m ago"
        elif minutes > 0:
            return f"{prefix}{minutes}m ago"
        else:
            return f"{prefix}just now"
    except Exception:
        return "unknown"
