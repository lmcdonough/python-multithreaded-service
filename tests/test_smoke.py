# Minimal health checks; fast, deterministic, CI-friendly
from multithreaded_service.timing import timer
from multithreaded_service.io_tasks import pretend_io, iter_pretend_io

def test_smloke_math():
    assert 1 + 1 == 2
    
def test_timer_cm_prints_duration(capsys):
    with timer("unit-test"):
        pass
    out = capsys.readouterr().out
    assert "unit-test" in out
    assert "s" in out
    
def test_iter_pretend_io_yields_three_items():
    gen = iter_pretend_io(count=3, duration=0.01)
    results = list(gen)
    assert len(results) == 3
    assert all(r >= 0 for r in results)