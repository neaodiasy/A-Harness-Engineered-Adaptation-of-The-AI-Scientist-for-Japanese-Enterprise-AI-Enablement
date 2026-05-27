"""Evaluate the generated enterprise agent product."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from backend.agent import run_case
from backend.data_store import load_sample_cases


APP_DIR = Path(__file__).resolve().parent
PLACEHOLDER_PATTERN = re.compile(r"エリア[ABC]|Area [ABC]", re.IGNORECASE)
FORBIDDEN_GUARANTEES = ["保証します", "確約します", "絶対に安全", "投資利益", "必ず値上がり", "法的助言"]


def _is_japanese(text: str) -> bool:
    return bool(re.search(r"[ぁ-んァ-ヶ一-龥]", text or ""))


def _candidate_names(output: dict[str, Any]) -> list[str]:
    return [item.get("name_ja", "") for item in output.get("ranked_area_candidates", []) if item.get("name_ja")]


def evaluate_output(case: dict[str, Any], output: dict[str, Any]) -> dict[str, bool]:
    classification = output.get("classification", {})
    names = _candidate_names(output)
    recommendation = output.get("recommendation_ja", "")
    draft = output.get("customer_or_business_draft_ja", "")
    combined = recommendation + "\n" + draft
    return {
        "has_case_id": bool(output.get("case_id")),
        "classification_label": bool(classification.get("label")),
        "confidence_not_fixed_half": isinstance(classification.get("confidence"), (int, float)) and classification.get("confidence") != 0.5,
        "classification_rationale": bool(classification.get("rationale")),
        "local_tool_results_exists": bool(output.get("local_tool_results")),
        "ranked_area_candidates_exists": bool(output.get("ranked_area_candidates")),
        "ranked_property_candidates_exists": bool(output.get("ranked_property_candidates")),
        "uses_actual_candidate_names": any(name and name in combined for name in names),
        "no_placeholder_candidate_names": not (PLACEHOLDER_PATTERN.search(combined) and not any(name in combined for name in names)),
        "has_evidence": bool(output.get("evidence")),
        "has_missing_information": bool(output.get("missing_information")),
        "human_approval_required": output.get("human_approval_required") is True,
        "send_allowed_false": output.get("send_allowed") is False,
        "customer_draft_is_japanese": _is_japanese(draft),
        "approval_packet": bool(output.get("approval_packet", {}).get("decision_options")),
        "audit_trace": bool(output.get("audit_trace", {}).get("tool_names")),
        "no_final_guarantee": not any(term in combined for term in FORBIDDEN_GUARANTEES),
    }


def _select_cases(case_id: str = "", max_cases: int = 0) -> list[dict[str, Any]]:
    cases = load_sample_cases()
    if case_id:
        cases = [case for case in cases if case.get("case_id") == case_id]
        if not cases:
            available = ", ".join(case.get("case_id", "<missing>") for case in load_sample_cases())
            raise SystemExit(f"Unknown case_id: {case_id}. Available: {available}")
    if max_cases > 0:
        cases = cases[:max_cases]
    return cases


def main(case_id: str = "", max_cases: int = 0) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for case in _select_cases(case_id, max_cases):
        try:
            output = run_case(case)
            checks = evaluate_output(case, output)
            results.append({
                "case_id": case.get("case_id"),
                "passed": all(checks.values()),
                "checks": checks,
                "output": output,
            })
        except Exception as exc:
            results.append({
                "case_id": case.get("case_id"),
                "passed": False,
                "checks": {"exception": False},
                "error": str(exc),
            })
    passed = sum(1 for item in results if item["passed"])
    summary = {
        "success": passed == len(results) and bool(results),
        "passed": passed,
        "total": len(results),
        "pass_rate": round(passed / max(len(results), 1), 2),
    }
    (APP_DIR / "evaluation_results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (APP_DIR / "evaluation_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"summary": summary, "results": results}, ensure_ascii=False, indent=2))
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate the generated product.")
    parser.add_argument("--case-id", default="", help="Evaluate only one sample case id.")
    parser.add_argument("--max-cases", type=int, default=0, help="Evaluate at most this many cases.")
    args = parser.parse_args()
    main(args.case_id, args.max_cases)
