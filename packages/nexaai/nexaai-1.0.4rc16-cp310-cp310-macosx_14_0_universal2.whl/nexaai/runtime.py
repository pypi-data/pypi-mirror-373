from __future__ import annotations
import atexit
import threading
from typing import Optional, Any

from nexaai.binds import common_bind

_init_lock        = threading.Lock()
_runtime_alive    = False          # global flag

def _ensure_runtime() -> None:
    """Initialise the runtime exactly once (thread‑safe, lazy)."""
    global _runtime_alive
    if not _runtime_alive:
        with _init_lock:
            if not _runtime_alive:          # double‑checked locking
                common_bind.ml_init()
                _runtime_alive = True
                atexit.register(_shutdown_runtime)

def _shutdown_runtime() -> None:
    """Tear the runtime down; idempotent and registered with atexit."""
    global _runtime_alive
    if _runtime_alive:
        common_bind.ml_deinit()
        _runtime_alive = False

# Public helper so advanced users can reclaim memory on demand
shutdown = _shutdown_runtime

# ----------------------------------------------------------------------
# Single public class
# ----------------------------------------------------------------------
class Session:
    """
    Model session **and** runtime guard in one object.

        sess = myrt.Session("foo.mdl")
        out  = sess.run(inputs)
        sess.close()           # optional (model only)

    The global runtime is initialised lazily when the first Session
    is created and stays alive until:
    • the interpreter exits, or
    • `myrt.shutdown()` is called.
    """

    # ---- construction -------------------------------------------------
    def __init__(self, model_path: str) -> None:
        _ensure_runtime()

    # safety net – make GC close the model
    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass

    # allow `with Session(...) as s:` syntax
    def __enter__(self) -> "Session":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
