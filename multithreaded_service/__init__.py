# Package namespace; export common defaults for org-wide reuse
DEFAULT_USER_AGENT = "py-mt-lab/1.0 (+https://example.internal)"
DEFAULT_TIMEOUT_S = 5.0
DEFAULT_RETRIES = 2

__all__ = [
    "DEFAULT_USER_AGENT",
    "DEFAULT_TIMEOUT_S",
    "DEFAULT_RETRIES",
]