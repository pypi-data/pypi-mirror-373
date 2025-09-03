from __future__ import annotations

import logging as _log
import textwrap

from flow.adapters.providers.builtin.mithril.runtime.startup.sections.base import (
    ScriptContext,
    ScriptSection,
)


class RuntimeMonitorSection(ScriptSection):
    @property
    def name(self) -> str:
        return "runtime_monitor"

    @property
    def priority(self) -> int:
        return 90

    def should_include(self, context: ScriptContext) -> bool:
        return bool(context.max_run_time_hours)

    def generate(self, context: ScriptContext) -> str:
        if not context.max_run_time_hours:
            return ""
        max_runtime_seconds = int(context.max_run_time_hours * 3600)
        api_key = context.environment.get("_FLOW_MITHRIL_API_KEY", "")
        api_url = context.environment.get("_FLOW_MITHRIL_API_URL", "https://api.mithril.ai")
        project = context.environment.get("_FLOW_MITHRIL_PROJECT", "")
        if not api_key or not project:
            return ""
        # Build smaller blocks via helpers for readability
        config_block = self._build_config_block(
            context, api_key, api_url, project, max_runtime_seconds
        )

        cancel_script_body = None
        timer_unit_body = None
        service_unit_body = None

        if getattr(self, "template_engine", None):
            try:
                from pathlib import Path as _Path

                cancel_script_body = self.template_engine.render_file(
                    _Path("sections/runtime_cancel.sh.j2"), {}
                ).strip()
                service_unit_body = self.template_engine.render_file(
                    _Path("sections/runtime_limit.service.j2"), {}
                ).strip()
            except Exception:
                _log.debug(
                    "RuntimeMonitorSection: template render failed; using inline units",
                    exc_info=True,
                )
                cancel_script_body = None
                service_unit_body = None

        if cancel_script_body is None:
            cancel_script_body = self._build_cancel_script_inline()

        # Always generate timer/service inline to use dynamic ${TIMER_SECONDS}
        timer_unit_body = self._build_timer_unit_inline()
        if service_unit_body is None:
            service_unit_body = self._build_service_unit_inline()

        return textwrap.dedent(
            f"""
			{config_block}
			cat > /usr/local/bin/flow-runtime-cancel.sh << 'CANCEL_EOF'
{cancel_script_body}
			CANCEL_EOF
			chmod +x /usr/local/bin/flow-runtime-cancel.sh
			cat > /etc/systemd/system/flow-runtime-limit.timer << TIMER_EOF
{timer_unit_body}
			TIMER_EOF
			cat > /etc/systemd/system/flow-runtime-limit.service << 'SERVICE_EOF'
{service_unit_body}
			SERVICE_EOF
			if command -v systemctl >/dev/null 2>&1; then
				systemctl daemon-reload
				systemctl enable flow-runtime-limit.timer
				systemctl restart flow-runtime-limit.timer || systemctl start flow-runtime-limit.timer
			else
				echo "[runtime_monitor] systemd not available; using background fallback" >&2
				nohup sh -c "sleep ${{TIMER_SECONDS}}; /usr/local/bin/flow-runtime-cancel.sh" >/var/log/flow/runtime-limit-oneshot.log 2>&1 &
			fi
			"""
        ).strip()

    def _build_config_block(
        self,
        context: ScriptContext,
        api_key: str,
        api_url: str,
        project: str,
        max_runtime_seconds: int,
    ) -> str:
        return textwrap.dedent(
            f"""
			mkdir -p /var/lib/flow /var/log/flow
			umask 077
			cat > /var/lib/flow/task-runtime.conf <<EOF
 TASK_NAME="{context.task_name or 'unknown'}"
 MAX_RUNTIME_HOURS="{context.max_run_time_hours}"
 MITHRIL_API_KEY="{api_key}"
 MITHRIL_API_URL="{api_url}"
 MITHRIL_PROJECT="{project}"
 EOF

			CONFIG_PATH="/var/lib/flow/task-runtime.conf"
			NOW=$(date +%s)
			if ! grep -q '^DEADLINE_EPOCH=' "$CONFIG_PATH" 2>/dev/null; then
			  echo "DEADLINE_EPOCH=$((NOW + {max_runtime_seconds}))" >> "$CONFIG_PATH"
			fi
			source "$CONFIG_PATH"
			NOW=$(date +%s)
			REMAINING=$((DEADLINE_EPOCH - NOW))
			if [ "$REMAINING" -le 0 ]; then REMAINING=60; fi
			TIMER_SECONDS=$((REMAINING - 120))
			if [ "$TIMER_SECONDS" -lt 60 ]; then TIMER_SECONDS=60; fi
			"""
        ).strip()

    def _build_cancel_script_inline(self) -> str:
        return textwrap.dedent(
            """
			#!/bin/bash
			set -euo pipefail
			CONFIG="/var/lib/flow/task-runtime.conf"
			[ -f "$CONFIG" ] && source "$CONFIG" || true
			log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [runtime_limit] $*"; }

			log "Max runtime reached; initiating graceful shutdown"
			docker stop -t 30 main 2>/dev/null || true
			sleep 10

			INSTANCE_ID=$(curl -s --max-time 5 http://169.254.169.254/latest/meta-data/instance-id || hostname)
			JSON=$(curl -sS --max-time 20 -H "Authorization: Bearer $MITHRIL_API_KEY" "$MITHRIL_API_URL/v2/spot/bids?project=$MITHRIL_PROJECT" || true)

			TASK_ID="unknown"
			if command -v jq >/dev/null 2>&1; then
			  TASK_ID=$(echo "$JSON" | jq -r --arg IID "$INSTANCE_ID" --arg NAME "${TASK_NAME:-}" '
				(.. | objects | select(has("instances")))? as $x |
				($x.instances[]? | select(.instance_id == $IID) | $x.fid) //
				((.data // .)[]? | select(.name == $NAME and .fid != null) | .fid) //
				"unknown"
			  ')
			else
			  TASK_ID=$( INSTANCE_ID="$INSTANCE_ID" TASK_NAME="${TASK_NAME:-}" python3 - <<'PY' 2>/dev/null || echo unknown
import os,sys,json
try:
  data=json.load(sys.stdin)
except Exception:
  print("unknown"); sys.exit(0)
items=data if isinstance(data,list) else data.get("data",[])
iid=os.environ.get("INSTANCE_ID","")
name=os.environ.get("TASK_NAME","")
fid="unknown"
for x in items:
  for inst in (x.get("instances") or []):
    if inst.get("instance_id")==iid:
      fid = x.get("fid") or "unknown"
      break
  if fid!="unknown":
    break
if fid=="unknown" and name:
  for x in items:
    if x.get("name")==name:
      fid = x.get("fid") or "unknown"
      break
print(fid)
PY
			  )
			fi

			if [ "$TASK_ID" != "unknown" ]; then
			  log "Cancelling task $TASK_ID"
			  for attempt in 1 2 3 4 5; do
				CODE=$(curl -sS -o /dev/null -w "%{http_code}" -X DELETE \
				  -H "Authorization: Bearer $MITHRIL_API_KEY" \
				  -H "Content-Type: application/json" \
				  "$MITHRIL_API_URL/v2/spot/bids/$TASK_ID" --max-time 30 || true)
				if [ "$CODE" = "200" ] || [ "$CODE" = "204" ] || [ "$CODE" = "202" ]; then
				  log "Cancelled task $TASK_ID successfully"
				  break
				fi
				sleep $((attempt * attempt))
			  done
			else
			  log "Could not resolve TASK_ID from provider API; skipping remote cancel"
			fi
			"""
        ).strip()

    def _build_timer_unit_inline(self) -> str:
        return textwrap.dedent(
            """
			[Unit]
			Description=Flow Runtime Limit Timer
			[Timer]
			OnBootSec=${TIMER_SECONDS}s
			AccuracySec=1min
			Persistent=true
			[Install]
			WantedBy=timers.target
			"""
        ).strip()

    def _build_service_unit_inline(self) -> str:
        return textwrap.dedent(
            """
			[Unit]
			Description=Flow Runtime Limit Enforcement
			[Service]
			Type=oneshot
			ExecStart=/usr/local/bin/flow-runtime-cancel.sh
			Restart=no
			"""
        ).strip()


__all__ = ["RuntimeMonitorSection"]
