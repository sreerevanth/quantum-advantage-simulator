import json

import numpy as np
import pytest
import torch

from qas import autoregressive, exact, variational
from qas.integrity import atomic_json, seal, verify
from qas.shot_noise import (
    Operation,
    density,
    folded,
    measure,
    zne,
)


def test_autoregressive_normalization_sampling_and_causality():
    model = autoregressive.Autoregressive(3, hidden=8, seed=7)
    state = model.state().detach().numpy()
    assert np.linalg.norm(state) == pytest.approx(1, abs=1e-12)
    assert np.max(abs(state.imag)) > 0.01
    bits = model.sample(30000, seed=3)
    counts = np.bincount(bits @ np.array([4, 2, 1]), minlength=8) / len(bits)
    assert np.max(abs(counts - abs(state) ** 2)) < 0.012
    assert np.array_equal(model.sample(20, 4), model.sample(20, 4))
    a = torch.zeros((1, 3), dtype=torch.float64)
    b = a.clone()
    b[0, 2] = 1
    assert torch.equal(model.conditional(a, 1), model.conditional(b, 1))


def test_complex_nqs_gradient_and_resume(tmp_path):
    h = exact.hamiltonian(2) + 0.4 * exact.operator(2, {0: "Y"})
    path = tmp_path / "checkpoint.pt"
    autoregressive.train(h, 2, steps=5, checkpoint=path, tolerance=0)
    resumed = autoregressive.train(h, 2, steps=10, checkpoint=path, resume=True, tolerance=0)
    uninterrupted = autoregressive.train(h, 2, steps=10, tolerance=0)
    assert np.allclose(resumed["state"], uninterrupted["state"], atol=1e-13)
    assert resumed["gradient_norms"] == uninterrupted["gradient_norms"]
    with pytest.raises(ValueError, match="mismatch"):
        autoregressive.train(h * 2, 2, steps=11, checkpoint=path, resume=True, tolerance=0)
    model = autoregressive.Autoregressive(2, hidden=4)
    psi = model.state()
    energy = torch.vdot(psi, torch.tensor(h) @ psi).real
    energy.backward()
    parameter = list(model.parameters())[-1]
    analytic = parameter.grad[1].item()
    epsilon = 1e-6
    values = []
    with torch.no_grad():
        original = parameter[1].item()
        for change in (epsilon, -epsilon):
            parameter[1] = original + change
            p = model.state()
            values.append(torch.vdot(p, torch.tensor(h) @ p).real.item())
        parameter[1] = original
    assert analytic == pytest.approx((values[0] - values[1]) / (2 * epsilon), abs=1e-8)


def test_complex_nqs_converges():
    h = exact.hamiltonian(2) + 0.4 * exact.operator(2, {0: "Y"})
    values, vectors = exact.solve(h)
    result = autoregressive.train(h, 2, steps=220)
    assert abs(exact.expectation(result["state"], h) - values[0]) < 1e-4
    assert abs(np.vdot(vectors[:, 0], result["state"])) ** 2 > 0.999


def test_device_failure(monkeypatch):
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    assert str(autoregressive.device_for("auto")) == "cpu"
    with pytest.raises(RuntimeError, match="unavailable"):
        autoregressive.device_for("cuda")
    with pytest.raises(ValueError):
        autoregressive.device_for("other")


@pytest.mark.parametrize("scale", [1, 3, 5])
def test_folding_preserves_unitary(scale):
    circuit = [
        Operation("H", (0,)),
        Operation("RY", (1,), 0.4),
        Operation("CNOT", (0, 1)),
        Operation("RZ", (0,), 0.3),
    ]
    assert len(folded(circuit, scale)) == scale * len(circuit)
    assert np.allclose(density(circuit, 2, scale=scale), density(circuit, 2), atol=1e-12)


@pytest.mark.parametrize(
    "kind", ["depolarizing", "bit_flip", "phase_flip", "amplitude_damping", "phase_damping"]
)
def test_circuit_noise_physical(kind):
    rho = density(
        [Operation("H", (0,)), Operation("CNOT", (0, 1))], 2, {kind: 0.2, "two_qubit_multiplier": 2}
    )
    assert np.trace(rho) == pytest.approx(1)
    assert np.linalg.eigvalsh(rho).min() > -1e-12
    assert np.trace(rho @ rho).real < 1


def test_amplitude_damping_independent_aer():
    pytest.importorskip("qiskit_aer")
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, amplitude_damping_error

    circuit = QuantumCircuit(1)
    circuit.x(0)
    circuit.save_density_matrix()
    noise = NoiseModel()
    noise.add_all_qubit_quantum_error(amplitude_damping_error(0.23), ["x"])
    result = AerSimulator(method="density_matrix", noise_model=noise).run(circuit).result()
    expected = np.asarray(result.data(0)["density_matrix"])
    actual = density([Operation("X", (0,))], 1, {"amplitude_damping": 0.23})
    assert np.allclose(actual, expected, atol=1e-12)
    assert actual[0, 0].real == pytest.approx(0.23)


