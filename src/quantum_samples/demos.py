"""Common quantum computing examples implemented with Qiskit."""

from __future__ import annotations

from math import pi

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFTGate, grover_operator
from qiskit.quantum_info import DensityMatrix, SparsePauliOp, Statevector, partial_trace, state_fidelity

from .common import DEFAULT_SEED, run_counts, strip_measurements, top_bitstring


def superposition_circuit() -> QuantumCircuit:
    """Create a one-qubit superposition with a Hadamard gate."""

    circuit = QuantumCircuit(1, 1, name="superposition")
    circuit.h(0)
    circuit.measure(0, 0)
    return circuit


def superposition_demo(shots: int = 1024) -> dict[str, object]:
    circuit = superposition_circuit()
    counts = run_counts(circuit, shots=shots)
    return {
        "title": "Hadamard superposition",
        "counts": counts,
        "note": "A balanced simulator result should be close to 50/50 over 0 and 1.",
    }


def bell_state_circuit() -> QuantumCircuit:
    """Create and measure the Bell state (|00> + |11>) / sqrt(2)."""

    circuit = QuantumCircuit(2, 2, name="bell_state")
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure([0, 1], [0, 1])
    return circuit


def bell_state_demo(shots: int = 1024) -> dict[str, object]:
    circuit = bell_state_circuit()
    counts = run_counts(circuit, shots=shots)
    state = Statevector.from_instruction(strip_measurements(circuit))
    amplitudes = {
        str(label): {"real": float(np.real(amplitude)), "imag": float(np.imag(amplitude))}
        for label, amplitude in state.to_dict().items()
    }
    return {
        "title": "Bell-state entanglement",
        "counts": counts,
        "statevector": amplitudes,
        "note": "Only 00 and 11 should appear, demonstrating correlated measurement outcomes.",
    }


def superdense_coding_circuit(message: str = "10") -> QuantumCircuit:
    """Encode two classical bits into one transmitted qubit."""

    if message not in {"00", "01", "10", "11"}:
        raise ValueError("message must be one of 00, 01, 10, 11")

    circuit = QuantumCircuit(2, 2, name=f"superdense_{message}")
    circuit.h(0)
    circuit.cx(0, 1)

    if message[0] == "1":
        circuit.x(0)
    if message[1] == "1":
        circuit.z(0)

    circuit.cx(0, 1)
    circuit.h(0)
    circuit.measure([0, 1], [0, 1])
    return circuit


def superdense_coding_demo(message: str = "10", shots: int = 1024) -> dict[str, object]:
    circuit = superdense_coding_circuit(message)
    counts = run_counts(circuit, shots=shots)
    return {
        "title": "Superdense coding",
        "message": message,
        "decoded": top_bitstring(counts),
        "counts": counts,
        "note": "A Bell pair lets Alice communicate two classical bits by sending one qubit.",
    }


def teleportation_circuit(theta: float = 0.73, phi: float = 0.41) -> QuantumCircuit:
    """Teleport a prepared qubit state with coherent correction gates."""

    circuit = QuantumCircuit(3, name="coherent_teleportation")
    circuit.ry(theta, 0)
    circuit.rz(phi, 0)

    circuit.h(1)
    circuit.cx(1, 2)

    circuit.cx(0, 1)
    circuit.h(0)

    circuit.cx(1, 2)
    circuit.cz(0, 2)
    return circuit


def teleportation_demo(theta: float = 0.73, phi: float = 0.41) -> dict[str, object]:
    input_circuit = QuantumCircuit(1)
    input_circuit.ry(theta, 0)
    input_circuit.rz(phi, 0)
    input_state = DensityMatrix(Statevector.from_instruction(input_circuit))

    circuit = teleportation_circuit(theta=theta, phi=phi)
    full_state = DensityMatrix.from_instruction(circuit)
    output_state = partial_trace(full_state, [0, 1])
    fidelity = state_fidelity(input_state, output_state)

    return {
        "title": "Quantum teleportation",
        "theta": theta,
        "phi": phi,
        "fidelity": float(fidelity),
        "note": "Fidelity near 1 means qubit 2 carries the original state.",
    }


def deutsch_jozsa_circuit(kind: str = "balanced", input_qubits: int = 3) -> QuantumCircuit:
    """Build the Deutsch-Jozsa circuit for a constant or balanced oracle."""

    if kind not in {"constant", "balanced"}:
        raise ValueError("kind must be constant or balanced")

    output = input_qubits
    circuit = QuantumCircuit(input_qubits + 1, input_qubits, name=f"deutsch_jozsa_{kind}")
    circuit.x(output)
    circuit.h(range(input_qubits + 1))

    if kind == "constant":
        pass
    else:
        for qubit in range(input_qubits):
            circuit.cx(qubit, output)

    circuit.h(range(input_qubits))
    circuit.measure(range(input_qubits), range(input_qubits))
    return circuit


def deutsch_jozsa_demo(kind: str = "balanced", shots: int = 1024) -> dict[str, object]:
    circuit = deutsch_jozsa_circuit(kind=kind)
    counts = run_counts(circuit, shots=shots)
    top = top_bitstring(counts)
    decision = "constant" if top == "0" * 3 else "balanced"
    return {
        "title": "Deutsch-Jozsa algorithm",
        "oracle": kind,
        "decision": decision,
        "counts": counts,
        "note": "One quantum oracle call distinguishes constant from balanced functions.",
    }


