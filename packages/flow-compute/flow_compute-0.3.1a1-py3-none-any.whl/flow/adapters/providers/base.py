"""Base provider models and utilities.

This module defines base classes and capabilities that all providers
can use to describe their features and constraints.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class PricingModel(str, Enum):
    """Provider pricing models."""

    MARKET = "market"  # Dynamic market-based pricing
    FIXED = "fixed"  # Fixed pricing
    HYBRID = "hybrid"  # Combination of market and fixed


class ProviderCapabilities(BaseModel):
    """Capabilities and features supported by a provider.

    This model allows the core Flow SDK to understand what features
    each provider supports without hardcoding provider-specific logic.
    """

    # Compute capabilities
    supports_spot_instances: bool = Field(
        default=False, description="Whether provider supports spot/preemptible instances"
    )
    supports_on_demand: bool = Field(
        default=True, description="Whether provider supports on-demand instances"
    )
    supports_multi_node: bool = Field(
        default=False, description="Whether provider supports multi-node tasks"
    )

    # Storage capabilities
    supports_attached_storage: bool = Field(
        default=True, description="Whether provider supports attached block storage"
    )
    supports_shared_storage: bool = Field(
        default=False, description="Whether provider supports shared filesystem storage"
    )
    storage_types: list[str] = Field(
        default_factory=lambda: ["volume"],
        description="Supported storage types (volume, nfs, object, etc.)",
    )

    # Access and security
    requires_ssh_keys: bool = Field(
        default=True, description="Whether SSH keys are required for instance access"
    )
    supports_console_access: bool = Field(
        default=False, description="Whether provider supports web console access"
    )

    # Pricing and allocation
    pricing_model: PricingModel = Field(
        default=PricingModel.FIXED, description="How instances are priced"
    )
    supports_reservations: bool = Field(
        default=False, description="Whether provider supports advance reservations"
    )

    # Regional capabilities
    supported_regions: list[str] = Field(
        default_factory=list, description="List of supported regions"
    )
    cross_region_networking: bool = Field(
        default=False, description="Whether provider supports cross-region networking"
    )

    # Resource limits
    max_instances_per_task: int | None = Field(
        default=None, description="Maximum instances allowed per task"
    )
    max_storage_per_instance_gb: int | None = Field(
        default=None, description="Maximum storage per instance in GB"
    )

    # Advanced features
    supports_custom_images: bool = Field(
        default=True, description="Whether custom Docker images are supported"
    )
    supports_gpu_passthrough: bool = Field(
        default=True, description="Whether GPU passthrough is supported"
    )
    supports_live_migration: bool = Field(
        default=False, description="Whether live migration is supported"
    )


class ProviderInfo(BaseModel):
    """Information about a provider."""

    name: str = Field(..., description="Provider name")
    display_name: str = Field(..., description="Human-friendly name")
    description: str = Field(..., description="Provider description")
    website: str | None = Field(None, description="Provider website")
    documentation: str | None = Field(None, description="Documentation URL")
    capabilities: ProviderCapabilities = Field(
        default_factory=ProviderCapabilities, description="Provider capabilities"
    )


class EnvVarSpec(BaseModel):
    """Specification for an environment variable."""

    name: str = Field(..., description="Environment variable name")
    required: bool = Field(True, description="Whether this var is required")
    default: str | None = Field(None, description="Default value if not set")
    description: str = Field(..., description="Human-readable description")
    validation_pattern: str | None = Field(None, description="Regex pattern for validation")
    sensitive: bool = Field(False, description="Whether to mask in output")


class ConnectionMethod(BaseModel):
    """How to connect to running tasks."""

    type: str = Field(..., description="Connection type: ssh, web, kubectl, etc")
    command_template: str | None = Field(None, description="Command template with {placeholders}")
    supports_interactive: bool = Field(True, description="Whether interactive sessions work")
    supports_exec: bool = Field(True, description="Whether remote exec works")


class ConfigField(BaseModel):
    """A configuration field for the provider."""

    name: str
    type: str = Field("string", description="Field type: string, int, bool")
    required: bool = True
    default: Any | None = None
    description: str
    validation_pattern: str | None = None
    env_var: str | None = None


class CLIConfig(BaseModel):
    """Everything the CLI needs to know about a provider."""

    env_vars: list[EnvVarSpec] = Field(default_factory=list)
    mount_patterns: dict[str, str] = Field(
        default_factory=dict, description="Regex pattern -> mount path mappings"
    )
    connection_method: ConnectionMethod = Field(...)
    config_fields: list[ConfigField] = Field(default_factory=list)
    default_region: str | None = None


class ValidationRules(BaseModel):
    """Provider-specific validation rules."""

    api_key_pattern: str | None = None
    region_pattern: str | None = None
    instance_name_pattern: str | None = None
    project_name_pattern: str | None = None


class ProviderManifest(BaseModel):
    """Complete provider specification for CLI/SDK integration."""

    # Identity
    name: str = Field(..., description="Provider identifier")
    display_name: str = Field(..., description="Human-friendly name")

    # Capabilities (reuse existing)
    capabilities: ProviderCapabilities = Field(...)

    # CLI Integration
    cli_config: CLIConfig = Field(...)

    # Validation Rules
    validation: ValidationRules = Field(default_factory=ValidationRules)
