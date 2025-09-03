"""Validation utilities for the Flow SDK.

Centralized validation helpers for consistent error handling across the SDK.
"""

import logging
import re
from typing import Any, TypeVar

from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError

from flow.errors import ProviderError, ValidationError

logger = logging.getLogger(__name__)

# Type variable for model validation
ModelT = TypeVar("ModelT", bound=BaseModel)


def validate_model(
    data: dict[str, Any],
    model_class: type[ModelT],
    context: str = "data",
) -> ModelT:
    """Validate data using a Pydantic model.

    This centralizes model validation to ensure consistent error handling.

    Args:
        data: Dictionary containing data to validate.
        model_class: Pydantic model class to use for validation.
        context: Context description for error messages.

    Returns:
        Validated model instance.

    Raises:
        ValidationError: If validation fails.
    """
    try:
        return model_class.model_validate(data)
    except PydanticValidationError as e:
        error_details = []
        for error in e.errors():
            loc = " -> ".join(map(str, error["loc"]))
            msg = f"{loc}: {error['msg']}"
            error_details.append(msg)
            logger.error("Validation error in %s: %s", context, msg)

        error_msg = (
            f"Failed to validate {context} using {model_class.__name__}: {'; '.join(error_details)}"
        )
        raise ValidationError(error_msg) from e


def validate_config(
    data: dict[str, Any],
    model_class: type[ModelT],
    config_path: str | None = None,
) -> ModelT:
    """Validate configuration data using a Pydantic model.

    This is a specialized version of validate_model for configuration data,
    which uses ProviderError instead of ValidationError.

    Args:
        data: Dictionary containing configuration data.
        model_class: Pydantic model class for validation.
        config_path: Optional path to the configuration file for error context.

    Returns:
        Validated configuration model instance.

    Raises:
        ProviderError: If validation fails.
    """
    try:
        return model_class.model_validate(data)
    except PydanticValidationError as e:
        error_details = []
        for error in e.errors():
            loc = " -> ".join(map(str, error["loc"]))
            msg = f"{loc}: {error['msg']}"
            error_details.append(msg)
            logger.error("Configuration validation error: %s", msg)

        context = f" in {config_path}" if config_path else ""
        error_msg = (
            f"Failed to validate configuration{context} using {model_class.__name__}: "
            f"{'; '.join(error_details)}"
        )
        raise ProviderError(error_msg) from e


def validate_email(email: str) -> bool:
    """Validate that a string is a properly formatted email address.

    Args:
        email: Email address to validate.

    Returns:
        True if valid, False otherwise.
    """
    # Simple regex pattern for basic email validation
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_required(value: Any, name: str) -> None:
    """Validate that a required value is not None or empty.

    Args:
        value: Value to validate.
        name: Name of the parameter for error messages.

    Raises:
        ValidationError: If the value is None or empty.
    """
    if value is None:
        raise ValidationError(f"Missing required parameter: {name}")

    if isinstance(value, str) and not value.strip():
        raise ValidationError(f"Required parameter '{name}' cannot be empty")


def validate_port_range(port: int | str) -> list[int]:
    """Validate and expand a port or port range.

    Args:
        port: Port number or range string (e.g., "8080-8090").

    Returns:
        List of port numbers.

    Raises:
        ValidationError: If the port specification is invalid.
    """
    if isinstance(port, int):
        if not (1 <= port <= 65535):
            raise ValidationError(f"Port number {port} is out of range (1-65535)")
        return [port]

    if isinstance(port, str):
        if "-" in port:
            try:
                start, end = port.split("-")
                start_port = int(start)
                end_port = int(end)

                if not (1 <= start_port <= end_port <= 65535):
                    raise ValidationError(
                        f"Port range {port} is invalid. Ports must be between 1 and 65535"
                    )

                return list(range(start_port, end_port + 1))
            except ValueError:
                raise ValidationError(f"Invalid port range format: {port}")
        else:
            try:
                port_num = int(port)
                if not (1 <= port_num <= 65535):
                    raise ValidationError(f"Port number {port} is out of range (1-65535)")
                return [port_num]
            except ValueError:
                raise ValidationError(f"Invalid port number: {port}")

    raise ValidationError(f"Unexpected port type: {type(port).__name__}")


# Additional high-level validators commonly needed across CLI/SDK
MAX_IDENTIFIER_LENGTH = 4096


def validate_task_identifier(identifier: str) -> tuple[bool, str | None]:
    """Validate task identifier for safety and length.

    Returns (ok, error_message).
    """
    if not identifier:
        return False, "Identifier cannot be empty"
    if len(identifier) > MAX_IDENTIFIER_LENGTH:
        return False, f"Identifier exceeds maximum length ({MAX_IDENTIFIER_LENGTH})"
    if "\x00" in identifier:
        return False, "Identifier contains null bytes"
    return True, None
