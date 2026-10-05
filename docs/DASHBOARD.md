# Research evidence explorer

Install `[api]` and start from the checkout with `python -m uvicorn qas.api:create_app --factory --host 127.0.0.1 --port 8765`. Open http://127.0.0.1:8765. The results root defaults to `results` relative to the working directory.

Select a run and research view to inspect NQS/VQE comparisons, seed distributions, finite-shot mitigation, MaxCut, discovery, chemistry and scaling. Graphs are saved PNGs, with publication SVG/PDF exports in each new complete run. Tables show actual measurements; limitations and per-setting statistics remain available. The checksum button verifies sealed evidence; historical/partial runs display UNSEALED. CPU/GPU and hardware comparisons are shown only when such evidence exists; no synthetic measurements are inserted.

The API is read-only. Missing or malformed configurations/metrics and non-finite JSON return controlled 503 responses; duplicate IDs return 409. `/run-catalog?limit=100&offset=0` supports bounded pagination (limit 1–1000); `/runs/ID/integrity` verifies manifests. PNG paths are restricted to the results root. Invalid paths and unknown IDs return 404. Repaired files are read on the next request. The local server is bound to loopback; authentication and public hosting are outside this local evidence viewer's scope.
