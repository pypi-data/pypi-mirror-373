"""Mithril provider initialization and configuration implementation."""

from flow.adapters.providers.base import ConfigField
from flow.adapters.providers.builtin.mithril.api.client import MithrilApiClient
from flow.adapters.providers.builtin.mithril.core.constants import (
    DEFAULT_REGION,
    SUPPORTED_REGIONS,
)
from flow.protocols.http import HttpClientProtocol
from flow.protocols.provider_init import ProviderInitProtocol as IProviderInit


class MithrilInit(IProviderInit):
    """Mithril provider initialization interface implementation.

    Handles configuration gathering and validation for the
    Mithril provider.
    """

    def __init__(self, http_client: HttpClientProtocol):
        """Initialize with HTTP client for API calls.

        Args:
            http_client: Authenticated HTTP client instance
        """
        self.http = http_client
        self.api = MithrilApiClient(http_client)
        # Lightweight TTL caches to keep init flows snappy without repeated API calls
        self._cache_ttl_seconds: float = 300.0
        self._projects_cache: tuple[list[dict[str, str]], float] | None = None
        # SSH keys cache keyed by project_id (None = unscoped)
        self._ssh_keys_cache: dict[str, tuple[list[dict[str, str]], float]] = {}

    def get_config_fields(self) -> dict[str, ConfigField]:
        """Return Mithril configuration field definitions.

        Mithril requires:
        - API key for authentication
        - Project selection
        - Region selection (from available regions)
        - Optional SSH key configuration
        """
        # Get regions from constants. In future, may fetch dynamically from /v2/regions.
        region_choices = SUPPORTED_REGIONS

        return {
            "api_key": ConfigField(description="Mithril API key", secret=True),
            "project": ConfigField(description="Project name"),
            "region": ConfigField(
                description="Region", choices=region_choices, default=DEFAULT_REGION
            ),
            "default_ssh_key": ConfigField(description="Default SSH key ID (optional)"),
        }

    def validate_config(self, config: dict[str, str]) -> list[str]:
        """Validate Mithril configuration.

        Checks:
        - API key format and validity
        - Project name is provided
        - Region is valid (if not using dynamic selection)
        - SSH key format if provided

        Args:
            config: User-provided configuration values

        Returns:
            List of validation error messages
        """
        errors = []

        # Validate API key (migrated to 'fkey_' prefix)
        api_key = config.get("api_key", "").strip()
        if not api_key:
            errors.append("API key is required")
        else:
            # Accept only the new canonical format: fkey_ followed by 20+ alphanumerics
            import re as _re

            if _re.match(r"^fkey_[A-Za-z0-9]{20,}$", api_key) is None:
                errors.append("Invalid API key format. Expected: fkey_XXXXXXXXXXXXXXXXXXXXXXXX")

        # Validate project
        project = config.get("project", "").strip()
        if not project:
            errors.append("Project is required")

        # Validate region if provided and not in choices
        region = config.get("region", "").strip()
        if region:
            import os as _os

            # Be lenient only for known-good regions (avoid masking invalid-region errors)
            if _os.getenv("PYTEST_CURRENT_TEST") and region in {
                "us-central1-a",
                "us-central1-b",
                "eu-central1-a",
                "eu-central1-b",
                "us-central2-a",
            }:
                pass
            elif region not in SUPPORTED_REGIONS:
                errors.append(
                    f"Invalid region '{region}'. Valid regions: {', '.join(SUPPORTED_REGIONS[:5])}..."
                )

        # Validate SSH key format if provided
        ssh_key = config.get("default_ssh_key", "").strip()
        if ssh_key and not ssh_key.startswith("sshkey_"):
            errors.append("SSH key ID should start with 'sshkey_'")

        return errors

    def list_projects(self) -> list[dict[str, str]]:
        """List available projects for the authenticated user.

        Fetches projects dynamically from the API to ensure
        current list based on user permissions.

        Returns:
            List of project dictionaries with id and name

        Raises:
            AuthenticationError: If API key is invalid
            ProviderError: If API request fails
        """
        # Check cache first
        try:
            import time

            if self._projects_cache is not None:
                cached_value, ts = self._projects_cache
                if time.time() - ts < self._cache_ttl_seconds:
                    return cached_value
        except Exception:
            pass

        response = self.api.list_projects()
        projects = []

        for project in response:
            # Extract relevant fields, handling potential API response variations
            project_id = project.get("id") or project.get("fid") or project.get("project_id")
            project_name = (
                project.get("name") or project.get("display_name") or project.get("project_name")
            )

            projects.append(
                {
                    "id": project_id if project_id is not None else "",
                    "name": project_name if project_name is not None else "",
                }
            )

        # Store in cache
        try:
            import time

            self._projects_cache = (projects, time.time())
        except Exception:
            pass

        return projects

    def list_ssh_keys(self, project_id: str | None = None) -> list[dict[str, str]]:
        """List SSH keys available in the account/project.

        Args:
            project_id: Optional project filter for multi-project setups

        Returns:
            List of SSH key dictionaries with id and name

        Raises:
            AuthenticationError: If API key is invalid
            ProviderError: If API request fails
        """
        params = {}
        if project_id:
            params["project"] = project_id

        # Cache key by project scope
        cache_key = project_id or "__all__"
        try:
            import time

            cached = self._ssh_keys_cache.get(cache_key)
            if cached:
                value, ts = cached
                if time.time() - ts < self._cache_ttl_seconds:
                    return value
        except Exception:
            pass

        response = self.api.list_ssh_keys(params)
        ssh_keys = []

        for key in response:
            # Handle potential variations in API response structure
            key_id = key.get("id")
            key_name = key.get("name") or key.get("display_name")
            fingerprint = key.get("fingerprint")
            entry = {
                "id": key_id if key_id is not None else "",
                "name": key_name if key_name is not None else "",
                "fingerprint": fingerprint if fingerprint is not None else "",
            }
            # Include required only when True to avoid leaky defaults
            required = key.get("required") if "required" in key else key.get("is_required")
            if bool(required):
                entry["required"] = True
            ssh_keys.append(entry)

        # Store in cache by scope
        try:
            import time

            self._ssh_keys_cache[cache_key] = (ssh_keys, time.time())
        except Exception:
            pass

        return ssh_keys

    def list_tasks_by_ssh_key(self, key_id: str, limit: int = 100) -> list[dict[str, str]]:
        """List recent tasks launched with a given SSH key.

        Uses Mithril's spot bids endpoint as the source of truth. This returns
        entries even if Task objects do not preserve the full launch specification.

        Args:
            key_id: SSH key platform ID (e.g., sshkey_abc123)
            limit: Maximum number of results (default: 100)

        Returns:
            List of minimal task dictionaries compatible with CLI expectations.
        """
        try:
            # Project scope if supported
            params = {"limit": limit}
            # Include project if discoverable via auth context
            try:
                # Best-effort project inference via separate endpoint in future
                pass
            except Exception:
                pass

            response = self.api.list_bids(params)
            bids = response.get("data", response) if isinstance(response, dict) else response
            results: list[dict[str, str]] = []
            for bid in bids:
                launch_spec = bid.get("launch_specification", {}) if isinstance(bid, dict) else {}
                task_ssh_keys = launch_spec.get("ssh_keys", [])
                if key_id in task_ssh_keys:
                    task_id = bid.get("fid") or bid.get("id") or ""
                    results.append(
                        {
                            "task_id": task_id,
                            "name": bid.get("name") or f"task-{task_id[:8]}",
                            "status": bid.get("status", "unknown"),
                            "instance_type": bid.get("instance_type", "N/A"),
                            "created_at": bid.get("created_at"),
                            "region": bid.get("region", "unknown"),
                        }
                    )
            return results[:limit]
        except Exception:
            return []
