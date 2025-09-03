"""Storage interface mapping for Mithril.

This module handles the mapping between Mithril's storage representations
and our domain model's storage interfaces.
"""

from flow.sdk.models import StorageInterface


class MithrilStorageMapper:
    """Maps Mithril storage details to domain storage interfaces.

    Mithril might represent storage differently than our domain model.
    This class encapsulates that knowledge.
    """

    @staticmethod
    def determine_interface(
        mount_path: str | None = None,
        device_type: str | None = None,
        volume_type: str | None = None,
        mithril_metadata: dict | None = None,
    ) -> StorageInterface:
        """Determine storage interface from Mithril volume data.

        Args:
            mount_path: Mount path from Mithril (e.g., "/dev/nvme0n1", "/dev/vda")
            device_type: Device type if provided by Mithril
            volume_type: Volume type from Mithril (e.g., "ssd", "nvme", "standard")
            mithril_metadata: Any additional Mithril metadata

        Returns:
            Appropriate StorageInterface enum value

        Note:
            This is where we encode our understanding of how Mithril
            represents different storage types. As we learn more about
            Mithril's API, we can make this more sophisticated.
        """
        # If API reported an explicit disk_interface, honor it first
        if mithril_metadata and mithril_metadata.get("disk_interface"):
            reported = str(mithril_metadata.get("disk_interface")).lower()
            if reported in {"file", "fileshare", "file share"}:
                return StorageInterface.FILE
            # Treat anything else (including "block") as block
            return StorageInterface.BLOCK

        # If we have explicit device type information
        if device_type:
            device_lower = device_type.lower()
            if "nvme" in device_lower:
                return StorageInterface.BLOCK  # NVMe is block storage
            elif "file" in device_lower or "nfs" in device_lower:
                return StorageInterface.FILE

        # Infer from mount path if available
        if mount_path:
            path_lower = mount_path.lower()
            if "/dev/nvme" in path_lower:
                return StorageInterface.BLOCK  # NVMe devices
            elif "/dev/vd" in path_lower or "/dev/sd" in path_lower:
                return StorageInterface.BLOCK  # Virtual/SCSI block devices
            elif path_lower.startswith("/mnt/") or path_lower.startswith("/data/"):
                # Could be either - need more info
                pass

        # Check volume type
        if volume_type:
            type_lower = volume_type.lower()
            if type_lower in ["ssd", "nvme", "standard", "persistent"]:
                return StorageInterface.BLOCK
            elif type_lower in ["nfs", "shared", "file"]:
                return StorageInterface.FILE

        # Default: In cloud environments, most volumes are block storage
        # This is a reasonable default, not a hack, because:
        # 1. Block storage is the most common type in cloud
        # 2. Mithril is a cloud provider
        # 3. We document this assumption
        return StorageInterface.BLOCK

    @staticmethod
    def get_device_path(interface: StorageInterface, index: int = 0) -> str:
        """Generate appropriate device path for given interface.

        Args:
            interface: Storage interface type
            index: Device index for multiple volumes

        Returns:
            Device path string
        """
        if interface == StorageInterface.BLOCK:
            # Mithril might use different conventions
            # This is our best guess based on common cloud patterns
            return f"/dev/disk{index}" if index > 0 else "/dev/disk0"
        else:
            # File storage typically mounts to paths
            return f"/mnt/storage{index}" if index > 0 else "/mnt/storage"
