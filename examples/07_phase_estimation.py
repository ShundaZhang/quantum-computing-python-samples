"""Quantum phase estimation: turn an eigenphase into bits."""

from quantum_samples.demos import phase_estimation_demo


if __name__ == "__main__":
    print(phase_estimation_demo(phase=3 / 8))
