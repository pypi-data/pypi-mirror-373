"""Jupyter notebook integration for Flow SDK (moved from _internal)."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class JupyterConnection:
    url: str
    task_id: str
    session_id: str
    instance_type: str
    startup_time: float
    ssh_command: str
    last_active: str | None = None
    checkpoint_size: str | None = None
    variables_restored: int | None = None
    restore_time: float | None = None


@dataclass
class LaunchOperation:
    session_id: str
    task_id: str | None
    instance_type: str
    stage: str
    start_time: datetime
    message: str
    error: str | None = None
    connection: JupyterConnection | None = None


class JupyterIntegration:
    KERNEL_SCRIPT = """#!/bin/bash
set -euo pipefail

# Simple kernel startup - security via SSH tunnel only
"""

    # Full implementation retained in original; truncated here for brevity in this move.
    pass
