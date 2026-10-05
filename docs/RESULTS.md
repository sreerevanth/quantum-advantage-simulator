# Executed research results

## NQS methodology and results
A causal conditional MLP at each site outputs a Bernoulli logit and phase increment. Their product gives an exactly normalized complex wavefunction. Batched amplitudes and direct ancestral samples are supported without enumerating configurations during sampling. Energy training still enumerates the entire Hilbert space and multiplies a dense Hamiltonian; it is not a scalable variational Monte Carlo implementation. Adam trains 350 steps with hidden width 16 in float64/complex128; SGD is also implemented. Full optimizer checkpoints preserve parameters, history and gradient norms and reject Hamiltonian/configuration mismatches. The complex stress test adds 0.4 Y on wire zero to TFIM; zero-field Heisenberg tests sign structure.

| Model | Qubits | n | Energy error mean ± sample SD | Fidelity mean ± sample SD |
|---|---|---|---|---|
| complex | 2 | 5 | 4.837375e-12 ± 1.223386e-12 | 1 ± 4.749571e-13 |
| complex | 4 | 5 | 6.89445e-06 ± 6.006265e-06 | 0.9999992 ± 6.663101e-07 |
| complex | 6 | 5 | 8.62481e-05 ± 4.053586e-05 | 0.9999895 ± 5.140457e-06 |
| heisenberg | 2 | 5 | 0.0006378005 ± 8.429859e-05 | 0.9998405 ± 2.107465e-05 |
| heisenberg | 4 | 5 | 0.1385762 ± 0.1861868 | 0.9810855 ± 0.02474918 |
| heisenberg | 6 | 5 | 0.08344978 ± 0.1663192 | 0.9855751 ± 0.02421085 |
| tfim | 2 | 5 | 4.983391e-12 ± 1.589926e-12 | 1 ± 2.891199e-13 |
| tfim | 4 | 5 | 3.96412e-06 ± 3.007219e-06 | 0.9999995 ± 3.428526e-07 |
| tfim | 6 | 5 | 8.551979e-05 ± 4.233492e-05 | 0.9999895 ± 5.42968e-06 |

## VQE methodology, controlled comparisons and failure analysis
The locked variant retains depth-3 RY/CNOT, normal initialization scale 0.3, BFGS and 150 iterations. One-factor variants change depth to 6, initialization to uniform, budget to 300, optimizer to L-BFGS-B or add a second independent restart. A distinct problem-inspired variant uses Hadamard preparation and independent ZZ/RX angles at depth 4. Restart selection minimizes variational energy, never exact fidelity; total iterations and all attempts are retained. Gradient norms, optimizer termination messages, parameters, logical gate counts and depth bounds are recorded. Rot counts as one logical operation. A post-run metadata audit found that the stored TFIM-inspired circuit depth bound omitted its initial Hadamard layer: use depth*n+1, not depth*n, for that ansatz. This correction does not change any energies, fidelities or iteration counts; sealed raw artifacts are preserved. RY/Rot hardware-efficient circuits and normal/uniform/plus/small initialization remain callable.

| Variant | Qubits | Pass / n | Energy error mean ± sample SD | Final gradient norm mean |
|---|---|---|---|---|
| budget | 6 | 4/5 | 0.1011255 ± 0.2201282 | 3.738832e-08 |
| budget | 7 | 1/5 | 0.3564036 ± 0.1954388 | 3.79524e-05 |
| budget | 8 | 2/5 | 0.2469081 ± 0.2146094 | 6.12987e-05 |
| depth | 6 | 3/5 | 0.1930222 ± 0.2641714 | 0.001336349 |
| depth | 7 | 4/5 | 0.08424593 ± 0.186979 | 0.004037592 |
| depth | 8 | 3/5 | 0.1546307 ± 0.2085096 | 0.004065176 |
| initialization | 6 | 3/5 | 0.2005507 ± 0.2687371 | 0.001115886 |
| initialization | 7 | 3/5 | 0.1813427 ± 0.2370527 | 0.003682036 |
| initialization | 8 | 2/5 | 0.2418399 ± 0.2104333 | 0.07271871 |
| locked | 6 | 4/5 | 0.1014692 ± 0.2199377 | 0.00455634 |
| locked | 7 | 1/5 | 0.3564058 ± 0.1954338 | 0.000114624 |
| locked | 8 | 2/5 | 0.246915 ± 0.2146157 | 2.69612e-05 |
| optimizer | 6 | 4/5 | 0.1016188 ± 0.2198657 | 0.003559764 |
| optimizer | 7 | 1/5 | 0.3558698 ± 0.1951108 | 0.001031761 |
| optimizer | 8 | 2/5 | 0.2515934 ± 0.2126254 | 0.0001505174 |
| problem | 6 | 5/5 | 0.0007513298 ± 0.001588112 | 0.003862605 |
| problem | 7 | 5/5 | 0.0002896812 ± 0.0004113192 | 0.003332786 |
| problem | 8 | 5/5 | 0.0133383 ± 0.01567971 | 0.01555926 |
| restart | 6 | 5/5 | 0.002779394 ± 0.000165513 | 0.001145491 |
| restart | 7 | 4/5 | 0.09468889 ± 0.195166 | 0.01258605 |
| restart | 8 | 3/5 | 0.167257 ± 0.2123343 | 0.02617598 |

