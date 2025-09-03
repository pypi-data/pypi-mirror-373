"""Log retrieval and streaming via provider remote operations.

Encapsulates the SSH-based log commands and adds a small TTL cache for the
`get_task_logs` fast-path.
"""

from __future__ import annotations

from datetime import datetime, timezone

from flow.protocols.remote_operations import RemoteOperationsProtocol as IRemoteOperations
from flow.utils.ttl_cache import TTLCache


class LogService:
    """Cache-aware log retrieval and streaming for tasks."""

    def __init__(
        self, remote_ops: IRemoteOperations, *, cache_ttl: float = 5.0, max_entries: int = 100
    ):
        self._remote = remote_ops
        self._cache = TTLCache[tuple[str, int, str], str](
            ttl_seconds=cache_ttl, max_entries=max_entries
        )

    def get_cached(self, task_id: str, tail: int, log_type: str) -> str | None:
        return self._cache.get((task_id, tail, log_type))

    def set_cache(self, task_id: str, tail: int, log_type: str, content: str) -> None:
        self._cache.set((task_id, tail, log_type), content)

    def build_command(self, task_id: str, tail: int, log_type: str, follow: bool = False) -> str:
        log_type = (log_type or "stdout").lower()
        # Provide a 'd' helper that falls back to sudo when docker socket is restricted
        sudo_helper = 'd() { docker "$@" 2>/dev/null || sudo -n docker "$@" 2>/dev/null; }; '

        # Determine options for tail/docker logs depending on streaming mode
        if follow:
            tail_opt = f"-F -n {tail}"
            docker_logs_opt = f"-f --tail {tail}"
        else:
            tail_opt = f"-n {tail}"
            docker_logs_opt = f"--tail {tail}"

        if log_type in {"startup", "host"}:
            # For host source, show startup + SSH logs
            if log_type == "host":
                if follow:
                    # Follow startup + system SSH + user SSH concurrently with per-stream FIFOs
                    return (
                        "umask 077; "
                        "START=/var/log/foundry/startup_script.log; "
                        "SSH_SYS=/var/log/foundry/flow_ssh.log; "
                        "SSH_USER=$HOME/.flow/flow_ssh.log; "
                        f"N={tail}; "
                        "if command -v stdbuf >/dev/null 2>&1; then S='stdbuf -oL -eL '; else S=''; fi; "
                        'TMPDIR=${TMPDIR:-/tmp}; DIR=$(mktemp -d -p "$TMPDIR" flow-logs-XXXXXX 2>/dev/null || echo "$TMPDIR/flow-logs-$$"); '
                        'P1="$DIR/startup.fifo"; P2="$DIR/ssh_sys.fifo"; P3="$DIR/ssh_user.fifo"; '
                        'mkfifo "$P1" "$P2" "$P3" 2>/dev/null || true; '
                        'cleanup(){ set +u; kill ${TAIL1-} ${TAIL2-} ${TAIL3-} ${CAT1-} ${CAT2-} ${CAT3-} 2>/dev/null || true; rm -rf "$DIR" 2>/dev/null || true; }; '
                        "trap cleanup EXIT INT TERM; "
                        # Optional snapshot
                        'if [ "$N" -gt 0 ]; then '
                        '  (sudo -n tail -n "$N" "$START" 2>/dev/null || tail -n "$N" "$START" 2>/dev/null) | sed \'s/^/[Startup] /\'; '
                        '  if sudo -n test -r "$SSH_SYS" 2>/dev/null; then sudo -n tail -n "$N" "$SSH_SYS" 2>/dev/null | sed \'s/^/[SSH-system] /\'; '
                        '  elif [ -f "$SSH_USER" ]; then tail -n "$N" "$SSH_USER" 2>/dev/null | sed \'s/^/[SSH-user] /\'; fi; '
                        "fi; "
                        "echo '--- Following new activity (Ctrl+C to stop) ---'; "
                        # Start readers first
                        '$S cat "$P1" & CAT1=$!; $S cat "$P2" & CAT2=$!; $S cat "$P3" & CAT3=$!; '
                        # Startup writer (sudo preferred, fallback to user)
                        '(sudo -n $S tail -F -n 0 "$START" 2>/dev/null || $S tail -F -n 0 "$START" 2>/dev/null) | $S sed \'s/^/[Startup] /\' > "$P1" & TAIL1=$!; '
                        # System SSH writer: retry until sudo -n tail attaches
                        '( while :; do sudo -n $S tail -F -n 0 "$SSH_SYS" 2>/dev/null && break; sleep 2; done ) | $S sed \'s/^/[SSH-system] /\' > "$P2" & TAIL2=$!; '
                        # User SSH writer (always readable)
                        '($S tail -F -n 0 "$SSH_USER" 2>/dev/null) | $S sed \'s/^/[SSH-user] /\' > "$P3" & TAIL3=$!; '
                        # Keep foreground attached
                        "wait"
                    )

                # Snapshot host logs: system SSH, then user SSH, then startup (each prefixed)
                return (
                    "START=/var/log/foundry/startup_script.log; "
                    "SSH_SYS=/var/log/foundry/flow_ssh.log; "
                    "SSH_USER=$HOME/.flow/flow_ssh.log; "
                    f"N={tail}; "
                    '( sudo -n tail -n "$N" "$SSH_SYS" 2>/dev/null | sed \'s/^/[SSH-system] /\' || true ); '
                    '( tail -n "$N" "$SSH_USER" 2>/dev/null | sed \'s/^/[SSH-user] /\' || true ); '
                    '( sudo -n tail -n "$N" "$START" 2>/dev/null | sed \'s/^/[Startup] /\' || true )'
                )

            # Only startup logs
            if follow:
                return (
                    "LOG=/var/log/foundry/startup_script.log; "
                    f'sudo -n tail {tail_opt} "$LOG" 2>/dev/null || tail {tail_opt} "$LOG" 2>/dev/null || '
                    "echo 'Waiting for startup logs...'"
                )

            return (
                "LOG=/var/log/foundry/startup_script.log; "
                f'( sudo -n tail -n {tail} "$LOG" 2>/dev/null || tail -n {tail} "$LOG" 2>/dev/null ) || '
                "echo 'Startup logs are empty (instance may still be starting).'"
            )

        # Helper scripts for container selection and waiting when streaming
        wait_for_container_script = (
            "  echo 'Waiting for container...'; "
            "  while [ -z \"$(d ps -a --format '{{.Names}}' | head -n1)\" ]; do sleep 1; done; "
            "  if d ps -a --format '{{.Names}}' | grep -q '^main$'; then CN='main'; else CN=$(d ps -a --format '{{.Names}}' | head -n1); fi; "
        )

        determine_cn_script = "if d ps -a --format '{{.Names}}' | grep -q '^main$'; then CN='main'; else CN=$(d ps -a --format '{{.Names}}' | head -n1); fi; "

        # Auto source: show startup until container exists, then container logs
        if log_type == "auto":
            if follow:
                # Show a small startup snapshot first, then follow startup until the
                # container appears, then switch to container logs with an initial tail.
                return sudo_helper + (
                    "LOG=/var/log/foundry/startup_script.log; "
                    "if command -v stdbuf >/dev/null 2>&1; then S='stdbuf -oL -eL '; else S=''; fi; "
                    # Initial snapshot of startup logs for immediate context
                    f'(sudo -n tail -n {tail} "$LOG" 2>/dev/null || tail -n {tail} "$LOG" 2>/dev/null) | sed \'s/^/[Startup] /\'; '
                    "echo '--- Following startup (waiting for container) ---'; "
                    '(sudo -n $S tail -F -n 0 "$LOG" 2>/dev/null || $S tail -F -n 0 "$LOG" 2>/dev/null) | $S sed \'s/^/[Startup] /\' & TPID=$!; '
                    "while :; do CN=$(d ps -a --format '{{.Names}}' | head -n1); if [ -n \"$CN\" ]; then break; fi; sleep 1; done; "
                    "echo '--- Container is up. Switching to container logs ---'; "
                    "kill $TPID 2>/dev/null || true; wait $TPID 2>/dev/null || true; "
                    "if d ps -a --format '{{.Names}}' | grep -q '^main$'; then CN='main'; else CN=$(d ps -a --format '{{.Names}}' | head -n1); fi; "
                    f'd logs "$CN" {docker_logs_opt} 2>&1; '
                )
            # Snapshot: prefer container if present else show startup snip with hint
            return (
                sudo_helper
                + "CN=$(d ps -a --format '{{.Names}}' | head -n1); "
                + 'if [ -n "$CN" ]; then '
                + '  d logs "$CN" --tail '
                + str(tail)
                + " 2>&1; "
                + "else "
                + "  echo 'Container not started. Showing startup logs snapshot...'; "
                + "  LOG=/var/log/foundry/startup_script.log; "
                + '  ( sudo -n tail -n "'
                + str(tail)
                + '" "$LOG" 2>/dev/null || tail -n "'
                + str(tail)
                + '" "$LOG" 2>/dev/null ); '
                + "  echo '--- End of startup snapshot. Use -f to follow until container starts.'; "
                + "fi"
            )

        if log_type in {"both", "combined", "all"}:
            # Combined stdout+stderr from container
            if follow:
                return (
                    sudo_helper
                    + determine_cn_script
                    + 'if [ -z "$CN" ]; then '
                    + wait_for_container_script
                    + "fi; "
                    + f'd logs "$CN" {docker_logs_opt} 2>&1; '
                )

            # Snapshot combined (no implicit fallback to startup here)
            return (
                sudo_helper
                + "CN=$(d ps -a --format '{{.Names}}' | head -n1); "
                + 'if [ -n "$CN" ]; then '
                + "  echo '=== Docker container logs ===' && d logs \"$CN\" --tail "
                + str(tail)
                + ' 2>&1 | awk \'BEGIN{p="";c=0}{if($0==p){c++;next} if(c>0){print "[... repeated " c " times]"; c=0} print; p=$0} END{if(c>0) print "[... repeated " c " times]"}\'; '
                + "else "
                + "  echo 'Task logs are not available yet (container not started).'; "
                + "  echo '  • Follow and wait: flow logs "
                + str(task_id)
                + " -f'; "
                + "  echo '  • View instance startup: flow logs "
                + str(task_id)
                + " --source startup'; "
                + "fi"
            )
        elif log_type == "stderr":
            # Docker does not split stdout/stderr in logs; stream combined for consistency
            if follow:
                return (
                    sudo_helper
                    + determine_cn_script
                    + 'if [ -z "$CN" ]; then '
                    + wait_for_container_script
                    + "fi; "
                    + f'd logs "$CN" {docker_logs_opt} 2>&1; '
                )

            return (
                sudo_helper
                + "CN=$(d ps -a --format '{{.Names}}' | head -n1); "
                + 'if [ -n "$CN" ]; then '
                + '  d logs "$CN" --tail '
                + str(tail)
                + ' 2>&1 | awk \'BEGIN{p="";c=0}{if($0==p){c++;next} if(c>0){print "[... repeated " c " times]"; c=0} print; p=$0} END{if(c>0) print "[... repeated " c " times]"}\'; '
                + "else echo 'No container logs available.'; fi"
            )
        else:
            # stdout
            if follow:
                return (
                    sudo_helper
                    + determine_cn_script
                    + 'if [ -z "$CN" ]; then '
                    + wait_for_container_script
                    + "fi; "
                    + f'd logs "$CN" {docker_logs_opt} 2>&1; '
                )

            # Snapshot stdout
            return self._build_snapshot_stdout_command(task_id, tail, sudo_helper)

        # unreachable
        raise AssertionError("unreachable")

    def _build_snapshot_stdout_command(self, task_id: str, tail: int, sudo_helper: str) -> str:
        return (
            sudo_helper
            + "if d ps --format '{{.Names}}' | grep -q '^main$'; then d logs main --tail "
            + str(tail)
            + ' 2>&1 | awk \'BEGIN{p="";c=0}{if($0==p){c++;next} if(c>0){print "[... repeated " c " times]"; c=0} print; p=$0} END{if(c>0) print "[... repeated " c " times]"}\'; '
            + "else CN=$(d ps -a --format '{{.Names}}' | head -n1); "
            + 'if [ -n "$CN" ]; then '
            + '  d logs "$CN" --tail '
            + str(tail)
            + ' 2>&1 | awk \'BEGIN{p="";c=0}{if($0==p){c++;next} if(c>0){print "[... repeated " c " times]"; c=0} print; p=$0} END{if(c>0) print "[... repeated " c " times]"}\'; '
            + "else "
            + "  echo 'Task logs are not available yet (container not started).'; "
            + "  echo '  • Follow and wait: flow logs "
            + str(task_id)
            + " -f'; "
            + "  echo '  • View instance startup: flow logs "
            + str(task_id)
            + " --source startup'; "
            + "fi; fi"
        )

    # Public helper to execute a log command via the remote interface without exposing internals
    def execute_via_remote(self, task_id: str, command: str) -> str:
        return self._remote.execute_command(task_id, command)

    # Centralized gating and retrieval for recent logs
    def get_recent(
        self,
        *,
        task_id: str,
        bid: dict | None,
        tail: int = 100,
        log_type: str = "stdout",
        execute: bool = True,
    ) -> str:
        """Return recent logs with pending/cancelled gating and helpful messages.

        If execute=False, returns the built command string instead of running it.
        """
        if not isinstance(bid, dict):
            return "Task not found"

        status = str(bid.get("status", "")).lower()
        if status == "cancelled":
            return (
                f"Task {task_id} was cancelled. Logs are not available because "
                "instances are terminated upon cancellation. Consider using "
                "'flow status' to check task outcomes."
            )

        instances = bid.get("instances", [])
        # Only gate when clearly pending/open; allow running tasks to proceed even if
        # instances array is missing or empty in the API response.
        if status in ["pending", "open", "queued", "accepted"]:
            created_at_str = bid.get("created_at")
            if created_at_str:
                try:
                    created_at = datetime.fromisoformat(str(created_at_str).replace("Z", "+00:00"))
                    _ = (datetime.now(timezone.utc) - created_at).total_seconds()
                except Exception:
                    pass
            # Generic pending message
            return (
                f"Task {task_id if not str(task_id).startswith('bid_') else 'the task'} "
                "is still starting; logs will appear once the instance is up."
            )

        command = self.build_command(task_id, tail, log_type)
        if not execute:
            return command
        try:
            content = self._remote.execute_command(task_id, command)
            if content:
                self.set_cache(task_id, tail, log_type, content.strip())
            return content.strip() if content else "No logs available"
        except Exception as e:
            return f"Failed to retrieve logs: {e}"
