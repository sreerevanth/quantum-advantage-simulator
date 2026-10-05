# Hardware and device execution

The audited local installation has CPU-only PyTorch, no CUDA device, no IBM token environment configuration and no saved IBM account. GPU benchmarks are NOT EXECUTED — HARDWARE UNAVAILABLE. IBM experiments are BLOCKED — IBM QUANTUM ACCESS REQUIRED. Simulator and mocked SDK paths are tested. No hardware result is fabricated.

Complex NQS supports `cpu`, `cuda` and `auto`; explicit unavailable CUDA raises an actionable error. GPU use requires a CUDA-capable device and a matching PyTorch installation, then `qas suite --full --device cuda --seed 0`. No CPU/GPU speedup claim is made; circuits and references remain CPU implementations.

Install `[hardware]`, configure a Qiskit Runtime account outside the repository, and run `qas hardware --backend BACKEND --shots 1000`. The command transpiles a Bell circuit, submits Runtime SamplerV2, and records backend, job ID, timestamp/provenance, transpiled depth/gates, exact probabilities and seeded simulator counts. Retrieval uses `qas hardware --backend BACKEND --shots 1000 --job-id ID`; pending jobs return a resumable command, completed jobs include hardware counts. Retrieval re-transpiles for diagnostic metadata and does not imply those new diagnostic counts are the original submitted ISA; retain the submission artifact as authoritative. Tokens are never printed or saved to artifacts.

[IBM Sampler documentation](https://quantum.cloud.ibm.com/docs/en/guides/get-started-with-sampler) describes service setup. Real service availability and backend permissions must be supplied externally.
