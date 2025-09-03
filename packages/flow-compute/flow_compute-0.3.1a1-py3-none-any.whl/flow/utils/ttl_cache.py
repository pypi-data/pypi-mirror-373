from __future__ import annotations

import time
from collections.abc import Hashable
from threading import RLock
from typing import Generic, TypeVar

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


class TTLCache(Generic[K, V]):
    """Simple thread-safe TTL cache.

    - Stores up to `max_entries` items.
    - Evicts expired entries on access and when capacity is exceeded (oldest first).
    """

    def __init__(self, ttl_seconds: float = 60.0, max_entries: int = 1024) -> None:
        self.ttl = float(ttl_seconds)
        self.max_entries = int(max_entries)
        self._data: dict[K, tuple[V, float]] = {}
        self._lock = RLock()

    def get(self, key: K) -> V | None:
        now = time.time()
        with self._lock:
            item = self._data.get(key)
            if not item:
                return None
            value, ts = item
            if now - ts > self.ttl:
                # expired
                self._data.pop(key, None)
                return None
            return value

    def set(self, key: K, value: V) -> None:
        now = time.time()
        with self._lock:
            self._data[key] = (value, now)
            if len(self._data) > self.max_entries:
                self._evict_oldest(now)

    def clear(self) -> None:
        with self._lock:
            self._data.clear()

    def _evict_oldest(self, now: float) -> None:
        # Remove expired first
        expired = [k for k, (_, ts) in self._data.items() if now - ts > self.ttl]
        for k in expired:
            self._data.pop(k, None)
        # If still over capacity, drop oldest timestamps
        if len(self._data) <= self.max_entries:
            return
        items = sorted(self._data.items(), key=lambda it: it[1][1])  # by ts asc
        to_drop = len(self._data) - self.max_entries
        for i in range(to_drop):
            self._data.pop(items[i][0], None)


__all__ = ["TTLCache"]
