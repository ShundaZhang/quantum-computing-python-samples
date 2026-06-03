from quantum_samples.advanced_workflow import run_advanced_workflow
from quantum_samples.demos import (
    bell_state_demo,
    grover_demo,
    phase_estimation_demo,
    superdense_coding_demo,
    teleportation_demo,
)


def test_bell_state_is_correlated():
    counts = bell_state_demo(shots=256)["counts"]
    assert set(counts).issubset({"00", "11"})


def test_superdense_decodes_message():
    result = superdense_coding_demo(message="10", shots=128)
    assert result["decoded"] == "10"


def test_teleportation_preserves_state():
    result = teleportation_demo(theta=0.61, phi=0.27)
    assert result["fidelity"] > 0.999999


def test_grover_finds_target():
    result = grover_demo(target="10", shots=128)
    assert result["found"] == "10"


def test_phase_estimation_exact_binary_fraction():
    result = phase_estimation_demo(phase=3 / 8, shots=128)
    assert result["measured_bits"] == "011"
    assert result["estimated_phase"] == 3 / 8


def test_advanced_workflow_smoke():
    report = run_advanced_workflow(shots=128)
    assert report["grover_route_search"]["found"] == "10"
    assert report["teleportation"]["fidelity"] > 0.999999
    assert "qaoa_partition" in report
