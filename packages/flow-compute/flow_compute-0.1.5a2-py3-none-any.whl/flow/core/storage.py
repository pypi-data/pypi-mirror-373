"""Storage helpers for robust volume operations."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flow.protocols.provider import ProviderProtocol as IProvider  # pragma: no cover
    from flow.sdk.models import Volume  # pragma: no cover
else:
    Volume = object  # type: ignore
    IProvider = object  # type: ignore


def salvage_volume_create(provider: IProvider, *, size_gb: int, name: str | None) -> Volume:
    """Create a volume with best-effort salvage for transient provider errors.

    If provider.create_volume raises a 5xx-like error but the volume may have been
    created, this attempts to find an existing volume by name and returns it.
    Re-raises the original exception if salvage fails or name is not provided.
    """
    try:
        return provider.create_volume(size_gb=size_gb, name=name)
    except Exception as e:
        status_code = getattr(e, "status_code", None)
        if status_code and int(status_code) >= 500 and name:
            try:
                existing: Iterable[Volume] = provider.list_volumes(limit=200)
                match = next((v for v in existing if getattr(v, "name", None) == name), None)
                if match:
                    return match
            except Exception:
                pass
        raise
