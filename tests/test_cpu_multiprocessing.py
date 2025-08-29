# Basic correctness: ensure process pool cputes the same fib values as serial
import os
from cpu_multiprocessing import run_process_pool
from multithreaded_service.cpu_tasks import fib

def test_process_pool_correctness():
    work = [20, 21, 22] # smaller values to keep CI fast
    expected = [(n, fib(n)) for n in work]
    got = sorted(run_process_pool(work, max_workers=min(4, (os.cpu_count() or 2))), key=lambda x: x[0])
    assert got == expected, f"Expected {expected}, got {got}"