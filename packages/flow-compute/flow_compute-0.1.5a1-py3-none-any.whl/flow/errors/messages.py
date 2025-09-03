"""Centralized error messages for Flow SDK.

This module contains all error message templates and constants used throughout
the Flow SDK to ensure consistency and maintainability.
"""

from flow import DEFAULT_PROVISION_MINUTES as EXPECTED_PROVISION_MINUTES

# Task-related error messages
TASK_NOT_FOUND = "Task {task_id} not found"
TASK_ALREADY_EXISTS = "Task {task_id} already exists"
TASK_INVALID_STATUS = "Invalid task status: {status}"
TASK_PENDING_LOGS = "Task {task_id} is pending. Logs will be available once the task starts running.\nUse 'flow logs {task_id} -f' to wait for logs."
TASK_NO_SSH_ACCESS = "No SSH access for task {task_id}"
TASK_INSTANCE_NOT_ACCESSIBLE = f"""Instance is not accessible via SSH.

Possible reasons:
1. Instance is still starting (Mithril instances can take up to {EXPECTED_PROVISION_MINUTES} minutes)
2. Task was created without SSH keys (use --ssh flag when running)
3. Network connectivity issues

Try again in a few moments or check task status with 'flow status {{task_id}}'"""

# Instance type error messages
INVALID_INSTANCE_TYPE = "Invalid instance type: {instance_type}"
UNKNOWN_INSTANCE_TYPE = "Unknown instance type '{instance_type}'"
INSTANCE_TYPE_SUGGESTION = "Unknown instance type '{instance_type}'. Did you mean '{suggestion}'?"
INSTANCE_TYPE_NOT_AVAILABLE = (
    "Instance type '{instance_type}' is not available in region '{region}'"
)

# Configuration error messages
CONFIG_FILE_NOT_FOUND = "Configuration file not found: {path}"
CONFIG_INVALID_FORMAT = "Invalid configuration format: {error}"
CONFIG_MISSING_REQUIRED = "Missing required configuration: {field}"
CONFIG_VALIDATION_ERROR = "Configuration validation error: {error}"

# Provider error messages
PROVIDER_NOT_FOUND = "Provider '{provider}' not found"
PROVIDER_NOT_CONFIGURED = "Provider '{provider}' is not configured"
PROVIDER_INITIALIZATION_ERROR = "Failed to initialize provider '{provider}': {error}"
PROVIDER_API_ERROR = "Provider API error: {error}"

# SSH error messages
SSH_CONNECTION_REFUSED = "SSH connection refused: {error}"
SSH_CONNECTION_TIMEOUT = "SSH connection timed out: {error}"
SSH_KEY_NOT_FOUND = "SSH key not found: {path}"
SSH_KEY_INVALID_PERMISSIONS = "SSH key has invalid permissions: {path}"
SSH_KEY_GENERATION_FAILED = "Failed to generate SSH key: {error}"

# Volume error messages
VOLUME_NOT_FOUND = "Volume {volume_id} not found"
VOLUME_ALREADY_EXISTS = "Volume {volume_id} already exists"
VOLUME_MOUNT_FAILED = "Failed to mount volume {volume_id}: {error}"
VOLUME_INVALID_PATH = "Invalid volume path: {path}"

# Docker error messages
DOCKER_NOT_INSTALLED = "Docker is not installed or not accessible"
DOCKER_DAEMON_NOT_RUNNING = "Docker daemon is not running"
DOCKER_IMAGE_NOT_FOUND = "Docker image not found: {image}"
DOCKER_PULL_FAILED = "Failed to pull Docker image '{image}': {error}"
DOCKER_RUN_FAILED = "Failed to run Docker container: {error}"

# Script error messages
SCRIPT_TOO_LARGE = "Startup script exceeds maximum size limit of {max_size}KB"
SCRIPT_INVALID_COMMAND = "Invalid command: {command}"
SCRIPT_COMPRESSION_FAILED = "Failed to compress script: {error}"
SCRIPT_VALIDATION_FAILED = "Script validation failed: {errors}"

# Authentication error messages
AUTH_TOKEN_MISSING = "Authentication token is missing"
AUTH_TOKEN_INVALID = "Authentication token is invalid"
AUTH_TOKEN_EXPIRED = "Authentication token has expired"
AUTH_INSUFFICIENT_PERMISSIONS = "Insufficient permissions for operation: {operation}"

