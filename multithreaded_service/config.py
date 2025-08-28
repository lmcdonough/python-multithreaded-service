# Minimal runtime config via env vars; no heavy deps
import os

# Purpose: read a boolean environment variable.
# How: returns default if unset; treats "1","true","yes","on" (case-insensitive) as True.
# Use: call env_bool("MY_FLAG", default=False) to gate features.
def env_bool(key: str, default: bool = False) -> bool:
    try:
        val = os.getenv(key)
        if val is None:
            return default
        return val.lower() in {"1", "true", "yes", "on"}
    except Exception:
        return default
    
# Purpose: read a float environment variable.
# How: converts the env value to float, returns default on unset or parse error.
# Use: call env_float("TIMEOUT_S", 1.0) to configure timeouts.
def env_float(key: str, default: float) -> float:
    try:
        val = os.getenv(key)
        return float(val) if val is not None else default
    except Exception:
        return default
    
# Purpose: read an int environment variable.
# How: converts the env value to int, returns default on unset or parse error.
# Use: call env_int("MAX_WORKERS", 4) to configure concurrency.
def env_int(key: str, default: int) -> int:
    try:
        val = os.getenv(key)
        return int(val) if val is not None else default
    except Exception:
        return default