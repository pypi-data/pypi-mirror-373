from __future__ import annotations

import hashlib
import re
import shlex
import socket
import subprocess
from pathlib import Path
from typing import Any, TypedDict

import click
from rich.text import Text

from flow.cli.commands.base import BaseCommand, console
from flow.cli.commands.input_types import (
    PortNumber,
    PortsExpr,
    merge_ports_expr,
    parse_ports_expression,
    validate_ports_range,
)
from flow.cli.ui.runtime.shell_completion import complete_task_ids
from flow.cli.utils.error_handling import cli_error_guard
from flow.cli.utils.preview_enrichment import get_preview_details
from flow.cli.utils.remote_ops_runner import RemoteOpsRunner
from flow.cli.utils.step_progress import StepTimeline
from flow.cli.utils.task_resolver import resolve_task_identifier
from flow.sdk.client import Flow
from flow.sdk.factory import create_client

# =============================================================================
# Configuration
# =============================================================================

# Default path used historically; actual path will be discovered remotely
FOUNDRYPF_BIN = "/usr/local/bin/foundrypf"
SYSTEMD_TEMPLATE_PATH = "/etc/systemd/system/foundrypf@.service"

# Standardized timeouts (seconds)
DISCOVER_TIMEOUT = 10
OPEN_CLOSE_CMD_TIMEOUT = 120
VERIFY_LIST_TIMEOUT = 30
SYSTEMD_RELOAD_TIMEOUT = 60


def _build_systemd_unit_template(foundrypf_path: str) -> str:
    return f"""[Unit]
Description=Foundry Port Forwarding %i
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
ExecStart={foundrypf_path} %i
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
""".rstrip()


# =============================================================================
# Utilities
# =============================================================================


class PortInfo(TypedDict):
    port: int
    service_name: str
    status: str  # 'active', 'failed', 'dead', 'inactive', 'activating', etc.


def _parse_ports_expression(expression: str) -> list[int]:
    """Deprecated: use parse_ports_expression from input_types."""
    return parse_ports_expression(expression)


def _safe_remote_ops(flow_client: Flow):
    """
    Return remote ops or print an elegant hint and return None.
    """
    try:
        provider = flow_client.provider
        remote_ops = provider.get_remote_operations() if provider else None
    except (AttributeError, NotImplementedError):
        remote_ops = None

    if remote_ops:
        return remote_ops

    try:
        from flow.cli.utils.provider_support import print_provider_not_supported as _ppns

        _ppns(
            "remote operations (required for ports)",
            tips=[
                "Switch provider: [accent]flow init --provider mithril[/accent]",
                "Use SSH port-forwarding as a fallback: [accent]ssh -L local:localhost:remote ...[/accent]",
            ],
        )
    except Exception:
        console.print(
            "[error]Error:[/error] Provider does not support remote operations required for ports"
        )
    return None


def _interactive_task_selection(flow_client: Flow, title: str) -> Any | None:
    """
    Provides a standardized interactive selector for active tasks (UX).
    Returns the selected item (not necessarily a Task).
    """
    from rich.markup import escape as _escape

    from flow.cli.ui.components import select_task
    from flow.cli.utils.status_utils import is_active_like
    from flow.cli.utils.task_fetcher import TaskFetcher

    fetcher = TaskFetcher(flow_client)
    # Show AEP while fetching tasks to avoid perceived hang
    try:
        from flow.cli.ui.presentation.animated_progress import (
            AnimatedEllipsisProgress as _AEP,
        )
    except Exception:
        _AEP = None  # type: ignore

    if _AEP:
        with _AEP(console, "Loading tasks", start_immediately=True):
            tasks = [t for t in fetcher.fetch_for_resolution(limit=1000) if is_active_like(t)]
    else:
        tasks = [t for t in fetcher.fetch_for_resolution(limit=1000) if is_active_like(t)]

    if not tasks:
        console.print("[warning]No eligible active tasks available.[/warning]")
        return None

    def _fast_preview(item):
        try:
            t = getattr(item, "value", None)
            title = _escape(getattr(t, "name", None) or getattr(item, "title", "Task"))
            lines = [f"<b>{title}</b>"]
            lines.append(f"ID: {_escape(getattr(item, 'id', '') or getattr(t, 'task_id', ''))}")
            if getattr(item, "status", None):
                try:
                    status_str = str(item.status).replace("TaskStatus.", "").capitalize()
                    lines.append(f"Status: {status_str}")
                except Exception:
                    pass
            try:
                it = getattr(t, "instance_type", None) or (getattr(item, "extra", {}) or {}).get(
                    "instance_type"
                )
                ni = int(getattr(t, "num_instances", 1) or 1)
                if it:
                    from flow.cli.ui.formatters import GPUFormatter as _GF

                    lines.append(f"GPU: {_GF.format_ultra_compact(it, ni)}")
            except Exception:
                pass
            try:
                region = (getattr(item, "extra", {}) or {}).get("region") or getattr(
                    t, "region", None
                )
                if region:
                    lines.append(f"Region: {region}")
            except Exception:
                pass

            # Lazy enrichment: SSH + key + mounts (non-blocking)
            try:
                details = get_preview_details(flow_client, t)
            except Exception:
                details = None
            if details:
                try:
                    host = details.get("ssh_host")
                    user = details.get("ssh_user") or "ubuntu"
                    port = int(details.get("ssh_port") or 22)
                    if host:
                        lines.append(f"SSH: {user}@{host}:{port}")
                except Exception:
                    pass
                try:
                    kp = details.get("ssh_key_path")
                    if kp:
                        name = Path(kp).name
                        fp = details.get("ssh_key_fp")
                        fp_short = f" ({fp[:11]}…)" if fp else ""
                        lines.append(f"Key: {name}{fp_short}")
                except Exception:
                    pass
                try:
                    mounts = details.get("mounts") or []
                    if mounts:

                        def _m_label(m):
                            return (
                                m.get("target") or m.get("name") or m.get("mountPoint") or ""
                            ).strip()

                        shown = [x for x in (_m_label(m) for m in mounts[:2]) if x]
                        more = len(mounts) - len(shown)
                        if shown:
                            suffix = f" (+{more} more)" if more > 0 else ""
                            lines.append(f"Volumes: {', '.join(shown)}{suffix}")
                except Exception:
                    pass
            # If details are not yet cached, avoid showing a noisy placeholder.
            # The UI will refresh when details arrive.
            return "\n".join(lines)
        except Exception:
            return ""

    selected = select_task(
        tasks,
        title=title,
        allow_multiple=False,
        show_preview=True,
        preferred_viewport_size=8,
        preview_renderer=_fast_preview,
    )
    return selected


