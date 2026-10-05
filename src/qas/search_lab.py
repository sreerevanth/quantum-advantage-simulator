"""Resumable equal-budget search with crossover and a nondominated archive."""

import hashlib
import json
from pathlib import Path

import numpy as np

from qas.discovery import Gate, depth, execute
from qas.exact import expectation, normalize
from qas.integrity import atomic_json
from qas.metrics import fidelity


def search(
    target,
    n,
    seed=0,
    budget=300,
    max_gates=8,
    population_size=16,
    vocabulary=("H", "RY", "RZ", "CNOT"),
    objective="fidelity",
    matrix=None,
    checkpoint=None,
    resume=False,
):
    target = normalize(target)
    if len(target) != 2**n or not 2 <= n <= 8 or budget < 1 or max_gates < 1 or population_size < 2:
        raise ValueError("Invalid search configuration")
    if (
        not vocabulary
        or set(vocabulary) - {"H", "RY", "RZ", "CNOT"}
        or objective not in ("fidelity", "energy")
    ):
        raise ValueError("Invalid vocabulary/objective")
    if objective == "energy" and matrix is None:
        raise ValueError("Energy objective needs Hamiltonian")
    signature = dict(
        n=n,
        seed=seed,
        max_gates=max_gates,
        population_size=population_size,
        vocabulary=list(vocabulary),
        objective=objective,
        target=hashlib.sha256(target.tobytes()).hexdigest(),
        matrix=None if matrix is None else hashlib.sha256(matrix.tobytes()).hexdigest(),
    )
    saved = {"signature": signature, "methods": {}}
    if resume:
        saved = json.loads(Path(checkpoint).read_text())
        if saved["signature"] != signature:
            raise ValueError("Search checkpoint mismatch")
    output = {}
    for method in ("random", "evolutionary"):
        rng = np.random.default_rng(seed)
        record = saved["methods"].get(
            method, {"evaluations": 0, "population": [], "archive": [], "history": []}
        )
        if "rng" in record:
            rng.bit_generator.state = record["rng"]

        def random_gate(rng=rng):
            name = str(rng.choice(vocabulary))
            a, b = map(int, rng.choice(n, 2, replace=False))
            return Gate(
                name, a, b if name == "CNOT" else -1, float(rng.uniform(-np.pi, np.pi))
            ).__dict__

        for index in range(record["evaluations"], budget):
            pop = record["population"]
            if method == "random" or len(pop) < population_size:
                candidate = [random_gate() for _ in range(int(rng.integers(1, max_gates + 1)))]
            else:
                a = pop[int(rng.integers(len(pop)))]["circuit"]
                b = pop[int(rng.integers(len(pop)))]["circuit"]
                cut = int(rng.integers(len(a) + 1))
                candidate = (a[:cut] + b[cut:])[:max_gates] or [random_gate()]
                candidate = [dict(g) for g in candidate]
                mutation = int(rng.integers(3))
                position = int(rng.integers(len(candidate)))
                if mutation == 0 and len(candidate) < max_gates:
                    candidate.insert(position, random_gate())
                elif mutation == 1 and len(candidate) > 1:
                    candidate.pop(position)
                else:
                    candidate[position] = random_gate()
            gates = [Gate(**g) for g in candidate]
            psi = execute(gates, n)
            quality = fidelity(target, psi)
            energy = expectation(psi, matrix) if matrix is not None else None
            utility = quality if objective == "fidelity" else -expectation(psi, matrix)
            entry = dict(
                circuit=candidate,
                fidelity=quality,
                energy=energy,
                gate_count=len(gates),
                depth=depth(gates, n),
                score=utility - 0.001 * (len(gates) + depth(gates, n)),
            )
            record["population"] = sorted(pop + [entry], key=lambda x: x["score"], reverse=True)[
                :population_size
            ]
            archive = record["archive"] + [entry]

            def dominates(a, b):
                av = [
                    -a["fidelity"] if objective == "fidelity" else a["energy"],
                    a["gate_count"],
                    a["depth"],
                ]
                bv = [
                    -b["fidelity"] if objective == "fidelity" else b["energy"],
                    b["gate_count"],
                    b["depth"],
                ]
                return all(x <= y for x, y in zip(av, bv, strict=True)) and any(
                    x < y for x, y in zip(av, bv, strict=True)
                )

            unique = {json.dumps(a, sort_keys=True): a for a in archive}
            record["archive"] = [
                a for a in unique.values() if not any(dominates(b, a) for b in unique.values())
            ]
            record["history"].append(record["population"][0]["score"])
            record["evaluations"] = index + 1
            record["rng"] = rng.bit_generator.state
            saved["methods"][method] = record
            if checkpoint and (index + 1) % 25 == 0:
                atomic_json(Path(checkpoint), saved)
        if checkpoint:
            atomic_json(Path(checkpoint), saved)
        output[method] = {
            **record["population"][0],
            "evaluations": record["evaluations"],
            "history": record["history"],
            "pareto": record["archive"],
        }
    return output
