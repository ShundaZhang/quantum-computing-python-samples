"""Run the larger scenario that chains many quantum computing ideas."""

from quantum_samples.advanced_workflow import format_advanced_report, run_advanced_workflow


if __name__ == "__main__":
    report = run_advanced_workflow()
    print(format_advanced_report(report))
