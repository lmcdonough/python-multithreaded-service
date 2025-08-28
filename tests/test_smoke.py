# Minimal health checks; fast, deterministic, CI-friendly
from multithreaded_service.timing import timer
from multithreaded_service.io_tasks import pretend_io, iter_pretend_io

# Purpose: sanity-check basic math works in test runner.
# How: tiny deterministic assertion to ensure test infra is sound.
# Use: keeps CI quick and detects catastrophic test environment issues.
def test_smoke_math():
    assert 1 + 1 == 2
    
# Purpose: verify the timing context manager prints a labeled duration.
# How: use `timer("unit-test")` in a with-block, capture stdout via capsys.
# Use: ensures timer prints label and time format expected by other tests.
def test_timer_cm_prints_duration(capsys):
    with timer("unit-test"):
        pass
    out = capsys.readouterr().out
    assert "unit-test" in out
    assert "s" in out
    
# Purpose: confirm iter_pretend_io yields the requested count of durations.
# How: convert generator to list and check length and non-negative durations.
# Use: ensures pretend IO helpers behave deterministically for benchmarks/tests.
def test_iter_pretend_io_yields_three_items():
    gen = iter_pretend_io(count=3, duration=0.01)
    results = list(gen)
    assert len(results) == 3
    assert all(r >= 0 for r in results)