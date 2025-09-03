"""Data models for the flow dev command."""

from typing import TypedDict


class ContainerInfo(TypedDict):
    """Docker container information from 'docker ps --format json'."""

    Names: str
    Status: str
    Image: str
    Command: str
    CreatedAt: str
    ID: str


class ContainerStatus(TypedDict):
    """Container status information for dev VM."""

    active_containers: int
    containers: list[ContainerInfo]
