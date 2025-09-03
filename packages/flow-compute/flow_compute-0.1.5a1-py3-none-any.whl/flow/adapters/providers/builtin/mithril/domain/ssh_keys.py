"""SSH key resolution and generation service."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flow.sdk.models import TaskConfig

logger = logging.getLogger(__name__)


class SSHKeyService:
    def __init__(self, ssh_key_manager, mithril_config=None) -> None:
        self._mgr = ssh_key_manager
        self._mithril_config = mithril_config

    def resolve_keys(self, requested: list[str] | None) -> list[str] | None:
        if not requested:
            return None
        # Special sentinel to auto-generate
        if requested == ["_auto_"]:
            existing = self._mgr.list_keys()
            # Always include any project-required keys
            required_ids = [k.fid for k in existing if getattr(k, "required", False)]
            # Prefer per-instance generation per docs; append required keys
            new_id = self._mgr.auto_generate_key()
            if new_id:
                merged = required_ids + [new_id]
                # Deduplicate and return
                seen: set[str] = set()
                result: list[str] = []
                for k in merged:
                    if k and k not in seen:
                        seen.add(k)
                        result.append(k)
                return result
            # Fallback: if generation fails, include required + any existing keys
            if existing:
                fallback = required_ids + [k.fid for k in existing]
                seen2: set[str] = set()
                uniq: list[str] = []
                for k in fallback:
                    if k and k not in seen2:
                        seen2.add(k)
                        uniq.append(k)
                return uniq
            return []
        filtered = [k for k in requested if k != "_auto_"]
        if not filtered:
            return None
        ensured = self._mgr.ensure_platform_keys(filtered)
        return ensured or None

    def merge_with_required(self, ssh_key_ids: list[str] | None) -> list[str]:
        """Ensure project-required SSH keys are always included in launch.

        Args:
            ssh_key_ids: Current list of SSH key IDs selected for launch

        Returns:
            Merged list including any project-required key IDs (deduplicated)
        """
        current = list(ssh_key_ids or [])
        platform_keys = self._mgr.list_keys()
        required_ids = [k.fid for k in platform_keys if getattr(k, "required", False)]
        if not required_ids:
            return current
        # Prepend required to make visibility obvious in any logs
        merged = required_ids + current
        # Deduplicate while preserving order
        seen: set[str] = set()
        result: list[str] = []
        for k in merged:
            if k not in seen:
                seen.add(k)
                result.append(k)
        return result

    def resolve_keys_for_task(self, config: TaskConfig, project_id_getter=None) -> list[str]:
        """Full SSH key resolution logic for task submission.

        This implements the complete resolution priority:
        1. Task config SSH keys
        2. Provider config SSH keys
        3. Environment variable (MITHRIL_SSH_KEY)
        4. Existing project keys with local private keys
        5. Auto-generation of new key

        Args:
            config: Task configuration
            project_id_getter: Callable to get project ID for scoping

        Returns:
            List of SSH key IDs to use for the task
        """
        # Ensure SSH operations are scoped to the active project
        if project_id_getter:
            try:
                if getattr(self._mgr, "project_id", None) is None:
                    self._mgr.project_id = project_id_getter()
            except Exception:
                pass

        # Resolution priority: task config > provider config > auto-generation
        requested_keys = config.ssh_keys
        if not requested_keys and self._mithril_config:
            requested_keys = getattr(self._mithril_config, "ssh_keys", None)

        resolved_keys: list[str] | None = None

        if requested_keys:
            # If the sentinel ['_auto_'] is specified, defer to standard resolution
            if requested_keys != ["_auto_"]:
                # Filter out accidental '_auto_' alongside explicit keys
                filtered_requested = [k for k in requested_keys if k != "_auto_"]
                if filtered_requested:
                    platform_keys = self._mgr.ensure_platform_keys(filtered_requested)
                    if platform_keys:
                        resolved_keys = platform_keys
                    else:
                        logger.warning(
                            "No SSH keys could be resolved from requested keys; "
                            "falling back to existing or auto-generated keys"
                        )

        if not resolved_keys:
            logger.debug("No SSH keys specified; resolving from environment and project")

            # Check environment variable for specific key
            env_key_path = os.environ.get("MITHRIL_SSH_KEY")
            if env_key_path:
                try:
                    env_path = Path(env_key_path).expanduser()
                    if env_path.exists() and env_path.is_file():
                        ensured = self._mgr.ensure_platform_keys([str(env_path)])
                        if ensured:
                            logger.info("Using SSH key from MITHRIL_SSH_KEY for launch")
                            resolved_keys = ensured
                except Exception:
                    pass

        # Prefer existing project keys that we also have locally
        if not resolved_keys:
            existing_keys = self._mgr.list_keys()
            if existing_keys:
                required_ids = [k.fid for k in existing_keys if getattr(k, "required", False)]

                # Find locally backed keys
                locally_available: list[str] = []
                for k in existing_keys:
                    try:
                        if self._mgr.find_matching_local_key(k.fid):
                            locally_available.append(k.fid)
                    except Exception:
                        continue

                if locally_available:
                    logger.info(
                        f"Using {len(locally_available)} existing project SSH key(s) with local private keys"
                    )
                    resolved_keys = required_ids + locally_available
                else:
                    # No local backups; auto-generate a fresh key
                    logger.info(
                        "No local private keys matching project SSH keys; auto-generating a new key"
                    )
                    generated_key_id = self._mgr.auto_generate_key()
                    if generated_key_id:
                        resolved_keys = required_ids + [generated_key_id]
                    else:
                        # Last resort: use existing keys
                        logger.info("Falling back to existing project SSH keys")
                        resolved_keys = required_ids or [k.fid for k in existing_keys]

        # If still nothing, auto-generate a new key
        if not resolved_keys:
            logger.info("No SSH keys found, auto-generating Mithril-specific SSH key")
            generated_key_id = self._mgr.auto_generate_key()
            if generated_key_id:
                logger.info(f"Successfully generated Mithril SSH key: {generated_key_id}")
                resolved_keys = [generated_key_id]
                # Try to backfill config for future runs
                self._backfill_config(generated_key_id)
            else:
                logger.warning(
                    "Failed to auto-generate SSH key. Tasks will fail without SSH access. "
                    "Please manually add an SSH key using: flow ssh-keys upload"
                )
                resolved_keys = []

        # Always merge with project-required keys
        try:
            resolved_keys = self.merge_with_required(resolved_keys)
        except Exception:
            pass

        # Deduplicate while preserving order
        if resolved_keys:
            seen: set[str] = set()
            deduped: list[str] = []
            for k in resolved_keys:
                if k and k not in seen:
                    seen.add(k)
                    deduped.append(k)
            resolved_keys = deduped

        return resolved_keys

    def _backfill_config(self, key_id: str) -> None:
        """Try to save generated key to config for future runs."""
        try:
            from flow.application.config.manager import ConfigManager

            cm = ConfigManager()
            payload = {
                "provider": "mithril",
                "mithril": {
                    "ssh_keys": [key_id],
                },
            }
            cm.save(payload)
        except Exception:
            # Never block launch on backfill issues
            pass
