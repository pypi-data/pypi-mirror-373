"""Logs facet - handles task log retrieval and streaming."""

from __future__ import annotations

import logging
import time
from collections import deque
from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING

from flow.adapters.providers.builtin.mithril.adapters.remote import RemoteExecutionError
from flow.adapters.providers.builtin.mithril.api.handlers import handle_mithril_errors
from flow.errors.messages import TASK_INSTANCE_NOT_ACCESSIBLE, format_error

if TYPE_CHECKING:
    from flow.adapters.providers.builtin.mithril.provider.context import MithrilContext

logger = logging.getLogger(__name__)


class LogsFacet:
    """Handles log operations for tasks."""

    def __init__(self, ctx: MithrilContext, get_remote_ops: Callable) -> None:
        """Initialize logs facet.

        Args:
            ctx: Mithril context with all dependencies
            get_remote_ops: Callable to get remote operations handler
        """
        self.ctx = ctx
        self._logger = getattr(ctx, "logger", logger)
        self.get_remote_ops = get_remote_ops

        # Connect LogService to remote ops
        if hasattr(self.ctx.log_service, "_remote"):
            self.ctx.log_service._remote = None  # Clear legacy internal

    @handle_mithril_errors("Get task logs")
    def get_task_logs(self, task_id: str, tail: int = 100, log_type: str = "stdout") -> str:
        """Get recent logs for a task.

        Args:
            task_id: Task ID
            tail: Number of lines to retrieve
            log_type: Type of logs ("stdout" or "stderr")

        Returns:
            Log contents as string
        """
        # Get bid data for status checking
        try:
            from flow.adapters.providers.builtin.mithril.provider.facets.tasks import TasksFacet

            tasks = TasksFacet(self.ctx)
            bid = tasks.get_bid_dict(task_id)
        except Exception as e:
            logger.debug(f"Failed to get bid for task {task_id}: {e}")
            bid = None

        # Check if logs are available (handles pending/cancelled states)
        if hasattr(self.ctx.log_service, "get_recent"):
            gated = self.ctx.log_service.get_recent(
                task_id=task_id, bid=bid, tail=tail, log_type=log_type, execute=False
            )

            # If gated response indicates logs aren't available, return it
            if isinstance(gated, str) and (
                gated.startswith("Task ")
                or gated.startswith("Failed")
                or gated.endswith("available")
            ):
                return gated

        # Build log retrieval command
        cmd = self.ctx.log_service.build_command(task_id, tail, log_type)

        # Check cache first
        cached = self.ctx.log_service.get_cached(task_id, tail, log_type)
        if cached is not None:
            return cached

        # Execute command to get logs
        try:
            remote = self.get_remote_ops()
            if remote is not None:
                output = remote.execute_command(task_id, cmd).strip()
            else:
                output = self.ctx.log_service.execute_via_remote(task_id, cmd)

            # Cache the result
            self.ctx.log_service.set_cache(task_id, tail, log_type, output.strip())

            return output.strip() if output else "No logs available"

        except RemoteExecutionError as e:
            if "no ssh access" in str(e).lower():
                return format_error(TASK_INSTANCE_NOT_ACCESSIBLE, task_id=task_id)
            return f"Failed to retrieve logs: {e}"
        except Exception as e:
            return f"Failed to retrieve logs: {e}"

    def stream_task_logs(
        self, task_id: str, log_type: str = "stdout", follow: bool = True, tail: int = 10
    ) -> Iterator[str]:
        """Stream logs from a task.

        Args:
            task_id: Task ID
            log_type: Type of logs ("stdout", "stderr", "combined", "startup", "host", "auto")
            follow: Whether to follow log output
            tail: Initial number of lines to retrieve

        Yields:
            Log lines as they become available
        """
        # If not following, just return recent logs via snapshot helper
        if not follow:
            for line in self.get_task_logs(task_id, tail=tail, log_type=log_type).split("\n"):
                if line:
                    yield line
            return

        # Build a streaming-friendly remote command (includes initial tail)
        try:
            cmd = self.ctx.log_service.build_command(task_id, tail, log_type, follow=True)
        except Exception as e:
            # Fallback to simple polling if command construction fails
            logger.debug(f"Failed to build follow command for logs: {e}")
            initial_logs = self.get_task_logs(task_id, tail=tail, log_type=log_type)
            if initial_logs and not initial_logs.startswith("Failed"):
                for line in initial_logs.split("\n"):
                    if line:
                        yield line
            # Minimal polling loop
            last_size = len(initial_logs) if initial_logs else 0
            while True:
                time.sleep(2)
                logs = self.get_task_logs(task_id, tail=1000, log_type=log_type)
                if not logs or logs.startswith("Failed"):
                    continue
                if len(logs) > last_size:
                    for line in logs[last_size:].split("\n"):
                        if line:
                            yield line
                    last_size = len(logs)
            return

        remote = self.get_remote_ops()
        if remote is None:
            yield "Failed to stream logs: remote operations unavailable"
            return

        # Simple, bounded de-dupe to avoid duplicate head after reconnect
        recent = deque(maxlen=max(10, tail))
        attempts = 0
        backoff = 1.0
        max_attempts = 4

        while True:
            try:
                for line in remote.stream_command(task_id, cmd):
                    if line and (line not in recent):
                        yield line
                        recent.append(line)
                # Process exited normally; stop retrying
                return
            except KeyboardInterrupt:
                return
            except Exception as e:
                attempts += 1
                if attempts >= max_attempts:
                    yield f"Failed to stream logs: {e}"
                    return
                time.sleep(backoff)
                backoff = min(backoff * 2.0, 8.0)
