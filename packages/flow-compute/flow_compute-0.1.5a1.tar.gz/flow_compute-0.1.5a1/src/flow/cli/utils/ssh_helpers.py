from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path


class SshStack:
    """CLI-facing wrapper around core SSH utilities.

    Keeps CLI imports decoupled from core by delegating at call time.
    """

    @staticmethod
    def find_fallback_private_key() -> Path | None:
        from flow.sdk.ssh import SshStack as _S

        return _S.find_fallback_private_key()

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
        from flow.sdk.ssh import SshStack as _S

        return _S.build_ssh_command(
            user=user,
            host=host,
            port=port,
            key_path=key_path,
            prefix_args=prefix_args,
            remote_command=remote_command,
        )

    @staticmethod
    def tcp_port_open(host: str, port: int, timeout_sec: float = 2.0) -> bool:
        from flow.sdk.ssh import SshStack as _S

        return _S.tcp_port_open(host, port, timeout_sec)

    @staticmethod
    def is_ssh_ready(*, user: str, host: str, port: int, key_path: Path) -> bool:
        from flow.sdk.ssh import SshStack as _S

        return _S.is_ssh_ready(user=user, host=host, port=port, key_path=key_path)
