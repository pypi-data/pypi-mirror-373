from __future__ import annotations

import logging
import os
import subprocess
import time
from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING

from flow.adapters.providers.builtin.mithril.core.constants import (
    EXPECTED_PROVISION_MINUTES,
    SSH_READY_WAIT_SECONDS,
)
from flow.adapters.providers.builtin.mithril.remote.connection_manager import (
    SshConnectionManager,
)
from flow.adapters.providers.builtin.mithril.remote.errors import (
    RemoteExecutionError,
    SshConnectionError,
    make_error,
)
from flow.adapters.providers.builtin.mithril.remote.recording import build_recording_command
from flow.adapters.providers.builtin.mithril.remote.utils import new_request_id
from flow.adapters.transport.ssh.ssh_stack import SshStack
from flow.protocols.remote_operations import RemoteOperationsProtocol as IRemoteOperations

if TYPE_CHECKING:
    from flow.adapters.providers.builtin.mithril.provider import MithrilProvider


logger = logging.getLogger(__name__)


class MithrilRemoteOperations(IRemoteOperations):
    """Mithril remote operations via SSH (refactored)."""

    def __init__(self, provider: MithrilProvider):
        self.provider = provider
        self.connection_manager = SshConnectionManager(provider)

    # ------------------------------------------------------------------
    # Command execution
    # ------------------------------------------------------------------
    def execute_command(self, task_id: str, command: str, timeout: int | None = None) -> str:
        request_id = new_request_id("ssh-exec")

        try:
            # Use a shorter readiness window for command exec to reduce latency
            conn = self.connection_manager.establish_connection(
                task_id=task_id,
                request_id=request_id,
                timeout_seconds=(timeout or SSH_READY_WAIT_SECONDS),
                node=None,
                quick_ready=True,
            )
        except SshConnectionError as e:
            raise e
        except Exception as e:
            raise make_error(f"SSH setup failed: {e!s}", request_id)

        ssh_cmd = SshStack.build_ssh_command(
            user=conn.user,
            host=conn.host,
            port=conn.port,
            key_path=Path(conn.key_path),
            remote_command=command,
        )

        try:
            result = subprocess.run(
                ssh_cmd,
                capture_output=True,
                text=True,
                timeout=timeout if timeout else None,
            )
            if result.returncode != 0:
                stderr = (result.stderr or "").lower()
                if "permission denied" in stderr or "publickey" in stderr:
                    suggestions = [
                        "Verify the task was launched with your SSH key",
                        "Run: flow ssh-keys list (confirm your key on the project)",
                        "Optionally override: MITHRIL_SSH_KEY=/path/to/private/key flow <cmd>",
                    ]
                    raise make_error(
                        (
                            "SSH authentication failed (Permission denied).\n"
                            f"Key used: {Path(conn.key_path).expanduser()!s}"
                        ),
                        request_id,
                        suggestions=suggestions,
                    )
                if "connection closed" in stderr or "connection reset" in stderr:
                    raise make_error(
                        "SSH connection was closed. The instance may still be starting up. "
                        "Please wait a moment and try again.",
                        request_id,
                    )
                raise make_error(f"Command failed: {result.stderr}", request_id)
            # Mark a recent success so subsequent quick ops (preflights) skip heavy waits
            try:
                self.connection_manager.mark_success(getattr(conn, "cache_key", None))
            except Exception:
                pass
            return result.stdout
        except subprocess.TimeoutExpired as e:
            raise TimeoutError(f"Command timed out after {timeout} seconds") from e
        except RemoteExecutionError:
            raise
        except Exception as e:
            raise make_error(f"SSH execution failed: {e!s}", request_id)

    # ------------------------------------------------------------------
    # Streaming
    # ------------------------------------------------------------------
    def stream_command(self, task_id: str, command: str) -> Iterator[str]:
        request_id = new_request_id("ssh-stream")

        try:
            conn = self.connection_manager.establish_connection(
                task_id=task_id,
                request_id=request_id,
                timeout_seconds=SSH_READY_WAIT_SECONDS,
            )
        except SshConnectionError as e:
            raise e
        except Exception as e:
            raise make_error(f"SSH setup failed: {e!s}", request_id)

        ssh_cmd = SshStack.build_ssh_command(
            user=conn.user,
            host=conn.host,
            port=conn.port,
            key_path=Path(conn.key_path),
            remote_command=command,
        )

        process = None
        try:
            process = subprocess.Popen(
                ssh_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            if process.stdout is not None:
                for line in iter(process.stdout.readline, ""):
                    yield line.rstrip("\n")

            process.wait()

            if process.returncode != 0:
                if process.returncode == 255:
                    raise make_error("SSH connection error (exit code 255)", request_id)
        except GeneratorExit:
            if process and process.poll() is None:
                process.terminate()
        except RemoteExecutionError:
            raise
        except Exception as e:
            raise make_error(f"SSH streaming failed unexpectedly: {e!s}", request_id)
        finally:
            if process and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()

    # ------------------------------------------------------------------
    # Interactive shell
    # ------------------------------------------------------------------
    def open_shell(
        self,
        task_id: str,
        command: str | None = None,
        node: int | None = None,
        progress_context=None,
        record: bool = False,
    ) -> None:
        request_id = new_request_id("ssh-connect")

        # Resolve endpoint and SSH key without enforcing readiness yet
        # We keep the fast-path and special waiting logic for best UX.
        # Endpoint
        task = self.provider.get_task(task_id)
        try:
            host, port = self.provider.resolve_ssh_endpoint(task_id, node=node)
            task.ssh_host = host
            try:
                task.ssh_port = int(port or 22)
            except Exception:
                task.ssh_port = 22
        except Exception as e:
            if not getattr(task, "ssh_host", None):
                raise make_error(str(e), request_id)

        # SSH key path
        ssh_key_path, error_msg = self.provider.get_task_ssh_connection_info(task_id)
        if not ssh_key_path:
            raise make_error(f"SSH key resolution failed: {error_msg}", request_id)

        # Build cache key for recent-success heuristics
        cache_key = self.connection_manager.build_cache_key(task_id, task, node)
        recent_success = self.connection_manager.check_recent_success(cache_key)

        # Fast TCP probe and optional immediate connect
        try:
            from flow.application.config.runtime import settings as _settings  # local import

            _debug = bool((_settings.ssh or {}).get("debug", False))
            fast_flag = bool((_settings.ssh or {}).get("fast", False))
        except Exception:
            _debug = os.environ.get("FLOW_SSH_DEBUG") == "1"
            fast_flag = os.environ.get("FLOW_SSH_FAST") == "1"
        if _debug:
            try:
                logger.debug(
                    "SSH readiness probe for %s host=%s port=%s key=%s",
                    task_id,
                    task.ssh_host,
                    getattr(task, "ssh_port", 22),
                    str(ssh_key_path),
                )
            except Exception:
                pass

        ssh_is_ready = SshStack.is_ssh_ready(
            user=getattr(task, "ssh_user", "ubuntu"),
            host=task.ssh_host,
            port=getattr(task, "ssh_port", 22),
            key_path=Path(ssh_key_path),
        )

        try:
            # Do not take the fast-path when recording; we must wrap with 'script' to capture logs.
            if (
                command is None
                and not record
                and (
                    fast_flag
                    or SshStack.tcp_port_open(task.ssh_host, getattr(task, "ssh_port", 22))
                )
            ):
                ssh_cmd = SshStack.build_ssh_command(
                    user=getattr(task, "ssh_user", "ubuntu"),
                    host=task.ssh_host,
                    port=getattr(task, "ssh_port", 22),
                    key_path=Path(ssh_key_path),
                )
                try:
                    _debug = bool((_settings.ssh or {}).get("debug", False))
                except Exception:
                    _debug = os.environ.get("FLOW_SSH_DEBUG") == "1"
                if _debug:
                    logger.debug("SSH fast-path exec argv: %s", " ".join(ssh_cmd))
                subprocess.run(ssh_cmd)
                return
        except Exception:
            pass

        if progress_context and hasattr(progress_context, "update_message"):
            try:
                progress_context.update_message(
                    "SSH ready, connecting..." if ssh_is_ready else "Waiting for SSH to be ready..."
                )
            except Exception:
                pass

        # Wait for readiness if needed (short sleeps/backoff), unless we recently succeeded
        if not ssh_is_ready and not recent_success:
            start_time = time.time()
            timeout = SSH_READY_WAIT_SECONDS
            attempts = 0
            while time.time() - start_time < timeout:
                if SshStack.is_ssh_ready(
                    user=getattr(task, "ssh_user", "ubuntu"),
                    host=task.ssh_host,
                    port=getattr(task, "ssh_port", 22),
                    key_path=Path(ssh_key_path),
                ):
                    break
                wait_time = min(0.2 * (1 + attempts), 2.0)
                time.sleep(wait_time)
                attempts += 1
            else:
                # Fallback: try immediate interactive connect once
                try:
                    ssh_cmd = SshStack.build_ssh_command(
                        user=getattr(task, "ssh_user", "ubuntu"),
                        host=task.ssh_host,
                        port=getattr(task, "ssh_port", 22),
                        key_path=Path(ssh_key_path),
                    )
                    try:
                        from flow.application.config.runtime import (
                            settings as _settings,  # local import
                        )

                        _debug = bool((_settings.ssh or {}).get("debug", False))
                    except Exception:
                        _debug = os.environ.get("FLOW_SSH_DEBUG") == "1"
                    if _debug:
                        logger.debug("SSH fallback exec argv: %s", " ".join(ssh_cmd))
                    subprocess.run(ssh_cmd)
                    return
                except Exception:
                    pass
                raise make_error("SSH connection timed out", request_id)

        # Prime SSH ControlMaster in the background
        try:
            master_cmd = SshStack.build_ssh_command(
                user=getattr(task, "ssh_user", "ubuntu"),
                host=task.ssh_host,
                port=getattr(task, "ssh_port", 22),
                key_path=Path(ssh_key_path),
                prefix_args=["-MNf", "-o", "ConnectTimeout=4", "-o", "ConnectionAttempts=1"],
            )
            with open("/dev/null", "w") as _null:
                subprocess.Popen(master_cmd, stdout=_null, stderr=_null)
        except Exception:
            pass

        # Build base SSH command
        ssh_cmd = SshStack.build_ssh_command(
            user=getattr(task, "ssh_user", "ubuntu"),
            host=task.ssh_host,
            port=getattr(task, "ssh_port", 22),
            key_path=Path(ssh_key_path),
        )

        # Apply recording wrapper if requested
        if record:
            remote_command, requires_tty = build_recording_command(command)
            if requires_tty:
                try:
                    ssh_cmd.insert(1, "-tt")
                except Exception:
                    ssh_cmd.append("-tt")
            ssh_cmd.append(remote_command)
        elif command:
            ssh_cmd.append(command)

        try:
            from flow.application.config.runtime import settings as _settings  # local import

            _debug = bool((_settings.ssh or {}).get("debug", False))
        except Exception:
            _debug = os.environ.get("FLOW_SSH_DEBUG") == "1"
        if _debug:
            try:
                logger.debug("SSH exec argv: %s", " ".join(ssh_cmd))
            except Exception:
                pass

        try:
            # For commands, capture output; for interactive shell, run normally
            if command:
                result = subprocess.run(ssh_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    if result.stdout:
                        print(result.stdout, end="")
                    self.connection_manager.mark_success(cache_key)
                    return
            else:
                # Stop animation if still active before taking over terminal
                if progress_context and hasattr(progress_context, "_active"):
                    if progress_context._active:  # type: ignore[attr-defined]
                        progress_context.__exit__(None, None, None)

                result = subprocess.run(ssh_cmd)
                self.connection_manager.mark_success(cache_key)
                return

            # Error handling
            stderr = (result.stderr or "").lower()
            if result.returncode != 0:
                if "connection timed out" in stderr or "operation timed out" in stderr:
                    elapsed = getattr(task, "instance_age_seconds", 0) or 0
                    if elapsed < EXPECTED_PROVISION_MINUTES * 60:
                        raise make_error(
                            f"SSH connection timed out. Instance may still be provisioning "
                            f"(elapsed: {elapsed / 60:.1f} minutes). Mithril instances can take up to "
                            f"{EXPECTED_PROVISION_MINUTES} minutes to become fully available. Please try again later.",
                            request_id,
                        )
                    self.connection_manager.bust_cache(cache_key)
                    raise make_error(
                        "SSH connection timed out. Possible causes:\n"
                        f"  - Instance is still provisioning (can take up to {EXPECTED_PROVISION_MINUTES} minutes)\n"
                        "  - Network connectivity issues\n"
                        "  - Security group/firewall blocking SSH (port 22)",
                        request_id,
                    )
                elif "connection refused" in stderr:
                    self.connection_manager.bust_cache(cache_key)
                    raise make_error(
                        "SSH connection refused. The instance is reachable but SSH service "
                        "is not ready yet. Please wait a few more minutes and try again.",
                        request_id,
                    )
                elif (
                    "connection reset by peer" in stderr or "kex_exchange_identification" in stderr
                ):
                    self.connection_manager.bust_cache(cache_key)
                    raise make_error(
                        "SSH connection was reset. The SSH service is still initializing.\n"
                        "This typically happens during the first few minutes after instance creation.\n"
                        "Please wait 1-2 minutes and try again.",
                        request_id,
                    )
                elif "permission denied" in stderr:
                    error_msg = "SSH authentication failed despite key resolution.\n\n"
                    error_msg += (
                        "This is unexpected - the SSH key was found but authentication failed.\n"
                    )
                    error_msg += "Possible causes:\n"
                    error_msg += (
                        "  1. The private key file permissions are too open (should be 600)\n"
                    )
                    error_msg += "  2. The key file is corrupted or invalid\n"
                    error_msg += (
                        "  3. The instance was created with a different key than expected\n\n"
                    )
                    error_msg += "Debug information:\n"
                    error_msg += f"  - SSH command: {' '.join(ssh_cmd[:6])}...\n"
                    error_msg += f"  - Task ID: {task_id}\n"
                    if "-i" in ssh_cmd:
                        key_idx = ssh_cmd.index("-i") + 1
                        if key_idx < len(ssh_cmd):
                            error_msg += f"  - Using SSH key: {ssh_cmd[key_idx]}\n"
                    raise make_error(error_msg, request_id)
                else:
                    raise make_error(f"SSH connection failed: {result.stderr}", request_id)
        except RemoteExecutionError:
            raise
        except Exception as e:
            raise make_error(f"SSH shell failed: {e!s}", request_id)
