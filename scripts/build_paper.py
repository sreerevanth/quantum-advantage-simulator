"""Build the paper and reports from completed, checksum-verified evidence only."""

import argparse
import json
import shutil
from collections import Counter
from pathlib import Path

import numpy as np

from qas.exact import hamiltonian, solve
from qas.integrity import verify
from qas.statistical import describe

parser = argparse.ArgumentParser()
parser.add_argument("run")
args = parser.parse_args()
run = Path(args.run)
verify(run)
data = json.loads((run / "metrics.json").read_text())
if not data.get("complete") or len(data["rows"]) != data["expected_jobs"]:
    raise ValueError("Full report requires every planned job")
rows = data["rows"]
paper = Path("paper")
(paper / "figures").mkdir(parents=True, exist_ok=True)
(paper / "tables").mkdir(exist_ok=True)
historical = Path("results/runs/tfim-phase1/20261004T184629Z-aec0c4bc")
old = json.loads((historical / "metrics.json").read_text())
env = json.loads((run / "environment.json").read_text())


def fmt(x):
    return "n/a" if x is None else f"{x:.7g}"


def mean_sd(values):
    d = describe(values)
    return f"{fmt(d['mean'])} ± {fmt(d['std'])}"


def table(headers, records):
    return "\n".join(
        ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
        + ["| " + " | ".join(map(str, r)) + " |" for r in records]
    )


def groups(kind, keys):
    result = {}
    for row in rows:
        if row["kind"] == kind:
            result.setdefault(tuple(row[k] for k in keys), []).append(row)
    return sorted(result.items())


nqs = table(
    ["Model", "Qubits", "n", "Energy error mean ± sample SD", "Fidelity mean ± sample SD"],
    [
        [
            *key,
            len(rs),
            mean_sd([r["absolute_energy_error"] for r in rs]),
            mean_sd([r["fidelity"] for r in rs]),
        ]
        for key, rs in groups("nqs", ["model", "qubits"])
    ],
)
vqe = table(
    [
        "Variant",
        "Qubits",
        "Pass / n",
        "Energy error mean ± sample SD",
        "Final gradient norm mean",
    ],
    [
        [
            *key,
            f"{sum(r['success'] for r in rs)}/{len(rs)}",
            mean_sd([r["absolute_energy_error"] for r in rs]),
            fmt(np.mean([r["final_gradient_norm"] for r in rs])),
        ]
        for key, rs in groups("vqe", ["variant", "qubits"])
    ],
)
mitigation = table(
    [
        "Method",
        "Shots/term/scale",
        "Trials",
        "Helped raw",
        "Beat equal-budget raw",
        "Raw error mean",
        "Mitigated error mean",
    ],
    [
        [
            *key,
            len(rs),
            sum(r["helped"] for r in rs),
            sum(r["mitigated_error"] < r["equal_budget_raw_error"] for r in rs),
            fmt(np.mean([r["raw_error"] for r in rs])),
            fmt(np.mean([r["mitigated_error"] for r in rs])),
        ]
        for key, rs in groups("mitigation", ["extrapolation", "shots"])
    ],
)
qaoa = table(
    ["Graph", "p", "Optimizer", "n", "Ratio mean ± sample SD"],
    [
        [*key, len(rs), mean_sd([r["approximation_ratio"] for r in rs])]
        for key, rs in groups("qaoa", ["family", "depth", "optimizer"])
    ],
)
discovery = table(
    ["Target", "Objective", "Method", "Fidelity mean ± sample SD", "Mean gates", "Mean depth"],
    [
        [
            *key,
            m,
            mean_sd([r[m]["fidelity"] for r in rs]),
            fmt(np.mean([r[m]["gate_count"] for r in rs])),
            fmt(np.mean([r[m]["depth"] for r in rs])),
        ]
        for key, rs in groups("discovery", ["target", "objective"])
        for m in ("random", "evolutionary")
    ],
)
chemistry = table(
    ["Distance / bohr", "Exact energy / Ha", "VQE error max / Ha", "HF energy / Ha"],
    [
        [
            key[0],
            fmt(rs[0]["exact_energy"]),
            fmt(max(r["absolute_energy_error"] for r in rs)),
            fmt(rs[0]["hartree_fock_energy"]),
        ]
        for key, rs in groups("chemistry", ["distance"])
    ],
)
scaling = table(
    [
        "Qubits",
        "Method",
        "Reference s",
        "Method s",
        "Energy error",
        "Parameters",
        "Sampled RSS bytes",
        "Hamiltonian bytes",
    ],
    [
        [
            r["qubits"],
            r["method"],
            fmt(r["reference_seconds"]),
            fmt(r["method_seconds"]),
            fmt(r["absolute_energy_error"]),
            r["parameter_count"],
            r["peak_memory_bytes"],
            r["hamiltonian_bytes"],
        ]
        for r in rows
        if r["kind"] == "scaling"
    ],
)
negative = [
    r
    for r in old["rows"]
    if r["method"] == "vqe" and (r["absolute_energy_error"] > 0.05 or r["fidelity"] < 0.95)
]

