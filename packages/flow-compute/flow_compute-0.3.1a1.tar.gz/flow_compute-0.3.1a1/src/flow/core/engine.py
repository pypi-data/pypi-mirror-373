"""Unified job submission service for Flow SDK.

Central submission interface that:
1. Accepts input from various frontends (SLURM, Submitit, YAML, SDK)
2. Uses frontend adapters to parse into a common TaskConfig
3. Submits to Flow infrastructure (TaskManager)
"""

import asyncio
import logging
from typing import Any

try:
    from flow.plugins.registry import PluginRegistry as FrontendRegistry
except Exception:
    from flow.adapters.frontends.registry import FrontendRegistry

try:
    from flow.application.services.task_service import (
        TaskService as TaskManager,
    )  # favor application layer
except Exception:  # pragma: no cover
    TaskManager = object  # type: ignore
from flow.sdk.models import Task, TaskConfig

logger = logging.getLogger(__name__)


class JobSubmissionService:
    """Central job submission service.

    Coordinates between frontend adapters and Flow infrastructure.
    """

    def __init__(
        self,
        task_manager: TaskManager | None = None,
    ):
        self.task_manager = task_manager

        # Track submitted jobs for status queries
        self._job_mappings: dict[str, str] = {}  # frontend_id -> flow_id
        self._job_metadata: dict[str, dict[str, Any]] = {}

    async def submit_job(self, frontend: str, input_data: Any, **options: Any) -> str:
        """Submit a job through specified frontend.

        Args:
            frontend: Frontend name (e.g., "slurm", "submitit", "yaml")
            input_data: Frontend-specific input data
            **options: Frontend-specific options

        Returns:
            Job ID in frontend-specific format
        """
        # Get frontend adapter
        adapter = FrontendRegistry.get_adapter(frontend)

        # Parse input into TaskConfig
        task_config = await adapter.parse_and_convert(input_data, **options)

        # Convert to Flow's internal format
        flow_config = adapter.to_flow_task_config(task_config)

        # Submit to Flow
        if self.task_manager:
            result = self._submit_to_flow(flow_config)
            flow_job_id = self._extract_job_id(result)
        else:
            # Mock submission for testing
            import uuid

            flow_job_id = f"task_{uuid.uuid4().hex[:8]}"
            logger.warning(f"No TaskManager available, using mock job ID: {flow_job_id}")

        # Format job ID for frontend
        frontend_job_id = adapter.format_job_id(flow_job_id)

        # Store mapping
        self._job_mappings[frontend_job_id] = flow_job_id
        self._job_metadata[flow_job_id] = {
            "frontend": frontend,
            "frontend_id": frontend_job_id,
            "task_config": task_config,
            "submitted_at": asyncio.get_event_loop().time(),
        }

        logger.info(f"Submitted job via {frontend} frontend: {frontend_job_id} -> {flow_job_id}")

        return frontend_job_id

    async def submit_array_job(self, frontend: str, input_data: Any, **options: Any) -> str:
        """Submit an array job (multiple related tasks).

        Args:
            frontend: Frontend name
            input_data: Frontend-specific input data
            **options: Frontend-specific options including array spec

        Returns:
            Array job ID in frontend-specific format
        """
        # Get frontend adapter
        adapter = FrontendRegistry.get_adapter(frontend)

        # Check if adapter supports array jobs
        if hasattr(adapter, "parse_array_job"):
            task_configs = await adapter.parse_array_job(input_data, **options)
        else:
            # Fall back to single job
            task_config = await adapter.parse_and_convert(input_data, **options)
            task_configs = [task_config]

        # Submit each task
        flow_job_ids = []
        for task_config in task_configs:
            flow_config = adapter.to_flow_task_config(task_config)

            if self.task_manager:
                result = self._submit_to_flow(flow_config)
                flow_job_id = self._extract_job_id(result)
            else:
                import uuid

                flow_job_id = f"task_{uuid.uuid4().hex[:8]}"

            flow_job_ids.append(flow_job_id)

        # Generate array job ID
        array_job_id = adapter.format_job_id(flow_job_ids[0])

        # Store mappings for all tasks
        for i, flow_job_id in enumerate(flow_job_ids):
            task_frontend_id = f"{array_job_id}_{i + 1}"
            self._job_mappings[task_frontend_id] = flow_job_id
            self._job_metadata[flow_job_id] = {
                "frontend": frontend,
                "frontend_id": task_frontend_id,
                "array_job_id": array_job_id,
                "array_index": i + 1,
                "submitted_at": asyncio.get_event_loop().time(),
            }

        logger.info(
            f"Submitted array job via {frontend} frontend: "
            f"{array_job_id} with {len(flow_job_ids)} tasks"
        )

        return array_job_id

    async def get_job_status(self, frontend: str, job_id: str) -> dict[str, Any]:
        """Get job status.

        Args:
            frontend: Frontend that submitted the job
            job_id: Frontend-specific job ID

        Returns:
            Status information dict
        """
        # Resolve to Flow job ID
        flow_job_id = self._job_mappings.get(job_id, job_id)

        # Get status from Flow
        status = "pending"
        if self.task_manager:
            task = self._get_task(flow_job_id)
            if task:
                status = task.status.value

        # Get frontend adapter for formatting
        adapter = FrontendRegistry.get_adapter(frontend)
        formatted_status = adapter.format_status(status)

        return {
            "job_id": job_id,
            "flow_job_id": flow_job_id,
            "status": status,
            "formatted_status": formatted_status,
            "frontend": frontend,
        }

    async def cancel_job(self, frontend: str, job_id: str) -> bool:
        """Cancel a job.

        Args:
            frontend: Frontend that submitted the job
            job_id: Frontend-specific job ID

        Returns:
            True if cancelled successfully
        """
        # Resolve to Flow job ID
        flow_job_id = self._job_mappings.get(job_id, job_id)

        # Cancel via Flow
        if self.task_manager:
            try:
                self._cancel_task(flow_job_id)
                logger.info(f"Cancelled job {job_id} ({flow_job_id})")
                return True
            except Exception as e:
                logger.error(f"Failed to cancel job {job_id}: {e}")
                return False

        return False

    def _submit_to_flow(self, flow_config: TaskConfig) -> Task:
        """Submit to Flow infrastructure."""
        return self.task_manager.submit_task(flow_config)

    def _get_task(self, task_id: str) -> Task | None:
        """Get task from Flow."""
        return self.task_manager.get_task_status(task_id)

    def _cancel_task(self, task_id: str) -> None:
        """Cancel task in Flow."""
        return self.task_manager.cancel_task(task_id)

    def _extract_job_id(self, result: Any) -> str:
        """Extract job ID from submission result."""
        if hasattr(result, "task_id"):
            return result.task_id
        if isinstance(result, dict):
            return result.get("task_id") or str(result)
        return str(result)


# Global submission service instance
_submission_service: JobSubmissionService | None = None


def get_submission_service(task_manager: TaskManager | None = None) -> JobSubmissionService:
    """Get or create the global submission service.

    Args:
        task_manager: Optional TaskManager instance. If not provided,
                     service will operate in mock mode.

    Returns:
        JobSubmissionService instance
    """
    global _submission_service

    if _submission_service is None or task_manager is not None:
        _submission_service = JobSubmissionService(
            task_manager=task_manager,
        )

    return _submission_service
