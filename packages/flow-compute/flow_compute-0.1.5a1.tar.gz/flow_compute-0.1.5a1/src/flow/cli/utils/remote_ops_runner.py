"""Thin wrapper around provider remote operations with safer helpers.

Standardizes quoting, sudo, file writes, and common checks so command modules
can stay readable and avoid bespoke shell composition.
"""

from __future__ import annotations

import base64
import shlex
from typing import Any


class RemoteOpsRunner:
    """Helper for executing commands on a remote task instance.

    This wrapper never returns None from run(); it converts falsy provider
    returns to empty strings to simplify callers. It also offers convenience
    helpers for sudo execution and base64 file writes.
    """

    def __init__(self, remote_ops: Any, task_id: str):
        self._ops = remote_ops
        self._task_id = task_id

    # ---- core execution ----

    def run(self, command: str, *, timeout: int = 60) -> str:
        out = self._ops.execute_command(self._task_id, command, timeout=timeout)
        return out or ""

    def run_sudo(self, command: str, *, timeout: int = 60) -> str:
        cmd = f"sudo bash -lc {shlex.quote(command)}"
        return self.run(cmd, timeout=timeout)

    # ---- common checks ----

    def discover_binary(
        self, name: str, extra_paths: list[str] | None = None, *, timeout: int = 10
    ) -> str | None:
        parts = ["(command -v " + shlex.quote(name) + " 2>/dev/null)"]
        for p in extra_paths or []:
            parts.append(f"([ -x {shlex.quote(p)} ] && echo {shlex.quote(p)})")
        parts.append("echo __MISSING__")
        cmd = " || ".join(parts)
        out = self.run(cmd, timeout=timeout).strip()
        if "__MISSING__" in out or not out:
            return None
        return out.splitlines()[0].strip()

    def check_systemctl(self) -> bool:
        out = self.run("command -v systemctl >/dev/null 2>&1 || echo __NO_SYSTEMCTL__", timeout=10)
        return "__NO_SYSTEMCTL__" not in (out or "")

    def check_passwordless_sudo(self) -> bool:
        out = self.run("sudo -n true 2>/dev/null || echo __NO_SUDO_NOPASS__", timeout=5)
        return "__NO_SUDO_NOPASS__" not in (out or "")

    # ---- file utilities ----

    def write_file_base64(self, path: str, content: str, *, reload_systemd: bool = False) -> None:
        encoded = base64.b64encode(content.encode()).decode()
        cmd = f"cat <<'B64' | base64 -d | sudo tee {shlex.quote(path)} >/dev/null\n{encoded}\nB64\n"
        if reload_systemd:
            cmd += "systemctl daemon-reload || true\n"
        self.run(f"bash -lc {shlex.quote(cmd)}", timeout=30)

    def list_units(self, pattern: str) -> str:
        return self.run(
            "systemctl list-units --all --type=service --no-legend --no-pager "
            + shlex.quote(pattern)
            + " 2>/dev/null || true",
            timeout=30,
        )

    def restart_units(self, glob: str) -> None:
        cmd = (
            "for u in $(systemctl list-units --type=service --no-legend "
            + shlex.quote(glob)
            + " | awk '{print $1}'); do systemctl restart \"$u\" || true; done"
        )
        self.run_sudo(cmd, timeout=60)
