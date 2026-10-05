# Architecture

`exact` and `metrics` define dense physics and normalized comparisons. `nqs` preserves the original positive RBM; `autoregressive` implements complex conditional wavefunctions and optimizer checkpoints. `variational` provides RY/Rot and TFIM-inspired VQE plus QAOA. `shot_noise` uses PennyLane density simulation, independent Pauli shots and unitary folding; `noise` retains the distinct historical post-state analytic toy model. `chemistry` builds H2 integrals and the two-electron reference. `discovery` provides restricted gates; `search_lab` adds crossover, Pareto archives and internal resume.

`research` owns the full/quick job plan and resumable batch protocol. `integrity` writes JSON atomically and verifies immutable SHA-256 manifests; `statistical` provides descriptive seed statistics. `research_plots` generates static exports; `scripts/build_paper.py` consumes completed verified artifacts. The historical runner and registry remain independent contracts. `api` and packaged HTML expose read-only evidence; `hardware` is an opt-in SDK boundary.

Core installation requires neither Torch nor a quantum service. Research modules import optional dependencies when invoked. Dense matrices and enumerated training are bounded small-system tools. Device choice is explicit; float64/complex128 is retained across CPU/CUDA paths.
