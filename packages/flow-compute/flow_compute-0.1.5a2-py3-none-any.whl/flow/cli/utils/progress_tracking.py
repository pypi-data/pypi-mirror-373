"""Progress tracking and management for the run command.

This module handles all progress reporting, timeline management,
and user feedback during task execution.
"""

from __future__ import annotations

import logging

from rich.console import Console

from flow import (
    DEFAULT_ALLOCATION_ESTIMATED_SECONDS,
    DEFAULT_PROVISION_MINUTES,
    DEFAULT_UPLOAD_ESTIMATED_MINUTES,
)
from flow.cli.utils.step_progress import (
    AllocationProgressAdapter,
    SSHWaitProgressAdapter,
    StepTimeline,
    UploadProgressReporter,
    build_provisioning_hint,
)
from flow.sdk.client import Flow
from flow.sdk.models import Task
from flow.sdk.models.run_params import RunParameters, UploadConfig

logger = logging.getLogger(__name__)


class ProgressTrackingError(Exception):
    """Raised when progress tracking fails."""

    pass


class RunProgressManager:
    """Manages progress tracking and user feedback.

    This class encapsulates progress tracking logic that was previously
    embedded in RunCommand._execute (lines 1236-1413).
    """

    def __init__(self, client: Flow, console: Console):
        """Initialize progress manager.

        Args:
            client: Flow API client.
            console: Rich console for output.
        """
        self.client = client
        self.console = console
        self.timeline: StepTimeline | None = None

    def start_timeline(self, params: RunParameters) -> None:
        """Start progress timeline if appropriate.

        Args:
            params: Run parameters to check display preferences.
        """
        if params.execution.output_json or params.display.compact:
            return

        self.timeline = StepTimeline(self.console, title="flow run", title_animation="auto")
        self.timeline.start()

    def finish_timeline(self) -> None:
        """Clean up timeline if active."""
        if self.timeline:
            try:
                self.timeline.finish()
            except Exception as e:
                logger.debug(f"Failed to finish timeline: {e}")
            finally:
                self.timeline = None

    def track_submission(self, submit_func) -> Task:
        """Track task submission progress.

        Args:
            submit_func: Function that performs the submission.

        Returns:
            Submitted task.
        """
        if not self.timeline:
            return submit_func()

        submit_idx = self.timeline.add_step("Submitting task", show_bar=False)
        self.timeline.start_step(submit_idx)
        try:
            task = submit_func()
            self.timeline.complete_step()
            return task
        except Exception:
            self.timeline.complete_step(note="Failed")
            raise

    def track_allocation(self, task: Task, params: RunParameters) -> str:
        """Track instance allocation progress.

        Args:
            task: Task being allocated.
            params: Run parameters.

        Returns:
            Final task status.
        """
        if not self.timeline:
            from flow.cli.commands.utils import wait_for_task

            return wait_for_task(
                self.client,
                task.task_id,
                watch=params.execution.watch,
                json_output=False,
                task_name=task.name,
            )

        alloc_idx = self.timeline.add_step(
            "Allocating instance",
            show_bar=True,
            estimated_seconds=DEFAULT_ALLOCATION_ESTIMATED_SECONDS,
        )

        alloc_adapter = AllocationProgressAdapter(
            self.timeline,
            alloc_idx,
            estimated_seconds=DEFAULT_ALLOCATION_ESTIMATED_SECONDS,
        )

        with alloc_adapter:
            # Standardized allocation hint (exits local wait; allocation continues)
            try:
                from flow.cli.utils.step_progress import build_allocation_hint as _bah

                self.timeline.set_active_hint_text(_bah("flow status -w", subject="allocation"))
            except Exception:
                pass

            from flow.cli.commands.utils import wait_for_task

            return wait_for_task(
                self.client,
                task.task_id,
                watch=False,
                json_output=False,
                task_name=task.name,
                progress_adapter=alloc_adapter,
            )

    def track_ssh_wait(self, task: Task, timeout_minutes: int = 10) -> Task:
        """Track SSH provisioning progress.

        Args:
            task: Task to wait for SSH.
            timeout_minutes: Maximum wait time.

        Returns:
            Updated task with SSH details.
        """
        if not self.timeline:
            # When no timeline is active, show a lightweight animated status line and
            # pass a minimal adapter so the SDK can nudge refresh without importing CLI.
            try:
                from flow import DEFAULT_PROVISION_MINUTES as _DEF_PROV
                from flow.cli.ui.presentation.animated_progress import AnimatedEllipsisProgress

                class _SimpleSSHAdapter:
                    def update_eta(self, eta: str | None = None) -> None:
                        # AnimatedEllipsisProgress updates itself; no explicit update needed
                        return None

                with AnimatedEllipsisProgress(
                    self.console,
                    "Provisioning instance",
                    start_immediately=True,
                    transient=True,
                    estimated_seconds=_DEF_PROV * 60,
                    show_progress_bar=True,
                    task_created_at=(
                        getattr(task, "instance_created_at", None)
                        or getattr(task, "created_at", None)
                    ),
                ):
                    return self.client.wait_for_ssh(
                        task_id=task.task_id,
                        timeout=timeout_minutes * 60,
                        show_progress=False,
                        progress_adapter=_SimpleSSHAdapter(),
                    )
            except Exception:
                # Fallback without animations if UI is unavailable
                return self.client.wait_for_ssh(
                    task_id=task.task_id,
                    timeout=timeout_minutes * 60,
                    show_progress=False,
                )

        # Calculate baseline from instance age
        baseline = 0
        try:
            baseline = int(getattr(task, "instance_age_seconds", 0) or 0)
        except Exception:
            baseline = 0

        prov_idx = self.timeline.add_step(
            f"Provisioning instance (up to {DEFAULT_PROVISION_MINUTES}m)",
            show_bar=True,
            estimated_seconds=DEFAULT_PROVISION_MINUTES * 60,
            baseline_elapsed_seconds=baseline,
        )

        ssh_adapter = SSHWaitProgressAdapter(
            self.timeline,
            prov_idx,
            DEFAULT_PROVISION_MINUTES * 60,
            baseline_elapsed_seconds=baseline,
        )

        with ssh_adapter:
            # Add hints for user actions under active step
            # Provide clear guidance plus concise context on why it may take a while
            try:
                self.timeline.set_active_hint_text(
                    build_provisioning_hint(
                        "job", "flow status -w", extra_action=("Upload later: ", "flow upload-code")
                    )
                )
            except Exception:
                pass
            return self.client.wait_for_ssh(
                task_id=task.task_id,
                timeout=timeout_minutes * 60,
                show_progress=False,
                progress_adapter=ssh_adapter,
            )

    def track_code_upload(self, task: Task, upload_config: UploadConfig) -> object | None:
        """Track code upload progress.

        Args:
            task: Task to upload code to.
            upload_config: Upload configuration.

        Returns:
            Upload result or None if skipped/failed.
        """
        if not self.timeline:
            return self._perform_upload(task, upload_config, None)

        # Start with checking phase
        check_idx = self.timeline.add_step("Checking for changes", show_bar=False)
        self.timeline.start_step(check_idx)

        reporter = None

        def flip_to_upload():
            """Switch from checking to uploading."""
            nonlocal reporter
            try:
                self.timeline.complete_step()
                upload_idx = self.timeline.add_step(
                    "Uploading code",
                    show_bar=True,
                    estimated_seconds=DEFAULT_UPLOAD_ESTIMATED_MINUTES * 60,
                )
                self.timeline.start_step(upload_idx)
                reporter = UploadProgressReporter(self.timeline, upload_idx)
            except Exception:
                pass

        # Create reporter with flip callback
        reporter = UploadProgressReporter(self.timeline, check_idx, on_start=flip_to_upload)

        # Add upload hints
        self._set_upload_hints(task)

        try:
            result = self._perform_upload(task, upload_config, reporter)

            # Annotate if no changes
            if result and self._is_noop_upload(result):
                self.timeline.complete_step(note="No changes")

            return result

        except KeyboardInterrupt:
            self.console.print(
                "\n[dim]Upload interrupted by user. Instance remains running.\n"
                "Resume anytime with: flow upload-code[/dim]"
            )
            return None
        except Exception as e:
            self._handle_upload_failure(e, task, upload_config)
            return None

    def _perform_upload(
        self, task: Task, upload_config: UploadConfig, reporter: UploadProgressReporter | None
    ) -> object:
        """Perform the actual code upload.

        Args:
            task: Task to upload to.
            upload_config: Upload configuration.
            reporter: Optional progress reporter.

        Returns:
            Upload result from provider.
        """
        return self.client.upload_code_to_task(
            task_id=task.task_id,
            source_dir=str(upload_config.code_root) if upload_config.code_root else None,
            timeout=upload_config.timeout,
            console=None,
            target_dir="~",
            progress_reporter=reporter,
        )

    def _is_noop_upload(self, result: object) -> bool:
        """Check if upload transferred no files.

        Args:
            result: Upload result object.

        Returns:
            True if no files were transferred.
        """
        try:
            files = getattr(result, "files_transferred", 0)
            bytes_transferred = getattr(result, "bytes_transferred", 0)
            return files == 0 and bytes_transferred == 0
        except Exception:
            return False

    def _set_upload_hints(self, task: Task) -> None:
        """Set user hints during upload.

        Args:
            task: Task being uploaded to.
        """
        if not self.timeline:
            return

        try:
            from rich.text import Text

            from flow.cli.utils.theme_manager import theme_manager

            accent = theme_manager.get_color("accent")
            hint = Text()
            hint.append("  Press ")
            hint.append("Ctrl+C", style=accent)
            hint.append(" to cancel upload. Instance keeps running; resume with ")
            hint.append("flow upload-code", style=accent)

            self.timeline.set_active_hint_text(hint)
        except Exception:
            pass

    def _handle_upload_failure(
        self, error: Exception, task: Task, upload_config: UploadConfig
    ) -> None:
        """Handle upload failure based on policy.

        Args:
            error: Upload error.
            task: Task that failed upload.
            upload_config: Upload configuration with failure policy.
        """
        from flow.cli.utils.theme_manager import theme_manager

        warn_color = theme_manager.get_color("warning")
        task_ref = task.name or task.task_id

        self.console.print(f"\n[{warn_color}]Upload skipped: {error}[/{warn_color}]")
        self.console.print(
            f"[dim]Instance is running. Sync later with: flow upload-code {task_ref}[/dim]"
        )

        # Honor failure policy
        if upload_config.on_failure == "fail":
            raise ProgressTrackingError(f"Code upload failed: {error}")

    def show_completion_message(self, task: Task, status: str, params: RunParameters) -> None:
        """Display appropriate completion message.

        Args:
            task: Completed task.
            status: Final task status.
            params: Run parameters.
        """
        from flow.cli.commands.messages import print_next_actions
        from flow.cli.utils.theme_manager import theme_manager

        task_ref = task.name or task.task_id

        if status == "running":
            success_color = theme_manager.get_color("success")
            self.console.print(f"\n[{success_color}]✓[/{success_color}] Task launched")

            if task.name:
                self.console.print(f"Task name: [accent]{task.name}[/accent]")
                self.console.print(f"Task ID: [dim]{task.task_id}[/dim]")
            else:
                self.console.print(f"Task ID: [accent]{task.task_id}[/accent]")

            # Prefer a calm, readiness-first flow: check details, follow logs, then SSH
            recommendations = [
                f"View details: [accent]flow status {task_ref}[/accent] [muted]— Readiness & timeline[/muted]",
                f"Follow logs: [accent]flow logs {task_ref} -f[/accent] [muted]— Startup output[/muted]",
                f"SSH when ready: [accent]flow ssh {task_ref}[/accent] [muted]— Auto-waits[/muted]",
            ]

            # Add upload action if code upload was intended
            try:
                if params.upload.strategy != "none":
                    recommendations.append(
                        f"Upload code: [accent]flow upload-code {task_ref}[/accent]"
                    )
            except Exception:
                pass

            print_next_actions(self.console, recommendations)

        elif status == "failed":
            self.console.print("\n[error]✗[/error] Task failed to start")
            print_next_actions(
                self.console,
                [
                    f"View error logs: [accent]flow logs {task_ref}[/accent]",
                    f"Check task details: [accent]flow status {task_ref}[/accent]",
                    "Retry with different parameters: [accent]flow run <config.yaml>[/accent]",
                ],
            )

        elif status == "cancelled":
            self.console.print("\n[warning]![/warning] Task was cancelled")
            print_next_actions(
                self.console,
                [
                    "Submit a new task: [accent]flow run <config.yaml>[/accent]",
                    "View task history: [accent]flow status --all[/accent]",
                ],
            )
