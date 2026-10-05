"""Post-run diagnostics for preserved failed VQE states; writes a new sealed run."""

import json
from pathlib import Path

import numpy as np

from qas import artifacts, exact
from qas.integrity import atomic_json, seal

source = Path("results/runs/tfim-phase1/20261004T184629Z-aec0c4bc")
rows = []
for row in json.loads((source / "metrics.json").read_text())["rows"]:
    if row["method"] != "vqe" or row["absolute_energy_error"] <= 0.05 and row["fidelity"] >= 0.95:
        continue
    n = row["qubits"]
    h = exact.hamiltonian(n)
    eigenvalues, vectors = exact.solve(h)
    psi = np.load(source / "checkpoints" / f"vqe-{n}-{row['seed']}.npz")["state"]
    rows.append(
        dict(
            qubits=n,
            seed=row["seed"],
            ground_fidelity=row["fidelity"],
            first_excited_fidelity=float(abs(np.vdot(vectors[:, 1], psi)) ** 2),
            energy_variance=float(np.linalg.norm(h @ psi) ** 2 - row["energy"] ** 2),
            excitation_gap=float(eigenvalues[1] - eigenvalues[0]),
        )
    )
run = artifacts.create(
    "results/analysis",
    {
        "experiment_id": "vqe-failure-analysis",
        "source_run": str(source),
        "kind": "post-run-diagnostic",
        "seeds": [0, 1, 2, 3, 4],
    },
)
atomic_json(
    run / "metrics.json",
    {
        "rows": rows,
        "verdict": "BENCHMARKED",
        "complete": True,
        "metadata_correction": "Full-study TFIM ansatz circuit_depth_upper_bound omitted initial H layer; corrected formula depth*n+1. No raw artifacts altered.",
    },
)
seal(run)
print(run)
