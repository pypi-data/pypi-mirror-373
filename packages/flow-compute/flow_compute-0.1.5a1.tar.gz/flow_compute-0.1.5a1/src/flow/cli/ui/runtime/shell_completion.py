"""Shell completion support for the Flow CLI.

This module wires up interactive shell completion for common Flow CLI
commands and flags. It integrates with Click's completion system and adds
dynamic completion backed by cached data and lightweight API calls.

Features:
- Command and subcommand completion (delegated to Click).
- Dynamic task completion (IDs, names, recent indices).
- Volume completion (IDs and names with region/size).
- YAML file completion for ``flow run`` inputs.
- Instance type completion (from cached catalog when available).
- SSH key completion (platform IDs, names, and local file paths).

Environment:
- Respects ``_FLOW_COMPLETE`` to ensure logic only runs during completion.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Iterable
from pathlib import Path

from click.shell_completion import CompletionItem
from rich.panel import Panel

from flow.cli.utils.config_validator import ConfigValidator
from flow.cli.utils.theme_manager import theme_manager
from flow.errors import FlowError
from flow.sdk.factory import create_client

# Use themed console so [accent]/[success]/[warning] map to theme colors
console = theme_manager.create_console()
SEP = " · "


class CompletionCommand:
    """Manage shell completion install/uninstall and script generation.

    This helper encapsulates shell-specific behavior for Bash, Zsh, and Fish:
    - Generate completion scripts (or fall back to static templates).
    - Resolve standard installation paths per shell.
    - Install or uninstall completion scripts and activation lines.

    Attributes:
      SUPPORTED_SHELLS: Shells explicitly supported by this implementation.
      SHELL_CONFIGS: Mapping of shell to its rc file and completion directory.
    """

    SUPPORTED_SHELLS = ["bash", "zsh", "fish"]
    SHELL_CONFIGS = {
        "bash": {"rc_file": "~/.bashrc", "completion_dir": "~/.bash_completion.d"},
        "zsh": {"rc_file": "~/.zshrc", "completion_dir": "~/.zsh/completions"},
        "fish": {
            "rc_file": "~/.config/fish/config.fish",
            "completion_dir": "~/.config/fish/completions",
        },
    }

    def _render_completion_script(self, shell: str) -> str:
        """Render a shell completion script for the given shell.

        Attempts to ask Click (via the Flow entrypoint) to emit a shell-specific
        script. When unavailable, falls back to a bundled, known-good template
        that mimics Click's behavior.

        Args:
          shell: Target shell name. One of ``"bash"``, ``"zsh"``, or ``"fish"``.

        Returns:
          The full shell completion script text to be written to a file.

        Raises:
          FlowError: If the requested shell is not supported.
        """
        import shutil
        import subprocess

        flow_cmd = shutil.which("flow")
        cmd = [flow_cmd] if flow_cmd else [sys.executable, "-m", "flow.cli"]
        result = subprocess.run(
            cmd,
            env={**os.environ, "_FLOW_COMPLETE": f"{shell}_source"},
            capture_output=True,
            text=True,
        )
        if result.stdout and not result.stdout.startswith("Usage:"):
            return result.stdout

        if shell == "bash":
            return """_flow_completion() {
    local IFS=$'\n'
    local response

    response=$(env COMP_WORDS="${COMP_WORDS[*]}" COMP_CWORD=$COMP_CWORD _FLOW_COMPLETE=bash_complete flow)

    for completion in $response; do
        IFS=',' read type value <<< "$completion"

        if [[ $type == 'dir' ]]; then
            COMPREPLY=()
            compopt -o dirnames
        elif [[ $type == 'file' ]]; then
            COMPREPLY=()
            compopt -o default
        elif [[ $type == 'plain' ]]; then
            COMPREPLY+=($value)
        fi
    done

    return 0
}

complete -o nosort -F _flow_completion flow"""
        if shell == "zsh":
            return """#compdef flow

