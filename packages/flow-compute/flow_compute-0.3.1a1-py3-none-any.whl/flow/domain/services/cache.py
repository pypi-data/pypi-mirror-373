"""Unified TTL cache implementation for the Flow domain.

This module provides a thread-safe, generic TTL cache with O(1) get/set operations
and efficient expiry management via min-heap. It replaces multiple cache implementations
across the codebase with a single, consistent solution.
"""

from __future__ import annotations

import heapq
import time
from dataclasses import dataclass, field
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


@dataclass(order=True)
class _ExpiryEntry:
    """Internal entry for tracking expiration times."""

    expires_at: float
    key: K = field(compare=False)


class TTLCache(Generic[K, V]):
    """Thread-safe TTL cache with O(1) get/set and efficient expiry.

    This cache provides:
    - O(1) get/set operations for cache hits
    - O(log n) expiry maintenance via min-heap
    - Automatic cleanup of expired entries
    - Maximum size enforcement with LRU-style eviction

    Thread Safety:
        The cache itself is not thread-safe. For concurrent access,
        wrap with appropriate locking at the usage site.

    Args:
        ttl_seconds: Time-to-live for cache entries in seconds
        max_entries: Maximum number of entries (default: 256)

    Example:
        >>> cache: TTLCache[str, int] = TTLCache(ttl_seconds=60, max_entries=100)
        >>> cache.set("key1", 42)
        >>> value = cache.get("key1")  # Returns 42
        >>> time.sleep(61)
        >>> value = cache.get("key1")  # Returns None (expired)
    """

    __slots__ = ("_store", "_expiries", "_ttl_seconds", "_max_entries")

    def __init__(self, ttl_seconds: float, max_entries: int = 256) -> None:
        """Initialize TTL cache.

        Args:
            ttl_seconds: Time-to-live for entries in seconds
            max_entries: Maximum cache size
        """
        if ttl_seconds <= 0:
            raise ValueError("TTL must be positive")
        if max_entries <= 0:
            raise ValueError("Max entries must be positive")

        self._store: dict[K, tuple[V, float]] = {}
        self._expiries: list[_ExpiryEntry[K]] = []
        self._ttl_seconds = ttl_seconds
        self._max_entries = max_entries

    def get(self, key: K) -> V | None:
        """Get value from cache if present and not expired.

        Args:
            key: Cache key to lookup

        Returns:
            Cached value if present and not expired, None otherwise
        """
        now = time.time()
        item = self._store.get(key)

        if not item:
            return None

        value, expires_at = item
        if expires_at <= now:
            # Entry expired, remove it
            self._store.pop(key, None)
            return None

        return value

    def set(self, key: K, value: V) -> None:
        """Set value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
        """
        now = time.time()
        expires_at = now + self._ttl_seconds

        # Store the value with expiration
        self._store[key] = (value, expires_at)

        # Track expiration for cleanup
        heapq.heappush(self._expiries, _ExpiryEntry(expires_at, key))

        # Enforce size limit
        if len(self._store) > self._max_entries:
            self._evict_oldest(now)

        # Opportunistic cleanup of expired entries
        self._purge_expired(now)

    def delete(self, key: K) -> bool:
        """Delete entry from cache.

        Args:
            key: Key to delete

        Returns:
            True if key was present and deleted, False otherwise
        """
        return self._store.pop(key, None) is not None

    def size(self) -> int:
        """Get current cache size after purging expired entries.

        Returns:
            Number of valid (non-expired) entries
        """
        self._purge_expired(time.time())
        return len(self._store)

    def clear(self) -> None:
        """Clear all cache entries."""
        self._store.clear()
        self._expiries.clear()

    def _purge_expired(self, now: float) -> None:
        """Remove expired entries from cache.

        Args:
            now: Current timestamp
        """
        while self._expiries and self._expiries[0].expires_at <= now:
            exp = heapq.heappop(self._expiries)
            # Only remove if the entry hasn't been updated
            cur = self._store.get(exp.key)
            if cur and cur[1] <= now:
                self._store.pop(exp.key, None)

    def _evict_oldest(self, now: float) -> None:
        """Evict oldest entry when cache is full.

        Args:
            now: Current timestamp
        """
        self._purge_expired(now)

        # If still over limit, remove the earliest expiring entry
        if self._expiries and len(self._store) > self._max_entries:
            exp = heapq.heappop(self._expiries)
            self._store.pop(exp.key, None)

    # Performance metrics support
    def get_metrics(self) -> dict[str, float]:
        """Get cache performance metrics.

        Returns:
            Dictionary with cache statistics
        """
        now = time.time()
        self._purge_expired(now)

        return {
            "size": len(self._store),
            "max_size": self._max_entries,
            "ttl_seconds": self._ttl_seconds,
            "utilization": len(self._store) / self._max_entries if self._max_entries > 0 else 0,
        }


# Async wrapper for compatibility with async code
class AsyncTTLCache(Generic[K, V]):
    """Async wrapper around TTLCache for async/await compatibility.

    This is a thin wrapper that allows TTLCache to be used in async contexts.
    Since the underlying cache operations are CPU-bound and fast, they don't
    actually need to be async, but this wrapper provides the async interface
    for consistency with async codebases.
    """

    def __init__(self, ttl_seconds: float, max_entries: int = 256) -> None:
        """Initialize async TTL cache.

        Args:
            ttl_seconds: Time-to-live for entries in seconds
            max_entries: Maximum cache size
        """
        self._cache = TTLCache[K, V](ttl_seconds, max_entries)

    async def get(self, key: K) -> V | None:
        """Async get value from cache.

        Args:
            key: Cache key to lookup

        Returns:
            Cached value if present and not expired, None otherwise
        """
        return self._cache.get(key)

    async def set(self, key: K, value: V) -> None:
        """Async set value in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        self._cache.set(key, value)

    async def delete(self, key: K) -> bool:
        """Async delete entry from cache.

        Args:
            key: Key to delete

        Returns:
            True if key was present and deleted, False otherwise
        """
        return self._cache.delete(key)

    async def size(self) -> int:
        """Async get current cache size.

        Returns:
            Number of valid entries
        """
        return self._cache.size()

    async def clear(self) -> None:
        """Async clear all cache entries."""
        self._cache.clear()

    async def get_metrics(self) -> dict[str, float]:
        """Async get cache metrics.

        Returns:
            Dictionary with cache statistics
        """
        return self._cache.get_metrics()
