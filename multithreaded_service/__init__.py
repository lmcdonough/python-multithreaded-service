# Package namespace; export common defaults for org-wide reuse

# Purpose: default User-Agent header used by HTTP clients in this package.
# How: string identifying this package; included in requests headers to aid observability.
# Use: referenced by modules that configure requests.Session headers.
DEFAULT_USER_AGENT = "py-mt-lab/1.0 (+https://example.internal)"

# Purpose: default timeout (seconds) for network IO operations.
# How: float seconds applied when no explicit timeout provided.
# Use: pass into _session or fetch helpers to prevent indefinite blocking.
DEFAULT_TIMEOUT_S = 5.0

# Purpose: default retry count for idempotent HTTP requests.
# How: small integer controlling urllib3 Retry.total (retries on certain HTTP errors).
# Use: keeps transient network failures less noisy while avoiding long retry storms.
DEFAULT_RETRIES = 2

__all__ = [
    "DEFAULT_USER_AGENT",
    "DEFAULT_TIMEOUT_S",
    "DEFAULT_RETRIES",
]