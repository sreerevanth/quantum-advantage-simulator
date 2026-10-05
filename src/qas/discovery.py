"""Budget-matched evolutionary and random search in a restricted circuit space."""

from dataclasses import dataclass

import numpy as np

from qas.exact import PAULI, normalize
from qas.metrics import fidelity


@dataclass(frozen=True)
class Gate:
    name: str
    wire: int
    target: int = -1
    angle: float = 0


def execute(circuit: list[Gate], n: int) -> np.ndarray:
    state = np.zeros(2**n, dtype=complex)
    state[0] = 1
    for gate in circuit:
        if not 0 <= gate.wire < n or gate.name not in ("H", "RY", "RZ", "CNOT"):
            raise ValueError("Invalid gate")
        if gate.name == "CNOT":
            if not 0 <= gate.target < n or gate.target == gate.wire:
                raise ValueError("Invalid CNOT")
            indices = np.arange(2**n)
            permutation = indices ^ (
                ((indices >> (n - 1 - gate.wire)) & 1) << (n - 1 - gate.target)
            )
            state = state[permutation]
        else:
            local = (
                (PAULI["X"] + PAULI["Z"]) / np.sqrt(2)
                if gate.name == "H"
                else np.array(
                    [
                        [np.cos(gate.angle / 2), -np.sin(gate.angle / 2)],
                        [np.sin(gate.angle / 2), np.cos(gate.angle / 2)],
                    ]
                )
            )
            if gate.name == "RZ":
                local = np.diag([np.exp(-0.5j * gate.angle), np.exp(0.5j * gate.angle)])
            full = np.ones((1, 1), dtype=complex)
            for wire in range(n):
                full = np.kron(full, local if wire == gate.wire else PAULI["I"])
            state = full @ state
    return state


def depth(circuit: list[Gate], n: int) -> int:
    last = [0] * n
    for g in circuit:
        wires = [g.wire, g.target] if g.name == "CNOT" else [g.wire]
        layer = max(last[w] for w in wires) + 1
        for w in wires:
            last[w] = layer
    return max(last, default=0)


def search(
    target: np.ndarray,
    n: int,
    seed: int = 0,
    budget: int = 200,
    max_gates: int = 8,
    penalty: float = 0.001,
) -> dict:
    if not 2 <= n <= 8 or budget < 2 or max_gates < 1 or penalty < 0:
        raise ValueError("Invalid search budget/system")
    target = normalize(target)
    if len(target) != 2**n:
        raise ValueError("Target size mismatch")
    rng = np.random.default_rng(seed)

    def random_gate():
        name = str(rng.choice(["H", "RY", "CNOT"]))
        a, b = rng.choice(n, 2, replace=False)
        return Gate(
            name, int(a), int(b) if name == "CNOT" else -1, float(rng.uniform(-np.pi, np.pi))
        )

    def random_circuit():
        return [random_gate() for _ in range(int(rng.integers(1, max_gates + 1)))]

    def score(c):
        return fidelity(target, execute(c, n)) - penalty * (len(c) + depth(c, n))

    results: dict = {}
    for method in ("random", "evolutionary"):
        # Same initialization stream and exactly budget fitness evaluations per method.
        rng = np.random.default_rng(seed)
        population: list[tuple[float, list[Gate]]] = []
        best = []
        best_score = -np.inf
        history = []
        for evaluation in range(budget):
            if method == "random" or evaluation < min(10, budget):
                candidate = random_circuit()
            else:
                parent = population[int(rng.integers(len(population)))][1]
                candidate = parent.copy()
                operation = int(rng.integers(3))
                if operation == 0 and len(candidate) < max_gates:
                    candidate.insert(int(rng.integers(len(candidate) + 1)), random_gate())
                elif operation == 1 and len(candidate) > 1:
                    candidate.pop(int(rng.integers(len(candidate))))
                else:
                    candidate[int(rng.integers(len(candidate)))] = random_gate()
            value = score(candidate)
            population.append((value, candidate))
            population = sorted(population, key=lambda v: v[0], reverse=True)[:10]
            if value > best_score:
                best_score, best = value, candidate
            history.append(float(best_score))
        results[method] = {
            "fidelity": fidelity(target, execute(best, n)),
            "score": float(best_score),
            "gate_count": len(best),
            "depth": depth(best, n),
            "evaluations": budget,
            "circuit": [g.__dict__ for g in best],
            "history": history,
        }
    human = [Gate("H", 0), Gate("CNOT", 0, 1)]
    results["human_bell_baseline"] = {
        "fidelity": fidelity(target, execute(human, n)),
        "gate_count": 2,
        "depth": 2,
        "evaluations": 1,
    }
    results["objective"] = "fidelity - penalty*(gate count + scheduled depth)"
    results["penalty"] = penalty
    results["discovery_advantage"] = "NOT TESTED: no pre-registered multi-seed advantage criterion"
    return results
