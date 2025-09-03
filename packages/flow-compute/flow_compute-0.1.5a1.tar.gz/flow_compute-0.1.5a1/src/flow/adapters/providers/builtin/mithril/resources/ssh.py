"""SSH key management component for the Mithril provider.

Provides SSH key operations including automatic provisioning and error handling.
"""

import json
import logging
import os
import platform
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from flow.adapters.providers.builtin.mithril.api.client import MithrilApiClient
from flow.adapters.providers.builtin.mithril.api.types import SSHKeyModel as SSHKey
from flow.errors import AuthenticationError, FlowError

logger = logging.getLogger(__name__)


class SSHKeyError(FlowError):
    """Base error for SSH key operations."""

    pass


class SSHKeyNotFoundError(SSHKeyError):
    """Raised when SSH keys cannot be found or created."""

    pass


class SSHKeyManager:
    """Manages SSH keys with automatic provisioning and caching."""

    def __init__(
        self, api_client: MithrilApiClient | None = None, project_id: str | None = None, **kwargs
    ):
        """Initialize SSH key manager.

        Args:
            http_client: HTTP client for API requests
            project_id: Optional project ID for scoped operations
        """
        # Accept either MithrilApiClient via 'api_client' or raw HttpClientPort via legacy 'http_client'
        if api_client is None and "http_client" in kwargs:
            http_client = kwargs.get("http_client")
            # Wrap legacy http client
            from flow.adapters.providers.builtin.mithril.api.client import MithrilApiClient as _Api

            api_client = _Api(http_client)  # type: ignore[arg-type]

        assert api_client is not None, "api_client or http_client is required"
        # Keep both references when possible for centralized operations
        self._api: MithrilApiClient = api_client  # type: ignore[assignment]
        self.http = getattr(api_client, "_http", None) or api_client  # type: ignore[assignment]
        self.project_id = project_id
        self._keys_cache: list[SSHKey] | None = None
        self._key_dir = Path.home() / ".flow" / "keys"

    def ensure_keys(self, requested_keys: list[str] | None = None) -> list[str]:
        """Ensure SSH keys are available for use.

        This method follows a fallback strategy:
        1. Use explicitly provided key IDs if given
        2. Use existing keys from the project
        3. Optionally create a default key if none exist

        Args:
            requested_keys: Optional list of specific SSH key IDs to use

        Returns:
            List of SSH key IDs ready for use

        Raises:
            SSHKeyNotFoundError: If no keys can be obtained
        """
        # Use explicitly provided keys if given
        if requested_keys:
            logger.debug(f"Using {len(requested_keys)} explicitly provided SSH keys")
            return requested_keys

        # Get existing keys
        existing_keys = self.list_keys()
        if existing_keys:
            key_ids = [key.fid for key in existing_keys]
            logger.debug(f"Using {len(key_ids)} existing SSH keys from project")
            return key_ids

        # No keys available
        logger.debug("No SSH keys available for the project")

        # Optionally try to create a default key from environment
        if default_key := self._try_create_default_key():
            return [default_key]

        # Return empty list - let the caller decide if this is an error
        return []

    def list_keys(self) -> list[SSHKey]:
        """List all SSH keys for the project.

        Returns:
            List of SSHKey objects
        """
        if self._keys_cache is not None:
            return self._keys_cache

        try:
            params = {}
            if self.project_id:
                params["project"] = self.project_id  # API expects 'project', not 'project_id'

            response = self._api.list_ssh_keys(params)

            # API returns list directly
            keys_data = response if isinstance(response, list) else []

            # Normalize optional fields like `required` which some APIs expose
            normalized_keys: list[SSHKey] = []
            for k in keys_data:
                if "fid" not in k or "name" not in k:
                    continue
                try:
                    normalized_keys.append(SSHKey.from_api(k))
                except Exception:
                    # Fallback minimal mapping if shape drifts
                    normalized_keys.append(
                        SSHKey(
                            fid=k.get("fid", ""),
                            name=k.get("name", ""),
                            public_key=k.get("public_key", ""),
                            created_at=k.get("created_at"),
                            required=k.get("required"),
                        )
                    )

            self._keys_cache = normalized_keys

            logger.debug(f"Loaded {len(self._keys_cache)} SSH keys from API")
            return self._keys_cache

        except Exception as e:
            # Never surface low-level provider validation noise to CLI display.
            # Log at debug level and return empty to trigger graceful fallbacks.
            try:
                msg = str(e)
            except Exception:
                msg = "<unknown error>"
            logger.debug(f"Fetching SSH keys failed; continuing without keys: {msg}")
            return []

    def create_key(self, name: str, public_key: str = None) -> str:
        """Create a new SSH key.

        Args:
            name: Key name
            public_key: SSH public key content (optional - if not provided, Mithril generates one)

        Returns:
            ID of the created key

        Raises:
            SSHKeyError: If key creation fails
        """
        payload = {
            "name": name,
        }

        # Only include public_key if provided
        if public_key:
            payload["public_key"] = public_key.strip()

        if self.project_id:
            payload["project"] = self.project_id

        try:
            response = self._api.create_ssh_key(payload)

            key_id = response.get("fid")
            if not key_id:
                raise SSHKeyError(f"No key ID returned in response: {response}")

            # Invalidate cache (API + task key-path cache)
            self.invalidate_cache()

            logger.info(f"Created SSH key '{name}' with ID: {key_id}")
            return key_id

        except Exception as e:
            raise SSHKeyError(f"Failed to create SSH key '{name}': {e}") from e

    def delete_key(self, key_id: str) -> bool:
        """Delete an SSH key.

        Args:
            key_id: SSH key ID to delete

        Returns:
            True if successful, False otherwise

        Raises:
            SSHKeyNotFoundError: If the key doesn't exist
            SSHKeyError: For other deletion failures
        """
        try:
            self._api.delete_ssh_key(key_id)

            # Invalidate cache (API + task key-path cache)
            self.invalidate_cache()

            logger.info(f"Deleted SSH key: {key_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete SSH key {key_id}: {e}")
            # Preserve the original error for better debugging
            error_msg = str(e)
            if "not found" in error_msg.lower():
                raise SSHKeyNotFoundError(f"SSH key {key_id} not found") from e
            raise SSHKeyError(f"Failed to delete SSH key {key_id}: {error_msg}") from e

    def get_key(self, key_id: str) -> SSHKey | None:
        """Get a specific SSH key by ID.

        Args:
            key_id: SSH key ID

        Returns:
            SSHKey if found, None otherwise
        """
        keys = self.list_keys()
        for key in keys:
            if key.fid == key_id:
                return key
        return None

    def find_keys_by_name(self, name: str) -> list[SSHKey]:
        """Find SSH keys by name.

        Args:
            name: Key name to search for

        Returns:
            List of matching SSH keys (may be empty)
        """
        keys = self.list_keys()
        return [k for k in keys if k.name == name]

    def invalidate_cache(self):
        """Clear the cache, forcing fresh lookups."""
        self._keys_cache = None
        try:
            # Also clear the task-id → key-path cache to prevent stale SSH keys
            # being used after key create/delete operations.
            from flow.core.utils.ssh_key_cache import SSHKeyCache

            SSHKeyCache().clear()
        except Exception as e:
            # Best-effort: cache invalidation should never hard-fail operations
            logger.debug(f"Failed to clear SSHKeyCache: {e}")
        # Invalidate higher-level caches that may hold key lists
        try:
            from flow.cli.utils.prefetch import invalidate_cache_for_current_context

            invalidate_cache_for_current_context(["ssh_keys"])  # type: ignore[arg-type]
        except Exception:
            pass
        # Also clear provider-init scoped key cache if reachable
        try:
            init = getattr(self.http, "_provider_init", None)
            if init is not None and hasattr(init, "_ssh_keys_cache"):
                try:
                    init._ssh_keys_cache.clear()
                except Exception:
                    pass
        except Exception:
            pass
        logger.debug("SSH key caches invalidated")

    def ensure_platform_keys(self, key_references: list[str]) -> list[str]:
        """Ensure local SSH keys are uploaded to platform.

        This method handles different key reference types:
        - Platform IDs (sshkey_*): Used directly
        - Key names: Resolved locally and uploaded if needed
        - Paths: Read and uploaded if needed

        Note: _auto_ is handled at a higher level in the provider's _get_ssh_keys method.

        Args:
            key_references: List of key references (names, paths, or platform IDs)

        Returns:
            List of platform SSH key IDs
        """
        # Minimal resolver: accept platform IDs, file paths, or project key names
        platform_keys = []

        for key_ref in key_references:
            # Skip _auto_ - it should be handled at provider level
            if key_ref == "_auto_":
                logger.debug(
                    "Skipping '_auto_' in ensure_platform_keys - should be handled at provider level"
                )
                continue

            # Platform SSH key IDs can be used directly (heuristic: prefix)
            if isinstance(key_ref, str) and key_ref.startswith("sshkey_"):
                platform_keys.append(key_ref)
                continue

            # For local keys, try to resolve as path, else resolve by project name
            local_key_path = None
            try:
                p = Path(str(key_ref)).expanduser()
                if p.exists() and p.is_file():
                    local_key_path = p
            except Exception:
                local_key_path = None
            if local_key_path is None and isinstance(key_ref, str):
                matches = self.find_keys_by_name(key_ref)
                if matches:
                    platform_keys.append(matches[0].fid)
                    continue
            if not local_key_path:
                logger.warning(
                    f"Could not resolve SSH key '{key_ref}'\n"
                    f"  - Not found locally in ~/.ssh/\n"
                    f"  - Not found on platform (check 'flow ssh-keys get')\n"
                    f"  - May have different format (RSA vs ED25519)"
                )
                continue

            # Check if this key already exists on platform
            public_key_path = local_key_path.with_suffix(".pub")
            if not public_key_path.exists():
                logger.warning(
                    f"No public key found at {local_key_path}.pub\n"
                    f"  - Ensure both private and public keys exist\n"
                    f"  - Run 'ssh-keygen -y -f {local_key_path} > {local_key_path}.pub' to regenerate"
                )
                continue

            public_key_content = public_key_path.read_text().strip()

            # Check if key with same content already exists
            existing_platform_key = self._find_existing_key_by_content(public_key_content)
            if existing_platform_key:
                logger.info(
                    f"SSH key '{key_ref}' already exists on platform as {existing_platform_key}"
                )
                platform_keys.append(existing_platform_key)
                continue

            # Upload the key
            try:
                # Use the original reference as the name for clarity
                key_name = key_reference.value
                if key_name.startswith("~/"):
                    key_name = key_name.replace("~/", "home_")
                if "/" in key_name:
                    key_name = Path(key_name).stem

                platform_key_id = self.create_key(key_name, public_key_content)
                logger.info(f"Uploaded SSH key '{key_ref}' to platform as {platform_key_id}")
                platform_keys.append(platform_key_id)

                # Invalidate cache to include new key
                self.invalidate_cache()
            except Exception as e:
                logger.warning(f"Failed to upload SSH key '{key_ref}': {e}")

        return platform_keys

    def ensure_public_key(self, public_key: str, name: str | None = None) -> str:
        """Ensure a given public key exists on the platform and return its ID.

        Args:
            public_key: SSH public key content
            name: Optional display name to use if creating

        Returns:
            Platform SSH key ID
        """
        existing = self._find_existing_key_by_content(public_key)
        if existing:
            return existing
        key_name = name or "flow-key"
        return self.create_key(key_name, public_key)

    def _find_existing_key_by_content(self, public_key_content: str) -> str | None:
        """Find platform key with matching public key content.

        Args:
            public_key_content: SSH public key content

        Returns:
            Platform key ID if found, None otherwise
        """
        existing_keys = self.list_keys()

        # Normalize the key content for comparison
        normalized_content = public_key_content.strip()

        for key in existing_keys:
            if hasattr(key, "public_key") and key.public_key:
                if key.public_key.strip() == normalized_content:
                    return key.fid

        return None

    def _try_create_default_key(self) -> str | None:
        """Try to create a default SSH key for Mithril use.

        Selection order:
        1) MITHRIL_SSH_PUBLIC_KEY (content) -> create_key("flow-env-key", ...)
        2) MITHRIL_SSH_KEY (path)
           - if private key with secure perms and .pub exists -> create_key("flow-mithril-key", ...)
           - if .pub directly -> create_key("flow-mithril-key", ...)
           - if private key with insecure perms -> call auto_generate_key()
        3) Default local key ~/.ssh/id_rsa (secure perms and .pub exist) -> create_key("flow-default-id_rsa", ...)
        4) Previously auto-generated key (metadata cache)
        5) Auto-generate a fresh key (server/local)

        Returns:
            Key ID if created, or "ssh-key_auto" when a new key is auto-generated.
        """
        # 1) Public key content env
        env_pub = os.environ.get("MITHRIL_SSH_PUBLIC_KEY")
        if not env_pub:
            legacy_env_pub = os.environ.get("Mithril_SSH_PUBLIC_KEY")
            if legacy_env_pub:
                logger.warning(
                    "Environment variable 'Mithril_SSH_PUBLIC_KEY' is deprecated. Use 'MITHRIL_SSH_PUBLIC_KEY'."
                )
                env_pub = legacy_env_pub
        if env_pub:
            return self.create_key("flow-env-key", env_pub)

        # 2) File path env
        env_key = os.environ.get("MITHRIL_SSH_KEY")
        if not env_key:
            legacy_env_key = os.environ.get("Mithril_SSH_KEY")
            if legacy_env_key:
                logger.warning(
                    "Environment variable 'Mithril_SSH_KEY' is deprecated. Use 'MITHRIL_SSH_KEY'."
                )
                env_key = legacy_env_key
        if env_key:
            key_path = Path(env_key)
            if key_path.exists():
                if key_path.suffix == ".pub":
                    public_key = key_path.read_text().strip()
                    return self.create_key("flow-mithril-key", public_key)
                else:
                    pub_key = key_path.with_suffix(".pub")
                    if not pub_key.exists():
                        return self.auto_generate_key()
                    from flow.sdk.helpers.security import check_ssh_key_permissions

                    try:
                        check_ssh_key_permissions(key_path)
                    except Exception:
                        # Insecure permissions → fall back to auto generation
                        return self.auto_generate_key()
                    public_key = pub_key.read_text().strip()
                    return self.create_key("flow-mithril-key", public_key)
            # Missing file → auto-generate per tests
            return self.auto_generate_key()

        # 3) Default local key ~/.ssh/id_rsa (only when secure)
        default_priv = Path.home() / ".ssh" / "id_rsa"
        default_pub = default_priv.with_suffix(".pub")
        if default_priv.exists() and default_pub.exists():
            from flow.sdk.helpers.security import check_ssh_key_permissions

            try:
                check_ssh_key_permissions(default_priv)
                public_key = default_pub.read_text().strip()
                return self.create_key("flow-default-id_rsa", public_key)
            except Exception:
                # Insecure default key → fall back to auto generation
                return self.auto_generate_key()

        # 4) Previously auto-generated key (reuse only if local private exists and platform key is present)
        cached = self._get_cached_auto_key()
        if cached:
            try:
                local_private = self._check_metadata_for_key(cached)
                existing = self.get_key(cached)
                if existing is not None and local_private is not None:
                    # Ensure secure permissions on reuse
                    self._set_key_permissions(local_private)
                    return cached
            except Exception:
                # Ignore and continue to step 5
                pass

        # 5) Auto-generate as final fallback
        return self.auto_generate_key()

    def auto_generate_key(self) -> str | None:
        """Auto-generate an SSH key using the best available method.

        Tries server-side generation first (no local dependencies),
        falls back to local generation if needed.

        Returns:
            Optional[str]: SSH key ID if successful, None otherwise.
        """
        # Reuse-first: if we have a previously auto-generated key for this project and it still
        # exists on the platform, reuse it rather than creating a new key every run.
        try:
            cached_auto_key_id = self._get_cached_auto_key()
            if cached_auto_key_id:
                # Ensure local private key still exists for this cached key
                local_private_key_path = self._check_metadata_for_key(cached_auto_key_id)
                # Also ensure the key still exists on the platform
                existing = self.get_key(cached_auto_key_id)
                if existing is not None and local_private_key_path is not None:
                    logger.info(f"Reusing existing auto-generated SSH key: {cached_auto_key_id}")
                    return cached_auto_key_id
                else:
                    # If the platform key or local private key is missing, fall back to generation
                    logger.info(
                        "Cached auto-generated key missing locally or on platform; generating a new key"
                    )
        except Exception:
            # Non-fatal: proceed to generation path
            pass

        # Prevent duplicate generation in concurrent runs via a simple file lock
        lock_path: Path | None = None
        try:
            lock_path = self._acquire_autogen_lock(timeout=10.0)
            # Try server-side generation first (preferred)
            key_id = self.generate_server_key()
            if key_id:
                return key_id

            # Fall back to local generation if server-side fails
            logger.info("Server-side generation unavailable, trying local generation...")
            return self._generate_ssh_key()
        finally:
            if lock_path is not None:
                self._release_autogen_lock(lock_path)

    def generate_server_key(self) -> str | None:
        """Generate SSH key server-side using Mithril API.

        This is simpler than local generation as it doesn't require ssh-keygen.
        Mithril returns both public and private keys which we save locally.

        Returns:
            Optional[str]: SSH key ID if successful, None if generation failed.
        """
        try:
            # Generate unique name with timestamp
            import random

            timestamp = int(time.time())
            random_suffix = random.randint(1000, 9999)
            key_name = f"flow-auto-{timestamp}-{random_suffix}"

            logger.info("Generating SSH key server-side...")

            # Make direct API call to get full response including private key
            # Validate project ID
            if not self.project_id:
                raise ValueError("Project ID is required for SSH key generation")

            request_payload = {
                "name": key_name,
                "project": self.project_id,
                # No public_key - server will generate both keys
            }
            logger.info(f"SSH key generation request: name={key_name}, project={self.project_id}")

            response = self._api.create_ssh_key(request_payload)

            logger.debug(f"SSH key generation response: {response}")

            key_id = response.get("fid")
            if not key_id:
                # Gracefully fall back to local generation path
                logger.warning(
                    f"No key ID in server response; falling back to local generation: {response}"
                )
                return None

            # Save private key locally if returned
            if "private_key" in response:
                logger.info("Saving private key locally...")

                # Ensure key directory exists
                self._key_dir.mkdir(parents=True, exist_ok=True)

                # Save private key
                private_path = self._key_dir / key_name
                private_path.write_text(response["private_key"])
                private_path.chmod(0o600)  # Set proper permissions

                # Save public key if available
                if "public_key" in response:
                    public_path = self._key_dir / f"{key_name}.pub"
                    public_path.write_text(response["public_key"])
                    public_path.chmod(0o644)

                # Store metadata
                self._store_key_metadata(key_id, key_name, private_path)

                logger.info(f"Server-generated SSH key: {key_id}")
                logger.info(f"Private key saved to: {private_path}")
            else:
                logger.warning("No private key in server response")
                # Still return the key id so callers can proceed; local save skipped
                return key_id

            return key_id

        except Exception as e:
            logger.error(f"Failed to generate SSH key server-side: {type(e).__name__}: {e}")
            import traceback

            logger.debug(f"Full traceback: {traceback.format_exc()}")
            return None

    def _check_ssh_keygen_available(self) -> bool:
        """Check if ssh-keygen is available on the system.

        Returns:
            bool: True if ssh-keygen is found in PATH, False otherwise.
        """
        if shutil.which("ssh-keygen"):
            return True

        logger.warning(
            "ssh-keygen not found. SSH keys cannot be auto-generated. "
            "Install OpenSSH or manually create keys."
        )
        return False

    def generate_local_key(self) -> str | None:
        """Generate SSH key locally using ssh-keygen.

        Public method for local key generation when server-side isn't available.

        Returns:
            Optional[str]: SSH key ID if successful, None if generation failed.
        """
        return self._generate_ssh_key()

    def _generate_ssh_key(self) -> str | None:
        """Generate SSH key pair locally and register with Mithril.

        Creates an Ed25519 key pair using ssh-keygen, stores it in ~/.flow/keys,
        registers the public key with Mithril API, and tracks metadata locally.

        Returns:
            Optional[str]: SSH key ID if successful, None if generation failed.
        """
        # Check if ssh-keygen is available
        if not self._check_ssh_keygen_available():
            return None

        try:
            # Generate unique name with timestamp and random component
            import random

            timestamp = int(time.time())
            random_suffix = random.randint(1000, 9999)
            key_name = f"flow-auto-{timestamp}-{random_suffix}"

            # Generate key pair locally
            private_path, public_path = self._create_key_pair(key_name)

            # Read public key
            public_key = public_path.read_text().strip()

            # Register with Mithril API (best-effort)
            if not self.project_id:
                raise ValueError("Project ID is required for SSH key registration")

            key_id: str | None = None
            try:
                response = self._api.create_ssh_key(
                    {"name": key_name, "project": self.project_id, "public_key": public_key}
                )
                if isinstance(response, dict):
                    key_id = response.get("fid")
                else:
                    key_id = None
            except Exception as reg_err:
                logger.debug(f"Local key generated but registration failed: {reg_err}")

            if not key_id:
                # Registration failed or returned unexpected shape; still proceed with synthetic ID
                key_id = f"sshkey_auto_{timestamp}_{random_suffix}"
                logger.warning(
                    f"Proceeding with synthetic local key ID {key_id} due to registration issue."
                )

            # Store metadata and return usable key id
            self._store_key_metadata(key_id, key_name, private_path)
            logger.info(f"Auto-generated SSH key: {key_id}")
            return key_id

        except Exception as e:
            logger.debug(f"Failed to auto-generate SSH key: {e}")
            return None

    def _create_key_pair(self, key_name: str) -> tuple[Path, Path]:
        """Create SSH key pair using ssh-keygen.

        Args:
            key_name: Base name for the key files (without extension).

        Returns:
            Tuple[Path, Path]: Paths to (private_key, public_key).

        Raises:
            SSHKeyError: If ssh-keygen fails or returns non-zero exit code.
        """
        key_dir = Path.home() / ".flow" / "keys"
        key_dir.mkdir(parents=True, exist_ok=True)

        private_path = key_dir / key_name
        public_path = private_path.with_suffix(".pub")

        # Build ssh-keygen command with secure defaults
        cmd = [
            "ssh-keygen",
            "-t",
            "ed25519",  # Ed25519 for better security and performance
            "-f",
            str(private_path),
            "-N",
            "",  # Empty passphrase for automation
            "-C",
            f"flow-auto@{platform.node()}",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)  # Prevent hanging
        if result.returncode != 0:
            raise SSHKeyError(f"ssh-keygen failed: {result.stderr}")

        # Ensure correct permissions
        self._set_key_permissions(private_path)

        return private_path, public_path

    def _store_key_metadata(self, key_id: str, key_name: str, private_path: Path) -> None:
        """Store metadata about auto-generated SSH key.

        Persists key information to ~/.flow/keys/metadata.json for future reuse.
        Updates existing metadata file if present, preserving other entries.

        Args:
            key_id: Mithril-assigned SSH key ID.
            key_name: Human-readable key name.
            private_path: Path to the private key file.
        """
        key_dir = private_path.parent

        # Store metadata
        metadata = {
            "key_id": key_id,
            "key_name": key_name,
            "private_key_path": str(private_path),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "project": self.project_id,
            "auto_generated": True,
        }

        metadata_path = key_dir / "metadata.json"
        existing = {}
        if metadata_path.exists():
            try:
                existing = json.loads(metadata_path.read_text())
            except Exception:
                pass

        existing[key_id] = metadata
        metadata_path.write_text(json.dumps(existing, indent=2))
        self._set_key_permissions(metadata_path)

    def _get_cached_auto_key(self) -> str | None:
        """Check for previously auto-generated keys.

        Searches metadata.json for auto-generated keys belonging to the current
        project. Returns the most recently created key if multiple exist.

        Returns:
            Optional[str]: SSH key ID of most recent auto-generated key, or None.
        """
        metadata_path = Path.home() / ".flow" / "keys" / "metadata.json"
        if not metadata_path.exists():
            return None

        try:
            metadata = json.loads(metadata_path.read_text())
            # Filter keys by project and auto-generated flag
            project_keys = [
                (k, v)
                for k, v in metadata.items()
                if v.get("project") == self.project_id and v.get("auto_generated")
            ]
            if project_keys:
                # Sort by timestamp descending, return newest
                project_keys.sort(key=lambda x: x[1]["created_at"], reverse=True)
                return project_keys[0][0]
        except Exception:
            pass

        return None

    def _set_key_permissions(self, key_path: Path) -> None:
        """Set secure permissions on private key.

        Sets file permissions to 0600 (read/write for owner only) to meet
        SSH security requirements. Continues silently if permission setting
        fails (e.g., on non-Unix systems).

        Args:
            key_path: Path to the file requiring secure permissions.
        """
        try:
            key_path.chmod(0o600)
        except Exception as e:
            logger.debug(f"Could not set key permissions: {e}")
            # Continue execution - functional key with suboptimal permissions
            # is preferable to complete failure

    def _acquire_autogen_lock(self, timeout: float = 10.0) -> Path | None:
        """Acquire a simple lock to serialize auto-generation across processes.

        Creates a lock file in the key directory, waiting up to timeout seconds.

        Returns:
            Path to the lock file if acquired, otherwise None (lock not acquired).
        """
        try:
            self._key_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

        lock_file = self._key_dir / ".autogen.lock"
        deadline = time.time() + max(0.0, float(timeout))
        while time.time() < deadline:
            try:
                # Exclusive create; fails if file exists
                with open(lock_file, "x") as f:
                    f.write(str(os.getpid()))
                return lock_file
            except FileExistsError:
                # If stale (>60s), remove
                try:
                    if lock_file.exists():
                        mtime = lock_file.stat().st_mtime
                        if time.time() - mtime > 60:
                            lock_file.unlink(missing_ok=True)
                except Exception:
                    pass
                time.sleep(0.2)
            except Exception:
                break
        # Could not acquire; continue without lock to avoid blocking indefinitely
        return None

    def _release_autogen_lock(self, lock_path: Path) -> None:
        """Release the auto-generation lock if we own it."""
        try:
            if lock_path.exists():
                lock_path.unlink(missing_ok=True)
        except Exception:
            pass

    def find_matching_local_key(self, api_key_id: str) -> Path | None:
        """Find local private key that matches an API SSH key.

        Searches standard SSH locations and cached metadata to find
        a local private key corresponding to the given API key ID.

        Args:
            api_key_id: Mithril SSH key ID to match

        Returns:
            Path to matching private key if found, None otherwise
        """
        # Get API key details
        api_key = self.get_key(api_key_id)
        if not api_key or not api_key.public_key:
            logger.debug(f"API key {api_key_id} not found or has no public key")
            return None

        # Check metadata cache first for auto-generated keys
        cached_key = self._check_metadata_for_key(api_key_id)
        if cached_key and cached_key.exists():
            logger.debug(f"Resolved private key via metadata for {api_key_id} -> {cached_key}")
            return cached_key

        # Standard SSH key locations to check
        key_paths = []

        # First check MITHRIL_SSH_KEY environment variable (with legacy alias)
        env_key = os.environ.get("MITHRIL_SSH_KEY")
        if not env_key:
            legacy_env_key = os.environ.get("Mithril_SSH_KEY")
            if legacy_env_key:
                logger.warning(
                    "Environment variable 'Mithril_SSH_KEY' is deprecated. Use 'MITHRIL_SSH_KEY'."
                )
                env_key = legacy_env_key
        if env_key:
            env_path = Path(env_key).expanduser()
            if env_path.suffix != ".pub":
                key_paths.append(env_path)

        # Add standard key names
        standard_names = ["id_rsa", "id_ed25519", "id_ecdsa", "id_dsa"]
        for name in standard_names:
            key_paths.append(Path.home() / ".ssh" / name)

        # Also check all other SSH keys in ~/.ssh directory
        ssh_dir = Path.home() / ".ssh"
        if ssh_dir.exists():
            for key_file in ssh_dir.glob("*"):
                # Skip if it's a public key, directory, or already in our list
                if (
                    key_file.suffix != ".pub"
                    and key_file.is_file()
                    and key_file not in key_paths
                    and key_file.name not in ["known_hosts", "authorized_keys", "config"]
                ):
                    key_paths.append(key_file)

        # Try each potential private key
        for private_key_path in key_paths:
            if not private_key_path.exists():
                continue

            public_key_path = private_key_path.with_suffix(".pub")
            if not public_key_path.exists():
                continue

            try:
                local_public_key = public_key_path.read_text().strip()
                if self._keys_match(local_public_key, api_key.public_key):
                    logger.debug(
                        f"Matched platform key {api_key.fid} ({api_key.name}) to local private key {private_key_path}"
                    )
                    return private_key_path
            except Exception as e:
                logger.debug(f"Error reading {public_key_path}: {e}")
                continue

        logger.debug(f"No matching local key found for {api_key_id} ({api_key.name})")
        return None

    def _check_metadata_for_key(self, api_key_id: str) -> Path | None:
        """Check metadata cache for auto-generated key.

        Args:
            api_key_id: Mithril SSH key ID

        Returns:
            Path to private key if found in metadata, None otherwise
        """
        metadata_path = Path.home() / ".flow" / "keys" / "metadata.json"
        if not metadata_path.exists():
            return None

        try:
            metadata = json.loads(metadata_path.read_text())
            if api_key_id in metadata:
                key_info = metadata[api_key_id]
                private_path = Path(key_info.get("private_key_path", ""))
                if private_path.exists():
                    return private_path
        except Exception as e:
            logger.debug(f"Error reading metadata: {e}")

        return None

    def _keys_match(self, local_public_key: str, api_public_key: str) -> bool:
        """Compare two SSH public keys for equality.

        Normalizes keys before comparison to handle formatting differences.

        Args:
            local_public_key: Public key content from local file
            api_public_key: Public key content from API

        Returns:
            True if keys match, False otherwise
        """
        # Normalize keys - strip whitespace and comments
        local_normalized = self._normalize_public_key(local_public_key)
        api_normalized = self._normalize_public_key(api_public_key)

        return local_normalized == api_normalized

    # --- Admin operations ---
    def set_key_required(self, key_id: str, required: bool) -> bool:
        """Set or clear the 'required' flag on an SSH key.

        Requires project admin privileges on Mithril. When a key is marked as
        required, the platform expects it to be included in all new launches
        for the project. Flow also auto-includes required keys for convenience.

        Args:
            key_id: Platform SSH key ID (e.g., sshkey_abc123)
            required: True to mark as required, False to clear required flag

        Returns:
            True if the update succeeded, False otherwise
        """
        try:
            self._api.patch_ssh_key(key_id, {"required": bool(required)})
            # Invalidate cache so list_keys reflects latest state
            self.invalidate_cache()
            return True
        except AuthenticationError:
            # Bubble up explicit auth/permission errors so CLI can show actionable text
            raise
        except Exception as e:
            logger.error(f"Failed to update required flag for SSH key {key_id}: {e}")
            return False

    def _normalize_public_key(self, public_key: str) -> str:
        """Normalize SSH public key for comparison.

        Extracts the key type and base64 data, ignoring comments.

        Args:
            public_key: Raw public key content

        Returns:
            Normalized key string (type + base64 data)
        """
        try:
            # SSH public keys format: <type> <base64-data> [comment]
            parts = public_key.strip().split()
            if len(parts) >= 2:
                # Return type and key data only
                return f"{parts[0]} {parts[1]}"
            return public_key.strip()
        except Exception:
            return public_key.strip()
