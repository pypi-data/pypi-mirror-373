from __future__ import annotations

import logging
import json
import hashlib
import subprocess
from datetime import datetime, timezone
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from flow.adapters.transport.rsync import (
    ITransferStrategy,
    RsyncTransferStrategy,
    TransferError,
    TransferResult,
)
from flow.adapters.transport.ssh import (
    ExponentialBackoffSSHWaiter,
    ISSHWaiter,
    SSHConnectionInfo,
)
from flow.errors import FlowError
from flow.sdk.models import Task
from flow.core.ignore import build_exclude_patterns

logger = logging.getLogger(__name__)


class CodeTransferError(FlowError):
    pass


@dataclass
class CodeTransferConfig:
    source_dir: Path | None = None
    target_dir: str = "~"
    ssh_timeout: int = 1200
    transfer_timeout: int = 600
    retry_on_failure: bool = True
    use_compression: bool = True
    # When True, build a file list from Git changes for rsync; when False,
    # perform a full tree scan. None defers to legacy env override
    # (FLOW_GIT_INCREMENTAL) for temporary compatibility.
    git_incremental: bool | None = None

    def __post_init__(self):
        if self.source_dir is None:
            self.source_dir = Path.cwd()


class IProgressReporter:
    @contextmanager
    def ssh_wait_progress(self, message: str):
        yield

    @contextmanager
    def transfer_progress(self, message: str):
        yield

    def update_status(self, message: str) -> None:
        pass


class RichProgressReporter(IProgressReporter):
    """Progress reporter using Rich.

    Kept light to avoid heavy imports during library use; only instantiates
    console and progress when used.
    """

    def __init__(self, console: object = None):
        if console is None:
            from rich.console import Console as _Console  # lazy import

            self.console = _Console()
        else:
            self.console = console
        self._current_progress = None

    def _start_progress(self, message: str):
        from flow.cli.ui.presentation.animated_progress import AnimatedEllipsisProgress

        progress = AnimatedEllipsisProgress(
            self.console, f"[dim]{message}[/dim]", transient=True, start_immediately=True
        )
        self._current_progress = progress
        progress.__enter__()
        return progress

    def _stop_progress(self):
        prog = self._current_progress
        self._current_progress = None
        if prog is not None:
            try:
                prog.__exit__(None, None, None)
            except Exception:
                pass

    @contextmanager
    def ssh_wait_progress(self, message: str):
        progress = self._start_progress(message)
        try:
            yield progress
        finally:
            self._stop_progress()

    @contextmanager
    def transfer_progress(self, message: str):
        progress = self._start_progress(message)
        try:
            yield progress
        finally:
            self._stop_progress()

    def update_status(self, message: str) -> None:
        if self._current_progress and hasattr(self._current_progress, "update_message"):
            self._current_progress.update_message(message)
        else:
            self.console.print(f"[dim]{message}[/dim]")


