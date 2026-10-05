# Quantum Advantage Simulator 0.1.0

Reproducible small-system quantum research software, licensed Apache-2.0.

Implemented complex autoregressive NQS with resumable training; expanded VQE diagnostics and ansatz studies; finite-shot Pauli measurements, gate-level noise and folded ZNE; graph QAOA; budget-matched evolutionary/random circuit search; minimal-basis H2; device selection; IBM submission/retrieval support; sealed resumable suites; statistics, API and evidence dashboard.

Executed 569 full-suite records plus a 21-record quick suite and eight historical VQE failure diagnostics. Preserved all 208 original evidence files. The full suite has 962 checksum-verified files. Interrupted runs are retained.

Observed results: problem-informed VQE passed 15/15 cases versus 7/15 for the locked baseline at 6-8 qubits. ZNE improved raw error in 161/240 cases and beat the equal-total-shot comparator in 156/240. Heisenberg NQS and circuit search retain negative results. H2 matched its minimal-basis reference within 6.7e-16 hartree. Scaling reached 10 qubits for exact/NQS and eight for VQE.

No quantum advantage, general search superiority, hardware performance or GPU speedup is demonstrated. CUDA hardware and IBM credentials were unavailable. Training uses dense enumerated energies; runtime scopes and approximate seed intervals are documented.

Validation: 95 local tests passed, 91% coverage; lint, formatting, typing, dependency checks, wheel/sdist builds, 17 CLI smoke checks, fresh wheel installation and browser evidence checks passed. GitHub's Python 3.11/3.12/3.13 matrix is a release gate.

A post-run correction includes the initial Hadamard layer in the TFIM circuit-depth bound. Sealed raw metadata is preserved; the correction is documented separately and does not alter energies or fidelities. Recorded run provenance discloses the working-tree state.

See docs/FINAL_RESEARCH_REPORT.md, docs/VALIDATION.md, docs/REPRODUCIBILITY.md and paper/manuscript.md. The evidence ZIP includes figures, tables, checkpoints, configurations and historical evidence. Wheel and source distribution are GitHub release assets; no PyPI publication is claimed.

Reproduce with `pip install -e ".[all,dev]"`, `qas suite --quick`, or `qas suite --full --device cpu --seed 0`. Use `qas verify RUN_DIRECTORY` to check sealed evidence and `qas suite --full --device cpu --seed 0 --resume RUN_DIRECTORY` to verify completed-job resume.
