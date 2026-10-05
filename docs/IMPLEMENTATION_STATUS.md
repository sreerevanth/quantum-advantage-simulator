# Implementation and execution status

The baseline contained only README and LICENSE. Historical evidence and all eight VQE failures are preserved. The current release implements the practical research workflow; scientific conclusions depend on the saved runs, not this capability table.

| Component | Status | Scope |
|---|---|---|
| Exact TFIM/Heisenberg | VALIDATED | dense complex128, analytic/QuTiP checks |
| Original positive RBM | VALIDATED | original locked benchmark retained |
| Complex autoregressive NQS | IMPLEMENTED / VALIDATED | causal amplitudes/sampling, exact-energy training, Adam/SGD, checkpoints, device selection |
| VQE laboratory | IMPLEMENTED / VALIDATED | RY/Rot/ZZ-RX, depths, initializations, optimizers/restarts, gradient diagnostics |
| Finite-shot estimation | VALIDATED | independent Pauli measurements and estimator variance |
| Circuit-level noise | VALIDATED | five local channels, readout and gate-dependent strength; Aer cross-check |
| Folded finite-shot ZNE | VALIDATED | odd scales, linear/Richardson, allocation, equal-budget comparison |
| QAOA | VALIDATED | graph families, depths, optimizers, exact cut and final shots |
| Circuit discovery | VALIDATED | matched budgets, mutation/crossover/elitism, multiple targets/objectives, Pareto, resume |
| H2 | VALIDATED | STO-3G, Jordan–Wigner, two-electron reference and excitation VQE |
| Scaling | IMPLEMENTED | recorded practical CPU study; no extrapolated advantage |
| GPU | IMPLEMENTED / NOT EXECUTED | CPU and unavailable-device paths tested; CUDA hardware absent |
| IBM | IMPLEMENTED / BLOCKED | simulator/mocks; credentials/access absent |
| Suite/resume/integrity | VALIDATED | per-task persistence, internal NQS/search resume, sealed SHA-256 evidence |
| API/dashboard | VALIDATED | read-only artifacts, research views, malformed/path/duplicate/checksum cases |
| License | APPLIED | owner-authorized Apache-2.0 |

Executed experiment counts, negative results, validation totals and release outcome are reported in FINAL_RESEARCH_REPORT.md, VALIDATION.md and GitHub release notes. IMPLEMENTED is not equivalent to experimentally demonstrated advantage.
