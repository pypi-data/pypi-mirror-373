"""Completion command for Flow CLI.

Provides `flow completion` with subcommands to generate and install shell
completion scripts for bash, zsh, and fish.
"""

import click

from flow.cli.commands.base import BaseCommand, console
from flow.cli.ui.runtime.shell_completion import command as completion_helper


class CompletionCLICommand(BaseCommand):
    """Manage shell completion for the Flow CLI."""

    @property
    def name(self) -> str:
        return "completion"

    @property
    def help(self) -> str:
        return "Generate and install shell completion scripts"

    def get_command(self) -> click.Command:
        @click.group(name=self.name, help=self.help)
        def completion():
            pass

        @completion.command(name="generate", help="Print completion script for a shell")
        @click.argument("shell", required=False, type=click.Choice(["bash", "zsh", "fish"]))
        def generate(shell: str | None = None):
            """Generate completion script to stdout.

            Example usages:
              - bash/zsh: eval "$(flow completion generate bash)"
              - fish:     flow completion generate fish | source
            """
            if not shell:
                # Attempt auto-detection when omitted
                shell = completion_helper._detect_shell()
                if not shell:
                    console.print(
                        "[error]Could not auto-detect shell. Specify one of: bash, zsh, fish[/error]"
                    )
                    raise click.exceptions.Exit(1)

            completion_helper._generate_completion(shell)

        @completion.command(name="install", help="Install completion into your shell rc file")
        @click.option(
            "--shell",
            "shell",
            type=click.Choice(["bash", "zsh", "fish"]),
            help="Shell to install for (auto-detect if omitted)",
        )
        @click.option(
            "--path",
            "path",
            type=click.Path(dir_okay=False, path_type=str),
            help="Optional path to rc file to modify (defaults per shell)",
        )
        def install(shell: str | None, path: str | None):
            completion_helper._install_completion(shell, path)

        @completion.command(name="uninstall", help="Remove installed shell completion")
        @click.option(
            "--shell",
            "shell",
            type=click.Choice(["bash", "zsh", "fish"]),
            help="Shell to uninstall for (auto-detect if omitted)",
        )
        @click.option(
            "--path",
            "path",
            type=click.Path(dir_okay=False, path_type=str),
            help="Optional path to rc file to clean (defaults per shell)",
        )
        def uninstall(shell: str | None, path: str | None):
            completion_helper._uninstall_completion(shell, path)

        return completion


# Export command instance
command = CompletionCLICommand()
