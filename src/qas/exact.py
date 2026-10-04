"""Dense reference physics; wire zero is the most significant bit."""

import numpy as np
from scipy.linalg import eigh

PAULI = {
    "I": np.eye(2, dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.diag([1, -1]).astype(complex),
}


def operator(n: int, sites: dict[int, str]) -> np.ndarray:
    if not 1 <= n <= 12 or any(i < 0 or i >= n for i in sites):
        raise ValueError("Dense reference supports 1–12 qubits and valid wire indices")
    result = np.ones((1, 1), dtype=complex)
    for i in range(n):
        result = np.kron(result, PAULI[sites.get(i, "I")])
    return result


def bonds(n: int, boundary: str) -> list[tuple[int, int]]:
    if boundary not in ("open", "periodic"):
        raise ValueError("boundary must be open or periodic")
    pairs = [(i, i + 1) for i in range(n - 1)]
    # Undirected bonds counted once, including the two-site ring.
    if boundary == "periodic" and n > 2:
        pairs.append((n - 1, 0))
    return pairs


def hamiltonian(
    n: int, j: float = 1, h: float = 1, boundary: str = "open", model: str = "tfim"
) -> np.ndarray:
    if type(n) is not int or not 1 <= n <= 12:
        raise ValueError("Dense reference supports integer 1–12 qubits")
    result = np.zeros((2**n, 2**n), dtype=complex)
    if model not in ("tfim", "heisenberg") or not np.isfinite([j, h]).all():
        raise ValueError("Unknown model or non-finite couplings")
    axes = "Z" if model == "tfim" else "XYZ"
    for a, b in bonds(n, boundary):
        for axis in axes:
            result += (-j if model == "tfim" else j) * operator(n, {a: axis, b: axis})
    for i in range(n):
        result -= h * operator(n, {i: "X" if model == "tfim" else "Z"})
    return result


def normalize(state: np.ndarray) -> np.ndarray:
    state = np.asarray(state, dtype=complex)
    norm = np.linalg.norm(state)
    if state.ndim != 1 or not np.isfinite(state).all() or norm <= 0:
        raise ValueError("State must be a finite nonzero vector")
    return state / norm


def expectation(state: np.ndarray, observable: np.ndarray) -> float:
    state = normalize(state)
    value = np.vdot(state, observable @ state)
    if abs(value.imag) > 1e-9:
        raise ValueError("Expected a Hermitian observable")
    return float(value.real)


def solve(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or not np.isfinite(matrix).all():
        raise ValueError("Hamiltonian must be a finite square matrix")
    if not np.allclose(matrix, matrix.conj().T, atol=1e-12, rtol=0):
        raise ValueError("Hamiltonian must be Hermitian")
    return eigh(matrix)


def magnetization(n: int, axis: str = "Z") -> np.ndarray:
    return sum((operator(n, {i: axis}) for i in range(n)), np.zeros((2**n, 2**n))) / n


def correlation(state: np.ndarray, n: int, i: int, k: int, axis: str = "Z") -> float:
    operator(n, {i: axis, k: axis})
    return 1.0 if i == k else expectation(state, operator(n, {i: axis, k: axis}))
