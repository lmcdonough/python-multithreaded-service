# Timing context manager; prints label + duration; resilient to exceptions
from contextlib import contextmanager
import time
from typing import Iterator, Optional
from .logging_config import get_logger

_logger = get_logger("timing")

@contextmanager
def timer(label: Optional[str] = None) -> Iterator[None]:
    start = time.perf_counter()
    try:
        yield
    except Exception as e:
        # Ensure timing still logs even on failure for postmortems
        dur = time.perf_counter() - start
        _logger.error(f"label={label or 'n/a'} error={type(e).__name__} duration_s={dur:.4f}")
        raise
    else:
        dur = time.perf_counter() - start
        print(f"{label or 'block'} {dur:.4f}s")
        