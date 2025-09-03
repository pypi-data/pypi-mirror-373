"""Task execution engine for Flow SDK.

Consolidates task lifecycle management, execution orchestration, and progress
monitoring into a single engine. Handles the full lifecycle from allocation
through cleanup.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone

# Local import to avoid circular import during module initialization
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from flow.sdk.models import Instance, Task, TaskConfig, TaskStatus, Volume
else:
    # Runtime imports to avoid type-only NameError at class definition time.
    # We only need the names for annotations at runtime, so import and alias to Any.
    from typing import Any as _Any

    from flow.sdk.models import TaskStatus as _TaskStatus

    TaskStatus = _TaskStatus
    Instance = _Any  # type: ignore
    Task = _Any  # type: ignore
    TaskConfig = _Any  # type: ignore
    Volume = _Any  # type: ignore
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flow.protocols.provider import ProviderProtocol as IProvider  # pragma: no cover
else:
    IProvider = object  # type: ignore
from flow.errors import FlowError

logger = logging.getLogger(__name__)


# ==================== Task Progress Models ====================


@dataclass
class TaskProgress:
    """Progress update for a running task."""

    status: TaskStatus
    message: str
    percent_complete: float | None = None
    metadata: dict[str, Any] | None = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


# ==================== Resource Tracking ====================


@dataclass
class TrackedResource:
    """Base class for tracked resources."""

    resource_id: str
    resource_type: str
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)


@dataclass
class TrackedVolume(TrackedResource):
    """Tracked volume resource."""

    def __init__(self, volume: Volume):
        super().__init__(resource_id=volume.volume_id, resource_type="volume")
        self.volume = volume


@dataclass
class TrackedInstance(TrackedResource):
    """Tracked instance resource."""

    def __init__(self, instance: Instance):
        super().__init__(resource_id=instance.instance_id, resource_type="instance")
        self.instance = instance


class ResourceTracker:
    """Tracks resources for lifecycle management.

    Maintains a stack of resources in creation order to enable
    LIFO cleanup (reverse order of creation).
    """

    def __init__(self):
        self._resources: list[TrackedResource] = []
        self._provider: IProvider | None = None

    def set_provider(self, provider: IProvider) -> None:
        """Set the provider for resource operations."""
        self._provider = provider

    def track_volume(self, volume: Volume) -> None:
        """Track a volume for cleanup."""
        self._resources.append(TrackedVolume(volume))
        logger.debug(f"Tracking volume: {volume.volume_id}")

    def track_instance(self, instance: Instance) -> None:
        """Track an instance for cleanup."""
        self._resources.append(TrackedInstance(instance))
        logger.debug(f"Tracking instance: {instance.instance_id}")

    def clear(self) -> None:
        """Clear tracked resources (on success)."""
        count = len(self._resources)
        self._resources.clear()
        if count > 0:
            logger.debug(f"Cleared {count} tracked resources")

    def cleanup_all(self) -> None:
        """Clean up all tracked resources in reverse order."""
        if not self._provider:
            logger.warning("No provider set for resource cleanup")
            return

        # Clean up in LIFO order
        while self._resources:
            resource = self._resources.pop()
            try:
                if isinstance(resource, TrackedVolume):
                    logger.info(f"Cleaning up volume: {resource.resource_id}")
                    self._provider.delete_volume(resource.resource_id)
                elif isinstance(resource, TrackedInstance):
                    logger.info(f"Terminating instance: {resource.resource_id}")
                    self._provider.stop_task(resource.resource_id)
            except Exception as e:
                # Log but continue cleanup
                logger.error(
                    f"Failed to clean up {resource.resource_type} {resource.resource_id}: {e}"
                )


# ==================== Task Engine ====================


class TaskEngine:
    """Unified task execution engine.

    Manages the complete task lifecycle including:
    - Resource allocation
    - Task execution
    - Progress monitoring
    - Automatic cleanup

    Example:
        >>> engine = TaskEngine()
        >>> task = engine.run_task(provider, config)
        >>> for progress in engine.monitor_progress(task):
        ...     print(f"{progress.status}: {progress.message}")
    """

    def __init__(self):
        self.logger = logger.getChild("TaskEngine")

    def run_task(self, provider: IProvider, config: TaskConfig, dry_run: bool = False) -> Task:
        """Execute a task with full lifecycle management.

        Implements the universal compute workflow:
        1. Find matching resources
        2. Prepare storage volumes
        3. Launch instance
        4. Wait for readiness
        5. Submit task

        Args:
            provider: Compute provider to use
            config: Task configuration
            dry_run: If True, validate without executing

        Returns:
            Task object for monitoring/interaction

        Raises:
            FlowError: If any step fails
        """
        self.logger.info(f"Starting task execution: {config.name}")

        # Create resource tracker for lifecycle management
        tracker = ResourceTracker()
        tracker.set_provider(provider)

        with self._resource_lifecycle(tracker):
            # Phase 1: Find matching resources
            self.logger.info("Phase 1: Finding available resources")
            requirements = self._build_requirements(config)
            instances = provider.find_instances(requirements, limit=10)

            if not instances:
                raise FlowError("No instances available matching requirements")

            # Select best instance
            instance = instances[0]
            self.logger.info(
                f"Selected instance: {instance.instance_type} "
                f"in {instance.region} at ${instance.price_per_hour}/hour"
            )

            if dry_run:
                self.logger.info("Dry run complete - no resources allocated")
                return self._create_dry_run_task(config, instance)

            # Phase 2: Prepare storage
            volumes = []
            if config.volumes:
                self.logger.info("Phase 2: Preparing storage volumes")
                for volume_spec in config.volumes:
                    if hasattr(volume_spec, "volume_id") and volume_spec.volume_id:
                        # Existing volume - just track it
                        volume = Volume(
                            volume_id=volume_spec.volume_id,
                            name=volume_spec.name or "",
                            size_gb=volume_spec.size_gb,
                            region=instance.region,
                            interface=volume_spec.interface,
                        )
                    else:
                        # Create new volume
                        volume = provider.create_volume(
                            size_gb=volume_spec.size_gb, name=volume_spec.name
                        )
                        tracker.track_volume(volume)
                    volumes.append(volume)
                    self.logger.info(f"Prepared volume: {volume.volume_id}")

            # Phase 3: Submit task
            self.logger.info("Phase 3: Submitting task to instance")

            # Prepare task configuration with provider defaults
            prepared_config = provider.prepare_task_config(config)

            # Submit task
            task = provider.submit_task(
                instance_type=instance.instance_type,
                config=prepared_config,
                volume_ids=[v.volume_id for v in volumes] if volumes else None,
            )

            # Inject allocation info
            task.allocation_id = instance.allocation_id
            task._provider = provider

            self.logger.info(f"Task submitted: {task.task_id}")

            # Phase 4: Wait for task to start
            self.logger.info("Phase 4: Waiting for task to start")
            task = self._wait_for_start(provider, task, timeout=300)

            # Clear tracker on success - resources now owned by task
            tracker.clear()

            self.logger.info(f"Task {task.task_id} is running")
            return task

    def monitor_progress(
        self, task: Task, poll_interval: float = 2.0
    ) -> Generator[TaskProgress, None, None]:
        """Monitor task progress with status updates.

        Yields progress updates only when status changes to avoid spam.

        Args:
            task: Task to monitor
            poll_interval: Seconds between status checks

        Yields:
            TaskProgress updates
        """
        provider = getattr(task, "_provider", None)
        if not provider:
            raise FlowError("Task missing provider reference")

        last_status = None
        last_message = None

        while True:
            try:
                # Get current task status
                current_task = provider.get_task(task.task_id)
                current_status = current_task.status
                current_message = current_task.message or ""

                # Yield update if status or message changed
                if current_status != last_status or current_message != last_message:
                    progress = TaskProgress(
                        status=current_status,
                        message=current_message,
                        metadata={"task_id": task.task_id},
                    )
                    yield progress

                    last_status = current_status
                    last_message = current_message

                # Check if terminal state
                if current_status in [
                    TaskStatus.COMPLETED,
                    TaskStatus.FAILED,
                    TaskStatus.CANCELLED,
                ]:
                    break

                time.sleep(poll_interval)

            except Exception as e:
                # Yield error as progress update
                yield TaskProgress(status=TaskStatus.FAILED, message=f"Monitoring error: {e}")
                break

    def wait_for_completion(
        self,
        task: Task,
        timeout: int | None = None,
        callback: Callable[[TaskProgress], None] | None = None,
    ) -> Task:
        """Wait for task to reach terminal state.

        Args:
            task: Task to wait for
            timeout: Maximum seconds to wait
            callback: Optional callback for progress updates

        Returns:
            Updated task object

        Raises:
            TimeoutError: If timeout exceeded
        """
        start_time = time.time()

        for progress in self.monitor_progress(task):
            # Call callback if provided
            if callback:
                callback(progress)

            # Check timeout
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(
                    f"Task {task.task_id} did not complete within {timeout}s. "
                    f"Current status: {progress.status}"
                )

            # Update task object
            task.status = progress.status
            task.message = progress.message

        return task

    # ==================== Private Methods ====================

    @contextmanager
    def _resource_lifecycle(self, tracker: ResourceTracker):
        """Context manager for resource lifecycle.

        Ensures resources are cleaned up on error.
        """
        try:
            yield tracker
        except Exception:
            self.logger.info("Error occurred - cleaning up resources")
            tracker.cleanup_all()
            raise

    def _build_requirements(self, config: TaskConfig) -> dict[str, Any]:
        """Build provider-agnostic requirements from task config."""
        requirements = {
            "instance_type": config.instance_type,
        }

        # Add optional requirements
        if config.max_price_per_hour:
            requirements["max_price"] = config.max_price_per_hour

        if config.region:
            requirements["region"] = config.region

        # Extract GPU requirements from instance type if needed
        if hasattr(config, "min_gpu_memory_gb") and config.min_gpu_memory_gb:
            requirements["min_gpu_memory"] = config.min_gpu_memory_gb

        return requirements

    def _wait_for_start(self, provider: IProvider, task: Task, timeout: int = 300) -> Task:
        """Wait for task to transition from pending to running."""
        start_time = time.time()

        while task.status == TaskStatus.PENDING:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Task {task.task_id} failed to start within {timeout}s")

            time.sleep(2)
            task = provider.get_task(task.task_id)

            # Check for early failure
            if task.status == TaskStatus.FAILED:
                raise FlowError(f"Task failed to start: {task.message}")

        return task

    def _create_dry_run_task(self, config: TaskConfig, instance: Any) -> Task:
        """Create a mock task for dry run mode."""
        return Task(
            task_id="dry-run-task",
            name=config.name,
            status=TaskStatus.PENDING,
            config=config,
            created_at=datetime.now(timezone.utc),
            instance_type=instance.instance_type,
            num_instances=config.num_instances,
            region=instance.region,
            cost_per_hour=f"${instance.price_per_hour}",
            message="Dry run - no resources allocated",
        )


# ==================== Convenience Functions ====================


def run_task(provider: IProvider, config: TaskConfig, **kwargs) -> Task:
    """Run a task using the default engine.

    Convenience function that creates an engine and runs the task.
    """
    engine = TaskEngine()
    return engine.run_task(provider, config, **kwargs)


def monitor_task(task: Task) -> Generator[TaskProgress, None, None]:
    """Monitor a task using the default engine.

    Convenience function for monitoring.
    """
    engine = TaskEngine()
    return engine.monitor_progress(task)


def wait_for_task(task: Task, timeout: int | None = None) -> Task:
    """Wait for task completion using the default engine.

    Convenience function for waiting.
    """
    engine = TaskEngine()
    return engine.wait_for_completion(task, timeout)
