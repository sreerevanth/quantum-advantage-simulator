"""Generate measurement tables/report from complete persisted evidence only."""

import argparse
import json
from pathlib import Path

import numpy as np

from qas.config import load

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run", type=Path)
args = parser.parse_args()
if load(args.run / "config.yaml").dict() != load("experiments/configs/tfim_phase1.yaml").dict():
    raise SystemExit("This report requires the locked Phase-1 configuration")
data = json.loads((args.run / "metrics.json").read_text())
if not data["complete"]:
    raise SystemExit("Refusing a final report for incomplete Phase-1 evidence")
config = json.loads((args.run / "environment.json").read_text())
rows = data["rows"]
lines = [
    "| Qubits | Method | Seeds | Energy error mean ± sample SD | Fidelity mean ± sample SD | Runtime mean (s) |",
    "|---|---|---|---|---|---|",
]
for group in data["seed_statistics"]:
    energy = group["absolute_energy_error"]
    fidelity = group["fidelity"]

    def sd(metric):
        return "n/a" if metric["std"] is None else f"{metric['std']:.6g}"

    lines.append(
        f"| {group['qubits']} | {group['method']} | {energy['count']} | {energy['mean']:.6g} ± {sd(energy)} | {fidelity['mean']:.8g} ± {sd(fidelity)} | {group['runtime_seconds']['mean']:.6g} |"
    )
table = "\n".join(lines)
failed = [
    r
    for r in rows
    if r["method"] != "exact" and (r["absolute_energy_error"] > 0.05 or r["fidelity"] < 0.95)
]
fail_table = (
    "| Qubits | Method | Seed | Energy error | Fidelity |\n|---|---|---|---|---|\n"
    + "\n".join(
        f"| {r['qubits']} | {r['method']} | {r['seed']} | {r['absolute_energy_error']:.8g} | {r['fidelity']:.8g} |"
        for r in failed
    )
)
labs = []
for file in sorted(Path("results/labs").glob("*/*/metrics.json")):
    payload = json.loads(file.read_text())
    lab_rows = payload["rows"]
    if "raw_error" in lab_rows[0]:
        detail = f"{len(lab_rows)} evaluations; raw error range {min(r['raw_error'] for r in lab_rows):.6g}–{max(r['raw_error'] for r in lab_rows):.6g}; maximum mitigated error {max(r['mitigated_error'] for r in lab_rows):.6g}. Analytic channel extrapolation, no finite-shot hardware inference."
    elif "approximation_ratio" in lab_rows[0]:
        ratios = [r["approximation_ratio"] for r in lab_rows]
        detail = f"{len(lab_rows)} seeds; mean approximation ratio {np.mean(ratios):.10g}, sample SD {np.std(ratios, ddof=1):.6g}; exhaustive maximum cut {lab_rows[0]['exact_cut']}."
    else:
        detail = f"{len(lab_rows)} seeds; random mean fidelity {np.mean([r['random']['fidelity'] for r in lab_rows]):.8g}; evolutionary mean fidelity {np.mean([r['evolutionary']['fidelity'] for r in lab_rows]):.8g}; 200 evaluations per method per seed, fixed human Bell baseline fidelity 1. No discovery advantage conclusion."
    labs.append(f"- `{file.parent.as_posix()}`: {detail}")
