# Core threading examples: direct Thread, Lock, Queue, and ThreadPoolExecutor
# CHANGED: add Optional to typing imports so queue can use Optional[int] for None sentinel
from typing import List, Tuple, Optional
import threading
import time
import queue
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from .logging_config import get_logger

_logger = get_logger("threading")

# Purpose: Increment a shared counter without synchronization so races occur.
# How: start `n` threads that repeatedly increment a shared variable without a lock.
# Use: run to observe lost updates caused by the GIL and scheduling races.
# example of unsafe shared state mutation without locks
# teaches what a race condition is and why shared memory is dangerous.
def unsafe_increment(n: int, loops: int = 100_000) -> int:
    """Increment shared counter without a lock. Expect race conditions.
    This version intentionally magnifies the race by separating read/modify/write
    and yielding the CPU between them.
    """
    counter = 0
    def _inc():
        nonlocal counter
        for _ in range(loops):
            tmp = counter          # read
            os.sched_yield()       # force a context switch to expose the race
            counter = tmp + 1      # write (not atomic)
    threads = [threading.Thread(target=_inc) for _ in range(n)]
    for t in threads: t.start()
    for t in threads: t.join()
    return counter

# Purpose: Increment a shared counter safely using a Lock so results are deterministic.
# How: each increment happens while holding a threading.Lock to serialize access.
# Use: compare output with `unsafe_increment` to see correctness vs performance tradeoffs.
# safe increment using threading.Lock to prevent race conditions
def safe_increment(n: int, loops: int = 100_000) -> int:
    """Increment shared counter with a lock. Thread-safe, deterministic."""
    counter = 0
    lock = threading.Lock()
    def _inc():
        nonlocal counter
        for _ in range(loops):
            with lock:
                counter += 1
    threads = [threading.Thread(target=_inc) for _ in range(n)]
    for t in threads: t.start()
    for t in threads: t.join()
    return counter

# Purpose: Demonstrate a producer putting items into a Queue and a consumer processing them.
# How: producer enqueues items and a sentinel; consumer dequeues until sentinel then processes items.
# Use: study thread-safe handoff patterns and queue coordination.
# classic producer-consumer with a thread-safe queue
def producer_consumer(num_items: int = 5) -> List[int]:
    """Classic producer-consumer with Queue. Thread-safe handoff."""
    # allow None sentinel by typing the queue as Optional[int]
    q: queue.Queue[Optional[int]] = queue.Queue()
    results: List[int] = []

    def producer():
        for i in range(num_items):
            _logger.info(f"producing {i}")
            q.put(i)
        q.put(None)  # Sentinel to signal consumer to stop (use None consistently)

    def consumer():
        while True:
            item = q.get()
            if item is None:
                q.task_done()
                break
            results.append(item * 2)  # Process item
            q.task_done()

    t1 = threading.Thread(target=producer)
    t2 = threading.Thread(target=consumer)
    t1.start(); t2.start()
    t1.join(); t2.join()
    return results

# Purpose: run `n` sleep tasks concurrently and measure per-task elapsed time.
# How: ThreadPoolExecutor schedules tasks; as_completed yields finished futures as they complete.
# Use: verify concurrency reduces wall-clock time for IO-bound work vs sequential runs.
# thread pool example for scalable IO fan-out
def parallel_sleep(n: int = 4, duration: float = 0.1) -> List[Tuple[int, float]]:
    """Run n tasks concurrently with ThreadPoolExecutor."""
    def _task(i: int) -> Tuple[int, float]:
        start = time.perf_counter()
        time.sleep(duration)
        return i, time.perf_counter() - start

    results: List[Tuple[int, float]] = []
    with ThreadPoolExecutor(max_workers=n) as pool:
        futures = [pool.submit(_task, i) for i in range(n)]
        for f in as_completed(futures):
            try:
                results.append(f.result())
            except Exception as e:
                _logger.error(f"parallel_sleep_error {e}")
    return results