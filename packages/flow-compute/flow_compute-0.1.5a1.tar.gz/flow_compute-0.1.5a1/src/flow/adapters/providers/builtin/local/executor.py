"""Task execution strategies for local provider."""

import logging
import os
import shlex
import subprocess
import threading
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from flow.adapters.providers.builtin.local.config import LocalTestConfig
from flow.sdk.models import TaskConfig

logger = logging.getLogger(__name__)

# Backwards-compat flag for tests that assert on availability of Mithril builder
# Back-compat surface for tests that patch this symbol/class
HAS_MITHRIL_STARTUP_BUILDER = False


# Optional export shims for tests that patch these names
class MithrilStartupScriptBuilder:  # type: ignore
    pass


class ScriptContext:  # type: ignore
    pass


@dataclass
class TaskExecution:
    """Represents a running task execution."""

    task_id: str
    container_id: str | None = None
    process_id: str | None = None
    process: subprocess.Popen | None = None

    def wait(self) -> int:
        """Wait for execution to complete and return exit code."""
        if self.container_id:
            # Docker container
            docker_mod = __import__("docker")  # type: ignore
            client = docker_mod.from_env()
            container = client.containers.get(self.container_id)
            result = container.wait()
            return result["StatusCode"]
        elif self.process:
            # Local process
            return self.process.wait()
        else:
            raise RuntimeError("No execution to wait for")