def phase_oracle(bitstring: str) -> QuantumCircuit:
    """Return a phase oracle that marks exactly one computational basis state."""

    if not bitstring or any(bit not in "01" for bit in bitstring):
        raise ValueError("bitstring must contain only 0 and 1")

    qubits = len(bitstring)
    circuit = QuantumCircuit(qubits, name=f"oracle_{bitstring}")
    for qubit, bit in enumerate(reversed(bitstring)):
        if bit == "0":
            circuit.x(qubit)

    if qubits == 1:
        circuit.z(0)
    else:
        circuit.h(qubits - 1)
        circuit.mcx(list(range(qubits - 1)), qubits - 1)
        circuit.h(qubits - 1)

    for qubit, bit in enumerate(reversed(bitstring)):
        if bit == "0":
            circuit.x(qubit)
    return circuit


def grover_search_circuit(target: str = "10") -> QuantumCircuit:
    """Build a one-iteration Grover search circuit for a small database."""

    oracle = phase_oracle(target)
    circuit = QuantumCircuit(len(target), len(target), name=f"grover_{target}")
    circuit.h(range(len(target)))
    circuit.compose(grover_operator(oracle), inplace=True)
    circuit.measure(range(len(target)), range(len(target)))
    return circuit


def grover_demo(target: str = "10", shots: int = 1024) -> dict[str, object]:
    circuit = grover_search_circuit(target=target)
    counts = run_counts(circuit, shots=shots)
    return {
        "title": "Grover search",
        "target": target,
        "found": top_bitstring(counts),
        "counts": counts,
        "note": "For four candidates, one Grover iteration amplifies the marked answer.",
    }


def phase_estimation_circuit(phase: float = 3 / 8, evaluation_qubits: int = 3) -> QuantumCircuit:
    """Estimate the eigenphase of a one-qubit phase gate."""

    target = evaluation_qubits
    circuit = QuantumCircuit(evaluation_qubits + 1, evaluation_qubits, name="phase_estimation")
    circuit.x(target)

    for qubit in range(evaluation_qubits):
        circuit.h(qubit)

    for qubit in range(evaluation_qubits):
        repetitions = 2**qubit
        circuit.cp(2 * pi * phase * repetitions, qubit, target)

    circuit.append(QFTGate(evaluation_qubits).inverse(), range(evaluation_qubits))
    circuit.measure(range(evaluation_qubits), range(evaluation_qubits))
    return circuit


def phase_estimation_demo(phase: float = 3 / 8, shots: int = 1024) -> dict[str, object]:
    circuit = phase_estimation_circuit(phase=phase)
    counts = run_counts(circuit, shots=shots)
    measured = top_bitstring(counts)
    estimated = int(measured, 2) / (2 ** len(measured))
    return {
        "title": "Quantum phase estimation",
        "actual_phase": phase,
        "measured_bits": measured,
        "estimated_phase": estimated,
        "counts": counts,
        "note": "QPE turns an eigenvalue phase into a readable binary estimate.",
    }


def vqe_ansatz(theta0: float, theta1: float) -> QuantumCircuit:
    """A compact two-qubit ansatz for the VQE sample."""

    circuit = QuantumCircuit(2, name="vqe_ansatz")
    circuit.ry(theta0, 0)
    circuit.ry(theta1, 1)
    circuit.cx(0, 1)
    return circuit


def toy_hamiltonian() -> SparsePauliOp:
    """A small Hamiltonian with ZZ, Z, and XX terms."""

    return SparsePauliOp.from_list(
        [
            ("II", 0.20),
            ("ZI", -0.75),
            ("IZ", -0.45),
            ("ZZ", 0.35),
            ("XX", 0.55),
        ]
    )


def estimate_energy(theta0: float, theta1: float, hamiltonian: SparsePauliOp | None = None) -> float:
    hamiltonian = hamiltonian or toy_hamiltonian()
    state = Statevector.from_instruction(vqe_ansatz(theta0, theta1))
    return float(np.real(state.expectation_value(hamiltonian)))


def vqe_demo(grid_points: int = 25) -> dict[str, object]:
    """Run a tiny grid-search VQE loop without extra optimizer dependencies."""

    hamiltonian = toy_hamiltonian()
    best = {"energy": float("inf"), "theta0": 0.0, "theta1": 0.0}
    for theta0 in np.linspace(0, 2 * pi, grid_points):
        for theta1 in np.linspace(0, 2 * pi, grid_points):
            energy = estimate_energy(theta0, theta1, hamiltonian)
            if energy < best["energy"]:
                best = {"energy": energy, "theta0": float(theta0), "theta1": float(theta1)}

    return {
        "title": "Variational quantum eigensolver",
        "hamiltonian": str(hamiltonian),
        "best": best,
        "note": "VQE alternates quantum state preparation with classical parameter search.",
    }


def run_basic_demos(shots: int = 1024) -> list[dict[str, object]]:
    """Run all standalone examples and return structured results."""

    return [
        superposition_demo(shots=shots),
        bell_state_demo(shots=shots),
        superdense_coding_demo(shots=shots),
        teleportation_demo(),
        deutsch_jozsa_demo(kind="constant", shots=shots),
        deutsch_jozsa_demo(kind="balanced", shots=shots),
        grover_demo(shots=shots),
        phase_estimation_demo(shots=shots),
        vqe_demo(),
    ]
