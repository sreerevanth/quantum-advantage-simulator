"""Real-positive RBM with exact enumeration, intended for tiny stoquastic systems."""

import numpy as np


def train(
    matrix: np.ndarray,
    n: int,
    seed: int = 0,
    steps: int = 300,
    lr: float = 0.03,
    hidden: int = 0,
    tolerance: float = 1e-10,
) -> dict:
    try:
        import torch
    except ImportError as exc:
        raise RuntimeError("Install QAS with [ml] for RBM training") from exc
    generator = torch.Generator().manual_seed(seed)
    spins = torch.tensor(
        1 - 2 * ((np.arange(2**n)[:, None] >> np.arange(n - 1, -1, -1)) & 1), dtype=torch.float64
    )
    hidden = hidden or 2 * n
    a = torch.nn.Parameter(torch.randn(n, generator=generator, dtype=torch.float64) * 0.01)
    b = torch.nn.Parameter(torch.randn(hidden, generator=generator, dtype=torch.float64) * 0.01)
    w = torch.nn.Parameter(torch.randn(n, hidden, generator=generator, dtype=torch.float64) * 0.01)
    ham = torch.tensor(matrix.real, dtype=torch.float64)
    if np.max(abs(matrix.imag)) > 1e-12:
        raise ValueError("Real RBM currently requires a real Hamiltonian")
    optimizer = torch.optim.Adam([a, b, w], lr=lr)

    def state():
        x = spins @ w + b
        log_amp = spins @ a + (torch.nn.functional.softplus(2 * x) - x).sum(dim=1)
        amplitude = torch.exp(log_amp - log_amp.max())
        return amplitude / torch.linalg.vector_norm(amplitude)

    history = []
    for _ in range(steps):
        optimizer.zero_grad()
        psi = state()
        energy = psi @ ham @ psi
        history.append(float(energy.detach()))
        energy.backward()
        optimizer.step()
        if len(history) > 20 and max(history[-10:]) - min(history[-10:]) < tolerance:
            break
    return {
        "state": state().detach().numpy(),
        "history": history,
        "parameters": {"a": a.detach().numpy(), "b": b.detach().numpy(), "w": w.detach().numpy()},
        "iterations": len(history),
    }


def sample(state: np.ndarray, shots: int, seed: int = 0) -> np.ndarray:
    from qas.exact import normalize

    return np.random.default_rng(seed).choice(len(state), shots, p=abs(normalize(state)) ** 2)
