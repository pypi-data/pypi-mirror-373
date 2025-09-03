"""Storage data models."""

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class StorageUrl:
    """Represents a URL with metadata for stored content."""

    url: str
    expires_at: datetime | None = None
    content_type: str = "text/x-shellscript"
    size_bytes: int | None = None

    @property
    def is_expired(self) -> bool:
        """Check if the URL has expired."""
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at


@dataclass
class StorageMetadata:
    """Metadata about stored content."""

    key: str
    size_bytes: int
    content_hash: str
    stored_at: datetime
    content_type: str = "text/x-shellscript"
    compression: str | None = None
    original_size_bytes: int | None = None
