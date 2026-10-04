import json
import sys
from types import ModuleType, SimpleNamespace

import numpy as np
import pytest

from qas import artifacts, exact, hardware, registry
from qas.config import Config


@pytest.mark.parametrize(
    "matrix", [np.ones((2, 3)), np.array([[0, 1], [0, 0]]), np.array([[np.nan]])]
)
def test_reject_invalid_matrix(matrix):
    with pytest.raises(ValueError):
        exact.solve(matrix)


def test_expectation_rejects_nonhermitian():
    with pytest.raises(ValueError):
        exact.expectation(np.array([1, 0]), np.array([[0, 1], [0, 0]]))


def test_artifact_path_guard(tmp_path):
    with pytest.raises(ValueError):
        artifacts.create(tmp_path, {"experiment_id": "../escape"})


def test_duplicate_results_cannot_pass(tmp_path):
    config = Config(qubits=(2,), seeds=(0,))
    row = {
        "method": "nqs",
        "qubits": 2,
        "seed": 0,
        "absolute_energy_error": 0,
        "fidelity": 1,
        "runtime_seconds": 0,
    }
    artifacts.write_results(tmp_path, [row] * 3, config.dict())
    assert json.loads((tmp_path / "metrics.json").read_text())["verdict"] == "INCONCLUSIVE"


def test_registry_malformed(tmp_path):
    file = tmp_path / "registry.yaml"
    file.write_text("- id: incomplete")
    with pytest.raises(ValueError):
        registry.read(file)


def test_ibm_adapter_mock(monkeypatch):
    calls = []
    job = SimpleNamespace(status=lambda: "DONE", result=lambda: {"counts": {"00": 10}})
    backend = object()
    runtime = ModuleType("qiskit_ibm_runtime")
    runtime.QiskitRuntimeService = lambda: SimpleNamespace(
        backend=lambda name: backend, job=lambda id: job
    )
    runtime.SamplerV2 = lambda mode: SimpleNamespace(
        run=lambda pubs, shots: calls.append((pubs, shots)) or job
    )
    manager = ModuleType("qiskit.transpiler.preset_passmanagers")
    manager.generate_preset_pass_manager = lambda **kw: SimpleNamespace(run=lambda c: "transpiled")
    monkeypatch.setitem(sys.modules, "qiskit_ibm_runtime", runtime)
    monkeypatch.setitem(sys.modules, "qiskit.transpiler.preset_passmanagers", manager)
    adapter = hardware.IBMBackend("mock", enabled=True)
    assert adapter.submit("circuit", shots=10) is job
    assert calls == [(["transpiled"], 10)]
    assert adapter.status("id") == "DONE"
    assert adapter.result("id")["counts"] == {"00": 10}
