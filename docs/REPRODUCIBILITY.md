# Reproducibility

Install Python 3.12 and `pip install -e '.[dev,ml,quantum,api]'`. `requirements-lock.txt` captures the executed Windows environment; platform-dependent wheels may require resolution on Linux. Core dependencies are intentionally separate from optional ML, quantum, hardware, and API groups.

For stable small CPU workloads set OMP_NUM_THREADS=1 and OPENBLAS_NUM_THREADS=1 before Python starts. The environment file records package versions, platform/CPU, CUDA availability, UTC timestamp, git commit/dirty flag, and SHA-256 of sorted canonical JSON config. Seeds/configs and all histories reside alongside measurements. Configuration files, not hardcoded results, control the experiment.

Run directories use UTC timestamps plus random unique IDs; config, environment, metrics, summary, stdout, verdict, checkpoints, and figures share a directory. Tiny numeric checkpoints are retained; large Torch checkpoints are ignored and must be archived separately. Windows timings include Python allocation tracing, first-use imports/optimizer setup, and contention with other processes. Reproduce numerical outputs within tolerances rather than byte-identical time/memory.

Replay with the saved config, matching code revision and package versions. A dirty run requires preserving the working source as well. Partial failures are logged and measured rows retained with INCONCLUSIVE verdicts. No failed evidence is deleted.
