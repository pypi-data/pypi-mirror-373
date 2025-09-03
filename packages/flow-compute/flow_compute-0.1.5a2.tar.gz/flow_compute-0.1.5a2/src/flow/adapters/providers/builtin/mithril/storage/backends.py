"""Storage backend implementation for the Mithril provider.

Local HTTP server backend for handling large files like startup scripts during
development and testing.
"""

import atexit
import hashlib
import json
import logging
import os
import re
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any, Protocol
from urllib.parse import quote

from flow.adapters.providers.builtin.mithril.storage.models import StorageMetadata, StorageUrl

logger = logging.getLogger(__name__)


class StorageError(Exception):
    """Base exception for storage-related errors."""


class IStorageBackend(Protocol):
    """Interface for storage backend implementations."""

    def store(
        self, key: str, data: bytes = None, content: bytes = None, metadata: dict[str, Any] = None
    ) -> StorageUrl:
        """Store content and return a URL for retrieval."""
        ...

    def retrieve(self, key: str) -> bytes | None:
        """Retrieve content by key."""
        ...

    def delete(self, key: str) -> bool:
        """Delete content by key."""
        ...

    def get_url(self, key: str) -> StorageUrl:
        """Get URL for existing content."""
        ...

    def exists(self, key: str) -> bool:
        """Check if content exists."""
        ...

    def get_metadata(self, key: str) -> StorageMetadata | None:
        """Get metadata for stored content."""
        ...

    def health_check(self) -> dict[str, Any]:
        """Perform health check on the backend."""
        ...


class StorageConfig:
    """Configuration for storage backends.

    Attributes:
        backend_type: Type of backend (currently only "local").
        local_port: Port for local HTTP server.
        local_bind: Bind address for local HTTP server.
        local_storage_path: Directory for local storage.
        local_cleanup_on_exit: Whether to cleanup on exit.
        url_expiry_seconds: URL expiration time in seconds.
        max_file_size_mb: Maximum file size in MB.
        request_timeout_seconds: Request timeout in seconds.
        max_retries: Maximum number of retries.
        enable_metrics: Whether to enable metrics collection.
    """

    def __init__(
        self,
        backend_type: str = "local",
        local_port: int = 8080,
        local_bind: str = "127.0.0.1",
        local_storage_path: str | None = None,
        local_cleanup_on_exit: bool = True,
        url_expiry_seconds: int = 3600,
        max_file_size_mb: int = 100,
        request_timeout_seconds: int = 30,
        max_retries: int = 3,
        enable_metrics: bool = True,
    ):
        self.backend_type = backend_type
        self.local_port = local_port
        self.local_bind = local_bind
        self.local_storage_path = local_storage_path or os.path.join(
            tempfile.gettempdir(), "flow-storage"
        )
        self.local_cleanup_on_exit = local_cleanup_on_exit
        self.url_expiry_seconds = url_expiry_seconds
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        self.request_timeout_seconds = request_timeout_seconds
        self.max_retries = max_retries
        self.enable_metrics = enable_metrics

    @classmethod
    def from_env(cls) -> "StorageConfig":
        """Create configuration from environment variables.

        Returns:
            StorageConfig instance populated from environment.
        """
        # Don't default to 'local' - require explicit opt-in
        backend_type = os.getenv("FLOW_STORAGE_BACKEND", None)

        # If no backend specified, return None to indicate no storage
        if not backend_type:
            return None

        return cls(
            backend_type=backend_type,
            local_port=int(os.getenv("FLOW_LOCAL_STORAGE_PORT", "8080")),
            local_bind=os.getenv("FLOW_LOCAL_STORAGE_BIND", "127.0.0.1"),
            local_storage_path=os.getenv("FLOW_LOCAL_STORAGE_PATH"),
            local_cleanup_on_exit=os.getenv("FLOW_LOCAL_CLEANUP_ON_EXIT", "true").lower() == "true",
            url_expiry_seconds=int(os.getenv("FLOW_URL_EXPIRY_SECONDS", "3600")),
            max_file_size_mb=int(os.getenv("FLOW_MAX_FILE_SIZE_MB", "100")),
            request_timeout_seconds=int(os.getenv("FLOW_REQUEST_TIMEOUT_SECONDS", "30")),
            max_retries=int(os.getenv("FLOW_MAX_RETRIES", "3")),
            enable_metrics=os.getenv("FLOW_ENABLE_METRICS", "true").lower() == "true",
        )

    def validate(self):
        """Validate configuration.

        Raises:
            ValueError: If configuration is invalid.
        """
        if self.backend_type != "local":
            raise ValueError(f"Invalid backend type: {self.backend_type}")

        if self.max_file_size_bytes <= 0:
            raise ValueError("Max file size must be positive")

        if self.url_expiry_seconds <= 0:
            raise ValueError("URL expiry seconds must be positive")


