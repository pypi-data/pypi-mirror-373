"""Volume index cache for quick volume references.

Provides ephemeral index-based volume references (e.g., 1, 2; legacy :1, :2) based on the
last shown volume list. Behavior is explicit and time-bounded to prevent stale
references.
"""

from pathlib import Path

from flow.cli.utils.index_cache_base import BaseIndexCache
from flow.sdk.models import Volume


class VolumeIndexCache(BaseIndexCache):
    """Manages ephemeral volume index mappings.

    Stores mappings from display indices to volume IDs, allowing users
    to reference volumes by position (e.g., :1, :2) from the last volume
    list display. Indices expire after 5 minutes to prevent stale references.
    """

    CACHE_TTL_SECONDS = 300  # 5 minutes

    def __init__(self, cache_dir: Path | None = None):
        """Initialize cache with optional custom directory."""
        super().__init__("volume_indices.json", cache_dir)

    def save_indices(self, volumes: list[Volume]) -> None:
        """Save volume indices from a displayed list.

        Args:
            volumes: Ordered list of volumes as displayed
        """
        # Create directory if needed
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Build index mapping (1-based for user friendliness)
        indices = {str(i + 1): volume.id for i, volume in enumerate(volumes)}

        # Cache full volume details for instant access
        volume_details = {}
        for volume in volumes:
            volume_details[volume.id] = {
                "id": volume.id,
                "name": volume.name,
                "region": volume.region,
                "size_gb": volume.size_gb,
                "interface": getattr(volume, "interface", "block"),
                "created_at": volume.created_at.isoformat() if volume.created_at else None,
            }

        payload = {
            "indices": indices,
            "volume_details": volume_details,
            "volume_count": len(volumes),
            # Scope on-disk indices to current provider/project context when known
            "context": self._current_context(),
        }

        self._ttl().save(payload)

    def resolve_index(self, index_str: str) -> tuple[str | None, str | None]:
        """Resolve an index reference to a volume ID.

        Args:
            index_str: Index string (e.g., "1", ":1")

        Returns:
            Tuple of (volume_id if found, error message if any)
        """
        # Parse index
        if index_str.startswith(":"):
            raw = index_str[1:]
        else:
            raw = index_str

        try:
            index = int(raw)
        except ValueError:
            return None, f"Invalid index format: {index_str}"

        if index < 1:
            return None, "Index must be positive"

        # Load cache
        cache_data = self._ttl().load()
        if not cache_data:
            return None, "No recent volume list. Run 'flow volumes get' first"

        # Look up index
        volume_id = cache_data["indices"].get(str(index))
        if not volume_id:
            max_index = cache_data["volume_count"]
            return None, f"Index {index} out of range (1-{max_index})"

        return volume_id, None

    def _load_cache(self) -> dict | None:
        return super()._load_cache()

    def get_cached_volume(self, volume_id: str) -> dict | None:
        """Get cached volume details if available.

        Args:
            volume_id: Volume ID to look up

        Returns:
            Volume details dict or None if not cached/expired
        """
        cache_data = self._ttl().load()
        if not cache_data:
            return None
        return cache_data.get("volume_details", {}).get(volume_id)

    def clear(self) -> None:
        super().clear()
