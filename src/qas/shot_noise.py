"""Gate-level density simulation and independent Pauli measurement with shot ZNE.

Local folding uses G (G† G)^k with an independent channel after every gate.
Readout flips affect measured Pauli eigenvalues, not the simulated density.
"""

import time
from dataclasses import dataclass

import numpy as np

from qas.exact import operator


@dataclass(frozen=True)
class Operation:
    name: str
    wires: tuple
    angle: float = 0.0


def folded(circuit, scale=1):
    if type(scale) is not int or scale < 1 or scale % 2 == 0:
        raise ValueError("Local folding needs positive odd integer scales")
    result = []
    for gate in circuit:
        if gate.name not in ("H", "X", "RY", "RZ", "RX", "CNOT", "ZZ"):
            raise ValueError("Unsupported foldable gate")
        inverse = Operation(gate.name, gate.wires, -gate.angle)
        result.append(gate)
        for _ in range((scale - 1) // 2):
            result.extend([inverse, gate])
    return result


def density(circuit, n, noise=None, scale=1):
    import pennylane as qml

    noise = dict(noise or {})
    allowed = {
        "depolarizing",
        "bit_flip",
        "phase_flip",
        "amplitude_damping",
        "phase_damping",
        "two_qubit_multiplier",
        "readout",
    }
    if set(noise) - allowed or not 1 <= n <= 8:
        raise ValueError("Invalid circuit noise configuration")
    multiplier = noise.get("two_qubit_multiplier", 1)
    if not np.isfinite(multiplier) or multiplier < 0:
        raise ValueError("Invalid gate noise multiplier")
    for key, value in noise.items():
        if key != "two_qubit_multiplier" and (not np.isfinite(value) or not 0 <= value <= 1):
            raise ValueError("Noise probability outside [0,1]")
        if key not in ("readout", "two_qubit_multiplier") and value * multiplier > 1:
            raise ValueError("Two-qubit noise exceeds probability one")
    channels = {
        "depolarizing": qml.DepolarizingChannel,
        "bit_flip": qml.BitFlip,
        "phase_flip": qml.PhaseFlip,
        "amplitude_damping": qml.AmplitudeDamping,
        "phase_damping": qml.PhaseDamping,
    }
    operations = folded(circuit, scale)

    @qml.qnode(qml.device("default.mixed", wires=n))
    def simulate():
        for gate in operations:
            if any(w < 0 or w >= n for w in gate.wires) or len(set(gate.wires)) != len(gate.wires):
                raise ValueError("Invalid gate wires")
            if gate.name in ("H", "X", "CNOT"):
                {"H": qml.Hadamard, "X": qml.PauliX, "CNOT": qml.CNOT}[gate.name](wires=gate.wires)
            else:
                {"RY": qml.RY, "RZ": qml.RZ, "RX": qml.RX, "ZZ": qml.IsingZZ}[gate.name](
                    gate.angle, wires=gate.wires
                )
            for wire in gate.wires:
                for kind, channel in channels.items():
                    probability = noise.get(kind, 0) * (multiplier if len(gate.wires) == 2 else 1)
                    if probability:
                        channel(probability, wires=wire)
        return qml.state()

    return np.asarray(simulate())


def tfim_terms(n):
    return [(-1.0, {i: "Z", i + 1: "Z"}) for i in range(n - 1)] + [
        (-1.0, {i: "X"}) for i in range(n)
    ]


def measure(rho, terms, shots, seed=0, readout=0.0):
    if type(shots) is not int or shots < 2 or not 0 <= readout <= 1:
        raise ValueError("At least two shots per Pauli term are required")
    n = int(round(np.log2(len(rho))))
    if (
        rho.shape != (2**n, 2**n)
        or not np.isfinite(rho).all()
        or not np.allclose(rho, rho.conj().T)
        or not np.isclose(np.trace(rho), 1)
    ):
        raise ValueError("Invalid density matrix")
    rng = np.random.default_rng(seed)
    estimate, variance, analytic, exact_variance = 0.0, 0.0, 0.0, 0.0
    for coefficient, sites in terms:
        mean = float(np.trace(rho @ operator(n, sites)).real) * (1 - 2 * readout) ** len(sites)
        mean = float(np.clip(mean, -1, 1))
        if not sites:
            measured, var = 1.0, 0.0
        else:
            measured = 2 * rng.binomial(shots, (1 + mean) / 2) / shots - 1
            var = (1 - measured**2) / (shots - 1)
        estimate += coefficient * measured
        analytic += coefficient * mean
        variance += coefficient**2 * var
        exact_variance += coefficient**2 * (1 - mean**2) / shots
    return dict(
        estimate=estimate,
        variance=variance,
        analytic=analytic,
        theoretical_variance=exact_variance,
        total_shots=shots * sum(bool(s) for _, s in terms),
    )


def extrapolation_weights(scales, method="linear"):
    if method not in ("linear", "richardson") or len(scales) < 2 or len(set(scales)) != len(scales):
        raise ValueError("Need distinct scales and linear/richardson method")
    order = 1 if method == "linear" else len(scales) - 1
    return np.linalg.pinv(np.vander(np.asarray(scales, dtype=float), order + 1, increasing=True))[0]


def zne(
    circuit,
    n,
    terms,
    noise,
    shots=1000,
    seed=0,
    scales=(1, 3, 5),
    method="linear",
    allocation="equal",
):
    start = time.perf_counter()
    if allocation not in ("equal", "weighted") or scales[0] != 1:
        raise ValueError("Allocation must be equal/weighted and first scale must be 1")
    weights = extrapolation_weights(scales, method)
    allocations = [shots] * len(scales)
    if allocation == "weighted":
        allocations = np.maximum(
            2, np.floor(shots * len(scales) * abs(weights) / sum(abs(weights))).astype(int)
        ).tolist()
    values = []
    for index, (scale, count) in enumerate(zip(scales, allocations, strict=True)):
        rho = density(circuit, n, noise, scale)
        values.append(measure(rho, terms, count, seed + index * 104729, noise.get("readout", 0)))
    ideal_rho = density(circuit, n)
    ideal = sum(c * float(np.trace(ideal_rho @ operator(n, s)).real) for c, s in terms)
    raw = values[0]["estimate"]
    mitigated = float(weights @ np.array([v["estimate"] for v in values]))
    # Equal total-shot comparator distinguishes mitigation from simply more samples.
    budget_shots = sum(allocations)
    equal_budget = measure(
        density(circuit, n, noise), terms, budget_shots, seed + 999983, noise.get("readout", 0)
    )
    return dict(
        ideal=ideal,
        raw=raw,
        mitigated=mitigated,
        raw_error=abs(raw - ideal),
        mitigated_error=abs(mitigated - ideal),
        improvement=abs(raw - ideal) - abs(mitigated - ideal),
        helped=bool(abs(mitigated - ideal) < abs(raw - ideal)),
        equal_budget_raw=equal_budget["estimate"],
        equal_budget_raw_error=abs(equal_budget["estimate"] - ideal),
        raw_variance=values[0]["variance"],
        mitigated_variance=float(weights**2 @ np.array([v["variance"] for v in values])),
        scales=list(scales),
        weights=weights.tolist(),
        allocations=allocations,
        scaled_measurements=values,
        shots=shots,
        total_shots=sum(v["total_shots"] for v in values),
        comparison_shots=equal_budget["total_shots"],
        gate_execution_multiplier=sum(scales),
        runtime_seconds=time.perf_counter() - start,
        extrapolation=method,
        allocation=allocation,
        backend="pennylane.default.mixed + independent Pauli binomial measurement",
        noise_model="circuit-level local Markov channels; ideal basis measurement + readout flips",
    )