def test_finite_shot_variance_and_readout():
    rho = density([Operation("RY", (0,), 0.9)], 1)
    terms = [(1.0, {0: "Z"})]
    estimates = [measure(rho, terms, 100, seed)["estimate"] for seed in range(1000)]
    expected = measure(rho, terms, 100)["theoretical_variance"]
    assert np.var(estimates, ddof=1) == pytest.approx(expected, rel=0.15)
    assert np.mean(estimates) == pytest.approx(np.cos(0.9), abs=0.01)
    assert measure(rho, terms, 100, readout=0.5)["analytic"] == pytest.approx(0)


@pytest.mark.parametrize("method", ["linear", "richardson"])
def test_zne_shot_cost_and_variance(method):
    result = zne(
        [Operation("RY", (0,), 0.7)],
        1,
        [(1.0, {0: "Z"})],
        {"depolarizing": 0.02},
        shots=1000,
        method=method,
    )
    assert result["total_shots"] == 3000 == result["comparison_shots"]
    weights = np.array(result["weights"])
    assert sum(weights) == pytest.approx(1)
    assert weights @ np.array(result["scales"]) == pytest.approx(0, abs=1e-12)
    assert result["mitigated_variance"] >= 0
    assert result["mitigated"] == pytest.approx(
        weights @ np.array([x["estimate"] for x in result["scaled_measurements"]])
    )
    if method == "richardson":
        assert weights @ np.array(result["scales"]) ** 2 == pytest.approx(0, abs=1e-12)


def test_vqe_problem_ansatz_and_qaoa_options():
    h = exact.hamiltonian(2)
    result = variational.vqe(h, 2, depth=3, ansatz="tfim", initialization="uniform", iterations=60)
    assert abs(exact.expectation(result["state"], h) - exact.solve(h)[0][0]) < 1e-6
    assert len(result["gradient_norms"]) >= 1
    assert result["parameter_count"] == 9
    q = variational.qaoa(3, [[0, 1], [1, 2]], iterations=50, optimizer="COBYLA", shots=1000)
    assert 0 <= q["approximation_ratio"] <= 1 + 1e-10
    assert q["finite_shot_evaluation"]["variance"] >= 0


def test_h2_sector_reference():
    from qas.chemistry import h2

    result = h2()
    assert result["exact_energy"] == pytest.approx(-1.13727594, abs=1e-7)
    assert result["absolute_energy_error"] < 1e-8
    assert result["fidelity"] > 0.999999
    assert result["energy"] < result["hartree_fock_energy"]


def test_search_resume_pareto(tmp_path):
    from qas.discovery import Gate, execute
    from qas.search_lab import search

    target = execute([Gate("H", 0), Gate("CNOT", 0, 1)], 2)
    path = tmp_path / "search.json"
    search(target, 2, budget=20, checkpoint=path)
    continued = search(target, 2, budget=40, checkpoint=path, resume=True)
    direct = search(target, 2, budget=40)
    assert continued == direct
    for method in ("random", "evolutionary"):
        assert direct[method]["evaluations"] == 40
        assert direct[method]["pareto"]


def test_manifest_corruption_and_extra_files(tmp_path):
    atomic_json(tmp_path / "metrics.json", {"rows": []})
    seal(tmp_path)
    assert verify(tmp_path)["verified_files"] == 1
    with pytest.raises(ValueError):
        seal(tmp_path)
    (tmp_path / "extra").write_text("x")
    with pytest.raises(ValueError, match="Unmanifested"):
        verify(tmp_path)
    (tmp_path / "extra").unlink()
    (tmp_path / "metrics.json").write_text("{}")
    with pytest.raises(ValueError, match="Corrupt"):
        verify(tmp_path)


def test_suite_resume_completed_tasks(tmp_path, monkeypatch):
    from qas import research

    jobs = [{"kind": "test", "qubits": 2, "seed": 0}, {"kind": "test", "qubits": 2, "seed": 1}]
    monkeypatch.setattr(research, "plan", lambda *a: jobs)
    calls = []

    def evaluate(job, checkpoints):
        calls.append(job["seed"])
        if len(calls) == 2:
            raise RuntimeError("interrupted")
        return {"energy": -1.0}

    monkeypatch.setattr(research, "evaluate", evaluate)
    with pytest.raises(RuntimeError, match="interrupted"):
        research.run(output=tmp_path)
    directory = next((tmp_path / "research-quick").iterdir())
    research.run(resume=directory)
    assert calls == [0, 1, 1]
    assert verify(directory)["verified_files"] > 5
    research.run(resume=directory)
    assert calls == [0, 1, 1]
    assert json.loads((directory / "metrics.json").read_text())["complete"]


def test_statistical_summary():
    from qas.statistical import describe

    result = describe([1, 2, 3, 4, 5])
    assert result["median"] == 3 and result["mean"] == 3
    assert result["std"] == pytest.approx(np.sqrt(2.5))
    assert result["mean_ci95"][0] < 3 < result["mean_ci95"][1]
    assert describe([1])["std"] is None
    assert describe([1, 2])["mean_ci95"] is None
