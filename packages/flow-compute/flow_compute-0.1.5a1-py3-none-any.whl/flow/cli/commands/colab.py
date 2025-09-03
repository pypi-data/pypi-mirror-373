"""Colab command group - Run Google Colab UI with Flow GPU runtime.

This command group wires up Google's "Connect to local runtime" to a Flow GPU
instance by launching a localhost-bound Jupyter server on the instance and
printing the SSH port-forward command and tokenized URL to paste into Colab.

Subcommands:
    flow colab up      # Launch a new Colab-ready instance
    flow colab list    # List running Colab-ready tasks
    flow colab url     # Print the Colab URL for a task (parses token from logs)
    flow colab down    # Stop a Colab task
    flow colab tunnel  # Print or run SSH port-forward (foreground)

Examples:
    # Launch an A100-backed runtime and get URL + SSH instructions
    flow colab up a100 --hours 4

    # List sessions and fetch URL for one
    flow colab list
    flow colab url my-colab

    # Start a foreground SSH tunnel (-N -L) until Ctrl+C
    flow colab tunnel my-colab
"""

from __future__ import annotations

import json
import logging
import os
import re
import shlex
import socket
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qs, urlparse, urlunparse

import click

from flow import DEFAULT_ALLOCATION_ESTIMATED_SECONDS
from flow.cli.commands.base import BaseCommand, console
from flow.cli.ui.formatters import TaskFormatter
from flow.cli.ui.presentation.animated_progress import AnimatedEllipsisProgress
from flow.cli.ui.runtime.shell_completion import complete_task_ids
from flow.cli.utils.step_progress import (
    AllocationProgressAdapter,
    SSHWaitProgressAdapter,
    StepTimeline,
)
from flow.cli.utils.task_resolver import resolve_task_identifier
from flow.errors import AuthenticationError, FlowError
from flow.sdk.client import Flow
from flow.sdk.factory import create_client
from flow.sdk.models import Task, TaskStatus

# Lazy import to avoid heavy deps at CLI import time


def _get_colab_integration(flow_client: Flow):
    from flow.sdk.colab import GoogleColabIntegration

    return GoogleColabIntegration(flow_client)


def _extract_token_from_logs(flow_client: Flow, task_id: str) -> str | None:
    """Legacy fallback: try to locate token from any printed URL or token=… snippet.

    Avoids printing tokens; use only when metadata/control channel isn't available.
    """
    try:
        logs = flow_client.tasks.logs(task_id, tail=400)
    except Exception:
        return None
    # Prefer full URL parsing first
    for m in re.finditer(r"http://[^\s]+", logs):
        try:
            u = urlparse(m.group(0))
            qs = parse_qs(u.query)
            token = qs.get("token", [None])[0]
            if token:
                return token
        except Exception:
            pass
    # Then look for token=… substring
    m2 = re.search(r"token=([A-Za-z0-9\-._~]+)", logs)
    return m2.group(1) if m2 else None


def _build_ssh_tunnel_command(
    task: Task, local_port: int = 8888, remote_port: int = 8888
) -> str | None:
    if not task.ssh_host or not task.ssh_user:
        return None
    return (
        f"ssh -N "
        f"-o ExitOnForwardFailure=yes "
        f"-o ServerAliveInterval=60 -o ServerAliveCountMax=2 "
        f"-L {local_port}:localhost:{remote_port} "
        f"{task.ssh_user}@{task.ssh_host}"
    )


def _pick_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _set_url_port(url: str, port: int) -> str:
    u = urlparse(url)
    host = u.hostname or "localhost"
    # Preserve auth if any
    auth = ""
    if u.username:
        auth = u.username
        if u.password:
            auth += f":{u.password}"
        auth += "@"
    netloc = f"{auth}{host}:{port}"
    return urlunparse(u._replace(netloc=netloc))


# Simple local store for tokenized URLs keyed by task_id (avoid log-scraping)
_LOCAL_STORE_PATH = Path.home() / ".flow" / "colab_local_runtime.json"


def _load_local_store() -> dict:
    try:
        if _LOCAL_STORE_PATH.exists():
            return json.loads(_LOCAL_STORE_PATH.read_text() or "{}")
    except Exception:
        pass
    return {}