def _resolve_task(
    flow_client: Flow, task_identifier: str | None, task_option: str | None, interactive_title: str
):
    """
    Resolve to a real Task object regardless of whether the user passed an id or used the selector.
    Returns (task, error_str_or_None).
    """
    final_tid = task_option or task_identifier
    if not final_tid:
        selected = _interactive_task_selection(flow_client, interactive_title)
        if not selected:
            return None, "No task selected"
        final_tid = getattr(selected, "task_id", None) or getattr(selected, "id", None)
        if not final_tid:
            return None, "Could not determine task id from selection"

    # Show a brief AEP while resolving identifiers to improve UX
    try:
        from flow.cli.ui.presentation.animated_progress import (
            AnimatedEllipsisProgress as _AEP,
        )
    except Exception:
        _AEP = None  # type: ignore

    if _AEP:
        with _AEP(console, "Looking up task", start_immediately=True):
            task, error = resolve_task_identifier(flow_client, final_tid)
    else:
        task, error = resolve_task_identifier(flow_client, final_tid)
    return task, error


# =============================================================================
# RemotePortManager (SRP)
# =============================================================================


class RemotePortManager:
    """
    Manages port forwarding (foundrypf) and persistence (systemd) on a remote task instance.
    Isolates low-level remote execution details from the CLI logic.
    """

    def __init__(self, remote_ops: Any, task_id: str):
        self.remote_ops = remote_ops
        self.task_id = task_id
        self.runner = RemoteOpsRunner(remote_ops, task_id)
        # Will be set during preflight; fallback to default
        self.foundrypf_bin: str = FOUNDRYPF_BIN
        self.foundrypf_version: str | None = None

    def _execute(self, command: str, timeout: int = 60) -> str:
        return self.runner.run(command, timeout=timeout)

    # ---------- Preflight ----------

    def ensure_prereqs(self, persist: bool) -> bool:
        """
        Verify required binaries are present on the remote.
        """
        # Discover foundrypf (prefer PATH, then common absolute locations)
        extra_paths = [
            "/usr/local/bin/foundrypf",
            "/usr/bin/foundrypf",
            "/usr/local/sbin/foundrypf",
            "/usr/sbin/foundrypf",
            "/opt/bin/foundrypf",
            "/opt/foundry/bin/foundrypf",
        ]
        out = self.runner.discover_binary(
            "foundrypf", extra_paths=extra_paths, timeout=DISCOVER_TIMEOUT
        )
        if not out:
            console.print(
                "[error]Error:[/error] foundrypf not found on the task instance. "
                "Checked PATH and common locations (/usr/local/bin, /usr/bin, /usr/local/sbin, /usr/sbin, /opt/bin). "
                "Install it on the instance or contact your administrator."
            )
            return False
        # Capture discovered path for subsequent commands and templates
        self.foundrypf_bin = out.strip()
        # Try to capture version for diagnostics (best-effort)
        try:
            ver_out = self._execute(f"{shlex.quote(self.foundrypf_bin)} --version 2>&1", timeout=5)
            self.foundrypf_version = (ver_out or "").strip().splitlines()[0][:80]
        except Exception:
            self.foundrypf_version = None

        if persist:
            if not self.runner.check_systemctl():
                console.print(
                    "[error]Error:[/error] systemd is not available on this instance. "
                    "Use [accent]--no-persist[/accent] to run without persistence."
                )
                return False
            # Ensure non-interactive sudo is available for persistence
            if not self.runner.check_passwordless_sudo():
                console.print(
                    "[error]Error:[/error] 'sudo' requires a password on this instance. "
                    "Either configure passwordless sudo for service management or use "
                    "[accent]--no-persist[/accent]."
                )
                return False

        return True

    # ---------- Template Management ----------

    def ensure_systemd_template(self, timeline: StepTimeline | None = None) -> bool:
        """
        Idempotently ensures the systemd template unit exists and is up-to-date.
        If updated, active instances are restarted to pick up new ExecStart.
        """
        unit_template = _build_systemd_unit_template(self.foundrypf_bin)
        local_md5 = hashlib.md5(unit_template.encode("utf-8")).hexdigest()
        local_sha256 = hashlib.sha256(unit_template.encode("utf-8")).hexdigest()

        # Try multiple checksum tools to avoid distro differences
        check_cmd = (
            f"(md5sum {SYSTEMD_TEMPLATE_PATH} 2>/dev/null || "
            f" sha256sum {SYSTEMD_TEMPLATE_PATH} 2>/dev/null || "
            f" shasum -a 256 {SYSTEMD_TEMPLATE_PATH} 2>/dev/null || "
            f" md5 {SYSTEMD_TEMPLATE_PATH} 2>/dev/null || echo missing)"
        )
        remote_output = self._execute(check_cmd, timeout=15).strip()
        up_to_date = local_md5 in remote_output or local_sha256 in remote_output
        if up_to_date:
            return True

        step_idx = None
        if timeline:
            step_idx = timeline.add_step("Configuring systemd persistence", show_bar=False)
            timeline.start_step(step_idx)

        # Transport content via base64 to avoid quoting pitfalls
        try:
            self.runner.write_file_base64(SYSTEMD_TEMPLATE_PATH, unit_template, reload_systemd=True)
            # Restart active units to pick up changed template
            self.runner.restart_units("foundrypf@*.service")
            if timeline and step_idx is not None:
                timeline.complete_step()
            return True
        except Exception as e:
            if timeline and step_idx is not None:
                timeline.fail_step(f"Failed to update systemd: {e}")
            return False

    # ---------- Open / Close ----------

    def open_ports(self, ports: list[int], persist: bool, timeline: StepTimeline):
        """
        Open multiple ports; if persist=True, enable and start systemd units; otherwise run foundrypf detached.
        """
        if persist and not self.ensure_systemd_template(timeline):
            raise RuntimeError("Failed to configure systemd persistence.")

        preview_ports = ", ".join(map(str, ports[:10])) + ("…" if len(ports) > 10 else "")
        step_idx = timeline.add_step(
            f"Opening {len(ports)} port(s) (Persist={persist})", show_bar=True
        )
        timeline.start_step(step_idx)

        cmds: list[str] = []
        for p in ports:
            if persist:
                cmds.append(f"systemctl enable --now foundrypf@{p}.service || true")
            else:
                # Detached with logging
                cmds.append(
                    f"nohup {shlex.quote(self.foundrypf_bin)} {p} >/var/log/foundrypf-{p}.log 2>&1 &"
                )

        total_cmds = len(cmds)
        for i, c in enumerate(cmds):
            if c.startswith("systemctl ") or c.startswith("nohup "):
                self.runner.run_sudo(c, timeout=OPEN_CLOSE_CMD_TIMEOUT)
            else:
                self._execute(c, timeout=OPEN_CLOSE_CMD_TIMEOUT)
            timeline.update_active(
                percent=(i + 1) / float(total_cmds), message=f"{i + 1}/{total_cmds}"
            )

        timeline.complete_step()

    def close_ports(self, ports: list[int], timeline: StepTimeline):
        """
        Close multiple ports; disable services and invoke foundrypf -d for safety.
        """
        step_idx = timeline.add_step(f"Closing {len(ports)} port(s)", show_bar=True)
        timeline.start_step(step_idx)

        cmds: list[str] = []
        for p in ports:
            cmds.append(f"systemctl disable --now foundrypf@{p}.service || true")
            cmds.append(f"{shlex.quote(self.foundrypf_bin)} -d {p} || true")

        total_cmds = len(cmds)
        for i, c in enumerate(cmds):
            if c.startswith("systemctl "):
                self.runner.run_sudo(c, timeout=OPEN_CLOSE_CMD_TIMEOUT)
            else:
                self.runner.run_sudo(c, timeout=OPEN_CLOSE_CMD_TIMEOUT)
            timeline.update_active(
                percent=(i + 1) / float(total_cmds), message=f"{i + 1}/{total_cmds}"
            )

        timeline.complete_step()

    # ---------- Verification / Inspection ----------

    def list_managed_ports(self) -> list[PortInfo]:
        """
        Systemd is the source of truth for persisted ports.
        """
        cmd = (
            "systemctl list-units --all --type=service --no-legend --no-pager "
            "'foundrypf@*.service' 2>/dev/null || true"
        )
        output = self._execute(cmd, timeout=VERIFY_LIST_TIMEOUT)

        ports_info: list[PortInfo] = []
        for line in (output or "").splitlines():
            parts = line.strip().split(maxsplit=4)  # UNIT LOAD ACTIVE SUB DESC
            if not parts:
                continue
            service_name = parts[0]
            m = re.match(r"foundrypf@(\d+)\.service", service_name)
            if not m:
                continue
            try:
                port = int(m.group(1))
            except ValueError:
                continue

            status = "unknown"
            if len(parts) >= 4:
                active, sub = parts[2], parts[3]
                if active == "active" and sub == "running":
                    status = "active"
                elif active == "failed" or sub == "failed":
                    status = "failed"
                else:
                    status = sub  # dead/inactive/activating/…
            ports_info.append({"port": port, "service_name": service_name, "status": status})

        return sorted(ports_info, key=lambda x: x["port"])

    def verify_persisted(
        self, ports: list[int], expect_open: bool, timeline: StepTimeline
    ) -> list[int]:
        """
        Verify persisted ports by inspecting systemd state.
        """
        action = "open" if expect_open else "closed"
        step_idx = timeline.add_step(f"Verifying ports are {action}", show_bar=False)
        timeline.start_step(step_idx)

        failed: list[int] = []
        try:
            current = {p["port"]: p["status"] for p in self.list_managed_ports()}
        except Exception as e:
            timeline.fail_step(f"Verification fetch failed: {e}")
            return ports  # assume failure

        for p in ports:
            status = current.get(p, "unknown")
            if expect_open:
                if status != "active":
                    # Unknown means not persisted; treat as fail for persisted verification.
                    failed.append(p)
            else:
                if status == "active":
                    failed.append(p)

        if failed:
            timeline.fail_step(f"Verification failed for {len(failed)} port(s)")
        else:
            timeline.complete_step()
        return failed

    def verify_ephemeral(self, ports: list[int], timeline: StepTimeline) -> list[int]:
        """
        Verify ephemeral opens by checking a listening socket for each port, with fallbacks.
        """
        step_idx = timeline.add_step("Verifying ephemeral ports", show_bar=False)
        timeline.start_step(step_idx)

        failed: list[int] = []
        for p in ports:
            # Prefer socket inspection; fall back to process grep
            check_cmd = (
                f"(command -v ss >/dev/null 2>&1 && ss -Htanlp 2>/dev/null | awk '{{print $4\" \"$7}}' | grep -E ':{p}\\s' | grep -q foundrypf && echo OK)"
                f" || (command -v netstat >/dev/null 2>&1 && netstat -tlnp 2>/dev/null | grep -E ':{p}\\s' | grep -q foundrypf && echo OK)"
                f" || (pgrep -af '[f]oundrypf {p}' >/dev/null && echo OK)"
                f" || echo __NOT_RUNNING__"
            )
            out = self._execute(check_cmd, timeout=10)
            if "__NOT_RUNNING__" in (out or ""):
                failed.append(p)

        if failed:
            timeline.fail_step(f"Ephemeral verification failed for {len(failed)} port(s)")
        else:
            timeline.complete_step()
        return failed


