TTL Cache Utilities

Two complementary TTL cache helpers exist in this codebase:

- Disk-backed JSON TTL (utils/cache/ttl_index.py)
  - Use for CLI indices or small payloads that should persist briefly across processes.
  - API: `TTLIndex(path, ttl_seconds).load()/save(payload)/clear()`.
  - Schema is flexible; conventionally, a top-level `timestamp` key is used alongside payload keys.
  - Scoping: CLI index caches include a `context` string to avoid cross-project leaks.

- In-memory async TTL (adapters/caching/ttl_cache.py)
  - Use inside long-running processes to cache expensive async lookups.
  - API: `TTLCache.get()/set()/clear()`, plus a `CachedResolver` wrapper.
  - Thread-safe for async via an internal asyncio.Lock.

Guidance
- Prefer disk TTL for user-facing CLI selections or lists that should be recalled after a command finishes.
- Prefer in-memory TTL for repeated API calls within a single command’s execution.
- Keep payloads small and avoid sensitive data; caches are best-effort hints, not sources of truth.