# Network error messages
NETWORK_CONNECTION_ERROR = "Network connection error: {error}"
NETWORK_TIMEOUT = "Network request timed out"
NETWORK_DNS_RESOLUTION_FAILED = "DNS resolution failed for: {host}"
NETWORK_SSL_ERROR = "SSL/TLS error: {error}"

# File operation error messages
FILE_NOT_FOUND = "File not found: {path}"
FILE_ACCESS_DENIED = "Access denied: {path}"
FILE_ALREADY_EXISTS = "File already exists: {path}"
FILE_OPERATION_FAILED = "File operation failed: {error}"

# Environment variable error messages
ENV_VAR_TOO_MANY = "Too many environment variables: {count} (max: {max_count})"
ENV_VAR_NAME_TOO_LONG = (
    "Environment variable name too long: {name} ({length} chars, max: {max_length})"
)
ENV_VAR_VALUE_TOO_LONG = (
    "Environment variable value too long for {name} ({length} chars, max: {max_length})"
)
ENV_VAR_INVALID_NAME = "Invalid environment variable name: {name}. Must match pattern: {pattern}"

# Command error messages
COMMAND_TOO_LONG = "Command exceeds maximum length of {max_length} characters"
COMMAND_INVALID_FORMAT = "Invalid command format: {command}"
COMMAND_EXECUTION_FAILED = "Command execution failed: {error}"

# Resource limit error messages
QUOTA_EXCEEDED = "Quota exceeded for {resource}: {current}/{limit}"
RATE_LIMIT_EXCEEDED = "Rate limit exceeded. Please try again in {retry_after} seconds"
RESOURCE_EXHAUSTED = "Resource exhausted: {resource}"

# Validation error messages
VALIDATION_FAILED = "Validation failed: {errors}"
INVALID_INPUT = "Invalid input: {input}"
MISSING_REQUIRED_FIELD = "Missing required field: {field}"
INVALID_FIELD_VALUE = "Invalid value for field '{field}': {value}"

# API error messages
API_REQUEST_FAILED = "API request failed: {error}"
API_RESPONSE_INVALID = "Invalid API response: {error}"
API_ENDPOINT_NOT_FOUND = "API endpoint not found: {endpoint}"
API_METHOD_NOT_ALLOWED = "Method not allowed: {method} {endpoint}"

# General error messages
OPERATION_FAILED = "Operation failed: {error}"
UNEXPECTED_ERROR = "An unexpected error occurred: {error}"
NOT_IMPLEMENTED = "Operation not implemented: {operation}"
DEPRECATED_FEATURE = "Feature '{feature}' is deprecated. Use '{alternative}' instead"

# Success messages (for consistency)
TASK_CREATED = "Task '{task_id}' created successfully"
TASK_CANCELLED = "Task '{task_id}' cancelled successfully"
VOLUME_CREATED = "Volume '{volume_id}' created successfully"
VOLUME_DELETED = "Volume '{volume_id}' deleted successfully"
CONFIG_SAVED = "Configuration saved successfully"

# Helper functions for formatting messages


def format_error(template: str, **kwargs) -> str:
    """Format an error message template with provided values.

    Args:
        template: Message template with {placeholders}
        **kwargs: Values to substitute in the template

    Returns:
        Formatted error message
    """
    try:
        return template.format(**kwargs)
    except KeyError as e:
        # If a placeholder is missing, return a more helpful error
        return f"{template} (missing value for: {e})"


def format_validation_errors(errors: list) -> str:
    """Format a list of validation errors into a readable message.

    Args:
        errors: List of error messages

    Returns:
        Formatted error message
    """
    if not errors:
        return "No validation errors"
    elif len(errors) == 1:
        return errors[0]
    else:
        return "Multiple validation errors:\n" + "\n".join(f"  - {e}" for e in errors)


def truncate_long_value(value: str, max_length: int = 100) -> str:
    """Truncate long values for display in error messages.

    Args:
        value: Value to potentially truncate
        max_length: Maximum length before truncation

    Returns:
        Truncated value with ellipsis if needed
    """
    if len(value) <= max_length:
        return value
    return value[: max_length - 3] + "..."
