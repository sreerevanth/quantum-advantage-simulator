"""PennyLane state-vector VQE and MaxCut QAOA baselines."""

import numpy as np
from scipy.optimize import minimize


def vqe(
    matrix: np.ndarray,
    n: int,
    seed: int = 0,
    depth: int = 3,
    iterations: int = 150,
    tolerance: float = 1e-9,
    ansatz: str = "ry",
    optimizer: str = "BFGS",
) -> dict:
    if not 1 <= n <= 12 or depth < 1 or iterations < 1 or matrix.shape != (2**n, 2**n):
        raise ValueError("Invalid VQE system or optimization budget")
    try:
        import pennylane as qml
    except ImportError as exc:
        raise RuntimeError("Install QAS with [quantum] for VQE") from exc
    if ansatz not in ("ry", "rot") or optimizer not in ("BFGS", "L-BFGS-B"):
        raise ValueError("ansatz: ry/rot; optimizer: BFGS/L-BFGS-B")
    width = 1 if ansatz == "ry" else 3
    shape = (depth, n, width)

    def circuit(params):
        weights = qml.math.reshape(params, shape)
        for layer in range(depth):
            for wire in range(n):
                if ansatz == "ry":
                    qml.RY(weights[layer, wire, 0], wires=wire)
                else:
                    qml.Rot(*weights[layer, wire], wires=wire)
            for wire in range(n - 1):
                qml.CNOT(wires=[wire, wire + 1])

    @qml.qnode(qml.device("default.qubit", wires=n), interface="autograd")
    def cost(params):
        circuit(params)
        return qml.expval(qml.Hermitian(matrix, wires=range(n)))

    @qml.qnode(qml.device("default.qubit", wires=n))
    def state(params):
        circuit(params)
        return qml.state()

    history = []

    def objective(params):
        value = float(cost(params))
        return value

    def gradient(params):
        return np.asarray(qml.grad(cost)(qml.numpy.array(params, requires_grad=True)), dtype=float)

    initial = np.random.default_rng(seed).normal(0, 0.3, np.prod(shape))
    history.append(objective(initial))
    result = minimize(
        objective,
        initial,
        jac=gradient,
        method=optimizer,
        callback=lambda p: history.append(objective(p)),
        options={"maxiter": iterations, "gtol": tolerance},
    )
    return {
        "state": np.asarray(state(result.x)),
        "history": history,
        "parameters": {"weights": result.x},
        "iterations": int(result.nit),
        "optimizer_success": bool(result.success),
        "optimizer_message": str(result.message),
        "gate_count": depth * (n + n - 1),
        "circuit_depth_upper_bound": depth * n,
    }


def qaoa(
    n: int, edges: list[list[int]], seed: int = 0, depth: int = 2, iterations: int = 100
) -> dict:
    if depth < 1 or iterations < 1:
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
        method="BFGS",
        callback=lambda p: history.append(-cost(p)),
        options={"maxiter": iterations},
    )
    return {
        "expected_cut": -float(result.fun),
        "exact_cut": int(max(cuts)),
        "approximation_ratio": -float(result.fun) / max(cuts),
        "history": history,
        "iterations": int(result.nit),
        "gate_count": n + depth * (n + len(edges)),
    }
