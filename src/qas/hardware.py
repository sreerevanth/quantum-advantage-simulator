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


def validation(backend, shots=1000, output="results/hardware", job_id=None):
    """Submit a small Bell experiment or collect a previously submitted job."""
    from qiskit import QuantumCircuit
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from qiskit_ibm_runtime import SamplerV2

    from qas import artifacts
    from qas.integrity import atomic_json

    if not 2 <= shots <= 10000:
        raise ValueError("Hardware validation supports 2–10000 shots")
    adapter = IBMBackend(backend, enabled=True)
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure_all()
    isa = generate_preset_pass_manager(backend=adapter.backend, optimization_level=1).run(circuit)
    job = (
        adapter.service.job(job_id)
        if job_id
        else SamplerV2(mode=adapter.backend).run([isa], shots=shots)
    )
    directory = artifacts.create(
        output, dict(experiment_id="ibm-bell", backend=backend, shots=shots, job_id=job.job_id())
    )
    status = str(job.status())
    data = dict(
        job_id=job.job_id(),
        backend=backend,
        status=status,
        shots=shots,
        transpiled_depth=isa.depth(),
        gate_counts=dict(isa.count_ops()),
        backend_qubits=adapter.backend.num_qubits,
        exact_probabilities={"00": 0.5, "11": 0.5},
        simulator=Simulator().submit([Gate("H", 0), Gate("CNOT", 0, 1)], 2, shots),
    )
    if status.upper() in ("DONE", "JOBSTATUS.DONE"):
        data["hardware_counts"] = job.result()[0].data.meas.get_counts()
    else:
        data["resume_command"] = (
            f"qas hardware --backend {backend} --shots {shots} --job-id {job.job_id()}"
        )
    atomic_json(directory / "metrics.json", data)
    return directory
