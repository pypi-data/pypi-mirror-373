"""Volume resolution utilities for CLI.

Provides functions to resolve volume identifiers (names or IDs) to actual
Volume objects, similar to task resolution functionality.
"""

from flow.cli.utils.volume_index_cache import VolumeIndexCache
from flow.sdk.client import Flow
from flow.sdk.models import Volume


def resolve_volume_identifier(
    flow_client: Flow, identifier: str
) -> tuple[Volume | None, str | None]:
    """Resolve a volume identifier (name or ID) to a Volume object.

    Resolution order:
    1. Index reference (e.g., 1, 2, or legacy ":1", ":2")
    2. Exact volume ID match
    3. Exact name match
    4. Partial name match

    Args:
        flow_client: Flow client instance
        identifier: Volume ID (vol_xxx), name, or index reference

    Returns:
        Tuple of (volume, error_message)
        - volume: The resolved Volume object if found
        - error_message: Error description if not found
    """
    # Check for index reference first (e.g., 1, 2 or legacy :1, :2)
    if identifier.startswith(":"):
        cache = VolumeIndexCache()
        volume_id, error = cache.resolve_index(identifier)
        if error:
            return None, error
        if volume_id:
            # Resolve the cached volume ID
            identifier = volume_id
    else:
        # Accept bare single-index form for consistency with task indices (e.g., "2")
        import re as _re

        if _re.fullmatch(r"\d+", identifier):
            cache = VolumeIndexCache()
            volume_id, error = cache.resolve_index(f":{identifier}")
            if error:
                return None, error
            if volume_id:
                identifier = volume_id

    # Check if it's a volume ID via provider interface
    provider = flow_client.provider
    if hasattr(provider, "is_volume_id") and provider.is_volume_id(identifier):
        # Try to find by ID
        volumes = flow_client.volumes.list()
        for volume in volumes:
            if volume.volume_id == identifier:
                return volume, None
        return None, f"Volume not found: {identifier}"

    # Otherwise treat as name
    volumes = flow_client.volumes.list()

    # Look for exact name match first
    exact_matches = [v for v in volumes if v.name == identifier]
    if len(exact_matches) == 1:
        return exact_matches[0], None
    elif len(exact_matches) > 1:
        # Multiple volumes with same name - show them
        ids = [v.volume_id for v in exact_matches]
        return None, (
            f"Multiple volumes found with name '{identifier}':\n"
            + "\n".join(f"  • {vid}" for vid in ids)
            + "\n\nPlease use the volume ID instead."
        )

    # Try partial name match
    partial_matches = [v for v in volumes if v.name and identifier.lower() in v.name.lower()]
    if len(partial_matches) == 1:
        return partial_matches[0], None
    elif len(partial_matches) > 1:
        # Show all partial matches
        matches_info = []
        for v in partial_matches[:5]:  # Limit to 5 to avoid spam
            matches_info.append(f"  • {v.volume_id} ({v.name})")

        msg = f"Multiple volumes found matching '{identifier}':\n" + "\n".join(matches_info)
        if len(partial_matches) > 5:
            msg += f"\n  ... and {len(partial_matches) - 5} more"
        msg += "\n\nPlease be more specific or use the volume ID."
        return None, msg

    # No matches found
    return None, f"No volume found matching: {identifier}"


def get_volume_display_name(volume: Volume) -> str:
    """Get a display name for a volume, preferring name over ID.

    Args:
        volume: Volume object

    Returns:
        Display string in format "name (id)" or just "id" if no name
    """
    if volume.name:
        return f"{volume.name} ({volume.volume_id})"
    return volume.volume_id
