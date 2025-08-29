# demonstrate why threads help IO but no CPU under CPythons GIL
# show how processes restore true parallelism for CPU bound work
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from multithreaded_service.cpu_tasks import fib
from multithreaded_service.timing import timer

# Tunables: keep small so you can run repeatedly during interview
N = 4 # number of tasks
DURATION = 0.2 # per task IO delay
FIB_N = 30 # per task CPU cost; raise/lower based on your laptop speed

# IO bound workload: sleeping simulates waiting on network/disk
def io_task():
    time.sleep(DURATION)
    
# CPU bound workload: naive Fib burns CPU to surface GIL limits
def cpu_task():
    fib(FIB_N)
    
# Serial IO baseline
with timer("serial_io"):
    for _ in range(N):
        io_task()
        
# Threaded IO: overlaps blocking sleep; GIL is released during sleep
with timer("threaded_io"):
    threads = [threading.Thread(target=io_task) for _ in range(N)]
    for t in threads: t.start()
    for t in threads: t.join()
    
# Serial CPU baseline
with timer("serial_cpu"):
    for _ in range(N):
        cpu_task()
        
# Threaded CPU: still serialized by the GIL for Python bytecode
with timer("threaded_cpu"):
    threads = [threading.Thread(target=cpu_task) for _ in range(N)]
    for t in threads: t.start()
    for t in threads: t.join()
    
# Multiprocessing CPU: true parallelism across cores (seperate interpreters)
if __name__ == "__main__":
    with timer("process_cpu"):
        with ProcessPoolExecutor(max_workers=os.cpu_count() or N) as pool:
            list(pool.map(lambda _: fib(FIB_N), range(N))) # force realization