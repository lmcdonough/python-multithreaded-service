# CPU bound helpers; input validation and safe fallbacks
from typing import Optional
from .logging_config import get_logger

_logger = get_logger("cpu")

def fib(n: int) -> int:
    """Naive Fib; intentionally CPU heave to surface GIL tradeoffs."""
    if n < 0:
        raise ValueError("n must be >= 0")
    if n <=1:
        return n
    return fib(n - 1) + fib(n - 2)

def sum_range(n: int) -> int:
    """CPU bound sum with basic validation."""
    if n < 0:
        raise ValueError("n must be >= 0")
    return sum(range(n))

def safe_fib(n: int, default: Optional[int] = None) -> int:
    """Guarded wrapper for pipeline stages; never throws in production paths."""
    try:
        return fib(n)
    except Exception as e:
        _logger.error(f"safe_fib_error n={n} err={type(e).__name__}")
        if default is None:
            raise
        return default