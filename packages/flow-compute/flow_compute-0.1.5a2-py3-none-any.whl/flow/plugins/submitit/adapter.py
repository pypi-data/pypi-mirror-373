"""Submitit frontend adapter for Flow SDK."""

import base64
import logging
from collections.abc import Callable
from typing import Any

import cloudpickle

from flow.adapters.frontends.base import BaseFrontendAdapter
from flow.adapters.frontends.registry import FrontendRegistry
from flow.sdk.models import TaskConfig

logger = logging.getLogger(__name__)


@FrontendRegistry.register("submitit")
class SubmititFrontendAdapter(BaseFrontendAdapter):
    """Submitit frontend adapter.

    Converts Submitit-style Python function submissions into Flow TaskConfig.
    """

    def __init__(self, name: str = "submitit"):
        super().__init__(name)
        self._job_counter = 1000

    async def parse_and_convert(self, input_data: Callable, *args, **options: Any) -> TaskConfig:
        """Parse Submitit function and convert to TaskConfig.

        Args:
            input_data: Python function to execute
            *args: Positional arguments for the function
            **options: Submitit parameters and keyword arguments

        Returns:
            TaskConfig for running the function
        """
        # Extract Submitit parameters from options
        submitit_params = self._extract_submitit_params(options)
        func_kwargs = options.copy()
        for key in submitit_params:
            func_kwargs.pop(key, None)

        # Serialize function and arguments
        serialized = self._serialize_function(input_data, args, func_kwargs)

        # Create startup script that deserializes and runs the function
        startup_script = self._create_runner_script(serialized)

        # Build TaskConfig
        task_config = self._build_task_config(
            func_name=getattr(input_data, "__name__", "submitit_function"),
            startup_script=startup_script,
            params=submitit_params,
        )

        logger.info(f"Converted Submitit function '{task_config.name}' to Flow task")

        return task_config

    def _extract_submitit_params(self, options: dict[str, Any]) -> dict[str, Any]:
        """Extract Submitit-specific parameters from options.

        Common Submitit parameters:
        - nodes: Number of nodes
        - gpus_per_node: GPUs per node
        - cpus_per_task: CPUs per task
        - mem_gb: Memory in GB
        - timeout_min: Timeout in minutes
        - slurm_partition: SLURM partition name
        - slurm_array_parallelism: Max array jobs
        """
        submitit_keys = {
            "nodes",
            "gpus_per_node",
            "cpus_per_task",
            "mem_gb",
            "timeout_min",
            "slurm_partition",
            "slurm_array_parallelism",
            "name",
            "comment",
            "exclude",
            "container_image",
        }

        params = {}
        for key in submitit_keys:
            if key in options:
                params[key] = options[key]

        return params

    def _serialize_function(
        self,
        func: Callable,
        args: tuple,
        kwargs: dict,
    ) -> str:
        """Serialize function and arguments using cloudpickle.

        Returns:
            Base64-encoded serialized data
        """
        data = {
            "func": func,
            "args": args,
            "kwargs": kwargs,
        }

        pickled = cloudpickle.dumps(data)
        encoded = base64.b64encode(pickled).decode("utf-8")

        return encoded

    def _create_runner_script(self, serialized_data: str) -> str:
        """Create Python script that deserializes and runs the function.

        Args:
            serialized_data: Base64-encoded pickled function data

        Returns:
            Python script content
        """
        script = f'''#!/usr/bin/env python3
"""Submitit function runner for Flow."""

import base64
import cloudpickle
import sys
import traceback
import os

# Serialized function data
SERIALIZED_DATA = """{serialized_data}"""

def main():
    """Deserialize and run the function."""
    try:
        # Decode and unpickle
        pickled = base64.b64decode(SERIALIZED_DATA)
        data = cloudpickle.loads(pickled)
        
        func = data["func"]
        args = data["args"]
        kwargs = data["kwargs"]
        
        # Set up Submitit-compatible environment
        os.environ["SUBMITIT_EXECUTOR"] = "flow"
        
        # Run the function
        print(f"Running function: {{func.__name__}}")
        result = func(*args, **kwargs)
        
        # Save result if needed (Submitit compatibility)
        if result is not None:
            import pickle
            with open("result.pkl", "wb") as f:
                pickle.dump(result, f)
            print(f"Result saved to result.pkl")
        
        print("Function completed successfully")
        
    except Exception as e:
        print(f"Error running function: {{e}}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
        return script

    def _build_task_config(
        self,
        func_name: str,
        startup_script: str,
        params: dict[str, Any],
    ) -> TaskConfig:
        """Build TaskConfig from Submitit parameters.

        Args:
            func_name: Name of the function
            startup_script: Python script to run
            params: Submitit parameters

        Returns:
            TaskConfig object
        """
        # Sanitize function name to match pattern ^[a-zA-Z0-9][a-zA-Z0-9-_]*$
        raw_name = params.get("name", func_name)

        # Handle special cases first
        if raw_name == "<lambda>":
            task_name = "lambda_function"
        else:
            # Remove invalid characters
            task_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in raw_name)
            # Ensure it starts with alphanumeric
            if not task_name or not task_name[0].isalnum():
                task_name = "func_" + task_name if task_name else "func"

        # Map GPUs per node to instance types
        gpu_instance_map = {
            1: "a100.80gb.sxm4.1x",
            2: "a100.80gb.sxm4.2x",
            4: "a100.80gb.sxm4.4x",
            8: "a100.80gb.sxm4.8x",
        }

        # Determine instance type from GPUs per node
        gpus_per_node = params.get("gpus_per_node", 1)
        instance_type = gpu_instance_map.get(gpus_per_node, "a100.80gb.sxm4.1x")

        # Infer GPU generation from partition name
        partition = params.get("slurm_partition", "")
        if "h100" in partition.lower():
            instance_type = instance_type.replace("a100", "h100").replace("sxm4", "sxm5")

        # Start with basic config - using script execution model
        config = TaskConfig(
            name=task_name,
            image=params.get("container_image", "python:3.9"),
            command=startup_script,  # Use script field
            num_instances=params.get("nodes", 1),
            instance_type=instance_type,
        )

        # Map GPU configuration
        if "gpus_per_node" in params:
            # num_instances is nodes, not GPUs per node
            # GPU count per node is determined by instance type
            if "slurm_partition" in params:
                gpu_type = self._infer_gpu_type(params["slurm_partition"])
                if gpu_type and gpu_type != "a100":
                    # Only update instance type if it's a different GPU generation
                    config.instance_type = config.instance_type.replace("a100", gpu_type)

        # Map timeout
        if "timeout_min" in params:
            # Convert minutes to hours
            hours = params["timeout_min"] / 60
            config.max_run_time_hours = hours
            config.max_price_per_hour = 100.0  # High limit to ensure it runs

        # Add Submitit environment variables
        config.env = {
            "SUBMITIT_EXECUTOR": "flow",
            "SUBMITIT_JOB_ID": "$FLOW_TASK_ID",
        }

        return config

    def _infer_gpu_type(self, partition: str) -> str | None:
        """Infer GPU type from partition name.

        Args:
            partition: SLURM partition name

        Returns:
            GPU type (lowercase) or None
        """
        partition_lower = partition.lower()

        if "a100" in partition_lower:
            return "a100"
        elif "v100" in partition_lower:
            return "v100"
        elif "h100" in partition_lower:
            return "h100"
        elif "t4" in partition_lower:
            return "t4"
        elif "gpu" in partition_lower:
            return "a100"  # Default GPU type

        return None

    def format_job_id(self, flow_job_id: str) -> str:
        """Format Flow job ID as Submitit job ID.

        Args:
            flow_job_id: Internal Flow job ID

        Returns:
            Submitit-compatible job ID
        """
        # Submitit expects numeric job IDs for SLURM compatibility
        job_id = self._job_counter
        self._job_counter += 1
        return str(job_id)

    def format_status(self, flow_status: str) -> str:
        """Format Flow status as Submitit status.

        Args:
            flow_status: Flow status

        Returns:
            Submitit status string
        """
        # Submitit status mapping (similar to SLURM)
        status_map = {
            "pending": "PENDING",
            "running": "RUNNING",
            "completed": "DONE",
            "failed": "FAILED",
            "cancelled": "CANCELLED",
            "timeout": "TIMEOUT",
            "preempted": "INTERRUPTED",
        }

        return status_map.get(flow_status.lower(), "UNKNOWN")
