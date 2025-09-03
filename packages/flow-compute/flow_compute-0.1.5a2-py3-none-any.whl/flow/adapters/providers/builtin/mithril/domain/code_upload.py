"""Code upload orchestration service.

Provides a high-level API to decide and perform code upload (embedded vs SCP)
without keeping this logic in the provider facade.
"""

from __future__ import annotations

import base64
import logging
import os
import tarfile
import tempfile
from pathlib import Path

from flow.adapters.transport.code_transfer import CodeTransferConfig, CodeTransferManager
from flow.sdk.models import Task, TaskConfig
from flow.core.ignore import build_exclude_patterns as _build_excludes


class CodeUploadPlan:
    def __init__(self, use_scp: bool) -> None:
        self.use_scp = use_scp


class CodeUploadService:
    def __init__(self, provider) -> None:
        self._provider = provider
        self._logger = logging.getLogger(__name__)

    def plan(self, config: TaskConfig) -> CodeUploadPlan:
        strategy = (getattr(config, "upload_strategy", None) or "embedded").lower()
        use_scp = strategy in {"scp", "rsync", "ssh"}
        return CodeUploadPlan(use_scp=use_scp)

    def maybe_package_embedded(self, config: TaskConfig) -> TaskConfig:
        # Package via service to avoid duplication in provider
        return self.package_local_code(config)

    def initiate_async_upload(self, task: Task, config: TaskConfig) -> None:
        manager = CodeTransferManager(provider=self._provider)
        # Fire-and-forget in background via provider public helper
        # Delegate to service implementation to minimize provider surface
        self.start_background_upload(manager, task, CodeTransferConfig())

    # -------- background upload (moved from provider) --------
    def start_background_upload(
        self, manager: CodeTransferManager, task: Task, transfer_config: CodeTransferConfig
    ) -> None:
        """Start background code upload using provided transfer manager.

        Updates transient task flags (_upload_pending/_upload_failed/_upload_error)
        and logs progress. Extracted from provider to reduce façade size.
        """
        import threading

        self._logger.info(f"Starting background code upload for task {task.task_id}")

        def upload_worker():
            try:
                result = manager.transfer_code_to_task(task, transfer_config)
                try:
                    task._upload_pending = False  # type: ignore[attr-defined]
                    task._upload_failed = False  # type: ignore[attr-defined]
                    task._upload_error = None  # type: ignore[attr-defined]
                except Exception:
                    pass
                self._logger.info(
                    f"Code upload completed for {task.task_id}: {result.files_transferred} files, {result.transfer_rate}"
                )
            except Exception as e:
                import traceback

                self._logger.error(f"Background code upload failed for {task.task_id}: {e}")
                self._logger.debug(f"Traceback: {traceback.format_exc()}")
                try:
                    task._upload_pending = False  # type: ignore[attr-defined]
                    task._upload_failed = True  # type: ignore[attr-defined]
                    task._upload_error = str(e)  # type: ignore[attr-defined]
                except Exception:
                    pass

        threading.Thread(target=upload_worker, daemon=True).start()

    # -------- direct SCP upload (moved from provider) --------
    def upload_code_to_task(
        self,
        task_id: str,
        *,
        source_dir: Path | None = None,
        timeout: int = 600,
        console: object | None = None,
        target_dir: str = "/workspace",
        progress_reporter: object | None = None,
        git_incremental: bool | None = None,
    ) -> object:
        """Upload code to an existing task using SCP via shared transport.

        Returns the transfer result from CodeTransferManager.
        """
        # Fetch task (will wait for SSH later inside manager if needed)
        task = self._provider.get_task(task_id)

        # Lazy import to avoid Rich hard dependency in non-CLI contexts
        try:
            from rich.console import Console as _Console  # type: ignore
        except Exception:  # pragma: no cover - rich is optional at runtime
            _Console = None  # type: ignore

        from flow.adapters.transport.code_transfer import (
            CodeTransferConfig as _Cfg,
        )
        from flow.adapters.transport.code_transfer import (
            CodeTransferManager as _Mgr,
        )
        from flow.adapters.transport.code_transfer import (
            RichProgressReporter as _Reporter,
        )

        # Allow caller to suppress provider prints by passing a NullConsole-compatible object
        if _Console is not None and console is None and progress_reporter is None:
            console = _Console()
        reporter_to_use = progress_reporter or (_Reporter(console) if console is not None else None)

        # Normalize source_dir to Path when provided as str
        try:
            if source_dir is not None and not isinstance(source_dir, Path):
                from os import PathLike as _PathLike  # type: ignore

                if isinstance(source_dir, (str, _PathLike)):
                    source_dir = Path(source_dir)  # type: ignore[assignment]
        except Exception:
            pass

        transfer_manager = _Mgr(provider=self._provider, progress_reporter=reporter_to_use)

        # Configure and execute upload
        code_root_val = getattr(getattr(task, "config", None), "code_root", None)
        config = _Cfg(
            source_dir=source_dir or (Path(code_root_val) if code_root_val else Path.cwd()),
            target_dir=target_dir,
            ssh_timeout=timeout,
            transfer_timeout=timeout,
            git_incremental=git_incremental,
        )

        result = transfer_manager.transfer_code_to_task(task, config)

        # Print concise summary for UX only when a console is used
        try:
            if console is not None:
                if result.bytes_transferred == 0 and result.files_transferred == 0:
                    task_ref = task.name or task.task_id
                    src = str(config.source_dir)
                    dst = target_dir
                    console.print(f"[dim]No changes to sync ({src} → {task_ref}:{dst})[/dim]")
                else:
                    size_mb = (result.bytes_transferred or 0) / (1024 * 1024)
                    console.print(
                        f"[success]✓[/success] Upload complete: {result.files_transferred} files, {size_mb:.1f} MB → {(task.name or task.task_id)}:{target_dir} @ {result.transfer_rate}"
                    )
        except Exception:
            # Avoid failing UX on print issues
            pass

        self._logger.info(
            f"Code uploaded successfully to {task_id} - Files: {result.files_transferred}, Size: {result.bytes_transferred / (1024 * 1024):.1f} MB, Rate: {result.transfer_rate}"
        )
        return result

    # -------- strategy decisions --------
    def should_use_scp_upload(self, config: TaskConfig) -> bool:
        """Determine if SCP upload should be used instead of embedded."""
        # Explicit strategy wins
        try:
            if getattr(config, "upload_strategy", None) == "scp":
                return True
            if getattr(config, "upload_strategy", None) in ["embedded", "none"]:
                return False
        except Exception:
            pass

        # Auto mode - estimate compressed size
        try:
            try:
                code_root_value = getattr(config, "code_root", None)
            except Exception:
                code_root_value = None
            cwd = Path(code_root_value) if code_root_value else Path.cwd()

            total_size = 0
            file_count = 0

            # Build exclude patterns locally (provider context may not expose legacy helpers)
            excludes = self.build_exclude_patterns(cwd)

            for root, dirs, files in os.walk(cwd):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if not any(Path(root, d).match(p) for p in excludes)]

                for file in files:
                    file_path = Path(root) / file
                    if any(file_path.match(p) for p in excludes):
                        continue
                    try:
                        total_size += file_path.stat().st_size
                        file_count += 1
                    except OSError:
                        continue

            estimated_compressed = total_size * 0.4  # heuristic
            if estimated_compressed > 8 * 1024:  # > 8KB
                self._logger.info(
                    f"Auto-selected SCP upload: {file_count} files, ~{estimated_compressed / 1024:.1f}KB compressed"
                )
                return True
            else:
                self._logger.info(
                    f"Auto-selected embedded upload: {file_count} files, ~{estimated_compressed / 1024:.1f}KB compressed"
                )
                return False
        except Exception as e:
            self._logger.warning(f"Error estimating project size: {e}. Using embedded upload.")
            return False

    # -------- embedded packaging --------
    def package_local_code(self, config: TaskConfig) -> TaskConfig:
        """Create gzipped tar archive and embed into config env as base64.

        Returns an updated TaskConfig with `_FLOW_CODE_ARCHIVE` set in `env`, or
        the original config when nothing should be packaged.
        """
        # Resolve code root (defaults to CWD)
        try:
            code_root_value = getattr(config, "code_root", None)
        except Exception:
            code_root_value = None
        cwd = Path(code_root_value) if code_root_value else Path.cwd()

        # Build excludes using the shared helper
        excludes = set(self.build_exclude_patterns(cwd))
        # Add packaging-specific excludes
        excludes.update(
            {
                ".env",
                ".venv",
                "venv",
                "*.log",
                ".tox",
                ".coverage",
                "htmlcov",
                ".idea",
                ".vscode",
                "dist",
                "build",
            }
        )

        # Collect files
        files_to_package: list[Path] = []
        for root, dirs, files in os.walk(cwd):
            root_path = Path(root)
            # Filter directories
            dirs[:] = [d for d in dirs if not any((root_path / d).match(p) for p in excludes)]
            for file in files:
                file_path = root_path / file
                if not any(file_path.match(pattern) for pattern in excludes):
                    files_to_package.append(file_path)

        if not files_to_package:
            self._logger.info("No files to upload (empty directory or all files excluded)")
            return config

        # Create archive and embed
        with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp_file:
            try:
                with tarfile.open(tmp_file.name, "w:gz") as tar:
                    for file_path in files_to_package:
                        rel_path = file_path.relative_to(cwd)
                        tar.add(file_path, arcname=str(rel_path))

                size_bytes = os.path.getsize(tmp_file.name)
                size_mb = size_bytes / (1024 * 1024)
                self._logger.info(f"Code archive size: {size_mb:.2f}MB")

                if size_mb > 10:  # 10MB limit
                    self._logger.info(
                        "Project size %.1fMB exceeds embedded limit (10MB). Falling back to upload_strategy='scp'",
                        size_mb,
                    )
                    try:
                        return config.model_copy(update={"upload_strategy": "scp"})
                    except Exception:
                        return config

                with open(tmp_file.name, "rb") as f:
                    code_archive = base64.b64encode(f.read()).decode("ascii")

                updated_env = dict(getattr(config, "env", {}) or {})
                updated_env["_FLOW_CODE_ARCHIVE"] = code_archive
                try:
                    return config.model_copy(update={"env": updated_env})
                except Exception:
                    # Best-effort – return original if cloning fails
                    return config
            finally:
                try:
                    os.unlink(tmp_file.name)
                except Exception:
                    pass

    # -------- shared exclude patterns --------
    def build_exclude_patterns(self, base: Path | None = None) -> list[str]:
        """Return unified exclude patterns for packaging and upload.

        Uses central builder: prefers `.flowignore`, falls back to `.gitignore`,
        else a minimal default set.
        """
        spec = _build_excludes(base or Path.cwd())
        return list(spec.patterns)

        # Create archive and embed
        with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp_file:
            try:
                with tarfile.open(tmp_file.name, "w:gz") as tar:
                    for file_path in files_to_package:
                        rel_path = file_path.relative_to(cwd)
                        tar.add(file_path, arcname=str(rel_path))

                size_bytes = os.path.getsize(tmp_file.name)
                size_mb = size_bytes / (1024 * 1024)
                self._logger.info(f"Code archive size: {size_mb:.2f}MB")

                if size_mb > 10:  # 10MB limit
                    self._logger.info(
                        f"Project size {size_mb:.1f}MB exceeds embedded limit (10MB). Falling back to upload_strategy='scp'"
                    )
                    try:
                        return config.model_copy(update={"upload_strategy": "scp"})
                    except Exception:
                        return config

                with open(tmp_file.name, "rb") as f:
                    code_archive = base64.b64encode(f.read()).decode("ascii")

                updated_env = dict(getattr(config, "env", {}) or {})
                updated_env["_FLOW_CODE_ARCHIVE"] = code_archive
                try:
                    return config.model_copy(update={"env": updated_env})
                except Exception:
                    # Best-effort – return original if cloning fails
                    return config
            finally:
                try:
                    os.unlink(tmp_file.name)
                except Exception:
                    pass
