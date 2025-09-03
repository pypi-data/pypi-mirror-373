"""Mithril-specific setup components for configuration items.

Provides specialized setup logic for Mithril provider configuration including
API keys, projects, SSH keys, and other Mithril-specific settings.

Note: This module is tightly coupled to the Mithril provider and its API.
Different providers would require their own setup components.
"""

import asyncio
import logging
import os
import time
import webbrowser
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.prompt import Confirm, Prompt

from flow.cli.ui.components import InteractiveSelector, SelectionItem
from flow.cli.ui.presentation.visual_constants import get_status_display
from flow.cli.utils.config_validator import ConfigValidator, ValidationStatus
from flow.sdk.helpers.masking import mask_api_key
from flow.sdk.http import HttpClient

logger = logging.getLogger(__name__)


def _run_async(awaitable):
    """Run an awaitable safely regardless of loop state.

    Uses asyncio.run() when no loop is running; otherwise falls back to a
    loop-agnostic execution by creating a new task on the existing loop.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        # Best-effort inline execution in existing loop
        try:
            import nest_asyncio  # type: ignore

            try:
                nest_asyncio.apply()
            except Exception:
                pass
        except Exception:
            pass
        return loop.run_until_complete(awaitable)
    else:
        return asyncio.run(awaitable)


class AnimatedDots:
    """Minimal animated dots implementation for progress messages."""

    def __init__(self):
        self._counter = 0
        self._dots = ["", ".", "..", "..."]

    def next(self) -> str:
        """Get next dots pattern in sequence."""
        dots = self._dots[self._counter % len(self._dots)]
        self._counter += 1
        return dots

    def get(self, base_text: str) -> str:
        """Get text with animated dots appended."""
        return f"{base_text}{self.next()}"


def select_from_options(
    console: Console,
    options: list[dict[str, Any]],
    name_key: str = "name",
    id_key: str = "id",
    title: str = "Select an option",
    show_ssh_table: bool = False,
    extra_header_html: str | None = None,
    breadcrumbs: list[str] | None = None,
    preferred_viewport_size: int | None = None,
) -> dict[str, Any] | None:
    """Intelligently select from options using appropriate UI pattern.

    Uses simple prompt for few options, interactive selector for many.

    Args:
        console: Console for output
        options: List of option dictionaries
        name_key: Key for display name in option dict
        id_key: Key for ID in option dict
        title: Title for selection interface

    Returns:
        Selected option dict or None if cancelled
    """
    if not options:
        return None

    # Single option: auto-select with confirmation
    if len(options) == 1:
        option = options[0]
        name = option.get(name_key, "Unknown")
        console.print(f"{get_status_display('configured', f'Selected project: {name}')}")
        return option

    # Show SSH keys in a table format if requested
    if show_ssh_table and any("created_at" in opt for opt in options):
        # Separate generation options from existing keys
        gen_options = [opt for opt in options if opt.get(id_key, "").startswith("GENERATE_")]
        ssh_keys = [opt for opt in options if not opt.get(id_key, "").startswith("GENERATE_")]

        # Create formatted options for interactive selector
        formatted_options = []

        # Add generation options first
        for i, opt in enumerate(gen_options):
            formatted_options.append(
                {**opt, "display_name": opt.get(name_key, "Unknown"), "index": i + 1}
            )

        # Add SSH keys
        for i, key in enumerate(ssh_keys):
            idx = len(gen_options) + i + 1
            formatted_options.append(
                {**key, "display_name": key.get("name", "Unknown"), "index": idx}
            )

        # Use interactive selector with custom formatting
        def ssh_option_to_selection(option: dict[str, Any]) -> SelectionItem[dict[str, Any]]:
            if option.get(id_key, "").startswith("GENERATE_"):
                # Action item
                return SelectionItem(
                    value=option, id="", title=option["display_name"], subtitle="", status=""
                )
            else:
                # SSH key with metadata
                subtitle_parts = []
                if option.get("created_at"):
                    subtitle_parts.append(f"Created: {option['created_at']}")
                if option.get("fingerprint"):
                    subtitle_parts.append(option["fingerprint"])
                # Provide an explicit hint when we detect a matching local private key
                try:
                    display_name = option.get("display_name") or option.get("name") or ""
                    if "(local copy)" in str(display_name):
                        subtitle_parts.append("local private key present")
                except Exception:
                    pass

                return SelectionItem(
                    value=option,
                    id="",
                    title=option["display_name"],
                    subtitle=" • ".join(subtitle_parts),
                    status="",
                )

        selector = InteractiveSelector(
            items=formatted_options,
            item_to_selection=ssh_option_to_selection,
            title=title,  # Use the provided title
            allow_multiple=False,
            allow_back=True,
            show_preview=False,
            breadcrumbs=breadcrumbs,
            extra_header_html=extra_header_html,
            preferred_viewport_size=preferred_viewport_size,
        )

        result = selector.select()
        if result is InteractiveSelector.BACK_SENTINEL:
            return None
        return result if result else None

        # Always try interactive selector first for better UX
    try:

        def option_to_selection(option: dict[str, Any]) -> SelectionItem[dict[str, Any]]:
            name = option.get(name_key, "Unknown")
            option_id = option.get(id_key, str(hash(str(option))))

            # Special handling for SSH keys - cleaner display
            if "ssh" in title.lower() and option_id.startswith("sshkey_"):
                # For existing SSH keys, include metadata in subtitle
                subtitle_parts = []
                if "created_at" in option:
                    subtitle_parts.append(option["created_at"])
                if option.get("fingerprint"):
                    subtitle_parts.append(option["fingerprint"])
                try:
                    name_or_disp = option.get(name_key, option.get("name", ""))
                    if "(local copy)" in str(name_or_disp):
                        subtitle_parts.append("local private key present")
                except Exception:
                    pass

                return SelectionItem(
                    value=option,
                    id="",  # Don't show ID separately
                    title=name,
                    subtitle=" • ".join(subtitle_parts) if subtitle_parts else "",
                    status="",  # Don't show redundant status
                )
            elif option_id in ["GENERATE_SERVER", "GENERATE_LOCAL"]:
                # For generation options, show as actions
                return SelectionItem(value=option, id="", title=name, subtitle="", status="")
            else:
                # Default behavior for other options
                return SelectionItem(
                    value=option, id=option_id, title=name, subtitle="", status="Available"
                )

        selector = InteractiveSelector(
            items=options,
            item_to_selection=option_to_selection,
            title=title,
            allow_multiple=False,
            allow_back=True,
            show_preview=False,
            breadcrumbs=breadcrumbs,
            extra_header_html=extra_header_html,
            preferred_viewport_size=preferred_viewport_size,
        )

        result = selector.select()
        if result is InteractiveSelector.BACK_SENTINEL:
            return None
        if result is not None:
            return result

    except Exception:
        # Fall back to numbered selection if interactive fails
        pass

    # Fallback: numbered prompt
    console.print(f"\n[bold]{title}:[/bold]")
    for i, option in enumerate(options, 1):
        name = option.get(name_key, "Unknown")
        console.print(f"  {i}. {name}")

    while True:
        choice = Prompt.ask("\nSelect number", default="1")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
            else:
                console.print("[error]Invalid selection[/error]")
        except ValueError:
            console.print("[error]Please enter a number[/error]")


class ApiKeySetup:
    """Handle API key configuration and validation."""

    def __init__(self, console: Console):
        """Initialize API key setup.

        Args:
            console: Rich console for output
        """
        self.console = console
        self.validator = ConfigValidator()

    def setup(self, existing_config: dict[str, Any]) -> str | None:
        """Configure and validate API key.

        Args:
            existing_config: Existing configuration values

        Returns:
            Valid API key or None if setup failed
        """
        # Check environment variable first
        env_key = os.environ.get("MITHRIL_API_KEY")
        if env_key and not env_key.startswith("YOUR_"):
            self.console.print(
                f"{get_status_display('configured', 'Found API key in environment')}"
            )
            use_env = Confirm.ask("Use this API key?", default=True)
            if use_env:
                if self._verify_api_key(env_key):
                    return env_key

        # Show instructions
        self.console.print("\nMithril Flow requires an API key from Mithril.")
        self.console.print("\n[bold]Get your API key:[/bold]")
        from flow.utils.links import WebLinks

        self.console.print(f"1. Visit: [link]{WebLinks.api_keys()}[/link]")
        self.console.print("2. Sign in or create an account")
        self.console.print("3. Create a new key or copy an existing one")

        # Get API key with validation
        self.console.print("\n[bold]Enter your API key[/bold]")
        self.console.print("[dim]Format: fkey_XXXXXXXXXXXXXXXXXXXXXXXX[/dim]")

        while True:
            api_key = Prompt.ask("\nAPI Key", password=True)

            # Validate format
            format_result = self.validator.validate_api_key_format(api_key)
            if format_result.status != ValidationStatus.VALID:
                self.console.print(f"[error]{format_result.message}[/error]")
                if not Confirm.ask("Continue anyway?", default=False):
                    continue

            # Show masked feedback
            self.console.print(f"[dim]Received: {mask_api_key(api_key)}[/dim]")

            # Verify the key works
            if self._verify_api_key(api_key):
                return api_key
            else:
                if not Confirm.ask("\nTry a different key?", default=True):
                    return None

    def _verify_api_key(self, api_key: str) -> bool:
        """Verify API key by making an API call.

        Args:
            api_key: API key to verify

        Returns:
            True if key is valid
        """
        dots = AnimatedDots()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=self.console,
            transient=True,
        ) as progress:
            task = progress.add_task(f"Verifying API key{dots.next()}", total=None)

            try:
                result = _run_async(self.validator.verify_api_key(api_key))

                if result.status == ValidationStatus.VALID:
                    from flow.cli.utils.theme_manager import theme_manager as _tm

                    success_color = _tm.get_color("success")
                    progress.update(
                        task, description=f"[{success_color}]✓ API key verified![/{success_color}]"
                    )
                    if result.details and result.details.get("project_count"):
                        self.console.print(
                            f"\n[dim]Found {result.details['project_count']} project(s)[/dim]"
                        )
                    return True
                else:
                    progress.update(task, description=f"[error]✗ {result.message}[/error]")
                    return False

            except Exception as e:
                progress.update(task, description="[error]✗ Verification failed[/error]")
                from rich.markup import escape

                self.console.print(f"\n[error]Error:[/error] {escape(str(e))}")
                try:
                    logger.debug("API key verification error", exc_info=True)
                except Exception:
                    pass
                return False


class ProjectSetup:
    """Handle project selection and configuration."""

    def __init__(self, console: Console):
        """Initialize project setup.

        Args:
            console: Rich console for output
        """
        self.console = console
        self.validator = ConfigValidator()

    def setup(self, api_key: str) -> str | None:
        """Configure project selection.

        Args:
            api_key: API key for fetching projects

        Returns:
            Selected project name or None
        """
        # Try to fetch projects from API
        projects = self._fetch_projects(api_key)

        if not projects:
            # Manual entry fallback
            self.console.print("\n[warning]Could not fetch projects from API.[/warning]")
            self.console.print("\nEnter your project name manually.")
            self.console.print(
                f"[dim]To create projects: "
                f"{__import__('flow.utils.links', fromlist=['WebLinks']).WebLinks.projects_settings()}[/dim]"
            )

            project = Prompt.ask("\nProject name", default="default")

            # Validate project name
            result = self.validator.validate_project_name(project)
            if result.status != ValidationStatus.VALID:
                self.console.print(f"[error]{result.message}[/error]")
                if not Confirm.ask("Use this name anyway?", default=False):
                    return None

            return project

        # Use intelligent selection based on number of projects
        selected_project = select_from_options(
            console=self.console,
            options=projects,
            name_key="name",
            id_key="fid",
            title="Available project",
            breadcrumbs=["Mithril Flow Setup", "Configuration", "Project"],
            preferred_viewport_size=5,
        )

        if selected_project:
            return selected_project["name"]

        return None

    def _fetch_projects(self, api_key: str) -> list[dict[str, Any]]:
        """Fetch user's projects from API.

        Args:
            api_key: API key for authentication

        Returns:
            List of project dicts or empty list
        """
        try:
            client = HttpClient(
                base_url=os.environ.get(
                    "MITHRIL_API_URL", os.environ.get("FLOW_API_URL", "https://api.mithril.ai")
                ),
                headers={"Authorization": f"Bearer {api_key}"},
            )

            response = client.request(
                method="GET",
                url="/v2/projects",
                timeout_seconds=10.0,
            )

            return response if isinstance(response, list) else []

        except Exception:
            try:
                logger.debug("Failed to fetch projects", exc_info=True)
            except Exception:
                pass
            return []


class SshKeySetup:
    """Handle SSH key configuration."""

    def __init__(self, console: Console):
        """Initialize SSH key setup.

        Args:
            console: Rich console for output
        """
        self.console = console
        self.validator = ConfigValidator()

    def setup(self, api_key: str, project: str | None = None) -> str | None:
        """Configure SSH keys with platform integration.

        Args:
            api_key: API key for fetching SSH keys
            project: Optional project to filter keys

        Returns:
            Selected SSH key ID or None
        """
        self.console.print(
            """
