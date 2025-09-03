"""Decorator-based remote execution.

Annotation-first API to run Python functions on remote GPUs while keeping user
code framework-free. Local calls run locally; `.remote()` runs on GPU.

Examples:
    Basic usage:
        >>> from flow.sdk.client import FlowApp
        >>> app = FlowApp()
        >>> @app.function(gpu="a100")
        ... def train(path: str) -> dict:
        ...     return {"ok": True}
        >>> train.remote("s3://bucket/data.csv")

    Advanced resources and secrets:
        >>> from flow.sdk.secrets import Secret
        >>> @app.function(
        ...     gpu="h100:8", cpu=32.0, memory=131072,
        ...     image="nvcr.io/nvidia/pytorch:23.10-py3",
        ...     volumes={"/models": "model-cache"},
        ...     environment={"NCCL_DEBUG": "INFO"},
        ...     secrets=[Secret.from_env("WANDB_API_KEY")],
        ... )
        ... def train_large(config_path: str) -> dict:
        ...     return {"status": "done"}
        >>> task = train_large.spawn("config.yaml")
        >>> task.wait()
"""

from __future__ import annotations

import functools
import inspect
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any, Generic, TypeVar

from typing_extensions import ParamSpec

from flow.sdk.client import Flow
from flow.sdk.models import Retries, Task, TaskConfig
from flow.sdk.secrets import Secret, validate_secrets

P = ParamSpec("P")
R = TypeVar("R")


