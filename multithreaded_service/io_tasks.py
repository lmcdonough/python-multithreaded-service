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

def _session(timeout: float = DEFAULT_TIMEOUT_S, reties: int = DEFAULT_RETRIES) -> requests.Session:
    # Session with retry/backoff for idempotent GETs; production friendly
    sess = requests.Session()
    adapter = HTTPAdapter(
        max_retries=Retry(
            status_forcelist(429, 500, 502, 503, 504),
            total=retries,
            backoff_factor=0.2,
            allowed_methods=frozenset(["GET", "HEAD"])
        )
    )
    sess.headers.update({"User-Agent": DEFAULT_USER_AGENT})
    sess.mount("http://", adapter)
    sess.mount("https://", adapter)
    # Attach default timeout via wrapper to avoid hanging calls
    sess.request = _wrap_request_with_timeout(sess.request, timeout)
    return sess

def _wrap_request_with_timeout(orig_request, timeout: float):
    def request_with_timeout(method, url, **kwargs):
        kwargs.setdefault("timeout", timeout)
        return orig_request(method, url, **kwargs)
    return request_with_timeout

def fetch_url(url: str, timeout: float = DEFAULT_TIMEOUT_S) -> Tuple[int, Optional[str]]:
    """Return (status_code, error). Non-exceptions return error=None"""
    try:
        with _session(timeout=timeout) as s:
            resp = s.get(url)
            return resp.status_code, None
    except requests.RequestException as e:
        _logger.warning(f"fetch_url_failed url={url} err={type(e).__name__}")
        return 0, str(e)
    
def fetch_all_serial(urls: Iterable[str], timeout: float = DEFAULT_TIMEOUT_S) -> List[Tuple[str, int, Optional[str]]]:
    """Serial baseline; returns list of (url, status, error)."""
    results: List[Tuple[str, int, Optional[str]]] = []
    for u in urls:
        code, err = fetch_url(u, timeout=timeout)
        results.append((u, code, err))
    return results

def iter_urls_serial(urls: Iterable[str], timeout: float = DEFAULT_TIMEOUT_S) -> Iterator[Tuple[str, int, Optional[str]]]:
    """Generator yielding (url, status, error) one-by-one; resilient to failures."""
    for u in urls:
        try:
            code, err = fetch_url(u, timeout=timeout)
            yield u, code, err
        except Exception as e:
            _logger.error(f"iter_urls_serial_unexpected url={u} err={type(e).__name__}")
            yield u, 0, str(e)
            
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
    
def iter_pretend_io(count: int, duration: float = 0.05) -> Iterator[float]:
    """Yield 'count' pretend IO durations; generator keeps memory small."""
    for _ in range(count):
        yield pretend_io(duration)