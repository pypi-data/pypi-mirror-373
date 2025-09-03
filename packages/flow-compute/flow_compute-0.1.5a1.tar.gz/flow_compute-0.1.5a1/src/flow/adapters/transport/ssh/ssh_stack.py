"""Centralized SSH utilities for Flow.

Single source of truth for:
- Building ssh commands with consistent options
- Checking SSH readiness
- Resolving private key path overrides (env/back-compat)

Providers and CLI should import and use this module to avoid duplicated logic.
"""

from __future__ import annotations

import os
import socket
import subprocess
from collections.abc import Iterable
from pathlib import Path


class SshStack:
    """Centralized helpers for SSH operations.

    This class deliberately avoids provider-specific behavior. Any provider
    that needs to scope API calls (e.g., project scoping) should do so before
    calling these helpers.
    """

    # Canonical SSH options used everywhere
    _BASE_OPTIONS: list[str] = [
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "UserKnownHostsFile=/dev/null",
        "-o",
        "PasswordAuthentication=no",
        "-o",
        "ConnectTimeout=10",
        "-o",
        "ServerAliveInterval=10",
        "-o",
        "ServerAliveCountMax=3",
    ]

    @staticmethod
    def find_fallback_private_key() -> Path | None:
        """Return a fallback private key path if explicitly configured.

        Precedence:
        1) MITHRIL_SSH_KEY (path to private key)
        2) FLOW_SSH_KEY_PATH (legacy/back-compat)
        3) Standard ~/.ssh key names (id_ed25519, id_rsa, id_ecdsa)
        """
        # Env override (preferred)
        env_key = os.environ.get("MITHRIL_SSH_KEY")
        if env_key:
            p = Path(env_key).expanduser()
            if p.exists():
                return p

        # Back-compat
        legacy = os.environ.get("FLOW_SSH_KEY_PATH")
        if legacy:
            p = Path(legacy).expanduser()
            if p.exists():
                return p

        # Common defaults
        ssh_dir = Path.home() / ".ssh"
        for name in ("id_ed25519", "id_rsa", "id_ecdsa"):
            p = ssh_dir / name
            if p.exists():
                return p
        return None

    @staticmethod
    def build_ssh_command(
        *,
        user: str,
        host: str,
        port: int | None = None,
        key_path: Path | None = None,
        prefix_args: Iterable[str] | None = None,
        remote_command: str | None = None,
    ) -> list[str]:
        """Build a canonical ssh command.

        Args:
            user: SSH username.
            host: Target hostname/IP.
            port: SSH port (default 22).
            key_path: Private key path, if any.
            prefix_args: Extra args preceding destination (e.g., -N -L ... for tunnels).
            remote_command: Optional command to execute remotely.
        """
        cmd: list[str] = ["ssh"]

        if prefix_args:
            cmd.extend(list(prefix_args))

        if port is None:
            port = 22
        cmd.extend(["-p", str(port)])

        if key_path:
            cmd.extend(["-i", str(Path(key_path).expanduser())])
            # Ensure only the provided key is used (avoid agent/other keys interfering)
            cmd.extend(["-o", "IdentitiesOnly=yes"])

        cmd.extend(SshStack._BASE_OPTIONS)

        # Prefer publickey auth and disable slow GSSAPI negotiation to reduce connection latency
        cmd.extend(
            [
                "-o",
                "PreferredAuthentications=publickey",
                "-o",
                "GSSAPIAuthentication=no",
            ]
        )

        # Enable connection multiplexing to speed subsequent SSH connects
        # Uses a safe ControlPath under /tmp to avoid user-home path issues
        cmd.extend(
            [
                "-o",
                "ControlMaster=auto",
                "-o",
                "ControlPersist=60s",
                "-o",
                "ControlPath=/tmp/flow-ssh-ctl-%r@%h:%p",
            ]
        )

        # Lightweight compression can help on slower links
        cmd.extend(["-o", "Compression=yes"])

        cmd.append(f"{user}@{host}")

        if remote_command:
            # Non-interactive command execution should avoid TTY and interactive prompts
            # to suppress MOTD and banners from polluting the output and to ensure
            # predictable behavior in automation contexts.
            cmd.insert(1, "-T")  # disable pseudo-tty allocation
            cmd.insert(1, "-o")
            cmd.insert(2, "BatchMode=yes")
            cmd.append(remote_command)

        # Debug logging when requested (env > YAML)
        try:
            from flow.application.config.runtime import settings as _settings  # local import

            _debug = bool((_settings.ssh or {}).get("debug", False))
        except Exception:
            _debug = os.environ.get("FLOW_SSH_DEBUG") == "1"
        if _debug:
            try:
                import logging as _logging

                _logging.getLogger(__name__).debug("SSH command argv: %s", " ".join(cmd))
            except Exception:
                pass

        return cmd

    @staticmethod
    def tcp_port_open(host: str, port: int, timeout_sec: float = 2.0) -> bool:
        """Lightweight TCP check before full SSH handshake."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout_sec)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    @staticmethod
    def is_ssh_ready(*, user: str, host: str, port: int, key_path: Path) -> bool:
        """Return True if SSH responds to a BatchMode probe."""
        try:
            from flow.application.config.runtime import settings as _settings  # local import

            debug = bool((_settings.ssh or {}).get("debug", False))
        except Exception:
            debug = os.environ.get("FLOW_SSH_DEBUG") == "1"
        if not SshStack.tcp_port_open(host, port):
            if debug:
                import logging as _logging

                _logging.getLogger(__name__).debug("SSH tcp_port_open(%s:%s) -> closed", host, port)
            return False
        elif debug:
            import logging as _logging

            _logging.getLogger(__name__).debug("SSH tcp_port_open(%s:%s) -> open", host, port)

        # Build probe with BatchMode in prefix args so it's parsed before host
        test_cmd = SshStack.build_ssh_command(
            user=user,
            host=host,
            port=port,
            key_path=key_path,
            # Tighten probe timeouts to reduce perceived latency
            prefix_args=[
                "-o",
                "BatchMode=yes",
                "-o",
                "ConnectTimeout=4",
                "-o",
                "ConnectionAttempts=1",
            ],
            remote_command="echo SSH_OK",
        )

        try:
            import os as _os

            probe_timeout = 4.0
            try:
                probe_timeout = float(_os.environ.get("FLOW_SSH_PROBE_TIMEOUT", "4"))
            except Exception:
                probe_timeout = 4.0
            result = subprocess.run(
                test_cmd, capture_output=True, text=True, timeout=int(probe_timeout)
            )
            if debug:
                import logging as _logging

                _logging.getLogger(__name__).debug(
                    "SSH probe exit=%s stdout=%r stderr=%r",
                    result.returncode,
                    result.stdout,
                    result.stderr,
                )
            if result.returncode == 255:
                stderr = (result.stderr or "").lower()
                if (
                    "connection reset by peer" in stderr
                    or "kex_exchange_identification" in stderr
                    or "connection closed" in stderr
                ):
                    return False
            return result.returncode == 0 and "SSH_OK" in (result.stdout or "")
        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False
