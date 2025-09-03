"""SSH command for connecting to running GPU instances.

Provides secure shell access to running tasks for debugging and development.

Examples:
    Connect interactively:
        $ flow ssh task-abc123

    Execute remote command (two supported forms):
        $ flow ssh task-abc123 -c 'nvidia-smi'
        $ flow ssh task-abc123 -- nvidia-smi

    Check GPU utilization:
        $ flow ssh task-abc123 -c 'watch -n1 nvidia-smi'
"""

import os
import shlex
from contextlib import suppress

import click

from flow.cli.commands.base import BaseCommand, console
from flow.cli.ui.formatters import TaskFormatter
from flow.cli.utils.error_handling import cli_error_guard
from flow.cli.utils.task_selector_mixin import TaskFilter, TaskOperationCommand
from flow.errors import FlowError
from flow.plugins import registry as plugin_registry

# Back-compat: expose Flow for tests that patch flow.cli.commands.ssh.Flow
from flow.sdk.client import Flow as Flow
from flow.sdk.models import Task


class SSHCommand(BaseCommand, TaskOperationCommand):
    """SSH command implementation.

    Handles both interactive sessions and remote command execution.
    Requires task to be in running state with SSH keys configured.
    """

    def __init__(self):
        """Initialize command with formatter."""
        super().__init__()
        self.task_formatter = TaskFormatter()

    @property
    def name(self) -> str:
        return "ssh"

    @property
    def manages_own_progress(self) -> bool:
        """SSH manages its own progress display."""
        return True

    @property
    def help(self) -> str:
        return """SSH to running GPU instances - Interactive shell or remote command execution

Quick connect:
  flow ssh                         # Interactive task selector
  flow ssh my-training             # Connect by task name
  flow ssh abc-123                 # Connect by task ID

Remote commands:
  flow ssh task -c 'nvidia-smi'    # Check GPU status
  flow ssh task -- nvidia-smi      # Alternate syntax using '--'
  flow ssh task -c 'htop'          # Monitor system resources
  flow ssh task --node 1           # Connect to specific node (multi-instance)"""

    # TaskSelectorMixin implementation
    def get_task_filter(self):
        """Show running tasks; SSH may still be provisioning.

        We purposely allow tasks without an SSH endpoint yet so users can
        select a running task and the command will wait for SSH readiness.
        """
        return TaskFilter.running_only

    def get_selection_title(self) -> str:
        return "Select a running task to SSH into"

    def get_no_tasks_message(self) -> str:
        return "No running tasks available for SSH"

    # Command execution
    def execute_on_task(self, task: Task, client, **kwargs) -> None:
        """Execute SSH connection on the selected task with a unified timeline."""
        command = kwargs.get("command")
        node = kwargs.get("node", 0)
        record = kwargs.get("record", False)

        # Validate node parameter for multi-instance tasks (shared helper)
        from flow.cli.utils.task_utils import validate_node_index

        validate_node_index(task, node)
        task_display = (
            f"{self.task_formatter.format_task_display(task)} [node {node}]"
            if getattr(task, "num_instances", 1) > 1
            else self.task_formatter.format_task_display(task)
        )

        # Pre-check: if provider lacks remote ops, show guidance and exit
        try:
            _ = client.get_remote_operations()
        except (AttributeError, NotImplementedError):
            from flow.cli.utils.provider_support import print_provider_not_supported

            print_provider_not_supported(
                "remote operations",
                tips=[
                    "Try again after switching provider: [accent]flow init --provider mithril[/accent]",
                    "Open a shell via the provider UI if available",
                ],
            )
            return

        # Best-effort: ensure a default SSH key exists to avoid waiting on instances
        # that will never expose SSH due to missing keys (non-fatal if unsupported)
        with suppress(Exception):
            provider = getattr(client, "provider", None)
            if provider and hasattr(provider, "ensure_default_ssh_key"):
                # Prefer Flow wrapper; fallback to provider if necessary
                try:
                    _ = client.ensure_default_ssh_key()
                except Exception:
                    try:
                        provider.ensure_default_ssh_key()
                    except Exception:
                        pass

        # Unified timeline
        from flow.cli.utils.step_progress import SSHWaitProgressAdapter, StepTimeline

        timeline = StepTimeline(console, title="flow ssh", title_animation="auto")
        timeline.start()

        # Step 1: Ensure SSH readiness if needed (skip when FAST mode is enabled)
        try:
            from flow.application.config.runtime import settings as _settings  # local import

            fast_mode = bool((_settings.ssh or {}).get("fast", False))
        except Exception:
            fast_mode = os.environ.get("FLOW_SSH_FAST") == "1"
        if not fast_mode and not task.ssh_host:
            from flow.sdk.ssh_utils import DEFAULT_PROVISION_MINUTES, SSHNotReadyError

            # Seed bar from existing instance age so resume after Ctrl+C is realistic
            try:
                baseline = int(getattr(task, "instance_age_seconds", 0) or 0)
            except (TypeError, ValueError):
                baseline = 0
            step_idx = timeline.add_step(
                f"Provisioning instance (up to {DEFAULT_PROVISION_MINUTES}m)",
                show_bar=True,
                estimated_seconds=DEFAULT_PROVISION_MINUTES * 60,
                baseline_elapsed_seconds=baseline,
            )
            adapter = SSHWaitProgressAdapter(
                timeline,
                step_idx,
                DEFAULT_PROVISION_MINUTES * 60,
                baseline_elapsed_seconds=baseline,
            )
            try:
                with adapter:
                    # Provide a concise, clear hint and context (standardized)
                    from flow.cli.utils.step_progress import build_provisioning_hint as _bph

                    timeline.set_active_hint_text(_bph("instance", "flow ssh"))
                    task = client.wait_for_ssh(
                        task_id=task.task_id,
                        timeout=DEFAULT_PROVISION_MINUTES * 60,  # standard wait for SSH
                        show_progress=False,
                        progress_adapter=adapter,
                    )
            except SSHNotReadyError as e:
                timeline.fail_step(str(e))
                timeline.finish()
                raise SystemExit(1)

        # Refresh task to ensure we have the freshest SSH endpoint/user right before connect
        with suppress(FlowError):
            task = client.get_task(task.task_id)
        # Now we have an up-to-date view, update display
        task_display = self.task_formatter.format_task_display(task)

        # Fresh-resolve endpoint via provider resolver to avoid any stale Task views
        try:
            host, port = client.resolve_ssh_endpoint(task.task_id, node=node)
            task.ssh_host = host
            task.ssh_port = int(port or 22)
        except (FlowError, ValueError, AttributeError):
            # Best-effort; remote operations will still resolve before connecting
            pass

        # Optional: brief handshake wait when host is known but SSH may not yet accept connections
        # This smooths over the common window where providers surface the host early but sshd isn't ready.
        if not fast_mode and getattr(task, "ssh_host", None):
            # Resolve SSH key path via provider to probe readiness accurately
            with suppress(FlowError):
                ssh_key_path, _err = client.get_task_ssh_connection_info(task.task_id)
                if ssh_key_path:
                    import time as _t

                    from flow.cli.utils.ssh_helpers import SshStack as _S

                    handshake_seconds = 90  # conservative short wait; avoids premature failures
                    step_idx = timeline.add_step(
                        "Establishing SSH session",
                        show_bar=True,
                        estimated_seconds=handshake_seconds,
                    )
                    adapter = SSHWaitProgressAdapter(timeline, step_idx, handshake_seconds)
                    with adapter:
                        start_wait = _t.time()
                        while not _S.is_ssh_ready(
                            user=getattr(task, "ssh_user", "ubuntu"),
                            host=task.ssh_host,
                            port=getattr(task, "ssh_port", 22),
                            key_path=ssh_key_path,
                        ):
                            if _t.time() - start_wait > handshake_seconds:
                                break
                            # Non-critical: ETA update can fail silently
                            with suppress(Exception):
                                adapter.update_eta()
                            _t.sleep(2)

        # Step 2: Connect or execute
        try:
            if command:
                # Close the timeline before emitting remote output to avoid Live collisions
                step_idx = timeline.add_step("Executing remote command", show_bar=False)
                timeline.start_step(step_idx)
                timeline.complete_step()
                timeline.finish()
                client.shell(
                    task.task_id, command=command, node=node, progress_context=None, record=record
                )
            else:
                # Close the timeline before handing terminal control to SSH to prevent overlay
                timeline.finish()
                client.shell(task.task_id, node=node, progress_context=None, record=record)
        except Exception as e:
            # Show manual connection hint once
            provider_name = (
                getattr(getattr(client, "config", None), "provider", None)
                or os.environ.get("FLOW_PROVIDER")
                or "mithril"
            )
            connection_cmd = None
            with suppress(Exception):  # best-effort formatting from provider
                ProviderClass = plugin_registry.get_provider(provider_name)
                if ProviderClass and hasattr(ProviderClass, "format_connection_hint"):
                    connection_cmd = ProviderClass.format_connection_hint(task)
            if connection_cmd:
                from flow.cli.utils.theme_manager import theme_manager as _tm_warn

                warn = _tm_warn.get_color("warning")
                console.print(
                    f"\n[{warn}]Connection failed. You can try connecting manually with:[/{warn}]"
                )
                console.print(f"  {connection_cmd}\n")
            # If the error carries a request/correlation ID, include it in the failure line
            req_id = getattr(e, "request_id", None)
            if req_id:
                timeline.fail_step(f"{e!s}\nRequest ID: {req_id}")
            else:
                timeline.fail_step(str(e))
            timeline.finish()
            raise

        # Show next actions after SSH session ends
        if not command:  # Only show after interactive sessions
            task_ref = task.name or task.task_id
            self.show_next_actions(
                [
                    f"View logs: [accent]flow logs {task_ref} --follow[/accent]",
                    f"Check status: [accent]flow status {task_ref}[/accent]",
                    f"Run nvidia-smi: [accent]flow ssh {task_ref} -c 'nvidia-smi'[/accent]",
                ]
            )
        # Finish timeline
        timeline.finish()

    def get_command(self) -> click.Command:
        # Import completion function
        # from flow.cli.utils.mode import demo_aware_command
        from flow.cli.ui.runtime.shell_completion import complete_task_ids

        @click.command(name=self.name, help=self.help)
        @click.argument("task_identifier", required=False, shell_complete=complete_task_ids)
        @click.option(
            "--command",
            "-c",
            help="Command to run on remote host (deprecated; prefer trailing command after --)",
            hidden=True,
        )
        @click.option(
            "--node", type=int, default=0, help="Node index for multi-instance tasks (default: 0)"
        )
        @click.option("--verbose", "-v", is_flag=True, help="Show detailed help and examples")
        @click.option(
            "--json", "output_json", is_flag=True, help="Output connection parameters as JSON"
        )
        @click.option(
            "--record",
            is_flag=True,
            help="Record session to host logs (viewable with flow logs --source host)",
        )
        # @demo_aware_command()
        @click.argument("remote_cmd", nargs=-1)
        @cli_error_guard(self)
        def ssh(
            task_identifier: str | None,
            command: str | None,
            node: int,
            verbose: bool,
            record: bool,
            remote_cmd: tuple[str, ...],
            output_json: bool,
        ):
            """SSH to a running task.

            TASK_IDENTIFIER: Task ID or name (optional - interactive selector if omitted)

            \b
            Examples:
                flow ssh                    # Interactive task selector
                flow ssh my-training        # Connect by name
                flow ssh task-abc123        # Connect by ID
                flow ssh task -c 'nvidia-smi'           # Run command remotely (flag)
                flow ssh task -- nvidia-smi             # Run command remotely (after --)

            Use 'flow ssh --verbose' for troubleshooting and advanced examples.
            """
            if verbose:
                console.print("\n[bold]Advanced SSH Usage:[/bold]\n")
                console.print("Multi-instance tasks:")
                console.print("  flow ssh distributed-job --node 1    # Connect to worker node")
                console.print(
                    "  flow ssh task -c 'hostname' --node 2 # Run command on specific node\n"
                )

                console.print("File transfer:")
                console.print("  scp file.py $(flow ssh task -c 'echo $USER@$HOSTNAME'):~/")
                console.print(
                    "  rsync -av ./data/ $(flow ssh task -c 'echo $USER@$HOSTNAME'):/data/\n"
                )

                console.print("Port forwarding:")
                console.print(
                    "  ssh -L 8888:localhost:8888 $(flow ssh task -c 'echo $USER@$HOSTNAME')"
                )
                console.print(
                    "  ssh -L 6006:localhost:6006 $(flow ssh task -c 'echo $USER@$HOSTNAME')  # TensorBoard\n"
                )

                console.print("Monitoring:")
                console.print("  flow ssh task -c 'watch -n1 nvidia-smi'    # GPU usage")
                console.print("  flow ssh task -c 'htop'                     # System resources")
                console.print("  flow ssh task -c 'tail -f output.log'       # Stream logs\n")

                console.print("Troubleshooting:")
                console.print("  • No SSH info? Wait 2-5 minutes for instance provisioning")
                console.print("  • Permission denied? Run: flow ssh-keys upload ~/.ssh/id_rsa.pub")
                console.print("  • Connection refused? Check: flow health --task <name>")
                console.print("  • Task terminated? Check: flow status <name>\n")
                return

            # If a trailing command was provided after '--', prefer it over -c
            # but guard against both being set to avoid ambiguity.
            if remote_cmd:
                if command:
                    from flow.cli.utils.theme_manager import theme_manager as _tm_err3

                    err_color = _tm_err3.get_color("error")
                    console.print(
                        f"[{err_color}]Specify either -c/--command or a trailing command after '--', not both[/{err_color}]"
                    )
                    return
                # Reconstruct the remote command string with safe quoting
                command = shlex.join(remote_cmd)

            # Selection support (works after 'flow status')
            if task_identifier:
                from flow.cli.utils.selection_helpers import parse_selection_to_task_ids

                ids, err = parse_selection_to_task_ids(task_identifier)
                if err:
                    from flow.cli.utils.theme_manager import theme_manager as _tm_err

                    err_color = _tm_err.get_color("error")
                    console.print(f"[{err_color}]{err}[/{err_color}]")
                    return
                if ids is not None:
                    if len(ids) != 1:
                        from flow.cli.utils.theme_manager import theme_manager as _tm_err2

                        err_color = _tm_err2.get_color("error")
                        console.print(
                            f"[{err_color}]Selection must resolve to exactly one task for ssh[/{err_color}]"
                        )
                        return
                    task_identifier = ids[0]

            # JSON mode requires a concrete task identifier to avoid interactive selector output
            if output_json:
                if not task_identifier:
                    from flow.cli.utils.json_output import error_json, print_json

                    print_json(
                        error_json(
                            "--json requires a task identifier (id or name)",
                            hint="Usage: flow ssh <task> --json",
                        )
                    )
                    return
                # Selection grammar: allow indices (works after 'flow status')
                from flow.cli.utils.selection_helpers import parse_selection_to_task_ids as _parse

                ids, err = _parse(task_identifier)
                if err:
                    from flow.cli.utils.theme_manager import theme_manager as _tm_err

                    err_color = _tm_err.get_color("error")
                    console.print(f"[{err_color}]{err}[/{err_color}]")
                    return
                if ids is not None:
                    if len(ids) != 1:
                        from flow.cli.utils.theme_manager import theme_manager as _tm_err2

                        err_color = _tm_err2.get_color("error")
                        console.print(
                            f"[{err_color}]Selection must resolve to exactly one task for ssh[/{err_color}]"
                        )
                        return
                    task_identifier = ids[0]

                # Resolve and emit connection parameters
                from flow.cli.utils.json_output import print_json
                from flow.sdk.factory import create_client as _create

                client = _create(auto_init=True)
                task = client.get_task(task_identifier)
                # Try to resolve endpoint, fallback to task fields
                try:
                    host, port = client.resolve_ssh_endpoint(task.task_id, node=node)
                except Exception:
                    host = getattr(task, "ssh_host", None)
                    port = int(getattr(task, "ssh_port", 22) or 22)
                user = getattr(task, "ssh_user", "ubuntu")
                key_path = None
                try:
                    key_path, _err = client.get_task_ssh_connection_info(task.task_id)
                except Exception:
                    key_path = None
                cmd = (
                    f"ssh -p {port} {user}@{host}"
                    if not key_path
                    else f"ssh -i {key_path} -p {port} {user}@{host}"
                )
                print_json(
                    {
                        "user": user,
                        "host": host,
                        "port": port,
                        "key_path": str(key_path) if key_path else None,
                        "ssh_command": cmd,
                        "task_id": task.task_id,
                        "task_name": getattr(task, "name", None),
                        "node": node,
                    }
                )
                return

            self._execute(task_identifier, command, node, record)

        return ssh

    def _execute(
        self, task_identifier: str | None, command: str | None, node: int = 0, record: bool = False
    ) -> None:
        """Execute SSH connection or command."""
        # For non-interactive commands, use standard flow
        if command:
            self.execute_with_selection(task_identifier, command=command, node=node, record=record)
            return

        # Delegate to selection without pre-animations; the timeline inside execute_on_task owns the UX
        self.execute_with_selection(
            task_identifier,
            command=command,
            node=node,
            record=record,
        )


# Export command instance
command = SSHCommand()