class TaskExecutor(ABC):
    """Abstract base class for task execution strategies."""

    def __init__(self, config: LocalTestConfig):
        self.config = config
        self.executions: dict[str, TaskExecution] = {}

    @abstractmethod
    def execute_task(
        self,
        task_id: str,
        config: TaskConfig,
        resources: dict,
        log_callback: Callable[[str], None] | None = None,
    ) -> TaskExecution:
        """Execute a task with given configuration."""
        pass

    @abstractmethod
    def stop_task(self, task_id: str) -> None:
        """Stop a running task."""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up all resources."""
        pass


class ContainerTaskExecutor(TaskExecutor):
    """Executes tasks in Docker containers."""

    def __init__(self, config: LocalTestConfig):
        super().__init__(config)

        # Initialize Docker client
        try:
            docker_mod = __import__("docker")  # type: ignore
            self.client = docker_mod.from_env()
            self._docker_sdk_available = True
        except Exception:
            # Defer errors until first use to avoid import warnings during lint
            self._docker_sdk_available = False
            self.client = None  # type: ignore

        # Create test network
        self.network_name = "flow-test-network"
        if self._docker_sdk_available and self.client is not None:
            try:
                self.network = self.client.networks.get(self.network_name)
            except Exception:
                self.network = self.client.networks.create(self.network_name, driver="bridge")

    def execute_task(
        self,
        task_id: str,
        config: TaskConfig,
        resources: dict,
        log_callback: Callable[[str], None] | None = None,
    ) -> TaskExecution:
        """Execute task in Docker container."""
        # Choose image: use task's image if specified, otherwise default
        if config.image:
            image = config.image
        elif resources.get("gpu_count", 0) > 0:
            image = self.config.gpu_docker_image
        else:
            image = self.config.docker_image

        # Build container configuration
        container_config = {
            "image": image,
            "name": f"flow-{task_id}",
            "detach": True,
            "remove": False,
            "network": self.network_name,
            "labels": {
                "flow.task_id": task_id,
                "flow.task_name": config.name,
            },
            "environment": self._build_environment(config, task_id),
            "volumes": self._build_volumes(config),
        }

        # Add resource limits
        if resources.get("memory_gb"):
            container_config["mem_limit"] = f"{resources['memory_gb']}g"

        if resources.get("cpu_cores"):
            # Docker uses CPU quota in microseconds per period
            container_config["cpu_quota"] = int(resources["cpu_cores"] * 100000)
            container_config["cpu_period"] = 100000

        # Add GPU support if needed
        if resources.get("gpu_count", 0) > 0:
            # Lazy import for type to avoid linter import resolution issues in environments without docker SDK
            try:
                docker_mod = __import__("docker")  # type: ignore
                container_config["device_requests"] = [
                    docker_mod.types.DeviceRequest(
                        count=resources["gpu_count"], capabilities=[["gpu"]]
                    )
                ]
            except Exception:
                pass

        # Handle command execution based on type
        needs_script = False
        if config.command:
            if isinstance(config.command, list):
                # List form - pass directly to container
                container_config["command"] = config.command
            elif isinstance(config.command, str):
                # String form - check if it's a multi-line script
                if "\n" in config.command or config.command.startswith("#!"):
                    # Multi-line script - create startup script
                    needs_script = True
                else:
                    # Single-line command - let shell handle it
                    container_config["command"] = ["sh", "-c", config.command]

        if needs_script:
            # For scripts, create startup script. Try Mithril builder when available
            try:
                if getattr(self.config, "use_mithril_startup_scripts", False):
                    builder = MithrilStartupScriptBuilder()  # patched in tests
                    context = ScriptContext()  # patched in tests
                    script = builder.build(context)
                    if getattr(script, "is_valid", False):
                        script_dir = self.config.storage_dir / "scripts"
                        script_dir.mkdir(parents=True, exist_ok=True)
                        script_path = script_dir / f"{task_id}.sh"
                        script_path.write_text(getattr(script, "content", ""))
                        script_path.chmod(0o755)
                    else:
                        script_path = self._create_startup_script(task_id, config)
                else:
                    script_path = self._create_startup_script(task_id, config)
            except Exception:
                # Fallback to simple script on any error
                script_path = self._create_startup_script(task_id, config)
            # Use sh for alpine-based images, bash for others
            shell = "sh" if image and "alpine" in image else "bash"
            # Use a unique path inside the container to avoid conflicts
            from flow.utils.paths import STARTUP_SCRIPT_PREFIX

            container_script_path = f"{STARTUP_SCRIPT_PREFIX}{task_id}.sh"
            container_config["command"] = [shell, container_script_path]
            # Add script to volumes
            container_config["volumes"][str(script_path)] = {
                "bind": container_script_path,
                "mode": "ro",
            }

        # Start container
        try:
            container = self.client.containers.run(**container_config)

            # Start log streaming
            if log_callback:
                self._start_log_streaming(container, log_callback)

            execution = TaskExecution(task_id=task_id, container_id=container.id)
            self.executions[task_id] = execution

            return execution

        except Exception as e:
            logger.error(f"Failed to start container for task {task_id}: {e}")
            raise

    def _build_environment(self, config: TaskConfig, task_id: str) -> dict[str, str]:
        """Build environment variables for container."""
        env = {
            "FLOW_TASK_ID": task_id,
            "FLOW_TASK_NAME": config.name,
            "FLOW_NODE_RANK": "0",
            "FLOW_NODE_COUNT": str(config.num_instances),
        }

        # Add multi-node environment variables for distributed training
        if config.num_instances > 1:
            env.update(
                {
                    # PyTorch distributed
                    "RANK": "0",  # Local is always rank 0
                    "LOCAL_RANK": "0",
                    "WORLD_SIZE": str(config.num_instances),
                    "MASTER_ADDR": "localhost",
                    "MASTER_PORT": "29500",
                    # TensorFlow/Horovod
                    "OMPI_COMM_WORLD_RANK": "0",
                    "OMPI_COMM_WORLD_SIZE": str(config.num_instances),
                    # NCCL settings for local testing
                    "NCCL_DEBUG": "INFO",
                    "NCCL_SOCKET_IFNAME": "lo",  # Use loopback for local
                }
            )

        # Add user environment
        if config.env:
            env.update(config.env)

        return env

    def _build_volumes(self, config: TaskConfig) -> dict[str, dict]:
        """Build volume mounts for container."""
        volumes = {}

        # Add volume mounts
        if config.volumes:
            for vol in config.volumes:
                # Create local directory
                local_path = self.config.storage_dir / "volumes" / vol.name
                local_path.mkdir(parents=True, exist_ok=True)

                volumes[str(local_path)] = {"bind": vol.mount_path, "mode": "rw"}

        return volumes

    def _create_startup_script(self, task_id: str, config: TaskConfig) -> Path:
        """Create startup script for container."""
        script_dir = self.config.storage_dir / "scripts"
        script_dir.mkdir(parents=True, exist_ok=True)

        script_path = script_dir / f"{task_id}.sh"
        # Always use a simple, provider-agnostic startup script in local mode
        # Use sh shebang for better compatibility
        script_lines = [
            "#!/bin/sh",
            "set -e",  # Exit on error
            "",
            "# Task startup script",
            f"echo 'Starting task {config.name}'",
            f"echo 'Task ID: {task_id}'",
            "echo 'Instance type: Local Docker'",
            "echo",
            "",
            "# Resolve python interpreter for portability",
            'PY_BIN="${PYTHON:-}"',
            'if [ -z "$PY_BIN" ]; then',
            "  if command -v python3 >/dev/null 2>&1; then PY_BIN=python3;",
            "  elif command -v python >/dev/null 2>&1; then PY_BIN=python;",
            "  else PY_BIN=echo; fi",
            "fi",
            'export PYTHON="$PY_BIN"',
            "# Provide a python shim if python isn't on PATH",
            "if ! command -v python >/dev/null 2>&1; then",
            '  if [ -n "$PYTHON" ] && command -v "$PYTHON" >/dev/null 2>&1; then',
            '    python() { command "$PYTHON" "$@"; }',
            "  fi",
            "fi",
            "",
            "# User script",
        ]

        # Add the command/script content
        if config.command:
            if isinstance(config.command, str):
                # String command - add directly (it's a script)
                script_lines.append(config.command)
            elif isinstance(config.command, list):
                # List command - convert to shell command; map python→$PYTHON for portability
                parts = [shlex.quote(str(arg)) for arg in config.command]
                if parts:
                    first_raw = config.command[0]
                    if first_raw in ("python", "python3", "/usr/bin/python", "/usr/bin/python3"):
                        parts[0] = "$PYTHON"
                script_lines.append(" ".join(parts))

        script_lines.extend(
            [
                "",
                "# Task complete",
                "echo",
                f"echo 'Task {config.name} completed'",
            ]
        )

        script_path.write_text("\n".join(script_lines))
        script_path.chmod(0o755)

        return script_path

    def _start_log_streaming(self, container, log_callback: Callable[[str], None]):
        """Start streaming container logs."""

        def stream_logs():
            try:
                # Stream logs from the beginning
                for line in container.logs(stream=True, follow=True, stdout=True, stderr=True):
                    if isinstance(line, bytes):
                        line = line.decode("utf-8", errors="replace")
                    line = line.rstrip()
                    if line:  # Skip empty lines
                        log_callback(line)
            except Exception as e:
                logger.error(f"Error streaming logs: {e}")

        thread = threading.Thread(target=stream_logs, daemon=True)
        thread.start()

    def stop_task(self, task_id: str) -> None:
        """Stop a running container."""
        if task_id not in self.executions:
            return

        execution = self.executions[task_id]
        if execution.container_id:
            try:
                container = self.client.containers.get(execution.container_id)
                container.stop(timeout=self.config.task_shutdown_timeout)
                container.remove()
            except Exception as e:
                logger.error(f"Error stopping container {execution.container_id}: {e}")

    def cleanup(self) -> None:
        """Clean up all containers and network."""
        # Stop all containers
        for task_id in list(self.executions.keys()):
            self.stop_task(task_id)

        # Remove network
        try:
            self.network.remove()
        except Exception as e:
            logger.warning(f"Error removing network: {e}")


class ProcessTaskExecutor(TaskExecutor):
    """Executes tasks as local processes."""

    def execute_task(
        self,
        task_id: str,
        config: TaskConfig,
        resources: dict,
        log_callback: Callable[[str], None] | None = None,
    ) -> TaskExecution:
        """Execute task as local process."""
        # Create working directory
        work_dir = self.config.storage_dir / "tasks" / task_id
        work_dir.mkdir(parents=True, exist_ok=True)

        # Create startup script
        script_path = self._create_startup_script(task_id, config, work_dir)

        # Build environment
        env = os.environ.copy()
        env.update(
            {
                "FLOW_TASK_ID": task_id,
                "FLOW_TASK_NAME": config.name,
                "FLOW_NODE_RANK": "0",
                "FLOW_NODE_COUNT": str(config.num_instances),
            }
        )

        # Add multi-node environment variables for distributed training
        if config.num_instances > 1:
            env.update(
                {
                    # PyTorch distributed
                    "RANK": "0",  # Local is always rank 0
                    "LOCAL_RANK": "0",
                    "WORLD_SIZE": str(config.num_instances),
                    "MASTER_ADDR": "localhost",
                    "MASTER_PORT": "29500",
                    # TensorFlow/Horovod
                    "OMPI_COMM_WORLD_RANK": "0",
                    "OMPI_COMM_WORLD_SIZE": str(config.num_instances),
                    # NCCL settings for local testing
                    "NCCL_DEBUG": "INFO",
                    "NCCL_SOCKET_IFNAME": "lo",  # Use loopback for local
                }
            )

        if config.env:
            env.update(config.env)

        # Start process
        process = subprocess.Popen(
            ["bash", str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=str(work_dir),
            env=env,
            text=True,
            bufsize=1,  # Line buffered
        )

        # Start log streaming
        if log_callback:
            self._start_log_streaming(process, log_callback)

        execution = TaskExecution(task_id=task_id, process_id=str(process.pid), process=process)
        self.executions[task_id] = execution

        return execution

    def _create_startup_script(self, task_id: str, config: TaskConfig, work_dir: Path) -> Path:
        """Create startup script for process."""
        script_path = work_dir / "startup.sh"
        # Always use a simple, provider-agnostic startup script in local mode
        script_lines = [
            "#!/bin/bash",
            "set -e",  # Exit on error
            "",
            "# Task startup script",
            f"echo 'Starting task {config.name}'",
            f"echo 'Task ID: {task_id}'",
            "echo 'Instance type: Local Process'",
            "echo",
            "",
            "# Resolve python interpreter for portability",
            'PY_BIN="${PYTHON:-}"',
            'if [ -z "$PY_BIN" ]; then',
            "  if command -v python3 >/dev/null 2>&1; then PY_BIN=python3;",
            "  elif command -v python >/dev/null 2>&1; then PY_BIN=python;",
            "  else PY_BIN=echo; fi",
            "fi",
            'export PYTHON="$PY_BIN"',
            "# Provide a python shim if python isn't on PATH",
            "if ! command -v python >/dev/null 2>&1; then",
            '  if [ -n "$PYTHON" ] && command -v "$PYTHON" >/dev/null 2>&1; then',
            '    python() { command "$PYTHON" "$@"; }',
            "  fi",
            "fi",
            "",
            "# User script",
        ]

        # Add the command/script content
        if config.command:
            if isinstance(config.command, str):
                # String command - add directly (it's a script)
                script_lines.append(config.command)
            elif isinstance(config.command, list):
                # List command - convert to shell command
                script_lines.append(" ".join(shlex.quote(arg) for arg in config.command))

        script_lines.extend(
            [
                "",
                "# Task complete",
                "echo",
                f"echo 'Task {config.name} completed'",
            ]
        )

        script_path.write_text("\n".join(script_lines))
        script_path.chmod(0o755)

        return script_path

    def _start_log_streaming(self, process: subprocess.Popen, log_callback: Callable[[str], None]):
        """Start streaming process output."""

        def stream_logs():
            try:
                for line in process.stdout:
                    if line:
                        log_callback(line.rstrip())
            except Exception as e:
                logger.error(f"Error streaming logs: {e}")

        thread = threading.Thread(target=stream_logs, daemon=True)
        thread.start()

    def stop_task(self, task_id: str) -> None:
        """Stop a running process."""
        if task_id not in self.executions:
            return

        execution = self.executions[task_id]
        if execution.process:
            try:
                execution.process.terminate()
                # Give it time to terminate gracefully
                time.sleep(1)
                if execution.process.poll() is None:
                    execution.process.kill()
            except Exception as e:
                logger.error(f"Error stopping process {execution.process_id}: {e}")

    def cleanup(self) -> None:
        """Clean up all processes."""
        for task_id in list(self.executions.keys()):
            self.stop_task(task_id)