SSH keys let you connect to GPU instances via SSH.

[bold]Important:[/bold] Flow uses SSH keys from your Mithril account. Upload your
SSH public key before selecting it here.

Steps:
1. Upload a public key: {__import__('flow.utils.links', fromlist=['WebLinks']).WebLinks.ssh_keys()}
2. Copy its ID (e.g., sshkey_ABC123)
3. Use that ID in your Flow configuration

[dim]SSH access is optional; you can configure it later.[/dim]
        """
        )

        # Check for local SSH keys first
        local_keys = self._find_local_ssh_keys()
        local_key_names = {key.stem for key in local_keys}  # Remove .pub extension

        # Check for platform SSH keys
        platform_keys = self._fetch_ssh_keys(api_key, project)

        # Show appropriate message based on project configuration
        if not project:
            self.console.print(
                "\n[warning]No project configured yet.[/warning] SSH keys are project-specific."
            )
            self.console.print("Configure a project first, then return to set up SSH keys.")
            return None
        elif platform_keys:
            self.console.print(
                f"\n{get_status_display('configured', f'Found {len(platform_keys)} SSH key(s) in your account')}"
            )

            # Enhance keys with local match information for display
            enhanced_keys = []
            for key in platform_keys:
                key_copy = key.copy()
                name = key.get("name", "Unnamed")
                if name in local_key_names:
                    key_copy["display_name"] = f"{name} (matches local key)"
                else:
                    key_copy["display_name"] = name
                enhanced_keys.append(key_copy)

            # Use intelligent selection
            selected_key = select_from_options(
                console=self.console,
                options=enhanced_keys,
                name_key="display_name",
                id_key="fid",
                title="Available SSH key",
                breadcrumbs=["Mithril Flow Setup", "Configuration", "Default SSH Key"],
                preferred_viewport_size=5,
            )

            if selected_key:
                selected_id = selected_key.get("fid", selected_key.get("id"))
                selected_name = selected_key.get("name", "Unknown")
                self.console.print(
                    f"{get_status_display('configured', f'Selected key: {selected_name}')}"
                )
                return selected_id

            # Allow skip if cancelled
            if Confirm.ask("\nSkip SSH key configuration?", default=True):
                return None

        # No platform keys found - only show this if project is configured
        if project:
            self.console.print(f"\n[warning]No SSH keys found for project '{project}'.[/warning]")

        # Check for local keys
        local_keys = self._find_local_ssh_keys()
        if local_keys:
            self.console.print(f"\n[dim]Found {len(local_keys)} local SSH key(s):[/dim]")
            for key in local_keys[:3]:
                self.console.print(f"  • {key.name}")

        # Guide user through upload
        self.console.print("\n[bold]To use SSH keys:[/bold]")
        self.console.print(
            "1. Upload your public key at: [link]"
            f"{__import__('flow.utils.links', fromlist=['WebLinks']).WebLinks.ssh_keys()}[/link]"
        )
        self.console.print(
            "   Or upload locally via CLI: [accent]flow ssh-keys upload ~/.ssh/id_ed25519.pub[/accent]"
        )
        self.console.print("   (Private keys are never uploaded; Flow only reads your .pub)")
        self.console.print("2. Copy the assigned key ID (sshkey_…)")

        if Confirm.ask("\nOpen SSH key management page?", default=True):
            from flow.utils.links import WebLinks

            webbrowser.open(WebLinks.ssh_keys())
            time.sleep(2)

        # Manual entry
        key_id = Prompt.ask("\nEnter SSH key ID (or press Enter to skip)", default="")

        if key_id:
            # Validate format
            result = self.validator.validate_ssh_key_id(key_id)
            if result.status != ValidationStatus.VALID:
                self.console.print(f"[warning]{result.message}[/warning]")
                if not Confirm.ask("Use this ID anyway?", default=False):
                    return None

            return key_id

        return None

    def _fetch_ssh_keys(self, api_key: str, project: str | None = None) -> list[dict[str, Any]]:
        """Fetch user's SSH keys from API.

        Args:
            api_key: API key for authentication
            project: Optional project name

        Returns:
            List of SSH key dicts
        """
        try:
            # Project parameter is required by the API
            if not project:
                return []

            client = HttpClient(
                base_url=os.environ.get(
                    "MITHRIL_API_URL", os.environ.get("FLOW_API_URL", "https://api.mithril.ai")
                ),
                headers={"Authorization": f"Bearer {api_key}"},
            )

            # Get all projects to find the ID for our project name
            # This is Mithril-specific: the /v2/projects endpoint and fid field
            projects = client.request("GET", "/v2/projects", timeout_seconds=10.0)
            project_id = None

            for proj in projects:
                if proj.get("name") == project:
                    project_id = proj.get("fid")
                    break

            if not project_id:
                # Project not found
                return []

            params = {"project": project_id}

            response = client.request(
                method="GET",
                url="/v2/ssh-keys",
                params=params,
                timeout_seconds=10.0,
            )

            return response if isinstance(response, list) else []

        except Exception:
            try:
                logger.debug("Failed to fetch SSH keys", exc_info=True)
            except Exception:
                pass
            return []

    def _find_local_ssh_keys(self) -> list[Path]:
        """Find SSH public keys in user's .ssh directory.

        Returns:
            List of Path objects for *.pub files
        """
        ssh_dir = Path.home() / ".ssh"
        if not ssh_dir.exists():
            return []

        return list(ssh_dir.glob("*.pub"))
