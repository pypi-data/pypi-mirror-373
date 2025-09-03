"""CLI-local task submission service.

Avoids CLI -> core import by providing a thin wrapper around the SDK client.
Implements single and array submission with name-conflict handling.
"""

from __future__ import annotations

import logging
import uuid

from flow.sdk.client import Flow
from flow.sdk.models import Task, TaskConfig
from flow.sdk.models.run_params import RunParameters

logger = logging.getLogger(__name__)


class TaskSubmissionError(Exception):
    """Raised when task submission fails."""

    pass


class TaskSubmitter:
    """Handles task submission to providers for the CLI run command."""

    def __init__(self, client: Flow):
        self.client = client

    def submit(
        self, config: TaskConfig | None, configs: list[TaskConfig] | None, params: RunParameters
    ) -> tuple[Task | None, list[Task] | None]:
        mounts = params.execution.mounts

        if configs and len(configs) > 1:
            tasks = self._submit_array(configs, mounts, params)
            return None, tasks

        task_config = config if config else configs[0] if configs else None
        if not task_config:
            raise TaskSubmissionError("No configuration to submit")

        task = self._submit_single(task_config, mounts, params)
        return task, None

    def _submit_single(
        self, config: TaskConfig, mounts: dict[str, str], params: RunParameters
    ) -> Task:
        # Adjust upload strategy if CLI will manage it
        if params.upload.is_cli_managed:
            config = config.model_copy(update={"upload_strategy": "none"})

        try:
            return self.client.run(config, mounts=mounts)
        except Exception as e:
            if self._is_name_conflict(e):
                retry_task = self._handle_name_conflict(
                    e, config, mounts, params.execution.name_conflict_policy
                )
                if retry_task:
                    logger.info(f"Name conflict resolved with: {retry_task.name}")
                    return retry_task
            raise TaskSubmissionError(f"Failed to submit task: {e}") from e

    def _submit_array(
        self, configs: list[TaskConfig], mounts: dict[str, str], params: RunParameters
    ) -> list[Task]:
        tasks: list[Task] = []
        for i, config in enumerate(configs):
            try:
                if params.upload.is_cli_managed:
                    config = config.model_copy(update={"upload_strategy": "none"})
                task = self.client.run(config, mounts=mounts)
                tasks.append(task)
                logger.info(f"Submitted task {i+1}/{len(configs)}: {task.task_id}")
            except Exception as e:
                if self._is_name_conflict(e):
                    retry_task = self._handle_name_conflict(
                        e, config, mounts, params.execution.name_conflict_policy
                    )
                    if retry_task:
                        tasks.append(retry_task)
                        logger.info(f"Name conflict resolved for task {i+1}: {retry_task.name}")
                        continue
                error_msg = f"Failed to submit task {i+1}/{len(configs)}: {e}"
                logger.error(error_msg)
                if tasks and params.execution.name_conflict_policy == "error":
                    self._cleanup_partial_array(tasks)
                    raise TaskSubmissionError(error_msg) from e
        if not tasks:
            raise TaskSubmissionError("No tasks were successfully submitted")
        return tasks

    def _is_name_conflict(self, error: Exception) -> bool:
        msg = str(error).lower()
        return any(
            indicator in msg
            for indicator in (
                "already in use",
                "already exists",
                "name conflict",
                "already used",
                "duplicate name",
            )
        )

    def _handle_name_conflict(
        self, error: Exception, config: TaskConfig, mounts: dict[str, str], policy: str
    ) -> Task | None:
        if policy != "suffix":
            return None
        base_name = getattr(config, "name", None) or "flow-task"
        suffix = uuid.uuid4().hex[:6]
        new_name = f"{base_name}-{suffix}"
        logger.info(f"Retrying with auto-generated name: {new_name}")
        try:
            updated = config.model_copy(update={"name": new_name, "unique_name": False})
            return self.client.run(updated, mounts=mounts)
        except Exception as retry_error:
            logger.error(f"Retry with new name failed: {retry_error}")
            return None

    def _cleanup_partial_array(self, tasks: list[Task]) -> None:
        logger.info(f"Cleaning up {len(tasks)} partially submitted tasks")
        for task in tasks:
            try:
                self.client.cancel(task.task_id)
                logger.debug(f"Cancelled task {task.task_id}")
            except Exception as e:
                logger.warning(f"Failed to cancel task {task.task_id}: {e}")
