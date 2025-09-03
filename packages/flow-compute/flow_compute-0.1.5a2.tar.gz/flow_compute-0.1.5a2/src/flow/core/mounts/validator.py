"""Mount validator (core) that wraps centralized rules."""

from __future__ import annotations


class MountValidator:
    def validate(self, mounts: dict[str, str]) -> list[str]:
        warnings: list[str] = []
        # Overlapping targets
        for target in mounts:
            for other in mounts:
                if target != other and target.startswith(other + "/"):
                    warnings.append(f"Mount target '{target}' is inside '{other}'")
        # System directories
        system_dirs = ["/bin", "/etc", "/proc", "/sys", "/dev", "/tmp"]
        for target in mounts:
            if any(target.startswith(d) for d in system_dirs):
                warnings.append(f"Mount target '{target}' overlaps with system directory")
        return warnings
