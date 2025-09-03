"""Project resolution component for the Mithril provider.

Resolves human-readable project names to IDs with a small in-memory cache and
clear errors when a project cannot be found.
"""

import logging

from flow.adapters.providers.builtin.mithril.api.client import MithrilApiClient
from flow.adapters.providers.builtin.mithril.api.types import ProjectModel as Project
from flow.errors import FlowError

logger = logging.getLogger(__name__)


class ProjectNotFoundError(FlowError):
    """Raised when a project cannot be resolved."""

    def __init__(self, project_name: str, available_projects: list[str]):
        self.project_name = project_name
        self.available_projects = available_projects

        msg = f"Project '{project_name}' not found."
        if available_projects:
            msg += "\n\nAvailable projects:\n"
            for project in available_projects[:5]:
                msg += f"  • {project}\n"
            if len(available_projects) > 5:
                msg += f"  ... and {len(available_projects) - 5} more"

        super().__init__(msg)


class ProjectResolver:
    """Resolves project names to IDs with caching and error handling."""

    def __init__(self, api_client: MithrilApiClient):
        """Initialize project resolver.

        Args:
            http_client: HTTP client for API requests
        """
        # Centralized API client only (no raw HTTP fallback)
        self._api: MithrilApiClient = api_client
        self._cache: dict[str, tuple[str, float]] = {}  # name -> (ID, ts)
        self._projects_cache: tuple[list[Project], float] | None = None
        self._ttl_seconds: float = 300.0  # 5 minutes

    def resolve(self, project_identifier: str) -> str:
        """Resolve project name or ID to project ID.

        Args:
            project_identifier: Project name or UUID

        Returns:
            Project ID (UUID)

        Raises:
            ProjectNotFoundError: If project cannot be resolved
        """
        if not project_identifier:
            raise FlowError("Project identifier is required")

        # If already a UUID, return as is
        if _is_uuid(project_identifier):
            logger.debug(f"Project identifier is already a UUID: {project_identifier}")
            return project_identifier

        # Check cache first (TTL)
        try:
            item = self._cache.get(project_identifier)
            if item is not None:
                pid, ts = item
                import time as _t

                if _t.time() - ts < self._ttl_seconds:
                    logger.debug(f"Resolved project '{project_identifier}' from cache")
                    return pid
                else:
                    self._cache.pop(project_identifier, None)
        except Exception:
            pass

        # Fetch and resolve
        project_id = self._resolve_from_api(project_identifier)
        if project_id:
            # Cache with TTL timestamp
            try:
                import time as _t

                self._cache[project_identifier] = (project_id, _t.time())
            except Exception:
                pass
            logger.info(f"Resolved project '{project_identifier}' to ID: {project_id}")
            return project_id

        # Not found - provide helpful error
        available_names = [p.name for p in self._get_all_projects()]
        raise ProjectNotFoundError(project_identifier, available_names)

    def list_projects(self) -> list[Project]:
        """List all available projects.

        Returns:
            List of Project objects
        """
        return self._get_all_projects()

    def resolve_project(self) -> str | None:
        """Auto-resolve project ID when no explicit project is configured.

        This method attempts to find a suitable default project for the user.
        If there's only one project, it returns that project's ID.
        If there are multiple projects, it returns None to avoid ambiguity.

        Returns:
            Project ID if a single project is available, None otherwise
        """
        try:
            projects = self._get_all_projects()

            if len(projects) == 1:
                # If there's only one project, use it as the default
                project_id = projects[0].fid
                logger.info(f"Auto-resolved to single project: {projects[0].name} ({project_id})")
                return project_id
            elif len(projects) == 0:
                logger.warning("No projects found for auto-resolution")
                return None
            else:
                # Multiple projects - cannot auto-resolve without ambiguity
                project_names = [p.name for p in projects[:5]]  # Show first 5
                logger.info(
                    f"Multiple projects found ({len(projects)} total), cannot auto-resolve. "
                    f"Available: {', '.join(project_names)}{'...' if len(projects) > 5 else ''}"
                )
                return None
        except Exception as e:
            logger.error(f"Failed to auto-resolve project: {e}")
            return None

    def invalidate_cache(self):
        """Clear the cache, forcing fresh lookups."""
        self._cache.clear()
        self._projects_cache = None
        logger.debug("Project resolver cache invalidated")

    def _resolve_from_api(self, project_name: str) -> str | None:
        """Resolve project name using API.

        Args:
            project_name: Project name to resolve

        Returns:
            Project ID if found, None otherwise
        """
        projects = self._get_all_projects()

        # Exact match first
        for project in projects:
            if project.name == project_name:
                return project.fid

        # Case-insensitive match
        name_lower = project_name.lower()
        for project in projects:
            if project.name.lower() == name_lower:
                logger.warning(
                    f"Found case-insensitive match: '{project.name}' for query '{project_name}'"
                )
                return project.fid

        return None

    def _get_all_projects(self) -> list[Project]:
        """Get all projects from API with caching.

        Handles API variations by accepting either 'fid' or 'id' for the
        project identifier and common variants for the creation timestamp.

        Returns:
            List of Project objects
        """
        if self._projects_cache is not None:
            try:
                projects, ts = self._projects_cache
                import time as _t

                if _t.time() - ts < self._ttl_seconds:
                    return projects
            except Exception:
                pass

        try:
            response = self._api.list_projects()

            # Normalize response to a list of dicts (support list or {data: [...]})
            if isinstance(response, list):
                projects_data = response
            elif isinstance(response, dict):
                projects_data = (
                    response.get("data") or response.get("projects") or response.get("items") or []
                )
            else:
                projects_data = []

            projects_list: list[Project] = []
            for p in projects_data:
                try:
                    # Accept both 'fid' and 'id' as the canonical identifier
                    fid = p.get("fid") or p.get("id") or p.get("project_id")
                    name = p.get("name") or p.get("display_name") or p.get("project_name")
                    created = (
                        p.get("created_at")
                        or p.get("createdAt")
                        or p.get("created")
                        or p.get("created_at_utc")
                        or p.get("createdAtUtc")
                    )
                    if not fid or not name:
                        continue
                    # Pydantic will parse common string datetime formats
                    if not created:
                        # Provide a stable fallback timestamp if missing
                        from datetime import datetime

                        created = datetime.utcnow().isoformat() + "Z"
                    projects_list.append(
                        Project(fid=fid, name=name, created_at=created)  # type: ignore[arg-type]
                    )
                except Exception:
                    # Skip malformed entries but keep going
                    continue

            logger.debug(f"Loaded {len(projects_list)} projects from API")
            try:
                import time as _t

                self._projects_cache = (projects_list, _t.time())
            except Exception:
                self._projects_cache = (projects_list, 0.0)
            return projects_list

        except Exception as e:
            logger.error(f"Failed to fetch projects: {e}")
            # Return empty list instead of failing completely
            return []


def _is_uuid(s: str) -> bool:
    """Best-effort UUID v4 format check."""
    try:
        import uuid

        _ = uuid.UUID(str(s))
        return True
    except Exception:
        return False