def _save_local_store(data: dict) -> None:
    try:
        import os

        _LOCAL_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(_LOCAL_STORE_PATH, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def _persist_connection(task_id: str, token: str, base_url: str, remote_port: int) -> None:
    store = _load_local_store()
    store[task_id] = {
        "token": token,
        "base_url": base_url,
        "remote_port": remote_port,
    }
    _save_local_store(store)


def _get_persisted(task_id: str) -> dict | None:
    return _load_local_store().get(task_id)


def _gc_local_store(flow_client: Flow) -> None:
    """Garbage-collect stale entries from the local colab store.

    Removes tokens for tasks that are no longer running/pending or not found.
    """
    store = _load_local_store()
    if not store:
        return
    changed = False
    for task_id in list(store.keys()):
        try:
            task = flow_client.get_task(task_id)
            if task.status not in {TaskStatus.RUNNING, TaskStatus.PENDING}:
                del store[task_id]
                changed = True
        except Exception:
            # Not found or inaccessible – remove
            del store[task_id]
            changed = True
    if changed:
        _save_local_store(store)


def _fetch_token_via_remote(flow_client: Flow, task_id: str) -> str | None:
    try:
        remote_ops = flow_client.get_remote_operations()
        cmd = (
            "awk -F\"'\" '/^c.NotebookApp.token/ {print $2}' ~/.jupyter/jupyter_notebook_config.py"
        )
        token_output = remote_ops.execute_command(task_id, cmd)
        token = (token_output or "").strip()
        return token or None
    except (AttributeError, NotImplementedError):
        # No remote access in this provider (e.g., demo/mock)
        return None
    except Exception:
        return None


@dataclass
class ColabSessionInfo:
    task: Task
    url: str | None
    tunnel_cmd: str | None


class ColabCommand(BaseCommand):
    """Manage Colab local-runtime sessions backed by Flow instances."""

    def __init__(self) -> None:
        super().__init__()
        self.task_formatter = TaskFormatter()

    @property
    def name(self) -> str:
        return "colab"

    @property
    def help(self) -> str:
        return "Use Google Colab UI with Flow GPU runtime (local runtime)"

    def get_command(self) -> click.Group:
        @click.group(name=self.name, help=self.help)
        @click.option(
            "--verbose", "verbose", is_flag=True, help="Show integration details and tips"
        )
        @click.pass_context
        def colab(ctx, verbose: bool):
            if verbose:
                console.print("\n[bold]Colab Local Runtime with Flow[/bold]\n")
                console.print(
                    "This connects Colab's UI to a Jupyter server running on your GPU instance."
                )
                console.print(
                    "Security: server binds to 127.0.0.1 on the instance; you tunnel via SSH.\n"
                )
            # Initialize a single client for this group invocation
            try:
                ctx.ensure_object(dict)
                if (ctx.obj or {}).get("flow_client") is None:
                    ctx.obj["flow_client"] = create_client(auto_init=True)
            except AuthenticationError:
                ctx.ensure_object(dict)
                ctx.obj["flow_client"] = None

        colab.add_command(self._up())
        colab.add_command(self._list())
        colab.add_command(self._url())
        colab.add_command(self._down())
        colab.add_command(self._tunnel())
        return colab

    # --- Subcommands ---
    def _up(self) -> click.Command:
        @click.command(name="up")
        @click.argument("instance_type", required=False)
        @click.option(
            "--hours",
            type=float,
            default=None,
            help="Max runtime hours (omit for no limit)",
            show_default=False,
        )
        @click.option("--name", "name", help="Optional task name (default: colab-<type>-<ts>)")
        @click.option(
            "--local-port",
            type=int,
            default=8888,
            show_default=True,
            help="Local port for SSH -L forward (0 = auto)",
        )
        @click.option(
            "--workspace/--no-workspace",
            default=True,
            show_default=True,
            help="Attach a persistent workspace volume at /workspace",
        )
        @click.option(
            "--workspace-size",
            type=int,
            default=50,
            show_default=True,
            help="Workspace volume size in GB (when --workspace)",
        )
        @click.option(
            "--workspace-name",
            type=str,
            help="Optional workspace volume name (reuse to persist across sessions)",
        )
        @click.pass_context
        def up(
            ctx,
            instance_type: str | None,
            hours: float | None,
            name: str | None,
            local_port: int,
            workspace: bool,
            workspace_size: int,
            workspace_name: str | None,
        ):
            """Launch a Colab-ready instance and print connection details."""
            try:
                flow_client = (
                    (ctx.obj or {}).get("flow_client") if getattr(ctx, "obj", None) else None
                )
                flow_client = flow_client or create_client(auto_init=True)
            except AuthenticationError:
                self.handle_auth_error()
                return

            try:
                # Determine default instance type when not provided
                if not instance_type:
                    instance_type = (
                        os.environ.get("FLOW_COLAB_INSTANCE_TYPE")
                        or os.environ.get("FLOW_DEFAULT_INSTANCE_TYPE")
                        or "h100"
                    )
                # Launch via internal integration (Jupyter on host)
                # Use the same provisioning UX as dev
                integration = _get_colab_integration(flow_client)
                # Submit and then wait with shared progress UI
                from flow.sdk.models import TaskConfig

                cfg = TaskConfig(
                    name=name or f"colab-{instance_type}",
                    unique_name=False,
                    instance_type=instance_type,
                    command=["bash", "-c", integration.JUPYTER_STARTUP_SCRIPT],
                    upload_code=False,
                    upload_strategy="none",
                    image="",
                    env={"FLOW_HEALTH_MONITORING": "false"},
                    max_run_time_hours=hours,
                    priority="high",
                )
                if workspace and workspace_size > 0:
                    vol_name = integration._sanitize_volume_name(
                        workspace_name or f"colab-ws-{instance_type}"
                    )
                    from flow.sdk.models import VolumeSpec

                    cfg.volumes = [
                        VolumeSpec(name=vol_name, size_gb=workspace_size, mount_path="/workspace")
                    ]

                # Pre-select a region to keep volumes and task in the same region
                # This avoids creating a volume in a region different from where the task runs
                try:
                    instances = flow_client.find_instances(
                        {"instance_type": instance_type}, limit=20
                    )
                    if instances:
                        # Prefer highest availability, then lowest price
                        def _avail(i):
                            return i.available_quantity if i.available_quantity is not None else 0

                        instances.sort(key=lambda i: (-_avail(i), i.price_per_hour))
                        cfg.region = instances[0].region
                except Exception:
                    # If pre-selection fails, let provider choose and fallback logic will handle mismatch
                    pass

                # Temporarily silence noisy 5xx retry warnings during provisioning
                http_logger = logging.getLogger("flow.adapters.http.client")
                prev_level = http_logger.level
                http_logger.setLevel(logging.ERROR)
                try:
                    # Unified timeline for submission → allocation → SSH
                    timeline = StepTimeline(console, title="flow colab", title_animation="auto")
                    timeline.start()
                    # Real provider safety guard (interactive only)
                    try:
                        from flow.cli.utils.real_provider_guard import ensure_real_provider_ack

                        if not ensure_real_provider_ack(
                            instance_type=instance_type,
                            priority=None,
                            max_price_per_hour=None,
                            num_instances=1,
                            auto_confirm=False,
                        ):
                            timeline.finish()
                            return
                    except Exception:
                        pass
                    submit_idx = timeline.add_step(
                        f"Submitting {instance_type} request", show_bar=False
                    )
                    timeline.start_step(submit_idx)
                    task = flow_client.run(cfg)
                    timeline.complete_step()

                    # Allocation
                    from flow.cli.commands.utils import wait_for_task

                    alloc_idx = timeline.add_step(
                        "Allocating instance",
                        show_bar=True,
                        estimated_seconds=DEFAULT_ALLOCATION_ESTIMATED_SECONDS,
                    )
                    alloc = AllocationProgressAdapter(
                        timeline, alloc_idx, estimated_seconds=DEFAULT_ALLOCATION_ESTIMATED_SECONDS
                    )
                    with alloc:
                        # Add standardized allocation hint during wait
                        try:
                            from flow.cli.utils.step_progress import (
                                build_allocation_hint as _bah,
                            )

                            timeline.set_active_hint_text(_bah("flow colab", subject="allocation"))
                        except Exception:
                            pass
                        final_status = wait_for_task(
                            flow_client,
                            task.task_id,
                            watch=False,
                            task_name=task.name,
                            progress_adapter=alloc,
                        )
                    if final_status != "running":
                        timeline.fail_step(f"Status: {final_status}")
                        timeline.finish()
                        raise FlowError(f"Failed to start instance (status: {final_status})")

                    # SSH readiness
                    from flow.sdk.ssh_utils import DEFAULT_PROVISION_MINUTES

                    baseline = 0
                    try:
                        baseline = int(getattr(task, "instance_age_seconds", None) or 0)
                    except Exception:
                        baseline = 0
                    ssh_idx = timeline.add_step(
                        f"Provisioning instance (up to {DEFAULT_PROVISION_MINUTES}m)",
                        show_bar=True,
                        estimated_seconds=DEFAULT_PROVISION_MINUTES * 60,
                        baseline_elapsed_seconds=baseline,
                    )
                    ssh = SSHWaitProgressAdapter(
                        timeline,
                        ssh_idx,
                        DEFAULT_PROVISION_MINUTES * 60,
                        baseline_elapsed_seconds=baseline,
                    )
                    with ssh:
                        # Add clear, standardized provisioning hint
                        try:
                            from flow.cli.utils.step_progress import (
                                build_provisioning_hint as _bph,
                            )

                            timeline.set_active_hint_text(_bph("instance", "flow colab"))
                        except Exception:
                            pass
                        task = flow_client.wait_for_ssh(
                            task_id=task.task_id,
                            timeout=DEFAULT_PROVISION_MINUTES * 60 * 2,
                            show_progress=False,
                            progress_adapter=ssh,
                        )
                    timeline.finish()
                except Exception as submit_err:
                    # If workspace volume creation fails, retry without workspace
                    if workspace and getattr(cfg, "volumes", None):
                        # Strip volumes and retry cleanly
                        cfg.volumes = []
                        try:
                            # Show a quick retry submission spinner as well
                            with AnimatedEllipsisProgress(
                                console,
                                message="Retrying submission (no workspace)",
                                start_immediately=True,
                                transient=True,
                                show_progress_bar=False,
                            ):
                                task = flow_client.run(cfg)
                            from flow.cli.commands.utils import wait_for_task

                            final_status = wait_for_task(
                                flow_client, task.task_id, watch=False, task_name=task.name
                            )
                            if final_status != "running":
                                raise FlowError(
                                    f"Failed to start instance (status: {final_status})"
                                )
                            from flow.sdk.ssh_utils import DEFAULT_PROVISION_MINUTES

                            try:
                                from flow.cli.ui.presentation.animated_progress import (
                                    AnimatedEllipsisProgress,
                                )

                                class _SimpleSSHAdapter:
                                    def update_eta(self, eta: str | None = None) -> None:
                                        return None

                                with AnimatedEllipsisProgress(
                                    console,
                                    message="Provisioning instance",
                                    start_immediately=True,
                                    transient=True,
                                ):
                                    task = flow_client.wait_for_ssh(
                                        task_id=task.task_id,
                                        timeout=DEFAULT_PROVISION_MINUTES * 60 * 2,
                                        show_progress=False,
                                        progress_adapter=_SimpleSSHAdapter(),
                                    )
                            except Exception:
                                task = flow_client.wait_for_ssh(
                                    task_id=task.task_id,
                                    timeout=DEFAULT_PROVISION_MINUTES * 60 * 2,
                                    show_progress=False,
                                )
                            # Soft, non-alarming note after successful retry
                            console.print(
                                "[dim]Note: Workspace volume couldn’t be provisioned quickly; continuing without workspace (files are ephemeral).[/dim]"
                            )
                        except Exception:
                            # Re-raise original error if retry also fails
                            raise submit_err
                    else:
                        raise
                finally:
                    http_logger.setLevel(prev_level)

                # Once SSH is ready, connect
                connection = integration._wait_for_instance_ready(
                    task, session_id=f"colab-{task.task_id[:6]}", quiet=True
                )

                # Fetch task to build SSH cmd
                task = flow_client.get_task(connection.task_id)
                # Auto-pick a free local port if requested
                if local_port == 0:
                    local_port = _pick_free_port()
                tunnel_cmd = _build_ssh_tunnel_command(
                    task,
                    local_port=local_port,
                    remote_port=getattr(connection, "remote_port", 8888),
                )

                console.print("\n[success]✓[/success] Instance ready for Colab")
                if tunnel_cmd:
                    console.print("\n[bold]SSH tunnel (run on your laptop):[/bold]")
                    console.print(f"  {tunnel_cmd}")
                console.print(
                    "\n[bold]Colab connection URL (paste in Colab → Connect to local runtime…):[/bold]"
                )
                # Persist connection details locally for future url/tunnel retrieval without logs
                try:
                    # Try to extract token from connection URL query param
                    parsed = urlparse(connection.connection_url)
                    qs = dict(p.split("=", 1) for p in parsed.query.split("&") if "=" in p)
                    token = qs.get("token", "")
                    if token:
                        _persist_connection(
                            task.task_id,
                            token=token,
                            base_url=f"{parsed.scheme}://{parsed.hostname or 'localhost'}:{getattr(connection, 'remote_port', 8888)}",
                            remote_port=getattr(connection, "remote_port", 8888),
                        )
                except Exception:
                    pass

                # Show URL using chosen local_port
                url = _set_url_port(connection.connection_url, local_port)
                console.print(f"  {url}")

                # Workspace guidance
                if workspace:
                    console.print(
                        "\n[dim]Workspace mounted at /workspace. Notebooks will persist at /workspace/notebooks.[/dim]"
                    )
                else:
                    console.print(
                        "\n[warning]No workspace volume attached. Files will be ephemeral unless you download or push them.[/warning]"
                    )

                # Next steps
                self.show_next_actions(
                    [
                        "Open Colab: colab.research.google.com",
                        "Click: Connect → Connect to local runtime…",
                        "Paste the URL above (with token)",
                        "Verify GPU: run !nvidia-smi in a Colab cell",
                    ]
                )
            except FlowError as e:
                self.handle_error(e)
            except Exception as e:
                self.handle_error(str(e))

        return up

    def _list(self) -> click.Command:
        @click.command(name="list")
        @click.option("--local-port", type=int, default=8888, show_default=True)
        @click.pass_context
        def _list_cmd(ctx, local_port: int):
            """List likely Colab-ready tasks (heuristic)."""
            try:
                flow_client = (
                    (ctx.obj or {}).get("flow_client") if getattr(ctx, "obj", None) else None
                )
                flow_client = flow_client or create_client(auto_init=True)
            except AuthenticationError:
                self.handle_auth_error()
                return

            # Clean up stale local entries quietly
            try:
                _gc_local_store(flow_client)
            except Exception:
                pass

            with AnimatedEllipsisProgress(console, "Fetching tasks"):
                tasks = flow_client.tasks.list(limit=200)

            # Heuristic: name starts with colab- OR logs mention JUPYTER_READY/JUPYTER_TOKEN
            candidates: list[ColabSessionInfo] = []
            for task in tasks:
                if task.status not in {TaskStatus.RUNNING, TaskStatus.PENDING}:
                    continue
                is_colab_name = (task.name or "").startswith("colab-")
                persisted = _get_persisted(task.task_id)
                url = None
                tunnel_cmd = None
                if persisted and persisted.get("token"):
                    token = persisted["token"]
                    remote_port = int(persisted.get("remote_port", 8888))
                    url = f"http://localhost:{local_port}/?token={token}"
                    tunnel_cmd = _build_ssh_tunnel_command(
                        task, local_port=local_port, remote_port=remote_port
                    )
                else:
                    # Legacy fallback only if we detect a colab-* name
                    token = (
                        _extract_token_from_logs(flow_client, task.task_id)
                        if is_colab_name
                        else None
                    )
                    url = f"http://localhost:{local_port}/?token={token}" if token else None
                    tunnel_cmd = _build_ssh_tunnel_command(task, local_port=local_port)
                if is_colab_name or token:
                    candidates.append(ColabSessionInfo(task=task, url=url, tunnel_cmd=tunnel_cmd))

            if not candidates:
                console.print("No Colab-ready tasks found.")
                self.show_next_actions(["Launch one: flow colab up a100"])
                return

            console.print("")
            for info in candidates:
                label = self.task_formatter.format_task_display(info.task)
                console.print(f"• {label}")
                if info.tunnel_cmd:
                    console.print(f"   tunnel: {info.tunnel_cmd}")
                if info.url:
                    console.print(f"   url:    {info.url}")

        return _list_cmd

    def _url(self) -> click.Command:
        @click.command(name="url")
        @click.argument("task_identifier", required=True, shell_complete=complete_task_ids)
        @click.option("--local-port", type=int, default=8888, show_default=True)
        @click.pass_context
        def url(ctx, task_identifier: str, local_port: int):
            """Print the Colab connection URL for a running task."""
            try:
                flow_client = (
                    (ctx.obj or {}).get("flow_client") if getattr(ctx, "obj", None) else None
                )
                flow_client = flow_client or create_client(auto_init=True)
            except AuthenticationError:
                self.handle_auth_error()
                return

            # Clean old entries
            try:
                _gc_local_store(flow_client)
            except Exception:
                pass

            task, error = resolve_task_identifier(flow_client, task_identifier)
            if error:
                console.print(f"[error]Error:[/error] {error}")
                return

            # Prefer local persisted token; fallback to remote fetch; last resort: logs
            token: str | None = None
            persisted = _get_persisted(task.task_id)
            if persisted and persisted.get("token"):
                token = persisted["token"]
            if not token:
                token = _fetch_token_via_remote(flow_client, task.task_id)
            if not token:
                token = _extract_token_from_logs(flow_client, task.task_id)
            if not token:
                console.print("Token not yet available; retry in ~15–30s.")
                return
            console.print(f"http://localhost:{local_port}/?token={token}")

        return url

    def _down(self) -> click.Command:
        @click.command(name="down")
        @click.argument("task_identifier", required=True, shell_complete=complete_task_ids)
        @click.pass_context
        def down(ctx, task_identifier: str):
            """Stop a Colab task."""
            try:
                flow_client = (
                    (ctx.obj or {}).get("flow_client") if getattr(ctx, "obj", None) else None
                )
                flow_client = flow_client or create_client(auto_init=True)
            except AuthenticationError:
                self.handle_auth_error()
                return

            task, error = resolve_task_identifier(flow_client, task_identifier)
            if error:
                console.print(f"[error]Error:[/error] {error}")
                return

            with AnimatedEllipsisProgress(console, f"Stopping {task.name or task.task_id}"):
                flow_client.stop(task.task_id)
            console.print("[success]✓[/success] Stopped")

        return down

    def _tunnel(self) -> click.Command:
        @click.command(name="tunnel")
        @click.argument("task_identifier", required=True, shell_complete=complete_task_ids)
        @click.option(
            "--local-port", type=int, default=8888, show_default=True, help="Local port (0 = auto)"
        )
        @click.option("--print-only", is_flag=True, help="Only print SSH command; do not execute")
        @click.pass_context
        def tunnel(ctx, task_identifier: str, local_port: int, print_only: bool):
            """Start or print the SSH port-forward command (-N -L)."""
            try:
                flow_client = (
                    (ctx.obj or {}).get("flow_client") if getattr(ctx, "obj", None) else None
                )
                flow_client = flow_client or create_client(auto_init=True)
            except AuthenticationError:
                self.handle_auth_error()
                return

            task, error = resolve_task_identifier(flow_client, task_identifier)
            if error:
                console.print(f"[error]Error:[/error] {error}")
                return

            # Auto-pick local port if requested
            if local_port == 0:
                local_port = _pick_free_port()
            # Try to infer remote port from persisted data or by querying remote file
            remote_port = 8888
            try:
                persisted = _get_persisted(task.task_id)
                if persisted and persisted.get("remote_port"):
                    remote_port = int(persisted["remote_port"]) or 8888
                else:
                    # Query remote port file (best-effort)
                    try:
                        remote_ops = flow_client.get_remote_operations()
                        port_output = remote_ops.execute_command(
                            task.task_id, "cat ~/.jupyter/colab_port || true"
                        )
                        port_str = (port_output or "").strip()
                        if port_str.isdigit():
                            remote_port = int(port_str)
                    except Exception:
                        pass
            except Exception:
                pass
            ssh_cmd = _build_ssh_tunnel_command(
                task, local_port=local_port, remote_port=remote_port
            )
            if not ssh_cmd:
                console.print("SSH not ready yet; wait for provisioning.")
                return

            if print_only:
                console.print(ssh_cmd)
                return

            # Execute foreground; user can Ctrl+C to stop
            import subprocess

            console.print("Starting SSH tunnel. Press Ctrl+C to stop…")
            try:
                subprocess.run(shlex.split(ssh_cmd), check=False)
            except KeyboardInterrupt:
                pass

        return tunnel


# Export command instance
command = ColabCommand()
