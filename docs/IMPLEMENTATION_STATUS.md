# Implementation audit

Audit baseline: c03986e, containing only README.md and proprietary LICENSE. No code, dependencies, tests, registry, or artifacts existed. README implementation claims were unsupported. No existing program could be executed.

| Component | Software status | Evidence |
|---|---|---|
| TFIM / isotropic Heisenberg | VALIDATED | analytical solutions and independent QuTiP matrices/spectra |
| RBM NQS | VALIDATED | real-positive, enumerated full Hilbert space; two-qubit convergence and deterministic seeds |
| PennyLane VQE | VALIDATED | RY/Rot chain ansatz, SciPy BFGS/L-BFGS-B; two-qubit convergence |
| Phase-1 runner | VALIDATED | multi-seed integration and artifacts; full experiment reported separately |
| Configuration / registry | VALIDATED | bounded YAML contracts and registry agreement |
| Metrics / verdicts | VALIDATED | normalized complex fidelity, sample statistics, locked all-seed thresholds |
| Provenance / checkpoints | IMPLEMENTED | environment, git, config hash, parameters and histories |
| Local noise / Richardson extrapolation | VALIDATED | trace/positivity, zero noise, known polynomial cancellation |
| MaxCut QAOA | VALIDATED | two-site exact cut / optimization sanity |
| Circuit discovery | VALIDATED | Bell circuit, deterministic equal-evaluation searches; advantage NOT TESTED |
| Hardware simulator | VALIDATED | seeded Bell shot counts |
| IBM adapter | PARTIAL / NOT EXECUTED | opt-in guard tested; live submission/status/results require credentials and optional SDK |
| Plotting / tables / read-only API | VALIDATED | persisted-artifact integration |
| Dashboard | NOT IMPLEMENTED | optional; plots and API provide stored evidence access |
| Complex/autoregressive NQS / H2 | NOT IMPLEMENTED | future optional research extensions |
| GPU / IBM hardware experiments | NOT EXECUTED | CPU environment; hardware access not configured |
| Open-source release | BLOCKED | existing proprietary license retained; owner must choose open-source terms |

IMPLEMENTED means software exists; VALIDATED indicates the specific correctness checks listed. Neither implies a research advantage. Executed measurements and limitations are recorded in RESULTS.md and FINAL_RESEARCH_REPORT.md.