class CodeTransferManager:
    def __init__(
        self,
        provider: object | None = None,
        ssh_waiter: ISSHWaiter | None = None,
        transfer_strategy: ITransferStrategy | None = None,
        progress_reporter: IProgressReporter | None = None,
    ):
        self.provider = provider
        self.ssh_waiter = ssh_waiter or ExponentialBackoffSSHWaiter(provider)
        self.transfer_strategy = transfer_strategy or RsyncTransferStrategy()
        self.progress_reporter = progress_reporter

    def transfer_code_to_task(
        self, task: Task, config: CodeTransferConfig | None = None
    ) -> TransferResult:
        if not config:
            config = CodeTransferConfig()

        logger.info(
            f"Starting code transfer to task {task.task_id}\n  Source: {config.source_dir}\n  Target: {task.task_id}:{config.target_dir}"
        )

        try:
            connection = self._wait_for_ssh(task, config)
            result = self._transfer_code(connection, config)
            self._verify_transfer(connection, config)
            return result
        except Exception as e:
            logger.error(f"Code transfer failed: {e}")
            if isinstance(e, CodeTransferError):
                raise
            # Include underlying error details for clearer CLI output
            raise CodeTransferError(f"Failed to transfer code to task {task.task_id}: {e!s}") from e

    def _wait_for_ssh(self, task: Task, config: CodeTransferConfig) -> SSHConnectionInfo:
        if task.ssh_host:
            try:
                return self.ssh_waiter.wait_for_ssh(task, timeout=3)
            except Exception:
                pass

        def ssh_progress(status: str):
            if self.progress_reporter:
                self.progress_reporter.update_status(status)

        try:
            if self.progress_reporter:
                with self.progress_reporter.ssh_wait_progress("Waiting for SSH access"):
                    return self.ssh_waiter.wait_for_ssh(
                        task, timeout=config.ssh_timeout, progress_callback=ssh_progress
                    )
            return self.ssh_waiter.wait_for_ssh(
                task, timeout=config.ssh_timeout, progress_callback=ssh_progress
            )
        except Exception as e:
            raise CodeTransferError(f"Failed to establish SSH connection: {e!s}") from e

    def _transfer_code(
        self, connection: SSHConnectionInfo, config: CodeTransferConfig
    ) -> TransferResult:
        # Decide if incremental mode is both requested and safe
        incremental_requested = getattr(config, "git_incremental", None) is True
        use_incremental = False
        if incremental_requested:
            try:
                use_incremental = self._is_incremental_safe(connection, config)
            except Exception:
                use_incremental = False
        def transfer_progress(progress):
            if self.progress_reporter:
                if hasattr(self.progress_reporter, "update_transfer"):
                    self.progress_reporter.update_transfer(
                        progress.percentage, progress.speed, progress.eta, progress.current_file
                    )
                else:
                    if progress.current_file:
                        file_display = progress.current_file.split("/")[-1]
                        self.progress_reporter.update_status(f"Uploading: {file_display}")
                    elif progress.percentage is not None:
                        status = f"Progress: {progress.percentage:.0f}%"
                        if progress.speed:
                            status += f" @ {progress.speed}"
                        if progress.eta:
                            status += f" (ETA: {progress.eta})"
                        self.progress_reporter.update_status(status)

        # Allow transfer strategies to seed a realistic estimated duration (e.g., from a preflight)
        # by attaching a helper on the callback. This avoids tight coupling and keeps the interface stable.
        try:
            if self.progress_reporter and hasattr(self.progress_reporter, "seed_estimated_seconds"):
                transfer_progress.seed_estimated_seconds = (
                    lambda seconds: self.progress_reporter.seed_estimated_seconds(seconds)
                )
        except Exception:
            pass

        try:
            if self.progress_reporter:
                with self.progress_reporter.transfer_progress(
                    f"Uploading code to {config.target_dir}"
                ):
                    # Helpful status before rsync emits the first progress line
                    try:
                        if incremental_requested and not use_incremental:
                            self.progress_reporter.update_status(
                                "Incremental requested but no matching baseline; using full scan"
                            )
                        else:
                            self.progress_reporter.update_status(
                                "Starting rsync (scanning changes)..."
                            )
                    except Exception:
                        pass
                    result = self.transfer_strategy.transfer(
                        source=config.source_dir,  # type: ignore[arg-type]
                        target=config.target_dir,
                        connection=connection,
                        progress_callback=transfer_progress,
                        git_incremental=use_incremental,
                    )
                    # Quick remote verification message
                    try:
                        self.progress_reporter.update_status("Verifying upload on remote...")
                    except Exception:
                        pass
                    # Write remote sync marker for future safe incrementals
                    try:
                        self._write_remote_marker(connection, config, result)
                    except Exception:
                        pass
                    # Attach a concise summary to the completed step (best-effort)
                    try:
                        if hasattr(self.progress_reporter, "set_completion_note"):
                            rate = getattr(result, "transfer_rate", None)
                            mb = max(0, int(result.bytes_transferred / (1024 * 1024)))
                            note = f"{result.files_transferred} files, {mb} MB"
                            if isinstance(rate, str) and rate:
                                note += f" @ {rate}"
                            self.progress_reporter.set_completion_note(note)
                    except Exception:
                        pass
                    return result
            result = self.transfer_strategy.transfer(
                source=config.source_dir,  # type: ignore[arg-type]
                target=config.target_dir,
                connection=connection,
                progress_callback=transfer_progress,
                git_incremental=use_incremental,
            )
            try:
                self._write_remote_marker(connection, config, result)
            except Exception:
                pass
            return result
        except TransferError as e:
            # Opportunistic fallback when target directory is not writable (e.g., /workspace on host)
            msg = str(e)
            try:
                target = config.target_dir
            except Exception:
                target = None

            def _should_fallback_to_home(error_text: str, target_dir: str | None) -> bool:
                if not target_dir:
                    return False
                denied_indicators = [
                    "Permission denied",
                    "failed: Permission denied",
                    f'mkdir "{target_dir}" failed',
                ]
                return any(ind in error_text for ind in denied_indicators)

            if target and _should_fallback_to_home(msg, target) and target != "~":
                try:
                    if self.progress_reporter:
                        self.progress_reporter.update_status(
                            f"Remote path {target} not writable; retrying with home (~)"
                        )
                except Exception:
                    pass
                # Retry once to home directory
                try:
                    return self.transfer_strategy.transfer(
                        source=config.source_dir,  # type: ignore[arg-type]
                        target="~",
                        connection=connection,
                        progress_callback=transfer_progress,
                        git_incremental=use_incremental,
                    )
                except TransferError:
                    # Fall through to generic handling
                    pass

            if config.retry_on_failure:
                return self.transfer_strategy.transfer(
                    source=config.source_dir,  # type: ignore[arg-type]
                    target=config.target_dir,
                    connection=connection,
                    git_incremental=use_incremental,
                )
            raise CodeTransferError(f"Code transfer failed: {e}") from e

    def _verify_transfer(self, connection: SSHConnectionInfo, config: CodeTransferConfig) -> None:
        # Optional: provider-specific verification via remote execution, if provider exposes it
        try:
            if getattr(self.provider, "remote_exec", None):
                output = self.provider.remote_exec(
                    connection.task_id, f"ls -la {config.target_dir} | head -5"
                )
                if output and "No such file or directory" in output:
                    raise CodeTransferError(
                        f"Target directory {config.target_dir} not found after transfer"
                    )
        except Exception:
            # Best-effort
            pass

    # ---------------- incremental handshake helpers ----------------
    def _get_git_head(self, source: Path | None) -> str | None:
        if not source:
            return None
        try:
            check = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=source,
                capture_output=True,
                text=True,
            )
            if check.returncode != 0 or check.stdout.strip().lower() != "true":
                return None
            head = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=source, capture_output=True, text=True
            )
            if head.returncode == 0:
                return head.stdout.strip()
        except Exception:
            return None
        return None

    def _hash_patterns(self, patterns: list[str]) -> str:
        h = hashlib.sha256()
        for p in sorted(patterns):
            h.update(p.encode("utf-8", "ignore") + b"\n")
        return h.hexdigest()

    def _is_incremental_safe(self, connection: SSHConnectionInfo, config: CodeTransferConfig) -> bool:
        source_dir = config.source_dir or Path.cwd()
        commit = self._get_git_head(source_dir)
        if not commit:
            return False
        spec = build_exclude_patterns(source_dir)
        ignore_hash = self._hash_patterns(spec.patterns)

        # Candidate marker locations: requested target and home
        candidates: list[str] = []
        try:
            if config.target_dir:
                candidates.append(f"{config.target_dir}/.flow-sync.json")
        except Exception:
            pass
        candidates.append("~/.flow-sync.json")

        for remote_path in candidates:
            try:
                if getattr(self.provider, "remote_exec", None):
                    out = self.provider.remote_exec(
                        connection.task_id, f"cat {remote_path} 2>/dev/null || true"
                    )
                    if not out:
                        continue
                    data = json.loads(out)
                    if (
                        isinstance(data, dict)
                        and data.get("commit") == commit
                        and data.get("ignore_hash") == ignore_hash
                    ):
                        return True
            except Exception:
                continue
        return False

    def _write_remote_marker(
        self, connection: SSHConnectionInfo, config: CodeTransferConfig, result: TransferResult
    ) -> None:
        source_dir = config.source_dir or Path.cwd()
        spec = build_exclude_patterns(source_dir)
        meta = {
            "version": 1,
            "commit": self._get_git_head(source_dir),
            "ignore_hash": self._hash_patterns(spec.patterns),
            "ignore_source": spec.source,
            "target_dir": getattr(result, "final_target", config.target_dir),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        content = json.dumps(meta, separators=(",", ":"))
        remote_dir = getattr(result, "final_target", config.target_dir)
        remote_file = f"{remote_dir}/.flow-sync.json"
        if not getattr(self.provider, "remote_exec", None):
            return
        # Write via here-doc with conservative quoting
        escaped = content.replace("'", "'\''")
        cmd = f"bash -lc 'cat > {remote_file} <<\'EOF\'\n{escaped}\nEOF'"
        try:
            self.provider.remote_exec(connection.task_id, cmd)
        except Exception:
            pass