| Qubits | First excitation gap | Historical failed seeds | Nearest failed energy to first excited energy |
|---|---|---|---|
| 6 | 0.4821467 | 1 | 0.01275681 |
| 7 | 0.4181139 | 4 | 0.02569258 |
| 8 | 0.3690734 | 3 | 0.03217342 |

Post-run projection of all eight historical failed states onto the first excited eigenvector gives fidelity 0.98975237–0.99743251; diagnostics are sealed in `results/analysis/vqe-failure-analysis/20261005T173835Z-09d44c59e4e94c2cb2b36ae1756b4770` and reproducible with `python scripts/analyze_failures.py`. Their nonzero energy variance means they are approximate excited states, not exact eigenstates. This supports convergence to excited-state-like variational stationary points. Comparing gradients, restarts and initialization provides evidence about optimizer sensitivity; finite-depth failures alone do not prove an expressibility barrier, and a finite optimization study cannot uniquely separate all causes. The matched locked subset in this new run is a replication, not a replacement of the historical evidence. Full per-seed diagnostics remain in metrics and checkpoints.

## Finite-shot, circuit-noise and mitigation methodology
PennyLane default.mixed applies configurable local depolarization, bit/phase flips, amplitude/phase damping after gates, with a separate two-qubit multiplier. Readout flips attenuate Pauli eigenvalue means at measurement. Independent Pauli terms are sampled with binomial draws from the density-matrix Born probabilities; this is statistically equivalent to independent projective ±1 measurements, not analytic expectation reporting. Measurement basis rotations are ideal, channels are Markovian and local, and no hardware calibration is implied. Each term receives 100, 1,000 or 10,000 shots. Stored estimator variances use independent-term propagation; repeated-seed tests cross-check the predicted variance.

Local folding G(G†G)^k uses scales 1,3,5 and applies noise after every physical gate. Linear least-squares and quadratic Richardson extrapolation preserve their signed weights. Shot budgets, propagated variance, raw/mitigated estimates and an independent equal-total-shot raw comparator are recorded. The full benchmark uses equal allocation; weighted allocation is implemented and tested separately. Noise strengths 0,0.002,0.02,0.1 combine depolarization p, damping p/2 and p/3, readout p/4 and two-qubit multiplier 2 on 2–3 qubits. Preparation angles are fixed independently of the results. Nonlinear damping/readout can violate ideal scaling assumptions. Extrapolated estimates are not clipped to physical bounds.

| Method | Shots/term/scale | Trials | Helped raw | Beat equal-budget raw | Raw error mean | Mitigated error mean |
|---|---|---|---|---|---|---|
| linear | 100 | 40 | 30 | 24 | 0.5258795 | 0.4561415 |
| linear | 1000 | 40 | 30 | 31 | 0.4603394 | 0.3773073 |
| linear | 10000 | 40 | 35 | 32 | 0.4542942 | 0.3656014 |
| richardson | 100 | 40 | 16 | 15 | 0.5258795 | 0.5080297 |
| richardson | 1000 | 40 | 25 | 28 | 0.4603394 | 0.2770635 |
| richardson | 10000 | 40 | 25 | 26 | 0.4542942 | 0.2448482 |

