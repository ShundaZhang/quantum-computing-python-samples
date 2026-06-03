"""Small helpers shared by the sample circuits."""

from __future__ import annotations

from collections import Counter
from typing import Iterable

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

DEFAULT_SEED = 20260603


def simulator(seed: int = DEFAULT_SEED, **kwargs) -> AerSimulator:
    """Return a deterministic Aer simulator for reproducible examples."""

    return AerSimulator(seed_simulator=seed, **kwargs)


def run_counts(
    circuit: QuantumCircuit,
    shots: int = 1024,
    seed: int = DEFAULT_SEED,
    backend: AerSimulator | None = None,
) -> dict[str, int]:
    """Transpile and run a measured circuit, then return counts."""

    backend = backend or simulator(seed)
    compiled = transpile(circuit, backend, seed_transpiler=seed)
    result = backend.run(compiled, shots=shots).result()
    return dict(result.get_counts())


def top_bitstring(counts: dict[str, int]) -> str:
    """Return the most frequent bitstring from a counts dictionary."""

    if not counts:
        raise ValueError("counts is empty")
    return max(counts, key=counts.get)


def strip_measurements(circuit: QuantumCircuit) -> QuantumCircuit:
    """Copy a circuit and remove final measurements when present."""

    return circuit.remove_final_measurements(inplace=False)


def pretty_counts(counts: dict[str, int], limit: int = 8) -> str:
    """Format counts in descending order for CLI output."""

    pairs = Counter(counts).most_common(limit)
    return ", ".join(f"{state}: {shots}" for state, shots in pairs)


def bitstring_to_assignment(bitstring: str) -> list[int]:
    """Convert Qiskit's display bit order into qubit-index order."""

    return [int(bit) for bit in reversed(bitstring)]


def assignment_to_bitstring(assignment: Iterable[int]) -> str:
    """Convert qubit-index order into Qiskit's display bit order."""

    return "".join(str(bit) for bit in reversed(list(assignment)))
