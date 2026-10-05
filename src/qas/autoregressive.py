"""Complex autoregressive wavefunctions with exact-energy training and direct sampling.

Each conditional network sees only preceding bits. Product conditionals normalize
probability exactly; a second output represents a configuration-dependent phase.
Training enumerates 2**n amplitudes and is explicitly a small-system method.
"""

import hashlib
import os
from pathlib import Path

import numpy as np
import torch
from torch import nn


def device_for(name="cpu"):
    if name not in ("cpu", "cuda", "auto"):
        raise ValueError("device must be cpu, cuda or auto")
    if name == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("NOT EXECUTED — CUDA hardware/runtime unavailable")
    return torch.device("cuda" if name != "cpu" and torch.cuda.is_available() else "cpu")


class Autoregressive(nn.Module):
    def __init__(self, n, hidden=16, seed=0, device="cpu"):
        super().__init__()
        if not 1 <= n <= 12 or not 1 <= hidden <= 256:
            raise ValueError("Autoregressive model supports 1–12 qubits, hidden 1–256")
        self.n, self.hidden = n, hidden
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(seed)
            self.nets = nn.ModuleList(
                [
                    nn.Sequential(nn.Linear(max(1, i), hidden), nn.Tanh(), nn.Linear(hidden, 2))
                    for i in range(n)
                ]
            )
        self.to(device=device_for(device), dtype=torch.float64)

    @property
    def device(self):
        return next(self.parameters()).device

    def conditional(self, bits, i):
        prefix = (
            bits[:, :i]
            if i
            else torch.zeros((len(bits), 1), device=self.device, dtype=torch.float64)
        )
        return self.nets[i](prefix)

    def amplitude(self, bits):
        bits = torch.as_tensor(bits, dtype=torch.float64, device=self.device)
        if bits.ndim != 2 or bits.shape[1] != self.n or not torch.all((bits == 0) | (bits == 1)):
            raise ValueError("Expected a batch of binary configurations")
        logp = torch.zeros(len(bits), dtype=torch.float64, device=self.device)
        phase = torch.zeros_like(logp)
        for i in range(self.n):
            output = self.conditional(bits, i)
            logp = logp - torch.nn.functional.softplus((1 - 2 * bits[:, i]) * output[:, 0])
            phase = phase + bits[:, i] * output[:, 1]
        return torch.exp(0.5 * logp + 1j * phase)

    def state(self):
        indices = torch.arange(2**self.n, device=self.device)
        bits = (indices[:, None] >> torch.arange(self.n - 1, -1, -1, device=self.device)) & 1
        return self.amplitude(bits)

    @torch.no_grad()
    def sample(self, shots, seed=0):
        if type(shots) is not int or shots < 1:
            raise ValueError("shots must be positive")
        generator = torch.Generator(device=self.device).manual_seed(seed)
        bits = torch.zeros((shots, self.n), dtype=torch.float64, device=self.device)
        for i in range(self.n):
            prob = torch.sigmoid(self.conditional(bits, i)[:, 0])
            bits[:, i] = (
                torch.rand(shots, generator=generator, device=self.device) < prob
            ).double()
        return bits.cpu().numpy().astype(int)


def train(
    matrix,
    n,
    seed=0,
    steps=300,
    lr=0.025,
    hidden=16,
    optimizer="Adam",
    device="cpu",
    checkpoint=None,
    resume=False,
    tolerance=1e-10,
    patience=30,
):
    if steps < 1 or lr <= 0 or patience < 2 or optimizer not in ("Adam", "SGD"):
        raise ValueError("Invalid training configuration")
    matrix = np.asarray(matrix, dtype=np.complex128)
    if (
        matrix.shape != (2**n, 2**n)
        or not np.isfinite(matrix).all()
        or not np.allclose(matrix, matrix.conj().T)
    ):
        raise ValueError("Expected finite Hermitian Hamiltonian")
    model = Autoregressive(n, hidden, seed, device)
    opt = getattr(torch.optim, optimizer)(model.parameters(), lr=lr)
    signature = dict(
        n=n,
        hidden=hidden,
        seed=seed,
        lr=lr,
        optimizer=optimizer,
        hamiltonian=hashlib.sha256(matrix.tobytes()).hexdigest(),
        tolerance=tolerance,
        patience=patience,
    )
    history, gradients = [], []
    if resume:
        if checkpoint is None or not Path(checkpoint).is_file():
            raise ValueError("Resume requires an existing checkpoint")
        saved = torch.load(checkpoint, map_location=model.device, weights_only=True)
        if saved["signature"] != signature:
            raise ValueError("Checkpoint configuration/Hamiltonian mismatch")
        model.load_state_dict(saved["model"])
        opt.load_state_dict(saved["optimizer"])
        history, gradients = saved["history"], saved["gradients"]
    ham = torch.as_tensor(matrix, dtype=torch.complex128, device=model.device)

    def save():
        if checkpoint:
            path = Path(checkpoint)
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_suffix(path.suffix + ".tmp")
            torch.save(
                dict(
                    signature=signature,
                    model=model.state_dict(),
                    optimizer=opt.state_dict(),
                    history=history,
                    gradients=gradients,
                ),
                temporary,
            )
            os.replace(temporary, path)

    stopped = False
    for _ in range(len(history), steps):
        if len(history) >= patience and np.ptp(history[-patience:]) < tolerance:
            stopped = True
            break
        opt.zero_grad()
        psi = model.state()
        energy = torch.vdot(psi, ham @ psi).real
        energy.backward()
        norm = torch.sqrt(
            torch.stack(
                [torch.sum(p.grad**2) for p in model.parameters() if p.grad is not None]
            ).sum()
        )
        if not torch.isfinite(energy) or not torch.isfinite(norm):
            raise RuntimeError("Non-finite energy/gradient")
        history.append(float(energy.detach().cpu()))
        gradients.append(float(norm.detach().cpu()))
        opt.step()
        if len(history) % 25 == 0:
            save()
    save()
    return dict(
        state=model.state().detach().cpu().numpy(),
        history=history,
        gradient_norms=gradients,
        iterations=len(history),
        early_stopped=stopped,
        parameter_count=sum(p.numel() for p in model.parameters()),
        device=str(model.device),
        precision="float64/complex128",
        model=model,
    )