Positive improvement means smaller absolute error; negative improvement records harm. The table pools sizes and strengths for compactness; `statistics.json` retains each complete setting with seed distributions and approximate intervals. Increased variance and failure at low noise/low shots are valid findings. Overhead includes three scaled circuits and an execution-weight multiplier of nine, plus separately recorded comparator shots. Sampling the term means is computationally cheap on a classical simulator; that does not imply cheap experimental execution.

## QAOA methodology and results
Exact bitstring enumeration gives MaxCut reference values. Path, cycle, connected seeded-random and complete graphs use five vertices, p=1,2,3 and BFGS/COBYLA with recorded budgets and evaluations. COBYLA's budget is function evaluations while BFGS uses iterations; these are not equal-cost optimizer comparisons. Final 1,000-shot cut evaluation is recorded separately from analytic optimization. No finite-shot optimization or tiny-graph quantum advantage is claimed.

| Graph | p | Optimizer | n | Ratio mean ± sample SD |
|---|---|---|---|---|
| cycle | 1 | BFGS | 5 | 0.9375 ± 1.14932e-12 |
| cycle | 1 | COBYLA | 5 | 0.9375 ± 1.643306e-08 |
| cycle | 2 | BFGS | 5 | 1 ± 1.548578e-12 |
| cycle | 2 | COBYLA | 5 | 0.9961029 ± 0.006484842 |
| cycle | 3 | BFGS | 5 | 1 ± 9.417697e-13 |
| cycle | 3 | COBYLA | 5 | 0.995461 ± 0.005495329 |
| dense | 1 | BFGS | 5 | 0.984202 ± 2.579925e-15 |
| dense | 1 | COBYLA | 5 | 0.984202 ± 1.001734e-08 |
| dense | 2 | BFGS | 5 | 1 ± 5.561254e-13 |
| dense | 2 | COBYLA | 5 | 0.994878 ± 0.00495943 |
| dense | 3 | BFGS | 5 | 1 ± 1.677917e-13 |
| dense | 3 | COBYLA | 5 | 0.9999322 ± 9.149866e-05 |
| path | 1 | BFGS | 5 | 0.7805462 ± 1.306666e-13 |
| path | 1 | COBYLA | 5 | 0.7805462 ± 2.588239e-08 |
| path | 2 | BFGS | 5 | 0.868407 ± 0.01837764 |
| path | 2 | COBYLA | 5 | 0.8651682 ± 0.0360932 |
| path | 3 | BFGS | 5 | 0.9347695 ± 0.01886053 |
| path | 3 | COBYLA | 5 | 0.891958 ± 0.02158043 |
| random | 1 | BFGS | 5 | 0.8742265 ± 2.019343e-13 |
| random | 1 | COBYLA | 5 | 0.8650584 ± 0.02050037 |
| random | 2 | BFGS | 5 | 0.9252607 ± 0.05002063 |
| random | 2 | COBYLA | 5 | 0.892006 ± 0.0592495 |
| random | 3 | BFGS | 5 | 0.977419 ± 0.002282547 |
| random | 3 | COBYLA | 5 | 0.9568274 ± 0.01549889 |

## Circuit discovery methodology and results
Random and evolutionary search each receive 300 fitness evaluations, population 16, H/RY/RZ/CNOT vocabulary, insertion/deletion/replacement mutation, crossover and elitism. Objectives use target fidelity or energy of the negative target projector, penalized by 0.001 times gates plus scheduled depth. Projector energy is mathematically minus fidelity, so these two labels do not provide independent objective evidence; small search-trajectory differences can arise from floating-point evaluation. Pareto archives retain nondominated quality/gate/depth tradeoffs. Bell, GHZ and three-site cluster targets have explicit human circuits evaluated once separately. These human baselines attain fidelity one; their design cost is not included in the search budget. Neither search's small-space outcome establishes discovery advantage.

