# Verdict: SUPPORTED

Hypothesis: both approximations meet the registered accuracy thresholds at every size and seed.

Baseline: dense exact diagonalisation.

Criteria: absolute energy error <= 0.05; fidelity >= 0.95.

Passed: 8/8 stochastic evaluations. Complete contract: True.

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
      "mean": 0.004177100025117397,
      "std": null
    }
  },
  {
    "qubits": 2,
    "method": "nqs",
    "absolute_energy_error": {
      "count": 2,
      "mean": 2.7348606490562588e-08,
      "std": 8.199682258079321e-10
    },
    "fidelity": {
      "count": 2,
      "mean": 0.9999999938161991,
      "std": 1.0467288291533362e-10
    },
    "runtime_seconds": {
      "count": 2,
      "mean": 7.115930699990713,
      "std": 9.439352128412088
    }
  },
  {
    "qubits": 2,
    "method": "vqe",
    "absolute_energy_error": {
      "count": 2,
      "mean": 0.0,
      "std": 0.0
    },
    "fidelity": {
      "count": 2,
      "mean": 1.0,
      "std": 0.0
    },
    "runtime_seconds": {
      "count": 2,
      "mean": 10.03776979999384,
      "std": 12.152686735083204
    }
  },
  {
    "qubits": 3,
    "method": "exact",
    "absolute_energy_error": {
      "count": 1,
      "mean": 0.0,
      "std": null
    },
    "fidelity": {
      "count": 1,
      "mean": 0.9999999999999996,
      "std": null
    },
    "runtime_seconds": {
      "count": 1,
      "mean": 0.005121599999256432,
      "std": null
    }
  },
  {
    "qubits": 3,
    "method": "nqs",
    "absolute_energy_error": {
      "count": 2,
      "mean": 3.143350490564245e-06,
      "std": 2.5554650702881607e-06
    },
    "fidelity": {
      "count": 2,
      "mean": 0.9999995264395424,
      "std": 3.396860636776763e-07
    },
    "runtime_seconds": {
      "count": 2,
      "mean": 0.39080949999333825,
      "std": 0.015256535910305381
    }
  },
  {
    "qubits": 3,
    "method": "vqe",
    "absolute_energy_error": {
      "count": 2,
      "mean": 2.220446049250313e-16,
      "std": 3.1401849173675503e-16
    },
    "fidelity": {
      "count": 2,
      "mean": 0.9999999999999997,
      "std": 1.5700924586837752e-16
    },
    "runtime_seconds": {
      "count": 2,
      "mean": 6.061810200000764,
      "std": 3.519832599845407
    }
  }
]
```
