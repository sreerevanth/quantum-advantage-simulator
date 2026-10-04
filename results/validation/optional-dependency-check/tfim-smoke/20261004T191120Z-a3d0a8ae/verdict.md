# Verdict: INCONCLUSIVE

Hypothesis: both approximations meet the registered accuracy thresholds at every size and seed.

Baseline: dense exact diagonalisation.

Criteria: absolute energy error <= 0.05; fidelity >= 0.95.

Passed: 0/0 stochastic evaluations. Complete contract: False.

Evidence level: BENCHMARKED. Accuracy support does not establish computational or quantum advantage.

Limitations: exact enumeration RBM, noiseless state-vector VQE, finite seeds, CPU timings include setup; tracemalloc excludes native allocations. Degenerate-state fidelity depends on selected eigenvector.

## Seed statistics

```json
[
  {
    "qubits": 2,
    "method": "exact",
    "absolute_energy_error": {
      "count": 1,
      "mean": 0.0,
      "std": null
    },
    "fidelity": {
      "count": 1,
      "mean": 1.0,
      "std": null
    },
    "runtime_seconds": {
      "count": 1,
      "mean": 0.005583899997873232,
      "std": null
    }
  }
]
```
