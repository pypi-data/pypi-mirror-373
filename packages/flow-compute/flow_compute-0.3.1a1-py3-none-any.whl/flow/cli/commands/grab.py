"""Grab command - quickly acquire GPU resources for interactive use.

Simplified interface for acquiring GPU resources without the full task
abstraction.

Examples:
    # Grab 8 GPUs of any type
    $ flow grab 8

    # Grab specific GPU type and count
    $ flow grab 256 h100

    # Grab with time limit
    $ flow grab 64 a100 --hours 4

    # Grab with price constraint
    $ flow grab 128 h100 --max-price 2.50

Command Usage:
    flow grab COUNT [GPU_TYPE] [OPTIONS]

The command will:
- Calculate optimal instance configuration
- Acquire resources from the provider
- Set up SSH access
- Display connection information
- Track grabbed resources for easy release

Note:
    Use 'flow cancel <grab-name>' to free grabbed resources.
    Default duration is 1 hour to prevent accidental long-running allocations.
"""

from __future__ import annotations

import json

import click

from flow import DEFAULT_ALLOCATION_ESTIMATED_SECONDS
from flow.cli.commands.base import BaseCommand, console
from flow.cli.commands.utils import maybe_show_auto_status, wait_for_task
from flow.cli.utils.step_progress import AllocationProgressAdapter, StepTimeline
from flow.errors import AuthenticationError, ValidationError
from flow.sdk.client import TaskConfig
from flow.sdk.factory import create_client