class RemoteFunction(Generic[P, R]):
    """Wraps a Python function to support `.remote()` GPU execution.

    Local calls execute the function as-is; `.remote()` runs it remotely with
    an isolated environment and returns the JSON-serializable result.
    """

    def __init__(
        self,
        func: Callable[P, R],
        flow_client: Flow,
        gpu: str | None = None,
        cpu: float | tuple[float, float] | None = None,
        memory: int | tuple[int, int] | None = None,
        gpu_memory_gb: int | None = None,
        image: str | None = None,
        retries: int | Retries = 0,
        timeout: int | None = None,
        volumes: dict[str, Any] | None = None,
        environment: dict[str, str] | None = None,
        secrets: list[Secret] | None = None,
        max_result_size: int | None = 10 * 1024 * 1024,
        **kwargs,
    ):
        """Initialize a RemoteFunction.

        Args:
            func: The function to wrap.
            flow_client: Flow client for task submission.
            gpu: GPU specification (e.g., "a100", "h100:4").
            cpu: CPU cores as float or (request, limit) tuple.
            memory: Memory in MB as int or (request, limit) tuple.
            image: Docker image name. Defaults to python:3.11.
            retries: Retry configuration. Either an int for simple retries
                or a Retries object for advanced configuration.
            timeout: Maximum execution time in seconds.
            volumes: Volume mount specifications.
            environment: Environment variables for execution.
            secrets: List of Secret objects for secure credential injection.
            **kwargs: Additional TaskConfig parameters.
        """
        self.func = func
        self.flow_client = flow_client
        self.gpu = gpu
        self.cpu = cpu
        self.memory = memory
        self.image = image or "python:3.11"
        self.retries = retries
        self.timeout = timeout
        self.volumes = volumes or {}
        self.environment = environment or {}
        self.env = self.environment  # Backward compatibility
        self.secrets = secrets or []
        self.gpu_memory_gb = gpu_memory_gb
        self.max_result_size = max_result_size
        self.kwargs = kwargs

        # Validate secrets if provided
        if self.secrets:
            validate_secrets(self.secrets)

        # Copy function metadata
        functools.update_wrapper(self, func)
        # Preserve the original function signature for better introspection
        try:
            self.__signature__ = inspect.signature(func)  # type: ignore[attr-defined]
        except (ValueError, TypeError):
            # Some callables may not have retrievable signatures; ignore silently
            pass

        # Store function location
        self.module_name = func.__module__
        self.func_name = func.__name__

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Execute locally (no infrastructure involved)."""
        return self.func(*args, **kwargs)

    def remote(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Execute remotely on GPU and return the JSON-serializable result.

        Args:
            *args: Positional arguments for the wrapped function.
            **kwargs: Keyword arguments for the wrapped function.

        Returns:
            R: The function's return value.

        Raises:
            TypeError: If arguments cannot be JSON-serialized.
            Exception: Propagated remote error if the function fails.

        Examples:
            Simple remote call:
                >>> @app.function(gpu="a100")
                ... def add(x: int, y: int) -> int:
                ...     return x + y
                >>> add.remote(2, 3)

            Configure retries and timeout:
                >>> @app.function(gpu="a100", retries=3, timeout=600)
                ... def train(cfg_path: str) -> dict:
                ...     return {"ok": True}
                >>> train.remote("config.yaml")
        """
        # Prepare the execution script
        wrapper_script = self._create_wrapper_script(args, kwargs)

        # Build TaskConfig
        config = self._build_task_config(wrapper_script)

        # Submit task and wait for terminal state, then extract result
        task = self.flow_client.run(config, wait=True)
        # Use Task.result() to surface rich error information if the function failed
        return self._extract_result(task)

    def spawn(self, *args: P.args, **kwargs: P.kwargs) -> Task:
        """Submit for async execution and return the `Task` immediately.

        Args:
            *args: Positional arguments for the wrapped function.
            **kwargs: Keyword arguments for the wrapped function.

        Returns:
            Task: Handle that can be used to monitor execution.

        Examples:
            Launch N parallel tasks and stream their last logs:
                >>> tasks = [process.spawn(i) for i in range(8)]
                >>> for t in tasks:
                ...     t.wait()
                ...     print(t.logs(tail=10))
        """
        # Prepare the execution script
        wrapper_script = self._create_wrapper_script(args, kwargs)

        # Build TaskConfig
        config = self._build_task_config(wrapper_script)

        # Submit task without waiting
        task = self.flow_client.run(config, wait=False)
        return task

    def _create_wrapper_script(self, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
        """Build the remote wrapper script that runs the function and writes JSON."""
        # Serialize arguments with helpful errors
        try:
            args_json = json.dumps({"args": list(args), "kwargs": kwargs})
        except (TypeError, ValueError) as e:
            # Provide specific guidance for common ML types
            error_msg = self._get_serialization_error_message(args, kwargs, e)
            raise TypeError(error_msg) from e

        # Get the source file path
        module = inspect.getmodule(self.func)
        if module and hasattr(module, "__file__"):
            source_file = Path(module.__file__).name
        else:
            source_file = "function.py"

        wrapper = f"""
import json
import sys
import traceback
import inspect
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

from {self.module_name} import {self.func_name}

MAX_RESULT_SIZE = {int(self.max_result_size) if self.max_result_size else 0}

args_data = json.loads({args_json!r})
args = args_data["args"]
kwargs = args_data["kwargs"]

try:
    func = {self.func_name}
    if inspect.iscoroutinefunction(func):
        result = asyncio.run({self.func_name}(*args, **kwargs))
    else:
        result = {self.func_name}(*args, **kwargs)
    
    # Result must be JSON-serializable
    try:
        _serialized = json.dumps(result)
    except (TypeError, ValueError) as e:
        # Provide guidance if result is not JSON-serializable
        raise TypeError(
            f"Function returned non-JSON-serializable result: {{type(result).__name__}}\\n"
            f"\\n"
            f"Functions must return JSON-serializable values:\\n"
            f"  - Basic types: str, int, float, bool, None\\n"
            f"  - Collections: list, dict (with JSON-serializable values)\\n"
            f"  - File paths: Return paths to saved outputs\\n"
            f"\\n"
            f"For complex outputs, save to disk and return the path:\\n"
            f"  def {self.func_name}(...):\\n"
            f"      # Process data...\\n"
            f"      np.save('/outputs/result.npy', result_array)\\n"
            f"      return {{'result_path': '/outputs/result.npy', 'metrics': {{...}}}}\\n"
        ) from e
    
    # Enforce maximum result size if configured
    try:
        result_size = len(_serialized.encode('utf-8'))
        if MAX_RESULT_SIZE and result_size > MAX_RESULT_SIZE:
            raise ValueError(
                f"Function returned result too large: {{result_size}} bytes > {{MAX_RESULT_SIZE}} bytes. "
                f"Save large outputs to disk and return the path instead."
            )
    except Exception:
        pass
    
    with open("/tmp/flow_result.json", "w") as f:
        json.dump({{"success": True, "result": result}}, f)
        
except Exception as e:
    # Capture full traceback for better debugging
    tb = traceback.format_exc()
    error_obj = {{
        "type": type(e).__name__,
        "message": str(e),
        "traceback": tb,
        # Backward-compat aliases expected by some tests/tools
        "error_type": type(e).__name__,
        "error_message": str(e),
    }}
    
    with open("/tmp/flow_result.json", "w") as f:
        json.dump({{"success": False, "error": error_obj}}, f)
    
    # Still raise to ensure non-zero exit code
    raise
"""
        return wrapper

    def _get_serialization_error_message(
        self, args: tuple[Any, ...], kwargs: dict[str, Any], original_error: Exception
    ) -> str:
        """Return a clear, type-aware message for non-JSON-serializable inputs."""
        import re

        # Try to detect common non-serializable types
        all_values = list(args) + list(kwargs.values())

        # Import common ML packages only if available
        numpy_array_type = None
        pandas_dataframe_type = None
        torch_tensor_type = None
        sklearn_model_types = []

        try:  # pragma: no cover - optional dependency
            import numpy as np  # type: ignore

            numpy_array_type = np.ndarray
        except Exception:
            pass

        try:  # pragma: no cover - optional dependency
            import pandas as pd  # type: ignore

            pandas_dataframe_type = pd.DataFrame
        except Exception:
            pass

        try:  # pragma: no cover - optional dependency
            import torch  # type: ignore

            torch_tensor_type = torch.Tensor
        except Exception:
            pass

        try:  # pragma: no cover - optional dependency
            from sklearn.base import BaseEstimator  # type: ignore

            sklearn_model_types.append(BaseEstimator)
        except Exception:
            pass

        # Check each argument for known types
        for i, arg in enumerate(all_values):
            arg_name = (
                f"argument {i + 1}"
                if i < len(args)
                else f"kwarg '{list(kwargs.keys())[i - len(args)]}'"
            )

            # NumPy arrays
            if numpy_array_type and isinstance(arg, numpy_array_type):
                return (
                    f"Cannot serialize numpy array ({arg_name}) to JSON.\n"
                    f"Flow uses JSON serialization to ensure reproducibility across environments.\n"
                    f"\n"
                    f"Save the array to disk and pass the path instead:\n"
                    f"\n"
                    f"  # Save locally:\n"
                    f"  np.save('/tmp/data.npy', array)\n"
                    f"  result = {self.func_name}.remote('/tmp/data.npy')\n"
                    f"\n"
                    f"  # Or use a volume:\n"
                    f"  np.save('/outputs/data.npy', array)  # Saved to persistent volume\n"
                    f"  result = {self.func_name}.remote('volume://outputs/data.npy')\n"
                    f"\n"
                    f"  # In your function:\n"
                    f"  def {self.func_name}(data_path: str):\n"
                    f"      data = np.load(data_path)\n"
                    f"      # ... process data ...\n"
                )

            # Pandas DataFrames
            elif pandas_dataframe_type and isinstance(arg, pandas_dataframe_type):
                return (
                    f"Cannot serialize pandas DataFrame ({arg_name}) to JSON.\n"
                    f"Flow uses JSON serialization to ensure reproducibility across environments.\n"
                    f"\n"
                    f"Save the DataFrame to disk and pass the path instead:\n"
                    f"\n"
                    f"  # Parquet (recommended - preserves types, efficient):\n"
                    f"  df.to_parquet('/tmp/data.parquet')\n"
                    f"  result = {self.func_name}.remote('/tmp/data.parquet')\n"
                    f"\n"
                    f"  # CSV (simpler but loses type info):\n"
                    f"  df.to_csv('/tmp/data.csv', index=False)\n"
                    f"  result = {self.func_name}.remote('/tmp/data.csv')\n"
                    f"\n"
                    f"  # In your function:\n"
                    f"  def {self.func_name}(data_path: str):\n"
                    f"      df = pd.read_parquet(data_path)  # or pd.read_csv()\n"
                    f"      # ... process dataframe ...\n"
                )

            # PyTorch tensors/models
            elif torch_tensor_type and isinstance(arg, torch_tensor_type):
                return (
                    f"Cannot serialize PyTorch tensor ({arg_name}) to JSON.\n"
                    f"Flow uses JSON serialization to ensure reproducibility across environments.\n"
                    f"\n"
                    f"Save the tensor to disk and pass the path instead:\n"
                    f"\n"
                    f"  # Save tensor:\n"
                    f"  torch.save(tensor, '/tmp/tensor.pt')\n"
                    f"  result = {self.func_name}.remote('/tmp/tensor.pt')\n"
                    f"\n"
                    f"  # In your function:\n"
                    f"  def {self.func_name}(tensor_path: str):\n"
                    f"      tensor = torch.load(tensor_path)\n"
                    f"      # ... use tensor ...\n"
                )

            # PyTorch models (have state_dict method)
            elif hasattr(arg, "state_dict") and callable(arg.state_dict):
                return (
                    f"Cannot serialize PyTorch model ({arg_name}) to JSON.\n"
                    f"Flow uses JSON serialization to ensure reproducibility across environments.\n"
                    f"\n"
                    f"Save the model checkpoint and pass the path instead:\n"
                    f"\n"
                    f"  # Save model state:\n"
                    f"  torch.save(model.state_dict(), '/tmp/model.pt')\n"
                    f"  result = {self.func_name}.remote('/tmp/model.pt', 'config.json')\n"
                    f"\n"
                    f"  # Or save complete model:\n"
                    f"  torch.save(model, '/tmp/model_complete.pt')\n"
                    f"\n"
                    f"  # In your function:\n"
                    f"  def {self.func_name}(checkpoint_path: str, config_path: str):\n"
                    f"      # Load config and recreate model\n"
                    f"      config = json.load(open(config_path))\n"
                    f"      model = ModelClass(**config)\n"
                    f"      model.load_state_dict(torch.load(checkpoint_path))\n"
                    f"      # ... use model ...\n"
                )

            # Sklearn models
            elif sklearn_model_types and any(isinstance(arg, t) for t in sklearn_model_types):
                return (
                    f"Cannot serialize scikit-learn model ({arg_name}) to JSON.\n"
                    f"Flow uses JSON serialization to ensure reproducibility across environments.\n"
                    f"\n"
                    f"Save the model to disk and pass the path instead:\n"
                    f"\n"
                    f"  # Using joblib (recommended):\n"
                    f"  import joblib\n"
                    f"  joblib.dump(model, '/tmp/model.joblib')\n"
                    f"  result = {self.func_name}.remote('/tmp/model.joblib')\n"
                    f"\n"
                    f"  # In your function:\n"
                    f"  def {self.func_name}(model_path: str):\n"
                    f"      model = joblib.load(model_path)\n"
                    f"      # ... use model ...\n"
                )

        # Generic error for other types
        type_match = re.search(r"of type '?([^']+)'? is not JSON serializable", str(original_error))
        problem_type = type_match.group(1) if type_match else "unknown"

        return (
            f"Cannot serialize {problem_type} object to JSON.\n"
            f"Flow uses JSON serialization to ensure reproducibility across environments.\n"
            f"\n"
            f"Only JSON-serializable types are supported for function arguments:\n"
            f"  - Basic types: str, int, float, bool, None\n"
            f"  - Collections: list, dict (with JSON-serializable values)\n"
            f"  - Paths to data files: '/path/to/data.ext'\n"
            f"\n"
            f"For complex objects, save to disk and pass the path:\n"
            f"  1. Save your data locally or to a volume\n"
            f"  2. Pass the file path as a string argument\n"
            f"  3. Load the data inside your function\n"
            f"\n"
            f"Example patterns:\n"
            f"  # NumPy: np.save('/tmp/data.npy', array)\n"
            f"  # Pandas: df.to_parquet('/tmp/data.parquet')\n"
            f"  # PyTorch: torch.save(model.state_dict(), '/tmp/model.pt')\n"
            f"  # Pickle: pickle.dump(obj, open('/tmp/object.pkl', 'wb'))\n"
        )

    def _build_task_config(self, command: str) -> TaskConfig:
        """Translate decorator settings into a `TaskConfig`."""
        # Parse resource requirements
        instance_type = None
        min_gpu_memory_gb = None

        if self.gpu:
            instance_type = self.gpu
        elif self.gpu_memory_gb:
            min_gpu_memory_gb = int(self.gpu_memory_gb)

        # Merge environment variables from secrets
        env = self.environment.copy()
        for secret in self.secrets:
            secret_env = secret.to_env_dict()
            # Check for conflicts
            for key in secret_env:
                if key in env and env[key] != secret_env[key]:
                    raise ValueError(
                        f"Environment variable '{key}' is set both directly "
                        f"and by secret '{secret.name}'. Remove the direct "
                        f"setting to use the secret."
                    )
            env.update(secret_env)

        # Base TaskConfig fields
        config_dict = {
            "name": f"{self.func_name}-remote",
            "command": ["python", "-c", command],
            "image": self.image,
            "env": env,
            **self.kwargs,
        }

        if instance_type:
            config_dict["instance_type"] = instance_type
        if min_gpu_memory_gb:
            config_dict["min_gpu_memory_gb"] = min_gpu_memory_gb

        if self.volumes:
            volume_specs = []
            for mount_path, volume_ref in self.volumes.items():
                if isinstance(volume_ref, str):
                    volume_specs.append({"name": volume_ref, "mount_path": mount_path})
                elif isinstance(volume_ref, dict):
                    volume_spec = volume_ref.copy()
                    volume_spec["mount_path"] = mount_path
                    volume_specs.append(volume_spec)
            config_dict["volumes"] = volume_specs

        # Map timeout (seconds) to TaskConfig.max_run_time_hours if provided
        if self.timeout and self.timeout > 0:
            try:
                config_dict["max_run_time_hours"] = float(self.timeout) / 3600.0
            except Exception:
                # Ignore invalid values silently; validation will happen downstream if needed
                pass

        # Map retries (int -> Retries) if provided
        if self.retries:
            if isinstance(self.retries, int):
                config_dict["retries"] = Retries.fixed(retries=self.retries)
            else:
                config_dict["retries"] = self.retries

        return TaskConfig(**config_dict)

    def _extract_result(self, task: Task) -> Any:
        """Fetch and return the remote function result from the completed task."""
        # Use the Task.result() method to fetch results
        return task.result()


class FlowApp(Flow):
    """`Flow` with an `@function` decorator for remote execution."""

    def function(
        self,
        gpu: str | None = None,
        cpu: float | tuple[float, float] | None = None,
        memory: int | tuple[int, int] | None = None,
        gpu_memory_gb: int | None = None,
        image: str | None = None,
        retries: int | Retries = 0,
        timeout: int | None = None,
        volumes: dict[str, Any] | None = None,
        environment: dict[str, str] | None = None,
        env: dict[str, str] | None = None,  # Allow both env and environment
        secrets: list[Secret] | None = None,
        max_result_size: int | None = 10 * 1024 * 1024,
        **kwargs,
    ) -> Callable[[Callable[P, R]], RemoteFunction[P, R]]:
        """Decorator that returns a `RemoteFunction` configured with resources.

        Args:
            gpu: GPU spec, for example "a100" or "h100:8". Alternatively set
                `gpu_memory_gb` to request by memory.
            cpu: CPU cores as float or (request, limit).
            memory: Memory in MB as int or (request, limit).
            image: Container image (default: "python:3.11").
            retries: Retry policy (int or `Retries`).
            timeout: Maximum runtime in seconds.
            volumes: Mapping of mount_path to volume reference. Each value can be
                a volume name or a dict with `volume_id` and other fields.
            environment | env: Environment variables to set.
            secrets: Secrets to inject as environment variables.
            max_result_size: Maximum allowed size of serialized result (bytes).
            **kwargs: Additional `TaskConfig` fields to merge.

        Returns:
            Callable[[Callable[P, R]], RemoteFunction[P, R]]: A decorator that wraps the function.

        Examples:
            Minimal configuration:
                >>> @app.function(gpu="a100")
                ... def f(x: int) -> int:
                ...     return x * 2

            Full configuration with volumes and env:
                >>> @app.function(
                ...     gpu="h100:8",
                ...     cpu=32.0,
                ...     memory=131072,
                ...     image="nvcr.io/nvidia/pytorch:23.10-py3",
                ...     volumes={
                ...         "/data": {"name": "datasets", "size_gb": 500},
                ...         "/ckpts": "model-checkpoints",
                ...     },
                ...     environment={"NCCL_DEBUG": "INFO"},
                ... )
                ... def train(cfg: str) -> dict:
                ...     return {"status": "ok"}
        """

        def decorator(func: Callable[P, R]) -> RemoteFunction[P, R]:
            # Use env if provided, otherwise use environment
            actual_env = env if env is not None else environment
            return RemoteFunction(
                func=func,
                flow_client=self,
                gpu=gpu,
                cpu=cpu,
                memory=memory,
                gpu_memory_gb=gpu_memory_gb,
                image=image,
                retries=retries,
                timeout=timeout,
                volumes=volumes,
                environment=actual_env,
                secrets=secrets,
                max_result_size=max_result_size,
                **kwargs,
            )

        return decorator


# Create a default app instance for convenience
# Lazy initialization to avoid auth checks during import
import threading

_app = None
_app_lock = threading.Lock()


def _get_app() -> FlowApp:
    """Return the singleton `FlowApp` (thread-safe)."""
    global _app
    if _app is None:
        with _app_lock:
            # Double-check pattern
            if _app is None:
                _app = FlowApp()
    return _app


class _LazyApp:
    """Lazy proxy that instantiates `FlowApp` on first use."""

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the underlying `FlowApp`."""
        return getattr(_get_app(), name)

    def __call__(self) -> FlowApp:
        """Return the underlying `FlowApp` instance."""
        return _get_app()

    def __repr__(self) -> str:
        """Represent using the underlying `FlowApp`."""
        return repr(_get_app())


# Create singleton instances for module-level use
app = _LazyApp()


def function(*args, **kwargs):
    """Module-level helper: `function(...)` == `_get_app().function(...)`."""
    return _get_app().function(*args, **kwargs)
