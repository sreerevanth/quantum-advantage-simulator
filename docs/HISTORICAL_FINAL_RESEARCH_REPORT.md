# Historical snapshot before the expanded research release

Statements below describe the earlier implementation and licensing state. Current status is in IMPLEMENTATION_STATUS.md.

# Final research report

## Abstract

QAS now provides executable and independently checked tiny-system baselines and a common provenance/metrics contract. A complete 2–8-qubit TFIM experiment executed 77 method records (7 exact, 35 RBM, 35 VQE). The registered joint approximation-accuracy hypothesis is **NOT_SUPPORTED**: 8 stochastic evaluations failed at least one threshold. This is a software and benchmark result, not evidence of quantum advantage.

## Research question

Do a real-positive enumerated RBM and a fixed-depth simulated VQE both reproduce the exact open-chain TFIM ground state across all locked sizes and five seeds? Broader efficiency/hardware hypotheses are NOT TESTED.

## Methods and exact baseline

TFIM uses Pauli ZZ couplings and X transverse fields, J=h=1, open boundaries, most-significant-bit wire ordering. Dense complex128 SciPy Hermitian diagonalisation supplies normalized reference states and spectral gaps. Analytical two-site spectra and independently assembled QuTiP TFIM/Heisenberg matrices validate the exact implementation.

## NQS methodology

The RBM uses real float64 visible/hidden biases and weights, 2n hidden units, stable log cosh, full 2^n amplitude normalization, exact energy sums, and differentiable Torch Adam. Initialization seeds 0–4, learning rate 0.03, at most 300 steps, and locked convergence tolerance. Enumeration is exponential and does not demonstrate scalable VMC.

## VQE methodology

PennyLane default.qubit executes depth-three RY layers with nearest-neighbor CNOT chains. SciPy BFGS uses autograd gradients, seeded Gaussian initialization, at most 150 iterations and gradient tolerance 1e-9. Optimizer messages and histories are retained, including unsuccessful terminations/local minima. Expectations are analytic and classical; no shot/QPU claim is made.

## Benchmark protocol and metrics

All methods use the same Hamiltonian and centralized normalized complex fidelity, absolute/relative energy errors, longitudinal/transverse magnetization errors, runtime, and Python allocation peak. Every stochastic record must meet energy error <=0.05 AND fidelity >=0.95. Complete identities are required before a support verdict. Sample SD uses ddof=1; it is neither a confidence interval nor an uncertainty on the exact reference. Zero reference energy has null relative error. Ground-space degeneracy can make single-vector fidelity basis-dependent.

## Reproducibility controls

Run: `results/runs/tfim-phase1/20261004T184629Z-aec0c4bc`. Recorded git revision: `2a48ffcfc76f434e6dbf781b08af225755a4da10`; dirty flag: `True`. Config hash: `07f37a32fc24639971e86722ca442db5ea049e187cf73ff3f08ddafea01190e6`. The full run began before later validation/plotting enhancements; its numerical solver source is preserved in that revision. The untracked environment lock caused a dirty flag; full config and environment are preserved. Seeds, histories, checkpoints, timings, environment packages and verdict are stored. OMP/BLAS threads were set to one. Later source improvements do not overwrite these measurements.

## Executed experiments and results

| Qubits | Method | Seeds | Energy error mean ± sample SD | Fidelity mean ± sample SD | Runtime mean (s) |
|---|---|---|---|---|---|
| 2 | exact | 1 | 0 ± n/a | 1 ± n/a | 0.0030156 |
| 2 | nqs | 5 | 1.60218e-10 ± 1.4688e-10 | 1 ± 3.32106e-11 | 3.14558 |
| 2 | vqe | 5 | 8.88178e-17 ± 1.98603e-16 | 1 ± 0 | 5.04902 |
| 3 | exact | 1 | 0 ± n/a | 1 ± n/a | 0.005328 |
| 3 | nqs | 5 | 4.43509e-07 ± 3.48419e-07 | 0.99999993 ± 5.3943e-08 | 0.8192 |
| 3 | vqe | 5 | 3.55271e-16 ± 1.98603e-16 | 1 ± 2.00148e-16 | 6.55361 |
| 4 | exact | 1 | 0 ± n/a | 1 ± n/a | 0.0085974 |
| 4 | nqs | 5 | 5.06054e-06 ± 5.18827e-06 | 0.99999938 ± 6.72612e-07 | 0.743456 |
| 4 | vqe | 5 | 1.24345e-15 ± 7.94411e-16 | 1 ± 0 | 20.0173 |
| 5 | exact | 1 | 0 ± n/a | 1 ± n/a | 0.0140921 |
| 5 | nqs | 5 | 9.11093e-05 ± 3.08748e-05 | 0.99999137 ± 2.64198e-06 | 0.819099 |
| 5 | vqe | 5 | 0.000847735 ± 0.000289927 | 0.99987381 ± 6.26389e-05 | 57.9592 |
| 6 | exact | 1 | 0 ± n/a | 1 ± n/a | 0.140157 |
| 6 | nqs | 5 | 0.000137929 ± 2.90816e-05 | 0.99998581 ± 2.46995e-06 | 0.895433 |
| 6 | vqe | 5 | 0.101469 ± 0.219938 | 0.79953421 ± 0.446953 | 75.2556 |
| 7 | exact | 1 | 0 ± n/a | 1 ± n/a | 0.0490569 |
| 7 | nqs | 5 | 0.000185068 ± 4.19964e-05 | 0.99998063 ± 4.70186e-06 | 0.967328 |
| 7 | vqe | 5 | 0.356406 ± 0.195434 | 0.19961884 ± 0.446361 | 56.7936 |
| 8 | exact | 1 | 0 ± n/a | 1 ± n/a | 0.287946 |
| 8 | nqs | 5 | 0.000304747 ± 6.10905e-05 | 0.99996795 ± 6.09532e-06 | 1.11723 |
| 8 | vqe | 5 | 0.246915 ± 0.214616 | 0.39846242 ± 0.545617 | 103.096 |

