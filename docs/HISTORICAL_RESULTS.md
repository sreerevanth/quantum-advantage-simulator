# Historical snapshot before the expanded research release

Statements below describe the earlier implementation and licensing state. Current status is in IMPLEMENTATION_STATUS.md.

# Executed results

Primary run: `results/runs/tfim-phase1/20261004T184629Z-aec0c4bc`. Verdict: **NOT_SUPPORTED**. 8 of 70 stochastic evaluations failed the locked accuracy gate. No advantage claim.

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

## Secondary evidence

- `results/labs/circuit-discovery/20261004T185520Z-74c916f4`: 5 seeds; random mean fidelity 1; evolutionary mean fidelity 0.99488491; 200 evaluations per method per seed, fixed human Bell baseline fidelity 1. No discovery advantage conclusion.
- `results/labs/noise-sweep/20261004T185444Z-7ab0f7ff`: 5 evaluations; raw error range 0.0356976–0.68374; maximum mitigated error 8.88178e-16. Analytic channel extrapolation, no finite-shot hardware inference.
- `results/labs/qaoa-maxcut/20261004T185506Z-7ea42980`: 5 seeds; mean approximation ratio 1, sample SD 3.47609e-13; exhaustive maximum cut 2.
- `results/labs/vqe-noise/20261004T190254Z-7250e1d5`: 15 evaluations; raw error range 0.0177097–0.160997; maximum mitigated error 3.10862e-15. Analytic channel extrapolation, no finite-shot hardware inference.
- `results/labs/zne-sweep/20261004T185457Z-f4a482d8`: 5 evaluations; raw error range 0.0356976–0.68374; maximum mitigated error 8.88178e-16. Analytic channel extrapolation, no finite-shot hardware inference.

See FINAL_RESEARCH_REPORT.md for failures, protocol, provenance and threats to validity.
