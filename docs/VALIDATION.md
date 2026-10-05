# Validation report

Executed locally on Windows, Python 3.12.4, CPU, 5 October 2026 (Asia/Calcutta). Full output/return codes are persisted under `results/validation/`.

| Check | Executed result |
|---|---|
| pytest | 55 passed, 1 dependency deprecation warning, 99.89 s |
| coverage | 87% overall (890 statements, 116 missed); detailed JSON and log retained |
| scientific numerical cases | 22, including independent Hamiltonian/circuit references, analytical spectra, normalization, seed convergence and noise invariants |
| remaining platform/robustness cases | 33, including config, registry, artifacts, API, mocked IBM lifecycle, pipeline and CLI |
| Ruff lint | passed |
| Ruff formatting | passed |
| mypy | passed, 17 package source files; configured check_untyped_defs and optional import handling |
| dependency consistency | pip check passed |
| packaging | isolated sdist/wheel build passed |
| clean installation | fresh core-only environment installed package; isolated import and exact TFIM returned -2.2360679774997863 |
| optional dependency failure | core-only NQS request returned actionable `[ml]` installation error, retained partial exact evidence |
| CLI smoke checks | 14 passed: top-level and 12 subcommand help invocations, plus expected invalid-config error |
| integration | real multi-seed tiny TFIM artifacts, PNG/SVG generation, tables, read-only API |
| full Phase-1 | 77/77 records executed; 35 NQS pass, 27 VQE pass, 8 VQE fail; NOT_SUPPORTED |
| checkpoint replay | 70/70 full-run parameter checkpoints verified within 1e-8 energy tolerance; 8/8 smoke checkpoints also verified |
| secondary labs | noise and ZNE sweeps; five-seed QAOA and discovery; five-seed VQE preparation/noise sweep |
| hardware | simulator and opt-in guard, mocked transpilation/submission/status/result; actual IBM SDK imports/signatures checked, live QPU NOT EXECUTED |
| security/CI syntax | source secret-pattern scan found no matches; workflow YAML parsed successfully |

`scripts/validate_release.py` persists commands, return codes, and logs; `cli_smoke.json` separately records all expected CLI exit codes. The deprecation warning comes from the installed FastAPI/Starlette HTTPX test-client integration; tests pass without suppressing it. No test tolerances were weakened to make the benchmark pass.

The exact scientific suite includes 12 QuTiP matrix/spectral comparisons (models × sizes × boundaries), known tiny-system energies, complex fidelity/global-phase invariants, seeded RBM and VQE convergence, physical noise-channel invariants and Richardson polynomial cancellation. Circuit tests independently compare custom simulation to PennyLane. These checks validate the listed scope; they do not establish an advantage or arbitrary-system correctness.

The original repository had no executable validation suite. Early intermediate runs found type/lint errors, which were corrected; the final gate log supersedes intermediate outputs. [GitHub-hosted Ubuntu CI passed for f51a3cc](https://github.com/sreerevanth/quantum-advantage-simulator/actions/runs/37227577424), including install, lint, formatting, types, tests, CLI and packaging. The final artifact/documentation snapshot receives its own CI run, reported separately in the completion report.

Dashboard browser checks verified the 77-record TFIM verdict, noise tables, QAOA and circuit-search results, including the separately evaluated human baseline. HTTP tests cover empty catalogs, stored PNG delivery and invalid paths. The packaged HTML was checked in a fresh installation; `results/validation/dashboard.png` records the rendered full-run view.
