"""Log management for local testing provider."""

import logging
import os
import threading
import time
from collections import deque
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Maximum log file size before rotation (100MB)
MAX_LOG_SIZE = 100 * 1024 * 1024


class LocalLogManager:
    """Manages log capture and streaming for local tasks."""

    def __init__(self, storage_dir: Path):
        """Initialize log manager.

        Args:
            storage_dir: Base directory for log storage
        """
        self.storage_dir = Path(storage_dir)
        self.logs_dir = self.storage_dir / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Active log streams
        self._active_streams: dict[str, LogStream] = {}
        self._lock = threading.Lock()

        # Track streamed lines to avoid duplicates
        self._streamed_lines: dict[str, set[str]] = {}

    def start_log_capture(self, task_id: str):
        """Start capturing logs for a task.

        Args:
            task_id: Task identifier
        """
        task_log_dir = self.logs_dir / task_id
        task_log_dir.mkdir(exist_ok=True)

        with self._lock:
            if task_id not in self._active_streams:
                self._active_streams[task_id] = LogStream(task_id=task_id, log_dir=task_log_dir)
                self._streamed_lines[task_id] = set()

    def append_log(self, task_id: str, line: str, log_type: str = "stdout"):
        """Append a log line.

        Args:
            task_id: Task identifier
            line: Log line to append
            log_type: Type of log (stdout/stderr)
        """
        with self._lock:
            if task_id in self._active_streams:
                self._active_streams[task_id].append(line, log_type)

    def get_logs(self, task_id: str, tail: int = 100, log_type: str = "stdout") -> str:
        """Get task logs.

        Args:
            task_id: Task identifier
            tail: Number of lines from end
            log_type: Type of logs to retrieve

        Returns:
            Log content as string
        """
        log_file = self.logs_dir / task_id / f"{log_type}.log"

        if not log_file.exists():
            return ""

        # Efficient tail implementation
        return self._tail_file(log_file, tail)

    def has_streamed_line(self, task_id: str, line: str) -> bool:
        """Check if a line was already streamed to avoid duplicates.

        Uses an internal hash set per task to track previously streamed lines.
        """
        line_hash = hash(line)
        return line_hash in self._streamed_lines.get(task_id, set())

    def stream_logs(
        self, task_id: str, log_type: str = "stdout", follow: bool = True
    ) -> Iterator[str]:
        """Stream logs in real-time.

        Args:
            task_id: Task identifier
            log_type: Type of logs to stream
            follow: Continue following new logs

        Yields:
            Log lines as they become available
        """
        log_file = self.logs_dir / task_id / f"{log_type}.log"

        # Wait for log file to exist
        wait_count = 0
        while not log_file.exists() and wait_count < 30:
            time.sleep(0.1)
            wait_count += 1

        if not log_file.exists():
            yield f"No logs available for task {task_id}"
            return

        # Stream logs
        with open(log_file) as f:
            # Start from beginning
            f.seek(0)

            while True:
                line = f.readline()

                if line:
                    line = line.rstrip()
                    # Track streamed lines to avoid duplicates
                    line_hash = hash(line)
                    if line_hash not in self._streamed_lines.get(task_id, set()):
                        self._streamed_lines[task_id].add(line_hash)
                        yield line
                elif not follow:
                    break
                else:
                    # Check if task is still active
                    with self._lock:
                        if task_id not in self._active_streams:
                            # Task completed, yield any remaining lines
                            for line in f:
                                yield line.rstrip()
                            break

                    # Wait for new content
                    time.sleep(0.1)

    def stop_log_capture(self, task_id: str):
        """Stop capturing logs for a task.

        Args:
            task_id: Task identifier
        """
        with self._lock:
            if task_id in self._active_streams:
                self._active_streams[task_id].close()
                del self._active_streams[task_id]

    def _tail_file(self, file_path: Path, num_lines: int) -> str:
        """Efficiently tail a file.

        Args:
            file_path: Path to file
            num_lines: Number of lines from end

        Returns:
            Last N lines as string
        """
        # For small files, just read all and slice
        if file_path.stat().st_size < 1_000_000:  # 1MB
            lines = file_path.read_text().splitlines()
            return "\n".join(lines[-num_lines:])

        # For large files, use deque for efficiency
        with open(file_path) as f:
            lines = deque(f, maxlen=num_lines)
            return "\n".join(lines)


class LogStream:
    """Manages a single log stream."""

    def __init__(self, task_id: str, log_dir: Path):
        """Initialize log stream.

        Args:
            task_id: Task identifier
            log_dir: Directory for log files
        """
        self.task_id = task_id
        self.log_dir = log_dir

        # Handle log rotation for existing large files
        self._rotate_if_needed(log_dir / "stdout.log")
        self._rotate_if_needed(log_dir / "stderr.log")

        # Open log files
        self.stdout_file = open(log_dir / "stdout.log", "a", buffering=1)
        self.stderr_file = open(log_dir / "stderr.log", "a", buffering=1)

        # Circular buffer for recent logs
        self.recent_stdout: deque[str] = deque(maxlen=1000)
        self.recent_stderr: deque[str] = deque(maxlen=1000)

    def _rotate_if_needed(self, log_path: Path):
        """Rotate log file if it exceeds maximum size.

        Args:
            log_path: Path to log file to check
        """
        if log_path.exists():
            file_size = log_path.stat().st_size
            if file_size > MAX_LOG_SIZE:
                # Simple rotation: move to .1 and remove old .1 if exists
                rotated_path = log_path.with_suffix(log_path.suffix + ".1")

                # Remove old rotated file if exists
                if rotated_path.exists():
                    rotated_path.unlink()

                # Rotate current file
                log_path.rename(rotated_path)
                logger.info(f"Rotated large log file {log_path} ({file_size / 1024 / 1024:.1f}MB)")

    def append(self, line: str, log_type: str = "stdout"):
        """Append a log line.

        Args:
            line: Log line to append
            log_type: Type of log (stdout/stderr)
        """
        # Add timestamp if enabled via centralized config (env > YAML)
        try:
            from flow.application.config.runtime import settings as _settings  # local import

            _ts = bool((_settings.logging or {}).get("timestamps", False))
        except Exception:
            _ts = os.environ.get("FLOW_LOG_TIMESTAMPS", "").lower() in ("1", "true", "yes")
        if _ts:
            timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
            # Only add timestamp if line doesn't already have one
            if not line.strip().startswith("["):
                line = timestamp + line

        # Ensure line ends with newline
        if not line.endswith("\n"):
            line += "\n"

        # Write to appropriate file
        if log_type == "stderr":
            self.stderr_file.write(line)
            self.stderr_file.flush()
            self.recent_stderr.append(line.rstrip())
        else:
            self.stdout_file.write(line)
            self.stdout_file.flush()
            self.recent_stdout.append(line.rstrip())

    def get_recent(self, log_type: str = "stdout", limit: int = 100) -> list[str]:
        """Get recent log lines from memory.

        Args:
            log_type: Type of logs
            limit: Maximum lines to return

        Returns:
            List of recent log lines
        """
        if log_type == "stderr":
            return list(self.recent_stderr)[-limit:]
        else:
            return list(self.recent_stdout)[-limit:]

    def close(self):
        """Close log files."""
        self.stdout_file.close()
        self.stderr_file.close()
