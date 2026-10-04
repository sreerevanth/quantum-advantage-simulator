# Architecture

The research core is a small Python package. Modules retain simple boundaries rather than empty subpackages: `exact` supplies Hamiltonians/states; `metrics` centralizes comparisons; `nqs` and `variational` produce states/parameters/histories; `benchmarks.tfim_compare` enforces one config; `artifacts` persists provenance and verdicts. `noise`, `discovery`, and `hardware` are independent labs. `api` is optional and read-only. `cli`, `registry`, and `plotting` orchestrate stored evidence.

No API or hardware dependency is required for exact calculations. Torch and PennyLane imports are delayed until needed. Dense exact calculations and enumerated RBM have exponential memory cost and are explicitly limited. No large-system capability is implied.
