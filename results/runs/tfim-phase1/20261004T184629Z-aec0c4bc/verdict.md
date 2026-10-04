# Verdict: NOT_SUPPORTED

Hypothesis: both approximations meet the registered accuracy thresholds at every size and seed.

Baseline: dense exact diagonalisation.

Criteria: absolute energy error <= 0.05; fidelity >= 0.95.

Passed: 62/70 stochastic evaluations. Complete contract: True.

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
      "mean": 0.0030155999993439764,
      "std": null
    }
  },
  {
    "qubits": 2,
    "method": "nqs",
    "absolute_energy_error": {
      "count": 5,
      "mean": 1.6021814985833772e-10,
      "std": 1.4688016346774208e-10
    },
    "fidelity": {
      "count": 5,
      "mean": 0.9999999999636835,
      "std": 3.3210572167159206e-11
    },
    "runtime_seconds": {
      "count": 5,
      "mean": 3.1455754599999635,
      "std": 5.7999056162508635
    }
  },
  {
    "qubits": 2,
    "method": "vqe",
    "absolute_energy_error": {
      "count": 5,
      "mean": 8.881784197001253e-17,
      "std": 1.9860273225978186e-16
    },
    "fidelity": {
      "count": 5,
      "mean": 1.0,
      "std": 0.0
    },
    "runtime_seconds": {
      "count": 5,
      "mean": 5.049016019998817,
      "std": 7.666183219946884
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
      "mean": 0.005327999999281019,
      "std": null
    }
  },
  {
    "qubits": 3,
    "method": "nqs",
    "absolute_energy_error": {
      "count": 5,
      "mean": 4.435085668497152e-07,
      "std": 3.4841894584832544e-07
    },
    "fidelity": {
      "count": 5,
      "mean": 0.999999931409471,
      "std": 5.3942967378143335e-08
    },
    "runtime_seconds": {
      "count": 5,
      "mean": 0.8192001400049775,
      "std": 0.0658817475392282
    }
  },
  {
    "qubits": 3,
    "method": "vqe",
    "absolute_energy_error": {
      "count": 5,
      "mean": 3.552713678800501e-16,
      "std": 1.9860273225978188e-16
    },
    "fidelity": {
      "count": 5,
      "mean": 0.9999999999999997,
      "std": 2.0014830212433605e-16
    },
    "runtime_seconds": {
      "count": 5,
      "mean": 6.553605480003171,
      "std": 3.998155661714512
    }
  },
  {
    "qubits": 4,
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
      "mean": 0.008597399981226772,
      "std": null
    }
  },
  {
    "qubits": 4,
    "method": "nqs",
    "absolute_energy_error": {
      "count": 5,
      "mean": 5.060542475732177e-06,
      "std": 5.188269737677438e-06
    },
    "fidelity": {
      "count": 5,
      "mean": 0.9999993781576901,
      "std": 6.726122653943484e-07
    },
    "runtime_seconds": {
      "count": 5,
      "mean": 0.7434564800001681,
      "std": 0.0654848245603371
    }
  },
  {
    "qubits": 4,
    "method": "vqe",
    "absolute_energy_error": {
      "count": 5,
      "mean": 1.2434497875801752e-15,
      "std": 7.944109290391273e-16
    },
    "fidelity": {
      "count": 5,
      "mean": 1.0,
      "std": 0.0
    },
    "runtime_seconds": {
      "count": 5,
      "mean": 20.017295219999504,
      "std": 5.567201177223672
    }
  },
  {
    "qubits": 5,
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
      "mean": 0.014092099998379126,
      "std": null
    }
  },
  {
    "qubits": 5,
    "method": "nqs",
    "absolute_energy_error": {
      "count": 5,
      "mean": 9.110931878062445e-05,
      "std": 3.087483641479607e-05
    },
    "fidelity": {
      "count": 5,
      "mean": 0.9999913707093718,
      "std": 2.6419849219382712e-06
    },
    "runtime_seconds": {
      "count": 5,
      "mean": 0.8190992999996525,
      "std": 0.0377519322382574
    }
  },
  {
    "qubits": 5,
    "method": "vqe",
    "absolute_energy_error": {
      "count": 5,
      "mean": 0.0008477345418771876,
      "std": 0.0002899270247340797
    },
    "fidelity": {
      "count": 5,
      "mean": 0.9998738074324075,
      "std": 6.263893962907932e-05
    },
    "runtime_seconds": {
      "count": 5,
      "mean": 57.95924195999978,
      "std": 3.3915653807619384
    }
  },
  {
    "qubits": 6,
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
      "mean": 0.14015709998784587,
      "std": null
    }
  },
  {
    "qubits": 6,
    "method": "nqs",
    "absolute_energy_error": {
      "count": 5,
      "mean": 0.00013792932229943488,
      "std": 2.9081587929606165e-05
    },
    "fidelity": {
      "count": 5,
      "mean": 0.999985813464078,
      "std": 2.4699547175928795e-06
    },
    "runtime_seconds": {
      "count": 5,
      "mean": 0.8954327200015542,
      "std": 0.048959933047108786
    }
  },
  {
    "qubits": 6,
    "method": "vqe",
    "absolute_energy_error": {
      "count": 5,
      "mean": 0.10146917746818307,
      "std": 0.2199377475068208
    },
    "fidelity": {
      "count": 5,
      "mean": 0.7995342062156466,
      "std": 0.4469532572808304
    },
    "runtime_seconds": {
      "count": 5,
      "mean": 75.25556331999833,
      "std": 5.835114676640155
    }
  },
  {
    "qubits": 7,
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
      "mean": 0.04905689999577589,
      "std": null
    }
  },
  {
    "qubits": 7,
    "method": "nqs",
    "absolute_energy_error": {
      "count": 5,
      "mean": 0.00018506758379750466,
      "std": 4.1996358808315087e-05
    },
    "fidelity": {
      "count": 5,
      "mean": 0.9999806340733555,
      "std": 4.701864977272998e-06
    },
    "runtime_seconds": {
      "count": 5,
      "mean": 0.9673275199951604,
      "std": 0.020928311117893582
    }
  },
  {
    "qubits": 7,
    "method": "vqe",
    "absolute_energy_error": {
      "count": 5,
      "mean": 0.35640578447160004,
      "std": 0.19543379065895147
    },
    "fidelity": {
      "count": 5,
      "mean": 0.19961884428780707,
      "std": 0.4463613054174822
    },
    "runtime_seconds": {
      "count": 5,
      "mean": 56.79361994000501,
      "std": 20.135567135808678
    }
  },
  {
    "qubits": 8,
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
      "mean": 0.287945900025079,
      "std": null
    }
  },
  {
    "qubits": 8,
    "method": "nqs",
    "absolute_energy_error": {
      "count": 5,
      "mean": 0.0003047473924542743,
      "std": 6.109054364483852e-05
    },
    "fidelity": {
      "count": 5,
      "mean": 0.9999679538286836,
      "std": 6.095321085405749e-06
    },
    "runtime_seconds": {
      "count": 5,
      "mean": 1.117228340008296,
      "std": 0.027783756811853827
    }
  },
  {
    "qubits": 8,
    "method": "vqe",
    "absolute_energy_error": {
      "count": 5,
      "mean": 0.24691503137978507,
      "std": 0.21461568281582805
    },
    "fidelity": {
      "count": 5,
      "mean": 0.39846242448727853,
      "std": 0.5456171454755923
    },
    "runtime_seconds": {
      "count": 5,
      "mean": 103.09561507999315,
      "std": 21.1410876486148
    }
  }
]
```
