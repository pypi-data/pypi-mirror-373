from __future__ import annotations

import logging
import hashlib
import os
import re
import subprocess
import tempfile
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from flow.errors import FlowError
from flow.core.ignore import build_exclude_patterns

logger = logging.getLogger(__name__)


@dataclass
class TransferProgress:
    bytes_transferred: int
    total_bytes: int | None
    percentage: float | None
    speed: str | None
    eta: str | None
    current_file: str | None

    @property
    def is_complete(self) -> bool:
        return self.percentage is not None and self.percentage >= 100


@dataclass
class TransferResult:
    success: bool
    bytes_transferred: int
    duration_seconds: float
    files_transferred: int
    error_message: str | None = None
    final_target: str | None = None
    mode: str | None = None
    ignore_source: str | None = None
    ignore_hash: str | None = None

    @property
    def transfer_rate(self) -> str:
        if self.duration_seconds == 0:
            return "N/A"
        rate_mbps = (self.bytes_transferred / self.duration_seconds) / (1024 * 1024)
        return f"{rate_mbps:.2f} MB/s"


class TransferError(FlowError):
    pass


class ITransferStrategy(Protocol):
    def transfer(
        self,
        source: Path,
        target: str,
        connection: SSHConnectionInfo,
        progress_callback: Callable[[TransferProgress], None] | None = None,
        *,
        git_incremental: bool | None = None,
    ) -> TransferResult: ...


