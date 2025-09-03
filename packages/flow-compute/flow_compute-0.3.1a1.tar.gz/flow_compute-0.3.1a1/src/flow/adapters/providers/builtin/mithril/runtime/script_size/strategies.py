"""Transfer strategies for handling scripts of different sizes."""

import base64
import gzip
import hashlib
import logging
from typing import Protocol

from flow.adapters.providers.builtin.mithril.runtime.script_size.models import PreparedScript
from flow.adapters.providers.builtin.mithril.runtime.script_size.templates import BootstrapTemplates
from flow.adapters.providers.builtin.mithril.storage import IStorageBackend

logger = logging.getLogger(__name__)


class ITransferStrategy(Protocol):
    """Protocol for script transfer strategies."""

    def can_handle(self, script: str, max_size: int) -> bool:
        """Check if this strategy can handle the script.

        Args:
            script: The script content
            max_size: Maximum allowed size in bytes

        Returns:
            True if this strategy can handle the script
        """
        ...

    def prepare(self, script: str, max_size: int) -> PreparedScript:
        """Prepare script for submission.

        Args:
            script: The script content
            max_size: Maximum allowed size in bytes

        Returns:
            PreparedScript with transformed content
        """
        ...

    @property
    def name(self) -> str:
        """Strategy name for identification."""
        ...


class InlineStrategy:
    """Strategy for scripts small enough to send directly.

    This is the simplest and most efficient strategy, used when
    scripts are already under the size limit.
    """

    @property
    def name(self) -> str:
        return "inline"

    def can_handle(self, script: str, max_size: int) -> bool:
        """Check if script is small enough to send inline."""
        # Leave 1KB safety margin for Mithril metadata
        safety_margin = 1000
        return len(script.encode("utf-8")) < max_size - safety_margin

    def prepare(self, script: str, max_size: int) -> PreparedScript:
        """Return script as-is since it's small enough."""
        script_size = len(script.encode("utf-8"))

        logger.debug(f"Using inline strategy for script of {script_size} bytes")

        return PreparedScript(
            content=script,
            strategy=self.name,
            requires_network=False,
            metadata={
                "original_size": script_size,
            },
        )


class CompressionStrategy:
    """Strategy using gzip compression with base64 encoding.

    Compresses the script and creates a bootstrap script that
    decompresses and executes it on the instance.
    """

    @property
    def name(self) -> str:
        return "compressed"

    def can_handle(self, script: str, max_size: int) -> bool:
        """Check if compressed script will fit within limit."""
        # Quick size estimate without full template rendering
        original_size = len(script.encode("utf-8"))
        compressed_bytes = gzip.compress(script.encode("utf-8"), compresslevel=9)
        compressed_size = len(compressed_bytes)

        # Estimate bootstrap size (template overhead + compressed data)
        template_overhead = 2000  # Conservative estimate for template
        compressed_base64_size = len(base64.b64encode(compressed_bytes))
        estimated_size = template_overhead + compressed_base64_size

        return estimated_size < max_size - 1000  # Safety margin

    def prepare(self, script: str, max_size: int) -> PreparedScript:
        """Compress script and create bootstrap."""
        original_size = len(script.encode("utf-8"))
        compressed_bytes = gzip.compress(script.encode("utf-8"), compresslevel=9)
        compressed_data = base64.b64encode(compressed_bytes).decode("ascii")
        compressed_size = len(compressed_bytes)

        # Calculate hash of compressed data for integrity check
        script_hash = hashlib.sha256(compressed_bytes).hexdigest()

        # Format compressed data with standard line length
        lines = []
        line_length = 76  # Standard base64 line length
        for i in range(0, len(compressed_data), line_length):
            lines.append(compressed_data[i : i + line_length])
        compressed_lines = "\n".join(lines)

        # Use template to generate bootstrap
        bootstrap = BootstrapTemplates.render_compression_bootstrap(
            compressed_data=compressed_lines,
            script_hash=script_hash,
            original_size=original_size,
            compressed_size=compressed_size,
        )

        final_size = len(bootstrap.encode("utf-8"))

        logger.info(
            f"Compressed script from {original_size:,} to {final_size:,} bytes "
            f"(ratio: {original_size / final_size:.2f}x)"
        )

        return PreparedScript(
            content=bootstrap,
            strategy=self.name,
            requires_network=False,
            metadata={
                "original_size": original_size,
                "compressed_size": compressed_size,
                "compression_ratio": original_size / final_size,
                "script_hash": script_hash,
            },
        )


class SplitStrategy:
    """Strategy that splits script into bootstrap + downloadable payload.

    Stores the actual script in external storage and creates a minimal
    bootstrap script that downloads and executes it.
    """

    def __init__(self, storage: IStorageBackend):
        """Initialize with storage backend.

        Args:
            storage: Storage backend for storing script payloads
        """
        self.storage = storage

    @property
    def name(self) -> str:
        return "split"

    def can_handle(self, script: str, max_size: int) -> bool:
        """Check if script can be handled via splitting.

        We limit to 100MB as a reasonable maximum for download.
        """
        script_size = len(script.encode("utf-8"))
        return script_size < 100_000_000  # 100MB limit

    def prepare(self, script: str, max_size: int) -> PreparedScript:
        """Store script and create download bootstrap."""
        script_bytes = script.encode("utf-8")
        script_size = len(script_bytes)

        # Generate content-addressed storage key
        script_hash = hashlib.sha256(script_bytes).hexdigest()
        storage_key = f"scripts/{script_hash[:8]}/{script_hash}"

        # Store script
        logger.info(f"Storing {script_size:,} byte script with hash {script_hash[:16]}...")
        storage_url = self.storage.store(
            key=storage_key,
            data=script_bytes,
            metadata={
                "content_type": "text/x-shellscript",
                "script_hash": script_hash,
            },
        )

        # Create bootstrap script using template
        bootstrap = BootstrapTemplates.render_storage_bootstrap(
            storage_url=storage_url.url, script_hash=script_hash, script_size=script_size
        )

        logger.info(
            f"Created bootstrap script ({len(bootstrap):,} bytes) for "
            f"downloading {script_size:,} byte payload from {storage_url.url}"
        )

        return PreparedScript(
            content=bootstrap,
            strategy=self.name,
            requires_network=True,
            metadata={
                "original_size": script_size,
                "payload_url": storage_url.url,
                "sha256": script_hash,
                "storage_key": storage_key,
                "expires_at": (
                    storage_url.expires_at.isoformat() if storage_url.expires_at else None
                ),
            },
        )
