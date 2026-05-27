"""Entrypoint for the generated agent product."""

from __future__ import annotations

import argparse
import json
import sys

from backend.agent import run_case, run_interaction
from backend.api import serve
from backend.data_store import load_sample_cases


def run_cli(case_id: str | None = None, max_cases: int = 0) -> None:
    cases = load_sample_cases()
    if case_id:
        cases = [case for case in cases if case.get("case_id") == case_id]
        if not cases:
            available = ", ".join(case.get("case_id", "<missing>") for case in load_sample_cases())
            raise SystemExit(f"Unknown case_id: {case_id}. Available: {available}")
    if max_cases > 0:
        cases = cases[:max_cases]
    outputs = []
    for index, case in enumerate(cases, start=1):
        current_id = case.get("case_id", f"case_{index}")
        print(
            f"[generated-app] running {current_id} ({index}/{len(cases)}) with DeepSeek runtime...",
            file=sys.stderr,
            flush=True,
        )
        outputs.append(run_case(case))
        print(f"[generated-app] completed {current_id}", file=sys.stderr, flush=True)
    print(json.dumps(outputs, ensure_ascii=False, indent=2))


def list_cases() -> None:
    for case in load_sample_cases():
        print(case.get("case_id", "<missing>"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the generated agent product.")
    parser.add_argument("--cli", action="store_true", help="Run generated sample cases and print JSON.")
    parser.add_argument("--case-id", default="", help="Run only one sample case id in CLI mode.")
    parser.add_argument("--max-cases", type=int, default=0, help="Run at most this many sample cases in CLI mode.")
    parser.add_argument("--list-cases", action="store_true", help="List available sample case ids.")
    parser.add_argument("--port", type=int, default=8766, help="Local web server port.")
    args = parser.parse_args()
    if args.list_cases:
        list_cases()
    elif args.cli:
        run_cli(args.case_id or None, args.max_cases)
    else:
        serve(args.port)


if __name__ == "__main__":
    main()
