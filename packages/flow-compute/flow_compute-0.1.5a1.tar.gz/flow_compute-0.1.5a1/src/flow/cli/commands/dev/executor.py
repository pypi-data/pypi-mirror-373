"""Handles command execution on the dev VM (direct and containerized)."""

import json
import logging
import os
import shlex

from flow.cli.commands.base import console
from flow.cli.commands.dev.models import ContainerInfo, ContainerStatus
from flow.sdk.client import Flow
from flow.sdk.models import Task

logger = logging.getLogger(__name__)


class DevContainerExecutor:
    """Executes commands in containers on the dev VM."""

    def __init__(self, flow_client: Flow, vm_task: Task):
        """Initialize container executor.

        Args:
            flow_client: Flow SDK client
            vm_task: The dev VM task object
        """
        self.flow_client = flow_client
        self.vm_task = vm_task
        self.container_prefix = "flow-dev-exec"

    def execute_command(
        self,
        command: str,
        image: str | None = None,
        interactive: bool = False,
        env_name: str = "default",
    ) -> int:
        """Execute command on the dev VM.

        Default environment runs directly on VM (no containers).
        Named environments use containers for isolation.

        Args:
            command: Command to execute
            image: Docker image to use (forces container for default env)
            interactive: Whether to run interactively
            env_name: Named environment (default: "default")

        Returns:
            Exit code of the command
        """
        try:
            remote_ops = self.flow_client.get_remote_operations()
        except (AttributeError, NotImplementedError):
            console.print("[error]Error: Provider doesn't support remote operations[/error]")
            return 1

        if env_name == "default" and not image:
            return self._execute_direct(command, interactive, remote_ops)
        else:
            return self._execute_containerized(command, image, interactive, env_name, remote_ops)

    def _execute_direct(self, command: str, interactive: bool, remote_ops) -> int:
        logger.info(f"Executing directly on VM: {command[:50]}...")

        if interactive:
            try:
                remote_ops.open_shell(self.vm_task.task_id, command=command)
                return 0
            except Exception as e:
                from rich.markup import escape

                console.print(f"[error]Error: {escape(str(e))}[/error]")
                return 1
        else:
            try:
                from flow.errors import RemoteExecutionError

                output = remote_ops.execute_command(self.vm_task.task_id, command)
                if output:
                    console.print(output, end="")
                return 0
            except RemoteExecutionError as e:
                from rich.markup import escape

                console.print(f"[error]Command failed: {escape(str(e))}[/error]")
                return 1
            except Exception as e:
                from rich.markup import escape

                console.print(f"[error]Error: {escape(str(e))}[/error]")
                return 1

    def _execute_containerized(
        self, command: str, image: str | None, interactive: bool, env_name: str, remote_ops
    ) -> int:
        from flow.cli.utils.name_generator import generate_unique_name
        from flow.utils.paths import DEV_ENVS_ROOT, DEV_HOME_DIR, WORKSPACE_DIR

        container_name = generate_unique_name(
            prefix=self.container_prefix, base_name=None, add_unique=True
        )

        # Default image
        if not image:
            image = os.environ.get("FLOW_DEV_CONTAINER_IMAGE", "ubuntu:22.04")

        env_dir = f"{DEV_ENVS_ROOT}/{env_name}"
        setup_env_cmd = f"mkdir -p {env_dir}"
        try:
            remote_ops.execute_command(self.vm_task.task_id, setup_env_cmd)
        except Exception:
            pass

        docker_args: list[str] = [
            "docker",
            "run",
            "--rm",
            "--name",
            container_name,
            "-v",
            f"{env_dir}:{WORKSPACE_DIR}",
            "-v",
            f"{DEV_HOME_DIR}:/shared:ro",
            "-w",
            WORKSPACE_DIR,
            "-e",
            f"HOME={WORKSPACE_DIR}",
            "--pull",
            "missing",
        ]

        docker_args.extend(
            [
                "-e",
                "FLOW_DEV_CONTAINER=true",
                "-e",
                f"FLOW_DEV_USER={os.environ.get('USER', 'default')}",
            ]
        )

        # Add GPU support if NVIDIA runtime is available
        try:
            gpu_runtime_check = "docker info --format '{{json .Runtimes}}' | grep -q nvidia"
            remote_ops.execute_command(self.vm_task.task_id, gpu_runtime_check)
            docker_args.extend(["--gpus", "all"])
        except Exception:
            pass

        if interactive:
            docker_args.extend(["-it"])

        docker_args.append(image)
        docker_args.extend(["bash", "-lc", command])

        docker_cmd = " ".join(shlex.quote(arg) for arg in docker_args)

        if interactive:
            try:
                remote_ops.open_shell(self.vm_task.task_id, command=docker_cmd)
                return 0
            except Exception as e:
                from rich.markup import escape

                console.print(f"[error]Error: {escape(str(e))}[/error]")
                return 1
        else:
            try:
                from flow.errors import RemoteExecutionError

                # Ensure image availability
                logger.debug(f"Checking Docker image availability: {image}")
                try:
                    pull_output = remote_ops.execute_command(
                        self.vm_task.task_id,
                        f"docker image inspect {image} >/dev/null 2>&1 || docker pull {image}",
                    )
                    if pull_output and "Pulling from" in pull_output:
                        console.print(f"Pulling Docker image: {image}")
                        logger.info(f"Pulling Docker image: {image}")
                except RemoteExecutionError as e:
                    logger.debug(f"Image pull failed (may use cache): {e}")
                    pass

                logger.info(f"Executing container command: {command[:50]}...")
                output = remote_ops.execute_command(self.vm_task.task_id, docker_cmd)
                if output:
                    console.print(output, end="")
                logger.debug("Command executed successfully")
                return 0
            except RemoteExecutionError as e:
                error_msg = str(e)
                if "unable to find image" in error_msg.lower():
                    console.print(
                        f"[error]Docker image '{image}' not found and could not be pulled[/error]"
                    )
                    console.print(
                        "[warning]Tip: Check image name or ensure internet connectivity on the dev VM[/warning]"
                    )
                elif "docker: command not found" in error_msg.lower():
                    console.print("[error]Docker is not installed on the dev VM[/error]")
                    console.print(
                        "[warning]Tip: SSH into the VM and install Docker first[/warning]"
                    )
                else:
                    from rich.markup import escape

                    console.print(f"[error]Command failed: {escape(str(e))}[/error]")
                return 1
            except Exception as e:
                from rich.markup import escape

                console.print(f"[error]Error: {escape(str(e))}[/error]")
                return 1

    def reset_containers(self) -> None:
        try:
            remote_ops = self.flow_client.get_remote_operations()
        except (AttributeError, NotImplementedError):
            try:
                from flow.cli.ui.runtime.mode import is_demo_active

                if is_demo_active():
                    console.print(
                        "Demo mode: container reset requires remote access which isn't supported by the mock provider."
                    )
                else:
                    console.print(
                        "[error]Error: Provider doesn't support remote operations[/error]"
                    )
            except Exception:
                console.print("[error]Error: Provider doesn't support remote operations[/error]")
            return

        cleanup_commands = [
            f"docker ps -q -f name={self.container_prefix} | xargs -r docker stop",
            f"docker ps -a -q -f name={self.container_prefix} | xargs -r docker rm -f",
        ]

        for cmd in cleanup_commands:
            try:
                from flow.errors import RemoteExecutionError

                remote_ops.execute_command(self.vm_task.task_id, cmd)
            except RemoteExecutionError as e:
                if "requires at least 1 argument" not in str(e):
                    from rich.markup import escape

                    console.print(f"[warning]Warning during cleanup: {escape(str(e))}[/warning]")
            except Exception as e:
                from rich.markup import escape

                console.print(f"[warning]Warning during cleanup: {escape(str(e))}[/warning]")

    def get_container_status(self) -> ContainerStatus:
        try:
            remote_ops = self.flow_client.get_remote_operations()
        except (AttributeError, NotImplementedError):
            return {"active_containers": 0, "containers": []}

        list_cmd = f"docker ps -f name={self.container_prefix} --format '{{{{json .}}}}'"

        try:
            from flow.errors import RemoteExecutionError

            output = remote_ops.execute_command(self.vm_task.task_id, list_cmd)

            containers: list[ContainerInfo] = []
            if output:
                for line in output.strip().split("\n"):
                    if line:
                        try:
                            containers.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass

            return {"active_containers": len(containers), "containers": containers}
        except RemoteExecutionError:
            return {"active_containers": 0, "containers": []}
        except Exception:
            return {"active_containers": 0, "containers": []}
