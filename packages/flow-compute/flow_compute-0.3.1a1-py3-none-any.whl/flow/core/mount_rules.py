"""Centralized mount auto-target rules.

Provides a single function to determine the default target mount path
for a given source URL/path across SDK, CLI, and providers.
"""

from __future__ import annotations

from pathlib import Path

from flow.core.paths import DATA_ROOT, VOLUMES_ROOT


def auto_target_for_source(source: str) -> str:
    """Return the default target path for a given source.

    Rules:
    - s3://...        -> /data
    - volume://...    -> /volumes
    - local path/url  -> /mnt/<basename> (fallback)
    """

    if source.startswith("s3://"):
        return DATA_ROOT
    if source.startswith("volume://"):
        return VOLUMES_ROOT

    # For local paths/URLs fall back to /mnt/<basename>
    try:
        name = Path(source).name
        return f"/mnt/{name or 'root'}"
    except Exception:
        return "/mnt/data"
