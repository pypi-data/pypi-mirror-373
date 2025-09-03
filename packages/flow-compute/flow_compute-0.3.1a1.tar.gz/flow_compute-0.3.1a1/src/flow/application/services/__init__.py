"""Application services package."""

try:  # Re-export common services for convenient imports
    from flow.application.services.task_service import TaskService  # noqa: F401
except Exception:  # pragma: no cover
    pass