class RsyncTransferStrategy:
    def __init__(self):
        self.rsync_path = self._find_rsync()

    def transfer(
        self,
        source: Path,
        target: str,
        connection: SSHConnectionInfo,
        progress_callback: Callable[[TransferProgress], None] | None = None,
        *,
        git_incremental: bool | None = None,
    ) -> TransferResult:
        if not source.exists():
            raise TransferError(f"Source path does not exist: {source}")
        if not source.is_dir():
            raise TransferError(f"Source must be a directory: {source}")

        exclude_file, ignore_source = self._create_exclude_file(source)
        # Compute a stable hash of the ignore patterns for handshake/markers
        try:
            spec = build_exclude_patterns(source)
            _h = hashlib.sha256()
            for p in sorted(spec.patterns):
                _h.update(p.encode("utf-8", "ignore") + b"\n")
            ignore_hash = _h.hexdigest()
        except Exception:
            ignore_hash = None
        files_from_file: Path | None = None
        files_from_is_from0 = False
        files_from_count = 0
        final_target = target
        mode_used = "full"
        try:
            git_files = self._get_git_changed_files(source, enabled=git_incremental)
            if git_files and git_files.get("list_path"):
                files_from_file = git_files["list_path"]
                files_from_is_from0 = git_files.get("from0", False)
                files_from_count = git_files.get("count", 0)
                if files_from_count == 0:
                    # Empty git diff provides no safety guarantee about the remote state.
                    # Fall back to a full scan to ensure remote receives the baseline.
                    try:
                        logger.info(
                            "Incremental list is empty; falling back to full scan to ensure correctness"
                        )
                    except Exception:
                        pass
                    files_from_file = None
                    files_from_is_from0 = False
                else:
                    mode_used = "incremental"
            elif git_incremental:
                try:
                    logger.info(
                        "Incremental upload requested but Git repository not detected or no changes; using full scan"
                    )
                except Exception:
                    pass
        except Exception:
            files_from_file = None

        try:
            # Observability on mode and ignore source
            try:
                mode = "incremental" if files_from_file else "full"
                logger.info(
                    f"Rsync upload mode={mode}, ignores={ignore_source} (source={source})"
                )
            except Exception:
                pass

            cmd = self._build_rsync_command(
                source,
                target,
                connection,
                exclude_file,
                files_from=files_from_file,
                use_from0=files_from_is_from0,
            )

            preflight_cmd = cmd.copy()
            preflight_cmd.insert(1, "--dry-run")
            preflight_cmd.insert(2, "--itemize-changes")
            # Include --stats so we can estimate total bytes and seed a realistic ETA
            preflight_cmd.insert(3, "--stats")

            preflight = subprocess.run(preflight_cmd, capture_output=True, text=True)
            if preflight.returncode == 0:
                has_changes = False
                estimated_bytes: int | None = None
                for line in preflight.stdout.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith(">") or line.startswith("cd+") or "*deleting" in line:
                        has_changes = True
                        break
                # Parse stats for a rough size estimate
                try:
                    for line in preflight.stdout.splitlines():
                        if "Total file size" in line:
                            m = re.search(r"([\d,]+)\s*bytes", line)
                            if m:
                                estimated_bytes = int(m.group(1).replace(",", ""))
                                break
                except Exception:
                    estimated_bytes = None
                if not has_changes:
                    return TransferResult(
                        True,
                        0,
                        0.0,
                        0,
                        None,
                        final_target,
                        mode_used,
                        ignore_source,
                        ignore_hash,
                    )
                # Allow the progress adapter to seed timeline estimate before the real transfer
                try:
                    if (
                        estimated_bytes
                        and progress_callback
                        and hasattr(progress_callback, "seed_estimated_seconds")
                    ):
                        # Assume a conservative throughput; allow env override
                        try:
                            mbps = float(os.environ.get("FLOW_UPLOAD_SEED_MBPS", "25"))
                        except Exception:
                            mbps = 25.0
                        mbps = max(1.0, mbps)
                        seconds = max(5, int(estimated_bytes / (mbps * 1024 * 1024)))
                        # Pad a bit to account for scanning overhead
                        seconds = int(seconds * 1.2)
                        progress_callback.seed_estimated_seconds(seconds)  # type: ignore[attr-defined]
                except Exception:
                    pass

            start_time = time.time()
            try:
                result = self._execute_with_progress(cmd, progress_callback, source_path=source)
                duration = time.time() - start_time
                return TransferResult(
                    True,
                    bytes_transferred=result["bytes_transferred"],
                    duration_seconds=duration,
                    files_transferred=result["files_transferred"],
                    error_message=None,
                    final_target=final_target,
                    mode=mode_used,
                    ignore_source=ignore_source,
                    ignore_hash=ignore_hash,
                )
            except Exception as e:
                msg = str(e)
                # Fallback 1: git optimized list may include deleted paths
                if files_from_file and ("No such file or directory" in msg or "stat:" in msg):
                    fallback_cmd = self._build_rsync_command(
                        source,
                        target,
                        connection,
                        exclude_file,
                        files_from=None,
                        use_from0=False,
                    )
                    start_time = time.time()
                    result = self._execute_with_progress(
                        fallback_cmd, progress_callback, source_path=source
                    )
                    duration = time.time() - start_time
                    return TransferResult(
                        True,
                        result["bytes_transferred"],
                        duration,
                        result["files_transferred"],
                        None,
                        final_target=final_target,
                        mode="full",
                        ignore_source=ignore_source,
                        ignore_hash=ignore_hash,
                    )
                # Fallback 2: remote target not writable (e.g., /workspace). Retry to home (~).
                denied_markers = [
                    "Permission denied",
                    f'mkdir "{target}" failed',
                    "error in file IO (code 11)",
                ]
                if target != "~" and any(m in msg for m in denied_markers):
                    try:
                        fallback_cmd = self._build_rsync_command(
                            source,
                            "~",
                            connection,
                            exclude_file,
                            files_from=files_from_file,
                            use_from0=files_from_is_from0,
                        )
                        final_target = "~"
                        start_time = time.time()
                        result = self._execute_with_progress(
                            fallback_cmd, progress_callback, source_path=source
                        )
                        duration = time.time() - start_time
                        return TransferResult(
                            True,
                            result["bytes_transferred"],
                            duration,
                            result["files_transferred"],
                            None,
                            final_target=final_target,
                            mode=mode_used,
                            ignore_source=ignore_source,
                            ignore_hash=ignore_hash,
                        )
                    except Exception:
                        pass
                raise
        except Exception as e:
            logger.error(f"Rsync transfer failed: {e}")
            raise TransferError(f"Transfer failed: {e!s}") from e
        finally:
            if exclude_file and exclude_file.exists():
                exclude_file.unlink()
            if files_from_file and files_from_file.exists():
                try:
                    files_from_file.unlink()
                except Exception:
                    pass

    def _find_rsync(self) -> str:
        try:
            result = subprocess.run(["which", "rsync"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        for path in ["/usr/bin/rsync", "/usr/local/bin/rsync", "/opt/homebrew/bin/rsync"]:
            if Path(path).exists():
                return path
        raise TransferError("rsync not found. Please install rsync")

    def _create_exclude_file(self, source: Path) -> tuple[Path | None, str]:
        spec = build_exclude_patterns(source)
        tmp = tempfile.NamedTemporaryFile(mode="w", delete=False, prefix="flow-rsync-exclude-")
        try:
            tmp.write("\n".join(spec.patterns))
        finally:
            tmp.close()
        return Path(tmp.name), spec.source

    def _get_git_changed_files(self, source: Path, enabled: bool | None = None) -> dict | None:
        # Determine whether to use git-based incremental listing. Preference order:
        #  1) explicit flag from config (git_incremental)
        #  2) legacy env var FLOW_GIT_INCREMENTAL (temporary compat)
        if enabled is None:
            try:
                env_val = os.environ.get("FLOW_GIT_INCREMENTAL")
                if env_val is not None:
                    env_low = str(env_val).lower()
                    if env_low in {"1", "true", "yes"}:
                        try:
                            logger.info(
                                "Using legacy env FLOW_GIT_INCREMENTAL=1 (deprecated); prefer CodeTransferConfig.git_incremental=True"
                            )
                        except Exception:
                            pass
                        enabled = True
                    elif env_low in {"0", "false", "no"}:
                        enabled = False
            except Exception:
                enabled = None
        if not enabled:
            return None
        try:
            check = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=source,
                capture_output=True,
                text=True,
            )
            if check.returncode != 0 or check.stdout.strip().lower() != "true":
                return None

            def _run_git(args: list[str]) -> list[str]:
                res = subprocess.run(
                    ["git", "-c", "core.quotepath=false", *args],
                    cwd=source,
                    capture_output=True,
                    text=False,
                )
                if res.returncode != 0 or res.stdout is None:
                    return []
                data = res.stdout
                paths = [p.decode("utf-8", "surrogateescape") for p in data.split(b"\0") if p]
                return paths

            changed: set[str] = set()
            deleted: set[str] = set()
            for p in _run_git(["diff", "--name-only", "-z", "--diff-filter=ACMR"]):
                changed.add(p)
            for p in _run_git(["diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR"]):
                changed.add(p)
            for p in _run_git(["ls-files", "--others", "--exclude-standard", "-z"]):
                changed.add(p)
            for p in _run_git(["diff", "--name-only", "-z", "--diff-filter=D"]):
                deleted.add(p)
            for p in _run_git(["diff", "--cached", "--name-only", "-z", "--diff-filter=D"]):
                deleted.add(p)
            for p in _run_git(["ls-files", "--deleted", "-z"]):
                deleted.add(p)

            all_paths = list(changed | deleted)
            include_deletions = os.environ.get("FLOW_RSYNC_DELETE_MISSING_ARGS", "0").lower() in {
                "1",
                "true",
                "yes",
            }
            tmp = tempfile.NamedTemporaryFile(
                mode="wb", delete=False, prefix="flow-rsync-files-", suffix=".lst"
            )
            try:
                filtered = (
                    all_paths
                    if include_deletions
                    else [p for p in all_paths if (source / p).exists()]
                )
                for rel_path in filtered:
                    tmp.write(rel_path.encode("utf-8", "surrogateescape") + b"\0")
            finally:
                tmp.close()
            return {
                "list_path": Path(tmp.name),
                "count": len(filtered),
                "from0": True,
                "enable_delete_missing": include_deletions,
            }
        except Exception:
            return None

    def _build_rsync_command(
        self,
        source: Path,
        target: str,
        connection: SSHConnectionInfo,
        exclude_file: Path | None,
        *,
        files_from: Path | None = None,
        use_from0: bool = False,
    ) -> list[str]:
        ssh_cmd = (
            f"ssh -p {connection.port} "
            f"-i {connection.key_path} "
            f"-o StrictHostKeyChecking=no "
            f"-o UserKnownHostsFile=/dev/null "
            f"-o ConnectTimeout=10 "
            f"-o ServerAliveInterval=10 "
            f"-o ServerAliveCountMax=3"
        )
        cmd = [
            self.rsync_path,
            "-avz",
            "--update",
            "--progress",
            "--human-readable",
            "--stats",
            "--partial",
            "--partial-dir=.rsync-partial",
            "--timeout=30",
            "--contimeout=10",
            "-e",
            ssh_cmd,
        ]
        try:
            if os.environ.get("FLOW_RSYNC_DEBUG", "0").lower() in {"1", "true", "yes"}:
                cmd.insert(1, "-vv")
        except Exception:
            pass
        if exclude_file:
            cmd.extend(["--exclude-from", str(exclude_file)])
        if files_from:
            cmd.extend(["--files-from", str(files_from)])
            if use_from0:
                cmd.append("--from0")
            if os.environ.get("FLOW_RSYNC_DELETE_MISSING_ARGS", "0").lower() in {
                "1",
                "true",
                "yes",
            }:
                cmd.append("--delete-missing-args")
        cmd.append(f"{source}/")
        cmd.append(f"{connection.destination}:{target}/")
        return cmd

    def _execute_with_progress(
        self,
        cmd: list[str],
        progress_callback: Callable[[TransferProgress], None] | None,
        source_path: Path | None = None,
    ) -> dict:
        logger.debug(f"Executing rsync: {' '.join(cmd[:3])}...")
        bytes_transferred = 0
        files_transferred = 0
        current_file = None

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        tail_lines: deque[str] = deque(maxlen=200)
        for line in process.stdout:  # type: ignore
            line = line.strip()
            if not line:
                continue
            tail_lines.append(line)

            progress = self._parse_rsync_progress(line)
            if progress and progress_callback:
                if progress.current_file:
                    current_file = progress.current_file
                progress_callback(progress)

            if "Number of files transferred:" in line:
                m = re.search(r"(\d+)", line)
                if m:
                    files_transferred = int(m.group(1))
            elif "Total transferred file size:" in line:
                m = re.search(r"([\d,]+)", line)
                if m:
                    bytes_transferred = int(m.group(1).replace(",", ""))

        process.wait()
        if process.returncode != 0:
            tail = "\n".join(list(tail_lines)[-40:])
            msg = f"rsync failed with code {process.returncode}"
            if tail:
                msg += f"\n--- rsync output (tail) ---\n{tail}\n--- end ---"
            raise TransferError(msg)

        return {"bytes_transferred": bytes_transferred, "files_transferred": files_transferred}

    def _human_size_to_bytes(self, s: str) -> int:
        try:
            s = s.strip()
            # Remove commas
            s_clean = s.replace(",", "")
            # If ends with B/s or similar, strip the /s
            if s_clean.endswith("/s"):
                s_clean = s_clean[:-2]
            units = {
                "k": 1024,
                "kb": 1024,
                "m": 1024**2,
                "mb": 1024**2,
                "g": 1024**3,
                "gb": 1024**3,
                "t": 1024**4,
                "tb": 1024**4,
            }
            # Match number + optional unit
            import re as _re

            m = _re.match(r"^(?P<num>[0-9]+(?:\.[0-9]+)?)\s*(?P<unit>[kKmMgGtT]?[bB]?)?$", s_clean)
            if not m:
                # Try plain int
                return int(float(s_clean))
            num = float(m.group("num"))
            unit = (m.group("unit") or "").lower()
            if not unit or unit == "b":
                return int(num)
            factor = units.get(unit, 1)
            return int(num * factor)
        except Exception:
            return 0

    def _parse_rsync_progress(self, line: str) -> TransferProgress | None:
        """Parse a single line of rsync --progress output.

        Supports common rsync formats such as:
        - "path/to/file"
        - "  12,345  42%  1.23MB/s  0:00:10 (xfr#1, to-chk=3/10)"
        - "  1.2M 100%  34.5MB/s  0:00:00 (xfr#5, to-chk=0/10)" (human-readable sizes)

        Returns a TransferProgress instance when a filename or a progress line is detected;
        otherwise returns None.
        """
        try:
            # Ignore clearly non-progress, non-filename lines
            ignored_markers = (
                "sending incremental file list",
                "receiving incremental file list",
                "building file list",
                "delta-transmission disabled",
                "Number of files:",
                "Number of files transferred:",
                "Total bytes sent:",
                "Total bytes received:",
                "Total transferred file size:",
                "sent ",
                "total size is ",
            )
            for marker in ignored_markers:
                if marker in line:
                    return None

            # If line looks like a bare filename/path (no percent sign, no parens-only), treat as current file
            if "%" not in line and not line.startswith("(") and not line.endswith(")"):
                # Heuristic: filenames typically contain '/' or a dot and are not commands
                if "/" in line or "." in line or line:
                    return TransferProgress(
                        bytes_transferred=0,
                        total_bytes=None,
                        percentage=None,
                        speed=None,
                        eta=None,
                        current_file=line,
                    )

            # Try to parse a typical progress line containing percentage, speed, and ETA
            # Examples we aim to match (whitespace can vary):
            #   "  12,345  42%  1.23MB/s  0:00:10 (xfr#1, to-chk=3/10)"
            #   "  1.2M 100%  34.5MB/s  0:00:00"
            percent_match = re.search(r"(?P<percent>\d{1,3})%", line)
            speed_match = re.search(r"(?P<speed>[0-9]+\.?[0-9]*\s*(?:[kKMGT]?B/s))", line)
            eta_match = re.search(r"(?P<eta>\d+:\d+(?::\d+)?)", line)
            tochk_match = re.search(r"to-chk=(?P<remain>\d+)/(\s?)(?P<total>\d+)", line)

            # Extract leading transferred size if present
            bytes_match = re.match(r"^\s*(?P<size>[0-9][0-9,\.]*\s*(?:[kKMGT]?B)?)\s+", line)

            if percent_match or speed_match or eta_match or tochk_match or bytes_match:
                percent_val: float | None = None
                if percent_match:
                    try:
                        percent_val = float(percent_match.group("percent"))
                    except Exception:
                        percent_val = None
                elif tochk_match:
                    try:
                        remain = float(tochk_match.group("remain"))
                        total = float(tochk_match.group("total"))
                        if total > 0:
                            percent_val = max(0.0, min(100.0, (1.0 - (remain / total)) * 100.0))
                    except Exception:
                        percent_val = None

                speed_val = speed_match.group("speed") if speed_match else None
                eta_val = eta_match.group("eta") if eta_match else None
                bytes_val = 0
                if bytes_match:
                    try:
                        bytes_val = self._human_size_to_bytes(bytes_match.group("size"))
                    except Exception:
                        bytes_val = 0

                return TransferProgress(
                    bytes_transferred=bytes_val,
                    total_bytes=None,
                    percentage=percent_val,
                    speed=speed_val,
                    eta=eta_val,
                    current_file=None,
                )

            return None
        except Exception:
            # Be defensive: never let parsing errors break the transfer
            return None