### Failed registered evaluations

| Qubits | Method | Seed | Energy error | Fidelity |
|---|---|---|---|---|
| 6 | vqe | 2 | 0.49490353 | 6.8852651e-12 |
| 7 | vqe | 0 | 0.44380643 | 1.63889e-17 |
| 7 | vqe | 1 | 0.44380643 | 3.2437033e-17 |
| 7 | vqe | 3 | 0.44380643 | 2.1993929e-18 |
| 7 | vqe | 4 | 0.44380643 | 3.6317188e-17 |
| 8 | vqe | 1 | 0.40484332 | 3.4584776e-17 |
| 8 | vqe | 2 | 0.40124686 | 1.0759686e-10 |
| 8 | vqe | 4 | 0.40484332 | 3.6389577e-21 |

### Noise/mitigation, QAOA and discovery

Noise uses exact post-preparation local Pauli channels; Richardson scales probabilities 1,2,3 and cancels low-degree polynomial error. The two-qubit analytic model permits nearly exact cancellation, with equal-shot coefficient variance multiplier 19. Actual sampled overhead, realistic gate noise, and QPU mitigation are NOT EXECUTED. The VQE-prepared lab separates preparation error from noise-induced error.

MaxCut QAOA compares expected cut against exhaustive bitstring enumeration. Circuit discovery uses H/RY/CNOT insertion, deletion and replacement, elite population selection, and fidelity minus 0.001 times gate count plus depth. Evolutionary and random search use equal 200-evaluation budgets; a hand-designed Bell circuit is separately reported with one evaluation.

- `results/labs/circuit-discovery/20261004T185520Z-74c916f4`: 5 seeds; random mean fidelity 1; evolutionary mean fidelity 0.99488491; 200 evaluations per method per seed, fixed human Bell baseline fidelity 1. No discovery advantage conclusion.
- `results/labs/noise-sweep/20261004T185444Z-7ab0f7ff`: 5 evaluations; raw error range 0.0356976–0.68374; maximum mitigated error 8.88178e-16. Analytic channel extrapolation, no finite-shot hardware inference.
- `results/labs/qaoa-maxcut/20261004T185506Z-7ea42980`: 5 seeds; mean approximation ratio 1, sample SD 3.47609e-13; exhaustive maximum cut 2.
- `results/labs/vqe-noise/20261004T190254Z-7250e1d5`: 15 evaluations; raw error range 0.0177097–0.160997; maximum mitigated error 3.10862e-15. Analytic channel extrapolation, no finite-shot hardware inference.
- `results/labs/zne-sweep/20261004T185457Z-f4a482d8`: 5 evaluations; raw error range 0.0356976–0.68374; maximum mitigated error 8.88178e-16. Analytic channel extrapolation, no finite-shot hardware inference.

## Statistical/seed analysis

The table reports means and sample standard deviations over five deterministic seeds per approximate method. The joint gate evaluates each seed rather than only averages, preserving local-minimum failures. Five seeds are insufficient for broad tail-risk, confidence or scaling conclusions. No multiple-comparison significance or speedup claim is inferred.

## Limitations and threats to validity

All executed research is classical small-system simulation. Positive RBM cannot describe arbitrary complex/sign-structured states. Dense/enumerated memory is exponential. VQE ansatz and finite optimization budget may limit accuracy or trap local minima. Runtime includes tracemalloc, cold optimizer/import costs and other-process contention; peak Python allocations omit some native/GPU memory. Exact timing includes Hamiltonian construction and diagonalisation, while approximate timing excludes reference preparation: these are method execution costs, not a rigorously normalized end-to-end resource contest. Noise strength scaling is an analytic toy model and no sampled variance was measured. Search target is a small Bell state with a known two-gate human solution. SDK mocks validate interfaces only; live IBM execution and GPU experiments are NOT EXECUTED. Optional H2 and autoregressive/complex NQS remain future work. The read-only dashboard displays persisted evidence without launching experiments. CI cloud validation is reported separately from local validation.

## Supported conclusions

Independent tiny-system physics tests and integration checks support the implemented scientific pipeline within tested sizes/models. Specific analytic extrapolation experiments reduce error under the saved model/configuration. Exact/NQS/VQE benchmarking and negative evidence are reproducible from saved contracts. The joint Phase-1 hypothesis has the verdict **NOT_SUPPORTED**.

## Unsupported conclusions

No quantum, hardware, neural-computational, general VQE, real-device mitigation, or discovery advantage has been established. Small-state fidelity and falling optimization loss do not establish those claims. A negative fixed-contract outcome is retained rather than addressed by post hoc budget changes.

## Future work

Pre-register deeper-ansatz/optimizer comparisons separately; add sampled VMC and complex/autoregressive NQS, finite-shot/channel-per-gate experiments, provider integration and hardware validation, stronger seed studies, and fair end-to-end scaling/resource contracts. A public open-source release requires an explicit license decision; the original proprietary license is retained.
