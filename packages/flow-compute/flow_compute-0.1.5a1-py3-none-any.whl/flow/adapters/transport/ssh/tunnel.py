from __future__ import annotations

"""SSH tunneling utilities (port-forwarding lifecycle)."""

import atexit
import os
import signal
import socket
import subprocess
from dataclasses import dataclass

from flow.adapters.transport.ssh.ssh_stack import SshStack
from flow.sdk.models import Task


@dataclass
class SSHTunnel:
    """Represents an active SSH tunnel process."""

    process: subprocess.Popen
    local_port: int
    remote_port: int
    remote_host: str = "localhost"
    task_id: str = ""

    def is_alive(self) -> bool:
        return self.process.poll() is None

    def terminate(self) -> None:
        if self.is_alive():
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()


class SSHTunnelManager:
    """Provider-agnostic SSH tunnel manager using SshStack."""

    _active: dict[str, SSHTunnel] = {}

    @classmethod
    def create_tunnel(
        cls,
        task: Task,
        local_port: int = 0,
        remote_port: int = 22,
        remote_host: str = "localhost",
        ssh_options: list[str] | None = None,
    ) -> SSHTunnel:
        if not getattr(task, "ssh_host", None):
            raise RuntimeError(f"Task {getattr(task, 'task_id', '?')} has no SSH host information")

        if local_port == 0:
            local_port = cls._find_free_port()

        cmd = cls._build_tunnel_cmd(task, local_port, remote_port, remote_host, ssh_options)
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid if os.name != "nt" else None,
        )

        # brief check window
        import time as _t

        _t.sleep(0.4)
        if proc.poll() is not None:
            err = proc.stderr.read().decode() if proc.stderr else ""
            raise RuntimeError(f"SSH tunnel failed to start: {err}")

        if not cls._verify(local_port, timeout=5.0):
            proc.terminate()
            raise RuntimeError(f"SSH tunnel on port {local_port} is not responding")

        tunnel = SSHTunnel(
            process=proc,
            local_port=local_port,
            remote_port=remote_port,
            remote_host=remote_host,
            task_id=getattr(task, "task_id", ""),
        )
        cls._active[f"{tunnel.task_id}:{tunnel.local_port}"] = tunnel
        return tunnel

    @classmethod
    def tunnel_context(
        cls,
        task: Task,
        local_port: int = 0,
        remote_port: int = 22,
        remote_host: str = "localhost",
        ssh_options: list[str] | None = None,
    ):
        tunnel = None
        try:
            tunnel = cls.create_tunnel(task, local_port, remote_port, remote_host, ssh_options)
            yield tunnel
        finally:
            if tunnel:
                try:
                    tunnel.terminate()
                finally:
                    cls._active.pop(f"{tunnel.task_id}:{tunnel.local_port}", None)

    @staticmethod
    def _find_free_port() -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            s.listen(1)
            return s.getsockname()[1]

    @staticmethod
    def _build_tunnel_cmd(
        task: Task,
        local_port: int,
        remote_port: int,
        remote_host: str,
        ssh_options: list[str] | None,
    ) -> list[str]:
        forward = ["-N", "-L", f"{local_port}:{remote_host}:{remote_port}"]
        key_path = SshStack.find_fallback_private_key()
        cmd = SshStack.build_ssh_command(
            user=getattr(task, "ssh_user", "ubuntu"),
            host=task.ssh_host,
            port=getattr(task, "ssh_port", 22),
            key_path=key_path,
            prefix_args=forward,
        )
        if ssh_options:
            cmd.extend(ssh_options)
        cmd.extend(["-o", "ExitOnForwardFailure=yes"])
        return cmd

    @staticmethod
    def _verify(port: int, timeout: float = 5.0) -> bool:
        import time as _t

        start = _t.time()
        while _t.time() - start < timeout:
            try:
                with socket.create_connection(("localhost", port), timeout=1):
                    return True
            except OSError:
                _t.sleep(0.1)
        return False


def _cleanup_all():
    try:
        for t in list(SSHTunnelManager._active.values()):
            try:
                t.terminate()
            except Exception:
                pass
        SSHTunnelManager._active.clear()
    except Exception:
        pass


atexit.register(_cleanup_all)

# Install signal handlers that perform cleanup but preserve default behavior
try:
    _prev_sigterm = signal.getsignal(signal.SIGTERM) if hasattr(signal, "SIGTERM") else None
except Exception:
    _prev_sigterm = None


def _handle_sigterm(signum, frame):  # pragma: no cover - signal dependent
    try:
        _cleanup_all()
    finally:
        try:
            if callable(_prev_sigterm):
                _prev_sigterm(signum, frame)
            elif _prev_sigterm in (None, signal.SIG_DFL):
                raise SystemExit(0)
        except SystemExit:
            raise
        except Exception:
            raise SystemExit(0)


try:
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _handle_sigterm)
except Exception:
    pass

try:
    _prev_sigint = signal.getsignal(signal.SIGINT) if hasattr(signal, "SIGINT") else None
except Exception:
    _prev_sigint = None


def _handle_sigint(signum, frame):  # pragma: no cover - signal dependent
    try:
        _cleanup_all()
    finally:
        try:
            if callable(_prev_sigint) and _prev_sigint not in {signal.SIG_DFL, signal.SIG_IGN}:
                _prev_sigint(signum, frame)
            else:
                signal.default_int_handler(signum, frame)
        except KeyboardInterrupt:
            raise
        except Exception:
            signal.default_int_handler(signum, frame)


try:
    if hasattr(signal, "SIGINT"):
        signal.signal(signal.SIGINT, _handle_sigint)
except Exception:
    pass
