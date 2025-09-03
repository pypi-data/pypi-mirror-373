"""Centralized Docker configuration and utilities."""

import logging
from enum import Enum

logger = logging.getLogger(__name__)


class DockerSystemPath(Enum):
    """Well-known Docker system paths with semantic meaning."""

    STORAGE = "/var/lib/docker"  # Docker's layer storage
    SOCKET = "/var/run/docker.sock"  # Docker daemon socket
    CONFIG = "/etc/docker"  # Docker configuration


class DockerConfig:
    """Docker-specific configuration and validation.

    This class provides centralized Docker knowledge to prevent
    duplication and ensure consistent behavior across providers.
    """

    # Docker system paths that shouldn't be mounted inside containers
    RESTRICTED_MOUNT_PATHS: set[str] = {path.value for path in DockerSystemPath}

    @classmethod
    def is_restricted_mount(cls, path: str) -> bool:
        """Check if a path should not be mounted inside containers.

        These paths would conflict with the container's own Docker daemon
        or expose sensitive host configuration.

        Args:
            path: The mount path to check

        Returns:
            True if the path is restricted and shouldn't be mounted
        """
        return path in cls.RESTRICTED_MOUNT_PATHS

    @classmethod
    def get_cache_volume_path(cls) -> str:
        """Get the standard Docker cache volume path.

        This is the path where Docker stores image layers and build cache.
        Mounting this path on the host provides persistent caching across
        container restarts.

        Returns:
            The Docker storage path
        """
        return DockerSystemPath.STORAGE.value

    @classmethod
    def should_mount_in_container(cls, mount_path: str) -> bool:
        """Determine if a volume should be mounted inside the container.

        This is the inverse of is_restricted_mount, provided for clearer
        intent at the call site.

        Args:
            mount_path: The path to potentially mount

        Returns:
            True if the path should be mounted in the container
        """
        return not cls.is_restricted_mount(mount_path)
