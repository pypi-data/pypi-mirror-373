"""Mount command - attach volumes to tasks.

Attaches a storage volume to a task's configuration. If the task hasn't fully
booted yet, the mount will finalize automatically during startup when SSH is
available. For already-booted instances, the volume is attached to the task but
may require a manual mount on the instance (or a restart) to become accessible.

Command Usage:
    flow mount VOLUME_ID TASK_ID
    flow mount VOLUME_ID TASK_ID --mount-point /custom/path

Examples:
    Mount by volume ID:
        $ flow mount vol_abc123def456 task_xyz789

    Mount by volume name:
        $ flow mount training-data gpu-job-1

    Mount using indices:
        $ flow mount 1 2

    Mount with custom path:
        $ flow mount datasets ml-training --mount-point /data/training

The mount operation:
1. Validates volume and task exist
2. Checks region compatibility
3. Updates task configuration via API (may pause/resume the task under the hood)
4. Mount becomes available at /volumes/{volume_name} once the instance mounts it

Requirements:
- Task can be pending/starting; mount finalizes when the task is ready (SSH available)
- Volume and task must be in same region
- Volume cannot already be attached to the task
- For already-booted instances, a manual mount may be required (e.g., update fstab and run 'sudo mount -a')
"""

import os
import re

import click

from flow.cli.commands.base import BaseCommand, console
from flow.cli.ui.presentation.animated_progress import AnimatedEllipsisProgress
from flow.cli.utils.error_handling import cli_error_guard
from flow.cli.utils.status_utils import get_status_string
from flow.cli.utils.step_progress import StepTimeline
from flow.cli.utils.task_resolver import resolve_task_identifier
from flow.cli.utils.volume_resolver import get_volume_display_name, resolve_volume_identifier
from flow.errors import (
    AuthenticationError,
    RemoteExecutionError,
    ResourceNotFoundError,
    ValidationError,
)
from flow.sdk.factory import create_client


