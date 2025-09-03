"""Run command - submit GPU tasks from YAML or direct command.

This is the refactored version of run.py that integrates the clean architecture
components while maintaining full backward compatibility with existing code.

Migration notes:
- All original functionality preserved
- New components used internally for better maintainability
- Can be swapped in place of run.py with no breaking changes
"""

from __future__ import annotations

import json
import logging
import os
from contextlib import suppress
from typing import TYPE_CHECKING

import click

from flow.cli.commands.base import BaseCommand, console
from flow.cli.commands.input_types import EnvItem, PortNumber
from flow.cli.commands.messages import print_next_actions
from flow.cli.commands.utils import maybe_show_auto_status, wait_for_task
from flow.cli.services.task_submitter import TaskSubmissionError, TaskSubmitter
from flow.cli.utils.error_handling import cli_error_guard
from flow.cli.utils.icons import flow_icon
from flow.cli.utils.progress_tracking import RunProgressManager
from flow.cli.utils.run_helpers import RunHelpers
from flow.errors import AuthenticationError, ValidationError

# Back-compat: expose Flow symbol for tests that patch flow.cli.commands.run.Flow
# Avoid importing the heavy SDK client at module import time to keep the UI responsive.
# Tests that patch run.Flow will still work since we provide a placeholder symbol.
if TYPE_CHECKING:  # only for type checkers
    from flow.sdk.client import Flow as Flow  # pragma: no cover
    from flow.sdk.models import Task  # pragma: no cover
else:  # runtime placeholder to allow test patching without importing SDK now
    Flow = object  # type: ignore
    Task = object  # type: ignore

# Import refactored components from their proper locations
from flow.sdk.models.run_params import (
    DEFAULT_IMAGE,
    DEFAULT_PROVISION_TIMEOUT_MINUTES,
    DEFAULT_UPLOAD_FAILURE_POLICY,
    DEFAULT_UPLOAD_STRATEGY,
    DEFAULT_UPLOAD_TIMEOUT,
    MAX_PORT,
    MIN_HIGH_PORT,
    RunParameters,
)

logger = logging.getLogger(__name__)


