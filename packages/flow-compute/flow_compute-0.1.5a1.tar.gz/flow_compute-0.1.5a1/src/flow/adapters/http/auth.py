"""HTTP-backed authentication helpers (moved from flow.core.auth).

Implements API-key and email/password session auth flows using an HttpClientProtocol.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from flow.errors import AuthenticationError
from flow.protocols.http import HttpClientProtocol

logger = logging.getLogger(__name__)


class AuthConfig:
    def __init__(
        self,
        api_key: str | None = None,
        email: str | None = None,
        password: str | None = None,
        session_file: Path | None = None,
    ):
        self.api_key = api_key or os.getenv("MITHRIL_API_KEY")
        self.email = email
        self.password = password
        self.session_file = session_file or self._default_session_file()

    def _default_session_file(self) -> Path:
        home = Path.home()
        flow_dir = home / ".flow"
        flow_dir.mkdir(exist_ok=True)
        return flow_dir / "session.json"

    @property
    def has_api_key(self) -> bool:
        return bool(self.api_key)

    @property
    def has_credentials(self) -> bool:
        return bool(self.email and self.password)


class Session:
    def __init__(self, token: str, expires_at: datetime, user_id: str):
        self.token = token
        self.expires_at = expires_at
        self.user_id = user_id

    @property
    def is_valid(self) -> bool:
        return datetime.now() < self.expires_at

    def to_dict(self) -> dict[str, Any]:
        return {
            "token": self.token,
            "expires_at": self.expires_at.isoformat(),
            "user_id": self.user_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Session:
        return cls(
            token=data["token"],
            expires_at=datetime.fromisoformat(data["expires_at"]),
            user_id=data["user_id"],
        )


class Authenticator:
    def __init__(self, config: AuthConfig, http_client: HttpClientProtocol):
        self.config = config
        self.http = http_client
        self._session: Session | None = None

    def authenticate(self) -> str:
        if self.config.has_api_key:
            return self.config.api_key
        if self._session and self._session.is_valid:
            return self._session.token
        saved = self._load_session()
        if saved and saved.is_valid:
            self._session = saved
            return saved.token
        if self.config.has_credentials:
            session = self._authenticate_with_credentials()
            self._session = session
            self._save_session(session)
            return session.token
        raise AuthenticationError("No valid authentication method available. Set MITHRIL_API_KEY.")

    def get_access_token(self) -> str:
        return self.authenticate()

    def _authenticate_with_credentials(self) -> Session:
        try:
            response = self.http.request(
                method="POST",
                url="/auth/login",
                json={
                    "email": self.config.email,
                    "password": self.config.password,
                },
                retry_server_errors=False,
            )
            token = response.get("token")
            expires_in = response.get("expires_in", 3600)
            user_id = response.get("user_id", "")
            if not token:
                raise AuthenticationError("No token in login response")
            expires_at = datetime.now() + timedelta(seconds=expires_in)
            session = Session(token, expires_at, user_id)
            logger.info(f"Successfully authenticated as user {user_id}")
            return session
        except Exception as e:
            raise AuthenticationError(f"Login failed: {e}") from e

    def logout(self):
        if self._session:
            try:
                self.http.request(
                    method="POST",
                    url="/auth/logout",
                    headers={"Authorization": f"Bearer {self._session.token}"},
                )
            except Exception as e:
                logger.warning(f"Logout request failed: {e}")
            self._session = None
            self._clear_saved_session()

    def _load_session(self) -> Session | None:
        if not self.config.session_file.exists():
            return None
        try:
            with open(self.config.session_file) as f:
                data = json.load(f)
            return Session.from_dict(data)
        except Exception as e:
            logger.warning(f"Failed to load session: {e}")
            return None

    def _save_session(self, session: Session):
        try:
            self.config.session_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config.session_file, "w") as f:
                json.dump(session.to_dict(), f)
            from contextlib import suppress

            with suppress(AttributeError):
                os.chmod(self.config.session_file, 0o600)
        except Exception as e:
            logger.warning(f"Failed to save session: {e}")

    def _clear_saved_session(self):
        try:
            if self.config.session_file.exists():
                self.config.session_file.unlink()
        except Exception:
            pass
