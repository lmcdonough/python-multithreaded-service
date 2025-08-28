<!-- [comment] High-level purpose and fast context -->
# Python Concurrency Lab: Threads, Processes, Asyncio, ETL, GPU Coordination

<!-- [comment] What this lab is -->
This is a focused 6-hour lab to master **Python multithreading** with practical coverage of **multiprocessing**, **asyncio/coroutines**, multicore **ETL** patterns, and **CPU→GPU coordination** you can map onto Knative.

<!-- [comment] Why it matters -->
**Why:** In Kubernetes-native, GPU-heavy platforms, threads excel at I/O multiplexing, processes give true CPU parallelism, and asyncio scales network fan-out. Coordinating CPUs to keep GPUs fed efficiently is critical for cost and performance.

<!-- [comment] How we practice -->
**How:** Small, measurable scripts using `threading`, `Lock`, `Queue`, `ThreadPoolExecutor`, `multiprocessing`, and `asyncio`. We compare I/O vs CPU-bound behavior, apply bounded concurrency and backpressure, and build interview-ready talking points.

<!-- [comment] Miniconda quick start (official flow) -->
## Quick Start

```bash
conda env create -f environment.yml
conda activate py-mt-lab
python -m pip install -U pip
python -m pip install -r requirements.txt
pytest
