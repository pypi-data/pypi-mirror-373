"""Owner resolver and formatter (core).

Resolves current user (me) once per run; formats Owner column per spec.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

from flow.sdk.client import Flow
from flow.sdk.factory import create_client


@dataclass
class Me:
    user_id: str
    username: str | None = None
    email: str | None = None


class OwnerResolver:
    def __init__(self, flow: Flow | None = None) -> None:
        # Prefer factory to avoid direct client construction in CLI layer
        self.flow = flow or create_client(auto_init=True)
        self._me: Me | None = None
        self._owner_map: dict[str, str] | None = None

    def _debug(self, msg: str) -> None:
        try:
            if (os.environ.get("FLOW_OWNER_DEBUG") or "").strip() == "1":
                print(f"[owner-debug] {msg}")
        except Exception:
            pass

    def get_me(self) -> Me | None:
        if self._me is not None:
            return self._me
        # Query identity: prefer provider API client (/v2/me), fallback to HTTP adapter if present
        try:
            provider = self.flow.provider
            # Ensure http is available for later enrichment even if api_client succeeds
            http = getattr(provider, "http", None)
            resp = None
            # Preferred: provider exposes API client with get_me()
            api_client = getattr(provider, "_api_client", None)
            if api_client and hasattr(api_client, "get_me"):
                try:
                    self._debug("get_me: using provider._api_client.get_me()")
                    resp = api_client.get_me()
                except Exception:
                    self._debug("get_me: api_client.get_me() raised; will try provider.http")
                    resp = None
            if resp is None:
                if http is None:
                    self._debug("get_me: no http client on provider; returning None")
                    return None
                self._debug("get_me: calling GET /v2/me via provider.http")
                resp = http.request(method="GET", url="/v2/me")
            data = None
            # Robust response handling: dict, Response-like, or plain object
            if isinstance(resp, dict):
                data = resp.get("data", resp)
            else:
                try:
                    if hasattr(resp, "json"):
                        j = resp.json()
                        if isinstance(j, dict):
                            data = j.get("data", j)
                except Exception:
                    data = None
                # Fallback: attribute-based
                if data is None:
                    try:
                        # Pydantic models and other typed objects
                        if hasattr(resp, "model_dump"):
                            dumped = resp.model_dump()  # type: ignore[attr-defined]
                            if isinstance(dumped, dict):
                                data = dumped
                        if data is None:
                            maybe_data = getattr(resp, "data", None)
                            if isinstance(maybe_data, dict):
                                data = maybe_data.get("data", maybe_data)
                    except Exception:
                        pass
            try:
                self._debug(
                    f"get_me: raw keys={list(data.keys()) if isinstance(data, dict) else type(data)}"
                )
            except Exception:
                pass
            # Some deployments wrap user under 'user' or 'profile'
            if isinstance(data, dict) and not any(
                k in data for k in ("fid", "id", "user_id", "username", "email")
            ):
                for k in ("user", "profile", "data", "me", "identity", "account", "result"):
                    try:
                        inner = data.get(k)
                        if isinstance(inner, dict):
                            data = inner
                            self._debug(f"get_me: unwrapped identity under '{k}'")
                            break
                        # Sometimes nested under list with single entry
                        if isinstance(inner, list) and inner:
                            first = inner[0]
                            if isinstance(first, dict):
                                data = first
                                self._debug(f"get_me: unwrapped identity list under '{k}'")
                                break
                    except Exception:
                        pass
            # Rare case: top-level list with single user
            if not isinstance(data, dict) and isinstance(data, list) and data:
                try:
                    if isinstance(data[0], dict):
                        data = data[0]
                        self._debug("get_me: unwrapped single-element list response")
                except Exception:
                    pass
            if not isinstance(data, dict):
                self._debug("get_me: data not dict; returning None")
                return None
            user_id = data.get("fid") or data.get("id") or data.get("user_id")

            # Accept a wider set of username/display fields across deployments
            username = (
                data.get("username")
                or data.get("user_name")
                or data.get("handle")
                or data.get("name")
                or data.get("display_name")
                or data.get("displayName")
                or data.get("full_name")
                or data.get("fullName")
                or data.get("given_name")
                or data.get("givenName")
            )

            # Robust email extraction: handle common variants and nesting
            email = (
                data.get("email")
                or data.get("primary_email")
                or data.get("primaryEmail")
                or data.get("email_address")
                or data.get("emailAddress")
            )
            if not email:
                # Look for list-based email fields or nested contact profiles
                try:
                    emails = data.get("emails")
                    if isinstance(emails, list) and emails:
                        # Support both list of strings and list of objects
                        first = emails[0]
                        if isinstance(first, str):
                            email = first
                        elif isinstance(first, dict):
                            email = first.get("email") or first.get("address") or first.get("value")
                except Exception:
                    pass
            if not email:
                try:
                    contact = data.get("contact")
                    if isinstance(contact, dict):
                        email = (
                            contact.get("email")
                            or contact.get("primary_email")
                            or contact.get("primaryEmail")
                            or contact.get("email_address")
                            or contact.get("emailAddress")
                        )
                except Exception:
                    pass
            self._debug(f"get_me: extracted user_id={user_id} username={username} email={email}")
            if not user_id:
                self._debug("get_me: missing user_id; returning None")
                return None
            self._me = Me(user_id=user_id, username=username, email=email)

            # Best-effort enrichment when identity endpoint is sparse
            if (not getattr(self._me, "email", None)) or (not getattr(self._me, "username", None)):
                # Try provider helper first
                try:
                    u = self.flow.get_user(user_id)
                    if isinstance(u, dict):
                        # Email/username from a broader set of keys
                        self._me.email = self._me.email or (
                            u.get("email")
                            or u.get("primary_email")
                            or u.get("primaryEmail")
                            or u.get("email_address")
                            or u.get("emailAddress")
                        )
                        if not self._me.email:
                            try:
                                emails = u.get("emails")
                                if isinstance(emails, list) and emails:
                                    first = emails[0]
                                    if isinstance(first, str):
                                        self._me.email = first
                                    elif isinstance(first, dict):
                                        self._me.email = (
                                            first.get("email")
                                            or first.get("address")
                                            or first.get("value")
                                        )
                            except Exception:
                                pass
                        self._me.username = self._me.username or (
                            u.get("username")
                            or u.get("user_name")
                            or u.get("handle")
                            or u.get("name")
                            or u.get("display_name")
                            or u.get("displayName")
                            or u.get("full_name")
                            or u.get("fullName")
                            or u.get("given_name")
                            or u.get("givenName")
                        )
                except Exception as e:
                    self._debug(f"get_me: flow.get_user enrichment failed: {e}")
                    pass
                # Fallback to a simple user fetch via HTTP
                try:
                    if http is not None:
                        u_resp = http.request(method="GET", url=f"/users/{user_id}")
                    else:
                        u_resp = None
                    u_data = u_resp.get("data", u_resp) if isinstance(u_resp, dict) else None
                    if isinstance(u_data, dict):
                        self._me.email = self._me.email or (
                            u_data.get("email")
                            or u_data.get("primary_email")
                            or u_data.get("primaryEmail")
                            or u_data.get("email_address")
                            or u_data.get("emailAddress")
                        )
                        if not self._me.email:
                            try:
                                emails = u_data.get("emails")
                                if isinstance(emails, list) and emails:
                                    first = emails[0]
                                    if isinstance(first, str):
                                        self._me.email = first
                                    elif isinstance(first, dict):
                                        self._me.email = (
                                            first.get("email")
                                            or first.get("address")
                                            or first.get("value")
                                        )
                            except Exception:
                                pass
                        self._me.username = self._me.username or (
                            u_data.get("username")
                            or u_data.get("user_name")
                            or u_data.get("handle")
                            or u_data.get("name")
                            or u_data.get("display_name")
                            or u_data.get("displayName")
                            or u_data.get("full_name")
                            or u_data.get("fullName")
                            or u_data.get("given_name")
                            or u_data.get("givenName")
                        )
                except Exception as e:
                    self._debug(f"get_me: GET /users/{{id}} enrichment failed: {e}")
                    pass

                # Environment fallbacks for offline/mocked contexts
                try:
                    env_email = os.environ.get("FLOW_USER_EMAIL")
                    env_name = os.environ.get("FLOW_USER_NAME") or os.environ.get("FLOW_USERNAME")
                    if env_email and not self._me.email:
                        self._me.email = env_email
                    if env_name and not self._me.username:
                        self._me.username = env_name
                    if env_email or env_name:
                        self._debug(f"get_me: env fallback email={env_email} username={env_name}")
                except Exception:
                    pass
            self._debug(
                f"get_me: final me user_id={self._me.user_id} username={self._me.username} email={self._me.email}"
            )
            return self._me
        except Exception:
            self._debug("get_me: unexpected exception; returning None")
            return None

    def get_teammates_map(self) -> dict[str, str]:
        """Return mapping of teammate user_id -> friendly label.

        Uses v1 IAM endpoint: GET /users/{user_id}/teammates (not under /v2).
        Falls back to empty mapping on error.
        """
        if self._owner_map is not None:
            return self._owner_map
        self._owner_map = {}
        me = self.get_me()
        self._debug(f"teammates: me={getattr(me, 'user_id', None)}")
        if me is None or not me.user_id:
            self._debug("teammates: no me; returning empty map")
            return self._owner_map
        try:
            self._debug(f"teammates: calling get_user_teammates({me.user_id})")
            resp = self.flow.get_user_teammates(me.user_id)
            items: list[dict] = []
            if isinstance(resp, list):
                items = resp
            elif isinstance(resp, dict):
                # Common envelopes across deployments
                for key in ("data", "teammates", "users", "members", "results", "items"):
                    try:
                        val = resp.get(key)
                        if isinstance(val, list):
                            items = val
                            break
                        if isinstance(val, dict) and isinstance(val.get("items"), list):
                            items = val.get("items")  # type: ignore[assignment]
                            break
                    except Exception:
                        continue
            self._debug(f"teammates: got {len(items) if isinstance(items, list) else 0} items")

            # Add current user label mapping for robust self-resolution
            try:
                self_label = None
                if me.email and "@" in me.email:
                    local = me.email.split("@")[0]
                    self_label = (local.split(".")[0].split("_")[0].split("-")[0] or "").lower()
                if not self_label and me.username:
                    self_label = (
                        str(me.username).split()[0].split(".")[0].split("_")[0].split("-")[0] or ""
                    ).lower()
                if not self_label:
                    self_label = str(me.user_id).replace("user_", "")[:8]

                # Index multiple normalized keys for self
                def _norm_tokens(v: str) -> list[str]:
                    low = v.lower()
                    stripped = re.sub(r"^user_", "", low)
                    alnum = re.sub(r"[^a-z0-9]", "", low)
                    tokens = {
                        low,
                        stripped,
                        alnum,
                        alnum[:8],
                        re.sub(r"[^a-z0-9]", "", stripped)[:8],
                        # Index shorter prefixes that sometimes appear in provider UIs
                        alnum[:6],
                        alnum[:4],
                        re.sub(r"[^a-z0-9]", "", stripped)[:6],
                        re.sub(r"[^a-z0-9]", "", stripped)[:4],
                    }
                    return [t for t in tokens if t]

                for key in _norm_tokens(str(me.user_id)):
                    self._owner_map[key] = self_label
                self._debug(
                    f"teammates: indexed self keys for '{self_label}' -> {len(self._owner_map)} entries"
                )
            except Exception:
                pass
            for user in items:
                try:
                    uid = user.get("fid") or user.get("id") or user.get("user_id") or None
                    if not uid:
                        continue
                    # Accept wider shapes for teammate details
                    email = (
                        user.get("email")
                        or user.get("primary_email")
                        or user.get("primaryEmail")
                        or user.get("email_address")
                        or user.get("emailAddress")
                    )
                    if not email:
                        try:
                            emails = user.get("emails")
                            if isinstance(emails, list) and emails:
                                first = emails[0]
                                if isinstance(first, str):
                                    email = first
                                elif isinstance(first, dict):
                                    email = (
                                        first.get("email")
                                        or first.get("address")
                                        or first.get("value")
                                    )
                        except Exception:
                            pass
                    username = (
                        user.get("username")
                        or user.get("user_name")
                        or user.get("handle")
                        or user.get("name")
                        or user.get("display_name")
                        or user.get("displayName")
                        or user.get("full_name")
                        or user.get("fullName")
                        or user.get("given_name")
                        or user.get("givenName")
                    )
                    display_name = (
                        user.get("name")
                        or user.get("display_name")
                        or user.get("displayName")
                        or user.get("full_name")
                        or user.get("fullName")
                    )
                    label = None
                    if email and "@" in email:
                        local = email.split("@")[0]
                        import re as _re

                        first = _re.split(r"[._-]+", local)[0]
                        label = first.lower() if first else None
                    if not label and username:
                        import re as _re

                        first = _re.split(r"[\s._-]+", str(username))[0]
                        label = first.lower() if first else None
                    if not label and display_name:
                        label = str(display_name).split()[0].lower()
                    if not label:
                        label = str(uid).replace("user_", "")[:8]

                    # Index multiple normalized keys for teammate id and username
                    def _norm_tokens(v: str) -> list[str]:
                        low = v.lower()
                        stripped = re.sub(r"^user_", "", low)
                        alnum = re.sub(r"[^a-z0-9]", "", low)
                        tokens = {
                            low,
                            stripped,
                            alnum,
                            alnum[:8],
                            re.sub(r"[^a-z0-9]", "", stripped)[:8],
                            # Include additional short prefixes for lenient matching
                            alnum[:6],
                            alnum[:4],
                            re.sub(r"[^a-z0-9]", "", stripped)[:6],
                            re.sub(r"[^a-z0-9]", "", stripped)[:4],
                        }
                        return [t for t in tokens if t]

                    for key in _norm_tokens(str(uid)):
                        self._owner_map[key] = label
                    if username:
                        for key in _norm_tokens(str(username)):
                            self._owner_map[key] = label
                    # Lenient: index any string fields that look like identifiers (may include short codes)
                    try:
                        for k, v in list(user.items()):
                            if not isinstance(v, str):
                                continue
                            vs = v.strip()
                            if not vs:
                                continue
                            # Skip obvious non-identifiers (emails handled above)
                            if "@" in vs:
                                continue
                            # Consider tokens 4-32 chars alnum-ish
                            raw = re.sub(r"\s+", "", vs)
                            if (
                                4 <= len(raw) <= 32
                                and re.search(r"[A-Za-z]", raw)
                                and re.search(r"[0-9]", raw)
                            ):
                                for key in _norm_tokens(raw):
                                    self._owner_map[key] = label
                                # Also index with explicit user_ prefix form
                                for key in _norm_tokens("user_" + raw):
                                    self._owner_map[key] = label
                    except Exception:
                        pass
                except Exception:
                    continue
                    self._debug(
                        f"teammates: mapped uid={uid} email={email} username={username} -> '{label}'"
                    )
                except Exception:
                    continue
        except Exception as e:
            # Non-fatal; return whatever we have
            self._debug(f"teammates: error fetching teammates: {e}")
            pass
        # Apply environment overrides to allow precise mapping without API fields
        try:
            overrides = (os.environ.get("FLOW_OWNER_OVERRIDES") or "").strip()
            if overrides:
                # Format: "token1=label1,token2=label2"
                parts = [p for p in overrides.split(",") if p and "=" in p]
                for p in parts:
                    key_raw, label_raw = p.split("=", 1)
                    key_raw = key_raw.strip()
                    label_raw = label_raw.strip()
                    if not key_raw or not label_raw:
                        continue

                    def _norm_tokens(v: str) -> list[str]:
                        low = v.lower()
                        stripped = re.sub(r"^user_", "", low)
                        alnum = re.sub(r"[^a-z0-9]", "", low)
                        return [t for t in {low, stripped, alnum, alnum[:8]} if t]

                    for key in _norm_tokens(key_raw):
                        self._owner_map[key] = label_raw.lower()
                self._debug(
                    f"teammates: applied overrides '{overrides}', total entries={len(self._owner_map)}"
                )
        except Exception:
            pass

        # If a user-level override is provided, map current user id tokens to that label
        try:
            me_label = (
                os.environ.get("FLOW_OWNER_NAME") or os.environ.get("FLOW_USER_NAME") or ""
            ).strip()
            if me_label and me and me.user_id:

                def _norm_tokens(v: str) -> list[str]:
                    low = v.lower()
                    stripped = re.sub(r"^user_", "", low)
                    alnum = re.sub(r"[^a-z0-9]", "", low)
                    return [t for t in {low, stripped, alnum, alnum[:8]} if t]

                for key in _norm_tokens(str(me.user_id)):
                    self._owner_map[key] = me_label.lower()
                self._debug(
                    f"teammates: applied FLOW_OWNER_NAME override='{me_label}', entries={len(self._owner_map)}"
                )
        except Exception:
            pass
        try:
            # Log a few indicative keys for quick inspection
            sample = [k for k in self._owner_map.keys() if k and len(k) <= 12][:8]
            self._debug(f"teammates: sample keys={sample}")
        except Exception:
            pass
        return self._owner_map

    @staticmethod
    def format_owner(
        created_by: str | None, me: Me | None, owner_map: dict[str, str] | None = None
    ) -> str:
        # Resolve via teammates map first when available
        if owner_map and created_by:
            try:
                # Case-insensitive lookups across normalized token forms
                key = str(created_by).lower()
                label = owner_map.get(key)
                if label:
                    try:
                        if (os.environ.get("FLOW_OWNER_DEBUG") or "").strip() == "1":
                            print(
                                f"[owner-debug] format_owner: owner_map direct hit key='{key}' -> '{label}'"
                            )
                    except Exception:
                        pass
                    return label
                # Try additional normalized forms
                stripped = re.sub(r"^user_", "", key)
                alnum = re.sub(r"[^a-z0-9]", "", key)
                for tok in (stripped, alnum, alnum[:8], re.sub(r"[^a-z0-9]", "", stripped)[:8]):
                    if tok and tok in owner_map:
                        try:
                            if (os.environ.get("FLOW_OWNER_DEBUG") or "").strip() == "1":
                                print(
                                    f"[owner-debug] format_owner: owner_map norm hit tok='{tok}' -> '{owner_map[tok]}'"
                                )
                        except Exception:
                            pass
                        return owner_map[tok]
            except Exception:
                pass
        # Prefer current user's friendly name when the creator matches the current user
        if me and created_by:
            try:
                # Normalize inputs (case-insensitive, strip common prefixes)
                created_by_str = str(created_by)
                me_user_id = str(me.user_id or "")
                me_username = str(me.username or "")
                me_email = str(me.email or "")

                # Direct equality first (exact provider IDs)
                if created_by_str == me_user_id:
                    pass  # treat as same user
                else:
                    # Normalize common ID formats to handle provider differences
                    # Examples:
                    #   created_by: "ClUS4619" vs me.user_id: "user_ClUS4619AbCdEf"
                    #   created_by: "user_kfV4CCaapLiqCNlv" vs me.user_id: "user_kfV4CCaapLiqCNlv"
                    created_token = re.sub(r"^user_", "", created_by_str)
                    me_token = re.sub(r"^user_", "", me_user_id)
                    # Lowercase and strip non-alphanumerics to tolerate formatting
                    created_token_l = re.sub(r"[^a-z0-9]", "", created_token.lower())
                    me_token_l = re.sub(r"[^a-z0-9]", "", me_token.lower())
                    # Consider a match if one token starts with the other (handles short IDs)
                    is_same_user = False
                    if created_token_l and me_token_l:
                        if (
                            created_token_l == me_token_l
                            or me_token_l.startswith(created_token_l)
                            or created_token_l.startswith(me_token_l)
                        ):
                            is_same_user = True
                        else:
                            # Also compare first 8 chars which are commonly displayed
                            is_same_user = created_token_l[:8] == me_token_l[:8]
                    # Also consider username-based identity commonly shown in external systems
                    if not is_same_user and me_username:
                        ct = created_by_str.lower()
                        un = me_username.lower()
                        if ct == un or ct.startswith(un) or un.startswith(ct):
                            is_same_user = True
                    # And finally compare against email local part (before @)
                    if not is_same_user and me_email and "@" in me_email:
                        local = me_email.split("@")[0].lower()
                        ct = created_by_str.lower()
                        if ct == local or ct.startswith(local) or local.startswith(ct):
                            is_same_user = True
                    try:
                        if (os.environ.get("FLOW_OWNER_DEBUG") or "").strip() == "1":
                            print(
                                f"[owner-debug] format_owner: me-match tokens ct='{created_token_l}' me='{me_token_l}' -> {is_same_user}"
                            )
                    except Exception:
                        pass
                    if not is_same_user:
                        raise ValueError("not same user")
                # Derive a first-name style label from email (e.g., jared@ → jared, john.doe@ → john)
                if me_email and "@" in me_email:
                    local = me_email.split("@")[0]
                    # Split on common separators and take the first segment
                    first = re.split(r"[._-]+", local)[0]
                    try:
                        if (os.environ.get("FLOW_OWNER_DEBUG") or "").strip() == "1":
                            print(
                                f"[owner-debug] format_owner: using email local='{first.lower() if first else ''}'"
                            )
                    except Exception:
                        pass
                    return first.lower() if first else "-"
                # Fallback to username if available
                if me_username:
                    # Use first token of username and normalize to lowercase
                    first = re.split(r"[\s._-]+", me_username)[0]
                    try:
                        if (os.environ.get("FLOW_OWNER_DEBUG") or "").strip() == "1":
                            print(
                                f"[owner-debug] format_owner: using username token='{first.lower() if first else ''}'"
                            )
                    except Exception:
                        pass
                    return first.lower() if first else "-"
                # Env-provided friendly name
                env_name = (
                    os.environ.get("FLOW_OWNER_NAME")
                    or os.environ.get("FLOW_USER_NAME")
                    or os.environ.get("FLOW_USERNAME")
                )
                if env_name:
                    first = re.split(r"[\s._-]+", str(env_name).strip())[0]
                    if first:
                        try:
                            if (os.environ.get("FLOW_OWNER_DEBUG") or "").strip() == "1":
                                print(
                                    f"[owner-debug] format_owner: using env name='{first.lower()}'"
                                )
                        except Exception:
                            pass
                        return first.lower()
                # No personal info available
                return "-"
            except Exception:
                # Fall through to compact FID formatting below
                pass

        # Heuristic: when teammates map is essentially empty (only self-index),
        # and created_by is a provider-style token (e.g., 'user_ClUS...'),
        # treat it as the current user to provide a friendly label.
        try:
            om_size = len(owner_map) if isinstance(owner_map, dict) else 0
        except Exception:
            om_size = 0
        if me and created_by and om_size and om_size <= 8:
            try:
                key = str(created_by).lower().strip()
                if not owner_map or key not in owner_map:
                    if re.match(r"^user_[a-z0-9]{6,}$", re.sub(r"[^a-zA-Z0-9_]", "", key)):
                        # Use same derivation as the me-path above
                        me_email = str(getattr(me, "email", "") or "")
                        me_username = str(getattr(me, "username", "") or "")
                        if me_email and "@" in me_email:
                            local = me_email.split("@")[0]
                            first = re.split(r"[._-]+", local)[0]
                            if first:
                                try:
                                    if (os.environ.get("FLOW_OWNER_DEBUG") or "").strip() == "1":
                                        print(
                                            f"[owner-debug] format_owner: self-heuristic using email local='{first.lower()}'"
                                        )
                                except Exception:
                                    pass
                                return first.lower()
                        if me_username:
                            first = re.split(r"[\s._-]+", me_username)[0]
                            if first:
                                try:
                                    if (os.environ.get("FLOW_OWNER_DEBUG") or "").strip() == "1":
                                        print(
                                            f"[owner-debug] format_owner: self-heuristic using username token='{first.lower()}'"
                                        )
                                except Exception:
                                    pass
                                return first.lower()
                        env_name = (
                            os.environ.get("FLOW_OWNER_NAME")
                            or os.environ.get("FLOW_USER_NAME")
                            or os.environ.get("FLOW_USERNAME")
                        )
                        if env_name:
                            first = re.split(r"[\s._-]+", str(env_name).strip())[0]
                            if first:
                                try:
                                    if (os.environ.get("FLOW_OWNER_DEBUG") or "").strip() == "1":
                                        print(
                                            f"[owner-debug] format_owner: self-heuristic using env name='{first.lower()}'"
                                        )
                                except Exception:
                                    pass
                                return first.lower()
            except Exception:
                pass
        # Compact FID for other users
        if created_by:
            # Avoid aggressive heuristics that could mislabel other users as the current user.
            # If we can't resolve to a friendly name here, leave a compact, readable token.
            try:
                if (os.environ.get("FLOW_OWNER_DEBUG") or "").strip() == "1":
                    print(
                        f"[owner-debug] format_owner: fallback compact for created_by='{created_by}'"
                    )
            except Exception:
                pass
            return created_by.replace("user_", "")[:8]
        # Unknown owner
        try:
            if (os.environ.get("FLOW_OWNER_DEBUG") or "").strip() == "1":
                print("[owner-debug] format_owner: unknown owner -> '-' ")
        except Exception:
            pass
        return "-"
