"""Time specification parsing utilities for CLI.

Provides a single function to parse human-friendly time specs like
"5m", "2h", "7d" or ISO8601 strings with optional trailing Z.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


def parse_timespec(value: str | None) -> datetime | None:
    """Parse a time specification string into an aware UTC datetime.

    Accepted formats:
    - Relative: "<int>m", "<int>h", "<int>d"
    - Absolute: ISO8601, with optional trailing "Z" for UTC

    Args:
        value: The input string

    Returns:
        A timezone-aware UTC datetime, or None if parsing fails or value is falsy.
    """
    if not value:
        return None

    s = value.strip()
    try:
        if s.endswith("m") and s[:-1].isdigit():
            return datetime.now(timezone.utc) - timedelta(minutes=int(s[:-1]))
        if s.endswith("h") and s[:-1].isdigit():
            return datetime.now(timezone.utc) - timedelta(hours=int(s[:-1]))
        if s.endswith("d") and s[:-1].isdigit():
            return datetime.now(timezone.utc) - timedelta(days=int(s[:-1]))

        # ISO8601 with optional Z
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None
