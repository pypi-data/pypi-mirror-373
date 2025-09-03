from __future__ import annotations

import textwrap

from flow.adapters.providers.builtin.mithril.runtime.startup.sections.base import (
    ScriptContext,
    ScriptSection,
)
from flow.adapters.providers.builtin.mithril.volume_operations import VolumeOperations


class VolumeSection(ScriptSection):
    @property
    def name(self) -> str:
        return "volumes"

    @property
    def priority(self) -> int:
        return 30

    def should_include(self, context: ScriptContext) -> bool:
        return bool(context.volumes)

    def generate(self, context: ScriptContext) -> str:
        if not context.volumes:
            return ""
        mount_commands = []
        for i, volume in enumerate(context.volumes):
            if volume.get("interface") == "file":
                mount_commands.append(self._generate_file_mount(i, volume))
            else:
                mount_commands.append(self._generate_block_mount(i, volume))
        mount_blob = "\n".join(mount_commands)
        return textwrap.dedent(
            f"""
            echo "Mounting {len(context.volumes)} volume(s)"
            {mount_blob}
            echo "Mounted volumes:"
            mount | grep -E "(^/dev/(vd|xvd)[f-z]|type nfs)" || true
        """
        ).strip()

    def _generate_file_mount(self, index: int, volume: dict[str, object]) -> str:
        mount_path = str(volume.get("mount_path", f"/data{index}"))
        volume_id = volume.get("volume_id")
        return VolumeOperations.generate_mount_script(
            volume_index=index, mount_path=mount_path, volume_id=volume_id, is_file_share=True
        )

    def _generate_block_mount(self, index: int, volume: dict[str, object]) -> str:
        mount_path = str(volume.get("mount_path", f"/data{index}"))
        volume_index = index + 2
        return VolumeOperations.generate_mount_script(
            volume_index=volume_index,
            mount_path=mount_path,
            format_if_needed=True,
            add_to_fstab=True,
            is_file_share=False,
        )

    def validate(self, context: ScriptContext) -> list[str]:
        errors: list[str] = []
        if len(context.volumes or []) > 20:
            errors.append(f"Too many volumes: {len(context.volumes)} (max 20)")
        for i, volume in enumerate(context.volumes or []):
            mount_path = str(volume.get("mount_path", f"/data{i}"))
            if not mount_path.startswith("/"):
                errors.append(f"Volume {i}: mount_path must be absolute: {mount_path}")
            interface = volume.get("interface")
            if interface not in (None, "block", "file"):
                errors.append(
                    f"Volume {i}: invalid interface '{interface}'. Allowed: 'block' or 'file'"
                )
        return errors


__all__ = ["VolumeSection"]
