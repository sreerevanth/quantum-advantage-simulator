"""Reconstruct saved parameters and check against measured energies without retraining."""

import argparse
import json
from pathlib import Path

import numpy as np

from qas import exact, nqs, variational
from qas.artifacts import git
from qas.config import load

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run")
args = parser.parse_args()
run = Path(args.run)
config = load(run / "config.yaml")
rows = json.loads((run / "metrics.json").read_text())["rows"]
checks = []
for row in rows:
    if row["method"] == "exact":
        continue
    n = row["qubits"]
    file = run / "checkpoints" / f"{row['method']}-{n}-{row['seed']}.npz"
    with np.load(file, allow_pickle=False) as archive:
        parameters = dict(archive)
    if row["method"] == "nqs":
        state = nqs.state_from_parameters(parameters)
    else:
        state = variational.prepare(parameters["weights"], n, config.vqe_depth, config.vqe_ansatz)
    energy = exact.expectation(state, exact.hamiltonian(n, config.j, config.h, config.boundary))
    error = abs(energy - row["energy"])
    if error > 1e-8:
        raise SystemExit(f"Checkpoint replay mismatch: {file}, {error}")
    # Original parameter arrays retained; later state reconstruction is separately recorded.
    parameters["state"] = state
    np.savez_compressed(file, **parameters)
    checks.append({"file": file.name, "energy_replay_difference": error})
(run / "checkpoint_replay.json").write_text(
    json.dumps(
        {
            "source_revision": git("rev-parse", "HEAD"),
            "note": "States regenerated from original numeric parameter checkpoints; measured metrics untouched",
            "checks": checks,
        },
        indent=2,
    ),
    encoding="utf-8",
)
print(f"Validated {len(checks)} parameter checkpoints")
