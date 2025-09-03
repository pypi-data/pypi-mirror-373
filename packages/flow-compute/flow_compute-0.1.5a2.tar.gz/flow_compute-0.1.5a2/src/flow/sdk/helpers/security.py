"""Security utilities for Flow SDK.

Small helpers for path and command sanitization and basic format checks.
"""

import shlex
from pathlib import Path

from flow.errors import ValidationError


def sanitize_path(path: str) -> Path:
    """Prevent directory traversal attacks.

    Args:
        path: User-provided path

    Returns:
        Resolved absolute path

    Raises:
        ValidationError: If path contains traversal attempts
    """
    # Convert to Path and resolve to absolute
    resolved = Path(path).resolve()

    # Check for common traversal patterns
    if ".." in str(path):
        raise ValidationError(f"Path traversal detected in: {path}")

    return resolved


def sanitize_command(command: str) -> str:
    """Shell escape for safety.

    Args:
        command: Command to escape

    Returns:
        Shell-escaped command
    """
    return shlex.quote(command)


def check_ssh_key_permissions(key_path: Path) -> None:
    """Ensure SSH key has secure permissions.

    SSH keys should not be readable by group or others.

    Args:
        key_path: Path to SSH private key

    Raises:
        ValidationError: If permissions are insecure
    """
    if not key_path.exists():
        raise ValidationError(f"SSH key not found: {key_path}")

    # Get file permissions
    mode = key_path.stat().st_mode & 0o777

    # Check if group or others have any permissions
    if mode & 0o077:
        raise ValidationError(
            f"SSH key has insecure permissions: {oct(mode)}. Fix with: chmod 600 {key_path}"
        )


def validate_instance_id(instance_id: str) -> str:
    """Validate instance ID format.

    Args:
        instance_id: Instance ID to validate

    Returns:
        Validated instance ID

    Raises:
        ValidationError: If format is invalid
    """
    # Basic format validation for Mithril instance IDs
    import re

    if not re.match(r"^[a-zA-Z0-9\-_]+$", instance_id):
        raise ValidationError(f"Invalid instance ID format: {instance_id}")

    return instance_id


def validate_project_id(project_id: str) -> str:
    """Validate project ID format.

    Args:
        project_id: Project ID to validate

    Returns:
        Validated project ID

    Raises:
        ValidationError: If format is invalid
    """
    # Basic format validation
    import re

    if not re.match(r"^[a-zA-Z0-9\-_]+$", project_id):
        raise ValidationError(f"Invalid project ID format: {project_id}")

    return project_id