class BaseStorageBackend:
    """Base class for storage backends with common functionality."""

    def __init__(self, config: StorageConfig):
        """Initialize storage backend.

        Args:
            config: Storage configuration.
        """
        self.config = config
        self._metrics = {
            "store_count": 0,
            "retrieve_count": 0,
            "delete_count": 0,
            "store_errors": 0,
            "retrieve_errors": 0,
            "delete_errors": 0,
            "total_bytes_stored": 0,
            "total_bytes_retrieved": 0,
        }
        self._metrics_lock = threading.Lock()

    def _compute_hash(self, content: bytes) -> str:
        """Compute SHA256 hash of content.

        Args:
            content: Content to hash.

        Returns:
            Hex-encoded SHA256 hash.
        """
        return hashlib.sha256(content).hexdigest()

    def _record_metric(self, metric: str, value: int = 1):
        """Record a metric.

        Args:
            metric: Metric name.
            value: Value to add (default 1).
        """
        if not self.config.enable_metrics:
            return

        with self._metrics_lock:
            if metric in self._metrics:
                self._metrics[metric] += value

    def get_metrics(self) -> dict[str, int]:
        """Get current metrics.

        Returns:
            Dictionary of metric names to values.
        """
        with self._metrics_lock:
            return self._metrics.copy()

    @contextmanager
    def _operation_context(self, operation: str):
        """Context manager for tracking operations.

        Args:
            operation: Operation name (e.g., "store", "retrieve").

        Yields:
            None

        Raises:
            StorageError: If operation fails.
        """
        start_time = time.time()
        try:
            yield
            self._record_metric(f"{operation}_count")
            logger.debug(f"{operation} completed in {time.time() - start_time:.2f}s")
        except Exception as e:
            logger.exception(f"Error during {operation}")
            self._record_metric(f"{operation}_errors")
            raise StorageError(f"{operation} failed: {e!s}") from e


