"""GPU specifications for the Mithril provider.

Provider-specific GPU specs are maintained here rather than in the core.
"""

# GPU specifications - single source of truth for Mithril provider
GPU_SPECS = {
    # A100 variants
    "a100": {"memory_gb": 80, "display_name": "A100", "full_name": "NVIDIA A100"},
    "a100-40gb": {"memory_gb": 40, "display_name": "A100", "full_name": "NVIDIA A100 40GB"},
    "a100-80gb": {"memory_gb": 80, "display_name": "A100", "full_name": "NVIDIA A100 80GB"},
    # H100 variants
    "h100": {"memory_gb": 80, "display_name": "H100", "full_name": "NVIDIA H100"},
    "h100-80gb": {"memory_gb": 80, "display_name": "H100", "full_name": "NVIDIA H100 80GB"},
    "h100-94gb": {"memory_gb": 94, "display_name": "H100", "full_name": "NVIDIA H100 94GB"},
    "h200": {"memory_gb": 141, "display_name": "H200", "full_name": "NVIDIA H200"},
    # Professional/Datacenter GPUs
    "a40": {"memory_gb": 48, "display_name": "A40", "full_name": "NVIDIA A40"},
    "rtx-a6000": {"memory_gb": 48, "display_name": "RTX A6000", "full_name": "NVIDIA RTX A6000"},
    "rtx-6000-ada": {
        "memory_gb": 48,
        "display_name": "RTX 6000 Ada",
        "full_name": "NVIDIA RTX 6000 Ada",
    },
    "l40s": {"memory_gb": 48, "display_name": "L40S", "full_name": "NVIDIA L40S"},
    # Older datacenter GPUs
    "a10": {"memory_gb": 24, "display_name": "A10", "full_name": "NVIDIA A10"},
    "a10g": {"memory_gb": 24, "display_name": "A10G", "full_name": "NVIDIA A10G"},
    "v100": {"memory_gb": 16, "display_name": "V100", "full_name": "NVIDIA V100"},
    "v100-32gb": {"memory_gb": 32, "display_name": "V100", "full_name": "NVIDIA V100 32GB"},
    # Inference optimized
    "l4": {"memory_gb": 24, "display_name": "L4", "full_name": "NVIDIA L4"},
    "t4": {"memory_gb": 16, "display_name": "T4", "full_name": "NVIDIA T4"},
}


def get_default_gpu_memory(gpu_type: str) -> int:
    """Get default memory for a GPU type.

    Args:
        gpu_type: GPU type (e.g., "a100", "h100")

    Returns:
        Default memory in GB
    """
    import re

    gpu_type = gpu_type.lower()
    if gpu_type in GPU_SPECS:
        return GPU_SPECS[gpu_type]["memory_gb"]
    # Try to extract from name (e.g., "a100-80gb" -> 80)
    match = re.search(r"(\d+)gb", gpu_type)
    if match:
        return int(match.group(1))
    return 80  # Default fallback
