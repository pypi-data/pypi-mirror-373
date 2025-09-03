"""Helpers for consistent JSON output across CLI commands.

Conventions
- Timestamps: ISO8601 in UTC with trailing 'Z' (no microseconds)
- Task objects: id, name, status, instance_type, num_instances, created_at,
  started_at, completed_at (all timestamps are ISO Z strings or null)
- Error objects: {"error": {"code": str|None, "message": str, "request_id": str|None, "hint": str|None}}
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from flow.cli.commands.base import console


def iso_z(dt: datetime | None) -> str | None:
    """Return ISO8601 UTC string with 'Z' suffix for a datetime.

    Drops microseconds for stability. Returns None if input is None.
    """
    if dt is None:
        return None
    try:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        dt = dt.astimezone(timezone.utc).replace(microsecond=0)
        s = dt.isoformat()
        # Normalize +00:00 to Z
        if s.endswith("+00:00"):
            s = s[:-6] + "Z"
        return s
    except Exception:
        # Best effort stringification
        try:
            return str(dt)
        except Exception:
            return None


def task_to_json(task: Any) -> dict[str, Any]:
    """Best-effort conversion of an SDK Task to a stable JSON shape."""
    status = getattr(task, "status", None)
    status_val = getattr(status, "value", None) or str(status or "")
    return {
        "id": getattr(task, "task_id", ""),
        "name": getattr(task, "name", None),
        "status": status_val,
        "instance_type": getattr(task, "instance_type", None),
        "num_instances": getattr(task, "num_instances", None),
        "region": getattr(task, "region", None),
        "created_at": iso_z(getattr(task, "created_at", None)),
        "started_at": iso_z(getattr(task, "started_at", None)),
        "completed_at": iso_z(getattr(task, "completed_at", None)),
    }


def error_json(
    message: str,
    *,
    code: str | None = None,
    request_id: str | None = None,
    hint: str | None = None,
) -> dict[str, Any]:
    """Standard error envelope for CLI JSON outputs."""
    return {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
            "hint": hint,
        }
    }


def print_json(data: Any) -> None:
    """Print JSON data through the themed console.

    Keeps a single place to control encoding nuances.
    """
    try:
        console.print(json.dumps(data))
    except Exception:
        # Last resort fallback
        try:
            console.print(str(data))
        except Exception:
            pass


def reservation_to_json(res: Any) -> dict[str, Any]:
    """Normalize a reservation object to a stable JSON shape."""
    status = getattr(res, "status", None)
    status_val = getattr(status, "value", None) or str(status or "")
    return {
        "id": getattr(res, "reservation_id", getattr(res, "id", "")),
        "name": getattr(res, "name", None),
        "status": status_val,
        "instance_type": getattr(res, "instance_type", None),
        "region": getattr(res, "region", None),
        "quantity": getattr(res, "quantity", None),
        "start_time_utc": iso_z(getattr(res, "start_time_utc", None)),
        "end_time_utc": iso_z(getattr(res, "end_time_utc", None)),
        "price_total_usd": getattr(res, "price_total_usd", None),
    }


def volume_to_json(vol: Any, *, attachments: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Normalize a volume object to a stable JSON shape."""
    interface = getattr(getattr(vol, "interface", None), "value", None) or getattr(
        vol, "interface", None
    )
    attached_to = getattr(vol, "attached_to", None) or []
    attached_count = (
        len(attached_to) if isinstance(attached_to, (list, tuple)) else (1 if attached_to else 0)
    )
    status = "attached" if attached_count else "available"
    return {
        "id": getattr(vol, "volume_id", getattr(vol, "id", "")),
        "name": getattr(vol, "name", None),
        "region": getattr(vol, "region", None),
        "size_gb": getattr(vol, "size_gb", None),
        "interface": interface,
        "status": status,
        "attached_count": attached_count,
        "created_at": iso_z(getattr(vol, "created_at", None)),
        **({"attachments": attachments} if attachments is not None else {}),
    }


__all__ = [
    "iso_z",
    "task_to_json",
    "reservation_to_json",
    "volume_to_json",
    "error_json",
    "print_json",
]
