import numpy as np
import pytest

from qas import exact, metrics, noise, nqs, variational


@pytest.mark.parametrize("n", [2, 3, 4])
@pytest.mark.parametrize("boundary", ["open", "periodic"])
@pytest.mark.parametrize("model", ["tfim", "heisenberg"])
def test_reference(n, boundary, model):
    import qutip as qt

    ham = exact.hamiltonian(n, 0.7, 0.4, boundary, model)

    def op(sites):
        axes = {"X": qt.sigmax(), "Y": qt.sigmay(), "Z": qt.sigmaz()}
        return qt.tensor([axes[sites[i]] if i in sites else qt.qeye(2) for i in range(n)])

    reference = 0 * op({})
    pairs = [(i, i + 1) for i in range(n - 1)]
    if boundary == "periodic" and n > 2:
        pairs.append((n - 1, 0))
    for i, j in pairs:
        for axis in "Z" if model == "tfim" else "XYZ":
            reference += (-0.7 if model == "tfim" else 0.7) * op({i: axis, j: axis})
    for i in range(n):
        reference -= 0.4 * op({i: "X" if model == "tfim" else "Z"})
    assert np.allclose(ham, reference.full())
    energies, states = exact.solve(ham)
    assert np.allclose(energies, reference.eigenenergies())
    assert np.all(np.diff(energies) >= -1e-12)
    assert np.allclose(states.conj().T @ states, np.eye(2**n))
    assert exact.expectation(states[:, 0], ham) == pytest.approx(energies[0])
    assert abs(exact.expectation(states[:, 0], exact.magnetization(n))) <= 1


def test_analytical():
    assert exact.solve(exact.hamiltonian(2))[0][0] == pytest.approx(-np.sqrt(5))
    assert exact.solve(exact.hamiltonian(2, h=0, model="heisenberg"))[0].tolist() == pytest.approx(
        [-3, 1, 1, 1]
    )
    assert exact.solve(exact.hamiltonian(3, j=0, h=0.5))[0][0] == pytest.approx(-1.5)


def test_fidelity():
    a = np.array([1, 1j])
    assert metrics.fidelity(a, -3j * a) == pytest.approx(1)
    assert metrics.fidelity(a, [1, -1j]) == pytest.approx(0)
    with pytest.raises(ValueError):
        metrics.fidelity([0, 0], a)
    assert metrics.statistics([1, 3])["std"] == pytest.approx(np.sqrt(2))
    assert metrics.statistics([1])["std"] is None


def test_rbm_convergence_reproducibility():
    ham = exact.hamiltonian(2)
    reference = exact.solve(ham)[1][:, 0]
    a = nqs.train(ham, 2, 0, steps=180)
    b = nqs.train(ham, 2, 0, steps=180)
    assert np.array_equal(a["state"], b["state"])
    assert np.allclose(nqs.state_from_parameters(a["parameters"]), a["state"])
    assert metrics.fidelity(a["state"], reference) > 0.999
    assert abs(exact.expectation(a["state"], ham) + np.sqrt(5)) < 1e-3
    assert nqs.sample(a["state"], 50).shape == (50,)


def test_vqe_convergence_reproducibility():
    ham = exact.hamiltonian(2)
    a = variational.vqe(ham, 2, iterations=80)
    b = variational.vqe(ham, 2, iterations=80)
    assert np.allclose(a["state"], b["state"])
    assert abs(exact.expectation(a["state"], ham) + np.sqrt(5)) < 1e-7


@pytest.mark.parametrize("kind", ["depolarizing", "bit_flip", "readout"])
def test_channels(kind):
    state = np.array([1, 0, 0, 1]) / np.sqrt(2)
    rho = np.outer(state, state)
    for p in (0, 0.1, 1):
        result = noise.channel(rho, 2, p, kind)
        assert np.trace(result) == pytest.approx(1)
        assert np.linalg.eigvalsh(result).min() >= -1e-12
    assert np.allclose(noise.channel(rho, 2, 0, kind), rho)


def test_zne():
    state = np.array([1, 0, 0, 0])
    result = noise.experiment(state, exact.operator(2, {0: "Z", 1: "Z"}), 2)
    assert result["mitigated_error"] < 1e-10
    assert result["raw_error"] > 0
    with pytest.raises(ValueError):
        noise.experiment(state, exact.hamiltonian(2), 2, kind="readout")


def test_qaoa():
    result = variational.qaoa(2, [[0, 1]], iterations=60)
    assert result["exact_cut"] == 1
    assert 0.999 < result["approximation_ratio"] <= 1 + 1e-10
