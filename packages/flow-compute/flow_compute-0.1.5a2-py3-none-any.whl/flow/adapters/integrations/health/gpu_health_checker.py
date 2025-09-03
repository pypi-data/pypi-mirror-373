"""GPU health checking utilities.

Provides helpers to diagnose GPU monitoring (GPUd) status and to build concise
node health snapshots for display in CLI tools.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import httpx

from flow.sdk.health_models import HealthStatus, NodeHealthSnapshot


class GPUdStatus(Enum):
    """Status of GPUd service on a node."""

    HEALTHY = "healthy"
    LEGACY = "legacy"  # Task predates GPUd integration
    NOT_INSTALLED = "not_installed"  # GPUd not installed (console/manual start)
    STARTING = "starting"  # GPUd is initializing
    FAILED = "failed"  # GPUd should be running but isn't
    UNREACHABLE = "unreachable"  # Cannot reach the node


@dataclass
class GPUdDiagnosis:
    """Result of GPUd status diagnosis."""

    status: GPUdStatus
    reason: str
    details: dict[str, Any] | None = None


class GPUdStatusDiagnoser:
    """Diagnoses the status of GPUd on a node."""

    LEGACY_TASK_AGE_HOURS = 24  # Tasks older than this are considered legacy
    NEW_TASK_AGE_HOURS = 0.1  # Tasks younger than this might still be starting
    HEALTH_CHECK_TIMEOUT = 2  # Seconds to wait for GPUd health check
    GPUD_INTEGRATION_DATE = "2024-07-15"  # Approximate date when GPUd was integrated
    GPUD_STATUS_FILE = "/var/run/flow-gpud-status"  # Marker file location

    def diagnose(
        self,
        api_url: str,
        task_age_hours: float | None,
        *,
        endpoints: list[str] | None = None,
        timeout: int | None = None,
    ) -> GPUdDiagnosis:
        """Diagnose GPUd status with intelligent heuristics.

        Args:
            api_url: GPUd API base URL
            task_age_hours: Age of the task in hours
            endpoints: Ordered list of health probe paths to try (e.g., ["/healthz", "/readyz", "/livez", "/health"]).
            timeout: Seconds to wait for each health probe

        Returns:
            GPUdDiagnosis with status and reason
        """
        # Try health check first
        health_result = self._check_health_endpoint(
            api_url,
            endpoints=endpoints,
            timeout=timeout,
        )

        if health_result == "healthy":
            return GPUdDiagnosis(GPUdStatus.HEALTHY, "GPUd is responding normally")
        elif health_result == "timeout" and self._is_new_task(task_age_hours):
            return GPUdDiagnosis(
                GPUdStatus.STARTING,
                "GPUd may still be initializing",
                {"task_age_hours": task_age_hours},
            )
        elif health_result == "connection_refused":
            # Connection refused means port is reachable but nothing listening
            # This could be: legacy task, manual/console start, or GPUd failed

            if self._is_legacy_task(task_age_hours):
                return GPUdDiagnosis(
                    GPUdStatus.LEGACY,
                    "Task started before GPU monitoring was available",
                    {"task_age_hours": task_age_hours},
                )
            else:
                # For newer tasks, assume GPUd not installed rather than failed
                # This handles console-started instances gracefully
                return GPUdDiagnosis(
                    GPUdStatus.NOT_INSTALLED,
                    "GPUd monitoring not available (instance may have been started manually)",
                    {"task_age_hours": task_age_hours},
                )

        # Default based on task age
        if self._is_legacy_task(task_age_hours):
            return GPUdDiagnosis(
                GPUdStatus.LEGACY,
                "Task likely started before GPU monitoring was available",
                {"task_age_hours": task_age_hours},
            )
        else:
            return GPUdDiagnosis(GPUdStatus.FAILED, "Unable to connect to GPUd service")

    def _check_health_endpoint(
        self, api_url: str, *, endpoints: list[str] | None = None, timeout: int | None = None
    ) -> str:
        """Check GPUd health endpoint(s).

        Tries endpoints in order and returns the first success.

        Returns:
            'healthy', 'timeout', 'connection_refused', or 'error'
        """
        paths = endpoints or ["/healthz", "/health"]
        last_error: str | None = None
        saw_timeout = False
        saw_conn_refused = False
        for path in paths:
            try:
                resp = httpx.get(f"{api_url}{path}", timeout=(timeout or self.HEALTH_CHECK_TIMEOUT))
                if resp.status_code == 200:
                    return "healthy"
                last_error = f"http_{resp.status_code}"
            except httpx.ConnectTimeout:
                saw_timeout = True
                last_error = "timeout"
            except httpx.ConnectError as e:
                if "connection refused" in str(e).lower():
                    saw_conn_refused = True
                    last_error = "connection_refused"
                else:
                    last_error = "conn_error"
            except Exception:
                last_error = "error"

        if saw_timeout:
            return "timeout"
        if saw_conn_refused:
            return "connection_refused"
        return "error"

    def _is_legacy_task(self, task_age_hours: float | None) -> bool:
        """Check if task is old enough to be considered legacy."""
        return task_age_hours is not None and task_age_hours > self.LEGACY_TASK_AGE_HOURS

    def _is_new_task(self, task_age_hours: float | None) -> bool:
        """Check if task is new enough that GPUd might still be starting."""
        return task_age_hours is not None and task_age_hours < self.NEW_TASK_AGE_HOURS

    def check_gpud_marker(self, ssh_command_prefix: list[str]) -> str | None:
        """Check GPUd status marker file via SSH.

        Args:
            ssh_command_prefix: SSH command prefix (without the actual command)

        Returns:
            Status from marker file or None if not found
        """
        import subprocess

        try:
            # Build command to read the marker file
            cmd = ssh_command_prefix + [
                f"cat {self.GPUD_STATUS_FILE} 2>/dev/null || echo 'not_found'"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)  # Short timeout

            if result.returncode == 0:
                status = result.stdout.strip()
                if status and status != "not_found":
                    return status
        except subprocess.TimeoutExpired:
            # SSH is hanging - skip marker check
            return None
        except Exception:
            # Any other error - skip marker check
            return None
        return None


class NodeHealthSnapshotFactory:
    """Factory for creating NodeHealthSnapshot objects for different scenarios."""

    @staticmethod
    def create_legacy_snapshot(task: Any) -> NodeHealthSnapshot:
        """Create snapshot for legacy tasks without GPUd."""
        return NodeHealthSnapshot(
            task_id=task.task_id,
            task_name=task.name or task.task_id,
            instance_id=getattr(task, "instance_id", "unknown"),
            instance_type=task.instance_type or "unknown",
            timestamp=datetime.now(timezone.utc),
            gpud_healthy=False,
            gpud_version=None,
            machine_info={"note": "GPUd not installed - legacy task"},
            gpu_metrics=[],
            system_metrics=None,
            health_score=0.0,
            health_status=HealthStatus.UNKNOWN,
        )

    @staticmethod
    def create_failed_snapshot(task: Any, reason: str) -> NodeHealthSnapshot:
        """Create snapshot for tasks where GPUd failed."""
        return NodeHealthSnapshot(
            task_id=task.task_id,
            task_name=task.name or task.task_id,
            instance_id=getattr(task, "instance_id", "unknown"),
            instance_type=task.instance_type or "unknown",
            timestamp=datetime.now(timezone.utc),
            gpud_healthy=False,
            gpud_version=None,
            machine_info={"error": reason},
            gpu_metrics=[],
            system_metrics=None,
            health_score=0.0,
            health_status=HealthStatus.CRITICAL,
        )

    @staticmethod
    def create_starting_snapshot(task: Any) -> NodeHealthSnapshot:
        """Create snapshot for tasks where GPUd is starting."""
        return NodeHealthSnapshot(
            task_id=task.task_id,
            task_name=task.name or task.task_id,
            instance_id=getattr(task, "instance_id", "unknown"),
            instance_type=task.instance_type or "unknown",
            timestamp=datetime.now(timezone.utc),
            gpud_healthy=False,
            gpud_version=None,
            machine_info={"status": "GPUd service is starting"},
            gpu_metrics=[],
            system_metrics=None,
            health_score=0.5,
            health_status=HealthStatus.UNKNOWN,
        )

    @staticmethod
    def create_not_installed_snapshot(task: Any) -> NodeHealthSnapshot:
        """Create snapshot for tasks where GPUd is not installed."""
        return NodeHealthSnapshot(
            task_id=task.task_id,
            task_name=task.name or task.task_id,
            instance_id=getattr(task, "instance_id", "unknown"),
            instance_type=task.instance_type or "unknown",
            timestamp=datetime.now(timezone.utc),
            gpud_healthy=False,
            gpud_version=None,
            machine_info={"note": "GPUd not installed - manual instance setup"},
            gpu_metrics=[],
            system_metrics=None,
            health_score=0.0,
            health_status=HealthStatus.UNKNOWN,
        )

    @staticmethod
    def create_unreachable_snapshot(task: Any, error: str) -> NodeHealthSnapshot:
        """Create snapshot for unreachable nodes."""
        return NodeHealthSnapshot(
            task_id=task.task_id,
            task_name=task.name or task.task_id,
            instance_id=getattr(task, "instance_id", "unknown"),
            instance_type=task.instance_type or "unknown",
            timestamp=datetime.now(timezone.utc),
            gpud_healthy=False,
            gpud_version=None,
            machine_info={"error": f"Node unreachable: {error}"},
            gpu_metrics=[],
            system_metrics=None,
            health_score=0.0,
            health_status=HealthStatus.CRITICAL,
        )


class HealthCheckMessageHandler:
    """Handles health check messages and issue tracking."""

    def __init__(self, issues: list, warnings: list, successes: list):
        self.issues = issues
        self.warnings = warnings
        self.successes = successes

    def handle_diagnosis(self, diagnosis: GPUdDiagnosis, task_id: str) -> None:
        """Add appropriate messages based on diagnosis."""
        if diagnosis.status == GPUdStatus.LEGACY:
            self.warnings.append(
                {
                    "category": "GPU Health",
                    "message": f"Task {task_id} was started before GPU monitoring was added",
                    "suggestion": "No action needed - this is expected for older tasks",
                }
            )
        elif diagnosis.status == GPUdStatus.NOT_INSTALLED:
            self.warnings.append(
                {
                    "category": "GPU Health",
                    "message": f"Task {task_id} does not have GPU monitoring installed",
                    "suggestion": (
                        "Flow-launched GPU tasks enable GPUd automatically. "
                        "For manual instances, see 'flow health --gpu --help' or relaunch via 'flow run'."
                    ),
                }
            )
        elif diagnosis.status == GPUdStatus.FAILED:
            self.issues.append(
                {
                    "category": "GPU Health",
                    "message": f"GPUd monitoring failed on {task_id}: {diagnosis.reason}",
                    "suggestion": "Check instance logs or restart the task",
                }
            )
        elif diagnosis.status == GPUdStatus.STARTING:
            self.warnings.append(
                {
                    "category": "GPU Health",
                    "message": f"GPUd is still initializing on {task_id}",
                    "suggestion": "Wait a few minutes and try again",
                }
            )
        elif diagnosis.status == GPUdStatus.UNREACHABLE:
            self.issues.append(
                {
                    "category": "GPU Health",
                    "message": f"Cannot reach node for {task_id}: {diagnosis.reason}",
                    "suggestion": "Check if the instance is still running",
                }
            )


class SSHConnectionHandler:
    """Handles SSH connection failures with intelligent error analysis."""

    @staticmethod
    def analyze_ssh_error(error: Exception, task_age_hours: float | None) -> GPUdDiagnosis:
        """Analyze SSH error to determine likely cause.

        Args:
            error: The SSH exception
            task_age_hours: Age of task in hours

        Returns:
            GPUdDiagnosis with appropriate status
        """
        error_str = str(error).lower()

        if "connection refused" in error_str and task_age_hours and task_age_hours > 24:
            return GPUdDiagnosis(
                GPUdStatus.LEGACY, "Task likely started before GPU monitoring was available"
            )
        elif "timeout" in error_str or "no route to host" in error_str:
            return GPUdDiagnosis(GPUdStatus.UNREACHABLE, "Node is not reachable")
        else:
            return GPUdDiagnosis(GPUdStatus.UNREACHABLE, f"SSH connection failed: {error_str}")


class GPUInstanceDetector:
    """Detects if an instance type is GPU-enabled."""

    GPU_IDENTIFIERS = ["gpu", "h100", "a100", "v100", "a10", "t4", "l4", "l40", "p4", "p100"]

    @classmethod
    def is_gpu_instance(cls, instance_type: str | None) -> bool:
        """Check if instance type indicates GPU availability."""
        if not instance_type:
            return False
        return any(gpu in instance_type.lower() for gpu in cls.GPU_IDENTIFIERS)


class TaskAgeCalculator:
    """Calculates task age with proper null handling."""

    @staticmethod
    def get_age_hours(created_at: datetime | None) -> float | None:
        """Calculate task age in hours."""
        if not created_at:
            return None
        try:
            # Ensure both datetimes are timezone-aware
            now = datetime.now(timezone.utc)

            # If created_at is naive (no timezone), assume UTC
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)

            age = now - created_at
            return age.total_seconds() / 3600
        except Exception:
            return None
