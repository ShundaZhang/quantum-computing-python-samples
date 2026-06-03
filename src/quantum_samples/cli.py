"""Command-line entry point for the sample project."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .advanced_workflow import format_advanced_report, run_advanced_workflow
from .common import pretty_counts
from .demos import run_basic_demos


def _json_default(value: object) -> object:
    if hasattr(value, "item"):
        return value.item()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def run_basics(shots: int) -> None:
    for result in run_basic_demos(shots=shots):
        print(f"\n== {result['title']} ==")
        for key, value in result.items():
            if key == "title":
                continue
            if key == "counts":
                print(f"{key}: {pretty_counts(value)}")
            elif key == "statevector":
                print(f"{key}: {value}")
            else:
                print(f"{key}: {value}")


def run_advanced(shots: int, output: Path | None) -> None:
    report = run_advanced_workflow(shots=shots)
    print(format_advanced_report(report))

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(report, indent=2, ensure_ascii=False, default=_json_default),
            encoding="utf-8",
        )
        print(f"\nWrote JSON report to {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Qiskit quantum computing samples.")
    parser.add_argument("--shots", type=int, default=1024, help="Number of simulator shots.")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("basics", help="Run all standalone educational examples.")
    advanced = subparsers.add_parser("advanced", help="Run the chained advanced workflow.")
    advanced.add_argument("--output", type=Path, default=None, help="Optional JSON report path.")

    args = parser.parse_args()
    command = args.command or "basics"
    if command == "basics":
        run_basics(shots=args.shots)
    elif command == "advanced":
        run_advanced(shots=args.shots, output=args.output)


if __name__ == "__main__":
    main()
