"""Session management for Flow-Colab integration.

Tracks notebook sessions and their associated GPU instances.
"""

import json
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


@dataclass
class FlowJupyterSession:
    """Represents a notebook session with persistent state."""

    session_id: str
    notebook_name: str | None
    notebook_path: str | None
    created_at: datetime
    last_active: datetime
    checkpoint_size_gb: float
    volume_id: str
    instance_type: str
    task_id: str
    status: str = "active"  # active, stopped, expired

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "notebook_name": self.notebook_name,
            "notebook_path": self.notebook_path,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "checkpoint_size_gb": self.checkpoint_size_gb,
            "volume_id": self.volume_id,
            "instance_type": self.instance_type,
            "task_id": self.task_id,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FlowJupyterSession":
        """Create from dictionary."""
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["last_active"] = datetime.fromisoformat(data["last_active"])
        return cls(**data)


class SessionManager:
    """Manages Colab notebook sessions."""

    def __init__(self, storage_path: Path | None = None):
        """Initialize session manager.

        Args:
            storage_path: Path to store session data (default: ~/.flow/colab_sessions.json)
        """
        if storage_path is None:
            storage_path = Path.home() / ".flow" / "colab_sessions.json"

        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._sessions = self._load_sessions()

    def save_session(
        self, session_id: str, task_id: str, instance_type: str, notebook_name: str | None = None
    ) -> FlowJupyterSession:
        """Save a new session or update existing one.

        Args:
            session_id: Unique session identifier
            task_id: Flow task ID for the GPU instance
            instance_type: GPU instance type
            notebook_name: Optional notebook name

        Returns:
            The saved session
        """
        now = datetime.now(timezone.utc)

        if session_id in self._sessions:
            # Update existing session
            session = self._sessions[session_id]
            session.last_active = now
            if notebook_name:
                session.notebook_name = notebook_name
        else:
            # Create new session
            session = FlowJupyterSession(
                session_id=session_id,
                notebook_name=notebook_name,
                notebook_path=None,
                created_at=now,
                last_active=now,
                checkpoint_size_gb=0.0,
                volume_id=f"colab-persist-{session_id}",
                instance_type=instance_type,
                task_id=task_id,
                status="active",
            )
            self._sessions[session_id] = session

        self._save_sessions()
        return session

    def get_session(self, session_id: str) -> FlowJupyterSession | None:
        """Get a session by ID."""
        return self._sessions.get(session_id)

    def find_session_for_notebook(self, notebook_name: str) -> FlowJupyterSession | None:
        """Find the most recent session for a notebook.

        Args:
            notebook_name: Name of the notebook (e.g., "training.ipynb")

        Returns:
            Most recent session for the notebook, or None
        """
        matching_sessions = [
            s
            for s in self._sessions.values()
            if s.notebook_name == notebook_name and s.status == "active"
        ]

        if not matching_sessions:
            return None

        # Return most recently active session
        return max(matching_sessions, key=lambda s: s.last_active)

    def list_sessions(self, status: str | None = None) -> list[FlowJupyterSession]:
        """List all sessions, optionally filtered by status.

        Args:
            status: Filter by status (active, stopped, expired)

        Returns:
            List of sessions sorted by last active time
        """
        sessions = list(self._sessions.values())

        if status:
            sessions = [s for s in sessions if s.status == status]

        # Sort by last active, most recent first
        return sorted(sessions, key=lambda s: s.last_active, reverse=True)

    def update_notebook_info(
        self, session_id: str, notebook_name: str, notebook_path: str | None = None
    ):
        """Update notebook information for a session.

        Called when a notebook connects to the kernel.
        """
        if session_id in self._sessions:
            session = self._sessions[session_id]
            session.notebook_name = notebook_name
            session.notebook_path = notebook_path
            session.last_active = datetime.now(timezone.utc)
            self._save_sessions()

    def update_checkpoint_size(self, session_id: str, size_gb: float):
        """Update checkpoint size for a session."""
        if session_id in self._sessions:
            session = self._sessions[session_id]
            session.checkpoint_size_gb = size_gb
            session.last_active = datetime.now(timezone.utc)
            self._save_sessions()

    def stop_session(self, session_id: str):
        """Mark a session as stopped."""
        if session_id in self._sessions:
            self._sessions[session_id].status = "stopped"
            self._save_sessions()

    def expire_old_sessions(self, days: int = 30):
        """Mark sessions older than N days as expired."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        for session in self._sessions.values():
            if session.last_active < cutoff and session.status == "active":
                session.status = "expired"

        self._save_sessions()

    def _load_sessions(self) -> dict[str, FlowJupyterSession]:
        """Load sessions from storage."""
        if not self.storage_path.exists():
            return {}

        try:
            with open(self.storage_path) as f:
                data = json.load(f)
                return {sid: FlowJupyterSession.from_dict(sdata) for sid, sdata in data.items()}
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Could not load sessions: {e}", file=sys.stderr)
            return {}

    def _save_sessions(self):
        """Save sessions to storage."""
        data = {sid: s.to_dict() for sid, s in self._sessions.items()}
        with open(self.storage_path, "w") as f:
            json.dump(data, f)