| Target | Objective | Method | Fidelity mean ± sample SD | Mean gates | Mean depth |
|---|---|---|---|---|---|
| bell | energy | random | 0.9998564 ± 0.0003211124 | 2.4 | 2.2 |
| bell | energy | evolutionary | 1 ± 0 | 2 | 2 |
| bell | fidelity | random | 0.9998564 ± 0.0003211124 | 2.4 | 2.2 |
| bell | fidelity | evolutionary | 1 ± 0 | 2 | 2 |
| cluster | energy | random | 0.5700482 ± 0.1566325 | 4 | 2.6 |
| cluster | energy | evolutionary | 0.6 ± 0.2236068 | 3 | 1.8 |
| cluster | fidelity | random | 0.5700482 ± 0.1566325 | 4 | 2.6 |
| cluster | fidelity | evolutionary | 0.6 ± 0.2236068 | 3 | 2 |
| ghz | energy | random | 0.8139453 ± 0.2532666 | 4.2 | 3.4 |
| ghz | energy | evolutionary | 0.5 ± 0 | 1 | 1 |
| ghz | fidelity | random | 0.8139453 ± 0.2532666 | 4.2 | 3.4 |
| ghz | fidelity | evolutionary | 0.6 ± 0.2236068 | 1.4 | 1.4 |

## Molecular experiment
H2 uses STO-3G, neutral singlet, both spatial orbitals/four spin orbitals, Jordan–Wigner mapping, two-electron exact sector diagonalization and total Hartree energies including nuclear repulsion. PennyLane differentiable Hartree–Fock generates integrals. VQE starts from |1100> and uses a particle-conserving double excitation, BFGS and float64/complex128. Geometry is in bohr. This is a minimal-basis molecular demonstration, not chemical accuracy against experiment or the complete-basis limit.

| Distance / bohr | Exact energy / Ha | VQE error max / Ha | HF energy / Ha |
|---|---|---|---|
| 1.0 | -1.07897 | 2.220446e-16 | -1.065999 |
| 1.4 | -1.137276 | 6.661338e-16 | -1.116714 |
| 2.0 | -1.088496 | 4.440892e-16 | -1.049171 |

## Scaling study
The measured boundary is 10 qubits for dense exact/NQS and 8 for VQE, selected under approximately 1.6 GiB available memory. It is a budget boundary, not proof that the next size is infeasible. State space is 2^n and dense Hamiltonian storage is 16·4^n bytes. Reference construction/diagonalization time is separate from approximate-method time; end-to-end wall time also includes checkpoint I/O. Process resident memory is sampled every 10 ms, includes imported dependencies and may miss very short peaks; explicit buffer sizes are also retained. The original historical runs used tracemalloc and are not directly memory-comparable. The recorded method-time field also includes observable-metric construction/evaluation. For exact rows it measures that evaluation overhead, not diagonalization; use the reference-time column for exact solver cost. Single-seed timing, cold imports and contention preclude performance advantage claims.

| Qubits | Method | Reference s | Method s | Energy error | Parameters | Sampled RSS bytes | Hamiltonian bytes |
|---|---|---|---|---|---|---|---|
| 2 | exact | 0.000626 | 0.0013482 | 0 | 0 | 425881600 | 256 |
| 2 | autoregressive | 0.0007357 | 0.5875331 | 1.064534e-08 | 132 | 425926656 | 256 |
| 2 | vqe | 0.0005842 | 0.2120251 | 0 | 6 | 425926656 | 256 |
| 4 | exact | 0.0019977 | 0.002501 | 0 | 0 | 425926656 | 4096 |
| 4 | autoregressive | 0.0011702 | 0.792592 | 0.000147371 | 312 | 425906176 | 4096 |
| 4 | vqe | 0.001191 | 3.6191 | 8.881784e-16 | 12 | 425697280 | 4096 |
| 6 | exact | 0.0038529 | 0.0053835 | 0 | 0 | 425697280 | 65536 |
| 6 | autoregressive | 0.0040332 | 0.9652514 | 0.0009937272 | 556 | 426033152 | 65536 |
| 6 | vqe | 0.0050828 | 8.128193 | 0.002681135 | 18 | 426045440 | 65536 |
| 8 | exact | 0.0487072 | 0.0842495 | 0 | 0 | 430764032 | 1048576 |
| 8 | autoregressive | 0.049181 | 1.378475 | 0.002051245 | 864 | 432394240 | 1048576 |
| 8 | vqe | 0.0608692 | 11.19764 | 0.01182083 | 24 | 432312320 | 1048576 |
| 10 | exact | 1.83662 | 1.473163 | 0 | 0 | 520294400 | 16777216 |
| 10 | autoregressive | 1.725476 | 4.707669 | 0.004001206 | 1236 | 539181056 | 16777216 |

