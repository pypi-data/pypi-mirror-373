"""Local Provider Manifest.

This module defines the specification for the local development provider,
which runs tasks on the local machine using Docker.
"""

from flow.adapters.providers.base import (
    CLIConfig,
    ConfigField,
    ConnectionMethod,
    EnvVarSpec,
    PricingModel,
    ProviderCapabilities,
    ProviderManifest,
    ValidationRules,
)

LOCAL_MANIFEST = ProviderManifest(
    name="local",
    display_name="Local Development Provider",
    capabilities=ProviderCapabilities(
        supports_spot_instances=False,
        supports_on_demand=True,
        supports_multi_node=False,
        supports_attached_storage=True,
        requires_ssh_keys=False,
        pricing_model=PricingModel.FIXED,
        supported_regions=["local"],
        max_instances_per_task=1,
        supports_gpu_passthrough=True,  # If host has GPU
        supports_custom_images=True,
    ),
    cli_config=CLIConfig(
        env_vars=[
            EnvVarSpec(
                name="FLOW_LOCAL_DATA_DIR",
                required=False,
                default="~/.flow/local/data",
                description="Directory for local task data",
            ),
            EnvVarSpec(
                name="FLOW_LOCAL_DOCKER_NETWORK",
                required=False,
                default="flow-local",
                description="Docker network name for local tasks",
            ),
        ],
        mount_patterns={
            # Local paths mount directly
            r"^/.*": "{source}",  # Local absolute paths
            r"^\..*": "{source}",  # Relative paths
            # Data URLs mount to standard locations
            r"^file://.*": "/data",
            r"^http://.*": "/downloads",
            r"^https://.*": "/downloads",
        },
        connection_method=ConnectionMethod(
            type="docker",
            command_template="docker exec -it {container_id} /bin/bash",
            supports_interactive=True,
            supports_exec=True,
        ),
        config_fields=[
            ConfigField(
                name="data_dir",
                type="string",
                required=False,
                default="~/.flow/local/data",
                description="Local directory for task data",
                env_var="FLOW_LOCAL_DATA_DIR",
            ),
            ConfigField(
                name="docker_network",
                type="string",
                required=False,
                default="flow-local",
                description="Docker network for containers",
                env_var="FLOW_LOCAL_DOCKER_NETWORK",
            ),
        ],
        default_region="local",
    ),
    validation=ValidationRules(
        # Local provider doesn't need API keys or complex validation
        instance_name_pattern=r"^[a-zA-Z0-9][a-zA-Z0-9-_]*[a-zA-Z0-9]$",
    ),
)

# Export at module level
__all__ = ["LOCAL_MANIFEST"]
