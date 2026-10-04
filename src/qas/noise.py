"""Exact density-matrix local channels and analytic noise-strength extrapolation."""

import time

import numpy as np

from qas.exact import normalize, operator


def channel(rho: np.ndarray, n: int, probability: float, kind: str = "depolarizing") -> np.ndarray:
    if not 0 <= probability <= 1 or kind not in ("depolarizing", "bit_flip", "readout"):
        raise ValueError("Invalid channel or probability")
    result = np.asarray(rho, dtype=complex).copy()
    if result.shape != (2**n, 2**n) or not np.allclose(result, result.conj().T):
        raise ValueError("Invalid density matrix")
    if not np.isclose(np.trace(result), 1) or np.linalg.eigvalsh(result).min() < -1e-10:
        raise ValueError("Density matrix must be positive and trace one")
    for wire in range(n):
        if kind in ("bit_flip", "readout"):
            x = operator(n, {wire: "X"})
            result = (1 - probability) * result + probability * x @ result @ x
        else:
            mixed = sum(operator(n, {wire: a}) @ result @ operator(n, {wire: a}) for a in "XYZ")
            result = (1 - probability) * result + probability * mixed / 3
    return result


def experiment(
    state: np.ndarray,
    matrix: np.ndarray,
    n: int,
    probability: float = 0.05,
    scales: tuple = (1.0, 2.0, 3.0),
    kind: str = "depolarizing",
) -> dict:
    if kind == "readout" and not np.allclose(matrix, np.diag(np.diag(matrix))):
        raise ValueError("Readout flips apply only to computational-basis diagonal observables")
    if (
        len(scales) < 2
        or len(set(scales)) != len(scales)
        or any(s < 1 or not np.isfinite(s) for s in scales)
    ):
        raise ValueError("Need distinct finite scales >= 1")
    if probability < 0 or probability * max(scales) > 1:
        raise ValueError("Scaled channel probability must lie in [0,1]")
    state = normalize(state)
    rho = np.outer(state, state.conj())
    ideal = float(np.trace(rho @ matrix).real)
    start = time.perf_counter()
    raw = float(np.trace(channel(rho, n, probability, kind) @ matrix).real)
    raw_runtime = time.perf_counter() - start
    start = time.perf_counter()
    values = [float(np.trace(channel(rho, n, probability * s, kind) @ matrix).real) for s in scales]
    # Richardson coefficients cancel polynomial orders 1..k-1.
    weights = np.linalg.solve(np.vander(scales, increasing=True).T, np.eye(len(scales))[0])
    mitigated = float(weights @ values)
    return {
        "ideal": ideal,
        "raw": raw,
        "mitigated": mitigated,
        "raw_error": abs(raw - ideal),
        "mitigated_error": abs(mitigated - ideal),
        "improvement": abs(raw - ideal) - abs(mitigated - ideal),
        "scales": list(scales),
        "scaled_values": values,
        "weights": weights.tolist(),
        "probability": probability,
        "kind": kind,
        "raw_runtime_seconds": raw_runtime,
        "mitigation_runtime_seconds": time.perf_counter() - start,
        "evaluations": len(scales),
        "equal_shot_variance_multiplier": float(weights @ weights),
        "shots": None,
        "sampling_overhead": "NOT EXECUTED: analytic expectations",
        "method": "polynomial noise-strength Richardson extrapolation; post-state channels, no gate folding",
        "verdict": "SUPPORTED" if abs(mitigated - ideal) < abs(raw - ideal) else "NOT_SUPPORTED",
    }
