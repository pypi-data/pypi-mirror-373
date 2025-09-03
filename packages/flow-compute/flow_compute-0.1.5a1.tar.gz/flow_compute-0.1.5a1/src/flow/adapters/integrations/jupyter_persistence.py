"""Persistence utilities for Flow-Colab integration.

Handles state checkpointing and restoration for notebook sessions.
"""

import os
import time
from pathlib import Path
from typing import Any

from flow.errors import FlowError
from flow.sdk.client import Flow


class PersistenceManager:
    """Manages persistent state for Colab notebooks."""

    def __init__(self, flow_client: Flow | None = None):
        """Initialize persistence manager.

        Args:
            flow_client: Flow client for volume management
        """
        self.flow = flow_client
        try:
            from flow.application.config.runtime import settings as _settings  # local import

            colab_cfg = _settings.colab or {}
            self._enabled = bool(colab_cfg.get("persistence", True))
        except Exception:
            self._enabled = os.environ.get("FLOW_COLAB_PERSISTENCE", "true").lower() == "true"

    def is_enabled(self) -> bool:
        """Check if persistence is enabled."""
        return self._enabled

    def ensure_volume(self, region: str, session_id: str, size_gb: int = 1) -> str:
        """Ensure a persistence volume exists for the session.

        Args:
            region: Region to create volume in (colocated with GPU)
            session_id: Session identifier
            size_gb: Volume size in GB

        Returns:
            Volume ID
        """
        if not self.flow:
            raise FlowError("Flow client required for volume management")

        from flow.adapters.resilience.retry import ExponentialBackoffPolicy, with_retry
        from flow.errors import NetworkError

        volume_name = f"colab-persist-{session_id}"

        # Check for existing volume with retry
        _list_policy = ExponentialBackoffPolicy(max_attempts=3, initial_delay=1.0)

        @with_retry(
            policy=_list_policy,
            retryable_exceptions=(NetworkError, ConnectionError),
        )
        def list_volumes():
            return self.flow.list_volumes()

        volumes = list_volumes()
        for vol in volumes:
            if vol.name == volume_name:
                return vol.volume_id

        # Create new volume with retry
        _create_policy = ExponentialBackoffPolicy(max_attempts=3, initial_delay=1.0)

        @with_retry(
            policy=_create_policy,
            retryable_exceptions=(NetworkError, ConnectionError),
        )
        def create_volume():
            return self.flow.create_volume(name=volume_name, size_gb=size_gb)

        volume = create_volume()
        return volume.volume_id

    def get_checkpoint_info(self, volume_id: str) -> dict[str, Any]:
        """Get information about saved checkpoints.

        Args:
            volume_id: Volume containing checkpoints

        Returns:
            Checkpoint metadata
        """
        # In a real implementation, this would query the volume
        # For now, return mock data
        return {
            "size_gb": 2.3,
            "variable_count": 24,
            "restore_time_ms": 89,
            "last_checkpoint": time.time() - 7200,  # 2 hours ago
        }

    def create_kernel_wrapper_script(self) -> str:
        """Create the kernel wrapper script with persistence hooks.

        Returns:
            Path to the wrapper script
        """
        wrapper_code = '''#!/usr/bin/env python3
"""Jupyter kernel wrapper with Flow persistence support."""

import os
import sys
import time
import pickle
import dill
import threading
from pathlib import Path
from datetime import datetime, timezone

# Persistence directory
PERSIST_DIR = Path("/flow/state")
CHECKPOINT_INTERVAL = 1800  # 30 minutes


class FlowPersistentKernel(IPKernelApp):
    """Jupyter kernel with automatic state persistence."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.checkpoint_thread = None
        self.last_checkpoint = None
    
    def initialize(self, argv=None):
        """Initialize kernel and restore state if available."""
        super().initialize(argv)
        
        # Restore previous state if available
        if PERSIST_DIR.exists():
            self._restore_state()
        
        # Start checkpoint thread
        self.checkpoint_thread = threading.Thread(
            target=self._checkpoint_loop,
            daemon=True
        )
        self.checkpoint_thread.start()
    
    def _restore_state(self):
        """Restore saved variables from persistent storage with validation."""
        import fcntl
        import hashlib
        
        state_file = PERSIST_DIR / "notebook_state.pkl"
        lock_file = PERSIST_DIR / ".checkpoint.lock"
        
        if not state_file.exists():
            return
        
        try:
            start_time = time.time()
            
            # Acquire shared lock for reading
            with open(lock_file, 'w') as lock:
                fcntl.flock(lock.fileno(), fcntl.LOCK_SH)
                
                with open(state_file, 'rb') as f:
                    checkpoint_data = f.read()
            
            # Verify checkpoint integrity
            checkpoint = dill.loads(checkpoint_data)
            
            if isinstance(checkpoint, dict) and 'version' in checkpoint:
                # New format with metadata
                if checkpoint['version'] != 1:
                    print(f"[Flow]: Warning: Unknown checkpoint version {checkpoint['version']}")
                    return
                
                # Verify checksum
                stored_checksum = checkpoint.get('checksum')
                checkpoint['checksum'] = None
                recomputed = hashlib.sha256(dill.dumps(checkpoint)).hexdigest()
                
                if stored_checksum != recomputed:
                    print("[Flow]: Error: Checkpoint corrupted (checksum mismatch)", file=sys.stderr)
                    # Try backup if available
                    backup_file = state_file.with_suffix('.pkl.backup')
                    if backup_file.exists():
                        print("[Flow]: Attempting to restore from backup...")
                        with open(backup_file, 'rb') as f:
                            checkpoint = dill.load(f)
                    else:
                        return
                
                saved_state = checkpoint.get('variables', {})
                timestamp = checkpoint.get('timestamp', 'unknown')
            else:
                # Old format - direct variables dict
                saved_state = checkpoint
                timestamp = 'unknown'
            
            # Inject variables into kernel namespace
            self.shell.user_ns.update(saved_state)
            
            restore_time = (time.time() - start_time) * 1000
            num_vars = len(saved_state)
            
            print(f"[Flow]: Restored {num_vars} variables in {restore_time:.0f}ms (checkpoint from {timestamp})")
            
        except Exception as e:
            print(f"[Flow]: Error: Could not restore state: {e}", file=sys.stderr)
            # Don't crash kernel on restore failure
    
    def _checkpoint_loop(self):
        """Background thread for periodic checkpointing."""
        while True:
            time.sleep(CHECKPOINT_INTERVAL)
            self._save_checkpoint()
    
    def _save_checkpoint(self):
        """Save current kernel state to persistent storage with proper atomicity."""
        import fcntl
        import hashlib
        import tempfile
        
        try:
            PERSIST_DIR.mkdir(parents=True, exist_ok=True)
            
            # Get user namespace, excluding builtins and modules
            user_vars = {}
            serialized_vars = {}
            
            for name, value in self.shell.user_ns.items():
                if not name.startswith('_') and not hasattr(value, '__module__'):
                    try:
                        # Serialize once and reuse
                        serialized = dill.dumps(value)
                        user_vars[name] = value
                        serialized_vars[name] = serialized
                    except:
                        pass
            
            # Create checkpoint with metadata
            checkpoint = {
                'version': 1,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'variables': user_vars,
                'checksum': None
            }
            
            # Serialize checkpoint
            checkpoint_data = dill.dumps(checkpoint)
            checksum = hashlib.sha256(checkpoint_data).hexdigest()
            checkpoint['checksum'] = checksum
            checkpoint_data = dill.dumps(checkpoint)
            
            # Use proper atomic write with fsync
            state_file = PERSIST_DIR / "notebook_state.pkl"
            lock_file = PERSIST_DIR / ".checkpoint.lock"
            
            # Acquire exclusive lock to prevent concurrent writes
            with open(lock_file, 'w') as lock:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
                
                # Write to temp file in same directory (same filesystem)
                with tempfile.NamedTemporaryFile(
                    dir=PERSIST_DIR,
                    prefix='checkpoint_',
                    suffix='.tmp',
                    delete=False
                ) as tmp:
                    tmp.write(checkpoint_data)
                    tmp.flush()
                    os.fsync(tmp.fileno())
                
                # Atomic rename
                tmp_path = Path(tmp.name)
                backup_path = state_file.with_suffix('.pkl.backup')
                if state_file.exists():
                    state_file.replace(backup_path)
                tmp_path.replace(state_file)
                
                # Update last checkpoint timestamp
                self.last_checkpoint = datetime.now(timezone.utc)
                
                print(f"[Flow]: Checkpoint saved at {self.last_checkpoint.isoformat()}")
            
        except Exception as e:
            print(f"[Flow]: Error: Could not save checkpoint: {e}", file=sys.stderr)

        '''

        # Write wrapper script to a temporary location
        persist_dir = Path("/tmp/flow")
        persist_dir.mkdir(parents=True, exist_ok=True)
        script_path = persist_dir / "kernel_wrapper.py"
        script_path.write_text(wrapper_code)
        script_path.chmod(0o755)
        return str(script_path)
