# show real multicore speedup by side-stepping the GIL with processes
# Uses ProcessPoolExecutor, with robust guards and annotations
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Iterable, List, Tuple

# We reuse the CPU heavy fib to exaggerate CPU cost (pure Python recursion)
from multithreaded_service.cpu_tasks import fib
from multithreaded_service.timing import timer

# Worker function must be top-level and picklable for "spawn"
def fib_task(n: int) -> int:
    """Compute naive Fib; CPU bound to dmonstrate parallelism"""
    return fib(n)

# Hlper to run a batch of fib tasks across prosses with a fixed pool size
def run_process_pool(nums: Iterable[int], max_workers: int | None = None) -> List[Tuple[int, int]]:
    """Executre fib(n) for each n in nums using a ProcessPoolExecutor
    
    Returns: list of (n, fig(n)) in arbitrary completion order
    Notes:
    - Requires top-level, picklable callables and the __main__ guard
    - On platforms using 'spawn' start method (Windows, macOS), the module is imported in the child; avoid side effects at import time.
    - the __main__ guard is required to avoid infinite process spawning
    """
    results: List[Tuple[int, int]] = []
    with ProcessPoolExecutor(max_workers=max_workers or (os.cpu_count() or 2)) as pool:
        # submit all tasks and collect futures
        futures = {pool.submit(fib_task, n): n for n in nums}
        # as each future completes, get the result
        for fut in as_completed(futures):
            n = futures[fut]
            try:
                results.append((n, fut.result()))
            except Exception as e:
                print(f"fib({n}) generated an exception: {e}")
    return results

# Simple CLI harness for quick, repeatable timings during interview
def main() -> None:
    # Choose a few moderately expensive values; tune if your laptop is fast or slow
    work = [30, 30, 30, 30] # 4 independent CPU bound tasks each taking ~0.2s on a laptop
    workers = os.cpu_count() or 4
    
    # Serial baseline for comparision
    with timer("serial_cpu"):
        serial_out = [(n, fib_task(n)) for n in work]
        
    # Process pool: seperate interpreters, parallel across cores
    with timer("process_cpu"):
        proc_out = run_process_pool(work, max_workers=workers)
        
    # Print to verify correctness and observe ordering differences
    print("serial:", serial_out) # already in order
    print("proc :", sorted(proc_out, key=lambda x: x[0])) # sort for comparision
    
# Required for multiprocessing on Win/Mac (spawn start method)
if __name__ == "__main__":
    main() # run the CLI harness