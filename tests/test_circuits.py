import numpy as np
import pennylane as qml

from qas.discovery import Gate, execute


def test_circuit_independent_pennylane_reference():
    gates = [
        Gate("RY", 0, angle=0.3),
        Gate("H", 2),
        Gate("CNOT", 0, 2),
        Gate("RY", 1, angle=-0.7),
        Gate("CNOT", 2, 1),
    ]

    @qml.qnode(qml.device("default.qubit", wires=3))
    def reference():
        for gate in gates:
            if gate.name == "H":
                qml.Hadamard(gate.wire)
            elif gate.name == "RY":
                qml.RY(gate.angle, gate.wire)
            else:
                qml.CNOT([gate.wire, gate.target])
        return qml.state()

    assert np.allclose(execute(gates, 3), reference(), atol=1e-12)
