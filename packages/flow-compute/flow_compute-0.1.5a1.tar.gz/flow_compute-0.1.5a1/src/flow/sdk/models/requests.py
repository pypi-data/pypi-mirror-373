from __future__ import annotations

from pydantic import BaseModel, Field

from flow.sdk.models.enums import TaskStatus
from flow.sdk.models.task import Task
from flow.sdk.models.task_config import TaskConfig


class SubmitTaskRequest(BaseModel):
    """Task submission request."""

    config: TaskConfig = Field(..., description="Task specification")
    wait: bool = Field(False, description="Block until complete")
    dry_run: bool = Field(False, description="Validation only")


class SubmitTaskResponse(BaseModel):
    """Task submission result."""

    task_id: str = Field(..., description="Assigned task ID")
    status: TaskStatus = Field(..., description="Initial state")
    message: str | None = Field(None, description="Status details")


class ListTasksRequest(BaseModel):
    """Task listing request."""

    status: TaskStatus | None = Field(None, description="Status filter")
    limit: int = Field(100, ge=1, le=1000, description="Page size")
    offset: int = Field(0, ge=0, description="Skip count")


class ListTasksResponse(BaseModel):
    """Task listing result."""

    tasks: list[Task] = Field(..., description="Task collection")
    total: int = Field(..., description="Total available")
    has_more: bool = Field(..., description="Pagination indicator")
