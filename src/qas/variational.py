"""PennyLane state-vector VQE and MaxCut QAOA baselines."""

from typing import Any

import numpy as np
from scipy.optimize import minimize


def apply_ansatz(params, n: int, depth: int, ansatz: str = "ry"):
    """Shared preparation circuit for optimization and checkpoint replay."""
    import pennylane as qml

    if ansatz not in ("ry", "rot", "tfim") or n < 1 or depth < 1:
        raise ValueError("Invalid ansatz")
    if ansatz == "tfim":
        weights = qml.math.reshape(params, (depth, 2 * n - 1))
        for wire in range(n):
            qml.Hadamard(wires=wire)
        for layer in range(depth):
            for wire in range(n - 1):
                qml.IsingZZ(weights[layer, wire], wires=[wire, wire + 1])
            for wire in range(n):
                qml.RX(weights[layer, n - 1 + wire], wires=wire)
        return
    weights = qml.math.reshape(params, (depth, n, 1 if ansatz == "ry" else 3))
    for layer in range(depth):
        for wire in range(n):
            if ansatz == "ry":
                qml.RY(weights[layer, wire, 0], wires=wire)
            else:
                qml.Rot(*weights[layer, wire], wires=wire)
        for wire in range(n - 1):
            qml.CNOT(wires=[wire, wire + 1])


def prepare(params: np.ndarray, n: int, depth: int, ansatz: str = "ry") -> np.ndarray:
    import pennylane as qml

    @qml.qnode(qml.device("default.qubit", wires=n))
    def state():
        apply_ansatz(params, n, depth, ansatz)
        return qml.state()

    return np.asarray(state())


def vqe(
    matrix: np.ndarray,
    n: int,
    seed: int = 0,
    depth: int = 3,
    iterations: int = 150,
    tolerance: float = 1e-9,
    ansatz: str = "ry",
    optimizer: str = "BFGS",
    initialization: str = "normal",
    initial_parameters=None,
) -> dict:
    if not 1 <= n <= 12 or depth < 1 or iterations < 1 or matrix.shape != (2**n, 2**n):
        raise ValueError("Invalid VQE system or optimization budget")
    try:
        import pennylane as qml
    except ImportError as exc:
        raise RuntimeError("Install QAS with [quantum] for VQE") from exc
    if ansatz not in ("ry", "rot", "tfim") or optimizer not in ("BFGS", "L-BFGS-B", "CG"):
        raise ValueError("ansatz: ry/rot; optimizer: BFGS/L-BFGS-B")
    width = 1 if ansatz == "ry" else 3
    shape = (depth, 2 * n - 1) if ansatz == "tfim" else (depth, n, width)

    def circuit(params):
        apply_ansatz(params, n, depth, ansatz)

    @qml.qnode(qml.device("default.qubit", wires=n), interface="autograd")
    def cost(params):
        circuit(params)
        return qml.expval(qml.Hermitian(matrix, wires=range(n)))

    @qml.qnode(qml.device("default.qubit", wires=n))
    def state(params):
        circuit(params)
        return qml.state()

    history = []

    cache: dict[str, Any] = {}

    def objective(params):
        if "point" not in cache or not np.array_equal(params, cache["point"]):
            cache.clear()
            cache["point"] = np.array(params, copy=True)
        if "value" not in cache:
            cache["value"] = float(cost(params))
        return cache["value"]

    def gradient(params):
        objective(params)
        if "gradient" not in cache:
            cache["gradient"] = np.asarray(
                qml.grad(cost)(qml.numpy.array(params, requires_grad=True)), dtype=float
            )
        return cache["gradient"].copy()

    rng = np.random.default_rng(seed)
    if initialization not in ("normal", "uniform", "plus", "small"):
        raise ValueError("Unknown initialization")
    initial = rng.normal(0, 0.3 if initialization == "normal" else 0.02, np.prod(shape))
    if initialization == "uniform":
        initial = rng.uniform(-np.pi, np.pi, np.prod(shape))
    if initialization == "plus" and ansatz == "ry":
        initial[:n] += np.pi / 2
    if initial_parameters is not None:
        initial = np.asarray(initial_parameters, dtype=float)
        if initial.shape != (np.prod(shape),) or not np.isfinite(initial).all():
            raise ValueError("Invalid initial parameters")
    gradient_norms = [float(np.linalg.norm(gradient(initial)))]

    def callback(p):
        history.append(objective(p))
        gradient_norms.append(float(np.linalg.norm(gradient(p))))

    history.append(objective(initial))
    result = minimize(
        objective,
        initial,
        jac=gradient,
        method=optimizer,
        callback=callback,
        options={"maxiter": iterations, "gtol": tolerance},
    )
    return {
        "state": np.asarray(state(result.x)),
        "gradient_norms": gradient_norms,
        "final_gradient_norm": float(np.linalg.norm(gradient(result.x))),
        "parameter_count": len(result.x),
        "initialization": initialization,
        "function_evaluations": int(result.nfev),
        "history": history,
        "parameters": {"weights": result.x},
        "iterations": int(result.nit),
        "optimizer_success": bool(result.success),
        "optimizer_message": str(result.message),
        "gate_count": depth * (n + n - 1) + (n if ansatz == "tfim" else 0),
        "circuit_depth_upper_bound": depth * n + (1 if ansatz == "tfim" else 0),
    }


