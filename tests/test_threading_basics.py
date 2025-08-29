import pytest
from multithreaded_service import threading_basics as tb

# Purpose: demonstrate difference between unsafe and locked increments.
# How: runs an unsafe increment (no lock) and a safe increment (with lock) many times.
# Use: asserts the unsafe result is lower due to race, and safe equals threads*loops.
def test_race_condition():
    wrong = tb.unsafe_increment(4, loops=10_000)
    right = tb.safe_increment(4, loops=10_000)
    # Unsafe version should be less than expected
    assert wrong < right
    # Safe version should equal threads * loops
    assert right == 4 * 10_000
    
# Purpose: validate a simple producer/consumer pipeline produces expected outputs.
# How: calls producer_consumer to run producer/consumer threads and collects results.
# Use: ensures coordination and ordering logic produces deterministic doubled values.
def test_producer_consumer():
    results = tb.producer_consumer(5)
    assert sorted(results) == [i * 2 for i in range(5)]

# Purpose: check parallel sleep tasks run concurrently, not sequentially.
# How: start multiple sleeps in parallel and assert each task's elapsed time ~duration.
# Use: sanity-check that threading reduces wall-clock time for IO-bound sleeps.
def test_parallel_sleep_timing():
    results = tb.parallel_sleep(n=4, duration=0.2)
    assert len(results) == 4
    for _, elapsed in results:
        # Even with 0.2s sleep, elapsed per task should be ~0.2s not 0.8s
        assert elapsed < 0.5