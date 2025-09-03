"""Daemon command - Manage local background agent (flowd).

Provides start/stop/status subcommands for the lightweight daemon that
keeps provider connections warm and maintains disk snapshots for instant CLI UX.
"""

from __future__ import annotations

import json
import os
import signal
import socket
import subprocess
import sys
import time
from contextlib import suppress
from pathlib import Path

import click

from flow.cli.commands.base import BaseCommand, console

SOCKET_PATH = Path.home() / ".flow" / "flowd.sock"
PID_PATH = Path.home() / ".flow" / "flowd.pid"
TOKEN_PATH = Path.home() / ".flow" / "flowd.token"


def _load_token() -> str | None:
    """Load daemon auth token if present.

    Returns None when the token file is missing or unreadable.
    """
    try:
        return TOKEN_PATH.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None
    except (OSError, UnicodeDecodeError):
        return None


def _send(cmd: dict, timeout: float = 0.5) -> dict | None:
    """Send a command to the daemon over its UNIX socket.

    Returns a dict response or None on connection/parse issues.
    """
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect(str(SOCKET_PATH))
            payload = dict(cmd)
            token = _load_token()
            if token:
                payload["token"] = token
            s.sendall((json.dumps(payload) + "\n").encode("utf-8"))
            buf = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                buf += chunk
                if b"\n" in chunk:
                    break
        if not buf:
            return None
        line = buf.split(b"\n", 1)[0].decode("utf-8", errors="ignore")
        return json.loads(line)
    except (OSError, TimeoutError, json.JSONDecodeError):
        return None


class DaemonCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "daemon"

    @property
    def help(self) -> str:
        return "Manage local background agent for snappier CLI UX"

    def get_command(self) -> click.Command:
        @click.group(name=self.name, help=self.help)
        def daemon():
            pass

        from flow.cli.utils.error_handling import cli_error_guard

        @daemon.command("start", help="Start the daemon in the background")
        @click.option("--idle-ttl", type=int, default=1800, help="Idle shutdown after N seconds")
        @cli_error_guard(self)
        def start(idle_ttl: int):
            # If already running, say so
            if SOCKET_PATH.exists() and _send({"cmd": "ping"}):
                console.print("[dim]flowd is already running[/dim]")
                return
            # Launch background process
            env = os.environ.copy()
            env["FLOW_DAEMON_IDLE_TTL"] = str(idle_ttl)
            cmd = [sys.executable, "-m", "flow.cli.utils.daemon_server"]
            # Detach
            subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Wait briefly for socket
            deadline = time.time() + 2.0
            while time.time() < deadline:
                if SOCKET_PATH.exists() and _send({"cmd": "ping"}):
                    from flow.cli.utils.theme_manager import theme_manager as _tm

                    console.print(
                        f"[{_tm.get_color('success')}]flowd started[/{_tm.get_color('success')}]"
                    )
                    return
                time.sleep(0.05)
            from flow.cli.utils.theme_manager import theme_manager as _tm

            console.print(
                f"[{_tm.get_color('warning')}]Started, but did not get a response in time[/{_tm.get_color('warning')}]"
            )

        @daemon.command("stop", help="Stop the daemon if running")
        @cli_error_guard(self)
        def stop():
            # Try graceful shutdown via RPC
            if SOCKET_PATH.exists():
                _send({"cmd": "shutdown"}, timeout=0.2)
                time.sleep(0.2)
            # If PID exists, try kill
            if PID_PATH.exists():
                with suppress(ValueError, OSError, ProcessLookupError):
                    pid = int(PID_PATH.read_text().strip())
                    os.kill(pid, signal.SIGTERM)
            # Cleanup best-effort
            with suppress(OSError):
                SOCKET_PATH.unlink(missing_ok=True)  # type: ignore[call-arg]
            with suppress(OSError):
                PID_PATH.unlink(missing_ok=True)  # type: ignore[call-arg]
            from flow.cli.utils.theme_manager import theme_manager as _tm

            console.print(f"[{_tm.get_color('success')}]flowd stopped[/{_tm.get_color('success')}]")

        @daemon.command("status", help="Show daemon status")
        @cli_error_guard(self)
        def status():
            resp = _send({"cmd": "status"})
            if not resp or not resp.get("ok"):
                from flow.cli.utils.theme_manager import theme_manager as _tm

                console.print(
                    f"[{_tm.get_color('warning')}]flowd is not running[/{_tm.get_color('warning')}]"
                )
                return
            status = resp.get("status", {})
            uptime = status.get("uptime", 0.0)
            console.print(
                f"[dim]flowd running[/dim] pid={status.get('pid')} uptime={uptime:.1f}s handled={status.get('connections_handled')}"
            )

        return daemon


command = DaemonCommand()
