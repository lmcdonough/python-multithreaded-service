# CPU bound helpers; input validation and safe fallbacks
from typing import Optional
from .logging_config import get_logger

_logger = get_logger("cpu")

# Purpose: compute Fibonacci numbers (naive recursive impl).
# How: recursion; intentionally CPU-heavy to demonstrate GIL and CPU-bound work.
# Use: call fib(n) for small n in tests or to show CPU contention in demos.
def fib(n: int) -> int:
    """Naive Fib; intentionally CPU heavy to surface GIL tradeoffs."""
    if n < 0:
        raise ValueError("n must be >= 0")
    if n <=1:
        return n
    return fib(n - 1) + fib(n - 2)

# Purpose: compute sum of integers from 0 to n-1.
# How: uses Python's built-in sum over range; efficient in Python for moderate n.
# Use: useful to compare CPU-bound loops vs recursive workloads.
def sum_range(n: int) -> int:
    """CPU bound sum with basic validation."""
    if n < 0:
        raise ValueError("n must be >= 0")
    return sum(range(n))

# Purpose: safe wrapper around fib that avoids raising in production paths.
# How: catches exceptions from fib, logs error, and returns a default if provided.
# Use: prefer safe_fib in pipeline stages where failures must not interrupt flow.
def safe_fib(n: int, default: Optional[int] = None) -> int:
    """Guarded wrapper for pipeline stages; never throws in production paths."""
    try:
        return fib(n)
    except Exception as e:
        _logger.error(f"safe_fib_error n={n} err={type(e).__name__}")
        if default is None:
            raise
        return default