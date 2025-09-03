"""SSH client protocol for remote operations.

This protocol defines the contract for SSH communication that the application layer
depends on. Adapters implement this interface to provide concrete SSH functionality.
"""

from pathlib import Path
from typing import Protocol


class SSHClientProtocol(Protocol):
    """Port for SSH client operations.

    This port abstracts SSH communication for the application layer.
    Implementations handle connection management, authentication, and
    command execution transparently.

    Implementation requirements:
      - Secure key-based authentication
      - Connection pooling and reuse
      - Automatic retry on connection failures
      - Port forwarding support
      - File transfer capabilities
      - Thread-safe operation
    """

    def connect(
        self,
        host: str,
        port: int = 22,
        user: str = "ubuntu",
        key_path: Path | None = None,
        timeout: float = 30.0,
    ) -> None:
        """Establish SSH connection.

        Args:
            host: Remote host address
            port: SSH port (default: 22)
            user: SSH username
            key_path: Path to private key file
            timeout: Connection timeout in seconds

        Raises:
            ConnectionError: Failed to establish connection
            AuthenticationError: Authentication failed
        """
        ...

    def execute(
        self,
        command: str,
        timeout: float | None = None,
        check: bool = True,
    ) -> tuple[str, str, int]:
        """Execute command on remote host.

        Args:
            command: Command to execute
            timeout: Command timeout in seconds
            check: Raise on non-zero exit code

        Returns:
            Tuple of (stdout, stderr, exit_code)

        Raises:
            CommandError: Command execution failed (if check=True)
            TimeoutError: Command exceeded timeout
        """
        ...

    def copy_file(
        self,
        local_path: Path,
        remote_path: str,
        recursive: bool = False,
    ) -> None:
        """Copy file to remote host.

        Args:
            local_path: Local file or directory path
            remote_path: Remote destination path
            recursive: Copy directories recursively

        Raises:
            FileNotFoundError: Local file doesn't exist
            TransferError: File transfer failed
        """
        ...

    def forward_port(
        self,
        local_port: int,
        remote_port: int,
        remote_host: str = "localhost",
    ) -> None:
        """Set up port forwarding.

        Args:
            local_port: Local port to bind
            remote_port: Remote port to forward to
            remote_host: Remote host for forwarding (default: localhost)

        Raises:
            PortError: Port forwarding failed
        """
        ...

    def is_connected(self) -> bool:
        """Check if SSH connection is active.

        Returns:
            True if connected, False otherwise
        """
        ...

    def close(self) -> None:
        """Close SSH connection.

        Releases resources and closes all channels.
        Safe to call multiple times.
        """
        ...
