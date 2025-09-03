"""Google Colab integration for Flow SDK.

Provides true Google Colab integration through local runtime connection protocol.
Uses Jupyter server with WebSocket extension for bi-directional communication.
"""

from __future__ import annotations

import logging
import re
import secrets
import socket
import time
from dataclasses import dataclass
from datetime import datetime, timezone

from flow.errors import FlowError, TaskNotFoundError, ValidationError
from flow.sdk.client import Flow, TaskConfig
from flow.sdk.models import Task, TaskStatus, VolumeSpec

logger = logging.getLogger(__name__)


@dataclass
class ColabConnection:
    """Connection details for Google Colab to connect to Flow GPU instance."""

    connection_url: str
    ssh_command: str
    instance_ip: str
    instance_type: str
    task_id: str
    session_id: str
    created_at: datetime
    jupyter_token: str
    remote_port: int = 8888

    def to_dict(self) -> dict[str, str]:
        return {
            "connection_url": self.connection_url,
            "ssh_command": self.ssh_command,
            "instance_ip": self.instance_ip,
            "instance_type": self.instance_type,
            "task_id": self.task_id,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "jupyter_token": self.jupyter_token,
            "remote_port": str(self.remote_port),
        }

    def connection_url_for_localport(self, local_port: int) -> str:
        return f"http://localhost:{local_port}/?token={self.jupyter_token}"

    def get_token(self) -> str:
        return self.jupyter_token


