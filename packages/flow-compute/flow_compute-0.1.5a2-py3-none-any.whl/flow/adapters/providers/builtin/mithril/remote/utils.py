from __future__ import annotations

import time
import uuid as _uuid


def human_age(seconds: float | None) -> str | None:
    """Return compact human age like '1h 32m' or '7d'."""
    try:
        if seconds is None or seconds < 0:
            return None
        seconds = max(0.0, min(seconds, 7 * 24 * 3600))
        minutes = int(seconds // 60)
        if minutes < 1:
            return "<1m"
        hours, mins = divmod(minutes, 60)
        if hours < 24:
            return f"{hours}h {mins}m" if hours else f"{mins}m"
        days, rem = divmod(hours, 24)
        return f"{days}d" if rem == 0 else f"{days}d {rem}h"
    except Exception:
        return None


def new_request_id(operation: str) -> str:
    """Generate a client-side correlation ID for non-HTTP operations."""
    try:
        return f"{operation}-{_uuid.uuid4()}"
    except Exception:
        return f"{operation}-{int(time.time()*1000)}"