# =============================================================================
# CLI
# =============================================================================


class PortsCommand(BaseCommand):
    """Manage instance port exposure and local tunnels for a task."""

    @property
    def name(self) -> str:
        return "ports"

    @property
    def help(self) -> str:
        return "Open/close/list exposed ports and create local SSH tunnels"

    def get_command(self) -> click.Command:
        @click.group(name=self.name, help=self.help)
        @click.pass_context
        @cli_error_guard(self)
        def ports(ctx: click.Context):
            flow_client = create_client(auto_init=True)
            ctx.ensure_object(dict)
            ctx.obj["flow_client"] = flow_client

        # ---------- open ----------

        @ports.command(name="open")
        @click.argument("task_identifier", required=False, shell_complete=complete_task_ids)
        @click.option(
            "--task", "-t", "task_option", help="Task ID or name", shell_complete=complete_task_ids
        )
        @click.option(
            "--port",
            "ports_expr",
            type=PortsExpr(),
            multiple=True,
            help="Port(s): allow repeats, comma/space lists, and ranges (e.g. '8080,8888 3000-3002')",
        )
        @click.option(
            "--persist/--no-persist", default=True, help="Persist via systemd service (recommended)"
        )
        @click.option("--json", "output_json", is_flag=True, help="Output JSON for automation")
        @click.pass_context
        @cli_error_guard(self)
        def open_cmd(
            ctx: click.Context,
            task_identifier: str | None,
            task_option: str | None,
            ports_expr: tuple[list[int], ...],
            persist: bool,
            output_json: bool,
        ):
            """Open one or more public ports on the task instance (Mithril: foundrypf)."""
            flow_client: Flow = ctx.obj["flow_client"]

            # Resolve task
            task, error = _resolve_task(
                flow_client, task_identifier, task_option, "Select a task to open a port on"
            )
            if error:
                if output_json:
                    from flow.cli.utils.json_output import error_json, print_json

                    print_json(error_json(str(error)))
                else:
                    console.print(f"[error]Error:[/error] {error}")
                return

            # Parse ports (already parsed by type); merge and validate
            ports_list: list[int] = merge_ports_expr(ports_expr)

            if not ports_list:
                console.print("\n[accent]Enter port(s) to open[/accent]")
                console.print("[dim]Examples: 8080, 8888 3000-3002[/dim]")
                console.print("[dim]Common: 80 (http), 443 (https), 8080, 8888, 3000, 5000[/dim]")
                try:
                    raw = click.prompt("Port(s)", type=str, default="8080")
                except (click.Abort, Exception):
                    console.print("[warning]Cancelled.[/warning]")
                    return
                try:
                    ports_list = parse_ports_expression(raw)
                except ValueError as ve:
                    console.print(f"[error]Error:[/error] {ve}")
                    return

            # Validate ports: allow 80, 443, or 1024–65535
            try:
                ports_list = validate_ports_range(
                    ports_list, min_port=1024, max_port=65535, allowed_extras={80, 443}
                )
            except click.BadParameter as e:
                console.print(f"[error]Error:[/error] {e}")
                return

            remote_ops = _safe_remote_ops(flow_client)
            if not remote_ops:
                if output_json:
                    from flow.cli.utils.json_output import error_json, print_json

                    print_json(error_json("Provider lacks remote operations"))
                return

            manager = RemotePortManager(remote_ops, task.task_id)
            timeline = StepTimeline(console, title="flow ports open", title_animation="auto")
            timeline.start()
            # Preflight step provides immediate feedback on submission
            try:
                pf_idx = timeline.add_step("Preflight checks", show_bar=False)
                timeline.start_step(pf_idx)
                try:
                    timeline.set_active_hint_text(
                        Text("Checking 'foundrypf' availability and systemd (for --persist)…")
                    )
                except Exception:
                    pass
                if not manager.ensure_prereqs(persist=persist):
                    timeline.fail_step("requirements not met")
                    timeline.finish()
                    if output_json:
                        from flow.cli.utils.json_output import error_json, print_json

                        print_json(error_json("Missing prerequisites on remote host"))
                    return
                # On success, display discovered path/version as a short note
                note = f"foundrypf: {manager.foundrypf_bin}"
                if manager.foundrypf_version:
                    note += f" ({manager.foundrypf_version})"
                timeline.complete_step(note=note)
            except Exception as e:
                try:
                    timeline.fail_step("preflight failed")
                    timeline.finish()
                except Exception:
                    pass
                self.handle_error(e)
                return

            try:
                manager.open_ports(ports_list, persist, timeline)

                # Verify
                failed: list[int] = []
                if persist:
                    failed = manager.verify_persisted(
                        ports_list, expect_open=True, timeline=timeline
                    )
                else:
                    failed = manager.verify_ephemeral(ports_list, timeline=timeline)

                timeline.finish()

                if failed:
                    if output_json:
                        from flow.cli.utils.json_output import error_json, print_json

                        print_json(
                            error_json(
                                "Failed to verify open ports", hint=", ".join(map(str, failed))
                            )
                        )
                    else:
                        console.print(
                            "[error]Error:[/error] Failed to verify open state for port(s): "
                            + ", ".join(map(str, failed))
                        )
                        console.print(
                            "[dim]Try checking logs: /var/log/foundrypf-<port>.log or "
                            "'systemctl status foundrypf@<port>.service'[/dim]"
                        )
                    return

                if output_json:
                    from flow.cli.utils.json_output import print_json

                    print_json(
                        {
                            "status": "opened",
                            "task_id": task.task_id,
                            "task_name": getattr(task, "name", None),
                            "ports": ports_list,
                            "persist": bool(persist),
                            "foundrypf": getattr(manager, "foundrypf_version", None)
                            or getattr(manager, "foundrypf_bin", None),
                        }
                    )
                else:
                    console.print(
                        "[success]✓[/success] Opened ports: " + ", ".join(map(str, ports_list))
                    )
                if not persist:
                    if not output_json:
                        console.print(
                            "[warning]Note:[/warning] Ports opened without persistence are not managed by systemd "
                            "and may close if the process fails."
                        )

                # URLs
                if getattr(task, "ssh_host", None) and not output_json:
                    console.print("URL(s):")
                    for p in ports_list:
                        console.print(f"  • http://{task.ssh_host}:{p}")

                # Next actions
                try:
                    task_ref = task.name or task.task_id
                    if not output_json:
                        self.show_next_actions(
                            [
                                f"Create a local tunnel: [accent]flow ports tunnel {task_ref} --remote {ports_list[0]}[/accent]",
                                f"List managed ports: [accent]flow ports list {task_ref}[/accent]",
                                f"Close a port: [accent]flow ports close {task_ref} --port {ports_list[0]}[/accent]",
                            ]
                        )
                except Exception:
                    pass

            except Exception as e:
                try:
                    timeline.finish()
                except Exception:
                    pass
                self.handle_error(e)

        # ---------- close ----------

        @ports.command(name="close")
        @click.argument("task_identifier", required=False, shell_complete=complete_task_ids)
        @click.option(
            "--task", "-t", "task_option", help="Task ID or name", shell_complete=complete_task_ids
        )
        @click.option(
            "--port",
            "ports_expr",
            type=PortsExpr(),
            multiple=True,
            help="Port(s) to close (e.g. '8080,8888 3000-3002')",
        )
        @click.option("--all", "close_all", is_flag=True, help="Close all managed ports")
        @click.option("--json", "output_json", is_flag=True, help="Output JSON for automation")
        @click.pass_context
        @cli_error_guard(self)
        def close_cmd(
            ctx: click.Context,
            task_identifier: str | None,
            task_option: str | None,
            ports_expr: tuple[list[int], ...],
            close_all: bool,
            output_json: bool,
        ):
            """Close one or more previously opened public ports."""
            flow_client: Flow = ctx.obj["flow_client"]

            if not ports_expr and not close_all:
                console.print("[error]Error:[/error] Must specify --port(s) or --all.")
                return

            # Resolve task
            task, error = _resolve_task(
                flow_client, task_identifier, task_option, "Select a task to close ports on"
            )
            if error:
                if output_json:
                    from flow.cli.utils.json_output import error_json, print_json

                    print_json(error_json(str(error)))
                else:
                    console.print(f"[error]Error:[/error] {error}")
                return

            remote_ops = _safe_remote_ops(flow_client)
            if not remote_ops:
                if output_json:
                    from flow.cli.utils.json_output import error_json, print_json

                    print_json(error_json("Provider lacks remote operations"))
                return

            manager = RemotePortManager(remote_ops, task.task_id)
            timeline = StepTimeline(console, title="flow ports close", title_animation="auto")
            timeline.start()
            # Preflight step for immediate feedback
            try:
                pf_idx = timeline.add_step("Preflight checks", show_bar=False)
                timeline.start_step(pf_idx)
                try:
                    timeline.set_active_hint_text(
                        Text("Checking 'foundrypf' availability and systemd…")
                    )
                except Exception:
                    pass
                if not manager.ensure_prereqs(persist=True):
                    timeline.fail_step("requirements not met")
                    timeline.finish()
                    return
                note = f"foundrypf: {manager.foundrypf_bin}"
                if manager.foundrypf_version:
                    note += f" ({manager.foundrypf_version})"
                timeline.complete_step(note=note)
            except Exception as e:
                try:
                    timeline.fail_step("preflight failed")
                    timeline.finish()
                except Exception:
                    pass
                self.handle_error(e)
                return

            # Determine ports
            ports_list: list[int] = []
            if close_all:
                try:
                    managed = manager.list_managed_ports()
                except Exception as e:
                    if output_json:
                        from flow.cli.utils.json_output import error_json, print_json

                        print_json(error_json(f"Failed to list managed ports: {e}"))
                    else:
                        self.handle_error(e)
                    return
                ports_list = [p["port"] for p in managed]
                if not ports_list:
                    if output_json:
                        from flow.cli.utils.json_output import print_json

                        print_json({"status": "noop", "closed": [], "failed": []})
                    else:
                        console.print("[warning]No managed ports found to close.[/warning]")
                    return
            else:
                ports_list = merge_ports_expr(ports_expr)
                try:
                    ports_list = validate_ports_range(ports_list, min_port=1, max_port=65535)
                except click.BadParameter as e:
                    console.print(f"[error]Error:[/error] {e}")
                    return

            try:
                manager.close_ports(ports_list, timeline)
                failed = manager.verify_persisted(ports_list, expect_open=False, timeline=timeline)
                timeline.finish()

                if output_json:
                    from flow.cli.utils.json_output import print_json

                    print_json({"status": "closed", "closed": ports_list, "failed": failed})
                else:
                    if failed:
                        console.print(
                            "[warning]Warning:[/warning] Failed to verify closed state for port(s): "
                            + ", ".join(map(str, failed))
                        )
                        console.print(
                            "[dim]They may still be active. Check 'systemctl status foundrypf@<port>.service'.[/dim]"
                        )

                    console.print(
                        "[success]✓[/success] Closed port(s): " + ", ".join(map(str, ports_list))
                    )

                try:
                    task_ref = task.name or task.task_id
                    self.show_next_actions(
                        [
                            f"List managed ports: [accent]flow ports list {task_ref}[/accent]",
                            f"Open a new port: [accent]flow ports open {task_ref} --port 8888[/accent]",
                        ]
                    )
                except Exception:
                    pass

            except Exception as e:
                try:
                    timeline.finish()
                except Exception:
                    pass
                self.handle_error(e)

        # ---------- list ----------

        @ports.command(name="list")
        @click.argument("task_identifier", required=False, shell_complete=complete_task_ids)
        @click.option(
            "--task", "-t", "task_option", help="Task ID or name", shell_complete=complete_task_ids
        )
        @click.option(
            "--all",
            "show_all",
            is_flag=True,
            help="Also scan listening TCP sockets (includes non-persisted)",
        )
        @click.option("--json", "output_json", is_flag=True, help="Output JSON for automation")
        @click.pass_context
        @cli_error_guard(self)
        def list_cmd(
            ctx: click.Context,
            task_identifier: str | None,
            task_option: str | None,
            show_all: bool,
            output_json: bool,
        ):
            """List ports managed via 'flow ports open --persist' (systemd services).

            Use --all to also show listening TCP sockets (includes non-persisted ports).
            """
            flow_client: Flow = ctx.obj["flow_client"]

            # Resolve task
            task, error = _resolve_task(
                flow_client, task_identifier, task_option, "Select a task to list ports for"
            )
            if error:
                if output_json:
                    from flow.cli.utils.json_output import error_json, print_json

                    print_json(error_json(str(error)))
                else:
                    console.print(f"[error]Error:[/error] {error}")
                return

            remote_ops = _safe_remote_ops(flow_client)
            if not remote_ops:
                if output_json:
                    from flow.cli.utils.json_output import error_json, print_json

                    print_json(error_json("Provider lacks remote operations"))
                return

            manager = RemotePortManager(remote_ops, task.task_id)

            timeline = StepTimeline(console, title="flow ports list", title_animation="auto")
            timeline.start()
            step_idx = timeline.add_step("Fetching port info", show_bar=False)
            timeline.start_step(step_idx)

            try:
                ports_info = manager.list_managed_ports()
                sockets_output = ""
                if show_all:
                    sockets_output = (
                        remote_ops.execute_command(
                            task.task_id,
                            "ss -lntp 2>/dev/null | awk 'NR>1 {print $4}' || true",
                            timeout=30,
                        )
                        or ""
                    )
                timeline.complete_step()
                timeline.finish()

                if output_json:
                    from flow.cli.utils.json_output import print_json

                    out = {
                        "task_id": task.task_id,
                        "task_name": getattr(task, "name", None),
                        "managed": ports_info,
                    }
                    if show_all:
                        ports = []
                        for line in (sockets_output or "").splitlines():
                            if ":" in line:
                                try:
                                    ports.append(int(line.rsplit(":", 1)[1]))
                                except Exception:
                                    continue
                        ports = sorted(
                            set(p for p in ports if p in {80, 443} or (1024 <= p <= 65535))
                        )
                        out["open_tcp_ports"] = ports
                    print_json(out)
                    return

                if not ports_info:
                    console.print(
                        "[warning]No ports are currently managed by systemd services.[/warning]"
                    )
                    console.print("[dim]Ports opened without --persist are not tracked here.[/dim]")
                else:
                    from rich.table import Table

                    table = Table(title="Managed Ports (Systemd Persistence)")
                    table.add_column("Port", justify="right", style="cyan", no_wrap=True)
                    table.add_column("Status", justify="left", style="bold")
                    table.add_column("Service Name", style="dim")
                    # Use theme link color for URLs instead of hard-coded magenta
                    from flow.cli.utils.theme_manager import theme_manager as _tm_link

                    table.add_column("URL", style=_tm_link.get_color("link"))

                    host = getattr(task, "ssh_host", None)

                    for info in ports_info:
                        status = info["status"]
                        if status == "active":
                            status_color = "green"
                        elif status == "failed":
                            status_color = "red"
                        else:
                            status_color = "yellow"

                        url = f"http://{host}:{info['port']}" if host else "-"
                        url_cell = url if status == "active" else f"[dim]{url}[/dim]"

                        table.add_row(
                            str(info["port"]),
                            f"[{status_color}]{status.capitalize()}[/]",
                            info["service_name"],
                            url_cell,
                        )

                    console.print(table)

                # When requested, also show open TCP sockets, including non-persisted ports
                if show_all:
                    ports = []
                    for line in (sockets_output or "").splitlines():
                        if ":" in line:
                            try:
                                ports.append(int(line.rsplit(":", 1)[1]))
                            except Exception:
                                continue
                    # Filter to common exposure range
                    ports = sorted(set(p for p in ports if p in {80, 443} or (1024 <= p <= 65535)))
                    console.print(
                        "[bold]Open ports (TCP):[/bold] " + (", ".join(map(str, ports)) or "-")
                    )
                    host = getattr(task, "ssh_host", None)
                    if host and ports:
                        console.print("[bold]URLs:[/bold]")
                        for p in ports:
                            console.print(f"  • http://{host}:{p}")

                # Next steps
                try:
                    task_ref = task.name or task.task_id
                    actions = [
                        f"Open a port: [accent]flow ports open {task_ref} --port 8888[/accent]"
                    ]
                    if ports_info:
                        actions.append(
                            f"Close all ports: [accent]flow ports close {task_ref} --all[/accent]"
                        )
                    self.show_next_actions(actions)
                except Exception:
                    pass

            except Exception as e:
                try:
                    timeline.finish()
                except Exception:
                    pass
                self.handle_error(e)

        # ---------- tunnel ----------

        @ports.command(name="tunnel")
        @click.argument("task_identifier", required=True, shell_complete=complete_task_ids)
        @click.option(
            "--remote",
            "remote_port",
            type=PortNumber(min_port=1, max_port=65535),
            required=True,
            help="Remote port",
        )
        @click.option(
            "--local",
            "local_port",
            type=int,
            default=0,
            show_default=True,
            help="Local port (0=auto)",
        )
        @click.option("--print-only", is_flag=True, help="Only print SSH command; do not execute")
        @click.option("--json", "output_json", is_flag=True, help="Output JSON for automation")
        @click.pass_context
        @cli_error_guard(self)
        def tunnel_cmd(
            ctx: click.Context,
            task_identifier: str,
            remote_port: int,
            local_port: int,
            print_only: bool,
            output_json: bool,
        ):
            """Create a local SSH tunnel to the remote port."""
            if local_port < 0 or local_port > 65535:
                console.print("[error]Error:[/error] Invalid local port number.")
                return

            flow_client: Flow = ctx.obj["flow_client"]
            # Show a brief AEP while resolving the identifier
            try:
                from flow.cli.ui.presentation.animated_progress import (
                    AnimatedEllipsisProgress as _AEP,
                )
            except Exception:
                _AEP = None  # type: ignore

            if _AEP:
                with _AEP(console, "Looking up task", start_immediately=True):
                    task, error = resolve_task_identifier(flow_client, task_identifier)
            else:
                task, error = resolve_task_identifier(flow_client, task_identifier)
            if error:
                if output_json:
                    from flow.cli.utils.json_output import error_json, print_json

                    print_json(error_json(str(error)))
                else:
                    console.print(f"[error]Error:[/error] {error}")
                return

            # Best-effort: resolve SSH endpoint if Task view lacks it
            if not getattr(task, "ssh_host", None):
                try:
                    host, port = flow_client.resolve_ssh_endpoint(task.task_id)
                    task.ssh_host = host
                    try:
                        task.ssh_port = int(port or 22)
                    except Exception:
                        task.ssh_port = 22
                except Exception:
                    pass

            if not task.ssh_host or not task.ssh_user:
                if output_json:
                    from flow.cli.utils.json_output import error_json, print_json

                    print_json(error_json("SSH not ready yet; wait for provisioning"))
                else:
                    console.print("[warning]SSH not ready yet; wait for provisioning.[/warning]")
                return

            # Autopick local port when 0
            if local_port == 0:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.bind(("", 0))
                        local_port = s.getsockname()[1]
                except Exception as e:
                    if output_json:
                        from flow.cli.utils.json_output import error_json, print_json

                        print_json(error_json(f"Could not find available local port: {e}"))
                    else:
                        console.print(
                            f"[error]Error:[/error] Could not find available local port: {e}"
                        )
                    return

            # Build SSH command
            from flow.cli.utils.ssh_helpers import SshStack

            ssh_key_path, error_msg = flow_client.get_task_ssh_connection_info(task.task_id)
            if not ssh_key_path:
                if output_json:
                    from flow.cli.utils.json_output import error_json, print_json

                    print_json(error_json(f"SSH key resolution failed: {error_msg}"))
                else:
                    console.print(f"[error]Error:[/error] SSH key resolution failed: {error_msg}")
                return

            tunnel_options = [
                "-N",  # No remote command
                "-L",
                f"{int(local_port)}:localhost:{int(remote_port)}",
                "-o",
                "ExitOnForwardFailure=yes",
                "-o",
                "ServerAliveInterval=30",
                "-o",
                "ServerAliveCountMax=3",
            ]

            cmd_list = SshStack.build_ssh_command(
                user=task.ssh_user,
                host=task.ssh_host,
                port=getattr(task, "ssh_port", 22),
                key_path=Path(ssh_key_path),
                prefix_args=tunnel_options,
            )

            local_url = f"http://localhost:{local_port}"

            if print_only or output_json:
                if output_json:
                    from flow.cli.utils.json_output import print_json

                    print_json(
                        {
                            "status": "ready",
                            "task_id": task.task_id,
                            "task_name": getattr(task, "name", None),
                            "remote_port": remote_port,
                            "local_port": local_port,
                            "ssh_command": " ".join(shlex.quote(x) for x in cmd_list),
                            "local_url": local_url,
                        }
                    )
                else:
                    console.print(" ".join(shlex.quote(x) for x in cmd_list))
                    console.print(f"Local URL: {local_url}")
                    try:
                        task_ref = task.name or task.task_id
                        self.show_next_actions(
                            [
                                f"Open in browser: [accent]{local_url}[/accent]",
                                f"List open ports: [accent]flow ports list {task_ref}[/accent]",
                            ]
                        )
                    except Exception:
                        pass
                return

            console.print(
                f"Starting SSH tunnel: [bold]{local_url}[/bold] → [dim]{task.ssh_host}:{remote_port}[/dim]\n"
                "Press Ctrl+C to stop…"
            )
            try:
                subprocess.run(cmd_list, check=False)
            except KeyboardInterrupt:
                if output_json:
                    from flow.cli.utils.json_output import print_json

                    print_json(
                        {"status": "closed", "local_port": local_port, "remote_port": remote_port}
                    )
                else:
                    console.print("\n[dim]Tunnel closed.[/dim]")
            except FileNotFoundError:
                if output_json:
                    from flow.cli.utils.json_output import error_json, print_json

                    print_json(error_json("SSH client not found in PATH"))
                else:
                    console.print("[error]Error:[/error] SSH client not found in PATH.")
            except Exception as e:
                if output_json:
                    from flow.cli.utils.json_output import error_json, print_json

                    print_json(error_json(str(e)))
                else:
                    self.handle_error(e)
            # Next steps after tunnel ends
            try:
                task_ref = task.name or task.task_id
                self.show_next_actions(
                    [
                        f"List managed ports: [accent]flow ports list {task_ref}[/accent]",
                        f"Open another tunnel: [accent]flow ports tunnel {task_ref} --remote {remote_port}[/accent]",
                    ]
                )
            except Exception:
                pass

        return ports


# Export command instance
command = PortsCommand()