class GoogleColabIntegration:
    """Google Colab integration using local runtime connection."""

    JUPYTER_STARTUP_SCRIPT = """#!/bin/bash
set -euo pipefail

USE_WS="${FLOW_COLAB_USE_WS:-1}"

# Ensure notebook is installed (quiet to minimize output); prefer python3 -m pip
python3 -c "import notebook" 2>/dev/null || \
  python3 -m pip install -q --no-warn-script-location --disable-pip-version-check notebook==6.*

if [ "$USE_WS" = "1" ]; then
  python3 -m pip install -q --no-warn-script-location --disable-pip-version-check jupyter_http_over_ws==0.0.8 || true
  jupyter serverextension enable --py jupyter_http_over_ws || true
fi

# Token and config
export JUPYTER_TOKEN=$(python - <<'PY'
import secrets; print(secrets.token_urlsafe(32))
PY
)
mkdir -p ~/.jupyter
cat > ~/.jupyter/jupyter_notebook_config.py << EOF
c.NotebookApp.allow_origin = 'https://colab.research.google.com'
c.NotebookApp.token = '$JUPYTER_TOKEN'
c.NotebookApp.port_retries = 0
EOF

# Select a free localhost port
REMOTE_PORT=$(python - <<'PY'
import socket
s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1]); s.close()
PY
)
echo "$REMOTE_PORT" > ~/.jupyter/colab_port

# Start Jupyter bound to localhost; emit minimal readiness markers to logs
echo "Starting Jupyter for Colab (localhost bind)" >&2 || true
nohup jupyter notebook \
  --NotebookApp.allow_origin='https://colab.research.google.com' \
  --NotebookApp.token=$JUPYTER_TOKEN \
  --NotebookApp.port_retries=0 \
  --port=$REMOTE_PORT \
  --no-browser \
  --ip=127.0.0.1 \
  >/dev/null 2>&1 &

echo "JUPYTER_STARTED=true" || true
wait $!
"""

    def __init__(self, flow_client: Flow):
        self.flow = flow_client
        self._active_connections: dict[str, ColabConnection] = {}

    def _sanitize_volume_name(self, desired_name: str | None) -> str:
        name = (desired_name or "colab-ws").strip().lower()
        name = re.sub(r"[^a-z0-9-]+", "-", name)
        name = re.sub(r"-{2,}", "-", name).strip("-")
        if len(name) < 3:
            name = (name + "000")[:3]
        if len(name) > 64:
            name = name[:64].rstrip("-")
        if not re.match(r"^[a-z0-9]", name or ""):
            name = f"a{name}"
        if not re.search(r"[a-z0-9]$", name or ""):
            name = f"{name}0"
        if len(name) < 3:
            name = (name + "000")[:3]
        return name

    def connect(
        self,
        instance_type: str,
        hours: float | None = None,
        auto_tunnel: bool = False,
        name: str | None = None,
        attach_workspace: bool = True,
        workspace_size_gb: int = 50,
        workspace_name: str | None = None,
        *,
        quiet: bool = False,
    ) -> ColabConnection:
        if hours is not None and (hours < 0.1 or hours > 168):
            raise ValidationError("Hours must be between 0.1 and 168 (or 0/unset for no limit)")
        session_id = f"colab-{secrets.token_hex(6)}"
        config = TaskConfig(
            name=name or f"colab-{instance_type}",
            unique_name=False,
            instance_type=instance_type,
            command=["bash", "-c", self.JUPYTER_STARTUP_SCRIPT],
            upload_code=False,
            upload_strategy="none",
            image="",
            env={"FLOW_HEALTH_MONITORING": "false"},
            max_run_time_hours=hours,
            priority="high",
        )
        try:
            if not getattr(config, "region", None):
                instances = self.flow.find_instances({"instance_type": instance_type}, limit=20)
                if instances:

                    def _avail(i):
                        return i.available_quantity if i.available_quantity is not None else 0

                    instances.sort(key=lambda i: (-_avail(i), i.price_per_hour))
                    config.region = instances[0].region
        except Exception:
            pass
        if attach_workspace and workspace_size_gb > 0:
            vol_name = self._sanitize_volume_name(workspace_name or f"colab-ws-{session_id}")
            config.volumes = [
                VolumeSpec(name=vol_name, size_gb=workspace_size_gb, mount_path="/workspace")
            ]
        if not quiet:
            if hours is None:
                logger.info(f"Launching {instance_type}...")
            else:
                logger.info(f"Launching {instance_type} for {hours} hours...")
            logger.info("Provisioning can take several minutes.")
        task = self.flow.run(config)
        connection = self._wait_for_instance_ready(task, session_id, quiet=quiet)
        self._active_connections[session_id] = connection
        if auto_tunnel:
            self._establish_ssh_tunnel(connection)
        return connection

    def _wait_for_instance_ready(
        self,
        task: Task,
        session_id: str,
        timeout: int = 900,
        *,
        quiet: bool = False,
    ) -> ColabConnection:
        start_time = time.time()
        last_status = None
        jupyter_token = None
        instance_ip = None
        remote_port_val: int | None = None
        while time.time() - start_time < timeout:
            try:
                task = self.flow.get_task(task.task_id)
                status = task.status
            except Exception as e:
                logger.error(f"Failed to get task status: {e}")
                status = TaskStatus.FAILED
            if status != last_status:
                if status == TaskStatus.PENDING:
                    if last_status is None and not quiet:
                        logger.info("Instance allocation started...")
                elif status == TaskStatus.RUNNING:
                    if not quiet:
                        logger.info("Instance running; preparing Jupyter environment...")
                elif status == TaskStatus.FAILED:
                    if not quiet:
                        logger.error("Instance failed to start")
                    raise FlowError(f"Task {task.task_id} failed: {task.message}")
                last_status = status
            if status == TaskStatus.RUNNING:
                if not instance_ip and task.ssh_host:
                    instance_ip = task.ssh_host
                if not jupyter_token and instance_ip:
                    try:
                        remote_ops = self.flow.get_remote_operations()
                        cmd = "awk -F\"'\" '/^c.NotebookApp.token/ {print $2}' ~/.jupyter/jupyter_notebook_config.py"
                        token_output = remote_ops.execute_command(task.task_id, cmd)
                        candidate = (token_output or "").strip()
                        if candidate:
                            jupyter_token = candidate
                    except (AttributeError, NotImplementedError):
                        pass
                    except Exception:
                        pass
                if instance_ip and remote_port_val is None:
                    try:
                        remote_ops = self.flow.get_remote_operations()
                        port_output = remote_ops.execute_command(
                            task.task_id, "cat ~/.jupyter/colab_port || true"
                        )
                        port_str = (port_output or "").strip()
                        if port_str.isdigit():
                            remote_port_val = int(port_str)
                    except (AttributeError, NotImplementedError):
                        pass
                    except Exception:
                        pass
                jupyter_http_ok = False
                if instance_ip and (remote_port_val is not None) and jupyter_token:
                    try:
                        remote_ops = self.flow.get_remote_operations()
                        check_cmd = (
                            f"python3 - <<'PY'\n"
                            f"import urllib.request, urllib.error\n"
                            f'url = "http://127.0.0.1:{remote_port_val}/api/status?token={jupyter_token}"\n'
                            f"try:\n"
                            f"    urllib.request.urlopen(url, timeout=2)\n"
                            f'    print("OK")\n'
                            f"except Exception as e:\n"
                            f"    pass\n"
                            f"PY"
                        )
                        http_out = (
                            remote_ops.execute_command(task.task_id, check_cmd) or ""
                        ).strip()
                        if "OK" in http_out:
                            jupyter_http_ok = True
                    except (AttributeError, NotImplementedError):
                        pass
                    except Exception:
                        pass
                if (
                    instance_ip
                    and jupyter_token
                    and (remote_port_val is not None)
                    and jupyter_http_ok
                    and self._verify_ssh_access(instance_ip)
                ):
                    if not quiet:
                        logger.info("SSH access confirmed")
                    return ColabConnection(
                        connection_url=f"http://localhost:{remote_port_val}/?token={jupyter_token}",
                        ssh_command=f"ssh -N -o ExitOnForwardFailure=yes -o ServerAliveInterval=60 -o ServerAliveCountMax=2 -L 8888:localhost:{remote_port_val} {task.ssh_user}@{instance_ip}",
                        instance_ip=instance_ip,
                        instance_type=task.instance_type,
                        task_id=task.task_id,
                        session_id=session_id,
                        created_at=datetime.now(timezone.utc),
                        jupyter_token=jupyter_token,
                        remote_port=remote_port_val,
                    )
            time.sleep(5)
        raise FlowError(f"Instance not ready after {timeout // 60} minutes")

    def _verify_ssh_access(self, host: str, port: int = 22) -> bool:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def _establish_ssh_tunnel(self, connection: ColabConnection) -> None:
        logger.info(f"Auto-tunnel requested for {connection.task_id}")

    def disconnect(self, session_id: str) -> None:
        if session_id not in self._active_connections:
            raise ValueError(f"Session {session_id} not found")
        connection = self._active_connections[session_id]
        try:
            self.flow.stop(connection.task_id)
            logger.info(f"Disconnected session {session_id}")
        except Exception as e:
            logger.error(f"Failed to stop task {connection.task_id}: {e}")
            raise FlowError(f"Failed to disconnect session: {e!s}")
        finally:
            del self._active_connections[session_id]

    def list_sessions(self) -> list[dict[str, str]]:
        sessions = []
        for session_id, connection in self._active_connections.items():
            try:
                task = self.flow.get_task(connection.task_id)
                status = task.status.value
            except TaskNotFoundError:
                status = "terminated"
            except Exception:
                status = "unknown"
            sessions.append(
                {
                    "session_id": session_id,
                    "instance_type": connection.instance_type,
                    "status": status,
                    "created_at": connection.created_at.isoformat(),
                    "connection_url": connection.connection_url,
                    "ssh_command": connection.ssh_command,
                }
            )
        return sessions

    def get_startup_progress(self, task_id: str) -> str:
        try:
            logs = self.flow.logs(task_id, tail=50)
            if "JUPYTER_READY=true" in logs:
                return "Jupyter server ready!"
            elif re.search(r"Starting Jupyter server on port \d+", logs):
                return "Starting Jupyter server..."
            elif "Installing dependencies" in logs or "pip install" in logs:
                return "Installing dependencies..."
            elif "Starting Jupyter server for Google Colab" in logs:
                return "Initializing Jupyter environment..."
            else:
                return "Instance initializing..."
        except Exception:
            return "Waiting for instance..."