failure = []
for n in (6, 7, 8):
    spectrum = solve(hamiltonian(n))[0]
    original = [r for r in negative if r["qubits"] == n]
    failure.append(
        [
            n,
            fmt(spectrum[1] - spectrum[0]),
            len(original),
            fmt(min(abs(r["energy"] - spectrum[1]) for r in original)),
        ]
    )
diagnostic_run = Path(
    "results/analysis/vqe-failure-analysis/20261005T173835Z-09d44c59e4e94c2cb2b36ae1756b4770"
)
verify(diagnostic_run)
diagnostic_rows = json.loads((diagnostic_run / "metrics.json").read_text())["rows"]
excited_min = min(r["first_excited_fidelity"] for r in diagnostic_rows)
excited_max = max(r["first_excited_fidelity"] for r in diagnostic_rows)
failure_table = table(
    [
        "Qubits",
        "First excitation gap",
        "Historical failed seeds",
        "Nearest failed energy to first excited energy",
    ],
    failure,
)
counts = Counter(r["kind"] for r in rows)
noise = [r for r in rows if r["kind"] == "mitigation"]
text = f"""# Quantum Advantage Simulator: reproducible small-system empirical study

## Abstract
We executed {len(rows)} new controlled jobs and retained the original 77-record TFIM benchmark, including all eight original VQE accuracy failures. The framework covers complex autoregressive NQS, variational circuits, gate-level density noise, finite-shot Pauli estimation and folding-based extrapolation, graph optimization, circuit search, molecular H2 and bounded scaling. These classical small-system simulations support reproducible methodological comparisons and expose failures; they do not demonstrate quantum or computational advantage. The mitigation estimate reduced absolute error versus the basic raw estimate in {sum(r["helped"] for r in noise)}/{len(noise)} trials, and beat an equal-total-shot raw estimate in {sum(r["mitigated_error"] < r["equal_budget_raw_error"] for r in noise)}/{len(noise)} trials.

## Research questions and protocol
How do model, ansatz, initialization and budget affect approximation reliability? When does circuit-folded mitigation repay its shot overhead? Can restricted search outperform a fixed human circuit under the stated objectives? The full job plan and descriptive protocol were committed before the full run. The original accuracy criterion (energy error ≤0.05 and fidelity ≥0.95 for every registered row) is unchanged. New studies are exploratory; no post-hoc significance or broad advantage claim is made.

Run: `{run.as_posix()}`. Source commit at creation: `{env["git_sha"]}`. Dirty flag: `{env["git_dirty"]}` (working API/dashboard edits and new evidence were present; numerical implementation was committed separately). Counts: `{dict(counts)}`. The full environment and configuration hashes are stored beside the metrics. Five seeds are used for stochastic comparisons; scaling uses one seed and is descriptive only.

## Exact methodology and historical evidence
Dense complex128 Hermitian TFIM and isotropic Heisenberg matrices use Pauli, not spin-half, coefficients and wire zero as the most significant bit. SciPy diagonalization is independently tested against QuTiP and analytic tiny systems. The original 77 records remain byte-for-byte preserved: 35/35 RBM and 27/35 VQE rows met the locked accuracy thresholds. Joint verdict: NOT_SUPPORTED. The original real-positive RBM remains available and is not relabeled a general complex model.

Historical secondary runs remain in `results/labs/` and are summarized in `docs/HISTORICAL_FINAL_RESEARCH_REPORT.md`: three analytic noise/preparation sweeps, five-seed triangle QAOA and five-seed Bell discovery. Their toy analytic cancellation and tiny-target outcomes are not substituted for the new finite-shot/graph/target studies. The 21-job quick run completed; two development/profiling attempts are retained as partial evidence and excluded from the complete-run summary.

## NQS methodology and results
A causal conditional MLP at each site outputs a Bernoulli logit and phase increment. Their product gives an exactly normalized complex wavefunction. Batched amplitudes and direct ancestral samples are supported without enumerating configurations during sampling. Energy training still enumerates the entire Hilbert space and multiplies a dense Hamiltonian; it is not a scalable variational Monte Carlo implementation. Adam trains 350 steps with hidden width 16 in float64/complex128; SGD is also implemented. Full optimizer checkpoints preserve parameters, history and gradient norms and reject Hamiltonian/configuration mismatches. The complex stress test adds 0.4 Y on wire zero to TFIM; zero-field Heisenberg tests sign structure.

{nqs}

## VQE methodology, controlled comparisons and failure analysis
The locked variant retains depth-3 RY/CNOT, normal initialization scale 0.3, BFGS and 150 iterations. One-factor variants change depth to 6, initialization to uniform, budget to 300, optimizer to L-BFGS-B or add a second independent restart. A distinct problem-inspired variant uses Hadamard preparation and independent ZZ/RX angles at depth 4. Restart selection minimizes variational energy, never exact fidelity; total iterations and all attempts are retained. Gradient norms, optimizer termination messages, parameters, logical gate counts and depth bounds are recorded. Rot counts as one logical operation. A post-run metadata audit found that the stored TFIM-inspired circuit depth bound omitted its initial Hadamard layer: use depth*n+1, not depth*n, for that ansatz. This correction does not change any energies, fidelities or iteration counts; sealed raw artifacts are preserved. RY/Rot hardware-efficient circuits and normal/uniform/plus/small initialization remain callable.

{vqe}

{failure_table}

Post-run projection of all eight historical failed states onto the first excited eigenvector gives fidelity {excited_min:.8f}–{excited_max:.8f}; diagnostics are sealed in `{diagnostic_run.as_posix()}` and reproducible with `python scripts/analyze_failures.py`. Their nonzero energy variance means they are approximate excited states, not exact eigenstates. This supports convergence to excited-state-like variational stationary points. Comparing gradients, restarts and initialization provides evidence about optimizer sensitivity; finite-depth failures alone do not prove an expressibility barrier, and a finite optimization study cannot uniquely separate all causes. The matched locked subset in this new run is a replication, not a replacement of the historical evidence. Full per-seed diagnostics remain in metrics and checkpoints.

## Finite-shot, circuit-noise and mitigation methodology
PennyLane default.mixed applies configurable local depolarization, bit/phase flips, amplitude/phase damping after gates, with a separate two-qubit multiplier. Readout flips attenuate Pauli eigenvalue means at measurement. Independent Pauli terms are sampled with binomial draws from the density-matrix Born probabilities; this is statistically equivalent to independent projective ±1 measurements, not analytic expectation reporting. Measurement basis rotations are ideal, channels are Markovian and local, and no hardware calibration is implied. Each term receives 100, 1,000 or 10,000 shots. Stored estimator variances use independent-term propagation; repeated-seed tests cross-check the predicted variance.

Local folding G(G†G)^k uses scales 1,3,5 and applies noise after every physical gate. Linear least-squares and quadratic Richardson extrapolation preserve their signed weights. Shot budgets, propagated variance, raw/mitigated estimates and an independent equal-total-shot raw comparator are recorded. The full benchmark uses equal allocation; weighted allocation is implemented and tested separately. Noise strengths 0,0.002,0.02,0.1 combine depolarization p, damping p/2 and p/3, readout p/4 and two-qubit multiplier 2 on 2–3 qubits. Preparation angles are fixed independently of the results. Nonlinear damping/readout can violate ideal scaling assumptions. Extrapolated estimates are not clipped to physical bounds.

{mitigation}

Positive improvement means smaller absolute error; negative improvement records harm. The table pools sizes and strengths for compactness; `statistics.json` retains each complete setting with seed distributions and approximate intervals. Increased variance and failure at low noise/low shots are valid findings. Overhead includes three scaled circuits and an execution-weight multiplier of nine, plus separately recorded comparator shots. Sampling the term means is computationally cheap on a classical simulator; that does not imply cheap experimental execution.

## QAOA methodology and results
Exact bitstring enumeration gives MaxCut reference values. Path, cycle, connected seeded-random and complete graphs use five vertices, p=1,2,3 and BFGS/COBYLA with recorded budgets and evaluations. COBYLA's budget is function evaluations while BFGS uses iterations; these are not equal-cost optimizer comparisons. Final 1,000-shot cut evaluation is recorded separately from analytic optimization. No finite-shot optimization or tiny-graph quantum advantage is claimed.

{qaoa}

## Circuit discovery methodology and results
Random and evolutionary search each receive 300 fitness evaluations, population 16, H/RY/RZ/CNOT vocabulary, insertion/deletion/replacement mutation, crossover and elitism. Objectives use target fidelity or energy of the negative target projector, penalized by 0.001 times gates plus scheduled depth. Projector energy is mathematically minus fidelity, so these two labels do not provide independent objective evidence; small search-trajectory differences can arise from floating-point evaluation. Pareto archives retain nondominated quality/gate/depth tradeoffs. Bell, GHZ and three-site cluster targets have explicit human circuits evaluated once separately. These human baselines attain fidelity one; their design cost is not included in the search budget. Neither search's small-space outcome establishes discovery advantage.

{discovery}

## Molecular experiment
H2 uses STO-3G, neutral singlet, both spatial orbitals/four spin orbitals, Jordan–Wigner mapping, two-electron exact sector diagonalization and total Hartree energies including nuclear repulsion. PennyLane differentiable Hartree–Fock generates integrals. VQE starts from |1100> and uses a particle-conserving double excitation, BFGS and float64/complex128. Geometry is in bohr. This is a minimal-basis molecular demonstration, not chemical accuracy against experiment or the complete-basis limit.

{chemistry}

## Scaling study
The measured boundary is 10 qubits for dense exact/NQS and 8 for VQE, selected under approximately 1.6 GiB available memory. It is a budget boundary, not proof that the next size is infeasible. State space is 2^n and dense Hamiltonian storage is 16·4^n bytes. Reference construction/diagonalization time is separate from approximate-method time; end-to-end wall time also includes checkpoint I/O. Process resident memory is sampled every 10 ms, includes imported dependencies and may miss very short peaks; explicit buffer sizes are also retained. The original historical runs used tracemalloc and are not directly memory-comparable. The recorded method-time field also includes observable-metric construction/evaluation. For exact rows it measures that evaluation overhead, not diagonalization; use the reference-time column for exact solver cost. Single-seed timing, cold imports and contention preclude performance advantage claims.

{scaling}

## Statistics, reproducibility and integrity
Report mean, sample SD (ddof=1), median, minimum, maximum and success rates. For ≥5 independent seeds the stored Student-t 95% mean interval is approximate and assumes independent approximately normal seed means; it is not uncertainty in an exact eigenvalue. Small or multimodal samples may violate that approximation. No hypothesis significance testing is performed. Complete task JSON and checkpoints are hashed; atomic replacement protects writes. Resume verifies completed tasks and reuses them, while incomplete optimizer jobs may restart at the documented task boundary. NQS and circuit search resume internal state; VQE retains completed restarts and QAOA retains completed sweep jobs. Completed runs are sealed with SHA-256 manifests and can be verified using `qas verify RUN`.

Reproduce with `pip install -e ".[dev,ml,quantum,api,validation]"`, then `qas suite --full --device cpu --seed 0 --output results/research`. Resume with the same arguments plus `--resume RUN`. `experiments/configs/research_full.yaml` enumerates the plan. Pin the source revision and recorded dependency versions. GPU support selects CUDA explicitly and fails clearly if unavailable; no GPU measurement was made. IBM credentials and saved accounts were absent; the ready command is `qas hardware --backend BACKEND --shots 1000`, with `--job-id` for retrieval. Hardware and simulator results remain distinct.

## Limitations and threats to validity
Small classical simulations, enumerated training, restricted circuits, few seeds, optimizer budget differences, uncalibrated gate-local noise, ideal measurement rotations, finite-shot variance, checkpoint/runtime overhead and one-machine scaling limit generality. Real QPU execution and CUDA acceleration are NOT EXECUTED. Partial development runs are retained as INCONCLUSIVE artifacts, not included in these complete-run tables. Historical negative evidence remains visible. No thresholds were loosened after observing results.

## Supported and unsupported conclusions
Supported: the implemented workflows execute reproducibly on these small systems; independent references and tests validate the specified numerical behavior; some optimization and mitigation settings fail and are preserved. Unsupported: quantum advantage, scalable NQS advantage, universal mitigation benefit, general circuit-discovery superiority, GPU acceleration, hardware performance or chemistry accuracy beyond the specified minimal basis.

## Future research questions
Do larger seed ensembles reproduce optimizer-sensitive failures? How do calibrated correlated channels and noisy measurement rotations affect mitigation? Can stochastic local-energy training and richer complex architectures scale beyond enumeration? These questions require new registered studies; they are not conclusions of this release.

## References
- [PennyLane quantum chemistry](https://docs.pennylane.ai/en/stable/introduction/chemistry.html): differentiable integrals and molecular Hamiltonians.
- [Digital zero-noise extrapolation](https://arxiv.org/abs/2005.10921): unitary folding methodology.
- [Mitiq noise scaling](https://mitiq.readthedocs.io/en/stable/examples/scaling.html): folding and noise-scaling assumptions. QAS implements the restricted odd-scale algorithm directly rather than depending on Mitiq.
- [PennyLane default.mixed](https://www.pennylane.ai/devices/default-mixed): density-matrix circuit backend.

This is a manuscript draft and evidence package, not an accepted publication.
"""
Path("docs/FINAL_RESEARCH_REPORT.md").write_text(text, encoding="utf-8", newline="\n")
Path("docs/RESULTS.md").write_text(
    "# Executed research results\n\n"
    + text[text.index("## NQS methodology") : text.index("## Statistics,")],
    encoding="utf-8",
    newline="\n",
)
(paper / "manuscript.md").write_text(text, encoding="utf-8", newline="\n")
for name, content in [
    ("nqs", nqs),
    ("vqe", vqe),
    ("mitigation", mitigation),
    ("qaoa", qaoa),
    ("discovery", discovery),
    ("chemistry", chemistry),
    ("scaling", scaling),
]:
    (paper / "tables" / f"{name}.md").write_text(content + "\n", encoding="utf-8", newline="\n")
for file in (run / "figures").iterdir():
    shutil.copy2(file, paper / "figures" / file.name)
shutil.copy2(run / "summary.csv", paper / "tables" / "research.csv")
(paper / "README.md").write_text(
    f"# Reproduction\n\nManuscript: manuscript.md. Evidence: `{run.as_posix()}`.\n\nRun `qas verify {run.as_posix()}` then `python scripts/build_paper.py {run.as_posix()}`. Figures and tables are generated from persisted measurements. Original evidence: `{historical.as_posix()}`. No publication acceptance or quantum advantage is claimed.\n",
    encoding="utf-8",
    newline="\n",
)
(paper / "experiment_references.json").write_text(
    json.dumps(
        {
            "full_run": run.as_posix(),
            "historical_run": historical.as_posix(),
            "source_commit": env["git_sha"],
            "counts": dict(counts),
        },
        indent=2,
    ),
    encoding="utf-8",
)
print("Paper and reports generated from", len(rows), "verified rows")
