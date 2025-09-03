"""Programmatic access to the persistent dev VM used by the CLI.

Enables fast iteration by executing commands in containers on a long-lived VM.

Examples:
    Start or connect, then run a command:
        >>> vm = flow.dev.start(instance_type="a100")
        >>> flow.dev.exec("python -V")

    Context manager (auto-stop):
        >>> with flow.dev_context(auto_stop=True) as dev:
        ...     dev.exec("python train.py")
"""

import logging
import time
from typing import Any, TypedDict

from flow.cli.commands.dev import DevContainerExecutor, DevVMManager
from flow.errors import DevContainerError, DevVMNotFoundError, DevVMStartupError, NetworkError
from flow.sdk.models import Task

logger = logging.getLogger(__name__)


class ContainerInfo(TypedDict):
    """Docker container information."""

    Names: str
    Status: str
    Image: str
    Command: str
    CreatedAt: str
    ID: str


class DevEnvironmentStatus(TypedDict):
    """Development environment status information."""

    vm: dict[str, Any] | None  # VM info dictionary
    active_containers: int
    containers: list[ContainerInfo]


class ImprovedDevContainerExecutor(DevContainerExecutor):
    """Container executor with clearer error mapping."""

    def execute_command(self, command: str, image: str = None, interactive: bool = False) -> int:
        """Execute a command with improved error handling."""
        try:
            # Get remote operations using clean interface
            remote_ops = self.flow_client.get_remote_operations()
        except (AttributeError, NotImplementedError) as e:
            raise DevContainerError(
                "Provider doesn't support remote operations required for dev containers", cause=e
            )

        try:
            return super().execute_command(command, image, interactive)
        except Exception as e:
            # Convert generic exceptions to specific dev errors
            error_msg = str(e)

            if "unable to find image" in error_msg.lower():
                raise DevContainerError(
                    f"Docker image '{image or 'default'}' not found",
                    command=command,
                    image=image,
                    cause=e,
                )
            elif "docker: command not found" in error_msg.lower():
                raise DevContainerError(
                    "Docker is not installed on the dev VM", command=command, cause=e
                )
            elif "connection refused" in error_msg.lower():
                raise DevContainerError(
                    "Cannot connect to Docker daemon on dev VM", command=command, cause=e
                )
            else:
                raise DevContainerError(
                    f"Container execution failed: {error_msg}",
                    command=command,
                    image=image,
                    cause=e,
                )


class DevSDK:
    """Compatibility shim around `DevEnvironment` (kept for tests)."""

    def __init__(self, flow_client: Any, auto_stop: bool = False) -> None:
        self._impl = DevEnvironment(flow_client, auto_stop=auto_stop)

    def get_or_create_vm(self, *args, **kwargs) -> Task:
        return self._impl.ensure_started(*args, **kwargs)

    def run_in_container(
        self, command: str, image: str | None = None, interactive: bool = False
    ) -> dict[str, Any]:
        exit_code = self._impl.exec(command, image=image, interactive=interactive)
        return {"exit_code": exit_code, "output": None}

    @property
    def env(self) -> "DevEnvironment":
        return self._impl


