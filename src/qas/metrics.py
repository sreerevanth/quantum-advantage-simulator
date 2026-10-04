"""Central normalized-state metrics and sample statistics."""

import numpy as np

from qas.exact import expectation, magnetization, normalize


def fidelity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.clip(abs(np.vdot(normalize(a), normalize(b))) ** 2, 0, 1))


def compare(state: np.ndarray, reference: np.ndarray, matrix: np.ndarray, n: int) -> dict:
    energy = expectation(state, matrix)
    exact = expectation(reference, matrix)
    error = abs(energy - exact)
    return {
        "energy": energy,
        "exact_energy": exact,
        "absolute_energy_error": error,
        "relative_energy_error": error / abs(exact) if abs(exact) > 1e-12 else None,
        "fidelity": fidelity(reference, state),
        "magnetization_error": abs(
            expectation(state, magnetization(n)) - expectation(reference, magnetization(n))
        ),
        "transverse_magnetization_error": abs(
            expectation(state, magnetization(n, "X"))
            - expectation(reference, magnetization(n, "X"))
        ),
    }


def statistics(values: list[float]) -> dict:
    if not values or not np.isfinite(values).all():
        raise ValueError("Statistics require finite observations")
    return {
        "count": len(values),
        "mean": float(np.mean(values)),
        "std": float(np.std(values, ddof=1)) if len(values) > 1 else None,
    }