_flow_completion() {
    local -a completions
    local -a completions_with_descriptions
    local -a response
    (( ! $+commands[flow] )) && return 1

    response=("${(@f)$(env COMP_WORDS="${words[*]}" COMP_CWORD=$((CURRENT-1)) _FLOW_COMPLETE=zsh_complete flow)}")

    for type key descr in ${response}; do
        if [[ "$type" == "plain" ]]; then
            if [[ "$descr" == "_" ]]; then
                completions+=("$key")
            else
                completions_with_descriptions+=("$key":"$descr")
            fi
        elif [[ "$type" == "dir" ]]; then
            _path_files -/
            return
        elif [[ "$type" == "file" ]]; then
            _path_files
            return
        fi
    done

    if [ -n "$completions_with_descriptions" ]; then
        _describe -t commands completion completions_with_descriptions
    fi

    if [ -n "$completions" ]; then
        compadd -U -a completions
    fi
}

if [[ $zsh_eval_context[-1] == loadautofunc ]]; then
    _flow_completion "$@"
else
    compdef _flow_completion flow
fi"""
        if shell == "fish":
            return '''function _flow_completion
    set -l response (env COMP_WORDS=(commandline -cp) COMP_CWORD=(commandline -t) _FLOW_COMPLETE=fish_complete flow)

    for completion in $response
        set -l metadata (string split "," $completion)

        if test $metadata[1] = "dir"
            __fish_complete_directories
        else if test $metadata[1] = "file"
            __fish_complete_path
        else if test $metadata[1] = "plain"
            echo $metadata[2]
        end
    end
end

complete -c flow -f -a "(_flow_completion)"'''
        raise FlowError(f"Unsupported shell: {shell}")

    def _get_standard_completion_path(self, shell: str) -> Path:
        """Return the standard completion file path for a shell.

        Args:
          shell: Shell name. One of ``"bash"``, ``"zsh"``, or ``"fish"``.

        Returns:
          Path to the completion script location for the shell.

        Raises:
          FlowError: If the shell is unsupported.
        """
        if shell == "bash":
            return Path(os.path.expanduser("~/.bash_completion.d/flow"))
        if shell == "zsh":
            return Path(os.path.expanduser("~/.zsh/completions/_flow"))
        if shell == "fish":
            return Path(os.path.expanduser("~/.config/fish/completions/flow.fish"))
        raise FlowError(f"Unsupported shell: {shell}")

    def _is_completion_present(self, shell: str, rc_content: str) -> bool:
        """Check whether completion activation is already present in rc content.

        Looks for a dedicated marker comment as well as common activation lines
        used by both the dynamic and static installation flows.

        Args:
          shell: Shell name. Used to match shell-specific activation markers.
          rc_content: Full text content of the rc configuration file.

        Returns:
          True if a completion activation line or marker is present; otherwise
          False.
        """
        marker = "# Flow CLI completion"
        if marker in rc_content:
            return True
        try:
            line = self._get_completion_line(shell)
        except Exception:
            line = ""
        if line and line in rc_content:
            return True
        substr = {
            "bash": [
                "_FLOW_COMPLETE=bash_source flow",
                "python -m flow.cli completion generate bash",
            ],
            "zsh": ["_FLOW_COMPLETE=zsh_source flow", "python -m flow.cli completion generate zsh"],
            "fish": [
                "_FLOW_COMPLETE=fish_source flow | source",
                "python -m flow.cli completion generate fish",
            ],
        }.get(shell, [])
        return any(s in rc_content for s in substr)

    def _get_completion_line(self, shell: str) -> str:
        """Build the activation line to source completion for a shell.

        If the ``flow`` binary is on ``PATH``, uses ``_FLOW_COMPLETE`` with the
        binary. Otherwise, falls back to ``python -m flow.cli`` for portability.

        Args:
          shell: Shell name. One of ``"bash"``, ``"zsh"``, or ``"fish"``.

        Returns:
          A single-line shell snippet appropriate for inclusion in the user's
          rc file to enable completion.
        """
        import shutil

        if shutil.which("flow"):
            if shell == "bash":
                return 'if [ -n "${BASH_VERSION-}" ]; then eval "$(_FLOW_COMPLETE=bash_source flow)"; fi'
            if shell == "zsh":
                return (
                    'if [ -n "${ZSH_VERSION-}" ]; then eval "$(_FLOW_COMPLETE=zsh_source flow)"; fi'
                )
            if shell == "fish":
                return 'if test -n "$FISH_VERSION"; _FLOW_COMPLETE=fish_source flow | source; end'
            return f"# Unsupported shell: {shell}"
        if shell == "bash":
            return 'if [ -n "${BASH_VERSION-}" ]; then eval "$(python -m flow.cli completion generate bash)"; fi'
        if shell == "zsh":
            return 'if [ -n "${ZSH_VERSION-}" ]; then eval "$(python -m flow.cli completion generate zsh)"; fi'
        if shell == "fish":
            return 'if test -n "$FISH_VERSION"; python -m flow.cli completion generate fish | source; end'
        return f"# Run: flow completion generate {shell}"

    def _install_completion(self, shell: str | None, path: str | None) -> None:
        """Install completion script and activation for the specified shell.

        When ``path`` is provided, appends an activation line to the file at
        that path (creating it if needed). Otherwise, writes the rendered
        completion script to the shell's standard completion directory and adds
        an activation line to the shell rc file if one is not already present.
        A concise summary is printed to the themed console.

        Args:
          shell: Shell name or ``None`` to auto-detect from the environment.
          path: Optional explicit rc/config file to append an activation line.

        Returns:
          None. Writes files and prints a user-facing summary.
        """
        try:
            if not shell:
                shell = self._detect_shell()
                if not shell:
                    console.print(
                        "[error]Could not auto-detect shell. Please specify with --shell[/error]"
                    )
                    return
            # Minimal: no progress line—render a single compact summary panel

            if path:
                install_path = Path(path).expanduser()
                install_path.parent.mkdir(parents=True, exist_ok=True)
                completion_line = self._get_completion_line(shell)
                existing = install_path.read_text() if install_path.exists() else ""
                already_present = self._is_completion_present(shell, existing)
                if not already_present:
                    with open(install_path, "a") as f:
                        f.write(f"\n# Flow CLI completion\n{completion_line}\n")
                # Summary panel
                body_lines = []
                body_lines.append(f"  [muted]Shell:[/muted] {shell}")
                if already_present:
                    body_lines.append(
                        f"  [muted]Status:[/muted] Already configured in [repr.path]{install_path}[/repr.path]"
                    )
                else:
                    body_lines.append(
                        f"  [muted]Installed:[/muted] [repr.path]{install_path}[/repr.path]"
                    )
                body_lines.append(
                    f"  [muted]Activate now:[/muted] [accent]source {install_path}[/accent]"
                )
                body_lines.append(f"  [muted]Tip:[/muted] Restart your {shell} shell to persist")
                panel = Panel(
                    "\n".join(body_lines),
                    title="[accent][bold]Shell Completion[/bold][/accent]",
                    border_style=theme_manager.get_color("table.border"),
                    expand=False,
                )
                console.print("")
                console.print(panel)
                return

            target_file = self._get_standard_completion_path(shell)
            target_file.parent.mkdir(parents=True, exist_ok=True)
            script_text = self._render_completion_script(shell)
            target_file.write_text(script_text)
            # Prepare activation line in rc file if missing

            rc_file = Path(self.SHELL_CONFIGS[shell]["rc_file"]).expanduser()
            completion_line = self._get_completion_line(shell)
            rc_content = rc_file.read_text() if rc_file.exists() else ""
            added_activation = False
            if not self._is_completion_present(shell, rc_content):
                rc_file.parent.mkdir(parents=True, exist_ok=True)
                with open(rc_file, "a") as f:
                    f.write(f"\n# Flow CLI completion\n{completion_line}\n")
                added_activation = True

            # Summary panel
            body_lines = []
            body_lines.append(f"  [muted]Shell:[/muted] {shell}")
            body_lines.append(f"  [muted]Installed:[/muted] [repr.path]{target_file}[/repr.path]")
            if added_activation:
                body_lines.append(
                    f"  [muted]Updated:[/muted] [repr.path]{rc_file}[/repr.path] [muted]— activation line added[/muted]"
                )
            body_lines.append(f"  [muted]Activate now:[/muted] [accent]source {rc_file}[/accent]")
            body_lines.append(f"  [muted]Tip:[/muted] Restart your {shell} shell to persist")
            panel = Panel(
                "\n".join(body_lines),
                title="[accent][bold]Shell Completion[/bold][/accent]",
                border_style=theme_manager.get_color("table.border"),
                expand=False,
            )
            console.print("")
            console.print(panel)
        except Exception as e:
            from rich.markup import escape

            console.print(f"[error]Installation failed: {escape(str(e))}[/error]")

    def _uninstall_completion(self, shell: str | None, path: str | None) -> None:
        """Remove Flow CLI completion script and activation lines.

        Removes the standard completion file for the ``shell`` when present and
        cleans any Flow-related activation lines from the chosen rc file.
        A brief status summary is printed to the themed console.

        Args:
          shell: Shell name or ``None`` to auto-detect from the environment.
          path: Optional rc/config file to clean instead of the default.

        Returns:
          None. Files are removed or updated as a side effect.
        """
        try:
            if not shell:
                shell = self._detect_shell()
                if not shell:
                    console.print(
                        "[error]Could not auto-detect shell. Please specify with --shell[/error]"
                    )
                    return
            console.print(f"Uninstalling completion for {shell}...")

            try:
                target_file = self._get_standard_completion_path(shell)
                if target_file.exists():
                    target_file.unlink()
                    console.print(f"[success]✓[/success] Removed {target_file}")
            except Exception:
                pass

            rc_file = (
                Path(path).expanduser()
                if path
                else Path(self.SHELL_CONFIGS[shell]["rc_file"]).expanduser()
            )
            if rc_file.exists():
                content = rc_file.read_text()
                lines = content.splitlines()
                new_lines = []
                skip_next = False
                for line in lines:
                    if skip_next:
                        skip_next = False
                        continue
                    if line.strip() == "# Flow CLI completion":
                        skip_next = True
                        continue
                    if ("_FLOW_COMPLETE=" in line and "flow" in line) or (
                        "python -m flow.cli completion generate" in line
                    ):
                        continue
                    new_lines.append(line)
                if new_lines != lines:
                    rc_file.write_text(
                        "\n".join(new_lines) + ("\n" if content.endswith("\n") else "")
                    )
                    console.print(f"[success]✓[/success] Cleaned {rc_file}")

            console.print(
                "[success]✓[/success] Completion uninstalled\nYou may need to restart your shell or re-source your rc file."
            )
        except Exception as e:
            from rich.markup import escape

            console.print(f"[error]Uninstall failed: {escape(str(e))}[/error]")

    def _detect_shell(self) -> str | None:
        """Best-effort detection of the current interactive shell.

        Prefers ``$SHELL`` and falls back to inspecting the parent process name
        via ``psutil`` if available.

        Returns:
          The detected shell name (e.g. ``"bash"``, ``"zsh"``, ``"fish"``) or
          ``None`` when detection fails.
        """
        shell_path = os.environ.get("SHELL", "")
        shell_name = os.path.basename(shell_path)
        if shell_name in self.SUPPORTED_SHELLS:
            return shell_name
        try:
            import psutil

            parent = psutil.Process(os.getppid())
            parent_name = parent.name()
            for sh in self.SUPPORTED_SHELLS:
                if sh in parent_name:
                    return sh
        except Exception:
            pass
        return None

    # NOTE: The real implementation of `_get_completion_line` is defined above.
    # A duplicate recursive stub here caused infinite recursion and broke
    # completion installation. It has been removed.


# ============ Dynamic completion helpers ============


def _matches(value: str | None, needle: str) -> bool:
    """Return True if ``value`` starts with ``needle`` (case-insensitive).

    Args:
      value: Candidate string or ``None``.
      needle: Prefix to match. Empty string matches any non-empty value.

    Returns:
      True when ``value`` starts with ``needle``. False for ``None`` values.
    """
    if not value:
        return False
    if not needle:
        return True
    try:
        return value.lower().startswith(needle.lower())
    except Exception:
        return value.startswith(needle)


def _limit(items: Iterable, n: int) -> list:
    """Return at most ``n`` items from an iterable without consuming all.

    Performs a manual, bounded iteration to avoid materializing large iterables
    or generators unless necessary. Falls back to slicing on error.

    Args:
      items: Iterable source.
      n: Maximum number of items to include.

    Returns:
      A list containing up to ``n`` items.
    """
    try:
        out = []
        for i, it in enumerate(items):
            if i >= n:
                break
            out.append(it)
        return out
    except Exception:
        return list(items)[:n]


def _format_task_help(task) -> str:
    """Format a compact help string describing a task.

    Builds a short descriptor using status, instance type, instance count, and
    region when available.

    Args:
      task: Any object with ``status``, ``instance_type``, ``num_instances``,
        and ``region`` attributes.

    Returns:
      A human-friendly single-line description suitable for completion help.
    """
    try:
        status = getattr(getattr(task, "status", None), "value", str(getattr(task, "status", "")))
    except Exception:
        status = ""
    try:
        gpu = getattr(task, "instance_type", None)
        ni = int(getattr(task, "num_instances", 1) or 1)
        if gpu and ni and ni > 1 and "x" not in str(gpu):
            gpu = f"{ni}x{gpu}"
    except Exception:
        gpu = getattr(task, "instance_type", None)
    try:
        region = getattr(task, "region", None) or ""
    except Exception:
        region = ""
    parts = [p for p in (status, gpu, region) if p]
    return SEP.join(parts)


def _tasks_from_prefetch() -> list:
    """Retrieve recent tasks from the CLI prefetch cache when available.

    Returns:
      A de-duplicated list of task objects, preferring running and pending
      tasks when present; otherwise, a broader cached list. Returns an empty
      list on error.
    """
    try:
        from flow.cli.utils.prefetch import get_cached

        running = get_cached("tasks_running") or []
        pending = get_cached("tasks_pending") or []
        if running or pending:
            seen: set[str] = set()
            combined = []
            for t in list(running) + list(pending):
                tid = getattr(t, "task_id", None)
                if tid and tid not in seen:
                    combined.append(t)
                    seen.add(tid)
            return combined
        all_tasks = get_cached("tasks_all") or []
        return list(all_tasks)
    except Exception:
        return []


def complete_task_ids(ctx, args, incomplete):
    """Complete task identifiers, names, and indices.

    This completion prioritizes recent tasks and supports:
    - Numeric index aliases (from a local index cache).
    - Task IDs and names with compact help text.

    Args:
      ctx: Click context (unused but required by the interface).
      args: Full list of CLI args preceding the incomplete token.
      incomplete: Current prefix being completed.

    Returns:
      A list of ``CompletionItem`` instances. Returns an empty list when not in
      a completion context or when credentials are invalid.
    """
    try:
        if os.environ.get("_FLOW_COMPLETE") is None:
            return []
        if not ConfigValidator().validate_credentials():
            return []

        tasks = _tasks_from_prefetch()
        if not tasks:
            flow = create_client(auto_init=True)
            try:
                tasks = flow.tasks.list(limit=100)
            except Exception:
                tasks = []

        index_items: list[CompletionItem] = []
        try:
            from flow.cli.utils.task_index_cache import TaskIndexCache

            idx_map = TaskIndexCache().get_indices_map()
            for idx, tid in idx_map.items():
                if _matches(idx, incomplete):
                    index_items.append(CompletionItem(idx, f"index → {tid[:12]}…"))
        except Exception:
            pass

        task_items: list[CompletionItem] = []
        for t in tasks:
            tid = getattr(t, "task_id", None)
            name = getattr(t, "name", None)
            help_text = _format_task_help(t)
            if tid and _matches(tid, incomplete):
                task_items.append(CompletionItem(tid, help_text or (name or "")))
            if name and name != tid and _matches(name, incomplete):
                task_items.append(CompletionItem(name, help_text or (tid or "")))

        return _limit(index_items + task_items, 50)
    except Exception:
        return []


def complete_volume_ids(ctx, args, incomplete):
    """Complete volume identifiers and names with contextual annotations.

    Includes region, size, and attachment status when available. Prefers cached
    data but falls back to listing via the SDK.

    Args:
      ctx: Click context (unused).
      args: Full list of CLI args preceding the incomplete token.
      incomplete: Current prefix being completed.

    Returns:
      A list of ``CompletionItem`` instances or an empty list on error.
    """
    try:
        if os.environ.get("_FLOW_COMPLETE") is None:
            return []
        if not ConfigValidator().validate_credentials():
            return []

        volumes = []
        try:
            from flow.cli.utils.prefetch import get_cached

            volumes = get_cached("volumes_list") or []
        except Exception:
            volumes = []
        if not volumes:
            flow = create_client(auto_init=True)
            try:
                volumes = flow.volumes.list(limit=200)
            except Exception:
                volumes = []

        items: list[CompletionItem] = []
        for v in volumes:
            vid = getattr(v, "volume_id", getattr(v, "id", None))
            name = getattr(v, "name", None)
            region = getattr(v, "region", "")
            size = getattr(v, "size_gb", None)
            status = "attached" if getattr(v, "attached_to", None) else "available"
            descr_parts = [status]
            if region:
                descr_parts.append(region)
            if size is not None:
                descr_parts.append(f"{size}GB")
            descr = SEP.join(descr_parts)
            if vid and _matches(vid, incomplete):
                items.append(CompletionItem(vid, descr))
            if name and name != vid and _matches(name, incomplete):
                items.append(CompletionItem(name, f"{descr}{SEP}{vid}"))

        return _limit(items, 50)
    except Exception:
        return []


def complete_yaml_files(ctx, args, incomplete):
    """Complete YAML file paths relative to the current directory.

    Searches the project root and common subdirectories like ``configs``,
    ``config``, ``tasks``, and ``.flow``.

    Args:
      ctx: Click context (unused).
      args: Full list of CLI args preceding the incomplete token.
      incomplete: Current path prefix being completed.

    Returns:
      A sorted list of matching relative paths (strings), capped at 50.
    """
    try:
        cwd = Path.cwd()
        yaml_files = []
        for pattern in ["*.yaml", "*.yml"]:
            yaml_files.extend(cwd.glob(pattern))
        for subdir in ["configs", "config", "tasks", ".flow"]:
            subdir_path = cwd / subdir
            if subdir_path.exists():
                yaml_files.extend(subdir_path.glob("*.yaml"))
                yaml_files.extend(subdir_path.glob("*.yml"))
        results = []
        for f in yaml_files:
            path_str = str(f.relative_to(cwd))
            if path_str.startswith(incomplete):
                results.append(path_str)
        return sorted(results)[:50]
    except Exception:
        return []


def complete_instance_types(ctx, args, incomplete):
    """Complete instance types from a cached catalog or a curated fallback.

    Args:
      ctx: Click context (unused).
      args: Full list of CLI args preceding the incomplete token.
      incomplete: Current prefix being completed.

    Returns:
      A list of ``CompletionItem`` objects when catalog data is available;
      otherwise a list of strings from a small fallback set.
    """
    try:
        if os.environ.get("_FLOW_COMPLETE") is None:
            return []
        types: list[CompletionItem] = []
        try:
            from flow.cli.utils.prefetch import get_cached

            catalog = get_cached("instance_catalog") or []
            seen: set[str] = set()
            for entry in catalog:
                try:
                    itype = entry.get("instance_type") or entry.get("type") or entry.get("name")
                    if (
                        not isinstance(itype, str)
                        or not _matches(itype, incomplete)
                        or itype in seen
                    ):
                        continue
                    seen.add(itype)
                    gpu = entry.get("gpu_type") or ""
                    gcount = entry.get("gpu_count")
                    region = entry.get("region") or ""
                    parts = []
                    if gpu:
                        parts.append(str(gpu))
                    if gcount:
                        parts.append(f"{gcount} GPU")
                    if region:
                        parts.append(region)
                    types.append(CompletionItem(itype, SEP.join(parts)))
                except Exception:
                    continue
            if types:
                return _limit(types, 50)
        except Exception:
            pass

        shortlist = [
            "h100x8",
            "h100x4",
            "h100x2",
            "h100x1",
            "a100-80gbx8",
            "a100-80gbx4",
            "a100-80gbx2",
            "a100-80gbx1",
            "rtx4090x8",
            "rtx4090x4",
            "rtx4090x2",
            "rtx4090x1",
            "cpu",
        ]
        return [t for t in shortlist if _matches(t, incomplete)]
    except Exception:
        return []


def complete_container_names(ctx, args, incomplete):
    """Complete Docker container names on a remote task host.

    Reads the ``--task/-t`` argument from ``args`` and queries ``docker ps`` on
    that host via the SDK remote operations API.

    Args:
      ctx: Click context (unused).
      args: Full list of CLI args preceding the incomplete token.
      incomplete: Current prefix being completed.

    Returns:
      A list of container name strings matching the prefix, up to 50 items.
    """
    try:
        task_id = None
        for i, arg in enumerate(args):
            if arg in ("--task", "-t") and i + 1 < len(args):
                task_id = args[i + 1]
                break
        if not task_id:
            return []
        flow = create_client(auto_init=True)
        rops = flow.get_remote_operations()
        output = rops.execute_command(task_id, "docker ps --format '{{.Names}}'")
        containers = [name.strip() for name in output.strip().split("\n") if name.strip()]
        return [name for name in containers if name.startswith(incomplete)][:50]
    except Exception:
        return []


def complete_ssh_key_identifiers(ctx, args, incomplete):
    """Complete SSH key identifiers from local files and platform keys.

    Scans ``~/.ssh`` and ``~/.flow/keys`` for local keys and, when credentials
    are valid, augments suggestions with platform-managed keys.

    Args:
      ctx: Click context (unused).
      args: Full list of CLI args preceding the incomplete token.
      incomplete: Current prefix being completed (path or identifier).

    Returns:
      A list of ``CompletionItem`` instances describing candidate keys.
    """
    try:
        if os.environ.get("_FLOW_COMPLETE") is None:
            return []
        items: list[CompletionItem] = []
        try:
            ssh_dir = Path.home() / ".ssh"
            flow_keys = Path.home() / ".flow" / "keys"
            for d in (ssh_dir, flow_keys):
                if d.exists():
                    for p in d.iterdir():
                        if (
                            p.is_file()
                            and (p.suffix in {"", ".pub"})
                            and not p.name.endswith(".json")
                        ):
                            s = str(p)
                            if _matches(s, incomplete) or _matches(p.name, incomplete):
                                items.append(CompletionItem(s, "local key"))
        except Exception:
            pass
        try:
            if ConfigValidator().validate_credentials():
                flow = create_client(auto_init=True)
                manager = flow.get_ssh_key_manager()
                keys = manager.list_keys()
                for k in keys:
                    fid = getattr(k, "fid", None)
                    name = getattr(k, "name", None)
                    if fid and _matches(fid, incomplete):
                        items.append(CompletionItem(fid, name or "platform key"))
                    if name and _matches(name, incomplete):
                        items.append(CompletionItem(name, fid or "platform key"))
        except Exception:
            pass
        return _limit(items, 50)
    except Exception:
        return []


# Export command instance
command = CompletionCommand()
