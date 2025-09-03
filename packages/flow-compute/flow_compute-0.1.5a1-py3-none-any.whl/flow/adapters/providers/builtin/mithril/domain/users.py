"""Users service: fetches user data with a small TTL cache.

Extracted from the provider facade to decouple from CLI caches and expose a
focused API for user info retrieval.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


@dataclass
class _CacheEntry:
    value: Any
    expires_at: float


class UsersService:
    def __init__(self, api_client: Any, *, cache_ttl_seconds: float = 3600.0) -> None:
        self._api = api_client
        self._ttl = float(cache_ttl_seconds)
        self._cache: dict[str, _CacheEntry] = {}

    def _now(self) -> float:
        return time.time()

    def _get_cached(self, key: str) -> Any | None:
        entry = self._cache.get(key)
        if not entry:
            return None
        if self._now() >= entry.expires_at:
            try:
                del self._cache[key]
            except Exception:
                pass
            return None
        return entry.value

    def _set_cached(self, key: str, value: Any) -> None:
        self._cache[key] = _CacheEntry(value=value, expires_at=self._now() + self._ttl)

    def get_user(self, user_id: str) -> Any:
        """Fetch user info from API with TTL caching and robust fallbacks.

        Returns provider-agnostic user dict/object as provided by the API client.
        Tries multiple API shapes to accommodate deployments with slightly
        different routes or response envelopes.
        """
        cache_key = f"user:{user_id}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        data = None
        # Normalize common id forms: accept both 'user_ClUS...' and 'ClUS...'
        uid_raw = str(user_id)
        try:
            import re as _re

            uid_stripped = _re.sub(r"^user_", "", uid_raw)
        except Exception:
            uid_stripped = uid_raw
        # Primary path per client wrapper
        try:
            response = self._api.get_user(uid_raw)
            data = response.get("data", response) if isinstance(response, dict) else response
        except Exception:
            data = None

        # Retry with stripped id if first attempt didn't yield a useful dict
        if not isinstance(data, dict) or (not data.get("email") and not data.get("username")):
            try:
                response2 = self._api.get_user(uid_stripped)
                data2 = response2.get("data", response2) if isinstance(response2, dict) else response2
                if isinstance(data2, dict) and (data2.get("email") or data2.get("username")):
                    data = data2
            except Exception:
                pass

        # Fallbacks for API variants and older deployments
        if not isinstance(data, dict) or (not data.get("email") and not data.get("username")):
            try:
                http = getattr(self._api, "_http", None)
                if http is not None:
                    # Try singular path: /v2/user/{id}
                    try:
                        resp2 = http.request(method="GET", url=f"/v2/user/{uid_raw}")
                        data2 = resp2.get("data", resp2) if isinstance(resp2, dict) else resp2
                        if isinstance(data2, dict) and (
                            data2.get("email") or data2.get("username")
                        ):
                            data = data2
                    except Exception:
                        pass
                    # Also try with stripped id
                    if not isinstance(data, dict) or (
                        not data.get("email") and not data.get("username")
                    ):
                        try:
                            resp2b = http.request(method="GET", url=f"/v2/user/{uid_stripped}")
                            data2b = resp2b.get("data", resp2b) if isinstance(resp2b, dict) else resp2b
                            if isinstance(data2b, dict) and (
                                data2b.get("email") or data2b.get("username")
                            ):
                                data = data2b
                        except Exception:
                            pass
                    # Try query-based lookups with various common keys
                    if not isinstance(data, dict) or (
                        not data.get("email") and not data.get("username")
                    ):
                        for key in ("fid", "id", "user_id", "username", "email"):
                            try:
                                respq = http.request(
                                    method="GET", url="/v2/users", params={key: uid_raw}
                                )
                                dq = respq.get("data", respq) if isinstance(respq, dict) else respq
                                if isinstance(dq, list) and dq:
                                    cand = dq[0]
                                    if isinstance(cand, dict) and (
                                        cand.get("email") or cand.get("username")
                                    ):
                                        data = cand
                                        break
                            except Exception:
                                continue
                    # Repeat query-based lookups with stripped id
                    if not isinstance(data, dict) or (
                        not data.get("email") and not data.get("username")
                    ):
                        for key in ("fid", "id", "user_id", "username", "email"):
                            try:
                                respq2 = http.request(
                                    method="GET", url="/v2/users", params={key: uid_stripped}
                                )
                                dq2 = respq2.get("data", respq2) if isinstance(respq2, dict) else respq2
                                if isinstance(dq2, list) and dq2:
                                    cand2 = dq2[0]
                                    if isinstance(cand2, dict) and (
                                        cand2.get("email") or cand2.get("username")
                                    ):
                                        data = cand2
                                        break
                            except Exception:
                                continue
                    # Try legacy v1 path: /users/{id}
                    if not isinstance(data, dict) or (
                        not data.get("email") and not data.get("username")
                    ):
                        try:
                            respv1 = http.request(method="GET", url=f"/users/{uid_raw}")
                            dv1 = respv1.get("data", respv1) if isinstance(respv1, dict) else respv1
                            if isinstance(dv1, dict) and (dv1.get("email") or dv1.get("username")):
                                data = dv1
                        except Exception:
                            pass
                    if not isinstance(data, dict) or (
                        not data.get("email") and not data.get("username")
                    ):
                        try:
                            respv1b = http.request(method="GET", url=f"/users/{uid_stripped}")
                            dv1b = respv1b.get("data", respv1b) if isinstance(respv1b, dict) else respv1b
                            if isinstance(dv1b, dict) and (dv1b.get("email") or dv1b.get("username")):
                                data = dv1b
                        except Exception:
                            pass
            except Exception:
                pass
        # Nested envelope fallback (some deployments wrap under 'user' or 'profile')
        if isinstance(data, dict) and not any(
            k in data for k in ("fid", "id", "user_id", "username", "email")
        ):
            try:
                for k in ("user", "profile", "data"):
                    inner = data.get(k)
                    if isinstance(inner, dict):
                        data = inner
                        break
            except Exception:
                pass

        # Final fallback: when the requested id refers to the current user, synthesize from /v2/me
        if not isinstance(data, dict) or (not data.get("email") and not data.get("username")):
            try:
                me_resp = self._api.get_me()
                me_data = me_resp.get("data", me_resp) if isinstance(me_resp, dict) else me_resp
                if isinstance(me_data, dict):
                    fid = str(
                        me_data.get("fid") or me_data.get("id") or me_data.get("user_id") or ""
                    )
                    # Normalize tokens for comparison
                    import re as _re

                    req_tok = _re.sub(r"[^a-z0-9]", "", str(user_id).lower())
                    fid_tok = _re.sub(r"[^a-z0-9]", "", fid.lower())
                    if (
                        req_tok
                        and fid_tok
                        and (
                            req_tok == fid_tok
                            or fid_tok.startswith(req_tok)
                            or req_tok.startswith(fid_tok)
                        )
                    ):
                        data = me_data
            except Exception:
                pass

        self._set_cached(cache_key, data)
        return data

    def get_user_teammates(self, user_id: str) -> Any:
        """Fetch teammates list for a user (not cached; often dynamic).

        Normalizes the return shape to a list for callers by unwrapping
        common response envelopes: {data: [...]}, {teammates: [...]}, etc.
        Returns an empty list on error.
        """
        try:
            resp = self._api.get_user_teammates(user_id)
            if isinstance(resp, list):
                return resp
            if isinstance(resp, dict):
                for key in ("data", "teammates", "users", "members", "results", "items"):
                    try:
                        val = resp.get(key)
                        if isinstance(val, list):
                            return val
                        if isinstance(val, dict) and isinstance(val.get("items"), list):
                            return val.get("items")
                    except Exception:
                        continue
            return []
        except Exception:
            return []

    def invalidate(self, user_id: str | None = None) -> None:
        if user_id is None:
            self._cache.clear()
        else:
            try:
                del self._cache[f"user:{user_id}"]
            except Exception:
                pass
