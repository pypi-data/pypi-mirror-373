"""Secure, explicit secrets management for tasks (env and provider-backed).

Examples:
    Use provider-managed and env-provided secrets with a decorator:
        >>> from flow.sdk.client import FlowApp
        >>> from flow.sdk.secrets import Secret
        >>> app = FlowApp()
        >>> @app.function(
        ...     gpu="a100",
        ...     secrets=[
        ...         Secret.from_name("huggingface-token"),
        ...         Secret.from_env("OPENAI_API_KEY"),
        ...     ],
        ... )
        ... def train() -> str:
        ...     import os
        ...     assert os.environ.get("HUGGINGFACE_TOKEN")
        ...     assert os.environ.get("OPENAI_API_KEY")
        ...     return "ok"
        >>> train.remote()
"""

import os

from pydantic import BaseModel, Field, field_validator


class Secret(BaseModel):
    """Reference to a secret that is injected at runtime as environment vars."""

    name: str = Field(..., description="Secret identifier")
    env_vars: dict[str, str] = Field(
        default_factory=dict, description="Environment variable mappings"
    )
    source: str = Field("provider", description="Secret source")

    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        """Validate secret name characters and non-emptiness."""
        if not v or not v.strip():
            raise ValueError("Secret name cannot be empty")
        # Basic validation - alphanumeric, dash, underscore
        if not all(c.isalnum() or c in "-_" for c in v):
            raise ValueError(
                f"Secret name '{v}' contains invalid characters. "
                "Use only letters, numbers, dashes, and underscores."
            )
        return v

    @classmethod
    def from_name(cls, name: str, env_var: str | None = None) -> "Secret":
        """Reference a provider-managed secret.

        Args:
            name: Secret name in the provider's secret store.
            env_var: Optional environment variable name to expose. If not
                provided, a name is derived (uppercase, '-' to '_').

        Returns:
            Secret: A secret reference that will be injected at runtime.

        Examples:
            Derive env var from name:
                >>> Secret.from_name("huggingface-token")  # HUGGINGFACE_TOKEN

            Specify a custom env var name:
                >>> Secret.from_name("api-key", env_var="MY_API_KEY")
        """
        if env_var is None:
            # Default: convert to uppercase, replace dashes
            # "huggingface-token" -> "HUGGINGFACE_TOKEN"
            env_var = name.upper().replace("-", "_")

        return cls(
            name=name,
            env_vars={env_var: "*"},  # "*" means use entire secret value
            source="provider",
        )

    @classmethod
    def from_env(cls, env_var: str, required: bool = True) -> "Secret":
        """Reference a local env var (optionally enforce presence).

        Args:
            env_var: The local environment variable to pass through.
            required: If True, raise if the variable is not set.

        Returns:
            Secret: A secret reference that passes the env var through.
        """
        if required and env_var not in os.environ:
            raise ValueError(
                f"Environment variable '{env_var}' not set. Either set it or use required=False."
            )

        return cls(
            name=f"env-{env_var.lower()}",
            env_vars={env_var: env_var},  # Pass through as-is
            source="env",
        )

    @classmethod
    def from_dict(cls, env_vars: dict[str, str], name: str | None = None) -> "Secret":
        """Create a secret mapping multiple env vars (custom source).

        Args:
            env_vars: Mapping of env var name to source key/value.
            name: Optional group name for this secret mapping.

        Returns:
            Secret: A configurable mapping reference.
        """
        if not name:
            name = "custom-secret"

        return cls(name=name, env_vars=env_vars, source="custom")

    def to_env_dict(self) -> dict[str, str]:
        """Return env var mappings to apply in the task configuration.

        Examples:
            Convert a provider secret to placeholder mappings:
                >>> Secret.from_name("huggingface-token").to_env_dict().keys()
                dict_keys(['HUGGINGFACE_TOKEN'])
        """
        result = {}

        if self.source == "env":
            # Pass through from local environment
            for env_var, local_var in self.env_vars.items():
                if local_var in os.environ:
                    result[env_var] = os.environ[local_var]
        elif self.source == "provider":
            # Provider will inject these at runtime
            # Use placeholder values for now
            for env_var in self.env_vars:
                result[env_var] = f"__SECRET_{self.name}_{env_var}__"
        else:
            # Custom dict - use as provided
            result.update(self.env_vars)

        return result


class SecretMount(BaseModel):
    """File-based secret mount (reserved for future use)."""

    secret_name: str
    mount_path: str
    file_name: str | None = None
    mode: str = "0600"  # Read-only by owner


def validate_secrets(secrets: list[Secret]) -> None:
    """Validate secrets and fail on env var conflicts."""
    env_vars = {}

    for secret in secrets:
        for env_var in secret.env_vars:
            if env_var in env_vars:
                raise ValueError(
                    f"Environment variable '{env_var}' is set by multiple secrets: "
                    f"'{env_vars[env_var]}' and '{secret.name}'. "
                    "Each environment variable can only be set by one secret."
                )
            env_vars[env_var] = secret.name
