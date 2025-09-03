"""Centralized name generation utilities for CLI commands.

Provides consistent unique name generation across Flow commands.
"""

import uuid


def generate_unique_name(prefix: str, base_name: str | None = None, add_unique: bool = True) -> str:
    """Generate a task name with optional unique suffix.

    Args:
        prefix: Default prefix if base_name not provided (e.g., "run", "dev", "grab")
        base_name: User-provided base name, if any
        add_unique: Whether to append unique suffix (controlled by --no-unique flag)

    Returns:
        Generated name with format:
        - No base_name + add_unique: "{prefix}-{uuid[:6]}"
        - No base_name + not add_unique: "{prefix}"
        - base_name + add_unique: "{base_name}-{uuid[:6]}"
        - base_name + not add_unique: "{base_name}"
    """
    if not base_name:
        # No user-provided name, use prefix
        if add_unique:
            return f"{prefix}-{str(uuid.uuid4())[:6]}"
        else:
            return prefix
    else:
        # User provided a name
        if add_unique:
            return f"{base_name}-{str(uuid.uuid4())[:6]}"
        else:
            return base_name
