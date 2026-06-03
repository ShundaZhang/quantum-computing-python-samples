"""Deutsch-Jozsa: distinguish constant and balanced oracles."""

from quantum_samples.demos import deutsch_jozsa_demo


if __name__ == "__main__":
    print(deutsch_jozsa_demo(kind="constant"))
    print(deutsch_jozsa_demo(kind="balanced"))