class LocalHttpBackend(BaseStorageBackend):
    """Local HTTP server backend for development and testing.

    This backend starts a local HTTP server to serve stored files. It's useful
    for development and testing but should not be used in production.
    """

    # Pattern for valid storage keys - alphanumeric, forward slash, dash, underscore, dot
    VALID_KEY_PATTERN = re.compile(r"^[a-zA-Z0-9/_.-]+$")
    MAX_KEY_LENGTH = 255

    def __init__(self, config: StorageConfig):
        """Initialize local HTTP backend.

        Args:
            config: Storage configuration.
        """
        super().__init__(config)
        self.storage_dir = Path(config.local_storage_path)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self._server = None
        self._server_thread = None
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="local-storage")
        self._running = False
        self._atexit_handler = None
        self._server_lock = threading.Lock()  # For atomic port allocation

        if config.local_cleanup_on_exit:
            self._atexit_handler = self.close
            atexit.register(self._atexit_handler)

        self._start_server()

    def _sanitize_key(self, key: str) -> str:
        """Securely sanitize storage keys to prevent path traversal.

        Args:
            key: Raw storage key.

        Returns:
            Sanitized key.

        Raises:
            StorageError: If key is invalid.
        """
        # Remove leading/trailing whitespace
        key = key.strip()

        # Check length
        if not key or len(key) > self.MAX_KEY_LENGTH:
            raise StorageError(f"Invalid key length: must be 1-{self.MAX_KEY_LENGTH} characters")

        # Normalize path separators and remove any traversal attempts
        key = os.path.normpath(key).replace("\\", "/")

        # Remove leading slashes and any remaining traversal patterns
        key = key.lstrip("/")

        # Check for any traversal attempts after normalization
        if ".." in key or key.startswith("/") or os.path.isabs(key):
            raise StorageError(f"Invalid key: contains path traversal: {key}")

        # Validate against whitelist pattern
        if not self.VALID_KEY_PATTERN.match(key):
            raise StorageError(
                f"Invalid key: must contain only alphanumeric, /, -, _, . characters: {key}"
            )

        # Final security check - ensure resolved path is within storage directory
        resolved = (self.storage_dir / key).resolve()
        try:
            resolved.relative_to(self.storage_dir.resolve())
        except ValueError:
            raise StorageError(f"Invalid key: escapes storage directory: {key}")

        return key

    def _find_available_port(self, start_port: int, max_attempts: int = 10) -> int:
        """Find an available port starting from the given port.

        Args:
            start_port: Port to start searching from
            max_attempts: Maximum number of ports to try

        Returns:
            Available port number

        Raises:
            StorageError: If no available port found
        """
        import socket

        for offset in range(max_attempts):
            port = start_port + offset
            try:
                # Try to bind to the port
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind((self.config.local_bind, port))
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    return port
            except OSError:
                # Port is in use, try next one
                continue

        raise StorageError(
            f"Could not find available port in range {start_port}-{start_port + max_attempts - 1}"
        )

    def _start_server(self):
        """Start the HTTP server with atomic port allocation."""
        with self._server_lock:  # Make port allocation atomic
            try:
                handler = self._create_handler()

                # Try to find an available port if the configured one is in use
                actual_port = self.config.local_port
                try:
                    self._server = HTTPServer((self.config.local_bind, actual_port), handler)
                except OSError as e:
                    if e.errno == 48 or e.errno == 98:  # Address already in use (macOS/Linux)
                        logger.debug(
                            f"Port {actual_port} is already in use, searching for available port..."
                        )
                        actual_port = self._find_available_port(actual_port + 1)
                        self._server = HTTPServer((self.config.local_bind, actual_port), handler)
                        # Update config to reflect actual port being used
                        self.config.local_port = actual_port
                    else:
                        raise

                self._running = True
                self._server_thread = threading.Thread(
                    target=self._serve_forever, daemon=True, name="local-storage-server"
                )
                self._server_thread.start()

                logger.info(
                    f"Local storage server started on "
                    f"http://{self.config.local_bind}:{actual_port} "
                    f"(storage: {self.storage_dir})"
                )

            except StorageError:
                raise
            except OSError as e:
                raise StorageError(f"Failed to start HTTP server: {e}") from e

    def _serve_forever(self):
        """Serve requests until shutdown."""
        try:
            self._server.serve_forever()
        except Exception as e:
            if self._running:
                logger.error(f"Server error: {e}")

    def _create_handler(self):
        """Create HTTP request handler.

        Returns:
            Request handler class.
        """
        storage_dir = self.storage_dir

        class StorageHandler(SimpleHTTPRequestHandler):
            """Custom handler for serving stored files."""

            def __init__(self, *args, **kwargs):
                self.directory = str(storage_dir)
                super().__init__(*args, directory=self.directory, **kwargs)

            def log_message(self, format, *args):
                """Log only errors."""
                if args[1] != "200":
                    logger.debug(f"HTTP {args[1]}: {args[0]}")

            def do_GET(self):
                """Handle GET requests with security checks."""
                if ".." in self.path or self.path.startswith("/"):
                    self.send_error(403, "Forbidden")
                    return
                super().do_GET()

            def do_POST(self):
                """Reject POST requests."""
                self.send_error(405, "Method Not Allowed")

            def do_PUT(self):
                """Reject PUT requests."""
                self.send_error(405, "Method Not Allowed")

            def do_DELETE(self):
                """Reject DELETE requests."""
                self.send_error(405, "Method Not Allowed")

        return StorageHandler

    def store(
        self, key: str, data: bytes = None, content: bytes = None, metadata: dict[str, Any] = None
    ) -> StorageUrl:
        """Store content and return URL.

        Args:
            key: Storage key.
            data: Content to store (preferred parameter name).
            content: Content to store (backward compatibility).
            metadata: Optional metadata dictionary.

        Returns:
            StorageUrl for retrieving the content.

        Raises:
            StorageError: If storage fails.
        """
        # Support both 'data' and 'content' parameter names
        content_bytes = data if data is not None else content
        if content_bytes is None:
            raise StorageError("Either 'data' or 'content' must be provided")

        with self._operation_context("store"):
            # Validate content size before any disk operations
            if len(content_bytes) > self.config.max_file_size_bytes:
                raise StorageError(
                    f"Content size {len(content_bytes):,} bytes exceeds maximum "
                    f"{self.config.max_file_size_bytes:,} bytes"
                )

            # Sanitize key to prevent path traversal
            key = self._sanitize_key(key)
            file_path = self.storage_dir / key

            # Check available disk space before writing
            import shutil

            _, _, free_bytes = shutil.disk_usage(self.storage_dir)
            required_bytes = len(content_bytes) * 1.1  # 10% buffer
            if free_bytes < required_bytes:
                raise StorageError(
                    f"Insufficient disk space: need {required_bytes:,} bytes, "
                    f"have {free_bytes:,} bytes free"
                )

            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)

            content_hash = self._compute_hash(content_bytes)
            file_path.write_bytes(content_bytes)

            # Use provided metadata or create default
            content_type = "text/x-shellscript"
            if metadata and "content_type" in metadata:
                content_type = metadata["content_type"]

            storage_metadata = StorageMetadata(
                key=key,
                size_bytes=len(content_bytes),
                content_hash=content_hash,
                stored_at=datetime.now(timezone.utc),
                content_type=content_type,
            )

            # Store metadata
            meta_dict = {
                "size_bytes": storage_metadata.size_bytes,
                "content_hash": storage_metadata.content_hash,
                "stored_at": storage_metadata.stored_at.isoformat(),
                "content_type": storage_metadata.content_type,
            }

            # Add any additional metadata provided
            if metadata:
                for k, v in metadata.items():
                    if k not in meta_dict:
                        meta_dict[k] = v

            meta_path = file_path.with_suffix(".meta")
            meta_path.write_text(json.dumps(meta_dict))

            self._record_metric("total_bytes_stored", len(content_bytes))

            return self.get_url(key)

    def retrieve(self, key: str) -> bytes | None:
        """Retrieve content by key.

        Args:
            key: Storage key.

        Returns:
            Content bytes or None if not found.
        """
        with self._operation_context("retrieve"):
            key = self._sanitize_key(key)
            file_path = self.storage_dir / key

            if not file_path.exists():
                return None

            content = file_path.read_bytes()
            self._record_metric("total_bytes_retrieved", len(content))
            return content

    def delete(self, key: str) -> bool:
        """Delete content by key.

        Args:
            key: Storage key.

        Returns:
            True if deleted, False if not found.
        """
        with self._operation_context("delete"):
            key = self._sanitize_key(key)
            file_path = self.storage_dir / key
            meta_path = file_path.with_suffix(".meta")

            if not file_path.exists():
                return False

            file_path.unlink()
            if meta_path.exists():
                meta_path.unlink()

            return True

    def get_url(self, key: str) -> StorageUrl:
        """Get URL for content.

        Args:
            key: Storage key.

        Returns:
            StorageUrl for the content.
        """
        key = self._sanitize_key(key)
        # Use the actual port from the running server
        actual_port = self._server.server_port if self._server else self.config.local_port
        base_url = f"http://{self.config.local_bind}:{actual_port}"

        return StorageUrl(
            url=f"{base_url}/{quote(key)}",
            expires_at=datetime.now(timezone.utc)
            + timedelta(seconds=self.config.url_expiry_seconds),
        )

    def exists(self, key: str) -> bool:
        """Check if content exists.

        Args:
            key: Storage key.

        Returns:
            True if content exists.
        """
        try:
            key = self._sanitize_key(key)
            return (self.storage_dir / key).exists()
        except StorageError:
            return False

    def get_metadata(self, key: str) -> StorageMetadata | None:
        """Get metadata for content.

        Args:
            key: Storage key.

        Returns:
            StorageMetadata or None if not found.
        """
        try:
            key = self._sanitize_key(key)
            meta_path = (self.storage_dir / key).with_suffix(".meta")
        except StorageError:
            return None

        if meta_path.exists():
            try:
                meta_dict = json.loads(meta_path.read_text())
                return StorageMetadata(
                    key=key,
                    size_bytes=meta_dict["size_bytes"],
                    content_hash=meta_dict["content_hash"],
                    stored_at=datetime.fromisoformat(meta_dict["stored_at"]),
                    content_type=meta_dict.get("content_type", "text/x-shellscript"),
                )
            except Exception as e:
                logger.warning(f"Failed to load metadata for {key}: {e}")

        return None

    def health_check(self) -> dict[str, Any]:
        """Perform health check.

        Returns:
            Health check results.
        """
        try:
            server_running = self._running and self._server_thread.is_alive()
            storage_accessible = self.storage_dir.exists() and os.access(self.storage_dir, os.W_OK)

            import shutil

            total, used, free = shutil.disk_usage(self.storage_dir)

            return {
                "status": "healthy" if server_running and storage_accessible else "unhealthy",
                "server_running": server_running,
                "storage_accessible": storage_accessible,
                "storage_path": str(self.storage_dir),
                "disk_usage": {
                    "total_gb": total / (1024**3),
                    "used_gb": used / (1024**3),
                    "free_gb": free / (1024**3),
                    "percent_used": (used / total * 100) if total > 0 else 0,
                },
                "metrics": self.get_metrics() if self.config.enable_metrics else {},
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }

    def close(self):
        """Shut down the server and clean up resources."""
        try:
            if self._atexit_handler:
                atexit.unregister(self._atexit_handler)
                self._atexit_handler = None

            logger.info("Shutting down local storage server...")

            self._running = False

            # Shutdown server first
            if self._server:
                try:
                    self._server.socket.settimeout(1.0)
                    self._server.shutdown()
                    self._server.server_close()
                except Exception as e:
                    logger.debug(f"Server shutdown error (may be expected): {e}")

            # Wait for server thread to complete
            if self._server_thread and self._server_thread.is_alive():
                self._server_thread.join(timeout=2.0)

            # Properly shutdown executor with timeout
            if self._executor:
                try:
                    self._executor.shutdown(wait=True, timeout=5.0)
                except Exception as e:
                    logger.debug(f"Executor shutdown error: {e}")
                    # Force shutdown if graceful shutdown fails
                    self._executor.shutdown(wait=False)

            logger.info("Local storage server shut down")
        except Exception as e:
            logger.error(f"Error during server shutdown: {e}")


def create_storage_backend(config: StorageConfig) -> IStorageBackend:
    """Create a storage backend from configuration.

    Args:
        config: Storage configuration.

    Returns:
        Storage backend instance.

    Raises:
        StorageError: If configuration is invalid or backend creation fails.
    """
    try:
        config.validate()
    except ValueError as e:
        raise StorageError(f"Invalid storage configuration: {e}") from e

    if config.backend_type == "local":
        return LocalHttpBackend(config)
    else:
        raise StorageError(f"Unknown storage backend type: {config.backend_type}")
