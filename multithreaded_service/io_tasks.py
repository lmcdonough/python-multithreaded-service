# IO helpers with robust error handling, retries, and safe generators
from typing import Iterable, Iterator, List, Optional, Tuple
import time
import random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from .logging_config import get_logger
from . import DEFAULT_TIMEOUT_S, DEFAULT_USER_AGENT, DEFAULT_RETRIES

_logger = get_logger("io")

# Purpose: create a requests.Session preconfigured with retries and a default timeout.
# How: subclass requests.Session to override request() and set timeout if absent.
# Use: call _session(timeout, retries) to get a configured Session usable with `with`.
def _session(timeout: float = DEFAULT_TIMEOUT_S, retries: int = DEFAULT_RETRIES) -> requests.Session:
    # use a tiny Session subclass to set a default timeout without monkeypatching.
    class _TimeoutSession(requests.Session):
        def __init__(self, timeout_val: float, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._default_timeout = timeout_val

        def request(self, method: str, url: str, **kwargs) -> requests.Response:
            kwargs.setdefault("timeout", self._default_timeout)
            return super().request(method, url, **kwargs)

    sess = _TimeoutSession(timeout)
    adapter = HTTPAdapter(
        max_retries=Retry(
            status_forcelist=[429, 500, 502, 503, 504],
            total=retries,
            backoff_factor=0.2,
            allowed_methods=frozenset(["GET", "HEAD"])
        )
    )
    sess.headers.update({"User-Agent": DEFAULT_USER_AGENT})
    sess.mount("http://", adapter)
    sess.mount("https://", adapter)
    return sess

# Purpose: fetch a single URL and return (status_code, error).
# How: opens a configured Session and uses s.get(); catches requests exceptions.
# Use: returns (HTTP code, None) on success or (0, error-string) on failure.
def fetch_url(url: str, timeout: float = DEFAULT_TIMEOUT_S) -> Tuple[int, Optional[str]]:
    """Return (status_code, error). Non-exceptions return error=None"""
    try:
        with _session(timeout=timeout) as s:
            resp = s.get(url)
            return resp.status_code, None
    except requests.RequestException as e:
        _logger.warning(f"fetch_url_failed url={url} err={type(e).__name__}")
        return 0, str(e)
    
# Purpose: fetch many URLs serially, collecting results.
# How: loops over input iterable and calls fetch_url for each entry.
# Use: returns list of tuples (url, status, error); memory grows with list size.
def fetch_all_serial(urls: Iterable[str], timeout: float = DEFAULT_TIMEOUT_S) -> List[Tuple[str, int, Optional[str]]]:
    """Serial baseline; returns list of (url, status, error)."""
    results: List[Tuple[str, int, Optional[str]]] = []
    for u in urls:
        code, err = fetch_url(u, timeout=timeout)
        results.append((u, code, err))
    return results

# Purpose: a memory-friendly generator yielding per-URL results as they complete.
# How: yields (url, status, error) one at a time and catches unexpected exceptions per-item.
# Use: iterate over this to process results without holding entire list in memory.
def iter_urls_serial(urls: Iterable[str], timeout: float = DEFAULT_TIMEOUT_S) -> Iterator[Tuple[str, int, Optional[str]]]:
    """Generator yielding (url, status, error) one-by-one; resilient to failures."""
    for u in urls:
        try:
            code, err = fetch_url(u, timeout=timeout)
            yield u, code, err
        except Exception as e:
            _logger.error(f"iter_urls_serial_unexpected url={u} err={type(e).__name__}")
            yield u, 0, str(e)
            
# Purpose: simulate IO latency without external network calls.
# How: sleeps for `duration` plus a tiny random jitter, and returns elapsed time.
# Use: helpful for benchmarking or testing concurrent patterns.
def pretend_io(duration: float = 0.1) -> float:
    """SimulatedIO wait using sleep with jitter to mimic variability."""
    start = time.perf_counter()
    try:
        # Small jitter simulates real IO variance without external calls
        time.sleep(max(0.0, duration + random.uniform(-0.02, 0.02)))
        return time.perf_counter() - start
    except Exception as e:
        _logger.error(f"pretend_io_error err={type(e).__name__}")
        return time.perf_counter() - start
    
# Purpose: yield multiple pretend_io durations without allocating a list.
# How: simple generator that calls pretend_io `count` times.
# Use: iterate to simulate repeated IO operations for load tests or demos.
def iter_pretend_io(count: int, duration: float = 0.05) -> Iterator[float]:
    """Yield 'count' pretend IO durations; generator keeps memory small."""
    for _ in range(count):
        yield pretend_io(duration)