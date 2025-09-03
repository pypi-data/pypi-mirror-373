"""Authentication support for Flow SDK (core module).

Provides API key and session-based authentication helpers and a simple
"ensure_initialized" check used by interactive flows.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from flow.adapters.http.auth import (
    AuthConfig as _AuthConfig,
)
from flow.adapters.http.auth import (
    Authenticator as _Authenticator,
)
from flow.adapters.http.auth import (
    Session as _Session,
)
from flow.errors import AuthenticationError
from flow.protocols.http import HttpClientProtocol

logger = logging.getLogger(__name__)


class AuthConfig(_AuthConfig):  # type: ignore[misc]
    """Deprecated: use flow.adapters.http.auth.AuthConfig."""

    def __init__(
        self,
        api_key: str | None = None,
        email: str | None = None,
        password: str | None = None,
        session_file: Path | None = None,
    ):
        """Initialize auth config.

        Args:
            api_key: API key for authentication
            email: Email for email/password auth
            password: Password for email/password auth
            session_file: Path to store session data
        """
        # Use canonical environment variable only
        self.api_key = api_key or os.getenv("MITHRIL_API_KEY")
        self.email = email
        self.password = password
        self.session_file = session_file or self._default_session_file()

    def _default_session_file(self) -> Path:
        """Get default session file path."""
        home = Path.home()
        flow_dir = home / ".flow"
        flow_dir.mkdir(exist_ok=True)
        return flow_dir / "session.json"

    @property
    def has_api_key(self) -> bool:
        """Check if API key is available."""
        return bool(self.api_key)

    @property
    def has_credentials(self) -> bool:
        """Check if email/password credentials are available."""
        return bool(self.email and self.password)


class Session(_Session):  # type: ignore[misc]
    """Deprecated: use flow.adapters.http.auth.Session."""

    def __init__(self, token: str, expires_at: datetime, user_id: str):
        """Initialize session.

        Args:
            token: Session token
            expires_at: When session expires
            user_id: ID of authenticated user
        """
        self.token = token
        self.expires_at = expires_at
        self.user_id = user_id

    @property
    def is_valid(self) -> bool:
        """Check if session is still valid."""
        return datetime.now() < self.expires_at

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "token": self.token,
            "expires_at": self.expires_at.isoformat(),
            "user_id": self.user_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Session:
        """Create from dictionary."""
        return cls(
            token=data["token"],
            expires_at=datetime.fromisoformat(data["expires_at"]),
            user_id=data["user_id"],
        )


class Authenticator(_Authenticator):  # type: ignore[misc]
    """Deprecated: use flow.adapters.http.auth.Authenticator."""

    def __init__(self, config: AuthConfig, http_client: HttpClientProtocol):
        """Initialize authenticator.

        Args:
            config: Authentication configuration
            http_client: HTTP client for API requests
        """
        self.config = config
        self.http = http_client
        self._session: Session | None = None

    def authenticate(self) -> str:
        """Get authentication token.

        Returns API key or session token based on configuration.

        Returns:
            Authentication token

        Raises:
            AuthenticationError: If authentication fails
        """
        # Try API key first
        if self.config.has_api_key:
            return self.config.api_key

        # Try existing session
        if self._session and self._session.is_valid:
            return self._session.token

        # Try loading saved session
        saved_session = self._load_session()
        if saved_session and saved_session.is_valid:
            self._session = saved_session
            return saved_session.token

        # Try email/password authentication
        if self.config.has_credentials:
            session = self._authenticate_with_credentials()
            self._session = session
            self._save_session(session)
            return session.token

        raise AuthenticationError("No valid authentication method available. Set MITHRIL_API_KEY.")

    def get_access_token(self) -> str:
        """Get access token for API requests.

        Convenience wrapper for authenticate().
        """
        return self.authenticate()

    def _authenticate_with_credentials(self) -> Session:
        """Authenticate with email/password.

        Returns:
            Session object

        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            response = self.http.request(
                method="POST",
                url="/auth/login",
                json={
                    "email": self.config.email,
                    "password": self.config.password,
                },
                retry_server_errors=False,  # Don't retry auth failures
            )

            # Extract session data
            token = response.get("token")
            expires_in = response.get("expires_in", 3600)  # Default 1 hour
            user_id = response.get("user_id", "")

            if not token:
                raise AuthenticationError("No token in login response")

            # Create session
            expires_at = datetime.now() + timedelta(seconds=expires_in)
            session = Session(token, expires_at, user_id)

            logger.info(f"Successfully authenticated as user {user_id}")
            return session

        except Exception as e:
            raise AuthenticationError(f"Login failed: {e}") from e

    def logout(self):
        """Log out and clear session."""
        if self._session:
            try:
                # Notify server
                self.http.request(
                    method="POST",
                    url="/auth/logout",
                    headers={"Authorization": f"Bearer {self._session.token}"},
                )
            except Exception as e:
                logger.warning(f"Logout request failed: {e}")

            # Clear local session
            self._session = None
            self._clear_saved_session()

    def _load_session(self) -> Session | None:
        """Load saved session from file."""
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
        """Save session to file."""
        try:
            # Ensure directory exists
            self.config.session_file.parent.mkdir(parents=True, exist_ok=True)

            # Save with restricted permissions
            with open(self.config.session_file, "w") as f:
                json.dump(session.to_dict(), f)

            # Set file permissions (Unix only)
            try:
                os.chmod(self.config.session_file, 0o600)
            except AttributeError:
                pass  # Windows doesn't support chmod

        except Exception as e:
            logger.warning(f"Failed to save session: {e}")

    def _clear_saved_session(self):
        """Remove saved session file."""
        try:
            if self.config.session_file.exists():
                self.config.session_file.unlink()
        except Exception as e:
            logger.warning(f"Failed to clear session: {e}")


def ensure_initialized() -> bool:
    """Ensure Flow is properly configured, launching interactive setup if needed.

    Returns:
        True if configuration is valid, False if setup was cancelled
    """
    from flow.application.config.loader import ConfigLoader

    loader = ConfigLoader()
    if loader.has_valid_config():
        return True

    # No valid configuration found - defer messaging to CLI handler
    # Avoid printing here to prevent duplicate/conflicting messages.
    logger.debug("No Flow configuration found (ensure_initialized returned False)")
    return False


def validate_config() -> bool:
    """Validate current configuration and connectivity.

    Returns:
        True if configuration is valid and API is reachable
    """
    try:
        from flow.sdk.client import Flow

        # Try to create client - this will validate credentials
        client = Flow()
        # Try a simple API call to verify connectivity
        try:
            client.status("test-connection")
        except Exception as e:
            # If error is "not found", auth worked
            if "not found" in str(e).lower():
                return True
            raise
        return True
    except AuthenticationError:
        logger.error("Authentication failed - invalid API key")
        return False
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return False


def create_authenticator(
    api_key: str | None = None,
    email: str | None = None,
    password: str | None = None,
    http_client: HttpClientProtocol | None = None,
) -> Authenticator:
    """Create authenticator with config."""
    try:
        from flow.adapters.http.client import HttpClient
    except Exception:
        from flow.adapters.http.client import HttpClient  # type: ignore

    config = AuthConfig(api_key=api_key, email=email, password=password)

    if not http_client:
        # Create basic HTTP client for auth requests
        http_client = HttpClient(
            base_url=os.getenv("MITHRIL_API_URL", "https://api.mithril.ai"),
        )

    return Authenticator(config, http_client)


__all__ = [
    "AuthConfig",
    "Session",
    "Authenticator",
    "ensure_initialized",
    "validate_config",
    "create_authenticator",
]
