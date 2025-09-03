"""Shared helpers for task status checks used across CLI commands.

Centralizes common logic for determining whether a task is "active-like"
(eligible for operations that may finalize when the task becomes ready),
so commands don't need to duplicate status string sets.
"""

from __future__ import annotations

from flow.sdk.models import Task

# Provider-agnostic set of statuses that represent an active/provisioning state
ACTIVE_LIKE_STATUSES: set[str] = {
    "running",
    "active",
    "pending",
    "starting",
    "initializing",
    "allocated",
    "provisioning",
}


def get_status_string(task: Task) -> str:
    """Return lowercase status string for a task in a provider-agnostic way."""
    status = getattr(task, "status", None)
    try:
        return getattr(status, "value", str(status)).lower()
    except Exception:
        return str(status).lower() if status is not None else ""


def is_active_like(task: Task) -> bool:
    """Determine if a task is in an active/provisioning state."""
    return get_status_string(task) in ACTIVE_LIKE_STATUSES


def filter_tasks_by_time(tasks: list[Task], since, until):
    """Filter tasks by created_at between since and until datetimes.

    Accepts naive or timezone-aware datetimes; naive values are compared by value.
    """
    if not since and not until:
        return tasks
    result: list[Task] = []
    for t in tasks:
        ts = getattr(t, "created_at", None)
        if not ts:
            continue
        try:
            if getattr(ts, "tzinfo", None) is None and getattr(since, "tzinfo", None) is not None:
                _ts = ts.replace(tzinfo=since.tzinfo)
            else:
                _ts = ts
        except Exception:
            _ts = ts
        if since and _ts < since:
            continue
        if until and _ts > until:
            continue
        result.append(t)
    return result