class RunCommand(BaseCommand):
    """Submit a task from YAML configuration.

    This refactored version maintains full backward compatibility while
    using clean architecture components internally.
    """

    @property
    def name(self) -> str:
        return "run"

    @property
    def help(self) -> str:
        return """Submit a task from YAML configuration

Examples:
  flow run                         # Interactive GPU instance (default: 8xh100)
  flow run "nvidia-smi" -i h100    # Quick GPU test with specific instance
  flow run "python train.py"       # Run command directly
  flow run <config.yaml>           # Submit from config file
  flow run <config.yaml> --watch   # Watch progress interactively
  flow run "python -m http.server 8080" --port 8080  # Expose a service on port 8080

Notes:
- Command may be provided positionally (recommended) or via -c/--command
- Use --port (repeatable) to expose high ports (>=1024) on the instance's public IP
- No runtime limit is applied by default. To auto-terminate, set max_run_time_hours in your TaskConfig"""

    def get_command(self) -> click.Command:
        """Build the Click command with all options."""
        from flow.cli.ui.runtime.shell_completion import (
            complete_instance_types as _complete_instance_types,
        )
        from flow.cli.ui.runtime.shell_completion import (
            complete_ssh_key_identifiers as _complete_ssh_keys,
        )
        from flow.cli.ui.runtime.shell_completion import (
            complete_volume_ids as _complete_volume_ids,
        )
        from flow.cli.ui.runtime.shell_completion import (
            complete_yaml_files as _complete_yaml_files,
        )

        @click.command(name=self.name, help=self.help)
        @click.argument("config_file", required=False, shell_complete=_complete_yaml_files)
        @click.argument("extra_args", nargs=-1)
        @click.option(
            "--instance-type",
            "-i",
            help="GPU instance type (e.g., a100, 8xa100, h100)",
            shell_complete=_complete_instance_types,
        )
        @click.option("--region", "-r", help="Preferred region (e.g., us-central1-b)")
        @click.option(
            "--ssh-keys",
            "-k",
            multiple=True,
            help="Authorized SSH keys (repeatable)",
            shell_complete=_complete_ssh_keys,
        )
        @click.option(
            "--image",
            default=DEFAULT_IMAGE,
            help=f"Docker image to use (default: {DEFAULT_IMAGE})",
        )
        @click.option("--name", "-n", help="Task name (default: auto-generated)")
        @click.option("--no-unique", is_flag=True, help="Don't append unique suffix to task name")
        @click.option("--command", "-c", help="Command to run (deprecated)", hidden=True)
        @click.option(
            "--priority",
            "-p",
            type=click.Choice(["low", "med", "high"], case_sensitive=False),
            help="Task priority (low/med/high)",
        )
        @click.option("--on-name-conflict", type=click.Choice(["error", "suffix"]), default=None)
        @click.option("--force-new", is_flag=True, help="Alias for --on-name-conflict=suffix")
        @click.option("--wait/--no-wait", default=True, help="Wait for task to start running")
        @click.option(
            "--dry-run", "-d", is_flag=True, help="Validate configuration without submitting"
        )
        @click.option("--watch", "-w", is_flag=True, help="Watch task progress interactively")
        @click.option("--json", "output_json", is_flag=True, help="Output JSON for automation")
        @click.option(
            "--allocation",
            type=click.Choice(["spot", "reserved", "auto"]),
            default=None,
            hidden=True,
        )
        @click.option("--reservation-id", default=None, hidden=True)
        @click.option("--start", "start_time", default=None, hidden=True)
        @click.option("--duration", "duration_hours", type=int, default=None, hidden=True)
        @click.option(
            "--env",
            "env_items",
            type=EnvItem(),
            multiple=True,
            help="Environment variables KEY=VALUE (repeatable)",
        )
        @click.option("--pricing", is_flag=True, help="Show pricing details in the config table")
        @click.option("--compact", is_flag=True, help="Compact table output")
        @click.option("--slurm", is_flag=True, help="Treat input as a SLURM script")
        @click.option(
            "--mount",
            multiple=True,
            help="Mount storage (format: source or target=source)",
            shell_complete=_complete_volume_ids,
        )
        @click.option(
            "--port",
            type=PortNumber(min_port=MIN_HIGH_PORT, max_port=MAX_PORT),
            multiple=True,
            help=f"Expose a port (repeatable). High ports only (>={MIN_HIGH_PORT}).",
        )
        @click.option(
            "--upload-strategy",
            type=click.Choice(["auto", "embedded", "scp", "none"]),
            default=DEFAULT_UPLOAD_STRATEGY,
            help=f"Code upload strategy: {DEFAULT_UPLOAD_STRATEGY} (default), embedded, scp, or none",
        )
        @click.option(
            "--upload-timeout",
            type=int,
            default=DEFAULT_UPLOAD_TIMEOUT,
            help=f"Upload timeout in seconds (default: {DEFAULT_UPLOAD_TIMEOUT})",
        )
        @click.option(
            "--code-root", type=str, default=None, help="Local project directory to upload"
        )
        @click.option(
            "--on-upload-failure",
            type=click.Choice(["continue", "fail"], case_sensitive=False),
            default=DEFAULT_UPLOAD_FAILURE_POLICY,
            help=f"Policy when code upload fails: {DEFAULT_UPLOAD_FAILURE_POLICY} (default) or fail",
        )
        @click.option("--max-price-per-hour", "-m", type=float, help="Maximum hourly price in USD")
        @click.option("--num-instances", "-N", type=int, default=1, help="Number of instances")
        @click.option(
            "--distributed",
            type=click.Choice(["auto", "manual"], case_sensitive=False),
            help="Distributed rendezvous mode",
        )
        @click.option("--verbose", "-v", is_flag=True, help="Show detailed configuration guide")
        @cli_error_guard(self)
        def run(**kwargs) -> None:
            """Click command handler."""
            # Show verbose help if requested
            if (
                kwargs.get("verbose")
                and not kwargs.get("config_file")
                and not kwargs.get("command")
            ):
                self._show_verbose_help()
                return

            # Convert to RunParameters
            params = self._build_parameters(kwargs)

            # Execute with new architecture
            self._execute_v2(params)

        return run

    def _execute(self, *args, **kwargs) -> None:
        """Legacy execute method for backward compatibility.

        This wrapper allows existing code to call _execute with the old signature
        while internally using the new clean architecture.
        """
        # Build parameters from legacy arguments
        params = self._build_parameters_from_legacy(*args, **kwargs)
        self._execute_v2(params)

    def _execute_v2(self, params: RunParameters) -> None:
        """Execute the run command using clean architecture.

        This is the new, clean implementation that uses our refactored components.
        """
        # Lazy import to avoid CLI→core dependency at module import time
        from flow.cli.utils.lazy_imports import import_attr as _import_attr

        ConfigurationError = _import_attr(
            "flow.application.config.run_loader", "ConfigurationError", default=Exception
        )
        TaskConfigLoader = _import_attr(
            "flow.application.config.run_loader", "TaskConfigLoader", default=None
        )
        # Validate parameters
        if (
            params.allocation_mode
            or params.reservation_id
            or params.start_time
            or params.duration_hours
        ):
            self.handle_error(
                "Reservations support is coming soon. The flags --allocation/--reservation-id/"
                "--start/--duration are temporarily disabled."
            )
            return

        try:
            params.validate()
        except ValueError as e:
            self.handle_error(str(e))
            return

        # Initialize components
        if TaskConfigLoader is None:
            self.handle_error("Run configuration loader is unavailable in this environment.")
            return
        loader = TaskConfigLoader()
        progress = RunProgressManager(None, console)

        try:
            # Start progress tracking
            progress.start_timeline(params)

            # Load configuration
            config, configs = loader.load(params)

            # Display configuration
            RunHelpers.display_configs_and_mounts(config, configs, params, console)

            # Handle dry run
            if params.execution.dry_run:
                RunHelpers.emit_dry_run_output(config, configs, params, console)
                return

            # Validate SSH keys (non-fatal; warn when absent)
            effective_config = config if config else configs[0] if configs else None
            if effective_config:
                keys = RunHelpers.preflight_ssh_keys(effective_config)
                if not params.execution.output_json and not keys:
                    from flow.cli.utils.theme_manager import theme_manager as _tm

                    warn = _tm.get_color("warning")
                    console.print(
                        f"\n[{warn}]No SSH keys configured[/{warn}] — proceeding without SSH access. "
                        f"Add later with: flow ssh-keys upload ~/.ssh/id_ed25519.pub"
                    )

            # Real provider guard (interactive safety prompt for real providers)
            if not params.execution.output_json:
                guard_vals = RunHelpers.real_provider_guard_values(config, configs)
                try:
                    from flow.cli.utils.real_provider_guard import ensure_real_provider_ack

                    acknowledged = ensure_real_provider_ack(
                        instance_type=guard_vals.get("instance_type"),
                        priority=guard_vals.get("priority"),
                        max_price_per_hour=guard_vals.get("max_price_per_hour"),
                        num_instances=int(guard_vals.get("num_instances", 1) or 1),
                        auto_confirm=False,
                    )
                    if not acknowledged:
                        return
                except Exception:
                    # Never block on guard failures; proceed
                    pass

            # Initialize client and submit (lazy import to avoid cold-start delay before progress)
            from flow.sdk.factory import create_client  # local import

            client = create_client(auto_init=True)
            progress.client = client
            submitter = TaskSubmitter(client)

            # Submit task(s) with an explicit timeline step for immediate feedback
            if progress.timeline:
                # Show a non-bar step so users see activity right away
                submit_idx = progress.timeline.add_step("Submitting task", show_bar=False)
                progress.timeline.start_step(submit_idx)
                try:
                    task, tasks = submitter.submit(config, configs, params)
                    progress.timeline.complete_step()
                except Exception:
                    # Mark failure before surfacing the error
                    try:
                        progress.timeline.complete_step(note="Failed")
                    except Exception:
                        pass
                    raise
            else:
                task, tasks = submitter.submit(config, configs, params)

            # Print task IDs
            if not params.execution.output_json:
                if task:
                    console.print(f"Task ID: [accent]{task.task_id}[/accent]")
                elif tasks:
                    for t in tasks:
                        console.print(
                            f"Task ID: [accent]{t.task_id}[/accent] ([dim]{t.name}[/dim])"
                        )

            # Invalidate caches
            RunHelpers.invalidate_caches()

            # Handle post-submission
            if tasks:
                self._handle_array_submission(tasks, params)
            else:
                self._handle_single_submission(task, params, progress)

        except AuthenticationError:
            self.handle_auth_error()
        except (ConfigurationError, TaskSubmissionError, ValidationError) as e:
            self.handle_error(str(e))
        except click.exceptions.Exit:
            raise
        except Exception as e:
            logger.exception("Unexpected error in run command")
            self.handle_error(str(e))
        finally:
            progress.finish_timeline()

    def _handle_array_submission(self, tasks: list[Task], params: RunParameters) -> None:
        """Handle post-submission for array jobs."""
        if params.execution.output_json:
            result = {
                "status": "submitted",
                "tasks": [{"task_id": t.task_id, "name": t.name} for t in tasks],
            }
            console.print(json.dumps(result))
        else:
            console.print(
                f"\nSubmitted {len(tasks)} tasks. Use filters by name to operate on the set."
            )
            print_next_actions(
                console,
                [
                    "List tasks: [accent]flow status --all[/accent]",
                    "Cancel by name pattern: [accent]flow cancel -n '<prefix>*'[/accent]",
                ],
            )

    def _handle_single_submission(
        self, task: Task, params: RunParameters, progress: RunProgressManager
    ) -> None:
        """Handle post-submission for single task."""
        if params.execution.output_json:
            self._handle_json_output(task, params, progress)
            return

        if not params.execution.wait:
            self._handle_no_wait(task)
            return

        # Wait for task to start
        status = progress.track_allocation(task, params)

        if status == "running":
            # Handle SSH wait and code upload if needed
            if params.upload.is_cli_managed:
                task = progress.track_ssh_wait(task, DEFAULT_PROVISION_TIMEOUT_MINUTES)
                progress.track_code_upload(task, params.upload)

            # Check for background upload status
            self._check_background_upload_status(task)

        # Show completion message
        progress.show_completion_message(task, status, params)

        # Show status snapshot
        if status == "running":
            try:
                task_ref = task.name or task.task_id
                maybe_show_auto_status(focus=task_ref, reason="After launch", show_all=False)
            except Exception:
                pass

    def _handle_json_output(
        self, task: Task, params: RunParameters, progress: RunProgressManager
    ) -> None:
        """Handle JSON output mode."""
        from flow.cli.utils.json_output import print_json, task_to_json

        result: dict[str, object] = {"task_id": task.task_id, "status": "submitted"}

        if params.execution.wait:
            status = wait_for_task(
                progress.client, task.task_id, watch=False, json_output=True, task_name=task.name
            )
            result["status"] = status

            # Get full task details in normalized JSON shape
            task_details = progress.client.get_task(task.task_id)
            result["task"] = task_to_json(task_details)

        print_json(result)

    def _handle_no_wait(self, task: Task) -> None:
        """Handle no-wait mode."""
        task_ref = task.name or task.task_id

        if task.name:
            console.print(f"\nTask submitted: [accent]{task.name}[/accent]")
        else:
            console.print(f"\nTask submitted with ID: [accent]{task.task_id}[/accent]")

        print_next_actions(
            console,
            [
                f"Check task status: [accent]flow status {task_ref}[/accent]",
                f"Stream logs: [accent]flow logs {task_ref} --follow[/accent]",
                f"Cancel if needed: [accent]flow cancel {task_ref}[/accent]",
            ],
        )

        # Show status snapshot
        try:
            maybe_show_auto_status(focus=task_ref, reason="After submission", show_all=False)
        except Exception:
            pass

    def _check_background_upload_status(self, task: Task) -> None:
        """Check and report background upload status."""
        task_ref = task.name or task.task_id

        # Check for pending upload
        if getattr(task, "_upload_pending", False):
            from flow.cli.utils.theme_manager import theme_manager

            muted = theme_manager.get_color("muted")
            console.print(
                f"[{muted}]Code upload will run in background. "
                f"If it fails, sync manually with: flow upload-code {task_ref}[/{muted}]"
            )

        # Check for failed upload
        if getattr(task, "_upload_failed", False):
            err = getattr(task, "_upload_error", "") or "code upload failed"
            from flow.cli.utils.theme_manager import theme_manager

            warn = theme_manager.get_color("warning")
            accent = theme_manager.get_color("accent")
            console.print(
                f"[{warn}]Background code upload failed[/{warn}]: {err}. "
                f"Sync manually with: [{accent}]flow upload-code {task_ref}[/{accent}]"
            )

    def _build_parameters(self, kwargs: dict) -> RunParameters:
        """Build RunParameters from Click arguments."""
        # Parse command from positional arguments
        config_file, inline_cmd = RunHelpers.parse_positionals(
            kwargs.get("config_file"), kwargs.get("extra_args", ()), kwargs.get("command")
        )
        command = " ".join(inline_cmd) if inline_cmd else kwargs.get("command")

        # Parse mounts
        mounts = self._parse_mounts(kwargs.get("mount", ()))

        # Determine SLURM mode
        is_slurm = kwargs.get("slurm", False)
        if not is_slurm and config_file:
            is_slurm = RunHelpers.detect_slurm_from_path(config_file)

        # Build parameters
        return RunParameters.from_click_params(
            config_file=config_file,
            command=command,
            is_slurm=is_slurm,
            instance_type=kwargs.get("instance_type"),
            region=kwargs.get("region"),
            ssh_keys=kwargs.get("ssh_keys", ()),
            image=kwargs.get("image", DEFAULT_IMAGE),
            name=kwargs.get("name"),
            no_unique=kwargs.get("no_unique", False),
            priority=kwargs.get("priority"),
            wait=kwargs.get("wait", True),
            dry_run=kwargs.get("dry_run", False),
            watch=kwargs.get("watch", False),
            output_json=kwargs.get("output_json", False),
            on_name_conflict=kwargs.get("on_name_conflict"),
            force_new=kwargs.get("force_new", False),
            env_items=kwargs.get("env_items", ()),
            port=kwargs.get("port", ()),
            mount=mounts,
            upload_strategy=kwargs.get("upload_strategy", DEFAULT_UPLOAD_STRATEGY),
            upload_timeout=kwargs.get("upload_timeout", DEFAULT_UPLOAD_TIMEOUT),
            code_root=kwargs.get("code_root"),
            on_upload_failure=kwargs.get("on_upload_failure", DEFAULT_UPLOAD_FAILURE_POLICY),
            max_price_per_hour=kwargs.get("max_price_per_hour"),
            num_instances=kwargs.get("num_instances", 1),
            distributed=kwargs.get("distributed"),
            pricing=kwargs.get("pricing", False),
            compact=kwargs.get("compact", False),
            verbose=kwargs.get("verbose", False),
            allocation=kwargs.get("allocation"),
            reservation_id=kwargs.get("reservation_id"),
            start_time=kwargs.get("start_time"),
            duration_hours=kwargs.get("duration_hours"),
        )

    def _build_parameters_from_legacy(self, *args, **kwargs) -> RunParameters:
        """Build RunParameters from legacy _execute arguments.

        This maintains backward compatibility with existing code that calls
        _execute directly with positional arguments.
        """
        # Map positional arguments to kwargs if provided
        if args:
            arg_names = [
                "config_file",
                "instance_type",
                "region",
                "ssh_keys",
                "image",
                "name",
                "no_unique",
                "priority",
                "wait",
                "dry_run",
                "watch",
                "output_json",
                "env_items",
                "mount",
                "port",
                "upload_strategy",
                "upload_timeout",
                "code_root",
                "on_upload_failure",
                "command",
                "extra_args",
                "max_price_per_hour",
                "num_instances",
                "slurm",
                "show_pricing",
                "compact",
                "on_name_conflict",
                "force_new",
                "distributed",
                "allocation",
                "reservation_id",
                "start_time",
                "duration_hours",
            ]
            for i, arg in enumerate(args):
                if i < len(arg_names):
                    kwargs[arg_names[i]] = arg

        return self._build_parameters(kwargs)

    def _parse_mounts(self, mount_specs: tuple[str, ...]) -> dict[str, str]:
        """Parse mount specifications into dictionary."""
        if not mount_specs:
            return {}

        # Prefer centralized core mounts parser when available to ensure
        # consistent target resolution and validation across CLI and SDK.
        try:
            from flow.core.mounts.parser import MountParser  # type: ignore

            parser = MountParser()
            parsed = parser.parse_mounts(mount_specs)
            return parsed or {}
        except Exception:
            pass

        provider_name = os.environ.get("FLOW_PROVIDER", "mithril").lower()
        from flow.plugins import registry as plugin_registry

        mounts = {}
        for spec in mount_specs:
            if "=" in spec:
                target, source = spec.split("=", 1)
            else:
                source = spec
                # Prefer provider-specific rule if available via entry-point manifest
                try:
                    ProviderClass = plugin_registry.get_provider(provider_name)
                    if ProviderClass and hasattr(ProviderClass, "resolve_mount_target"):
                        target = ProviderClass.resolve_mount_target(source)  # type: ignore[attr-defined]
                    else:
                        # Core rule if available; fallback to local heuristic
                        try:
                            from flow.core.mount_rules import auto_target_for_source as _auto

                            target = _auto(source)
                        except Exception:
                            target = self._auto_target_for_source(source)
                except Exception:
                    try:
                        from flow.core.mount_rules import auto_target_for_source as _auto

                        target = _auto(source)
                    except Exception:
                        target = self._auto_target_for_source(source)
            mounts[target] = source

        return mounts

    @staticmethod
    def _auto_target_for_source(source: str) -> str:
        """Heuristic fallback for mount target when provider doesn't supply one.

        Rules:
          - volume://NAME -> /mnt/volume/NAME
          - s3://bucket/path -> /mnt/s3/bucket/path
          - /abs/path or file:// -> /mnt/data/<basename>
          - anything else -> /mnt/data
        """
        try:
            s = str(source or "").strip()
            if s.startswith("volume://"):
                name = s[len("volume://") :].strip("/") or "volume"
                return f"/mnt/volume/{name}"
            if s.startswith("s3://"):
                rest = s[len("s3://") :].strip("/")
                return "/" + "/".join([t for t in ("mnt", "s3") if t] + rest.split("/"))
            # file:// or absolute path
            import os as _os

            if s.startswith("file://"):
                s = s[len("file://") :]
            if s.startswith("/"):
                base = _os.path.basename(s.rstrip("/")) or "data"
                return f"/mnt/data/{base}"
        except Exception:
            pass
        return "/mnt/data"

    def _show_verbose_help(self) -> None:
        """Show verbose configuration guide."""
        console.print(f"\n[bold]{flow_icon()} Flow Run Configuration Guide:[/bold]\n")
        console.print("Quick start patterns:")
        console.print("  flow run                          # Interactive 8xH100 instance")
        console.print("  flow run 'nvidia-smi'             # Quick GPU test")
        console.print("  flow run 'python train.py' -i h100  # Run script on specific GPU")
        console.print("  flow run <config.yaml>            # From configuration file\n")

        console.print("Configuration file format:")
        console.print("  name: my-training-job")
        console.print("  instance_type: 8xh100")
        console.print("  image: nvidia/cuda:12.1.0-runtime-ubuntu22.04")
        console.print("  command: python train.py --epochs 100")
        console.print("  volumes:")
        console.print("    - size_gb: 100")
        console.print("      mount_path: /data\n")

        console.print("Instance types:")
        console.print("  • h100, 8xh100 - Latest NVIDIA H100 GPUs")
        console.print("  • a100, 8xa100 - NVIDIA A100 GPUs")
        console.print("  • a10g, 4xa10g - Budget-friendly options\n")

        console.print("Common workflows:")
        console.print("  # Development iteration")
        console.print("  flow run 'bash' -i h100          # Start interactive")
        console.print("  flow upload-code                  # Update code")
        console.print("  ")
        console.print("  # Production training")
        console.print("  flow run <config.yaml> --watch    # Monitor progress")
        console.print("  flow logs <task> -f               # Stream logs\n")

    # Legacy helper methods for backward compatibility
    def _ensure_nest(self) -> None:
        """Apply nest_asyncio if available for async compatibility."""
        with suppress(ImportError, RuntimeError):
            import nest_asyncio  # type: ignore

            nest_asyncio.apply()

    def _safe_async_run(self, awaitable):
        """Run async code safely."""
        try:
            loop = __import__("asyncio").get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            self._ensure_nest()
            return loop.run_until_complete(awaitable)
        else:
            return __import__("asyncio").run(awaitable)


# Export command instance
command = RunCommand()
