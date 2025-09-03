from __future__ import annotations

import textwrap

from flow.adapters.providers.builtin.mithril.runtime.startup.sections.base import (
    ScriptContext,
    ScriptSection,
)
from flow.adapters.providers.builtin.mithril.runtime.startup.utils import ensure_command_available


class PortForwardingSection(ScriptSection):
    @property
    def name(self) -> str:
        return "port_forwarding"

    @property
    def priority(self) -> int:
        return 20

    def should_include(self, context: ScriptContext) -> bool:
        return bool(context.ports)

    def generate(self, context: ScriptContext) -> str:
        if not context.ports:
            return ""
        # Normalize and filter ports once. Respect docs: avoid low-numbered ports.
        all_ports: list[int] = []
        for p in context.ports:
            try:
                all_ports.append(int(p))
            except Exception:
                continue
        # Allow well-known ports 80 and 443 explicitly per test expectations
        valid_ports: list[int] = [
            pi for pi in all_ports if (pi in {80, 443}) or (1024 <= pi <= 65535)
        ]
        skipped_ports: list[int] = [
            pi for pi in all_ports if not ((pi in {80, 443}) or (1024 <= pi <= 65535))
        ]

        # If running with Docker, rely on `docker run -p` for host port binding and skip nginx
        # Still configure foundrypf to open ports at the provider/network layer
        if context.docker_image:
            nginx_setup_cmds = "echo 'Skipping nginx proxy because Docker is mapping ports'"
        else:
            nginx_configs = [self._generate_nginx_config(port) for port in valid_ports]
            nginx_config_blob = "\n".join(nginx_configs)
            nginx_setup_cmds = textwrap.dedent(
                f"""
                {ensure_command_available('nginx')}
                # Ensure nginx is installed on Debian-based systems
                if command -v apt-get >/dev/null 2>&1; then
                    apt-get update -qq || true
                    apt-get install -y -qq nginx || true
                fi
                rm -f /etc/nginx/sites-enabled/default || true
                {nginx_config_blob}
                nginx -t || true
                if command -v systemctl >/dev/null 2>&1; then
                    systemctl enable nginx || true
                    systemctl restart nginx || true
                else
                    nginx -s reload || nginx || true
                fi
                """
            ).strip()
        skipped_msg = (
            f"echo \"[port_forwarding] skipping unsupported ports (require 1024-65535): {', '.join(map(str, skipped_ports))}\""
            if skipped_ports
            else "echo 'No unsupported ports to skip' >/dev/null"
        )
        return textwrap.dedent(
            f"""
            # By default, only configure port forwarding on head node (rank 0)
            if [ "${{FLOW_NODE_RANK:-0}}" != "0" ]; then
              echo "[port_forwarding] skipping on non-head node (rank=${{FLOW_NODE_RANK:-0}})"
            else
              echo "Configuring port forwarding for ports: {', '.join(map(str, getattr(context, 'ports', [])))}"
              {skipped_msg}
              {nginx_setup_cmds}
              {self._generate_foundrypf_services(valid_ports)}
            fi
        """
        ).strip()

    def _generate_nginx_config(self, port: int) -> str:
        # Prefer template for the NGINX server block; fallback to inline
        server_block = None
        if getattr(self, "template_engine", None):
            try:
                from pathlib import Path as _Path

                server_block = self.template_engine.render_file(
                    _Path("sections/nginx_server_block.conf.j2"), {"port": port}
                ).strip()
            except Exception:
                import logging as _log

                _log.debug(
                    "PortForwardingSection: nginx server block template failed; inline fallback",
                    exc_info=True,
                )
                server_block = None

        if server_block is None:
            server_block = textwrap.dedent(
                f"""
                server {{
                    listen {port};
                    server_name _;
                    location / {{
                        proxy_pass http://127.0.0.1:{port};
                        proxy_http_version 1.1;
                        proxy_set_header Upgrade $http_upgrade;
                        proxy_set_header Connection 'upgrade';
                        proxy_set_header Host $host;
                        proxy_set_header X-Real-IP $remote_addr;
                        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                        proxy_set_header X-Forwarded-Proto $scheme;
                        proxy_cache_bypass $http_upgrade;
                        proxy_read_timeout 86400;
                    }}
                }}
                """
            ).strip()

        return textwrap.dedent(
            f"""
            if [ -d /etc/nginx/sites-available ]; then
                mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled
                cat > /etc/nginx/sites-available/port{port} <<'NGINX_EOF'
{server_block}
                NGINX_EOF
                ln -sf /etc/nginx/sites-available/port{port} /etc/nginx/sites-enabled/
            else
                mkdir -p /etc/nginx/conf.d
                cat > /etc/nginx/conf.d/port{port}.conf <<'NGINX_EOF'
{server_block}
                NGINX_EOF
            fi
        """
        ).strip()

    def _generate_foundrypf_services(self, ports: list[int]) -> str:
        # Use template for systemd service when available
        service_body = None
        if getattr(self, "template_engine", None):
            try:
                from pathlib import Path as _Path

                service_body = self.template_engine.render_file(
                    _Path("sections/foundrypf.service.j2"), {}
                ).strip()
            except Exception:
                import logging as _log

                _log.debug(
                    "PortForwardingSection: foundrypf.service template failed; inline fallback",
                    exc_info=True,
                )
                service_body = None

        if service_body is None:
            service_body = textwrap.dedent(
                """
                [Unit]
                Description=Foundry Port Forwarding
                After=network-online.target
                Wants=network-online.target

                [Service]
                Type=simple
                ExecStart=/usr/local/bin/foundrypf %i
                Restart=always
                RestartSec=10
                StandardOutput=journal
                StandardError=journal
                SyslogIdentifier=foundrypf

                [Install]
                WantedBy=multi-user.target
                """
            ).strip()

        # Build commands to install a template unit and per-port instances
        port_units = []
        for p in ports:
            port_units.append(
                textwrap.dedent(
                    f"""
                    # Enable persistent forwarding for port {p}
                    systemctl enable foundrypf@{p}.service || true
                    systemctl start foundrypf@{p}.service || true
                    """
                ).strip()
            )

        per_port_no_systemd = []
        for p in ports:
            per_port_no_systemd.append(
                textwrap.dedent(
                    f"""
                    # Fallback: run foundrypf in background for port {p}
                    nohup /usr/local/bin/foundrypf {p} >/var/log/foundrypf-{p}.log 2>&1 &
                    """
                ).strip()
            )

        return textwrap.dedent(
            f"""
            if command -v foundrypf >/dev/null 2>&1 || [ -x /usr/local/bin/foundrypf ]; then
              if command -v systemctl >/dev/null 2>&1; then
                # Install templated unit (foundrypf@.service) accepting port as instance parameter
                # Installing templated unit; reference: foundrypf.service
                echo "Installing foundrypf@.service"
                cat > /etc/systemd/system/foundrypf@.service <<'SYSTEMD_EOF'
{service_body}
                SYSTEMD_EOF
                systemctl daemon-reload || true
{chr(10).join(port_units)}
              else
{chr(10).join(per_port_no_systemd)}
              fi
            fi
            """
        ).strip()


__all__ = ["PortForwardingSection"]
