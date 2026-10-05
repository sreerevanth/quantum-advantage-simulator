# Release validation

Executed locally on Windows / Python 3.12 CPU, 5 October 2026 (Asia/Calcutta). The original baseline was 65 tests and 87% coverage.

| Check | Result |
|---|---|
| Tests | 95 passed, no warnings; 90.71 seconds |
| Coverage | 91%; 1,669 statements, 154 missed |
| Ruff lint / formatting | Passed |
| mypy | Passed, 26 package source files |
| pip check | Passed |
| Isolated wheel / sdist build | Passed |
| CLI smoke | 17 expected exit codes passed |
| Quick suite integration | All 21 jobs exercised in pytest, including sealed resume without rewriting |
| Full research suite | 569/569 jobs completed, 962 manifest files verified |
| Historical preservation | 208 original result files match pre-work SHA-256 inventory |
| External paths | CUDA unavailable-device path and mocked IBM submit/retrieve tested; real resources unavailable |

Scientific tests cover independent QuTiP spectra, analytic solutions, complex phase invariance, causal NQS normalization/sampling, finite-difference gradients, convergence, optimizer resume equivalence, noiseless folding, physical channels, independent Qiskit Aer amplitude damping, empirical finite-shot variance, H2 sector reference, variational convergence, search budget/Pareto/resume, and descriptive statistics. API tests cover missing/malformed/non-finite evidence, duplicate IDs, pagination, paths and manifest corruption. The end-to-end CLI test runs every research family, generates figures and verifies sealed resume.

The HTTP client deprecation warning was resolved by installing the current supported httpx2 transport. No numerical assertions or research thresholds were loosened. `results/validation/` contains actual commands, logs, coverage and CLI outputs. Fresh-install and browser verification records are saved separately there. CI tests Python 3.11–3.13, package installation and committed evidence integrity; its final outcome is linked in the GitHub release.

Memory in the full study is sampled process RSS, which includes dependencies and can miss short peaks. Historical runs used tracemalloc and are not directly comparable. The first new full attempt was stopped after profiling identified large tracing overhead; its 50 rows remain INCONCLUSIVE. The complete replacement run is a separate immutable directory, with all negative outcomes retained.
