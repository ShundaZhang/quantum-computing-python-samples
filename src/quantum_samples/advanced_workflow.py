"""A larger educational workflow that chains many quantum computing ideas."""

from __future__ import annotations

from dataclasses import dataclass
from math import pi
from typing import Iterable

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import DensityMatrix, Statevector, partial_trace, state_fidelity
from qiskit_aer.noise import NoiseModel, depolarizing_error

from .common import (
    DEFAULT_SEED,
    assignment_to_bitstring,
    bitstring_to_assignment,
    pretty_counts,
    run_counts,
    simulator,
    top_bitstring,
)
from .demos import (
    bell_state_circuit,
    grover_demo,
    phase_estimation_demo,
    superdense_coding_demo,
    teleportation_circuit,
    vqe_demo,
)


@dataclass(frozen=True)
class Route:
    """A toy candidate in the advanced scenario."""

    bitstring: str
    name: str
    distance: int
    congestion: int
    battery_risk: int
    priority: int

    @property
    def score(self) -> int:
        return self.priority * 3 - self.distance - self.congestion - self.battery_risk


ROUTES = [
    Route("00", "north ridge", distance=2, congestion=2, battery_risk=1, priority=3),
    Route("01", "east tunnel", distance=1, congestion=4, battery_risk=2, priority=2),
    Route("10", "south bridge", distance=3, congestion=1, battery_risk=1, priority=5),
    Route("11", "west harbor", distance=2, congestion=3, battery_risk=3, priority=4),
]


def quantum_random_bits(length: int, seed: int = DEFAULT_SEED) -> str:
    """Generate reproducible simulator-backed random bits with Hadamards."""

    bits: list[str] = []
    chunk_size = 16
    while sum(len(chunk) for chunk in bits) < length:
        remaining = length - sum(len(chunk) for chunk in bits)
        width = min(chunk_size, remaining)
        circuit = QuantumCircuit(width, width, name="qrng")
        circuit.h(range(width))
        circuit.measure(range(width), range(width))
        counts = run_counts(circuit, shots=1, seed=seed + len(bits))
        bits.append(next(iter(counts)).zfill(width))
    return "".join(bits)[:length]


def bb84_sifted_key(raw_bits: str, key_length: int = 12) -> dict[str, object]:
    """Simulate the BB84 basis-sifting idea using QRNG bits."""

    cursor = 0

    def take(n: int) -> list[int]:
        nonlocal cursor
        chunk = raw_bits[cursor : cursor + n]
        cursor += n
        return [int(bit) for bit in chunk]

    sender_bits = take(key_length)
    sender_bases = take(key_length)
    receiver_bases = take(key_length)
    fallback = take(key_length)

    sifted: list[int] = []
    measurements: list[int] = []
    for index, bit in enumerate(sender_bits):
        if sender_bases[index] == receiver_bases[index]:
            measured = bit
            sifted.append(measured)
        else:
            measured = fallback[index]
        measurements.append(measured)

    return {
        "sender_bits": sender_bits,
        "sender_bases": sender_bases,
        "receiver_bases": receiver_bases,
        "measurements": measurements,
        "sifted_key": "".join(str(bit) for bit in sifted),
        "matched_positions": [
            index for index, (alice, bob) in enumerate(zip(sender_bases, receiver_bases)) if alice == bob
        ],
    }


def choose_route_with_grover(shots: int = 1024) -> dict[str, object]:
    """Use Grover search to amplify the best-scoring route."""

    best_route = max(ROUTES, key=lambda route: route.score)
    result = grover_demo(target=best_route.bitstring, shots=shots)
    result["route"] = best_route.__dict__
    return result


def teleport_route_state(route: Route) -> dict[str, object]:
    """Encode route risk as a qubit angle and teleport that state."""

    theta = (route.battery_risk + route.congestion) / 8 * pi
    phi = route.distance / 8 * pi

    input_circuit = QuantumCircuit(1)
    input_circuit.ry(theta, 0)
    input_circuit.rz(phi, 0)
    input_state = DensityMatrix(Statevector.from_instruction(input_circuit))

    circuit = teleportation_circuit(theta=theta, phi=phi)
    output_state = partial_trace(DensityMatrix.from_instruction(circuit), [0, 1])
    return {
        "theta": theta,
        "phi": phi,
        "fidelity": float(state_fidelity(input_state, output_state)),
    }


def qaoa_circuit(gamma: float, beta: float, edges: Iterable[tuple[int, int]], nodes: int = 4) -> QuantumCircuit:
    """Build a one-layer QAOA circuit for MaxCut."""

    circuit = QuantumCircuit(nodes, name="qaoa_maxcut")
    circuit.h(range(nodes))
    for left, right in edges:
        circuit.rzz(2 * gamma, left, right)
    for qubit in range(nodes):
        circuit.rx(2 * beta, qubit)
    return circuit


def cut_value(bitstring: str, edges: Iterable[tuple[int, int]]) -> int:
    assignment = bitstring_to_assignment(bitstring)
    return sum(assignment[left] != assignment[right] for left, right in edges)


def expected_cut(circuit: QuantumCircuit, edges: Iterable[tuple[int, int]]) -> float:
    probabilities = Statevector.from_instruction(circuit).probabilities_dict()
    return float(sum(probability * cut_value(bitstring, edges) for bitstring, probability in probabilities.items()))


