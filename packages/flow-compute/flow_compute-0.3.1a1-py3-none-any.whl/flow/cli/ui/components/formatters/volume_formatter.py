"""Volume-specific formatting for interactive selection."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flow.cli.ui.components.models import SelectionItem
    from flow.sdk.models import Volume


class VolumeFormatter:
    """Formats volumes for display in the interactive selector."""

    @staticmethod
    def to_selection_item(volume: Volume) -> SelectionItem:
        """Convert a Volume to a SelectionItem.

        Args:
            volume: Volume to convert

        Returns:
            SelectionItem for display
        """
        from flow.cli.ui.components.models import SelectionItem

        # Build subtitle with volume metadata
        subtitle_parts = []

        # Add size if available
        if hasattr(volume, "size") and volume.size:
            subtitle_parts.append(f"{volume.size}GB")

        # Add region if available
        if hasattr(volume, "region") and volume.region:
            subtitle_parts.append(volume.region)

        # Add mount path if available
        if hasattr(volume, "mount_path") and volume.mount_path:
            subtitle_parts.append(f"→ {volume.mount_path}")

        subtitle = " • ".join(subtitle_parts) if subtitle_parts else None

        # Determine status
        status = None
        if hasattr(volume, "status"):
            status = volume.status
        elif hasattr(volume, "state"):
            status = volume.state

        return SelectionItem(
            value=volume,
            id=volume.id,
            title=volume.name or volume.id,
            subtitle=subtitle,
            status=status,
            extra={"volume": volume},
        )

    @staticmethod
    def format_preview(item: SelectionItem[Volume]) -> str:
        """Format a volume preview for the detail pane.

        Args:
            item: SelectionItem containing a Volume

        Returns:
            Formatted preview string
        """
        volume = item.value
        lines = []

        lines.append(f"Volume: {volume.name or volume.id}")

        if hasattr(volume, "status"):
            lines.append(f"Status: {volume.status}")
        elif hasattr(volume, "state"):
            lines.append(f"State: {volume.state}")

        if hasattr(volume, "size") and volume.size:
            lines.append(f"Size: {volume.size}GB")

        if hasattr(volume, "region") and volume.region:
            lines.append(f"Region: {volume.region}")

        if hasattr(volume, "mount_path") and volume.mount_path:
            lines.append(f"Mount Path: {volume.mount_path}")

        if hasattr(volume, "created_at") and volume.created_at:
            lines.append(f"Created: {volume.created_at}")

        if hasattr(volume, "attached_to") and volume.attached_to:
            lines.append(f"Attached To: {volume.attached_to}")

        if hasattr(volume, "description") and volume.description:
            lines.append("")
            lines.append("Description:")
            lines.append(volume.description)

        return "\n".join(lines)
