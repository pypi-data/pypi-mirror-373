"""JSON Schema generation for Flow IR models."""

from typing import Any

from pydantic.json_schema import models_json_schema

from flow.domain.ir.spec import TaskSpec


def generate_task_schema() -> dict[str, Any]:
    """Generate JSON Schema for TaskSpec and related models.

    Returns:
        Complete JSON Schema including all referenced models.
    """
    _, schema = models_json_schema(
        [(TaskSpec, "validation")],
        title="Flow IR Schema v1",
        description="Flow Intermediate Representation for task specifications",
    )

    # Add schema metadata
    schema["$id"] = "https://flow.foundry.com/schemas/ir/v1/task.json"
    schema["$comment"] = "Canonical schema for Flow task specifications"

    return schema


def generate_compact_schema() -> dict[str, Any]:
    """Generate a compact schema with only TaskSpec.

    Returns:
        Simplified schema focused on TaskSpec.
    """
    return TaskSpec.model_json_schema()


def validate_ir_version(spec: dict[str, Any]) -> bool:
    """Check if a spec dict has a supported IR version.

    Args:
        spec: Task specification dictionary

    Returns:
        True if version is supported
    """
    version = spec.get("api_version", "")
    return version == "flow.ir/v1"
