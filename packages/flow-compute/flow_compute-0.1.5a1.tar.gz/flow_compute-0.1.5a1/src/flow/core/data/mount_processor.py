"""Generic mount processing for data sources.

Provider-agnostic mount handling:
- Validation: Early failure with actionable error messages
- Resolution: URL to mount specification conversion
- No provider-specific logic

The MountProcessor is responsible for:
1. Validating mount specifications (paths, duplicates, system directories)
2. Resolving URLs to concrete mount specifications via URLResolver
3. Maintaining clean separation from provider-specific adaptations

Mount flow:
1. User specifies mounts in Flow.run() or CLI
2. MountProcessor validates and resolves URLs
3. Provider-specific adapter (e.g., MithrilMountAdapter) converts to provider format
4. Provider attaches volumes or sets environment variables
5. Instance startup scripts handle runtime mounting
"""

import logging
import time
from typing import TYPE_CHECKING, Any

from flow.core.data.loaders import VolumeLoader
from flow.core.data.resolver import URLResolver
from flow.core.mounts.parser import MountParser
from flow.core.mounts.planner import MountPlanner
from flow.core.mounts.validator import MountValidator
from flow.sdk.models import MountSpec, TaskConfig

if TYPE_CHECKING:
    from flow.protocols.provider import ProviderProtocol as IProvider  # pragma: no cover
else:
    IProvider = object  # type: ignore
from flow.errors import ValidationError

logger = logging.getLogger(__name__)


class MountProcessor:
    """Generic mount processing for data sources.

    Provider-agnostic mount handling:
    1. Validation - Fail fast with clear errors
    2. Resolution - URL to MountSpec conversion

    Performance target: <100ms for typical workloads.
    Thread-safe: No shared mutable state.

    Example:
        >>> processor = MountProcessor()
        >>> resolved_mounts = processor.process_mounts(config, provider)
        >>> # resolved_mounts: List of resolved MountSpec objects
    """

    def __init__(self) -> None:
        """Initialize mount processor with default resolver."""
        self._resolver = URLResolver()
        # Add volume loader explicitly (S3 loader is added by default)
        self._resolver.add_loader("volume", VolumeLoader())
        # Core mounts pipeline
        self._parser = MountParser()
        self._validator = MountValidator()
        self._planner = MountPlanner()

    def process_mounts(self, config: TaskConfig, provider: IProvider) -> list[MountSpec]:
        """Process and resolve all mount specifications.

        Args:
            config: Task configuration with data_mounts
            provider: Provider instance for volume operations

        Returns:
            List of resolved MountSpec objects

        Raises:
            ValidationError: Invalid mount configuration
            FlowError: Resolution errors
        """
        if not config.data_mounts:
            return []

        # Early validation - fail fast
        start_time = time.perf_counter()
        # When given raw strings, allow using core parser to compute targets
        target_to_source: dict[str, str] = {}
        try:
            raw_specs: tuple[str, ...] = tuple(
                [
                    (
                        m
                        if isinstance(m, str)
                        else (m.get("source") if isinstance(m, dict) else None) or ""
                    )
                    for m in (config.data_mounts or [])
                ]  # type: ignore[list-item]
            )
            parsed = self._parser.parse_mounts(raw_specs)
            if parsed:
                target_to_source = parsed
        except Exception:
            target_to_source = {}
        # Validate duplicates/targets when available
        if target_to_source:
            warnings = self._validator.validate(target_to_source)
            if warnings:
                # Surface first warning as error for strictness in core pipeline
                raise ValidationError(warnings[0])
        else:
            self._validate_mounts(config.data_mounts)

        # Resolve each mount
        resolved_mounts = []
        for mount in config.data_mounts:
            if isinstance(mount, dict):
                mount = MountSpec(**mount)

            try:
                # Resolve URL to mount spec
                resolved = self._resolver.resolve(mount.source, mount.target, provider)
                resolved_mounts.append(resolved)
            except Exception as e:
                raise ValidationError(f"Failed to resolve mount {mount.source}: {e}") from e

        # Log performance warning if slow
        elapsed = time.perf_counter() - start_time
        if elapsed > 0.1:  # 100ms threshold
            logger.warning(f"Mount resolution took {elapsed:.3f}s")

        return resolved_mounts

    def _validate_mounts(self, mounts: list[MountSpec | dict[str, Any]]) -> None:
        """Validate mount specifications early.

        Catches common errors before any processing begins.

        Args:
            mounts: List of mount specifications

        Raises:
            ValidationError: Invalid mount configuration
        """
        seen_targets = set()

        for _i, mount in enumerate(mounts):
            if isinstance(mount, dict):
                mount = MountSpec(**mount)

            if mount.target in seen_targets:
                raise ValidationError(
                    f"Duplicate mount target: {mount.target}. Each target path must be unique."
                )
            seen_targets.add(mount.target)

            if not mount.target.startswith("/"):
                raise ValidationError(f"Mount target must be absolute path: {mount.target}")

            if not any(mount.source.startswith(p) for p in ["s3://", "volume://", "/"]):
                raise ValidationError(
                    f"Invalid mount source: {mount.source}. "
                    f"Must start with s3://, volume://, or / (absolute path)"
                )

            system_dirs = {"/bin", "/sbin", "/usr", "/etc", "/proc", "/sys", "/dev"}
            for sys_dir in system_dirs:
                if mount.target == sys_dir or mount.target.startswith(sys_dir + "/"):
                    raise ValidationError(f"Cannot mount over system directory: {mount.target}")
