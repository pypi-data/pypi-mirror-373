from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path as _Path
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from flow.errors import FlowError
from flow.sdk.models.enums import TaskStatus
from flow.sdk.models.task_config import TaskConfig

if TYPE_CHECKING:
    from flow.sdk.models import Instance


class Task(BaseModel):
    """Task handle with lifecycle control (status, logs, wait, cancel, ssh)."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    task_id: str = Field(..., description="Task UUID")
    name: str = Field(..., description="Human-readable name")
    status: TaskStatus = Field(..., description="Execution state")
    config: TaskConfig | None = Field(None, description="Original configuration")

    # Timestamps
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    instance_created_at: datetime | None = Field(
        None, description="Creation time of current instance (for preempted/restarted tasks)"
    )

    # Resources
    instance_type: str
    num_instances: int
    region: str

    # Cost information
    cost_per_hour: str = Field(..., description="Hourly cost")
    total_cost: str | None = Field(None, description="Accumulated cost")

    # User information
    created_by: str | None = Field(None, description="Creator user ID")

    # Access information
    ssh_host: str | None = Field(None, description="SSH endpoint")
    ssh_port: int | None = Field(22, description="SSH port")
    ssh_user: str = Field("ubuntu", description="SSH user")
    shell_command: str | None = Field(None, description="Complete shell command")

    # Endpoints and runtime info
    endpoints: dict[str, str] = Field(default_factory=dict, description="Exposed service URLs")
    instances: list[str] = Field(default_factory=list, description="Instance identifiers")
    message: str | None = Field(None, description="Human-readable status")

    # Provider-specific metadata
    provider_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Provider-specific state and metadata (e.g., Mithril bid status, preemption reasons)",
    )

    # Provider reference (for method implementations)
    _provider: object | None = PrivateAttr(default=None)

    # Cached user information
    _user: Any | None = PrivateAttr(default=None)

    @property
    def is_running(self) -> bool:
        return self.status == TaskStatus.RUNNING

    @property
    def instance_status(self) -> str | None:
        return self.provider_metadata.get("instance_status")

    @property
    def instance_age_seconds(self) -> float | None:
        now = datetime.now(timezone.utc)
        if self.instance_created_at:
            return (now - self.instance_created_at).total_seconds()
        if self.created_at:
            return (now - self.created_at).total_seconds()
        return None

    @property
    def is_terminal(self) -> bool:
        return self.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]

    @property
    def has_ssh_access(self) -> bool:
        return bool(self.ssh_host and self.shell_command)

    @property
    def ssh_keys_configured(self) -> bool:
        return bool(self.config and self.config.ssh_keys) if self.config else False

    @property
    def host(self) -> str | None:
        return self.ssh_host

    @property
    def capabilities(self) -> dict[str, bool]:
        return {
            "ssh": self.has_ssh_access,
            "logs": self.has_ssh_access,
            "interactive": self.has_ssh_access,
        }

    def logs(
        self,
        follow: bool = False,
        tail: int = 100,
        stderr: bool = False,
        *,
        source: str | None = None,
        stream: str | None = None,
    ) -> str | Iterator[str]:
        if not self._provider:
            raise RuntimeError("Task not connected to provider")

        # Determine log type preference
        if follow:
            if source in {"startup", "host"}:
                log_type = source
            elif source in {"both", "all"}:
                log_type = "all"
            else:
                log_type = "stderr" if stderr else (stream or "stdout")
        else:
            if source in {"startup", "host"}:
                log_type = "host" if source == "host" else "startup"
            elif (stream or "").lower() in {"combined"} or (source or "").lower() in {
                "both",
                "all",
            }:
                log_type = "both"
            else:
                log_type = "stderr" if stderr else (stream or "stdout")

        # Prefer logs facet when available; fall back to provider methods
        try:
            from flow.adapters.providers.registry import ProviderRegistry  # local import

            facets = ProviderRegistry.facets_for_instance(self._provider)
            if facets and getattr(facets, "logs", None) is not None:
                if follow:
                    return facets.logs.stream_task_logs(self.task_id, log_type=log_type)
                return facets.logs.get_task_logs(self.task_id, tail=tail, log_type=log_type)
        except Exception:
            pass

        if follow:
            return self._provider.stream_task_logs(self.task_id, log_type=log_type)
        return self._provider.get_task_logs(self.task_id, tail=tail, log_type=log_type)

    def wait(self, timeout: int | None = None) -> None:
        import time

        start_time = time.time()
        while not self.is_terminal:
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Task {self.task_id} did not complete within {timeout} seconds")
            time.sleep(2)
            if self._provider:
                self.refresh()

    def refresh(self) -> None:
        if not self._provider:
            raise RuntimeError("Task not connected to provider")

        updated = self._provider.get_task(self.task_id)
        for field in self.model_fields:
            if hasattr(updated, field) and field != "_provider":
                setattr(self, field, getattr(updated, field))

    def stop(self) -> None:
        if not self._provider:
            raise RuntimeError("Task not connected to provider")
        self._provider.stop_task(self.task_id)
        self.status = TaskStatus.CANCELLED

    def cancel(self) -> None:
        self.stop()

    @property
    def public_ip(self) -> str | None:
        if self.ssh_host and self._is_ip_address(self.ssh_host):
            return self.ssh_host
        return None

    def _is_ip_address(self, host: str) -> bool:
        try:
            import ipaddress

            ipaddress.ip_address(host)
            return True
        except ValueError:
            return False

    def get_instances(self) -> list[Instance]:
        if not self._provider:
            raise FlowError("No provider available for instance resolution")
        return self._provider.get_task_instances(self.task_id)

    def get_user(self) -> Any | None:
        if not self.created_by:
            return None
        if self._user:
            return self._user
        if not self._provider:
            return None
        # Try multiple shapes for provider/context to fetch user info robustly
        try:
            prov = self._provider
            # 1) Provider facade exposing get_user()
            if hasattr(prov, "get_user") and callable(prov.get_user):
                self._user = prov.get_user(self.created_by)  # type: ignore[attr-defined]
                return self._user
            # 2) Context shape exposing users.get_user()
            users = getattr(prov, "users", None)
            if users is not None and hasattr(users, "get_user"):
                self._user = users.get_user(self.created_by)
                return self._user
            # 3) Provider/api client exposing _api_client.get_user()
            api_client = getattr(prov, "_api_client", None)
            if api_client is not None and hasattr(api_client, "get_user"):
                resp = api_client.get_user(self.created_by)
                self._user = resp.get("data", resp) if isinstance(resp, dict) else resp
                return self._user
            # 4) Raw HTTP adapter available: GET /v2/users/{id}
            http = getattr(prov, "http", None)
            if http is not None and hasattr(http, "request"):
                resp = http.request(method="GET", url=f"/v2/users/{self.created_by}")
                self._user = resp.get("data", resp) if isinstance(resp, dict) else resp
                return self._user
        except Exception:
            pass
        return None

    def result(self) -> Any:
        import json

        if not self.is_terminal:
            raise FlowError(
                f"Cannot retrieve result from task in {self.status} state",
                suggestions=[
                    "Wait for task to complete with task.wait()",
                    "Check task status with task.status",
                    "Results are only available after task completes",
                ],
            )

        if not self._provider:
            raise RuntimeError("Task not connected to provider")

        try:
            remote_ops = self._provider.get_remote_operations()
        except (AttributeError, NotImplementedError):
            remote_ops = None
        if not remote_ops:
            raise FlowError(
                "Provider does not support remote operations",
                suggestions=[
                    "This provider does not support result retrieval",
                    "Use a provider that implements remote operations",
                    "Store results in cloud storage or volumes instead",
                ],
            )

        try:
            from flow.utils.paths import RESULT_FILE

            result_data = remote_ops.retrieve_file(self.task_id, RESULT_FILE)
            result_json = json.loads(result_data.decode("utf-8"))
            success = result_json.get("success")
            has_error_field = "error" in result_json
            if success is False or has_error_field:
                error_field = result_json.get("error")
                if isinstance(error_field, dict):
                    err_type = error_field.get("type") or error_field.get("error_type") or "Unknown"
                    message = error_field.get("message") or error_field.get("error") or "No message"
                    tb = error_field.get("traceback")
                else:
                    message = str(error_field) if error_field is not None else "Unknown error"
                    err_type = result_json.get("error_type", "Unknown")
                    tb = result_json.get("traceback")
                suggestions = [
                    "Check the full traceback in task logs",
                    "Use task.logs() to see the complete error",
                ]
                if tb:
                    try:
                        tail = "\n".join(tb.strip().splitlines()[-5:])
                        suggestions.append(f"Traceback (last lines):\n{tail}")
                    except Exception:
                        pass
                raise FlowError(
                    f"Remote function failed: {err_type}: {message}", suggestions=suggestions
                )
            return result_json.get("result")
        except FileNotFoundError:
            raise FlowError(
                "Result file not found on remote instance",
                suggestions=[
                    "The function may not have completed successfully",
                    "Check task logs with task.logs() for errors",
                    "Ensure your function is wrapped with @app.function decorator",
                ],
            ) from None
        except json.JSONDecodeError as e:
            raise FlowError(
                "Failed to parse result JSON",
                suggestions=[
                    "The result file may be corrupted",
                    "Check task logs for errors during execution",
                    "Ensure the function returns JSON-serializable data",
                ],
            ) from e

    def shell(
        self,
        command: str | None = None,
        node: int | None = None,
        progress_context=None,
        record: bool = False,
    ) -> None:
        if node is not None and hasattr(self, "instances") and isinstance(self.instances, list):
            total = len(self.instances)
            if node < 0:
                node = None
            elif node >= total:
                raise ValueError(f"Invalid node index {node}; task has {total} nodes")

        if self._provider:
            remote_ops = self._provider.get_remote_operations()
            if not remote_ops:
                raise FlowError(
                    "Provider does not support shell access",
                    suggestions=[
                        "This provider does not support remote shell access",
                        "Use a provider that implements remote operations",
                        "Check provider documentation for supported features",
                    ],
                )
            remote_ops.open_shell(
                self.task_id,
                command=command,
                node=node,
                progress_context=progress_context,
                record=record,
            )
            return

        if not getattr(self, "ssh_host", None):
            from flow.errors import FlowError as _FlowError

            raise _FlowError(
                "Provider does not support shell access",
                suggestions=[
                    "This provider does not support remote shell access",
                    "Use a provider that implements remote operations",
                    "Check provider documentation for supported features",
                ],
            )

        from flow.sdk.ssh import SshStack

        ssh_cmd = SshStack.build_ssh_command(
            user=getattr(self, "ssh_user", "ubuntu"),
            host=self.ssh_host,
            port=getattr(self, "ssh_port", 22),
            key_path=(
                _Path(getattr(self, "ssh_key_path", ""))
                if getattr(self, "ssh_key_path", None)
                else None
            ),
            remote_command=command,
        )
        if command is None:
            import subprocess

            subprocess.run(ssh_cmd)
        else:
            import subprocess

            result = subprocess.run(ssh_cmd, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout, end="")