def qaoa_route_partition(grid_points: int = 11, shots: int = 1024) -> dict[str, object]:
    """Partition four route monitors with a tiny QAOA MaxCut example."""

    edges = [(0, 1), (1, 2), (2, 3), (0, 3), (1, 3)]
    best = {"value": -1.0, "gamma": 0.0, "beta": 0.0}
    for gamma in np.linspace(0, pi, grid_points):
        for beta in np.linspace(0, pi / 2, grid_points):
            value = expected_cut(qaoa_circuit(gamma, beta, edges), edges)
            if value > best["value"]:
                best = {"value": value, "gamma": float(gamma), "beta": float(beta)}

    measured = QuantumCircuit(4, 4)
    measured.compose(qaoa_circuit(best["gamma"], best["beta"], edges), inplace=True)
    measured.measure(range(4), range(4))
    counts = run_counts(measured, shots=shots)
    winner = top_bitstring(counts)

    return {
        "edges": edges,
        "best_parameters": best,
        "counts": counts,
        "best_partition_bitstring": winner,
        "best_partition_assignment": bitstring_to_assignment(winner),
        "best_cut_value": cut_value(winner, edges),
    }


def noisy_bell_comparison(shots: int = 1024, seed: int = DEFAULT_SEED) -> dict[str, object]:
    """Compare ideal and noisy Bell-pair measurements."""

    ideal_counts = run_counts(bell_state_circuit(), shots=shots, seed=seed)

    noise_model = NoiseModel()
    noise_model.add_all_qubit_quantum_error(depolarizing_error(0.01, 1), ["h", "x", "z", "rx", "ry"])
    noise_model.add_all_qubit_quantum_error(depolarizing_error(0.04, 2), ["cx", "cz", "rzz"])
    backend = simulator(seed, noise_model=noise_model)
    noisy_counts = run_counts(bell_state_circuit(), shots=shots, seed=seed, backend=backend)

    return {
        "ideal_counts": ideal_counts,
        "noisy_counts": noisy_counts,
        "noise_model": "1% one-qubit depolarizing noise, 4% two-qubit depolarizing noise",
    }


def transpilation_snapshot() -> dict[str, object]:
    """Show how a circuit changes when compiled for a simulator backend."""

    circuit = bell_state_circuit()
    backend = simulator()
    compiled = transpile(circuit, backend, seed_transpiler=DEFAULT_SEED, optimization_level=2)
    return {
        "original_depth": circuit.depth(),
        "compiled_depth": compiled.depth(),
        "original_ops": dict(circuit.count_ops()),
        "compiled_ops": dict(compiled.count_ops()),
    }


def run_advanced_workflow(shots: int = 1024) -> dict[str, object]:
    """Run the full chained scenario and return a structured report."""

    random_bits = quantum_random_bits(64)
    bb84 = bb84_sifted_key(random_bits)
    grover = choose_route_with_grover(shots=shots)
    chosen_route = max(ROUTES, key=lambda route: route.score)
    teleported = teleport_route_state(chosen_route)
    superdense = superdense_coding_demo(message=chosen_route.bitstring, shots=shots)
    phase = phase_estimation_demo(phase=3 / 8, shots=shots)
    vqe = vqe_demo(grid_points=21)
    qaoa = qaoa_route_partition(grid_points=9, shots=shots)
    noise = noisy_bell_comparison(shots=shots)
    transpilation = transpilation_snapshot()

    return {
        "scenario": "Quantum-assisted dispatch lab",
        "story": (
            "A dispatch system uses QRNG and BB84-like basis sifting for shared randomness, "
            "superdense coding for compact control messages, teleportation to move a qubit state, "
            "Grover search to select a route, QPE for phase calibration, VQE for an energy proxy, "
            "QAOA for a partitioning decision, and a noise/transpilation check before execution."
        ),
        "routes": [route.__dict__ | {"score": route.score} for route in ROUTES],
        "qrng_bits_preview": random_bits[:24],
        "bb84": bb84,
        "superdense_coding": superdense,
        "teleportation": teleported,
        "grover_route_search": grover,
        "phase_estimation": phase,
        "vqe_energy_proxy": vqe,
        "qaoa_partition": qaoa,
        "noise_comparison": noise,
        "transpilation": transpilation,
    }


def format_advanced_report(report: dict[str, object]) -> str:
    """Create a concise text report for CLI users."""

    grover = report["grover_route_search"]
    qaoa = report["qaoa_partition"]
    noise = report["noise_comparison"]
    return "\n".join(
        [
            f"Scenario: {report['scenario']}",
            f"QRNG preview: {report['qrng_bits_preview']}",
            f"BB84 sifted key: {report['bb84']['sifted_key'] or '(empty in this run)'}",
            f"Superdense decoded route bits: {report['superdense_coding']['decoded']}",
            f"Teleportation fidelity: {report['teleportation']['fidelity']:.6f}",
            f"Grover chose: {grover['found']} ({grover['route']['name']})",
            f"Phase estimate: {report['phase_estimation']['estimated_phase']:.3f}",
            f"VQE best energy: {report['vqe_energy_proxy']['best']['energy']:.6f}",
            f"QAOA partition: {qaoa['best_partition_bitstring']} cut={qaoa['best_cut_value']}",
            f"Ideal Bell counts: {pretty_counts(noise['ideal_counts'])}",
            f"Noisy Bell counts: {pretty_counts(noise['noisy_counts'])}",
            f"Transpiled depth: {report['transpilation']['original_depth']} -> {report['transpilation']['compiled_depth']}",
        ]
    )


def route_assignment_table() -> dict[str, str]:
    """Expose route labels in the same bit order used by Qiskit counts."""

    return {assignment_to_bitstring(bitstring_to_assignment(route.bitstring)): route.name for route in ROUTES}
