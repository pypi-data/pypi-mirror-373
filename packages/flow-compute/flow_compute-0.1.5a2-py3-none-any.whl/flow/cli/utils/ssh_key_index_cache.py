"""SSH Key index cache for quick key references.

Stores ephemeral index-based key references (e.g., 1, :1) for the last shown
SSH key list. We store lightweight refs that can be resolved to a platform ID
or local path when used by commands.
"""

from __future__ import annotations

from pathlib import Path

from flow.cli.utils.index_cache_base import BaseIndexCache


class SSHKeyIndexCache(BaseIndexCache):
    """Manages ephemeral SSH key index mappings.

    Each entry stores a minimal reference dict, e.g.:
      {"ref": "sshkey_ABC", "type": "platform_id"}
      {"ref": "/Users/me/.ssh/id_ed25519", "type": "local"}
      {"ref": "_auto_", "type": "sentinel"}
    """

    CACHE_TTL_SECONDS = 300  # 5 minutes

    def __init__(self, cache_dir: Path | None = None):
        super().__init__("ssh_key_indices.json", cache_dir)

    def save_indices(self, refs: list[dict[str, str]]) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        if not refs:
            self.clear()
            return
        payload = {
            "indices": {str(i + 1): refs[i] for i in range(len(refs))},
            "count": len(refs),
            "context": self._current_context(),
        }
        self._ttl().save(payload)

    def resolve_index(self, index_str: str) -> tuple[dict | None, str | None]:
        # Accept ":N" or "N"
        raw = index_str[1:] if index_str.startswith(":") else index_str
        try:
            index = int(raw)
        except ValueError:
            return None, f"Invalid index format: {index_str}"
        if index < 1:
            return None, "Index must be positive"
        data = self._ttl().load()
        if not data:
            return None, "No recent SSH key list. Run 'flow ssh-keys get' first"
        ref = data.get("indices", {}).get(str(index))
        if not ref:
            max_index = data.get("count", 0)
            return None, f"Index {index} out of range (1-{max_index})"
        return dict(ref), None

    def _load_cache(self) -> dict | None:
        return super()._load_cache()

    def clear(self) -> None:
        super().clear()
