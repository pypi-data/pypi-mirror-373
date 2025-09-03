"""Guided tutorial command for Flow CLI.

This command walks new users through:
1) Interactive configuration (provider setup wizard)
2) Quick health validation (connectivity/auth/ssh)
3) Optional verification example run

Usage:
  flow tutorial             # Full guided setup
  flow tutorial --yes       # Auto-confirm running the verification example
  flow tutorial --skip-example
  flow tutorial --example gpu-test
"""

import click
from rich.prompt import Confirm

from flow.cli.commands.base import BaseCommand, console
from flow.cli.commands.feedback import feedback
from flow.cli.commands.messages import print_next_actions
from flow.cli.ui.presentation.animated_progress import AnimatedEllipsisProgress
from flow.cli.utils.hyperlink_support import hyperlink_support

# Avoid static import; import ConfigManager lazily within the command
from flow.sdk.factory import create_client


class TutorialCommand(BaseCommand):
    """Interactive, end-to-end onboarding for the Flow SDK."""

    @property
    def name(self) -> str:
        return "tutorial"

    @property
    def help(self) -> str:
        return (
            "Guided setup and verification: run setup wizard, validate connectivity, "
            "and optionally run a GPU test"
        )

    def get_command(self) -> click.Command:
        @click.command(name=self.name, help=self.help)
        @click.option("--provider", envvar="FLOW_PROVIDER", help="Provider to use (e.g., mithril)")
        # Demo mode disabled for initial release
        # @click.option("--demo/--no-demo", default=True, help="Start in demo mode by default (mock provider)")
        @click.option(
            "--example",
            type=click.Choice(["gpu-test"], case_sensitive=False),
            default="gpu-test",
            show_default=True,
            help="Verification example to run",
        )
        @click.option("--skip-init", is_flag=True, help="Skip interactive setup wizard")
        @click.option("--force-init", is_flag=True, help="Run setup wizard even if config is valid")
        @click.option("--skip-health", is_flag=True, help="Skip quick health validation")
        @click.option("--skip-example", is_flag=True, help="Skip verification example run")
        @click.option("--yes", "--y", "yes", is_flag=True, help="Auto-confirm prompts")
        def tutorial(
            provider: str | None,
            example: str,
            skip_init: bool,
            force_init: bool,
            skip_health: bool,
            skip_example: bool,
            yes: bool,
        ):
            """Run the guided tutorial."""
            # Intro (compact banner)
            feedback.info(
                "Sets up credentials, validates connectivity, and optionally runs a GPU check.",
                title="Mithril Flow Tutorial",
            )

            # Show current configuration status (best effort)
            try:
                from flow.cli.utils.lazy_imports import import_attr as _import_attr

                ConfigManager = _import_attr(
                    "flow.application.config.manager", "ConfigManager", default=None
                )
                sources = ConfigManager().load_sources() if ConfigManager else None
                mith = sources.get_mithril_config()
                api_present = bool(sources.api_key)
                provider_name = sources.provider or "—"
                project = mith.get("project", "—")
                region = mith.get("region", "—")
                status_lines = [
                    f"Provider: [accent]{provider_name}[/accent]",
                    f"API key: {'[success]✓[/success]' if api_present else '[error]✗[/error]'}",
                    f"Project: [accent]{project}[/accent]",
                    f"Region: [accent]{region}[/accent]",
                ]

                feedback.info("\n".join(status_lines), title="Current configuration")
            except Exception:
                pass

            # 1) Interactive configuration
            config_valid = False
            try:
                # Consider valid if an API key is configured and a project is set
                from flow.cli.utils.lazy_imports import import_attr as _import_attr

                ConfigManager = _import_attr(
                    "flow.application.config.manager", "ConfigManager", default=None
                )
                sources = ConfigManager().load_sources() if ConfigManager else None
                mith = sources.get_mithril_config()
                config_valid = bool(sources.api_key) and bool(mith.get("project"))
            except Exception:
                config_valid = False

            should_run_wizard = not skip_init and (force_init or not config_valid)

            if not skip_init and config_valid and not force_init:
                console.print(
                    "[dim]Valid configuration detected. Skipping setup wizard (use --force-init to rerun).[/dim]"
                )

            if should_run_wizard:
                from flow.cli.commands.init import run_setup_wizard

                with AnimatedEllipsisProgress(
                    console, "Starting setup wizard", start_immediately=True
                ):
                    ok = run_setup_wizard(provider)
                if not ok:
                    console.print("[error]Setup wizard did not complete successfully[/error]")
                    raise click.exceptions.Exit(1)
            else:
                if skip_init and not config_valid:
                    console.print(
                        "[warning]No valid configuration found; running setup wizard is required for first-time use[/warning]"
                    )
                    from flow.cli.commands.init import run_setup_wizard as _wiz

                    with AnimatedEllipsisProgress(
                        console, "Starting setup wizard", start_immediately=True
                    ):
                        ok = _wiz(provider)
                    if not ok:
                        console.print("[error]Setup wizard did not complete successfully[/error]")
                        raise click.exceptions.Exit(1)
                elif skip_init:
                    console.print("[dim]Skipping setup wizard (--skip-init)[/dim]")

            # 2) Quick health validation
            health_issues: int | None = None
            if not skip_health:
                try:
                    from flow.cli.commands.health import HealthChecker

                    with AnimatedEllipsisProgress(
                        console, "Validating connectivity and auth", transient=True
                    ):
                        checker = HealthChecker(create_client(auto_init=True))
                        checker.check_connectivity()
                        checker.check_authentication()
                        checker.check_ssh_keys()

                    report = checker.generate_report()
                    issues = int(report.get("summary", {}).get("issues", 0))
                    warnings = int(report.get("summary", {}).get("warnings", 0))
                    successes = int(report.get("summary", {}).get("successes", 0))
                    health_issues = issues

                    message = (
                        f"✓ {successes} checks passed\n⚠ {warnings} warnings\n✗ {issues} issues"
                    )
                    if issues == 0:
                        feedback.success(message, title="Health checks")
                    else:
                        feedback.error(message, title="Health checks")
                    if issues > 0:
                        # Show a few actionable issues immediately
                        details = (report.get("details", {}) or {}).get("issues", [])
                        for item in details[:3]:
                            cat = item.get("category", "Issue")
                            msg = item.get("message", "")
                            console.print(f"  • [error]{cat}[/error]: {msg}")
                            if item.get("suggestion"):
                                console.print(f"    → [dim]{item['suggestion']}[/dim]")
                        console.print(
                            "\n[dim]Run 'flow health --verbose' for detailed diagnostics[/dim]"
                        )
                        console.print("[dim]Try auto-fixes: 'flow health --fix'[/dim]")
                except Exception as e:
                    console.print(f"[warning]Health validation skipped due to error:[/warning] {e}")
            else:
                console.print("[dim]Skipping health validation (--skip-health)[/dim]")

            # 3) Optional verification example
            if not skip_example:
                should_run = yes or Confirm.ask(
                    "Run verification example now? [dim](recommended)[/dim]", default=True
                )
                if should_run:
                    try:
                        # Reuse example command implementation for consistent UX
                        from flow.cli.commands import example as example_cmd

                        feedback.info(
                            f"Running example: [accent]{example}[/accent]", title="Verification"
                        )
                        example_cmd.command._execute(example, show=False)
                        from flow.cli.commands.messages import print_next_actions as _pna

                        _pna(
                            console,
                            [
                                "Monitor: [accent]flow status[/accent]",
                                "Stream logs: [accent]flow logs <task> -f[/accent]",
                            ],
                        )
                    except Exception as e:
                        console.print(f"[error]Failed to run example:[/error] {e}")
                        raise click.exceptions.Exit(1)
                else:
                    console.print(f"You can run later: [accent]flow example {example}[/accent]")
            else:
                console.print("[dim]Skipping example run (--skip-example)[/dim]")

            # Finish with next steps (concise, context-aware)
            recs: list[str] = []
            if health_issues and health_issues > 0:
                recs.append("Fix issues: [accent]flow health --fix[/accent] (then re-run tutorial)")
            recs.append("Explore examples: [accent]flow example[/accent]")
            recs.append("Watch status: [accent]flow status --watch[/accent]")
            print_next_actions(console, recs)

            # Link to docs for deeper dive
            try:
                from flow.utils.links import DocsLinks

                link = hyperlink_support.create_link(
                    "Compute quickstart →", DocsLinks.compute_quickstart()
                )
                console.print(f"\n[dim]{link}[/dim]")
            except Exception:
                from flow.utils.links import DocsLinks

                console.print(f"\n[dim]Docs: {DocsLinks.compute_quickstart()}[/dim]")

        return tutorial


# Export command instance
command = TutorialCommand()
