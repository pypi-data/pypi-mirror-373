from __future__ import annotations

import shlex


def build_recording_command(command: str | None) -> tuple[str, bool]:
    """Build the remote command for session or command recording.

    Returns a tuple of (remote_command, requires_tty).
    """
    if command:
        escaped_cmd = command.replace("'", "'\"'\"'")
        script = (
            # Always record under $HOME to avoid sudo/TTY fragility; mirror to /var/log when possible
            'LOG_DIR="$HOME/.flow"; mkdir -p "$LOG_DIR" 2>/dev/null; '
            'LOG_FILE="$LOG_DIR/flow_ssh.log"; '
            "TS=$(date +%Y-%m-%d' '%H:%M:%S); "
            f"CMD='{escaped_cmd}'; "
            # Emit a start marker to both logs (best effort) so host follow lights up immediately
            'echo "[$TS] Command: $CMD" | tee -a "$LOG_FILE" >/dev/null; '
            '( echo "[flow-ssh] command start $(date -Is)" >> "$LOG_FILE" 2>/dev/null || true ); '
            # Best-effort mirroring to /var/log for admins
            "if sudo -n true 2>/dev/null; then sudo -n mkdir -p /var/log/foundry 2>/dev/null; sudo -n touch /var/log/foundry/flow_ssh.log 2>/dev/null; sudo -n chown $(id -un):$(id -gn) /var/log/foundry/flow_ssh.log 2>/dev/null; fi; "
            '( echo "[flow-ssh] command start $(date -Is)" | sudo -n tee -a /var/log/foundry/flow_ssh.log >/dev/null 2>&1 || true ); '
            'eval "$CMD" 2>&1 | tee -a "$LOG_FILE" | (sudo -n tee -a /var/log/foundry/flow_ssh.log >/dev/null 2>&1 || true)'
        )
        return f"bash -lc {shlex.quote(script)}", False

    # Interactive session recording
    script = (
        # Always record to $HOME; also create a mirror file under /var/log when sudo is available
        'LOG_DIR="$HOME/.flow"; mkdir -p "$LOG_DIR" 2>/dev/null; '
        'LOG_FILE="$LOG_DIR/flow_ssh.log"; '
        "TS=$(date +%Y-%m-%d' '%H:%M:%S); "
        # Emit start markers to both user and system logs (best effort)
        'echo "[$TS] Interactive session started" | tee -a "$LOG_FILE" >/dev/null; '
        '( echo "[flow-ssh] session start $(date -Is)" >> "$LOG_FILE" 2>/dev/null || true ); '
        "if sudo -n true 2>/dev/null; then sudo -n mkdir -p /var/log/foundry 2>/dev/null; sudo -n touch /var/log/foundry/flow_ssh.log 2>/dev/null; sudo -n chown $(id -un):$(id -gn) /var/log/foundry/flow_ssh.log 2>/dev/null; fi; "
        '( echo "[flow-ssh] session start $(date -Is)" | sudo -n tee -a /var/log/foundry/flow_ssh.log >/dev/null 2>&1 || true ); '
        # Use script to capture full interactive session; ensure append and flush
        "( command -v script >/dev/null 2>&1 && script -q -a -f \"$LOG_FILE\" -c 'bash -l' 2>/dev/null ) || "
        # Fallback: tee interactive bash output to log (less exact but ensures visibility)
        "( bash -lc 'bash -i' 2>&1 | tee -a \"$LOG_FILE\" | (sudo -n tee -a /var/log/foundry/flow_ssh.log >/dev/null 2>&1 || true) )"
    )
    return f"bash -lc {shlex.quote(script)}", True
