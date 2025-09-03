"""Configuration for local testing provider."""

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class LocalInstanceMapping:
    """Maps cloud instance types to local resources."""

    cpu_cores: int
    memory_gb: float
    gpu_count: int = 0
    gpu_memory_gb: int = 0


@dataclass
class LocalTestConfig:
    """Configuration for local testing."""

    # Storage
    storage_dir: Path = field(default_factory=lambda: Path.home() / ".flow" / "local-test")
    max_storage_gb: int = 100
    clean_on_exit: bool = False

    # Execution
    use_docker: bool = True  # Default to Docker when available (with fallback)
    use_mithril_startup_scripts: bool = True  # Use production startup scripts when available
    docker_image: str = "ubuntu:24.04"
    gpu_docker_image: str = (
        "ubuntu:24.04"  # Use same image for now, GPU support requires NVIDIA runtime
    )

    # Resource limits
    max_concurrent_tasks: int = 10
    max_cpu_cores: int = 8
    max_memory_gb: int = 32

    # Instance type mappings
    instance_mappings: dict[str, LocalInstanceMapping] = field(default_factory=dict)

    # Timeouts
    task_startup_timeout: int = 30
    task_shutdown_timeout: int = 10

    @classmethod
    def default(cls) -> "LocalTestConfig":
        """Create default configuration."""
        config = cls()

        # Default instance mappings
        config.instance_mappings = {
            # CPU instances
            "cpu.small": LocalInstanceMapping(cpu_cores=2, memory_gb=4),
            "cpu.medium": LocalInstanceMapping(cpu_cores=4, memory_gb=8),
            "cpu.large": LocalInstanceMapping(cpu_cores=8, memory_gb=16),
            "cpu.xlarge": LocalInstanceMapping(cpu_cores=16, memory_gb=32),
            # GPU instances
            "gpu.t4": LocalInstanceMapping(
                cpu_cores=4, memory_gb=16, gpu_count=1, gpu_memory_gb=16
            ),
            "gpu.a10": LocalInstanceMapping(
                cpu_cores=8, memory_gb=32, gpu_count=1, gpu_memory_gb=24
            ),
            "gpu.a100": LocalInstanceMapping(
                cpu_cores=8, memory_gb=64, gpu_count=1, gpu_memory_gb=80
            ),
            "gpu.a100.2x": LocalInstanceMapping(
                cpu_cores=16, memory_gb=128, gpu_count=2, gpu_memory_gb=160
            ),
            # Aliases for common names
            "a100": LocalInstanceMapping(cpu_cores=8, memory_gb=64, gpu_count=1, gpu_memory_gb=80),
            "a100-80gb": LocalInstanceMapping(
                cpu_cores=8, memory_gb=64, gpu_count=1, gpu_memory_gb=80
            ),
        }

        return config

    @classmethod
    def from_env(cls) -> "LocalTestConfig":
        """Create configuration from environment variables."""
        config = cls.default()

        # Override from environment
        if os.environ.get("FLOW_LOCAL_STORAGE_DIR"):
            config.storage_dir = Path(os.environ["FLOW_LOCAL_STORAGE_DIR"])

        if os.environ.get("FLOW_LOCAL_USE_DOCKER"):
            config.use_docker = os.environ["FLOW_LOCAL_USE_DOCKER"].lower() == "true"

        if os.environ.get("FLOW_LOCAL_DOCKER_IMAGE"):
            config.docker_image = os.environ["FLOW_LOCAL_DOCKER_IMAGE"]

        return config

    def get_instance_mapping(self, instance_type: str) -> dict:
        """Get resource mapping for instance type.

        Args:
            instance_type: Instance type name

        Returns:
            Resource mapping dictionary
        """
        # Check exact match
        if instance_type in self.instance_mappings:
            mapping = self.instance_mappings[instance_type]
            return {
                "cpu_cores": mapping.cpu_cores,
                "memory_gb": mapping.memory_gb,
                "gpu_count": mapping.gpu_count,
                "gpu_memory_gb": mapping.gpu_memory_gb,
            }

        # Check for partial matches (e.g., "a100" matches "gpu.a100")
        for key, mapping in self.instance_mappings.items():
            if instance_type in key or key in instance_type:
                return {
                    "cpu_cores": mapping.cpu_cores,
                    "memory_gb": mapping.memory_gb,
                    "gpu_count": mapping.gpu_count,
                    "gpu_memory_gb": mapping.gpu_memory_gb,
                }

        # Default fallback
        return {
            "cpu_cores": 2,
            "memory_gb": 4,
            "gpu_count": 0,
            "gpu_memory_gb": 0,
        }
