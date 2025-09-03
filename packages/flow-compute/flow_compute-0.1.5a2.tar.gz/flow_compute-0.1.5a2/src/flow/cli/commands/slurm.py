from __future__ import annotations

import json
from typing import Any

import click

from flow.cli.commands.base import BaseCommand, console
from flow.cli.commands.input_types import EnvItem
from flow.cli.commands.utils import env_items_to_dict
from flow.cli.utils.error_handling import cli_error_guard
from flow.sdk.factory import create_client


class SlurmCommand(BaseCommand):
    @property
    def name(self) -> str:
        return "slurm"

    @property
    def help(self) -> str:
        return "Interact with Slurm on reservations (submit/status/cancel/ssh)"

    def get_command(self) -> click.Command:
        @click.group(name=self.name, help=self.help)
        @cli_error_guard(self)
        def grp() -> None:
            pass

        def _get_slurm_meta(reservation_id: str) -> dict[str, Any]:
            flow = create_client(auto_init=True)
            res = flow.get_reservation(reservation_id)
            meta = getattr(res, "provider_metadata", {}) or {}
            slurm = meta.get("slurm") or {}
            if not slurm:
                self.handle_error(
                    "Reservation is not Slurm-enabled. Recreate with --with-slurm or contact support."
                )
                raise click.Abort()
            return slurm

        @grp.command(name="submit", help="Submit a SLURM script to a reservation's Slurm cluster")
        @click.argument("reservation_id")
        @click.argument("script_path")
        @click.option(
            "--env",
            "env_items",
            type=EnvItem(),
            multiple=True,
            help="Env variables KEY=VALUE (repeatable)",
        )
        @click.option("--account", default=None)
        @click.option("--partition", default=None)
        @click.option("--array", default=None)
        @click.option("--name", default=None)
        @click.option(
            "--insecure",
            is_flag=True,
            default=False,
            help="Do not verify TLS certificate for slurmrestd (or set FLOW_SLURM_INSECURE=1)",
        )
        @click.option(
            "--ca-cert",
            type=click.Path(exists=True, dir_okay=False, readable=True, path_type=str),
            default=None,
            help="Path to CA certificate PEM for slurmrestd (or set FLOW_SLURM_CA_CERT)",
        )
        @click.option(
            "--api-version",
            type=str,
            default=None,
            help="slurmrestd API version (e.g., v0.0.40); overrides FLOW_SLURM_API_VERSION",
        )
        def submit_cmd(
            reservation_id: str,
            script_path: str,
            env_items: tuple[tuple[str, str], ...],
            account: str | None,
            partition: str | None,
            array: str | None,
            name: str | None,
            insecure: bool,
            ca_cert: str | None,
            api_version: str | None,
        ) -> None:
            try:
                slurm = _get_slurm_meta(reservation_id)
            except click.Abort:
                return

            try:
                content = open(script_path, encoding="utf-8").read()
            except Exception as e:
                self.handle_error(e)
                return

            # Minimal slurmrestd payload with validated env
            env_dict: dict[str, Any] = env_items_to_dict(env_items)
            payload: dict[str, Any] = {
                "script": content,
                "environment": env_dict,
            }
            if account:
                payload["account"] = account
            if partition:
                payload["partition"] = partition
            if array:
                payload["array"] = array
            if name:
                payload["name"] = name

            restd_url = slurm.get("restd_url")
            ca_pem = slurm.get("ca_pem")
            if not restd_url:
                self.handle_error("Slurm REST endpoint is not available for this reservation")
                return

            import os
            import tempfile

            from flow.sdk.http import HttpClient as _Http

            # TLS verification handling
            # Priority: --insecure → --ca-cert → slurm.ca_pem → True
            verify_param: object = True
            caf = None
            caf_path: str | None = None
            try:
                # CLI-specified CA cert path overrides metadata
                ca_cert = ca_cert or os.getenv("FLOW_SLURM_CA_CERT")
                insecure = insecure or (
                    os.getenv("FLOW_SLURM_INSECURE", "").strip() in {"1", "true", "yes"}
                )
                if insecure:
                    verify_param = False
                elif ca_cert:
                    verify_param = ca_cert
                elif ca_pem:
                    caf = tempfile.NamedTemporaryFile("w", delete=False)
                    caf.write(ca_pem)
                    caf.flush()
                    caf_path = caf.name
                    verify_param = caf_path
                api_version = api_version or os.getenv("FLOW_SLURM_API_VERSION", "v0.0.40")
                try:
                    http = _Http(base_url=restd_url.rstrip("/"), verify=verify_param)
                    data = http.request(
                        "POST",
                        f"/slurm/{api_version}/job/submit",
                        json=payload,
                        timeout_seconds=30,
                    )
                except Exception as e:
                    # Provide user-friendly hints mirroring previous behavior
                    msg = str(e)
                    if "SSL" in msg or "certificate" in msg or "tls" in msg.lower():
                        self.handle_error(
                            f"TLS verification failed contacting slurmrestd at {restd_url}. "
                            f"Hint: pass --ca-cert <pem> or --insecure. Error: {e}"
                        )
                        return
                    if "connect" in msg.lower() or "connection" in msg.lower():
                        self.handle_error(
                            f"Failed to connect to slurmrestd at {restd_url}. Ensure the reservation is active and Slurm is provisioned. Error: {e}"
                        )
                        return
                    if "timeout" in msg.lower():
                        self.handle_error(
                            f"Timeout contacting slurmrestd at {restd_url}. Try again or check network. Error: {e}"
                        )
                        return
                    self.handle_error(f"slurmrestd error: {msg}")
                    return
            finally:
                try:
                    if caf:
                        caf.close()
                    if caf_path:
                        try:
                            os.unlink(caf_path)
                        except Exception:
                            pass
                except Exception:
                    pass
            console.print(json.dumps(data))

        @grp.command(name="status", help="List jobs for a Slurm-enabled reservation")
        @click.argument("reservation_id")
        @click.option("--user", default=None)
        @click.option("--state", default=None)
        @click.option(
            "--insecure",
            is_flag=True,
            default=False,
            help="Do not verify TLS certificate for slurmrestd (or set FLOW_SLURM_INSECURE=1)",
        )
        @click.option(
            "--ca-cert",
            type=click.Path(exists=True, dir_okay=False, readable=True, path_type=str),
            default=None,
            help="Path to CA certificate PEM for slurmrestd (or set FLOW_SLURM_CA_CERT)",
        )
        @click.option(
            "--api-version",
            type=str,
            default=None,
            help="slurmrestd API version (e.g., v0.0.40); overrides FLOW_SLURM_API_VERSION",
        )
        def status_cmd(
            reservation_id: str,
            user: str | None,
            state: str | None,
            insecure: bool,
            ca_cert: str | None,
            api_version: str | None,
        ) -> None:
            try:
                slurm = _get_slurm_meta(reservation_id)
            except click.Abort:
                return
            restd_url = slurm.get("restd_url")
            ca_pem = slurm.get("ca_pem")
            if not restd_url:
                self.handle_error("Slurm REST endpoint is not available for this reservation")
                return
            import os
            import tempfile

            from flow.sdk.http import HttpClient as _Http

            params: dict[str, Any] = {}
            if user:
                params["user_name"] = user
            if state:
                params["job_state"] = state
            # TLS verification handling
            verify_param: object = True
            caf = None
            caf_path: str | None = None
            try:
                ca_cert = ca_cert or os.getenv("FLOW_SLURM_CA_CERT")
                insecure = insecure or (
                    os.getenv("FLOW_SLURM_INSECURE", "").strip() in {"1", "true", "yes"}
                )
                if insecure:
                    verify_param = False
                elif ca_cert:
                    verify_param = ca_cert
                elif ca_pem:
                    caf = tempfile.NamedTemporaryFile("w", delete=False)
                    caf.write(ca_pem)
                    caf.flush()
                    caf_path = caf.name
                    verify_param = caf_path
                api_version = api_version or os.getenv("FLOW_SLURM_API_VERSION", "v0.0.40")
                try:
                    http = _Http(base_url=restd_url.rstrip("/"), verify=verify_param)
                    data = http.request(
                        "GET",
                        f"/slurm/{api_version}/jobs",
                        params=params,  # type: ignore[arg-type]
                        timeout_seconds=30,
                    )
                except Exception as e:
                    msg = str(e)
                    if "SSL" in msg or "certificate" in msg or "tls" in msg.lower():
                        self.handle_error(
                            f"TLS verification failed contacting slurmrestd at {restd_url}. "
                            f"Hint: pass --ca-cert <pem> or --insecure. Error: {e}"
                        )
                        return
                    if "connect" in msg.lower() or "connection" in msg.lower():
                        self.handle_error(
                            f"Failed to connect to slurmrestd at {restd_url}. Ensure the reservation is active and Slurm is provisioned. Error: {e}"
                        )
                        return
                    if "timeout" in msg.lower():
                        self.handle_error(
                            f"Timeout contacting slurmrestd at {restd_url}. Try again or check network. Error: {e}"
                        )
                        return
                    self.handle_error(f"slurmrestd error: {msg}")
                    return
            finally:
                try:
                    if caf:
                        caf.close()
                    if caf_path:
                        try:
                            os.unlink(caf_path)
                        except Exception:
                            pass
                except Exception:
                    pass
            console.print(json.dumps(data))

        @grp.command(name="cancel", help="Cancel a Slurm job")
        @click.argument("reservation_id")
        @click.argument("job_id")
        @click.option(
            "--insecure",
            is_flag=True,
            default=False,
            help="Do not verify TLS certificate for slurmrestd (or set FLOW_SLURM_INSECURE=1)",
        )
        @click.option(
            "--ca-cert",
            type=click.Path(exists=True, dir_okay=False, readable=True, path_type=str),
            default=None,
            help="Path to CA certificate PEM for slurmrestd (or set FLOW_SLURM_CA_CERT)",
        )
        @click.option(
            "--api-version",
            type=str,
            default=None,
            help="slurmrestd API version (e.g., v0.0.40); overrides FLOW_SLURM_API_VERSION",
        )
        def cancel_cmd(
            reservation_id: str,
            job_id: str,
            insecure: bool,
            ca_cert: str | None,
            api_version: str | None,
        ) -> None:
            try:
                slurm = _get_slurm_meta(reservation_id)
            except click.Abort:
                return
            restd_url = slurm.get("restd_url")
            ca_pem = slurm.get("ca_pem")
            if not restd_url:
                self.handle_error("Slurm REST endpoint is not available for this reservation")
                return
            import os
            import tempfile

            from flow.sdk.http import HttpClient as _Http

            # TLS verification handling
            verify_param: object = True
            caf = None
            caf_path: str | None = None
            try:
                ca_cert = ca_cert or os.getenv("FLOW_SLURM_CA_CERT")
                insecure = insecure or (
                    os.getenv("FLOW_SLURM_INSECURE", "").strip() in {"1", "true", "yes"}
                )
                if insecure:
                    verify_param = False
                elif ca_cert:
                    verify_param = ca_cert
                elif ca_pem:
                    caf = tempfile.NamedTemporaryFile("w", delete=False)
                    caf.write(ca_pem)
                    caf.flush()
                    caf_path = caf.name
                    verify_param = caf_path
                api_version = api_version or os.getenv("FLOW_SLURM_API_VERSION", "v0.0.40")
                try:
                    http = _Http(base_url=restd_url.rstrip("/"), verify=verify_param)
                    http.request(
                        "DELETE",
                        f"/slurm/{api_version}/job/{job_id}",
                        timeout_seconds=30,
                    )
                except Exception as e:
                    msg = str(e)
                    if "SSL" in msg or "certificate" in msg or "tls" in msg.lower():
                        self.handle_error(
                            f"TLS verification failed contacting slurmrestd at {restd_url}. "
                            f"Hint: pass --ca-cert <pem> or --insecure. Error: {e}"
                        )
                        return
                    if "connect" in msg.lower() or "connection" in msg.lower():
                        self.handle_error(
                            f"Failed to connect to slurmrestd at {restd_url}. Ensure the reservation is active and Slurm is provisioned. Error: {e}"
                        )
                        return
                    if "timeout" in msg.lower():
                        self.handle_error(
                            f"Timeout contacting slurmrestd at {restd_url}. Try again or check network. Error: {e}"
                        )
                        return
                    self.handle_error(f"slurmrestd error: {msg}")
                    return
            finally:
                try:
                    if caf:
                        caf.close()
                    if caf_path:
                        try:
                            os.unlink(caf_path)
                        except Exception:
                            pass
                except Exception:
                    pass
            console.print(f"Cancelled job {job_id}")

        @grp.command(name="ssh", help="Print an SSH command to the reservation's login node")
        @click.argument("reservation_id")
        def ssh_cmd(reservation_id: str) -> None:
            try:
                slurm = _get_slurm_meta(reservation_id)
            except click.Abort:
                return
            host = slurm.get("login_host")
            if not host:
                self.handle_error("No login_host available on this reservation")
                return
            console.print(f"ssh {host}")

        return grp


command = SlurmCommand()
