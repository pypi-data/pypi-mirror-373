"""Unified cache utilities (canonical import path).

This module provides a single place to import TTL caches used across the codebase.
It re-exports the domain implementations and offers a small async `CachedResolver`
wrapper for convenience.
"""

from __future__ import annotations

import warnings as _warnings
from collections.abc import Awaitable, Callable
from typing import Generic, TypeVar

from flow.domain.services.cache import AsyncTTLCache, TTLCache

K = TypeVar("K")
V = TypeVar("V")


class CachedResolver(Generic[K, V]):
    """Async resolver with TTL caching.

    Wraps an async `resolver_func` using `AsyncTTLCache` to avoid duplicate work
    within the TTL period. Uses a simple size cap and relies on the underlying
    cache for expiry.
    """

    def __init__(
        self,
        resolver_func: Callable[[K], Awaitable[V]],
        *,
        ttl_seconds: float = 3600,
        max_entries: int = 256,
    ) -> None:
        self._resolver = resolver_func
        self._cache = AsyncTTLCache[K, V](ttl_seconds=ttl_seconds, max_entries=max_entries)

    async def resolve(self, key: K) -> V:
        cached = await self._cache.get(key)
        if cached is not None:
            return cached
        # Resolve fresh and cache
        value = await self._resolver(key)
        await self._cache.set(key, value)
        return value

    async def clear_cache(self) -> None:
        await self._cache.clear()


__all__ = [
    "TTLCache",
    "AsyncTTLCache",
    "CachedResolver",
]