class DevEnvironment:
    """High-level API for managing the dev VM (start, exec, status, stop)."""

    def __init__(self, flow_client, auto_stop: bool = False):
        """Initialize the dev environment manager."""
        self._flow = flow_client
        self._vm_manager = DevVMManager(flow_client)
        self._current_vm = None
        self._executor = None
        self._auto_stop = auto_stop
        self._context_started = False

    def start(
        self,
        instance_type: str | None = None,
        ssh_keys: list | None = None,
        max_price_per_hour: float | None = None,
        docker_image: str | None = None,
        force_new: bool = False,
    ) -> Task:
        """Start a dev VM or connect if one already exists."""
        # Stop existing VM if force_new
        if force_new:
            existing_vm = self._vm_manager.find_dev_vm()
            if existing_vm:
                logger.info("Force stopping existing dev VM")
                self._vm_manager.stop_dev_vm()

        # Find or create VM
        vm = self._vm_manager.find_dev_vm()
        if not vm:
            logger.info("Creating new dev VM")
            vm = self._vm_manager.create_dev_vm(
                instance_type=instance_type,
                ssh_keys=ssh_keys,
                max_price_per_hour=max_price_per_hour,
                image=docker_image,
            )

            # Wait for VM to be ready
            self._wait_for_ready(vm)
        else:
            logger.info(f"Using existing dev VM: {vm.name}")

        self._current_vm = vm
        self._executor = ImprovedDevContainerExecutor(self._flow, vm)
        return vm

    def ensure_started(
        self,
        instance_type: str | None = None,
        ssh_keys: list | None = None,
        max_price_per_hour: float | None = None,
    ) -> Task:
        """Ensure a dev VM is running; start one if needed."""
        vm = self._vm_manager.find_dev_vm()
        if vm:
            logger.info(f"Using existing dev VM: {vm.name}")
            self._current_vm = vm
            self._executor = DevContainerExecutor(self._flow, vm)
            return vm

        # No existing VM, create new one
        return self.start(
            instance_type=instance_type, ssh_keys=ssh_keys, max_price_per_hour=max_price_per_hour
        )

    def _ensure_vm(self) -> Task:
        """Return the current dev VM or raise if none is running."""
        if self._current_vm:
            return self._current_vm

        vm = self._vm_manager.find_dev_vm()
        if not vm:
            raise DevVMNotFoundError()

        self._current_vm = vm
        self._executor = ImprovedDevContainerExecutor(self._flow, vm)
        return vm

    def connect(self, command: str | None = None) -> None:
        """Open an SSH session to the dev VM (or run a one-off command)."""
        vm = self._ensure_vm()
        self._flow.shell(vm.task_id, command=command)

    def run(
        self,
        command: str | None = None,
        image: str | None = None,
        instance_type: str | None = None,
        **kwargs,
    ) -> int | Task:
        """If `command` is set, run it in a container; otherwise open SSH."""
        # Ensure VM is running
        vm = self.ensure_started(instance_type=instance_type, **kwargs)

        if command:
            # Execute command in container
            return self.exec(command, image=image)
        else:
            # Connect interactively
            self.connect()
            return vm

    def exec(
        self, command: str, image: str | None = None, interactive: bool = False, retries: int = 1
    ) -> int:
        """Run a containerized command on the dev VM and return its exit code."""
        self._ensure_vm()

        last_error = None
        for attempt in range(max(1, retries)):
            try:
                return self._executor.execute_command(command, image=image, interactive=interactive)
            except (NetworkError, DevContainerError) as e:
                last_error = e

                # Don't retry certain errors
                if interactive:
                    raise  # Interactive commands shouldn't retry

                error_msg = str(e).lower()
                if any(
                    msg in error_msg
                    for msg in [
                        "docker: command not found",
                        "docker is not installed",
                        "no dev vm running",
                    ]
                ):
                    raise  # These won't be fixed by retry

                if attempt < retries - 1:
                    logger.warning(
                        f"Container execution failed (attempt {attempt + 1}/{retries}): {e}"
                    )
                    time.sleep(2**attempt)  # Exponential backoff: 1s, 2s, 4s
                else:
                    raise

        # This should never be reached, but just in case
        if last_error:
            raise last_error

    def reset(self) -> None:
        """Stop/remove dev containers and clean images; keep the VM running."""
        self._ensure_vm()
        self._executor.reset_containers()
        logger.info("Dev containers reset successfully")

    def stop(self) -> bool:
        """Terminate the dev VM and all containers. Returns True if stopped."""
        stopped = self._vm_manager.stop_dev_vm()
        if stopped:
            self._current_vm = None
            self._executor = None
            logger.info("Dev VM stopped successfully")
        return stopped

    def status(self) -> DevEnvironmentStatus:
        """Return VM and container status for the dev environment."""
        vm = self._vm_manager.find_dev_vm()

        if not vm:
            return {"vm": None, "active_containers": 0, "containers": []}

        # Build VM info
        vm_info = {
            "name": vm.name,
            "id": vm.task_id,
            "instance_type": vm.instance_type,
            "status": "running",
        }

        # Calculate uptime if available
        if vm.started_at:
            from datetime import datetime, timezone

            uptime = datetime.now(timezone.utc) - vm.started_at
            vm_info["uptime_hours"] = round(uptime.total_seconds() / 3600, 2)

        # Get container status
        container_status = {"active_containers": 0, "containers": []}
        try:
            executor = DevContainerExecutor(self._flow, vm)
            container_status = executor.get_container_status()
        except Exception as e:
            logger.debug(f"Could not fetch container status: {e}")

        return {
            "vm": vm_info,
            "active_containers": container_status["active_containers"],
            "containers": container_status["containers"],
        }

    def _wait_for_vm(self, vm: Task) -> None:
        """Wait until the VM is ready for use (including SSH readiness)."""
        from flow.cli.commands.utils import wait_for_task

        # Wait for running status
        final_status = wait_for_task(self._flow, vm.task_id, watch=False)

        if final_status != "running":
            # Try to get more details about the failure
            error_msg = None
            try:
                task = self._flow.get_task(vm.task_id)
                if hasattr(task, "message") and task.message:
                    error_msg = task.message
            except:
                pass

            raise DevVMStartupError(
                message=error_msg, instance_type=getattr(vm, "instance_type", None)
            )

        # Wait for SSH readiness if needed
        if not vm.ssh_host:
            from flow.sdk.ssh_utils import wait_for_task_ssh_info

            # Ensure provider is initialized (use public accessor)
            provider = self._flow.provider
            if provider:
                try:
                    vm = wait_for_task_ssh_info(
                        task=vm, provider=provider, timeout=1200, show_progress=False
                    )
                except Exception as e:
                    logger.warning(f"SSH info wait failed: {e}")

        # Give SSH a moment to initialize
        time.sleep(2)

    # Backward-compatibility alias expected by some tests
    def _wait_for_ready(self, vm: Task) -> None:  # pragma: no cover - simple alias
        self._wait_for_vm(vm)

    def __enter__(self) -> "DevEnvironment":
        """Enter context manager, ensuring a VM is running."""
        self._context_started = True
        self.ensure_started()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Exit context manager and optionally stop the VM."""
        if self._auto_stop and self._current_vm:
            try:
                self.stop()
            except Exception as e:
                logger.warning(f"Failed to auto-stop dev VM: {e}")

        self._context_started = False
        return False  # Don't suppress exceptions
