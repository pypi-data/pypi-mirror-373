from __future__ import annotations

"""Generic startup sections registry (entry point target).

During migration this simply proxies to the existing Mithril generic sections
to avoid behavior changes. In future, generic-only sections should live here.
"""

from collections.abc import Callable, Iterable
from typing import Any


def register() -> dict[str, Callable[..., Any]]:
    """Return a mapping of generic section names to factories.

    Consumers may call these factories to obtain section instances.
    """
    try:
        from flow.adapters.providers.builtin.mithril.runtime.startup.sections import (
            CodeUploadSection,
            CompletionSection,
            DevVMDockerSection,
            DockerSection,
            GPUdHealthSection,
            HeaderSection,
            PortForwardingSection,
            RendezvousSection,
            S3Section,
            UserScriptSection,
            VolumeSection,
            WorkloadResumeSection,
        )

        return {
            "header": HeaderSection,
            "port_forwarding": PortForwardingSection,
            "volumes": VolumeSection,
            "s3": S3Section,
            "dev_vm_docker": DevVMDockerSection,
            "gpud_health": GPUdHealthSection,
            "code_upload": CodeUploadSection,
            "rendezvous": RendezvousSection,
            "docker": DockerSection,
            "user_script": UserScriptSection,
            "workload_resume": WorkloadResumeSection,
            "completion": CompletionSection,
        }
    except Exception:
        return {}
