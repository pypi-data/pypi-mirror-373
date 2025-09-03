"""Intermediate Representation (IR) for Flow tasks.

This is the canonical representation that all frontends compile to
and all providers accept. It represents the platform contract.
"""

from typing import Literal

from pydantic import BaseModel, Field


class ResourceSpec(BaseModel, frozen=True):
    """Hardware resource requirements."""

    gpus: int = Field(default=0, ge=0, description="Number of GPUs required")
    gpu_type: str | None = Field(default=None, description="GPU type (e.g., 'H100-80GB')")
    cpus: int = Field(default=4, ge=1, description="Number of CPUs required")
    memory_gb: int = Field(default=16, ge=1, description="Memory in GB")
    accelerator_hints: dict[str, str] = Field(
        default_factory=dict,
        description="Hints for accelerator configuration (MIG, NVLink, SXM/PCIe, compute capability)",
    )


class MountSpec(BaseModel, frozen=True):
    """Volume mount specification."""

    kind: Literal["s3", "local", "nfs", "juicefs", "persistent"] = Field(
        description="Type of mount"
    )
    source: str = Field(description="Source path or URI")
    target: str = Field(description="Target mount path in container")
    read_only: bool = Field(default=True, description="Whether mount is read-only")
    cache: dict[str, str] | None = Field(
        default=None, description="Cache configuration for remote mounts"
    )


class RunParams(BaseModel, frozen=True):
    """Runtime parameters for task execution."""

    env: dict[str, str] = Field(default_factory=dict, description="Environment variables")
    working_dir: str | None = Field(default=None, description="Working directory")
    retry: int = Field(default=0, ge=0, description="Number of retries on failure")
    preemptible_ok: bool = Field(default=False, description="Allow preemptible instances")
    time_limit_s: int | None = Field(default=None, ge=1, description="Time limit in seconds")
    image: str | None = Field(default=None, description="Container image to use")


class TaskSpec(BaseModel, frozen=True):
    """Complete task specification - the core IR model."""

    api_version: Literal["flow.ir/v1"] = Field(
        default="flow.ir/v1", description="IR schema version"
    )
    name: str = Field(description="Task name")
    command: list[str] = Field(description="Command to execute")
    resources: ResourceSpec = Field(description="Resource requirements")
    mounts: list[MountSpec] = Field(default_factory=list, description="Volume mounts")
    params: RunParams = Field(default_factory=RunParams, description="Runtime parameters")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "api_version": "flow.ir/v1",
                    "name": "training-job",
                    "command": ["python", "train.py"],
                    "resources": {"gpus": 8, "gpu_type": "H100-80GB", "cpus": 32, "memory_gb": 256},
                    "mounts": [
                        {
                            "kind": "s3",
                            "source": "s3://mybucket/data",
                            "target": "/data",
                            "read_only": True,
                        }
                    ],
                    "params": {"env": {"BATCH_SIZE": "256"}, "retry": 2, "time_limit_s": 3600},
                }
            ]
        }
    }
