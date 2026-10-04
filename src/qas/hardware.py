"""Credential-free simulator plus explicitly opted-in IBM job adapter."""

from dataclasses import dataclass

import numpy as np

from qas.discovery import Gate, execute


class HardwareUnavailable(RuntimeError):
    pass


@dataclass
class Simulator:
    seed: int = 0

    def submit(self, circuit: list[Gate], n: int, shots: int = 1024) -> dict:
        if shots < 1:
            raise ValueError("shots must be positive")
        probabilities = abs(execute(circuit, n)) ** 2
        counts = np.random.default_rng(self.seed).multinomial(shots, probabilities)
        return {
            "status": "DONE",
            "counts": {format(i, f"0{n}b"): int(c) for i, c in enumerate(counts) if c},
            "backend": "qas-statevector",
            "seed": self.seed,
            "shots": shots,
        }


class IBMBackend:
    def __init__(self, backend: str, *, enabled: bool = False):
        if not enabled:
            raise HardwareUnavailable(
                "BLOCKED — explicit IBM hardware opt-in and saved credentials required"
            )
        try:
            from qiskit_ibm_runtime import QiskitRuntimeService

            self.service = QiskitRuntimeService()
            self.backend = self.service.backend(backend)
        except Exception as exc:
            raise HardwareUnavailable(
                "BLOCKED — IBM dependency, credentials or backend access unavailable"
            ) from exc

    def submit(self, circuit, shots: int = 1024):
        from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
        from qiskit_ibm_runtime import SamplerV2

        isa = generate_preset_pass_manager(backend=self.backend, optimization_level=1).run(circuit)
        return SamplerV2(mode=self.backend).run([isa], shots=shots)

    def status(self, job_id: str):
        return self.service.job(job_id).status()

    def result(self, job_id: str):
        return self.service.job(job_id).result()
