"""Simple TTL cache utilities used by the Mithril provider services.

Caches maintain a maximum entry count and time-based expiration. They are
intentionally lightweight and synchronous for use in CLI/SDK contexts.
"""

from __future__ import annotations

import time
from collections import OrderedDict
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class TtlCache(Generic[K, V]):
    """A minimal TTL cache with size and time-based eviction.

    Args:
        ttl_seconds: Time-to-live for entries.
        max_entries: Maximum number of entries to retain. Oldest entries
            are evicted when the limit is exceeded.
    """

    def __init__(self, *, ttl_seconds: float, max_entries: int = 256) -> None:
        self._ttl = float(ttl_seconds)
        self._max = int(max_entries)
        self._store: OrderedDict[K, tuple[V, float]] = OrderedDict()

    def _purge_expired(self) -> None:
        now = time.time()
        expired_keys = [k for k, (_, ts) in self._store.items() if now - ts > self._ttl]
        for k in expired_keys:
            self._store.pop(k, None)

    def get(self, key: K) -> V | None:
        """Get a value by key, returning None if missing or expired."""
        self._purge_expired()
        item = self._store.get(key)
        if item is None:
            return None
        value, ts = item
        if time.time() - ts > self._ttl:
            self._store.pop(key, None)
            return None
        # refresh recency order
        self._store.move_to_end(key)
        return value

    def set(self, key: K, value: V) -> None:
        """Insert or update a value and evict if over capacity."""
        self._purge_expired()
        self._store[key] = (value, time.time())
        self._store.move_to_end(key)
        while len(self._store) > self._max:
            self._store.popitem(last=False)
