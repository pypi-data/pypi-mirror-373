from __future__ import annotations

from pydantic import BaseModel, Field


class User(BaseModel):
    """User identity information."""

    user_id: str = Field(..., description="Unique user identifier (e.g., 'user_kfV4CCaapLiqCNlv')")
    username: str = Field(..., description="Username for display")
    email: str = Field(..., description="User email address")
    # Future fields: full_name, organization, created_at
