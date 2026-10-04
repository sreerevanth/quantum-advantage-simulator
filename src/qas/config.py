"""Strict, bounded local benchmark configuration."""

from dataclasses import asdict, dataclass, fields
from pathlib import Path

import numpy as np
import yaml


@dataclass
class Config:
    experiment_id: str = "tfim-phase1"
    qubits: tuple = (2, 3, 4, 5, 6, 7, 8)
    seeds: tuple = (0, 1, 2, 3, 4)
    j: float = 1.0
    h: float = 1.0
    boundary: str = "open"
    nqs_steps: int = 300
    nqs_lr: float = 0.03
    nqs_hidden: int = 0
    vqe_depth: int = 3
    vqe_iterations: int = 150
    vqe_ansatz: str = "ry"
    vqe_optimizer: str = "BFGS"
    tolerance: float = 1e-9
    energy_error_max: float = 0.05
    fidelity_min: float = 0.95

    def __post_init__(self):
        import re

        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", self.experiment_id):
            raise ValueError("Unsafe experiment identifier")
        for name, values, low, high in [
            ("qubits", self.qubits, 2, 8),
            ("seeds", self.seeds, 0, 2**32 - 1),
        ]:
            if (
                not isinstance(values, (list, tuple))
                or not values
                or len(set(values)) != len(values)
            ):
                raise ValueError(f"{name} must be a nonempty unique list")
            if any(type(v) is not int or not low <= v <= high for v in values):
                raise ValueError(f"Invalid {name}")
        for name in ("nqs_steps", "vqe_iterations", "vqe_depth"):
            value = getattr(self, name)
            if type(value) is not int or not 1 <= value <= 10000:
                raise ValueError(f"Invalid {name}")
        if type(self.nqs_hidden) is not int or not 0 <= self.nqs_hidden <= 1024:
            raise ValueError("Invalid hidden count")
        if self.boundary not in ("open", "periodic"):
            raise ValueError("Invalid boundary")
        if self.vqe_ansatz not in ("ry", "rot") or self.vqe_optimizer not in ("BFGS", "L-BFGS-B"):
            raise ValueError("Invalid VQE configuration")
        for name in ("j", "h", "nqs_lr", "tolerance", "energy_error_max", "fidelity_min"):
            if not isinstance(getattr(self, name), (int, float)) or not np.isfinite(
                getattr(self, name)
            ):
                raise ValueError(f"Invalid {name}")
        if (
            self.nqs_lr <= 0
            or self.tolerance < 0
            or self.energy_error_max < 0
            or not 0 <= self.fidelity_min <= 1
        ):
            raise ValueError("Invalid learning rate or criteria")

    def dict(self) -> dict:
        return asdict(self)


def load(path: str | Path) -> Config:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) - {f.name for f in fields(Config)}:
        raise ValueError("Configuration must be a mapping with recognized keys")
    return Config(**data)
