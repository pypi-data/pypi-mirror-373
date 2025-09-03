from __future__ import annotations

"""Orchestration for the Generic Setup Wizard.

This class coordinates rendering, input, validation, and field configuration
using the modular helpers in this package.
"""

import os
import signal
import sys
from typing import Any

from rich.console import Console

from flow.core.setup_adapters import FieldType, ProviderSetupAdapter
from flow.core.setup_wizard.field_configurator import configure_field
from flow.core.setup_wizard.menu_selector import interactive_menu_select
from flow.core.setup_wizard.ui_renderer import UIRenderer, build_selector_header


class GenericSetupWizard:
    """Generic setup wizard that works with any provider adapter."""

    @staticmethod
    def _coerce_to_type(field, value):
        if field.field_type == FieldType.BOOLEAN:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ("true", "yes", "1", "on")
            return bool(value)
        return value

    def __init__(self, console: Console, adapter: ProviderSetupAdapter):
        self.console = console
        self.adapter = adapter
        self.ui = UIRenderer(console)
        self.config: dict[str, Any] = {}
        self._validation_cache: dict[str, tuple[str, bool]] = {}
        self._recently_updated: set[str] = set()
        self._last_status_header: str | None = None

    def run(self) -> bool:
        """Run the setup wizard flow."""

        # Keyboard interrupt handler
        def keyboard_interrupt_handler(signum, frame):
            self.console.print("\n\n[warning]Setup cancelled[/warning]")
            try:
                os.system("stty sane 2>/dev/null || true")
            except Exception:
                pass
            sys.exit(0)

        old_handler = signal.signal(signal.SIGINT, keyboard_interrupt_handler)
        try:
            self.ui.render_welcome(self.adapter)

            # Opportunistic prefetch
            try:
                from flow.cli.utils.prefetch import prefetch_for_command

                prefetch_for_command(["flow", "init"])
            except Exception:
                pass

            existing_config = self.adapter.detect_existing_config()

            # Render the status panel only once. If configuration is incomplete,
            # the configuration loop will render (and re-render) the status as
            # needed. For a fully-configured environment, show the status here
            # before presenting the completion actions. This avoids duplicate
            # status/SSH panels in typical interactive flows.
            if self._is_fully_configured(existing_config):
                if not self._show_configuration_status(existing_config):
                    return False
                proceed = self._handle_fully_configured(existing_config)
                if not proceed:
                    return False
                try:
                    if self.config:
                        final_config = existing_config.copy()
                        final_config.update(self.config)
                        if not self.adapter.save_configuration(final_config):
                            self.console.print("\n[error]Failed to save configuration[/error]")
                            return False
                    return True
                except Exception:
                    return True
            else:
                # Let the configuration loop own status rendering to prevent
                # duplicating the status/SSH panels.
                if not self._configure_missing_items(existing_config):
                    return False

                final_config = existing_config.copy()
                final_config.update(self.config)
                if not self.adapter.save_configuration(final_config):
                    self.console.print("\n[error]Failed to save configuration[/error]")
                    return False
                if self._verify_configuration(final_config):
                    self.ui.render_completion(self.adapter)
                    return True
                else:
                    self.console.print(
                        "\n[warning]Setup completed but verification failed. Check your settings.[/warning]"
                    )
                    return False
        finally:
            signal.signal(signal.SIGINT, old_handler)

    def _update_validation_cache(self, config: dict[str, Any]) -> None:
        """Update local validation cache for fields where it is cheap and useful."""
        # Keep this non-blocking: do fast, local validation only (no network).
        # Network verification happens explicitly during field configuration
        # and the final verification step, avoiding a "hung" feeling before
        # the menu appears.
        try:
            fields = self.adapter.get_configuration_fields()
            for f in fields:
                if f.name != "api_key":
                    continue
                v = config.get("api_key")
                if not v:
                    self._validation_cache.pop("api_key", None)
                    continue
                sval = str(v)
                cached = self._validation_cache.get("api_key")
                if cached and cached[0] == sval:
                    continue
                try:
                    from flow.cli.utils.config_validator import ConfigValidator
                    from flow.cli.utils.config_validator import ValidationStatus as _VS

                    provider = None
                    try:
                        provider = str(self.adapter.get_provider_name())
                    except Exception:
                        provider = None
                    validator = ConfigValidator(provider=provider)
                    res = validator.validate_api_key_format(sval, provider)
                    is_valid = res.status == _VS.VALID
                except Exception:
                    # Fall back to "unknown" validity to avoid blocking
                    is_valid = False
                self._validation_cache["api_key"] = (sval, is_valid)
        except Exception:
            # Never let validation impact the UI flow
            pass

    def _show_configuration_status(self, existing_config: dict[str, Any]) -> bool:
        try:
            merged_config = {**existing_config, **self.config}
            self._update_validation_cache(merged_config)
            status_table = self.ui.build_status_table(
                self.adapter,
                existing_config,
                self.config,
                self._validation_cache,
                self._recently_updated,
            )
            show_demo_hint = False
            try:
                if str(self.adapter.get_provider_name()).lower() == "mock":
                    required_missing = any(
                        (f.required and not (merged_config.get(f.name)))
                        for f in self.adapter.get_configuration_fields()
                    )
                    show_demo_hint = required_missing
            except Exception:
                pass
            self.ui.render_status_panel(status_table, self.adapter, show_demo_hint=show_demo_hint)
            self._last_status_header = build_selector_header(self.adapter, merged_config)
            return True
        except Exception:
            return True

    def _is_fully_configured(self, existing_config: dict[str, Any]) -> bool:
        fields = self.adapter.get_configuration_fields()
        required_fields = [f for f in fields if f.required]
        for f in required_fields:
            if not self._is_field_effectively_configured(f, existing_config):
                return False
        return True

    def _is_field_effectively_configured(self, field, existing_config: dict[str, Any]) -> bool:
        value = self.config.get(field.name) or existing_config.get(field.name)
        if value in (None, ""):
            return False
        name = field.name
        try:
            if name == "api_key":
                v = str(value)
                if v.startswith("YOUR_"):
                    return False
                return v.startswith("fkey_") and len(v) >= 20
            if name == "project":
                v = str(value).strip()
                if v.startswith("YOUR_"):
                    return False
                return len(v) > 0
            if name == "default_ssh_key":
                v = str(value).strip()
                return v == "_auto_" or v.startswith("sshkey_")
        except Exception:
            return False
        return True

    def _handle_fully_configured(self, existing_config: dict[str, Any]) -> bool:
        from flow.cli.ui.presentation.visual_constants import get_status_display
        from flow.cli.utils.theme_manager import theme_manager

        self.console.print(
            f"\n{get_status_display('configured', 'All required components are configured', icon_style='check')}"
        )
        menu_options = [
            ("verify", "Verify and finish (recommended)", ""),
            ("reconfig", "Change configuration", ""),
            ("exit", "Exit now (skip verification)", ""),
        ]
        self.console.print()
        header = build_selector_header(self.adapter, existing_config)
        brand_prefix = (
            "Mithril Flow Setup"
            if str(self.adapter.get_provider_name()).lower() == "mithril"
            else "Flow Setup"
        )
        action = interactive_menu_select(
            options=menu_options,
            title="What would you like to do?",
            default_index=0,
            extra_header_html=header,
            breadcrumbs=[brand_prefix, "Complete"],
        )
        # If selection couldn't be obtained (non-interactive/EOF), default to verify
        if action is None:
            action = "verify"
        if action == "verify":
            success, error = self.adapter.verify_configuration(existing_config)
            if success:
                success_color = theme_manager.get_color("success")
                self.console.print(
                    f"\n[{success_color}]✓ Configuration verified successfully![/{success_color}]"
                )
                return True
            else:
                self.console.print(f"\n[warning]Verification failed: {error}[/warning]")
                return self._configure_missing_items(existing_config)
        elif action == "reconfig":
            return self._configure_missing_items(existing_config)
        elif action == "exit":
            missing = [
                f.name
                for f in self.adapter.get_configuration_fields()
                if f.required and not self._is_field_effectively_configured(f, existing_config)
            ]
            if missing:
                self.console.print(
                    f"\n[warning]Warning: Required items not configured: {', '.join(missing)}[/warning]"
                )
                from flow.core.setup_wizard.prompter import confirm_with_escape

                exit_anyway = confirm_with_escape("Exit anyway?", default=False)
                if not exit_anyway:
                    return False
            self.console.print("\n[dim]Exiting without verification.[/dim]")
            return True
        return True

    def _configure_missing_items(self, existing_config: dict[str, Any]) -> bool:
        fields = self.adapter.get_configuration_fields()
        # Always add a spacer before the selector so returning to the menu
        # after a change doesn't butt up against the panels.
        spacer_printed = False
        self._shown_empty_choice_hint: set[str] = set()
        while True:
            try:
                self.console.clear()
            except Exception:
                pass
            try:
                detected = self.adapter.detect_existing_config()
                current_state = {**detected, **self.config}
                self._show_configuration_status(current_state)
                existing_config.update(detected)
            except Exception:
                pass

            menu_options = []
            choice_map: dict[str, str] = {}
            choice_num = 1
            for field in fields:
                existing_value = existing_config.get(field.name)
                field_title = field.display_name or field.name.replace("_", " ").title()
                if existing_value:
                    if getattr(field, "mask_display", False):
                        from flow.sdk.helpers.masking import mask_strict_last4

                        display_val = mask_strict_last4(existing_value)
                    else:
                        display_val = existing_value
                    display_text = f"[{choice_num}] Reconfigure {field_title}"
                    description = ""
                else:
                    display_text = f"[{choice_num}] Configure {field_title}"
                    try:
                        depends_on = getattr(field, "depends_on", None) or []
                        missing = [
                            d
                            for d in depends_on
                            if not (existing_config.get(d) or self.config.get(d))
                        ]
                        if missing:
                            description = f"Requires: {', '.join(m.replace('_', ' ').title() for m in missing)}"
                            menu_options.append(
                                (
                                    f"disabled_{choice_num}",
                                    f"[{choice_num}] {field_title} (disabled)",
                                    description,
                                )
                            )
                            choice_num += 1
                            continue
                        else:
                            description = ""
                    except Exception:
                        description = ""
                menu_options.append((str(choice_num), display_text, description))
                choice_map[str(choice_num)] = field.name
                choice_num += 1

            menu_options.append(("done", f"[{choice_num}] Done (save and exit)", ""))
            # Print a spacer line before the menu every time to keep
            # consistent padding between status panels and the selector.
            self.console.print()
            spacer_printed = True

            try:
                default_index = 0
                first_missing_menu_index = None
                for idx, field in enumerate(fields):
                    if not self._is_field_effectively_configured(field, existing_config):
                        chosen_key = None
                        for k, v in choice_map.items():
                            if v == field.name:
                                chosen_key = k
                                break
                        if chosen_key is not None:
                            for mi, (val, _t, _d) in enumerate(menu_options):
                                if val == chosen_key:
                                    first_missing_menu_index = mi
                                    break
                        break
                if first_missing_menu_index is not None:
                    default_index = first_missing_menu_index
                else:
                    default_index = len(menu_options) - 1
            except Exception:
                default_index = 0

            header = self._last_status_header
            brand_prefix = (
                "Mithril Flow Setup"
                if str(self.adapter.get_provider_name()).lower() == "mithril"
                else "Flow Setup"
            )
            choice = interactive_menu_select(
                options=menu_options,
                title="Configuration Menu",
                default_index=default_index,
                extra_header_html=header,
                breadcrumbs=[brand_prefix, "Configuration"],
            )

            # If selection couldn't be obtained (non-interactive/EOF), fall back to Done
            if choice is None:
                choice = "done"
            if choice == "done":
                required_fields = [f for f in fields if f.required]
                missing = []
                for field in required_fields:
                    if not existing_config.get(field.name) and not self.config.get(field.name):
                        missing.append(field.display_name or field.name.replace("_", " ").title())
                if missing:
                    self.console.print(
                        f"\n[warning]Warning: Required items not configured: {', '.join(missing)}[/warning]"
                    )
                    from flow.core.setup_wizard.prompter import confirm_with_escape

                    exit_anyway = confirm_with_escape("Exit anyway?", default=False)
                    if not exit_anyway:
                        continue
                return True

            field_name = choice_map.get(choice)
            if field_name:
                result = configure_field(
                    console=self.console,
                    adapter=self.adapter,
                    field_name=field_name,
                    context=existing_config,
                    current_config=self.config,
                    coerce_fn=self._coerce_to_type,
                    status_header=self._last_status_header,
                    shown_empty_choice_hint=self._shown_empty_choice_hint,
                )
                if result:
                    self.config[field_name] = result.value
                    existing_config[field_name] = result.value
                    try:
                        self._recently_updated.add(field_name)
                    except Exception:
                        pass
        return True

    def _verify_configuration(self, config: dict[str, Any]) -> bool:
        from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

        from flow.cli.ui.presentation.visual_constants import format_text
        from flow.cli.utils.theme_manager import theme_manager
        from flow.core.setup_wizard.ui_renderer import AnimatedDots

        self.console.print(f"\n{format_text('title', 'Verifying Configuration')}")
        self.console.print("─" * 50)

        import time as _time

        start_time = _time.time()
        dots = AnimatedDots()
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=self.console,
            transient=True,
        ) as progress:
            task = progress.add_task("Connecting to API...", total=None)
            try:
                progress.update(task, description=f"Connecting to API{dots.next()}")
                _time.sleep(0.5)
                progress.update(task, description=f"Testing configuration{dots.next()}")
                success, error = self.adapter.verify_configuration(config)
                elapsed = _time.time() - start_time
                if success:
                    success_color = theme_manager.get_color("success")
                    progress.update(
                        task,
                        description=f"[{success_color}]✓ Configuration verified! ({elapsed:.1f}s)[/{success_color}]",
                    )
                    return True
                else:
                    progress.update(
                        task, description=f"[error]✗ Verification failed ({elapsed:.1f}s)[/error]"
                    )
                    self.console.print(f"\n[error]Error:[/error] {error}")
                    return False
            except Exception as e:
                elapsed = _time.time() - start_time
                progress.update(
                    task, description=f"[error]✗ Verification failed ({elapsed:.1f}s)[/error]"
                )
                self.console.print(f"\n[error]Error:[/error] {e}")
                return False
