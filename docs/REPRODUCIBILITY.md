# Reproducibility

Use the source commit and environment recorded in each artifact, with the saved full configuration. `requirements-lock.txt` captures the Windows environment; platform-specific pins may not install unchanged on Linux. Python 3.11–3.13 is supported. CPU research sets OMP_NUM_THREADS=1 and OPENBLAS_NUM_THREADS=1 to reduce nested threading. Use the same seed, precision and device for numerical comparisons; timings are not byte-reproducible.

New run IDs contain UTC time and a full UUID. Environments record Git SHA/dirty state, Python/platform, dependency versions, CUDA availability and config SHA-256. Full suite tasks contain job parameters, scalar metrics, diagnostics and checkpoint hashes. JSON writes use flush/fsync and atomic replacement. A completed run is sealed; `qas verify RUN` detects changed, missing or extra files. The original evidence has a separate hash inventory and is never retroactively sealed or rewritten.

Resume NQS optimizer state and circuit-search population/RNG internally. Batch resume reuses every completed job; VQE additionally reuses completed restarts, while an interrupted SciPy optimization restarts its unfinished attempt. QAOA resume is at completed sweep-job granularity. This boundary is explicit: no unsupported SciPy optimizer state recovery is claimed. Task checksums are verified before reuse; full sealed runs return without any rewriting.

Commands: `qas suite --full --device cpu --seed 0 --resume RUN`; `qas verify RUN`; `python scripts/build_paper.py RUN`. Keep the small research `.pt` checkpoints with the evidence. Torch loading uses weights_only=True and verifies configuration/Hamiltonian signatures. Do not treat arbitrary untrusted checkpoints as research evidence.

Historical runs include dirty-source provenance from the initial development. Their original configurations, checkpoints and negative verdicts remain visible; replay checks quantify numerical consistency. New full-run numerical modules were committed before execution; concurrently edited API/docs can mark the checkout dirty without changing the loaded numerical source. This limitation is disclosed in the report.

Git attributes preserve evidence bytes across platforms, so checkout line-ending conversion cannot invalidate manifests. CI verifies every committed sealed run. `paper/historical-evidence.sha256.json` inventories the 208 original protected files.
