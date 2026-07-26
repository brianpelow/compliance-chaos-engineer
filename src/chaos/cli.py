"""Command-line interface for the compliance chaos engine.

Runs governance chaos experiments and prints a detection scorecard. The whole
run is deterministic: the same command always produces the same scorecard.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from chaos.failures import all_failures
from chaos.runner import run_all


def _print_catalog() -> None:
    print("Governance failure classes this engine can inject:\n")
    for d in all_failures():
        print(f"  {d.failure_class.value}")
        print(f"    {d.title}  [{d.severity.value}]")
        print(f"    expected control: {d.expected_control}")
        print()


def _print_scorecard(as_json: bool, out_path: str | None) -> int:
    card = run_all()

    if as_json:
        payload = json.dumps(card.to_dict(), indent=2)
        if out_path:
            Path(out_path).write_text(payload + "\n", encoding="utf-8")
            print(f"Scorecard written to {out_path}")
        else:
            print(payload)
        return 0

    print("=" * 66)
    print("  GOVERNANCE CHAOS SCORECARD")
    print("=" * 66)
    print()
    for r in card.results:
        marker = "PASS" if r.detected else "MISS"
        print(f"  [{marker}] {r.title}")
        print(f"         severity: {r.severity}   expected: {r.expected_control}")
        if not r.detected:
            print(f"         BLAST RADIUS: {r.blast_radius}")
        print()

    print("-" * 66)
    print(f"  Detection rate: {card.detection_rate}%  ({card.detected}/{card.total})")
    print(f"  Critical misses: {len(card.critical_misses)}")
    print("-" * 66)

    if card.missed:
        print()
        print("  A missed failure is not a bug in this tool. It is a governance")
        print("  gap the tool exists to surface. A control set that catches every")
        print("  failure a chaos engine can imagine has simply not imagined enough")
        print("  failures. The value is in the miss, named and attributed.")

    if out_path:
        Path(out_path).write_text(json.dumps(card.to_dict(), indent=2) + "\n", encoding="utf-8")
        print(f"\n  Full scorecard written to {out_path}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="chaos",
        description="Chaos engineering for governance controls.",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="List the governance failure classes.")

    run_p = sub.add_parser("run", help="Run all experiments and print the scorecard.")
    run_p.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    run_p.add_argument("--out", metavar="PATH", help="Also write the scorecard JSON to a file.")

    args = parser.parse_args()

    if args.command == "list":
        _print_catalog()
        return 0
    if args.command == "run":
        return _print_scorecard(as_json=args.json, out_path=args.out)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())