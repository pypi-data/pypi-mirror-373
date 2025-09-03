"""Mount specification parser for storage mounts (core owner).

This implements the parsing and validation logic used across the SDK.
The CLI re-exports this class for backward compatibility.
"""

from __future__ import annotations

from flow.core.mount_rules import auto_target_for_source


class MountParser:
    """Parse and validate mount specifications.

    Supports two input formats per item:
    - "source" (auto-generates target based on source scheme)
    - "target=source" (explicit target path)
    """

    # Deprecated: kept for backward compatibility in docs; logic now centralized
    AUTO_MOUNT_RULES = {"s3://": "/data", "volume://": "/volumes"}

    def parse_mounts(self, mount_specs: tuple[str, ...]) -> dict[str, str] | None:
        """Parse mount specifications into target:source mapping.

        Args:
            mount_specs: Tuple of mount specifications in format:
                - "source" (auto-generates target)
                - "target=source" (explicit target)

        Returns:
            Dictionary mapping target paths to source paths,
            or None if no mounts specified.
        """
        if not mount_specs:
            return None

        mount_dict: dict[str, str] = {}

        for mount_spec in mount_specs:
            target, source = self._parse_single_mount(mount_spec)

            # Check for duplicate targets
            if target in mount_dict:
                raise ValueError(
                    f"Duplicate mount target '{target}'. "
                    f"Both '{mount_dict[target]}' and '{source}' mount to the same path."
                )

            mount_dict[target] = source

        return mount_dict

    def _parse_single_mount(self, mount_spec: str) -> tuple[str, str]:
        """Parse a single mount specification.

        Returns a tuple of (target, source). Raises ValueError for invalid input.
        """
        if not mount_spec:
            raise ValueError("Empty mount specification")

        if "=" in mount_spec:
            # Format: target=source
            parts = mount_spec.split("=", 1)
            if len(parts) != 2 or not parts[0] or not parts[1]:
                raise ValueError(f"Invalid mount specification: '{mount_spec}'")

            target, source = parts

            # Validate target path
            if not target.startswith("/"):
                raise ValueError(f"Mount target must be an absolute path: '{target}'")

            return target, source
        else:
            # Format: source (auto-generate target)
            source = mount_spec
            target = self._generate_target_path(source)
            return target, source

    def _generate_target_path(self, source: str) -> str:
        """Generate target path based on source type using centralized rules."""
        return auto_target_for_source(source)

    def validate_mounts(self, mounts: dict[str, str]) -> list[str]:
        """Validate mount configuration, returning non-fatal warnings."""
        warnings: list[str] = []

        for target, _source in mounts.items():
            # Check for overlapping mount points
            for other_target in mounts:
                if target != other_target and target.startswith(other_target + "/"):
                    warnings.append(f"Mount target '{target}' is inside '{other_target}'")

            # Warn about common system directories
            system_dirs = ["/bin", "/etc", "/proc", "/sys", "/dev", "/tmp"]
            if any(target.startswith(d) for d in system_dirs):
                warnings.append(f"Mount target '{target}' overlaps with system directory")

        return warnings

    def format_mounts_display(self, mounts: dict[str, str]) -> list[str]:
        """Format mounts for display as a sorted list of 'target → source' lines."""
        if not mounts:
            return []
        return [f"{target} → {source}" for target, source in sorted(mounts.items())]
