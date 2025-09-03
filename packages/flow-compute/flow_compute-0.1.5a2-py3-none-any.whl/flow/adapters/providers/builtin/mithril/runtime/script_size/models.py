"""Data models for script size handling."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PreparedScript:
    """Result of preparing a script for submission.

    Contains the final script content (possibly transformed) and metadata
    about how it was prepared.
    """

    content: str
    strategy: str
    requires_network: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def size_bytes(self) -> int:
        """Get the size of the prepared script in bytes."""
        return len(self.content.encode("utf-8"))

    @property
    def original_size(self) -> int | None:
        """Get the original script size if stored in metadata."""
        return self.metadata.get("original_size")

    @property
    def compression_ratio(self) -> float | None:
        """Get compression ratio if script was compressed."""
        if self.strategy == "compressed" and self.original_size:
            return self.original_size / self.size_bytes
        return None
