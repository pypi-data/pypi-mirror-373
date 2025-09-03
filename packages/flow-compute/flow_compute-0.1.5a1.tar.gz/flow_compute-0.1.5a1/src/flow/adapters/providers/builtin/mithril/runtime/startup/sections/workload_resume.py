from __future__ import annotations

import logging as _log
import textwrap

from flow.adapters.providers.builtin.mithril.runtime.startup.sections.base import (
    ScriptContext,
    ScriptSection,
)
from flow.utils.paths import WORKSPACE_DIR


class WorkloadResumeSection(ScriptSection):
    """Create systemd service for automatic workload resumption after preemption.

    This section creates a systemd service that runs on every boot to detect
    if this is a fresh start or a resume after preemption/relocation. It handles
    both Docker and non-Docker workloads, automatically resuming work from the
    last known state.
    """

    @property
    def name(self) -> str:
        return "workload_resume"

    @property
    def priority(self) -> int:
        return 85

    def should_include(self, context: ScriptContext) -> bool:
        return context.enable_workload_resume and bool(
            context.docker_image or (context.user_script and context.user_script.strip())
        )

    def generate(self, context: ScriptContext) -> str:
        resume_script = self._generate_resume_script(context)
        systemd_service = self._generate_systemd_service()
        return textwrap.dedent(
            f"""
            echo "Setting up automatic workload resumption service"
            mkdir -p /var/lib/flow
            cat > /usr/local/sbin/flow-workload-resume.sh <<'RESUME_SCRIPT_EOF'
{resume_script}
RESUME_SCRIPT_EOF
            chmod +x /usr/local/sbin/flow-workload-resume.sh
            cat > /etc/systemd/system/flow-workload-resume.service <<'SYSTEMD_SERVICE_EOF'
{systemd_service}
SYSTEMD_SERVICE_EOF
            if command -v systemctl >/dev/null 2>&1; then
                systemctl daemon-reload
                systemctl enable flow-workload-resume.service
                systemctl start flow-workload-resume.service || true
            else
                echo "[workload_resume] systemd not available; running resume script once in background" >&2
                nohup /usr/local/sbin/flow-workload-resume.sh >/var/log/flow/workload-resume-oneshot.log 2>&1 &
            fi
        """
        ).strip()

    def validate(self, context: ScriptContext) -> list[str]:
        return []

    def _generate_resume_script(self, context: ScriptContext) -> str:
        if context.docker_image:
            workload_check = self._generate_docker_resume_logic(context)
        else:
            workload_check = self._generate_script_resume_logic(context)

        if getattr(self, "template_engine", None):
            try:
                from pathlib import Path as _Path

                return self.template_engine.render_file(
                    _Path("sections/workload_resume.sh.j2"),
                    {"workload_check": workload_check},
                ).strip()
            except Exception:
                _log.debug(
                    "WorkloadResumeSection: template render failed; using inline", exc_info=True
                )

        return textwrap.dedent(
            f"""#!/bin/bash
            set -euo pipefail
            LOG_FILE="/var/log/flow/workload-resume.log"
            STATE_FILE="/var/lib/flow/task-state"
            BOOT_MARKER="/var/lib/flow/first-boot-completed"
            mkdir -p /var/log/flow
            log() {{ echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"; }}
            log "Starting workload resume check"
            if [ ! -f "$BOOT_MARKER" ]; then
                log "First boot detected, marking as completed"
                touch "$BOOT_MARKER"; exit 0; fi
            if [ ! -f "$STATE_FILE" ]; then
                log "No previous task state found, this appears to be a fresh instance"; exit 0; fi
            log "Previous task state detected, checking workload status"
            source "$STATE_FILE"
            GPU_INSTANCE=""
            if command -v nvidia-smi >/dev/null 2>&1; then GPU_INSTANCE="yes"; log "GPU instance detected"; fi
            VOLUME_MOUNTS=""
            # Collect mount points of block devices to pass through to the container
            for mount in $(mount | grep -E "^/dev/(vd|xvd|nvme)" | awk '{{print $3}}'); do
              case "$mount" in
                /var/lib/docker|/var/run/docker.sock|/etc/docker)
                  continue ;;
              esac
              if [ -d "$mount" ]; then VOLUME_MOUNTS="$VOLUME_MOUNTS -v \"$mount\":\"$mount\""; fi
            done
            log "Volume mounts: $VOLUME_MOUNTS"
            {workload_check}
            log "Workload resume check completed"
            """
        ).strip()

    def _generate_docker_resume_logic(self, context: ScriptContext) -> str:
        docker_cmd = self._build_docker_run_command_for_resume(context)
        return textwrap.dedent(
            f"""
            if command -v docker >/dev/null 2>&1; then
              # Build env-file from state for safe propagation
              ENV_FILE=/var/lib/flow/env.list
              mkdir -p /var/lib/flow
              rm -f "$ENV_FILE" || true
              if [ -f "$STATE_FILE" ]; then
                grep '^ENV_' "$STATE_FILE" | sed 's/^ENV_//' > "$ENV_FILE" || true
              fi
              if docker ps -a --format '{{{{.Names}}}}' | grep -q '^main$'; then
                CONTAINER_STATUS=$(docker inspect -f '{{{{.State.Status}}}}' main 2>/dev/null || echo "unknown")
                log "Container 'main' status: $CONTAINER_STATUS"
                case "$CONTAINER_STATUS" in
                  "running") log "Container is already running" ;;
                  "exited"|"stopped") log "Restarting stopped container"; docker start main; sleep 5; docker logs main --tail 50 ;;
                  *) log "Container in unexpected state: $CONTAINER_STATUS"; log "Removing and recreating container"; docker rm -f main 2>/dev/null || true; {docker_cmd} ;;
                esac
              else
                log "Container 'main' not found, creating new container"; {docker_cmd}
              fi
              sleep 5
              if docker ps --format '{{{{.Names}}}}' | grep -q '^main$'; then log "Container 'main' is running successfully"; else log "ERROR: Failed to start container 'main'"; exit 1; fi
            else
              log "Docker not found, cannot resume Docker workload"; exit 1
            fi
            """
        ).strip()

    def _generate_script_resume_logic(self, context: ScriptContext) -> str:
        if not context.user_script or not context.user_script.strip():
            return 'log "No user script to resume"'
        script_content = context.user_script.strip()
        if not script_content.startswith("#!"):
            script_content = "#!/bin/bash\n" + script_content
        return textwrap.dedent(
            f"""
            if [ -f /tmp/user_startup.sh ]; then
              log "Found user script, checking if it should be re-run"
              if grep -q "FLOW_RESUME_SAFE" /tmp/user_startup.sh; then
                log "User script marked as resume-safe, re-running"; /tmp/user_startup.sh
              else
                log "User script not marked as resume-safe, skipping re-run"; log "To make your script resume-safe, add '# FLOW_RESUME_SAFE' comment"
              fi
            else
              log "Creating and running user script"
              cat > /tmp/user_startup.sh <<'USER_SCRIPT_EOF'
{script_content}
USER_SCRIPT_EOF
              chmod +x /tmp/user_startup.sh; /tmp/user_startup.sh
            fi
            """
        ).strip()

    def _build_docker_run_command_for_resume(self, context: ScriptContext) -> str:
        gpus_flag = "--gpus all" if context.has_gpu else ""
        parts: list[str] = [
            "docker run",
            "-d",
            "--restart=unless-stopped",
            "--name=main",
        ]
        if gpus_flag:
            parts.append(gpus_flag)
        parts.append('$([ -f /var/lib/flow/env.list ] && echo "--env-file /var/lib/flow/env.list")')
        parts.append("$VOLUME_MOUNTS")
        parts.append(
            f'$([ -d {WORKSPACE_DIR} ] && echo "-v {WORKSPACE_DIR}:{WORKSPACE_DIR} -w {WORKSPACE_DIR}")'
        )
        parts.append('"$DOCKER_IMAGE"')
        parts.append("$DOCKER_COMMAND")
        return " \\\n                    ".join(parts)

    def _generate_systemd_service(self) -> str:
        if getattr(self, "template_engine", None):
            try:
                from pathlib import Path as _Path

                return self.template_engine.render_file(
                    _Path("sections/workload_resume_service.service.j2"), {}
                ).strip()
            except Exception:
                pass
        return textwrap.dedent(
            """[Unit]
            Description=Flow Workload Resume Service
            After=network-online.target docker.service
            Wants=network-online.target
            ConditionPathExists=/var/lib/flow/task-state

            [Service]
            Type=oneshot
            ExecStart=/usr/local/sbin/flow-workload-resume.sh
            RemainAfterExit=yes
            StandardOutput=journal
            StandardError=journal
            SyslogIdentifier=flow-workload-resume

            [Install]
            WantedBy=multi-user.target"""
        ).strip()


__all__ = ["WorkloadResumeSection"]
