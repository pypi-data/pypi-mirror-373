"""Centralized path constants and helpers for mount destinations.

This module defines canonical paths used inside task containers/instances
and provides helpers to compute consistent mount destinations.
"""

from __future__ import annotations

# Canonical directories inside the task container/instance
WORKSPACE_DIR: str = "/workspace"
VOLUMES_ROOT: str = "/volumes"
DATA_ROOT: str = "/data"
DOWNLOADS_DIR: str = "/downloads"

# Ephemeral NVMe/instance-local storage (if present)
EPHEMERAL_NVME_DIR: str = "/mnt/local"

# Dev environment standard locations
DEV_HOME_DIR: str = "/root"
DEV_ENVS_ROOT: str = "/envs"

# Temporary/result files used by Flow
RESULT_FILE: str = "/tmp/flow_result.json"
STARTUP_SCRIPT_PREFIX: str = "/tmp/flow-startup-"

# S3FS-related paths
S3FS_CACHE_DIR: str = "/tmp/s3fs_cache"
S3FS_PASSWD_FILE: str = "/tmp/s3fs_passwd"


def default_volume_mount_path(
    *, name: str | None = None, volume_id: str | None = None, index: int | None = None
) -> str:
    """Compute a stable default mount path for a volume.

    Preference order:
    1) Use provided human-readable name
    2) Derive from volume_id suffix
    3) Use index-based fallback if provided
    4) Generic fallback
    """

    if name:
        return f"{VOLUMES_ROOT}/{name}"
    if volume_id:
        suffix = volume_id[-6:] if len(volume_id) >= 6 else volume_id
        return f"{VOLUMES_ROOT}/volume-{suffix}"
    if index is not None:
        return f"{VOLUMES_ROOT}/volume-{index}"
    return f"{VOLUMES_ROOT}/volume"
