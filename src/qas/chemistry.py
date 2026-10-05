"""Small H2/STO-3G molecular calculation, including nuclear repulsion (Hartree)."""

import numpy as np
from scipy.optimize import minimize


def h2(distance=1.4, seed=0, iterations=100):
    import pennylane as qml

    if not 0.4 <= distance <= 4 or iterations < 1:
        raise ValueError("H2 distance must be 0.4–4 bohr")
    coordinates = qml.numpy.array(
        [[0.0, 0.0, -distance / 2], [0.0, 0.0, distance / 2]], requires_grad=False
    )
    molecule = qml.qchem.Molecule(["H", "H"], coordinates, basis_name="sto-3g", unit="bohr")
    hamiltonian, n = qml.qchem.molecular_hamiltonian(
        molecule, method="dhf", mapping="jordan_wigner"
    )
    matrix = np.asarray(qml.matrix(hamiltonian, wire_order=range(n)), dtype=complex)
    sector = [i for i in range(2**n) if i.bit_count() == 2]
    eigenvalues, eigenvectors = np.linalg.eigh(matrix[np.ix_(sector, sector)])
    reference = np.zeros(2**n, dtype=complex)
    reference[sector] = eigenvectors[:, 0]

    @qml.qnode(qml.device("default.qubit", wires=n), interface="autograd")
    def energy(theta):
        qml.BasisState(np.array([1, 1, 0, 0]), wires=range(n))
        qml.DoubleExcitation(theta[0], wires=range(n))
        return qml.expval(hamiltonian)

    @qml.qnode(qml.device("default.qubit", wires=n))
    def state(theta):
        qml.BasisState(np.array([1, 1, 0, 0]), wires=range(n))
        qml.DoubleExcitation(theta[0], wires=range(n))
        return qml.state()

    history = []
    result = minimize(
        lambda t: float(energy(t)),
        np.random.default_rng(seed).normal(0, 0.1, 1),
        jac=lambda t: np.asarray(qml.grad(energy)(qml.numpy.array(t, requires_grad=True))),
        callback=lambda t: history.append(float(energy(t))),
        method="BFGS",
        options={"maxiter": iterations, "gtol": 1e-9},
    )
    return dict(
        energy=float(result.fun),
        exact_energy=float(eigenvalues[0]),
        absolute_energy_error=abs(float(result.fun) - float(eigenvalues[0])),
        fidelity=float(abs(np.vdot(reference, state(result.x))) ** 2),
        hartree_fock_energy=float(energy(np.zeros(1))),
        distance_bohr=distance,
        basis="STO-3G",
        mapping="Jordan-Wigner",
        electrons=2,
        spin_orbitals=4,
        active_space="all two spatial orbitals; two-electron sector",
        units="Hartree",
        reference="PennyLane differentiable HF integrals + NumPy sector diagonalization",
        ansatz="HF |1100> + particle-conserving DoubleExcitation",
        parameters=result.x.tolist(),
        iterations=int(result.nit),
        optimizer_success=bool(result.success),
        history=history,
    )
