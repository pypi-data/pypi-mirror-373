from __future__ import annotations

"""Logs facet: access to task logs and streaming."""

from collections.abc import Iterable
from typing import Protocol, runtime_checkable


@runtime_checkable
class LogsProtocol(Protocol):
    """Log retrieval and streaming operations."""

    def get_task_logs(self, task_id: str, tail: int = 100, log_type: str = "stdout") -> str: ...

    def stream_task_logs(
        self,
        task_id: str,
        log_type: str = "stdout",
        follow: bool = True,
        tail: int = 10,
    ) -> Iterable[str]: ...
