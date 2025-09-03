from __future__ import annotations

"""SSH access resolution helpers for Mithril provider.

Encapsulates key matching/caching and bid-driven SSH access preparation so the
provider facade can remain thin.
"""

import logging
import os
from pathlib import Path

from flow.core.utils.ssh_key_cache import SSHKeyCache

logger = logging.getLogger(__name__)


def parse_ssh_destination(ssh_destination: str | None) -> tuple[str | None, int]:
    """Parse SSH destination string into host and port.

    Args:
        ssh_destination: SSH destination in format "host:port" or just "host"

    Returns:
        Tuple of (host, port) where port defaults to 22
    """
    if not ssh_destination:
        return None, 22

    # Handle "host:port" format
    if ":" in ssh_destination:
        parts = ssh_destination.rsplit(":", 1)
        try:
            return parts[0], int(parts[1])
        except (ValueError, IndexError):
            return ssh_destination, 22

    return ssh_destination, 22


class SshAccessService:
    """Resolves local SSH key to use for a task and prepares access errors.

    This service depends on the provider's `ssh_key_manager` for platform key
    lookup and local key matching. It does not perform any network operations on
    its own beyond accessing the provider's collaborators.
    """

    def __init__(self, ssh_key_manager) -> None:  # type: ignore[no-any-unimported]
        self.ssh_key_manager = ssh_key_manager

    def get_task_ssh_connection_info(self, provider, task_id: str) -> tuple[Path | None, str]:
        """Get SSH connection info for a task.

        Returns (private_key_path, error_message). Error message is empty string
        on success.
        """
        # Ensure SSH operations are scoped to the active project
        try:
            if getattr(self.ssh_key_manager, "project_id", None) is None:
                self.ssh_key_manager.project_id = provider._get_project_id()
        except Exception:
            pass

        ssh_cache = SSHKeyCache()

        # Try to discover platform keys to validate cached entry
        bid = None
        try:
            bid = provider._get_bid(task_id)
        except Exception:
            bid = None

        platform_keys = None
        if bid:
            try:
                launch_spec = bid.get("launch_specification", {})
                platform_keys = launch_spec.get("ssh_keys", []) or None
            except Exception:
                platform_keys = None

        cached_path = ssh_cache.get_key_path(task_id, validate_with_platform_keys=platform_keys)
        if cached_path:
            return Path(cached_path), ""

        # Not cached, resolve via bid
        if bid is None:
            bid = provider._get_bid(task_id)

        ssh_key_path, error_msg = self.prepare_ssh_access(provider, bid)

        if ssh_key_path:
            try:
                ssh_cache.save_key_path(task_id, str(ssh_key_path), platform_key_ids=platform_keys)
            except Exception:
                pass

        return ssh_key_path, error_msg

    def prepare_ssh_access(self, provider, bid: dict) -> tuple[Path | None, str]:
        """Prepare SSH access by finding matching local keys for the bid.

        Returns (private_key_path, error_message). Error message is empty string
        on success.
        """
        # SSH keys configured on the bid
        launch_spec = bid.get("launch_specification", {})
        bid_ssh_keys = launch_spec.get("ssh_keys", []) or []

        # Respect explicit override for power-users/automation
        if os.environ.get("MITHRIL_SSH_KEY"):
            ssh_key_path = Path(os.environ["MITHRIL_SSH_KEY"]).expanduser()
            if ssh_key_path.exists():
                return ssh_key_path, ""

        # If the bid has no SSH keys, try conservative fallbacks before failing.
        if not bid_ssh_keys:
            # 1) Try configured platform key IDs from provider config
            try:
                provider_cfg = (
                    provider.config.provider_config
                    if isinstance(provider.config.provider_config, dict)
                    else {}
                )
                cfg_keys = provider_cfg.get("ssh_keys")
                if isinstance(cfg_keys, list) and cfg_keys:
                    logger.debug(
                        "SSH fallback: trying provider-config keys: %s",
                        ", ".join([str(k) for k in cfg_keys]),
                    )
                    for key_id in cfg_keys:
                        try:
                            private_key_path = self.ssh_key_manager.find_matching_local_key(
                                str(key_id)
                            )
                            if private_key_path:
                                logger.debug(
                                    "SSH fallback success: using %s for key %s",
                                    private_key_path,
                                    key_id,
                                )
                                return private_key_path, ""
                        except Exception:
                            continue
            except Exception:
                pass

            # 2) If the task is still pending/starting, surface a more accurate message
            try:
                status = str(bid.get("status", "")).lower()
                instances = bid.get("instances", [])
                if status in {"pending", "open", "starting"} or not instances:
                    return (
                        None,
                        (
                            "Instance is still starting; SSH may not be ready yet.\n"
                            "Try again in 1–2 minutes, or run 'flow status' to check readiness."
                        ),
                    )
            except Exception:
                pass

            # 3) Fail with actionable guidance only when clearly keyless
            return (
                None,
                (
                    "This instance was created without SSH keys; authentication will fail.\n"
                    "Solutions:\n"
                    "  - Add a project SSH key and recreate the dev VM: flow ssh-keys upload ~/.ssh/<your_key>.pub && flow cancel <dev-vm> && flow dev\n"
                    "  - Or set MITHRIL_SSH_KEY=/path/to/private/key and retry\n"
                ),
            )

        # Resolve against platform keys and local names/paths deterministically
        for ssh_key_id in bid_ssh_keys:
            # Try platform key → local private key via public key match
            private_key_path = self.ssh_key_manager.find_matching_local_key(ssh_key_id)
            if private_key_path:
                return private_key_path, ""

            # Try path-like references
            try:
                p = Path(str(ssh_key_id)).expanduser()
                if p.exists() and p.is_file():
                    return p, ""
            except Exception:
                pass

        # No matching key found - build precise error (do not guess a local key)
        key_names: list[str] = []
        for key_id in bid_ssh_keys[:3]:
            try:
                key = self.ssh_key_manager.get_key(key_id)
            except Exception:
                key = None
            key_names.append(f"'{getattr(key, 'name', None)}' ({key_id})" if key else key_id)

        keys_desc = ", ".join(key_names)
        if len(bid_ssh_keys) > 3:
            keys_desc += f" and {len(bid_ssh_keys) - 3} more"

        return (
            None,
            (
                "No matching local SSH key found for required platform key(s): "
                f"{keys_desc}.\n"
                "To fix this:\n"
                "  1. Ensure the corresponding private key exists locally (check ~/.flow/keys and ~/.ssh)\n"
                "  2. Or export MITHRIL_SSH_KEY=/path/to/private/key and retry\n"
                "  3. Or upload your local key to the platform: flow ssh-keys upload ~/.ssh/<key>.pub\n"
            ),
        )
