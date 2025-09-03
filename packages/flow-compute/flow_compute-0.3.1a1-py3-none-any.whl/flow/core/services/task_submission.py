"""Task submission logic for the run command.

This module handles the actual submission of tasks to providers,
including name conflict resolution and batch submissions.
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


class NameConflictError(TaskSubmissionError):
    """Raised when a task name conflict occurs."""

    pass


class TaskSubmitter:
    """Handles task submission to providers.

    This class encapsulates submission logic that was previously
    embedded in RunCommand._execute (lines 1052-1130).
    """

    def __init__(self, client: Flow):
        """Initialize submitter with Flow client.

        Args:
            client: Initialized Flow API client.
        """
        self.client = client

    def submit(
        self, config: TaskConfig | None, configs: list[TaskConfig] | None, params: RunParameters
    ) -> tuple[Task | None, list[Task] | None]:
        """Submit task(s) to the provider.

        Args:
            config: Single task configuration (if not array job).
            configs: List of configurations (if array job).
            params: Run parameters including mount specs and policies.

        Returns:
            Tuple of (single_task, task_list) where one will be None.

        Raises:
            TaskSubmissionError: If submission fails.
        """
        mounts = params.execution.mounts

        if configs and len(configs) > 1:
            # Array job submission
            tasks = self._submit_array(configs, mounts, params)
            return None, tasks

        # Single task submission
        task_config = config if config else configs[0] if configs else None
        if not task_config:
            raise TaskSubmissionError("No configuration to submit")

        task = self._submit_single(task_config, mounts, params)
        return task, None

    def _submit_single(
        self, config: TaskConfig, mounts: dict[str, str], params: RunParameters
    ) -> Task:
        """Submit a single task.

        Args:
            config: Task configuration.
            mounts: Mount specifications.
            params: Run parameters for conflict policy.

        Returns:
            Submitted task object.

        Raises:
            TaskSubmissionError: If submission fails.
        """
        # Adjust upload strategy if CLI will manage it
        if params.upload.is_cli_managed:
            config = config.model_copy(update={"upload_strategy": "none"})

        try:
            return self.client.run(config, mounts=mounts)
        except Exception as e:
            # Try to handle name conflict
            if self._is_name_conflict(e):
                retry_task = self._handle_name_conflict(
                    e, config, mounts, params.execution.name_conflict_policy
                )
                if retry_task:
                    logger.info(f"Name conflict resolved with: {retry_task.name}")
                    return retry_task

            # Re-raise with context
            raise TaskSubmissionError(f"Failed to submit task: {e}") from e

    def _submit_array(
        self, configs: list[TaskConfig], mounts: dict[str, str], params: RunParameters
    ) -> list[Task]:
        """Submit an array of tasks.

        Args:
            configs: List of task configurations.
            mounts: Mount specifications.
            params: Run parameters for conflict policy.

        Returns:
            List of submitted tasks.

        Raises:
            TaskSubmissionError: If any submission fails.
        """
        tasks = []

        for i, config in enumerate(configs):
            try:
                # Adjust upload strategy if needed
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

                # For array jobs, we might want to continue or abort
                error_msg = f"Failed to submit task {i+1}/{len(configs)}: {e}"
                logger.error(error_msg)

                # Optionally cancel already submitted tasks
                if tasks and params.execution.name_conflict_policy == "error":
                    self._cleanup_partial_array(tasks)
                    raise TaskSubmissionError(error_msg) from e

        if not tasks:
            raise TaskSubmissionError("No tasks were successfully submitted")

        return tasks

    def _is_name_conflict(self, error: Exception) -> bool:
        """Check if an error indicates a name conflict.

        Args:
            error: Exception to check.

        Returns:
            True if this is a name conflict error.
        """
        error_msg = str(error).lower()
        conflict_indicators = [
            "already in use",
            "already exists",
            "name conflict",
            "already used",
            "duplicate name",
        ]
        return any(indicator in error_msg for indicator in conflict_indicators)

    def _handle_name_conflict(
        self, error: Exception, config: TaskConfig, mounts: dict[str, str], policy: str
    ) -> Task | None:
        """Handle a name conflict based on policy.

        Args:
            error: The conflict error.
            config: Original configuration.
            mounts: Mount specifications.
            policy: Conflict resolution policy (error or suffix).

        Returns:
            Retry task if successful, None otherwise.
        """
        if policy != "suffix":
            return None

        # Generate new name with suffix
        base_name = getattr(config, "name", None) or "flow-task"
        suffix = uuid.uuid4().hex[:6]
        new_name = f"{base_name}-{suffix}"

        logger.info(f"Retrying with auto-generated name: {new_name}")

        try:
            updated_config = config.model_copy(update={"name": new_name, "unique_name": False})
            return self.client.run(updated_config, mounts=mounts)
        except Exception as retry_error:
            logger.error(f"Retry with new name failed: {retry_error}")
            return None

    def _cleanup_partial_array(self, tasks: list[Task]) -> None:
        """Cancel tasks from a partially submitted array.

        Args:
            tasks: List of already submitted tasks to cancel.
        """
        logger.info(f"Cleaning up {len(tasks)} partially submitted tasks")

        for task in tasks:
            try:
                self.client.cancel(task.task_id)
                logger.debug(f"Cancelled task {task.task_id}")
            except Exception as e:
                logger.warning(f"Failed to cancel task {task.task_id}: {e}")

    def validate_ssh_keys(self, config: TaskConfig, params: RunParameters) -> None:
        """Validate that SSH keys are configured.

        Args:
            config: Task configuration.
            params: Run parameters.

        Raises:
            TaskSubmissionError: If no SSH keys are configured.
        """
        # Get effective SSH keys
        effective_keys = []

        # Task-level keys have highest priority
        if getattr(config, "ssh_keys", None):
            effective_keys = list(config.ssh_keys)

        # Environment variable override
        if not effective_keys:
            import os

            env_keys = os.getenv("MITHRIL_SSH_KEYS")
            if env_keys:
                parsed = [k.strip() for k in env_keys.split(",") if k.strip()]
                if parsed:
                    effective_keys = parsed

        # Provider config fallback
        if not effective_keys:
            try:
                from flow.application.config.config import Config

                cfg = Config.from_env(require_auth=True)
                provider_cfg = cfg.provider_config if isinstance(cfg.provider_config, dict) else {}
                cfg_keys = provider_cfg.get("ssh_keys") or []
                if isinstance(cfg_keys, list):
                    effective_keys = list(cfg_keys)
            except Exception:
                logger.debug("Could not load provider config for SSH keys")

        if not effective_keys:
            raise TaskSubmissionError(
                "No SSH keys configured for this run. "
                "Fix: flow ssh-keys upload ~/.ssh/id_ed25519.pub or "
                "export MITHRIL_SSH_KEY=~/.ssh/id_ed25519 or "
                "add mithril.ssh_keys to ~/.flow/config.yaml"
            )