class GrabCommand(BaseCommand):
    """Quickly grab GPU resources for interactive use."""

    @property
    def name(self) -> str:
        return "grab"

    @property
    def help(self) -> str:
        return """Quickly grab GPU resources for interactive development
        
        Example: flow grab 256 h100"""

    def get_command(self) -> click.Command:
        # from flow.cli.utils.mode import demo_aware_command

        @click.command(name=self.name, help=self.help)
        @click.argument("count", type=int)
        @click.argument("gpu_type", required=False, default=None)
        @click.option(
            "--hours",
            type=float,
            help="Maximum runtime in hours",
        )
        @click.option(
            "--days",
            "-d",
            type=float,
            help="Maximum runtime in days",
        )
        @click.option(
            "--weeks",
            "-w",
            type=float,
            help="Maximum runtime in weeks",
        )
        @click.option(
            "--months",
            "-m",
            type=float,
            help="Maximum runtime in months (30 days)",
        )
        @click.option(
            "--max-price",
            "-p",
            type=float,
            help="Maximum price per GPU/hour in USD",
        )
        @click.option(
            "--ssh-keys",
            "-k",
            multiple=True,
            help=(
                "Authorized SSH keys (repeatable). Accepts: platform key ID like 'sshkey_ABC123', "
                "a local private key path like '~/.ssh/id_ed25519', or a key name like 'id_ed25519'. "
                "Repeat -k/--ssh-keys for multiple values. Example: "
                "-k ~/.ssh/id_ed25519 -k sshkey_ABC123 -k work_laptop"
            ),
        )
        @click.option(
            "--region",
            "-r",
            help="Preferred region (e.g., us-west-2)",
        )
        @click.option(
            "--run",
            help="Command to run after grabbing resources",
        )
        @click.option(
            "--name",
            "-n",
            help="Custom name for the grabbed resources",
        )
        @click.option(
            "--no-unique",
            is_flag=True,
            help="Don't append unique suffix to resource name",
        )
        @click.option(
            "--json",
            "output_json",
            is_flag=True,
            help="Output JSON for automation",
        )
        @click.option(
            "--verbose",
            "-v",
            is_flag=True,
            help="Show detailed usage patterns and pricing info",
        )
        # @demo_aware_command()
        def grab(
            count: int,
            gpu_type: str | None,
            hours: float | None,
            days: float | None,
            weeks: float | None,
            months: float | None,
            max_price: float | None,
            ssh_keys: tuple[str, ...],
            region: str | None,
            run: str | None,
            name: str | None,
            no_unique: bool,
            output_json: bool,
            verbose: bool,
        ):
            """Grab GPU resources for interactive use.

            COUNT: Number of GPUs to grab
            GPU_TYPE: Type of GPU (e.g., h100, a100). If not specified, any available type.

            \b
            Examples:
                flow grab 8                  # 8 GPUs, any type, 1 hour
                flow grab 8 h100             # 8 H100 GPUs specifically
                flow grab 32 a100 --hours 4  # 32 A100s for 4 hours
                flow grab 1 --name notebook  # Named single GPU

            Use 'flow grab --verbose' for advanced patterns and pricing guidance.

            SSH keys:
                - Pass multiple keys by repeating -k/--ssh-keys
                - Accepts platform key IDs (e.g., sshkey_ABC123), local private key paths
                  (e.g., ~/.ssh/id_ed25519), or key names resolvable in ~/.ssh or ~/.flow/keys
                - Prefer private key path/name ('.pub' should exist alongside)

                Example:
                    flow grab 8 h100 -k ~/.ssh/id_ed25519 -k sshkey_ABC123 -k work_laptop
            """
            if verbose:
                console.print("\n[bold]GPU Grab Patterns & Pricing:[/bold]\n")
                console.print("Quick allocations:")
                console.print("  flow grab 8                       # Any available GPU type")
                console.print("  flow grab 8 h100                  # Specific GPU type")
                console.print("  flow grab 128 h100 --hours 24     # Large cluster")
                console.print("  flow grab 1 --name jupyter        # Named for easy reference\n")

                console.print("Duration options:")
                console.print("  flow grab 8 --hours 2             # 2 hours")
                console.print("  flow grab 8 --days 1              # 24 hours")
                console.print("  flow grab 8 --weeks 1             # 7 days")
                console.print("  flow grab 8 --months 1            # 30 days\n")

                console.print("Cost optimization:")
                console.print("  flow grab 32 --max-price 2.00     # Max $2/GPU/hour")
                console.print("  flow grab 8 a10g                  # Budget GPU option")
                console.print("  flow grab 8 --region us-east-1    # Specific region\n")

                console.print("Common workflows:")
                console.print("  # Grab and connect immediately")
                console.print("  flow grab 8 && flow ssh grab-*")
                console.print("  ")
                console.print("  # Run command after grabbing")
                console.print("  flow grab 8 --run 'nvidia-smi'")
                console.print("  ")
                console.print("  # Interactive notebook")
                console.print("  flow grab 1 --name notebook && flow ssh notebook -c 'jupyter lab'")
                console.print("  ")
                console.print("  # Multi-node cluster")
                console.print("  flow grab 64 --name cluster       # Creates 8 nodes")
                console.print("  flow ssh cluster --node 0          # SSH to first node")
                console.print("  flow ssh cluster --node 7          # SSH to last node\n")

                console.print("SSH keys (repeatable -k/--ssh-keys):")
                console.print("  # Mix of local path, platform ID, and local key name")
                console.print(
                    "  flow grab 8 h100 -k ~/.ssh/id_ed25519 -k sshkey_ABC123 -k work_laptop\n"
                )

                console.print("Instance configurations:")
                console.print("  • 1 GPU   → Single GPU instance")
                console.print("  • 8 GPUs  → Standard multi-GPU node")
                console.print("  • 64 GPUs → 8 nodes of 8 GPUs each")
                console.print("  • Custom counts rounded to instance sizes\n")

                console.print("Next steps after grab:")
                console.print("  • Connect: flow ssh <grab-name>")
                console.print("  • Multi-node: flow ssh <grab-name> --node <0-N>")
                console.print("  • Cancel: flow cancel <grab-name>")
                console.print("  • Check status: flow status <grab-name>\n")
                return

            # Handle the rest of the logic
            self._execute(
                count,
                gpu_type,
                hours,
                days,
                weeks,
                months,
                max_price,
                ssh_keys,
                region,
                run,
                name,
                no_unique,
                output_json,
            )

        return grab

    def _execute(
        self,
        count: int,
        gpu_type: str | None,
        hours: float | None,
        days: float | None,
        weeks: float | None,
        months: float | None,
        max_price: float | None,
        ssh_keys: tuple[str, ...],
        region: str | None,
        run: str | None,
        name: str | None,
        no_unique: bool,
        output_json: bool,
    ) -> None:
        """Execute the grab command."""
        # Unified timeline
        timeline: StepTimeline | None = None
        if not output_json:
            timeline = StepTimeline(console, title="flow grab", title_animation="auto")
            timeline.start()

        try:
            # Validate inputs
            if count <= 0:
                self.handle_error("GPU count must be positive")
                return

            # Convert all time units to hours
            total_hours = self._calculate_total_hours(hours, days, weeks, months)

            if total_hours is not None:
                if total_hours <= 0:
                    self.handle_error("Duration must be positive")
                    return
                if total_hours > 168:  # Warn but don't block
                    console.print(
                        "[warning]Note: Maximum supported duration is typically 168 hours (7 days)[/warning]"
                    )

            # Initialize Flow client early and calculate optimal instance configuration
            flow_client = create_client(auto_init=True)
            instance_type, num_instances = self._calculate_optimal_config(
                count, gpu_type, flow_client
            )

            # Auto-select region when not explicitly provided: probe availability across regions
            auto_region: str | None = None
            if not region:
                try:
                    # Query provider for available instances of this type across regions
                    candidates = flow_client.find_instances(
                        {"instance_type": instance_type}, limit=50
                    )
                    # Derive gpu token (e.g., '8xa100' -> 'a100') for safety filtering
                    it_lower = (instance_type or "").lower()
                    gpu_token = it_lower.split("x", 1)[1] if "x" in it_lower else it_lower
                    # Keep only candidates that match requested GPU family
                    filtered = []
                    for c in candidates or []:
                        try:
                            c_gpu = (getattr(c, "gpu_type", None) or "").lower()
                            c_name = (getattr(c, "instance_type", None) or "").lower()
                            if (c_gpu and c_gpu == gpu_token) or (
                                gpu_token and gpu_token in c_name
                            ):
                                filtered.append(c)
                        except Exception:
                            continue
                    # Only trust a region if we have at least one GPU-family match
                    if filtered:
                        try:
                            auto_region = getattr(filtered[0], "region", None) or None
                        except Exception:
                            auto_region = None
                except Exception:
                    # Best-effort hint only; provider will still do multi-region selection
                    auto_region = None

            # Generate name if not provided
            if not name:
                from flow.cli.utils.name_generator import generate_unique_name

                name = generate_unique_name(prefix="grab", base_name=None, add_unique=not no_unique)
            # If name is provided, use it as-is

            # Create config for resource allocation
            config_dict = {
                "name": name,
                "unique_name": False,  # We handle uniqueness ourselves with --no-unique
                "instance_type": instance_type,
                "num_instances": num_instances,
                "command": run if run else ["sleep", "infinity"],
                "image": "nvidia/cuda:12.1.0-runtime-ubuntu22.04",
                # Grab is an interactive devbox; skip code packaging for speed
                "upload_code": False,
                "env": {
                    "FLOW_GRAB": "true",
                    "FLOW_GPU_COUNT": str(count),
                    "FLOW_GPU_TYPE": gpu_type or "any",
                },
            }

            # Add max_run_time_hours if specified
            if total_hours is not None:
                config_dict["max_run_time_hours"] = total_hours

            # Add optional parameters
            if ssh_keys:
                config_dict["ssh_keys"] = list(ssh_keys)
            if max_price:
                config_dict["max_price_per_hour"] = max_price * count  # Total price
            # Prefer explicit region; otherwise use auto-selected region when available
            selected_region = region or auto_region
            if selected_region:
                config_dict["region"] = selected_region

            config = TaskConfig(**config_dict)

            if not output_json and timeline:
                # Show what we're doing
                console.print("\n[bold]Configuration:[/bold]")
                console.print(f"  GPUs: {count}x {gpu_type or 'any'}")
                console.print(f"  Instance config: {num_instances}x {instance_type}")
                if selected_region:
                    console.print(f"  Region: {selected_region}")
                if total_hours is not None:
                    console.print(f"  Duration: {self._format_duration(total_hours)}")
                if max_price:
                    console.print(
                        f"  Max price: ${max_price:.2f}/GPU/hour (${max_price * count:.2f}/hour total)"
                    )
                console.print()

                submit_idx = timeline.add_step(
                    f"Provisioning {num_instances}x {instance_type}", show_bar=False
                )
                timeline.start_step(submit_idx)
                task = flow_client.run(config)
                timeline.complete_step()
            else:
                task = flow_client.run(config)

            if output_json:
                result = {
                    "grab_id": task.task_id,
                    "name": name,
                    "gpus": count,
                    "gpu_type": gpu_type or "any",
                    "instance_config": f"{num_instances}x {instance_type}",
                    "status": "provisioning",
                }
                console.print(json.dumps(result))
                return

            # Wait for resources to be ready
            if timeline:
                alloc_idx = timeline.add_step(
                    "Allocating instances",
                    show_bar=True,
                    estimated_seconds=DEFAULT_ALLOCATION_ESTIMATED_SECONDS,
                )
                alloc = AllocationProgressAdapter(
                    timeline, alloc_idx, estimated_seconds=DEFAULT_ALLOCATION_ESTIMATED_SECONDS
                )
                with alloc:
                    status = wait_for_task(
                        flow_client,
                        task.task_id,
                        watch=False,
                        json_output=False,
                        task_name=task.name,
                        progress_adapter=alloc,
                    )
            else:
                status = wait_for_task(
                    flow_client, task.task_id, watch=False, json_output=False, task_name=task.name
                )

            if status == "running":
                # Get updated task info
                task = flow_client.get_task(task.task_id)

                from flow.cli.utils.theme_manager import theme_manager as _tm

                success_color = _tm.get_color("success")
                console.print(
                    f"\n[{success_color}]✓[/{success_color}] Resources acquired successfully!"
                )
                console.print(f"\nCluster: [accent]{name}[/accent]")
                console.print(
                    f"GPUs: {count}x {gpu_type or 'any'} ({num_instances} node{'s' if num_instances > 1 else ''})"
                )

                # Show pricing information
                if (
                    hasattr(task, "cost_per_hour")
                    and task.cost_per_hour
                    and task.cost_per_hour != "$0"
                ):
                    # cost_per_hour from provider is per instance; show total for multi-node
                    try:
                        per_instance_cost = float(str(task.cost_per_hour).strip().lstrip("$") or 0)
                    except Exception:
                        per_instance_cost = 0.0
                    instances_count = getattr(task, "num_instances", None) or num_instances or 1
                    if instances_count and instances_count > 1 and per_instance_cost > 0:
                        total_cost = per_instance_cost * instances_count
                        console.print(
                            f"Cost: ${total_cost:.2f}/hour (${per_instance_cost:.2f}/node/hour)"
                        )
                    else:
                        console.print(f"Cost: {task.cost_per_hour}/hour")

                # Show the price limit if it was specified by the user
                if max_price:
                    console.print(
                        f"Price limit: ${max_price:.2f}/GPU/hour (${max_price * count:.2f}/hour total)"
                    )

                console.print(f"\nSSH access: [accent]flow ssh {name}[/accent]")
                if num_instances > 1:
                    console.print(
                        f"Multi-node access: [accent]flow ssh {name} --node <0-{num_instances - 1}>[/accent]"
                    )

                if total_hours is not None:
                    console.print(
                        f"\n[warning]Resources will remain allocated for up to {self._format_duration(total_hours)}.[/warning]"
                    )
                else:
                    console.print(
                        "\n[warning]Resources will remain allocated until manually released.[/warning]"
                    )
                console.print(f"To cancel: [accent]flow cancel {name}[/accent]")

                if run:
                    console.print(f"\n[dim]Running command: {run}[/dim]")
            elif status == "failed":
                console.print("\n[error]✗[/error] Failed to acquire resources")
                console.print("Try adjusting your requirements or check availability")
            else:
                # Still pending or preparing after soft timeout — continue in background
                console.print("\n[warning]⏳ Allocation in progress[/warning]")
                console.print(
                    f"Resources are still {status}. This is normal during bidding/queueing."
                )
                console.print(
                    f"We'll keep provisioning in the background. Check progress with: [accent]flow status {name}[/accent]"
                )
                console.print(
                    f"Connect when ready: [accent]flow ssh {name}[/accent]  |  Cancel: [accent]flow cancel {name}[/accent]"
                )

            # Show a compact status snapshot after submission or acquisition
            try:
                maybe_show_auto_status(focus=name, reason="After grab", show_all=False)
            except Exception:
                pass

        except AuthenticationError:
            self.handle_auth_error()
        except ValidationError as e:
            from rich.markup import escape

            self.handle_error(f"Invalid configuration: {escape(str(e))}")
        except Exception as e:
            self.handle_error(str(e))
        finally:
            if timeline:
                try:
                    timeline.finish()
                except Exception:
                    pass

    def _calculate_optimal_config(
        self, gpu_count: int, gpu_type: str | None, flow_client=None
    ) -> tuple[str, int]:
        """Calculate optimal instance type and count for requested GPUs.

        Args:
            gpu_count: Total number of GPUs requested
            gpu_type: Type of GPU (e.g., 'h100', 'a100') or None for any

        Returns:
            Tuple of (instance_type, num_instances)
        """
        # Use Flow helper (provider-first under the hood)
        flow = flow_client or create_client(auto_init=True)
        instance_type, num_instances, warning = flow.normalize_instance_request(gpu_count, gpu_type)

        # Display any warning about adjustments
        if warning:
            console.print(f"[warning]Note: {warning}[/warning]")

        return instance_type, num_instances

    def _calculate_total_hours(
        self,
        hours: float | None,
        days: float | None,
        weeks: float | None,
        months: float | None,
    ) -> float | None:
        """Calculate total hours from various time units.

        Args:
            hours: Hours specified
            days: Days specified (converted to hours)
            weeks: Weeks specified (converted to hours)
            months: Months specified (converted to 30-day months)

        Returns:
            Total hours or None if no duration specified
        """
        # Check that only one time unit is specified
        time_args = [arg for arg in [hours, days, weeks, months] if arg is not None]
        if len(time_args) > 1:
            self.handle_error(
                "Please specify only one time unit (--hours, --days, --weeks, or --months)"
            )
            return None

        if not time_args:
            return None

        # Convert to hours
        if hours is not None:
            return hours
        elif days is not None:
            return days * 24
        elif weeks is not None:
            return weeks * 7 * 24
        elif months is not None:
            return months * 30 * 24  # Approximate month as 30 days

        return None

    def _format_duration(self, total_hours: float) -> str:
        """Format duration in human-readable form.

        Args:
            total_hours: Duration in hours

        Returns:
            Formatted string like "2 days", "1 week", "3.5 hours"
        """
        if total_hours >= 24 * 30:  # More than a month
            months = total_hours / (24 * 30)
            return f"{months:.1f} month{'s' if months != 1 else ''}"
        elif total_hours >= 24 * 7:  # More than a week
            weeks = total_hours / (24 * 7)
            return f"{weeks:.1f} week{'s' if weeks != 1 else ''}"
        elif total_hours >= 24:  # More than a day
            days = total_hours / 24
            return f"{days:.1f} day{'s' if days != 1 else ''}"
        else:
            return f"{total_hours:.1f} hour{'s' if total_hours != 1 else ''}"


# Export command instance
command = GrabCommand()
