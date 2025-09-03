"""Mithril-specific mount adaptation.

Converts generic MountSpec objects to Mithril-specific formats:
- volume:// -> VolumeSpec for attachment
- s3:// -> Environment variables for startup script

Mithril Mount Implementation Details:
1. Volume mounts:
   - Converted to VolumeSpec objects
   - Attached at instance creation time via Mithril API
   - Automatically mounted by Mithril at specified paths

2. S3 mounts:
   - Converted to environment variables (S3_MOUNT_N_*)
   - S3Section in startup script reads these variables
   - Mounts via s3fs-fuse during instance initialization
   - Requires AWS credentials in environment

Environment Variable Format:
- S3_MOUNT_0_BUCKET: bucket name
- S3_MOUNT_0_PATH: path within bucket (empty for root)
- S3_MOUNT_0_TARGET: mount point on instance
- S3_MOUNTS_COUNT: total number of S3 mounts
"""

from flow.errors import ValidationError
from flow.sdk.models import MountSpec, VolumeSpec


class MithrilMountAdapter:
    """Adapts generic mount specifications to Mithril-specific format.

    Mithril uses:
    - Direct volume attachment for volume:// mounts
    - Environment variables for s3:// mounts (processed by startup script)
    """

    def adapt_mounts(self, mounts: list[MountSpec]) -> tuple[list[VolumeSpec], dict[str, str]]:
        """Convert generic mount specs to Mithril-specific format.

        Args:
            mounts: List of resolved MountSpec objects

        Returns:
            Tuple of:
            - volumes: VolumeSpec list for attachment
            - env_vars: Environment variables for S3 mounts
        """
        volumes = []
        env_vars = {}
        s3_mount_index = 0

        for mount in mounts:
            if mount.mount_type == "volume":
                volume_spec = self._mount_to_volume(mount)
                volumes.append(volume_spec)
            elif mount.mount_type == "s3fs":
                mount_env = self._s3_to_env(mount, s3_mount_index)
                env_vars.update(mount_env)
                s3_mount_index += 1
            else:
                # Mithril only supports volume and S3 mounts
                raise ValidationError(
                    f"Mithril does not support mount type: {mount.mount_type}. "
                    f"Only volume:// and s3:// are supported."
                )

        # Add S3 mount count for startup script
        if s3_mount_index > 0:
            env_vars["S3_MOUNTS_COUNT"] = str(s3_mount_index)

        return volumes, env_vars

    def _mount_to_volume(self, mount: MountSpec) -> VolumeSpec:
        """Convert volume mount to VolumeSpec.

        Args:
            mount: Resolved mount specification with volume_id

        Returns:
            VolumeSpec for Mithril volume attachment
        """
        volume_id = mount.options.get("volume_id")
        if not volume_id:
            raise ValidationError(f"Volume mount missing volume_id: {mount.source}")

        return VolumeSpec(volume_id=volume_id, mount_path=mount.target)

    def _s3_to_env(self, mount: MountSpec, index: int) -> dict[str, str]:
        """Convert S3 mount to Mithril environment variables.

        Mithril uses environment variables to pass S3 mount info to startup script.
        The S3Section in script_sections.py expects these specific patterns.

        Args:
            mount: Resolved S3 mount specification
            index: S3 mount index for unique env var names

        Returns:
            Environment variables for Mithril S3 mounting
        """
        bucket = mount.options.get("bucket")
        path = mount.options.get("path", "")

        if not bucket:
            raise ValidationError(f"S3 mount missing bucket: {mount.source}")

        # Generate Mithril-specific environment variables
        mount_key = f"S3_MOUNT_{index}"
        return {
            f"{mount_key}_BUCKET": bucket,
            f"{mount_key}_PATH": path,
            f"{mount_key}_TARGET": mount.target,
        }
