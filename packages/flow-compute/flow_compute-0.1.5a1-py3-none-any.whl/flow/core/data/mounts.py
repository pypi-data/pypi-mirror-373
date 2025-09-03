"""Unified helpers for normalizing and resolving data mounts.

These helpers centralize mount handling so callers (API/CLI/services)
don't duplicate parsing and resolution logic.
"""

from __future__ import annotations

import os
from collections.abc import Iterable
from typing import TYPE_CHECKING

from flow.core.data.resolver import URLResolver
from flow.core.mounts.parser import MountParser
from flow.sdk.models import MountSpec, TaskConfig

if TYPE_CHECKING:  # avoid runtime circular import
    from flow.protocols.provider import ProviderProtocol as IProvider  # pragma: no cover
else:
    IProvider = object  # type: ignore


def normalize_mounts_param(mounts: str | dict[str, str] | Iterable[str]) -> list[MountSpec]:
    """Normalize a mounts parameter into a list of MountSpec.

    Accepts a single source string, a mapping of target->source, a sequence of
    mount specifications ("source" or "target=source"), or a YAML path that
    contains a TaskConfig with data_mounts.
    """

    # YAML path case (used by app service)
    if (
        isinstance(mounts, str)
        and mounts.lower().endswith((".yml", ".yaml"))
        and os.path.exists(mounts)
    ):
        cfg = TaskConfig.from_yaml(mounts)
        return [m if isinstance(m, MountSpec) else MountSpec(**m) for m in (cfg.data_mounts or [])]

    # Single string treated as a single source → auto-target via parser rules
    if isinstance(mounts, str):
        parser = MountParser()
        target, source = parser._parse_single_mount(mounts)  # type: ignore[attr-defined]
        return [MountSpec(source=source, target=target, mount_type=_infer_mount_type(source))]

    # Tuple/list of mount specifications
    if not isinstance(mounts, dict):
        parser = MountParser()
        parsed = parser.parse_mounts(tuple(mounts))  # type: ignore[arg-type]
        if not parsed:
            return []
        return [
            MountSpec(source=src, target=dst, mount_type=_infer_mount_type(src))
            for dst, src in parsed.items()
        ]

    # Mapping of explicit targets -> sources
    return [
        MountSpec(source=src, target=dst, mount_type=_infer_mount_type(src))
        for dst, src in mounts.items()
    ]


def resolve_mounts(mount_specs: list[MountSpec], provider: IProvider) -> list[MountSpec]:
    """Resolve a list of MountSpec (possibly with names) into concrete specs.

    This uses URLResolver, which delegates to scheme loaders (e.g., volume, s3).
    """

    if not mount_specs:
        return []
    resolver = URLResolver()
    resolved: list[MountSpec] = []
    for m in mount_specs:
        spec = resolver.resolve(m.source, m.target, provider)
        resolved.append(spec)
    return resolved


def _infer_mount_type(source: str) -> str:
    if source.startswith("s3://"):
        return "s3fs"
    if source.startswith("volume://"):
        return "volume"
    # local path or file://
    return "bind"