def qaoa(
    n: int,
    edges: list[list[int]],
    seed: int = 0,
    depth: int = 2,
    iterations: int = 100,
    optimizer: str = "BFGS",
    shots: int | None = None,
) -> dict:
    if depth < 1 or iterations < 1 or optimizer not in ("BFGS", "COBYLA", "Nelder-Mead"):
        raise ValueError("QAOA depth and iterations must be positive")
    import pennylane as qml

    if (
        n < 2
        or n > 12
        or any(len(e) != 2 or e[0] == e[1] or any(v < 0 or v >= n for v in e) for e in edges)
    ):
        raise ValueError("Invalid MaxCut graph")
    if len({tuple(sorted(e)) for e in edges}) != len(edges) or not edges:
        raise ValueError("Edges must be nonempty and unique")
    indices = np.arange(2**n)
    cuts = sum(((indices >> (n - 1 - a)) & 1) != ((indices >> (n - 1 - b)) & 1) for a, b in edges)

    @qml.qnode(qml.device("default.qubit", wires=n))
    def state(params):
        for i in range(n):
            qml.Hadamard(i)
        for layer in range(depth):
            for a, b in edges:
                qml.IsingZZ(-params[layer], wires=[a, b])
            for i in range(n):
                qml.RX(2 * params[depth + layer], wires=i)
        return qml.state()

    def cost(params):
        return -float(abs(state(params)) ** 2 @ cuts)

    history = []
    result = minimize(
        cost,
        np.random.default_rng(seed).uniform(0, 1, 2 * depth),
        method=optimizer,
        callback=lambda p: history.append(-cost(p)),
        options={"maxiter": iterations},
    )
    final_state = np.asarray(state(result.x))
    sampled = None
    if shots is not None:
        if shots < 2:
            raise ValueError("At least two shots required")
        outcomes = np.random.default_rng(seed + 100000).choice(
            cuts, size=shots, p=abs(final_state) ** 2
        )
        sampled = {
            "shots": shots,
            "expected_cut": float(np.mean(outcomes)),
            "variance": float(np.var(outcomes, ddof=1) / shots),
        }
    return {
        "parameters": result.x.tolist(),
        "parameter_count": len(result.x),
        "optimizer": optimizer,
        "finite_shot_evaluation": sampled,
        "expected_cut": -float(result.fun),
        "exact_cut": int(max(cuts)),
        "approximation_ratio": -float(result.fun) / max(cuts),
        "history": history,
        "iterations": int(getattr(result, "nit", len(history))),
        "function_evaluations": int(result.nfev),
        "budget_semantics": "COBYLA max function evaluations; BFGS/Nelder-Mead max iterations",
        "gate_count": n + depth * (n + len(edges)),
        "circuit_depth_upper_bound": 1 + depth * (len(edges) + 1),
        "optimizer_success": bool(result.success),
        "optimizer_message": str(result.message),
    }
