"""Setup helpers for status command pre-execution concerns."""

from __future__ import annotations

import os


def apply_project_env(project: str | None) -> None:
    """If provided, set provider project env variable before creating Flow()."""
    if not project:
        return
    try:
        os.environ["MITHRIL_PROJECT"] = project
    except Exception:
        pass


def apply_force_refresh() -> None:
    """Clear prefetch caches before proceeding when --force-refresh is set."""
    try:
        from flow.cli.utils.prefetch import (
            refresh_active_task_caches as _refresh_active,
        )
        from flow.cli.utils.prefetch import (
            refresh_all_tasks_cache as _refresh_all,
        )

        _refresh_active()
        _refresh_all()
    except Exception:
        pass
