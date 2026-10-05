# Quantum Advantage Simulator

A reproducible small-system research platform for exact references, neural quantum states, variational algorithms, finite-shot circuit noise, mitigation, MaxCut, circuit discovery and H2. **No quantum advantage has been established.** Apache-2.0; version 0.1.0.

## Install

Python 3.11–3.13 is supported; the executed research environment is Python 3.12 on Windows CPU.

```sh
python -m venv .venv
# Activate .venv for your shell
pip install -e '.[dev,ml,quantum,api,validation]'
qas doctor
qas suite --quick --device cpu
qas suite --full --device cpu --seed 0
qas suite --full --device cpu --seed 0 --resume results/research/research-full/RUN
qas verify results/research/research-full/RUN
```

The full suite records 569 jobs: complex autoregressive NQS, seven controlled VQE variants, 100/1,000/10,000-shot circuit-level mitigation, four MaxCut graph families, three circuit-search targets, three H2 geometries and bounded scaling. It resumes completed jobs rather than rerunning them. Internal NQS optimizer and circuit-search checkpoints also resume. GPU selection is available with `--device cuda`; unavailable CUDA fails explicitly. IBM uses the separate opt-in `qas hardware --backend BACKEND --shots 1000` command and optional `[hardware]` dependencies.

## Historical and new evidence

The original locked TFIM benchmark is preserved: 77 records, 35/35 RBM accuracy passes and 27/35 VQE passes. The joint hypothesis is **NOT_SUPPORTED**. New studies have independent run directories; their results do not replace the original negatives. See [research report](docs/FINAL_RESEARCH_REPORT.md), [results](docs/RESULTS.md), [validation](docs/VALIDATION.md), and [implementation status](docs/IMPLEMENTATION_STATUS.md).

```sh
qas experiment list
qas benchmark --config experiments/configs/tfim_phase1.yaml
qas results plot results/runs/tfim-phase1/RUN
```

Dense references and energy-training enumeration remain exponential. The autoregressive model directly samples normalized complex states, but its training here is not scalable VMC. QAOA is optimized analytically and then sampled. Circuit noise is a configurable Markov simulator model, not hardware calibration. ZNE includes unsuccessful trials and equal-total-shot comparators. Hardware/GPU measurements are absent unless explicitly recorded.

## Evidence explorer

```sh
python -m uvicorn qas.api:create_app --factory --host 127.0.0.1 --port 8765
```

Open http://127.0.0.1:8765. Select a saved run and research view to inspect method comparisons, seed distributions, noise/mitigation, graph/search results, chemistry, scaling and limitations. Figures come from stored artifacts. The API is read-only and provides checksum verification.

## Reproduction and paper

Full job plans are in `experiments/configs/research_full.yaml`; protocols are in `experiments/research_registry.yaml`. A completed run contains config, environment, metrics, per-job checksums, optimizer/circuit checkpoints, CSV tables, statistics, PNG/SVG/PDF figures and a sealed manifest. `python scripts/build_paper.py RUN` generates the manuscript and exports in `paper/` from verified evidence. The manuscript is a draft, not an accepted publication.

Run `python scripts/validate_release.py` for local quality gates. Fast CI tests Python 3.11–3.13; heavy experiments use a separate manual workflow. Package wheels/sdists are release artifacts; installation from PyPI is not claimed. See [reproducibility](docs/REPRODUCIBILITY.md), [methodology](docs/METHODOLOGY.md), [hardware](docs/HARDWARE.md), [dashboard](docs/DASHBOARD.md), and [changelog](CHANGELOG.md).

## License

Copyright 2026 S. Sreerevanth. Licensed under [Apache License 2.0](LICENSE), applied with the owner's explicit authorization. Third-party dependencies retain their own licenses. Cite `CITATION.cff` together with the exact source commit and experiment run.