secondary = "\n".join(labs)
body = f"""# Final research report

## Abstract

QAS now provides executable and independently checked tiny-system baselines and a common provenance/metrics contract. A complete 2–8-qubit TFIM experiment executed {len(rows)} method records (7 exact, 35 RBM, 35 VQE). The registered joint approximation-accuracy hypothesis is **{data["verdict"]}**: {len(failed)} stochastic evaluations failed at least one threshold. This is a software and benchmark result, not evidence of quantum advantage.

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

Run: `{args.run.as_posix()}`. Recorded git revision: `{config["git_sha"]}`; dirty flag: `{config["git_dirty"]}`. Config hash: `{config["config_sha256"]}`. The full run began before later validation/plotting enhancements; its numerical solver source is preserved in that revision. The untracked environment lock caused a dirty flag; full config and environment are preserved. Seeds, histories, checkpoints, timings, environment packages and verdict are stored. OMP/BLAS threads were set to one. Later source improvements do not overwrite these measurements.

## Executed experiments and results

{table}

### Failed registered evaluations

{fail_table}

### Noise/mitigation, QAOA and discovery

Noise uses exact post-preparation local Pauli channels; Richardson scales probabilities 1,2,3 and cancels low-degree polynomial error. The two-qubit analytic model permits nearly exact cancellation, with equal-shot coefficient variance multiplier 19. Actual sampled overhead, realistic gate noise, and QPU mitigation are NOT EXECUTED. The VQE-prepared lab separates preparation error from noise-induced error.

MaxCut QAOA compares expected cut against exhaustive bitstring enumeration. Circuit discovery uses H/RY/CNOT insertion, deletion and replacement, elite population selection, and fidelity minus 0.001 times gate count plus depth. Evolutionary and random search use equal 200-evaluation budgets; a hand-designed Bell circuit is separately reported with one evaluation.

{secondary}

## Statistical/seed analysis

The table reports means and sample standard deviations over five deterministic seeds per approximate method. The joint gate evaluates each seed rather than only averages, preserving local-minimum failures. Five seeds are insufficient for broad tail-risk, confidence or scaling conclusions. No multiple-comparison significance or speedup claim is inferred.

## Limitations and threats to validity

All executed research is classical small-system simulation. Positive RBM cannot describe arbitrary complex/sign-structured states. Dense/enumerated memory is exponential. VQE ansatz and finite optimization budget may limit accuracy or trap local minima. Runtime includes tracemalloc, cold optimizer/import costs and other-process contention; peak Python allocations omit some native/GPU memory. Exact timing includes Hamiltonian construction and diagonalisation, while approximate timing excludes reference preparation: these are method execution costs, not a rigorously normalized end-to-end resource contest. Noise strength scaling is an analytic toy model and no sampled variance was measured. Search target is a small Bell state with a known two-gate human solution. SDK mocks validate interfaces only; live IBM execution and GPU experiments are NOT EXECUTED. Optional H2 and autoregressive/complex NQS remain future work. The read-only dashboard displays persisted evidence without launching experiments. CI cloud validation is reported separately from local validation.

## Supported conclusions

Independent tiny-system physics tests and integration checks support the implemented scientific pipeline within tested sizes/models. Specific analytic extrapolation experiments reduce error under the saved model/configuration. Exact/NQS/VQE benchmarking and negative evidence are reproducible from saved contracts. The joint Phase-1 hypothesis has the verdict **{data["verdict"]}**.

## Unsupported conclusions

No quantum, hardware, neural-computational, general VQE, real-device mitigation, or discovery advantage has been established. Small-state fidelity and falling optimization loss do not establish those claims. A negative fixed-contract outcome is retained rather than addressed by post hoc budget changes.

## Future work

Pre-register deeper-ansatz/optimizer comparisons separately; add sampled VMC and complex/autoregressive NQS, finite-shot/channel-per-gate experiments, provider integration and hardware validation, stronger seed studies, and fair end-to-end scaling/resource contracts. A public open-source release requires an explicit license decision; the original proprietary license is retained.
"""
Path("docs/HISTORICAL_FINAL_RESEARCH_REPORT.md").write_text(body, encoding="utf-8")
Path("docs/HISTORICAL_RESULTS.md").write_text(
    f"# Executed results\n\nPrimary run: `{args.run.as_posix()}`. Verdict: **{data['verdict']}**. {len(failed)} of 70 stochastic evaluations failed the locked accuracy gate. No advantage claim.\n\n{table}\n\n## Secondary evidence\n\n{secondary}\n\nSee FINAL_RESEARCH_REPORT.md for failures, protocol, provenance and threats to validity.\n",
    encoding="utf-8",
)
print("Reports generated from complete persisted evidence")
