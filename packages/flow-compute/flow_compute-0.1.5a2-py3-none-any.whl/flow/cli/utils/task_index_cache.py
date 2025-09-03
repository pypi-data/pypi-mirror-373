"""Task index cache for quick task references.

Provides ephemeral index-based task references (e.g., "1", "2"; legacy ":1", ":2") based on the
last shown task list. Also serves as the backing data for list/range selections
like "1,2-3,9" used by CLI commands via `selection.py` and
`selection_helpers.py`. Behavior is explicit and time-bounded to prevent stale
references.
"""

from pathlib import Path

from flow.cli.utils.index_cache_base import BaseIndexCache
from flow.sdk.models import Task


class TaskIndexCache(BaseIndexCache):
    """Manages ephemeral task index mappings.

    Stores a 1-based index -> task_id map for the last displayed task list,
    plus lightweight task details for fast UX. Used in two ways:

    - Single-index resolution via `resolve_index(":N")` (legacy input accepted; callers may pass bare "N")
    - Range/list selections (e.g., "1-3,5,7") by callers that parse the
      expression (see `selection.py`) and then map indices using
      `get_indices_map()`

    Indices expire after 5 minutes to prevent stale references.
    """

    CACHE_TTL_SECONDS = 300  # 5 minutes

    def __init__(self, cache_dir: Path | None = None):
        """Initialize cache with optional custom directory.

        Args:
            cache_dir: Directory for cache file (defaults to ~/.flow)
        """
        super().__init__("task_indices.json", cache_dir)

    def save_indices(self, tasks: list[Task]) -> None:
        """Save task indices from a displayed list.

        Args:
            tasks: Ordered list of tasks as displayed
        """
        # Create directory if needed
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # If there are no tasks, clear the cache to avoid stale mappings
        if not tasks:
            self.clear()
            return

        # Build index mapping (1-based for user friendliness)
        indices = {str(i + 1): getattr(task, "task_id", str(i + 1)) for i, task in enumerate(tasks)}

        # Cache full task details for instant access
        task_details = {}
        for task in tasks:
            tid = getattr(task, "task_id", None) or f"task-{id(task)}"
            try:
                name = getattr(task, "name", None)
                status = getattr(
                    getattr(task, "status", None), "value", str(getattr(task, "status", ""))
                )
                instance_type = getattr(task, "instance_type", None)
                ssh_host = getattr(task, "ssh_host", None)
                ssh_port = getattr(task, "ssh_port", None)
                ssh_user = getattr(task, "ssh_user", None)
                created_at = getattr(task, "created_at", None)
                started_at = getattr(task, "started_at", None)
                region = getattr(task, "region", None)
                cost_per_hour = getattr(task, "cost_per_hour", None)
                task_details[tid] = {
                    "task_id": tid,
                    "name": name,
                    "status": status,
                    "instance_type": instance_type,
                    "ssh_host": ssh_host,
                    "ssh_port": ssh_port,
                    "ssh_user": ssh_user,
                    "created_at": (
                        created_at.isoformat() if hasattr(created_at, "isoformat") else None
                    ),
                    "started_at": (
                        started_at.isoformat() if hasattr(started_at, "isoformat") else None
                    ),
                    "region": region,
                    "cost_per_hour": cost_per_hour,
                }
            except Exception:
                task_details[tid] = {"task_id": tid}

        payload = {
            "indices": indices,
            "task_details": task_details,
            "task_count": len(tasks),
            # Scope on-disk indices to current provider/project context when known
            "context": self._current_context(),
        }

        self._ttl().save(payload)

    def resolve_index(self, index_str: str) -> tuple[str | None, str | None]:
        """Resolve a single index reference to a task ID.

        Accepts legacy `:N` and also bare `N`. For lists/ranges (e.g., "1-3,5"),
        use the selection utilities (`selection.py` / `selection_helpers.py`) to
        parse the expression and then map via `get_indices_map()`.

        Args:
            index_str: Index string (e.g., ":1", ":2")

        Returns:
            Tuple of (task_id if found, error message if any)
        """
        # Parse index
        if index_str.startswith(":"):
            raw = index_str[1:]
        else:
            raw = index_str

        try:
            index = int(raw)
        except ValueError:
            return None, f"Invalid index format: {index_str}"

        if index < 1:
            return None, "Index must be positive"

        # Load cache
        cache_data = self._ttl().load()
        if not cache_data:
            return None, "No recent task list. Run 'flow status' first"

        # Look up index
        task_id = cache_data["indices"].get(str(index))
        if not task_id:
            max_index = cache_data["task_count"]
            return None, f"Index {index} out of range (1-{max_index})"

        return task_id, None

    def get_indices_map(self) -> dict[str, str]:
        """Return the last saved indices mapping if cache is fresh.

        Used by selection helpers to expand list/range expressions.

        Returns:
            Mapping of display index (str) -> task_id, or empty dict if expired/unavailable.
        """
        cache_data = self._ttl().load()
        if not cache_data:
            return {}
        return dict(cache_data.get("indices", {}))

    def _load_cache(self) -> dict | None:
        return super()._load_cache()

    def get_cached_task(self, task_id: str) -> dict | None:
        """Get cached task details if available.

        Args:
            task_id: Task ID to look up

        Returns:
            Task details dict or None if not cached/expired
        """
        cache_data = self._ttl().load()
        if not cache_data:
            return None
        return cache_data.get("task_details", {}).get(task_id)

    def clear(self) -> None:
        super().clear()
