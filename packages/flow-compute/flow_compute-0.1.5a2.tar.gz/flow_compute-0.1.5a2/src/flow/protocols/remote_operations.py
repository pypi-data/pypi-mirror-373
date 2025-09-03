"""Remote operations interface.

This module defines the interface for remote operations on running tasks,
separate from the main provider interface.
"""

from pathlib import Path
from typing import Any, Protocol


class RemoteOperationsProtocol(Protocol):
    """Provider-agnostic remote operations on running tasks.

    This abstraction enables providers to implement remote operations
    using their platform-specific mechanisms (SSH, kubectl exec,
    cloud APIs, etc.) while maintaining a consistent interface.
    """

    def execute_command(self, task_id: str, command: str, timeout: int | None = None) -> str:
        """Execute a command on a remote task.

        Args:
            task_id: Task identifier
            command: Command to execute
            timeout: Optional timeout in seconds

        Returns:
            Command output (stdout)

        Raises:
            TaskNotFoundError: Task doesn't exist
            RemoteExecutionError: Command failed
            TimeoutError: Command timed out
        """
        ...

    def upload_file(self, task_id: str, local_path: Path, remote_path: str) -> bool:
        """Upload a file to a remote task.

        Args:
            task_id: Task identifier
            local_path: Local file path
            remote_path: Remote file path

        Returns:
            True if upload succeeded

        Raises:
            TaskNotFoundError: Task doesn't exist
            RemoteOperationError: Upload failed
        """
        ...

    def download_file(self, task_id: str, remote_path: str, local_path: Path) -> bool:
        """Download a file from a remote task.

        Args:
            task_id: Task identifier
            remote_path: Remote file path
            local_path: Local file path

        Returns:
            True if download succeeded

        Raises:
            TaskNotFoundError: Task doesn't exist
            RemoteOperationError: Download failed
        """
        ...

    def get_task_logs(self, task_id: str, log_type: str = "stdout", tail: int | None = None) -> str:
        """Get logs from a remote task.

        Args:
            task_id: Task identifier
            log_type: Type of logs to retrieve (stdout, stderr, etc.)
            tail: Number of lines from end to retrieve

        Returns:
            Log content as string

        Raises:
            TaskNotFoundError: Task doesn't exist
            RemoteOperationError: Log retrieval failed
        """
        ...

    def stream_task_logs(
        self, task_id: str, log_type: str = "stdout", follow: bool = True
    ) -> Any:  # Iterator[str] but avoiding import
        """Stream logs from a remote task.

        Args:
            task_id: Task identifier
            log_type: Type of logs to stream
            follow: Whether to follow log output

        Returns:
            Iterator of log lines

        Raises:
            TaskNotFoundError: Task doesn't exist
            RemoteOperationError: Log streaming failed
        """
        ...

    def get_ssh_connection_info(self, task_id: str) -> dict[str, Any]:
        """Get SSH connection information for a task.

        Args:
            task_id: Task identifier

        Returns:
            Dictionary with SSH connection details (host, port, user, etc.)

        Raises:
            TaskNotFoundError: Task doesn't exist
            RemoteOperationError: SSH info not available
        """
        ...


# Backward compatibility alias
IRemoteOperations = RemoteOperationsProtocol
