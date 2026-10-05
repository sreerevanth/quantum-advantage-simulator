# Quantum Advantage Simulator

QAS is an executable small-system research framework for exact references, neural quantum states, variational circuits, noise mitigation, and circuit search. **Measure first. Claim second.** No quantum advantage or general neural, variational, hardware or discovery advantage has been established. The original repository contained only README and LICENSE; the scientific implementation is new.

## Install and quickstart

Python 3.12 is validated; supported Python >=3.11. From the checkout:

```sh
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1; POSIX: source .venv/bin/activate
python -m pip install -e '.[dev,ml,quantum,api]'
qas --help
qas exact --config experiments/configs/tfim_exact.yaml
qas benchmark --config experiments/configs/tfim_smoke.yaml
qas benchmark --config experiments/configs/tfim_phase1.yaml
```

Optional groups: ml, quantum, hardware, api, dev, all. Core installation works without optional services. No PyPI publication has been made. requirements-lock.txt captures the executed Windows environment.

## Scientific contract and evidence

Phase-1 locks open-chain TFIM, H=-J sum ZZ-h sum X, J=h=1, 2–8 qubits, seeds 0–4. Exact SciPy diagonalisation is the reference. RBM uses real-positive amplitudes, exact enumeration and Torch Adam. PennyLane VQE uses depth-three RY/CNOT layers, analytic state-vector expectations and SciPy BFGS.

Every stochastic evaluation must have energy error <=0.05 and fidelity >=0.95 for the accuracy hypothesis to be SUPPORTED. Missing evaluations yield INCONCLUSIVE; any complete-contract failure yields NOT_SUPPORTED. Accuracy support never establishes computational advantage. Tests independently compare QuTiP matrices/spectra, analytical energies, optimizer convergence, normalized complex fidelity, seeded reproduction and artifacts.

See [actual results](docs/RESULTS.md), [validation](docs/VALIDATION.md), [methodology](docs/METHODOLOGY.md), and [final research report](docs/FINAL_RESEARCH_REPORT.md).

## CLI

```sh
qas experiment list
qas experiment inspect tfim-phase1
qas experiment run tfim-phase1
qas nqs --config experiments/configs/tfim_nqs.yaml
qas vqe --config experiments/configs/tfim_vqe.yaml
qas noise --config experiments/configs/noise_sweep.yaml
qas mitigate --config experiments/configs/zne.yaml
qas qaoa --config experiments/configs/qaoa.yaml
qas discover --config experiments/configs/discovery.yaml
qas results summarize results/runs --output results/tables/combined.csv
qas results plot results/runs/EXPERIMENT/RUN
qas doctor
qas validate
```

Noise labs use exact local post-state depolarizing/bit-flip channels and Richardson noise-strength extrapolation. They do not model complete device noise or sampled gate folding. MaxCut has an exhaustive classical reference. Evolutionary/random search receive equal fitness evaluation budgets; a fixed human Bell circuit is separately reported. Secondary labs remain separate from Phase-1 evidence.

The optional read-only FastAPI app is constructed with qas.api.create_app(). It exposes /health, /experiments, /experiments/{id}, /runs, /runs/{id}, /results/summary. Registry workflows and validation commands expect a checkout with configs/tests. The packaged dashboard at `/` displays saved runs, verdicts, tables and figures. Start it with `python -m uvicorn qas.api:create_app --factory --host 127.0.0.1 --port 8765`, then open http://127.0.0.1:8765. See [dashboard instructions](docs/DASHBOARD.md).

## Reproduction and layout

Runs persist config.yaml, environment.json, metrics.json, summary.csv, stdout.log, verdict.md, numeric checkpoints and figures under results/runs/EXPERIMENT/RUN. Secondary artifacts live under results/labs. Metadata includes packages, Python/platform/CPU/CUDA, git SHA/dirty flag, UTC timestamp and config hash. Tiny checkpoints and measured failures are retained. Plots read stored measurements and export PNG/SVG; curves show means and dots show actual evaluations. Tables report sample standard deviations.

Set OMP_NUM_THREADS=1 and OPENBLAS_NUM_THREADS=1 before Python starts for small CPU workloads. Timings include tracing and cold setup and are affected by process contention; memory reports Python allocations rather than total process/GPU memory. No speedup conclusion is supported.

- src/qas: scientific modules, benchmarks, artifacts, registry, CLI, API and plotting.
- experiments: registry and validated configs.
- tests: scientific, integration and robustness checks.
- results: runs, plots, tables and validation evidence.
- docs: architecture, methodology, reproducibility, results and reports.

Dense exact references and enumerated RBM scale exponentially. RBM is real-positive, not a general complex NQS. VQE is noiseless/analytic. Finite-shot/QPU VQE, GPU experiments, chemistry, autoregressive/transformer NQS are NOT EXECUTED or future extensions. IBM opt-in and mocked service paths are tested; live access remains BLOCKED pending credentials/hardware. See [status](docs/IMPLEMENTATION_STATUS.md), [hardware](docs/HARDWARE.md), [reproducibility](docs/REPRODUCIBILITY.md), and [architecture](docs/ARCHITECTURE.md).

## Development, citation and license

```sh
ruff check .
ruff format --check .
mypy src/qas
pytest --cov=qas
python -m build
```

CI runs cheap credential-free validation; a manual workflow runs Phase-1. See [contributing](CONTRIBUTING.md), [release notes](CHANGELOG.md) and [citation](CITATION.cff).

The original proprietary [LICENSE](LICENSE) remains pending the owner's license choice. QAS is not yet licensed as open source; no public release has been created.
