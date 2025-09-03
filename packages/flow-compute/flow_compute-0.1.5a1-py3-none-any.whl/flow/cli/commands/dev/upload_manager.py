"""Handles code synchronization (rsync) for the dev command."""

import logging
from pathlib import Path

from flow import DEFAULT_UPLOAD_ESTIMATED_MINUTES
from flow.cli.commands.base import console
from flow.cli.utils.step_progress import StepTimeline, UploadProgressReporter
from flow.sdk.client import Flow
from flow.sdk.models import Task

logger = logging.getLogger(__name__)


class DevUploadManager:
    """Handles synchronization of local code to the dev VM."""

    def __init__(self, flow_client: Flow, vm_task: Task, timeline: StepTimeline):
        self.flow_client = flow_client
        self.vm_task = vm_task
        self.timeline = timeline
        self.provider = flow_client.provider

    def upload(self, upload_path: str, env_name: str) -> None:
        """Validates the path and uploads code."""
        upload_path_resolved = Path(upload_path).resolve()
        if not upload_path_resolved.exists():
            console.print(f"[error]Error: Upload path does not exist: {upload_path}[/error]")
            raise SystemExit(1)

        if not upload_path_resolved.is_dir():
            console.print(f"[error]Error: Upload path must be a directory: {upload_path}[/error]")
            raise SystemExit(1)

        try:
            if env_name == "default":
                self._upload_to_default(upload_path_resolved)
            else:
                self._upload_to_env(upload_path_resolved, env_name)
        except Exception as e:
            self._handle_upload_error(e)

    def _upload_to_default(self, source_dir: Path) -> None:
        from flow.cli.utils.step_progress import build_sync_check_hint

        step_idx_upload = self.timeline.add_step("Checking for changes", show_bar=False)
        self.timeline.start_step(step_idx_upload)
        try:
            self.timeline.set_active_hint_text(build_sync_check_hint())
        except Exception:
            pass

        def _flip_to_upload():
            try:
                self.timeline.complete_step()
                new_idx = self.timeline.add_step(
                    "Uploading code",
                    show_bar=True,
                    estimated_seconds=DEFAULT_UPLOAD_ESTIMATED_MINUTES * 60,
                )
                self.timeline.start_step(new_idx)
                nonlocal upload_reporter
                upload_reporter = UploadProgressReporter(self.timeline, new_idx)
            except Exception:
                pass

        upload_reporter = UploadProgressReporter(
            self.timeline, step_idx_upload, on_start=_flip_to_upload
        )
        # Use transport-layer manager to support progress and provider-agnostic upload
        from flow.sdk.transfer import CodeTransferConfig as _Cfg
        from flow.sdk.transfer import CodeTransferManager as _Mgr

        cfg = _Cfg(source_dir=source_dir, target_dir="~", ssh_timeout=1200, transfer_timeout=600)
        result = _Mgr(
            provider=self.provider, progress_reporter=upload_reporter
        ).transfer_code_to_task(self.vm_task, cfg)
        try:
            if (
                getattr(result, "files_transferred", 0) == 0
                and getattr(result, "bytes_transferred", 0) == 0
            ):
                try:
                    self.timeline.complete_step(note="No changes")
                except Exception:
                    pass
        except Exception:
            pass

    def _upload_to_env(self, source_dir: Path, env_name: str) -> None:
        from flow.cli.utils.step_progress import build_sync_check_hint

        # Create environment directory
        remote_ops = self.flow_client.get_remote_operations()
        env_target_dir = f"/envs/{env_name}"
        setup_cmd = f"mkdir -p {env_target_dir}"
        remote_ops.execute_command(self.vm_task.task_id, setup_cmd)

        # Upload to home directory first (provider default)
        step_idx_upload = self.timeline.add_step("Checking for changes", show_bar=False)
        self.timeline.start_step(step_idx_upload)
        try:
            self.timeline.set_active_hint_text(build_sync_check_hint())
        except Exception:
            pass

        def _flip_to_upload2():
            try:
                self.timeline.complete_step()
                new_idx = self.timeline.add_step(
                    "Uploading code",
                    show_bar=True,
                    estimated_seconds=DEFAULT_UPLOAD_ESTIMATED_MINUTES * 60,
                )
                self.timeline.start_step(new_idx)
                nonlocal upload_reporter
                upload_reporter = UploadProgressReporter(self.timeline, new_idx)
            except Exception:
                pass

        upload_reporter = UploadProgressReporter(
            self.timeline, step_idx_upload, on_start=_flip_to_upload2
        )
        from flow.sdk.transfer import CodeTransferConfig as _Cfg
        from flow.sdk.transfer import CodeTransferManager as _Mgr

        cfg = _Cfg(source_dir=source_dir, target_dir="~", ssh_timeout=1500, transfer_timeout=1200)
        result = _Mgr(
            provider=self.provider, progress_reporter=upload_reporter
        ).transfer_code_to_task(self.vm_task, cfg)
        try:
            if (
                getattr(result, "files_transferred", 0) == 0
                and getattr(result, "bytes_transferred", 0) == 0
            ):
                try:
                    self.timeline.complete_step(note="No changes")
                except Exception:
                    pass
        except Exception:
            pass

        # Copy to environment directory with a brief spinner
        copy_cmd = f"rsync -av \"$HOME/\" {env_target_dir}/ --exclude='/envs/'"
        step_idx_env = self.timeline.add_step(f"Environment '{env_name}'", show_bar=False)
        self.timeline.start_step(step_idx_env)
        remote_ops.execute_command(self.vm_task.task_id, copy_cmd)
        self.timeline.complete_step()

    def _handle_upload_error(self, e: Exception) -> None:
        msg = str(e)
        console.print(f"[error]Error uploading code: {msg}[/error]")
        low = msg.lower()

        # Heuristic guidance based on common rsync/SSH errors
        if "permission denied" in low or "publickey" in low:
            console.print("\n[warning]SSH authentication failed[/warning]")
            console.print(
                "  • Ensure your SSH key is registered: [accent]flow ssh-keys get[/accent]"
            )
            console.print(
                "  • Upload a key if missing: [accent]flow ssh-keys upload ~/.ssh/id_ed25519.pub[/accent]"
            )
            console.print("  • Or set MITHRIL_SSH_KEYS env to your private key path")
            return

        if "rsync" in low or "command not found" in low:
            console.print("\n[warning]rsync missing[/warning]")
            console.print(
                "  • Local: macOS [accent]brew install rsync[/accent]; Ubuntu [accent]sudo apt-get install rsync[/accent]"
            )
            console.print(
                "  • Remote VM: attach with [accent]flow dev[/accent] and run [accent]sudo apt-get update && sudo apt-get install -y rsync[/accent]"
            )
            return

        if "no space left on device" in low:
            console.print("\n[warning]Remote disk is full[/warning]")
            console.print(
                "  • Clean up large files on the VM or reduce what you upload via [.flowignore]"
            )
            console.print(
                "  • Check disk usage: [accent]flow dev[/accent] then [accent]df -h[/accent]"
            )
            return

        if (
            "connection timed out" in low
            or "connection refused" in low
            or "network is unreachable" in low
        ):
            console.print("\n[warning]Network issue during upload[/warning]")
            console.print("  • Verify the VM is reachable: [accent]flow dev[/accent]")
            console.print("  • Retry shortly; transient network hiccups can occur")
            return

        if "file name too long" in low or "argument list too long" in low:
            console.print("\n[warning]Too many files or paths too long[/warning]")
            console.print("  • Add more patterns to [.flowignore] to limit uploads")
            console.print("  • Consider excluding build artifacts, venvs, node_modules")
            return

        # Generic guidance
        console.print(
            "\n[dim]Tips:[/dim] Use [.flowignore] to exclude large directories; run [accent]flow upload-code[/accent] for manual sync."
        )