class MountCommand(BaseCommand):
    """Mount volumes to tasks (finalizes when task is ready)."""

    def validate_mount_point(self, mount_point: str) -> str | None:
        """Validate and sanitize a custom mount point.

        Args:
            mount_point: User-provided mount path

        Returns:
            Sanitized mount path or None if invalid

        Raises:
            ValidationError: If mount point is invalid
        """
        if not mount_point:
            return None

        # Must be absolute path
        if not mount_point.startswith("/"):
            raise ValidationError("Mount point must be an absolute path (start with '/')")

        # Check for path traversal
        if ".." in mount_point:
            raise ValidationError("Mount point cannot contain '..' (path traversal)")

        # Check allowed prefixes
        allowed_prefixes = ["/volumes/", "/mnt/", "/data/", "/opt/", "/var/"]
        if not any(mount_point.startswith(prefix) for prefix in allowed_prefixes):
            raise ValidationError(
                f"Mount point must start with one of: {', '.join(allowed_prefixes)}"
            )

        # Check length
        if len(mount_point) > 255:
            raise ValidationError("Mount point path too long (max 255 characters)")

        # Check valid characters
        if not re.match(r"^/[a-zA-Z0-9/_-]+$", mount_point):
            raise ValidationError(
                "Mount point can only contain letters, numbers, hyphens, underscores, and slashes"
            )

        return mount_point

    @property
    def name(self) -> str:
        return "mount"

    @property
    def help(self) -> str:
        return (
            "Attach storage volumes to tasks (may require machine restart to take effect). "
            "Multi-instance: file-share volumes mount to all instances; block volumes are single-instance only."
        )

    def get_command(self) -> click.Command:
        """Return the mount command."""
        # Import completion functions
        # from flow.cli.utils.mode import demo_aware_command
        from flow.cli.ui.runtime.shell_completion import complete_task_ids, complete_volume_ids

        @click.command(name=self.name, help=self.help)
        @click.argument("volume_identifier", required=False, shell_complete=complete_volume_ids)
        @click.argument("task_identifier", required=False, shell_complete=complete_task_ids)
        @click.option(
            "--volume", "-v", help="Volume ID or name to mount", shell_complete=complete_volume_ids
        )
        @click.option(
            "--task", "-t", help="Task ID or name to mount to", shell_complete=complete_task_ids
        )
        @click.option(
            "--instance",
            "-i",
            type=int,
            help="Specific instance index (0-based) for multi-instance tasks (not yet supported)",
        )
        @click.option(
            "--mount-point",
            "-m",
            type=str,
            help="Custom mount path on the instance (default: /volumes/{volume_name})",
        )
        @click.option(
            "--dry-run", is_flag=True, help="Preview the mount operation without executing"
        )
        @click.option(
            "--verbose",
            "-V",
            is_flag=True,
            help="Show detailed mount workflows and troubleshooting",
        )
        @click.option(
            "--wait/--no-wait",
            default=True,
            help="Wait for SSH and verify the mount before exiting (default: wait)",
        )
        @click.option(
            "--persist",
            is_flag=True,
            help="Attempt to persist the mount in /etc/fstab after verification",
        )
        @click.option(
            "--yes",
            "-y",
            is_flag=True,
            help="Skip confirmation when attaching to a running instance (may pause VM)",
        )
        @click.option("--json", "output_json", is_flag=True, help="Output JSON for automation")
        # @demo_aware_command()
        @cli_error_guard(self)
        def mount(
            volume_identifier: str | None,
            task_identifier: str | None,
            volume: str | None,
            task: str | None,
            instance: int | None,
            mount_point: str | None,
            dry_run: bool,
            verbose: bool,
            wait: bool,
            persist: bool,
            yes: bool,
            output_json: bool,
        ):
            """Mount a volume to a task.

            \b
            Examples:
                flow mount vol-abc123 my-task    # Mount by IDs/names
                flow mount dataset training-job   # Mount by names
                flow mount 1 2                    # Mount by indices
                flow mount -v data -t task -i 0   # Specific instance
                flow mount vol-123 task-456 --mount-point /data/datasets  # Custom path

            Use 'flow mount --verbose' for detailed workflows and troubleshooting.
            """
            if verbose:
                from flow.cli.utils.icons import flow_icon as _flow_icon

                console.print(f"\n[bold]{_flow_icon()} Volume Mounting Guide:[/bold]\n")
                console.print("Basic usage:")
                console.print("  flow mount VOLUME TASK            # Positional arguments")
                console.print("  flow mount -v VOLUME -t TASK      # Using flags")
                console.print("  flow mount --dry-run VOLUME TASK  # Preview operation\n")

                console.print("Multi-instance tasks:")
                console.print("  flow mount data distributed-job -i 0    # Mount to head node")
                console.print("  flow mount data distributed-job -i 1    # Mount to worker")
                console.print(
                    "  flow mount data distributed-job         # Mount to all instances\n"
                )

                console.print("Selection methods:")
                console.print("  flow mount vol_abc123 task_xyz789       # By full IDs")
                console.print("  flow mount training-data my-job         # By names")
                console.print("  flow mount 1 2                         # By index from listings\n")

                console.print("Mount locations:")
                console.print("  • Default: /volumes/{volume_name}")
                console.print("  • Example: volume 'datasets' → /volumes/datasets")
                console.print("  • Custom: --mount-point /data/my-volume")
                console.print("  • Allowed prefixes: /volumes/, /mnt/, /data/, /opt/, /var/")
                console.print("  • Access: cd /volumes/datasets\n")

                console.print("Common workflows:")
                console.print("  # Mount dataset to a training job")
                console.print("  flow volumes get                  # Find volume")
                console.print("  flow status                       # Find task")
                console.print("  flow mount dataset training-job   # Mount it")
                console.print("  ")
                console.print("  # Share data between tasks")
                console.print("  flow mount shared-data task1")
                console.print("  flow mount shared-data task2\n")

                console.print("Requirements:")
                console.print("  • Task can be pending; mount finalizes when task starts")
                console.print("  • Volume and task in same region")
                console.print("  • Volume not already mounted")
                console.print("  • SSH access available\n")

                console.print("Troubleshooting:")
                console.print("  • Permission denied → Check volume exists: flow volumes get")
                console.print("  • Task not found → Verify status: flow status")
                console.print("  • Region mismatch → Create volume in task's region")
                console.print("  • Mount failed → Check SSH: flow ssh <task>\n")
                return
            try:
                flow_client = create_client(auto_init=True)

                # Handle both positional and flag-based arguments
                volume_id = volume or volume_identifier
                task_id = task or task_identifier

                # Track if we used interactive selection
                selected_volume = None
                selected_task = None

                # Interactive selection if arguments are missing
                if not volume_id:
                    # Get available volumes (show AEP while fetching)
                    from flow.cli.ui.components import select_volume
                    from flow.cli.ui.presentation.animated_progress import (
                        AnimatedEllipsisProgress as _AEP,
                    )

                    with _AEP(console, "Fetching volumes", start_immediately=True):
                        volumes = flow_client.volumes.list()
                    if not volumes:
                        console.print("[warning]No volumes available.[/warning]")
                        console.print(
                            "\nCreate a volume with: [accent]flow volumes create --size 100[/accent]"
                        )
                        return

                    selected_volume = select_volume(volumes, title="Select a volume to mount")
                    if not selected_volume:
                        console.print("[warning]No volume selected.[/warning]")
                        return
                    volume_id = selected_volume.volume_id
                    # Debug: Show what we selected
                    if verbose:
                        console.print(f"[dim]Selected volume ID: {volume_id}[/dim]")

                if not task_id:
                    # Get available tasks using centralized fetcher (leverages prefetch cache)
                    from flow.cli.ui.components import select_task
                    from flow.cli.utils.status_utils import is_active_like
                    from flow.cli.utils.task_fetcher import TaskFetcher

                    fetcher = TaskFetcher(flow_client)
                    # Prioritize active tasks, large limit but efficient via batching/caching
                    from flow.cli.ui.presentation.animated_progress import (
                        AnimatedEllipsisProgress as _AEP,
                    )

                    with _AEP(console, "Loading tasks", start_immediately=True):
                        tasks = [
                            t for t in fetcher.fetch_for_resolution(limit=1000) if is_active_like(t)
                        ]
                    if not tasks:
                        console.print("[warning]No eligible tasks available.[/warning]")
                        console.print("\nStart a task with: [accent]flow run[/accent]")
                        return

                    # Lightweight preview to keep UX informative without per-item network fetches
                    from rich.markup import escape as _escape

                    def _fast_preview(item):  # type: ignore[override]
                        try:
                            t = getattr(item, "value", None)
                            title = _escape(
                                getattr(t, "name", None) or getattr(item, "title", "Task")
                            )
                            lines = [f"<b>{title}</b>"]
                            lines.append(
                                f"ID: {_escape(getattr(item, 'id', '') or getattr(t, 'task_id', ''))}"
                            )
                            # Status
                            try:
                                if getattr(item, "status", None):
                                    status_str = (
                                        str(item.status).replace("TaskStatus.", "").capitalize()
                                    )
                                    lines.append(f"Status: {status_str}")
                            except Exception:
                                pass
                            # GPU summary
                            try:
                                it = getattr(t, "instance_type", None) or (
                                    getattr(item, "extra", {}) or {}
                                ).get("instance_type")
                                ni = int(getattr(t, "num_instances", 1) or 1)
                                if it:
                                    try:
                                        from flow.cli.ui.formatters import GPUFormatter as _GF
                                    except Exception:
                                        from flow.cli.ui.facade import GPUFormatter as _GF

                                    gpu_disp = _GF.format_ultra_compact(it, ni)
                                    lines.append(f"GPU: {gpu_disp}")
                            except Exception:
                                pass
                            # Region
                            try:
                                region = (getattr(item, "extra", {}) or {}).get(
                                    "region"
                                ) or getattr(t, "region", None)
                                if region:
                                    lines.append(f"Region: {region}")
                            except Exception:
                                pass
                            # Created age (best-effort)
                            try:
                                from datetime import datetime
                                from datetime import timezone as _tz

                                created_at = getattr(t, "created_at", None)
                                if created_at:
                                    if getattr(created_at, "tzinfo", None) is None:
                                        created_at = created_at.replace(tzinfo=_tz.utc)
                                    delta = datetime.now(_tz.utc) - created_at
                                    mins = int(delta.total_seconds() // 60)
                                    pretty = f"{mins}m" if mins < 120 else f"{mins//60}h"
                                    lines.append(f"Created: {pretty} ago")
                            except Exception:
                                pass
                            return "\n".join(lines)
                        except Exception:
                            return ""

                    selected_task = select_task(
                        tasks,
                        title="Select a task to mount to",
                        allow_multiple=False,
                        show_preview=True,
                        preferred_viewport_size=8,
                        preview_renderer=_fast_preview,
                    )
                    if not selected_task:
                        console.print("[warning]No task selected.[/warning]")
                        return
                    task_id = selected_task.task_id

                # Resolve volume (skip if we already have it from interactive selection)
                if selected_volume:
                    volume = selected_volume
                    volume_display = get_volume_display_name(volume)
                else:
                    with AnimatedEllipsisProgress(
                        console, "Resolving volume", start_immediately=True
                    ) as progress:
                        volume, volume_error = resolve_volume_identifier(flow_client, volume_id)
                        if volume_error:
                            from flow.cli.utils.theme_manager import theme_manager as _tm

                            console.print(
                                f"[{_tm.get_color('error')}]Error:[/{_tm.get_color('error')}] {volume_error}"
                            )
                            return
                        volume_display = get_volume_display_name(volume)

                # Resolve task (skip if we already have it from interactive selection)
                if selected_task:
                    task = selected_task
                    task_display = task.name or task.task_id
                else:
                    with AnimatedEllipsisProgress(
                        console, "Resolving task", start_immediately=True
                    ) as progress:
                        task, task_error = resolve_task_identifier(flow_client, task_id)
                        if task_error:
                            from flow.cli.utils.theme_manager import theme_manager as _tm

                            console.print(
                                f"[{_tm.get_color('error')}]Error:[/{_tm.get_color('error')}] {task_error}"
                            )
                            return
                        task_display = task.name or task.task_id

                # Validate mount point if provided
                validated_mount_point = None
                if mount_point:
                    try:
                        validated_mount_point = self.validate_mount_point(mount_point)
                    except ValidationError as e:
                        from rich.markup import escape

                        from flow.cli.utils.theme_manager import theme_manager as _tm

                        console.print(
                            f"[{_tm.get_color('error')}]Error:[/{_tm.get_color('error')}] {escape(str(e))}"
                        )
                        return

                # Show what we're about to mount (compact, legible)
                def _short_id(s: str | None) -> str:
                    if not s:
                        return ""
                    return s if len(s) <= 12 else f"{s[:6]}…{s[-4:]}"

                compact_volume = (
                    f"{(volume.name or volume.id)} · {_short_id(volume.id)}"
                    if getattr(volume, "id", None)
                    else (volume.name or "(unknown)")
                )
                compact_task = (
                    f"{(task.name or task.task_id)} · {_short_id(task.task_id)}"
                    if getattr(task, "task_id", None)
                    else (task.name or "(unknown)")
                )

                console.print("")
                console.print(f"Mounting volume [accent]{compact_volume}[/accent]")
                console.print(f"To task        [accent]{compact_task}[/accent]")

                # Multi-instance check
                num_instances = getattr(
                    task, "num_instances", len(task.instances) if hasattr(task, "instances") else 1
                )
                if num_instances > 1:
                    # Check if volume is a file share (supports multi-instance)
                    is_file_share = hasattr(volume, "interface") and volume.interface == "file"

                    if is_file_share:
                        console.print(
                            f"[success]✓[/success] File share volume can be mounted to all {num_instances} instances"
                        )
                    else:
                        # Block storage cannot be multi-attached
                        from flow.cli.utils.theme_manager import theme_manager as _tm

                        console.print(
                            f"[{_tm.get_color('error')}]Error:[/{_tm.get_color('error')}] Cannot mount block storage to multi-instance task ({num_instances} nodes)"
                        )
                        console.print(
                            "[warning]Suggestion:[/warning] Use file storage (--type file) for multi-instance tasks"
                        )
                        console.print("\nOptions:")
                        console.print(
                            "  • Create a file share volume: [accent]flow volumes create --interface file --size 100[/accent]"
                        )
                        console.print(
                            "  • Use an existing file share: [accent]flow volumes get | grep file[/accent]"
                        )
                        console.print("  • Mount to a single-instance task instead")
                        return

                # Check task status using provider-agnostic resolver
                status_str = get_status_string(task)
                if status_str not in ["running", "active"]:
                    console.print(
                        f"[warning]Note:[/warning] Task is {status_str}. The attachment will complete now; the mount will finalize when the task is ready (SSH available)."
                    )
                else:
                    # Provider-specific warning for live mounts
                    try:
                        provider_name = getattr(
                            getattr(flow_client, "config", None), "provider", None
                        ) or (os.environ.get("FLOW_PROVIDER") or "mithril")
                    except Exception:
                        provider_name = os.environ.get("FLOW_PROVIDER", "mithril")
                    provider_name = str(provider_name).lower()

                    if provider_name == "mithril":
                        console.print("")
                        console.print("[warning]Warning:[/warning]")
                        console.print("  • Briefly pauses the VM to attach the device")
                        console.print(
                            "  • Ephemeral data not on a volume (e.g., /tmp, container scratch, in-memory) will be lost"
                        )
                        console.print(
                            "  • Prefer specifying volumes at creation (e.g., [accent]flow run --mount ...[/accent])"
                        )
                    else:
                        console.print("")
                        console.print("[warning]Warning:[/warning]")
                        console.print(
                            "  • Mounting to a running instance may pause or require recreation"
                        )
                        console.print(
                            "  • Ephemeral data not on volumes may be lost; prefer mounting at creation"
                        )

                # Determine mount path
                if validated_mount_point:
                    actual_mount_path = validated_mount_point
                else:
                    actual_mount_path = f"/volumes/{volume.name or f'volume-{volume.id[-6:]}'}"

                # Dry run mode
                if dry_run:
                    console.print("\n[accent]DRY RUN - No changes will be made[/accent]")
                    console.print(
                        f"Would mount volume {_short_id(volume.id)} to task {_short_id(task.task_id)}"
                    )
                    if instance is not None:
                        console.print(f"Target instance: {instance}")
                    else:
                        console.print(f"Target instances: ALL ({num_instances} instances)")
                    console.print(f"Mount path: {actual_mount_path}")
                    if output_json:
                        from flow.cli.utils.json_output import print_json

                        print_json(
                            {
                                "status": "dry_run",
                                "volume_id": getattr(volume, "volume_id", None)
                                or getattr(volume, "id", None),
                                "volume_name": getattr(volume, "name", None),
                                "task_id": getattr(task, "task_id", None),
                                "task_name": getattr(task, "name", None),
                                "mount_path": actual_mount_path,
                                "instances": "all" if instance is None else instance,
                            }
                        )
                    return

                # Unified confirmation/info pane before attachment
                try:
                    from flow.cli.commands.feedback import feedback as _fb

                    details: list[str] = [
                        f"Volume: [accent]{compact_volume}[/accent]",
                        f"Task:   [accent]{compact_task}[/accent]",
                        f"Path:   [accent]{actual_mount_path}[/accent]",
                    ]
                    if status_str in ["running", "active"]:
                        details.append(
                            "[warning]Note:[/warning] Attaching to a running VM may briefly pause it; ephemeral data not on volumes can be lost."
                        )
                    _fb.info("\n".join(details), title="Confirm mount", neutral_body=True)
                except Exception:
                    pass

                # Confirm risky live attach if task is running/active
                if status_str in ["running", "active"] and not yes:
                    if not click.confirm("Proceed with mount?", default=False):
                        console.print("[dim]Mount aborted.[/dim]")
                        return

                # Perform the attachment
                # Create timeline for mount operation
                timeline = StepTimeline(
                    console,
                    title=f"Mounting {_short_id(volume.id)} → {_short_id(task.task_id)}",
                    enable_animations=True,
                )

                # Single step: attach to task configuration
                attach_idx = timeline.add_step("Attaching volume to task configuration")

                timeline.start()
                # Mark the step active before setting the hint so it renders
                timeline.start_step(attach_idx)

                # Add Ctrl+C hint
                from rich.text import Text

                from flow.cli.utils.theme_manager import theme_manager

                hint_color = theme_manager.get_color("muted")
                accent = theme_manager.get_color("accent")
                hint = Text()
                hint.append("  Press ")
                hint.append("Ctrl+C", style=accent)
                hint.append(
                    " to cancel. Volume attachment will continue in background if interrupted."
                )
                timeline.set_active_hint_text(hint)

                try:
                    # Step 1: Attach volume (updates task configuration)
                    try:
                        # Instance-specific mounting is not implemented yet
                        if instance is not None:
                            raise ValidationError("Instance-specific mounting is not yet supported")

                        # Pass custom mount point if provided; check provider result
                        # Temporarily suppress noisy provider logs to keep UX readable
                        import logging as _logging

                        _prov_logger = _logging.getLogger(
                            "flow.adapters.providers.builtin.mithril.provider.facets.storage"
                        )
                        _prev_level = getattr(_prov_logger, "level", None)
                        try:
                            # Only suppress provider facet logs when not verbose
                            if not verbose:
                                try:
                                    _prov_logger.setLevel(_logging.CRITICAL)
                                except Exception:
                                    pass
                            if validated_mount_point:
                                ok = flow_client.volumes.mount(
                                    volume.id, task.task_id, mount_point=validated_mount_point
                                )
                            else:
                                ok = flow_client.volumes.mount(volume.id, task.task_id)
                        finally:
                            try:
                                if _prev_level is not None:
                                    _prov_logger.setLevel(_prev_level)
                            except Exception:
                                pass

                        if not ok:
                            raise RemoteExecutionError(
                                "Provider did not confirm attachment (no changes were applied)"
                            )

                        timeline.complete_step()

                    except ValidationError as e:
                        timeline.fail_step(str(e))
                        timeline.finish()
                        from rich.markup import escape

                        from flow.cli.utils.theme_manager import theme_manager as _tm

                        console.print(
                            f"\n[{_tm.get_color('error')}]Validation Error:[/{_tm.get_color('error')}] {escape(str(e))}"
                        )
                        return
                    except RemoteExecutionError as e:
                        timeline.fail_step("Mount execution failed")
                        timeline.finish()
                        from rich.markup import escape

                        from flow.cli.utils.theme_manager import theme_manager as _tm

                        console.print(
                            f"\n[{_tm.get_color('error')}]Mount Failed:[/{_tm.get_color('error')}] {escape(str(e))}"
                        )
                        console.print("\n[warning]Troubleshooting:[/warning]")
                        console.print("  - Ensure the task is ready (SSH available)")
                        console.print("  - Check that the volume is not already mounted")
                        console.print("  - Verify region compatibility")
                        return
                    except KeyboardInterrupt:
                        timeline.fail_step("Cancelled by user")
                        timeline.finish()
                        console.print("\n[warning]Mount operation cancelled.[/warning]")
                        console.print("Volume attachment may continue in background.")
                        console.print(
                            f"Check status with: [accent]flow status {task_display}[/accent]"
                        )
                        return

                finally:
                    timeline.finish()

                # Success - use the actual mount path we determined earlier
                mount_path = actual_mount_path

                console.print()  # Add spacing after timeline

                # Determine post-attach guidance based on task status
                if status_str in ["pending", "starting", "initializing", "provisioning"]:
                    console.print(
                        "[success]✓[/success] Volume attached to task. Mount will complete when the task is ready."
                    )
                    console.print(
                        f"\n[warning]Note:[/warning] Task is still starting. The volume will be available at "
                        f"[accent]{mount_path}[/accent] once the task starts."
                    )
                    console.print(f"Mount path: [accent]{mount_path}[/accent]")
                    if output_json and not wait:
                        from flow.cli.utils.json_output import print_json

                        print_json(
                            {
                                "status": "attached",
                                "deferred": True,
                                "volume_id": getattr(volume, "volume_id", None)
                                or getattr(volume, "id", None),
                                "volume_name": getattr(volume, "name", None),
                                "task_id": getattr(task, "task_id", None),
                                "task_name": getattr(task, "name", None),
                                "mount_path": mount_path,
                            }
                        )
                        return
                    console.print(
                        "\nMithril instances can take several minutes to start. To check status:"
                    )
                    task_ref = task.name or task.task_id
                    if wait:
                        # Wait for SSH, then poll for mount availability with unified hint
                        try:
                            from flow.cli.utils.step_progress import (
                                SSHWaitProgressAdapter as _SSHAdapter,
                            )
                            from flow.cli.utils.step_progress import (
                                StepTimeline as _Timeline,
                            )
                            from flow.cli.utils.step_progress import (
                                build_provisioning_hint as _bph,
                            )
                            from flow.sdk.ssh_utils import DEFAULT_PROVISION_MINUTES as _DEF_PROV

                            # Seed baseline from instance age when available
                            try:
                                baseline = int(getattr(task, "instance_age_seconds", None) or 0)
                            except Exception:
                                baseline = 0

                            _tl = _Timeline(console, title="flow mount", title_animation="auto")
                            _tl.start()
                            step_idx = _tl.add_step(
                                f"Provisioning instance (up to {_DEF_PROV}m)",
                                show_bar=True,
                                estimated_seconds=_DEF_PROV * 60,
                                baseline_elapsed_seconds=baseline,
                            )
                            adapter = _SSHAdapter(
                                _tl, step_idx, _DEF_PROV * 60, baseline_elapsed_seconds=baseline
                            )
                            with adapter:
                                # Compose hint + volume context addendum under active step
                                try:
                                    hint = _bph("instance", "flow mount")
                                    hint.append("\n")
                                    hint.append(
                                        "  Volume is already attached; it becomes available when the instance is ready."
                                    )
                                    _tl.set_active_hint_text(hint)
                                except Exception:
                                    pass
                                task = flow_client.wait_for_ssh(
                                    task.task_id,
                                    timeout=_DEF_PROV * 60,
                                    show_progress=False,
                                    progress_adapter=adapter,
                                )
                            _tl.finish()
                        except Exception:
                            flow_client.wait_for_ssh(task.task_id, timeout=900, show_progress=False)
                            # Verify presence with a short polling window to allow startup scripts
                            try:
                                remote_ops = flow_client.get_remote_operations()
                            except Exception:
                                remote_ops = None
                            mounted = False
                            if remote_ops is not None:
                                import time as _time

                                for _ in range(24):  # ~2 minutes @5s
                                    try:
                                        result = remote_ops.execute_command(
                                            task.task_id,
                                            f"mountpoint -q {mount_path} && echo MOUNTED || echo NOT_MOUNTED",
                                            timeout=10,
                                        )
                                        if "MOUNTED" in (result or ""):
                                            mounted = True
                                            break
                                    except Exception:
                                        pass
                                    _time.sleep(5)
                            if mounted:
                                console.print(
                                    f"[success]✓[/success] Mounted at [accent]{mount_path}[/accent]"
                                )
                                if output_json:
                                    from flow.cli.utils.json_output import print_json

                                    print_json(
                                        {
                                            "status": "mounted",
                                            "deferred": False,
                                            "volume_id": getattr(volume, "volume_id", None)
                                            or getattr(volume, "id", None),
                                            "volume_name": getattr(volume, "name", None),
                                            "task_id": getattr(task, "task_id", None),
                                            "task_name": getattr(task, "name", None),
                                            "mount_path": mount_path,
                                            "verified": True,
                                        }
                                    )
                                    return
                                if persist and remote_ops is not None:
                                    try:
                                        persist_cmd = (
                                            "entry=$(awk '$2==\""
                                            + mount_path
                                            + '" {print $1" "$2" "$3" "$4" 0 0"}\' /proc/mounts); '
                                            'if [ -n "$entry" ]; then echo "$entry" | sudo tee -a /etc/fstab >/dev/null && sudo mount -a && echo PERSISTED; else echo NOENTRY; fi'
                                        )
                                        remote_ops.execute_command(
                                            task.task_id, persist_cmd, timeout=20
                                        )
                                    except Exception:
                                        pass
                            else:
                                self.show_next_actions(
                                    [
                                        f"Verify mount: [accent]flow ssh {task_ref} -c 'df -h {mount_path}'[/accent]",
                                    ],
                                    title="Verification / fallback",
                                )
                        except KeyboardInterrupt:
                            console.print(
                                "\n[dim]Stopped waiting. The volume is attached to the task configuration.[/dim]"
                            )
                            self.show_next_actions(
                                [
                                    f"Verify later: [accent]flow ssh {task_ref} -c 'df -h {mount_path}'[/accent]",
                                ],
                                title="Verification / fallback",
                            )
                            return
                        except Exception:
                            self.show_next_actions(
                                [
                                    f"Check task status: [accent]flow status {task_ref}[/accent]",
                                    f"Wait for SSH and verify: [accent]flow ssh {task_ref} -c 'df -h {mount_path}'[/accent]",
                                    f"Stream startup logs: [accent]flow logs {task_ref} -f[/accent]",
                                ],
                                title="Verification / fallback",
                            )
                    else:
                        self.show_next_actions(
                            [
                                f"Check task status: [accent]flow status {task_ref}[/accent]",
                                f"Wait for SSH and verify: [accent]flow ssh {task_ref} -c 'df -h {mount_path}'[/accent]",
                                f"Stream startup logs: [accent]flow logs {task_ref} -f[/accent]",
                            ],
                            title="Verification / fallback",
                        )
                elif status_str == "paused":
                    console.print("[success]✓[/success] Volume attached to task configuration.")
                    console.print(
                        "\n[warning]Next steps after resuming:[/warning] The instance may require a manual mount to make the volume accessible."
                    )
                    task_ref = task.name or task.task_id
                    console.print(f"Mount path: [accent]{mount_path}[/accent]")
                    self.show_next_actions(
                        [
                            "Resume the task (provider/UI)",
                            f"Mount inside instance: [accent]flow ssh {task_ref} -c 'sudo mkdir -p {mount_path} && sudo mount -a || true && (mountpoint -q {mount_path} && echo Mounted || echo Needs fstab)'[/accent]",
                            f"Verify: [accent]flow ssh {task_ref} -c 'df -h {mount_path} || ls -la {mount_path}'[/accent]",
                        ]
                    )
                    if output_json:
                        from flow.cli.utils.json_output import print_json

                        print_json(
                            {
                                "status": "attached",
                                "paused": True,
                                "volume_id": getattr(volume, "volume_id", None)
                                or getattr(volume, "id", None),
                                "volume_name": getattr(volume, "name", None),
                                "task_id": getattr(task, "task_id", None),
                                "task_name": getattr(task, "name", None),
                                "mount_path": mount_path,
                            }
                        )
                        return
                else:
                    # Running/active: attachment succeeded, mount may require manual steps
                    console.print("[success]✓[/success] Volume attached to task configuration.")
                    console.print(f"Mount path: [accent]{mount_path}[/accent]")
                    console.print(
                        "\n[warning]Note:[/warning] For already-booted instances, the mount may not be immediate. You may need to mount it manually or restart the instance."
                    )
                    task_ref = task.name or task.task_id
                    verified = False
                    if output_json and not wait:
                        from flow.cli.utils.json_output import print_json

                        print_json(
                            {
                                "status": "attached",
                                "volume_id": getattr(volume, "volume_id", None)
                                or getattr(volume, "id", None),
                                "volume_name": getattr(volume, "name", None),
                                "task_id": getattr(task, "task_id", None),
                                "task_name": getattr(task, "name", None),
                                "mount_path": mount_path,
                                "verified": False,
                            }
                        )
                        return
                    if wait:
                        # Verification can take minutes; use a timeline with bar and clear cancel hint
                        try:
                            try:
                                remote_ops = flow_client.get_remote_operations()
                            except Exception:
                                remote_ops = None
                            if remote_ops is None:
                                raise RuntimeError("remote-ops unavailable")

                            import time as _time

                            from rich.text import Text as _Text

                            from flow.cli.utils.step_progress import StepTimeline as _Timeline
                            from flow.sdk.ssh_utils import DEFAULT_PROVISION_MINUTES as _DEF_PROV

                            EST_SECS = int(_DEF_PROV) * 60
                            tl = _Timeline(console, title="flow mount", title_animation="auto")
                            tl.start()
                            step_idx = tl.add_step(
                                "Verifying mount (up to 5m)",
                                show_bar=True,
                                estimated_seconds=EST_SECS,
                            )
                            tl.start_step(step_idx)

                            # Hint: safe to cancel; attachment remains applied
                            hint = _Text()
                            from flow.cli.utils.theme_manager import theme_manager as _tm

                            hint.append("  Press ")
                            hint.append("Ctrl+C", style=_tm.get_color("accent"))
                            hint.append(
                                " to stop waiting. The volume is already attached; it becomes available when the instance completes mounting."
                            )
                            tl.set_active_hint_text(hint)

                            start = _time.monotonic()
                            interval = 5
                            while True:
                                try:
                                    result = remote_ops.execute_command(
                                        task.task_id,
                                        f"mountpoint -q {mount_path} && echo MOUNTED || echo NOT_MOUNTED",
                                        timeout=10,
                                    )
                                    if "MOUNTED" in (result or ""):
                                        verified = True
                                        tl.complete_step(note="Mounted")
                                        break
                                except Exception:
                                    pass

                                elapsed = _time.monotonic() - start
                                pct = min(0.95, max(0.0, elapsed / EST_SECS))
                                tl.update_active(percent=pct)
                                if elapsed >= EST_SECS:
                                    break
                                _time.sleep(interval)

                            try:
                                tl.finish()
                            except Exception:
                                pass

                            if verified:
                                console.print(
                                    f"[success]✓[/success] Mounted at [accent]{mount_path}[/accent]"
                                )
                                if output_json:
                                    from flow.cli.utils.json_output import print_json

                                    print_json(
                                        {
                                            "status": "mounted",
                                            "volume_id": getattr(volume, "volume_id", None)
                                            or getattr(volume, "id", None),
                                            "volume_name": getattr(volume, "name", None),
                                            "task_id": getattr(task, "task_id", None),
                                            "task_name": getattr(task, "name", None),
                                            "mount_path": mount_path,
                                            "verified": True,
                                        }
                                    )
                                    return
                                if persist and remote_ops is not None:
                                    try:
                                        persist_cmd = (
                                            "entry=$(awk '$2==\""
                                            + mount_path
                                            + '" {print $1" "$2" "$3" "$4" 0 0"}\' /proc/mounts); '
                                            'if [ -n "$entry" ]; then echo "$entry" | sudo tee -a /etc/fstab >/dev/null && sudo mount -a && echo PERSISTED; else echo NOENTRY; fi'
                                        )
                                        remote_ops.execute_command(
                                            task.task_id, persist_cmd, timeout=20
                                        )
                                    except Exception:
                                        pass
                        except KeyboardInterrupt:
                            try:
                                tl.fail_step("Cancelled by user")
                                tl.finish()
                            except Exception:
                                pass
                            console.print(
                                "\n[dim]Stopped waiting. The volume is attached to the task configuration.[/dim]"
                            )
                            self.show_next_actions(
                                [
                                    f"Verify later: [accent]flow ssh {task_ref} -c 'df -h {mount_path}'[/accent]",
                                ],
                                title="Verification / fallback",
                            )
                            return
                        except Exception:
                            pass
                    if not verified:
                        self.show_next_actions(
                            [
                                f"Verify mount: [accent]flow ssh {task_ref} -c 'df -h {mount_path}'[/accent]",
                            ],
                            title="Verification / fallback",
                        )

            except AuthenticationError:
                self.handle_auth_error()
            except ResourceNotFoundError as e:
                from rich.markup import escape

                from flow.cli.utils.theme_manager import theme_manager as _tm

                console.print(
                    f"[{_tm.get_color('error')}]Not Found:[/{_tm.get_color('error')}] {escape(str(e))}"
                )
            except Exception as e:
                self.handle_error(str(e))

        return mount


# Export command instance
command = MountCommand()
