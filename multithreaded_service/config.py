# Minimal runtime config via env vars; no heavy deps
import os

def env_bool(key: str, default: bool = False) -> bool:
    try:
        val = os.getenv(key)
        if val is None:
            return default
        return val.lower() in {"1", "true", "yes", "on"}
    except Exception:
        return default
    
def env_float(key: str, default: float) -> float:
    try:
        val = os.getenv(key)
        return float(val) if val is not None else default
    except Exception:
        return default
    
def env_int(key: str, default: int) -> int:
    try:
        val = os.getenv(key)
        return int(val) if val is not None else default
    except Exception:
        return default