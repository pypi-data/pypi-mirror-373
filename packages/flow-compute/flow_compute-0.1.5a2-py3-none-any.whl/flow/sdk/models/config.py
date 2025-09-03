from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class FlowConfig(BaseModel):
    """Flow SDK configuration settings.

    Immutable configuration for API authentication and default behaviors.
    Typically loaded from environment variables or config files.
    """

    model_config = ConfigDict(frozen=True)

    api_key: str = Field(..., description="Authentication key")
    project: str = Field(..., description="Project identifier")
    region: str = Field(default="us-central1-b", description="Default deployment region")
    api_url: str = Field(default="https://api.mithril.ai", description="API base URL")


class Project(BaseModel):
    """Project metadata."""

    name: str = Field(..., description="Project identifier")
    region: str = Field(..., description="Primary region")


class ValidationResult(BaseModel):
    """Configuration validation result."""

    is_valid: bool = Field(..., description="Validation status")
    projects: list[Project] = Field(default_factory=list, description="Accessible projects")
    error_message: str | None = Field(None, description="Validation error")
