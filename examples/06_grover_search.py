"""Grover search: amplify one marked answer among four candidates."""

from quantum_samples.demos import grover_demo


if __name__ == "__main__":
    print(grover_demo(target="10"))
