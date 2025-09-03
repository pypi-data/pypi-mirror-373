"""URL resolution to mount specifications."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Protocol
from urllib.parse import urlparse

from flow.errors import FlowError
from flow.sdk.models import MountSpec

if TYPE_CHECKING:  # avoid runtime import to prevent circular dependency
    from flow.protocols.provider import ProviderProtocol as IProvider  # pragma: no cover
else:
    IProvider = object  # type: ignore


class DataError(FlowError):
    """Data access errors."""

    pass


class ILoader(Protocol):
    """Loader protocol - single method interface."""

    def resolve(self, url: str, provider: IProvider) -> MountSpec:
        """Convert URL to mount specification."""
        ...


class URLResolver:
    """Resolves URLs to mount specifications.

    Simple, direct mapping from URL schemes to loaders. No complexity,
    no registration, just a dictionary lookup.

    Performance: O(1) scheme lookup, <1ms per resolution.
    Thread-safe: No shared mutable state between resolve() calls.

    Examples:
        >>> resolver = URLResolver()
        >>> spec = resolver.resolve("volume://my-data", "/data", provider)
        >>> spec.mount_type
        'volume'
        >>> spec = resolver.resolve("s3://bucket/path", "/datasets", provider)
        >>> spec.mount_type
        's3fs'
    """

    def __init__(self):
        # Import loaders here to avoid circular imports
        # (loaders import DataError from this module)
        from flow.core.data.loaders import S3Loader, VolumeLoader

        self._loaders: dict[str, ILoader] = {
            "volume": VolumeLoader(),
            "s3": S3Loader(),
        }

    def add_loader(self, scheme: str, loader: ILoader) -> None:
        """Add a loader for a URL scheme."""
        self._loaders[scheme] = loader

    def resolve(self, url: str, target: str, provider: IProvider) -> MountSpec:
        """Resolve URL to mount specification.

        Args:
            url: Data URL (volume://name, /path, etc.)
            target: Mount path in container
            provider: Provider instance for capability checks

        Returns:
            MountSpec ready for provider consumption

        Raises:
            DataError: If URL cannot be resolved
        """
        # Parse URL
        parsed = urlparse(url)

        # Local paths (no scheme or file://)
        if not parsed.scheme or parsed.scheme == "file":
            # Simple bind mount
            abspath = os.path.abspath(url if not parsed.scheme else parsed.path)
            if not os.path.exists(abspath):
                raise DataError(
                    f"Local path does not exist: {abspath}",
                    suggestions=["Check the path exists", "Use absolute paths"],
                )
            return MountSpec(
                source=abspath, target=target, mount_type="bind", options={"readonly": True}
            )

        # Delegate to loader
        loader = self._loaders.get(parsed.scheme)
        if not loader:
            raise DataError(
                f"Unsupported URL scheme: {parsed.scheme}://",
                suggestions=[
                    (
                        f"Supported schemes: {', '.join(self._loaders.keys())}"
                        if self._loaders
                        else "No schemes registered yet"
                    ),
                    "Use local paths without scheme",
                ],
            )

        spec = loader.resolve(url, provider)
        spec.target = target  # Override with user-specified target
        return spec
