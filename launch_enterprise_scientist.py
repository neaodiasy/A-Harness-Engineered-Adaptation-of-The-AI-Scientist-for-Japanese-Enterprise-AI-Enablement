"""Launch the full J-Enterprise Agent Scientist pipeline.

This mirrors the launch-script role in Sakana AI's AI Scientist repositories:
one command runs the template/profile loading, opportunity generation,
feasibility check, candidate search, workflow design, prototype generation,
sandbox evaluation, proposal writing, and automated review.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from debug_server import run_pipeline


DEFAULT_PROFILE = {
    "company_description": "Japanese mid-sized enterprise exploring AI enablement across customer operations and back-office workflows.",
    "industry": "general Japanese enterprise",
    "main_business": "B2B and B2C operations with manual document, inquiry, and approval workflows.",
    "ai_objective": "Find a bounded, high-value AI software PoC that improves productivity while preserving human approval.",
    "pain_points": "Slow manual search, inconsistent answers, approval bottlenecks, and difficulty turning internal knowledge into repeatable workflow software.",
    "available_data": "Process descriptions, internal manuals, approved examples, tickets, sample documents, and escalation rules.",
    "constraints": "No automatic external sending, no final legal/financial/HR/customer-impacting decisions, evidence and audit trace required.",
}


def load_profile(path: str | None) -> dict:
    """Load an enterprise profile JSON file or return a generic sample."""
    if not path:
        return DEFAULT_PROFILE
    profile_path = Path(path).expanduser().resolve()
    return json.loads(profile_path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the enterprise scientist pipeline.")
    parser.add_argument("--profile", help="Path to a JSON enterprise profile.", default=None)
    parser.add_argument("--run-id", help="Optional run id stored in outputs.", default="")
    args = parser.parse_args()

    if not os.environ.get("DEEPSEEK_API_KEY"):
        raise SystemExit(
            "DEEPSEEK_API_KEY is required for strict API mode.\n"
            "Run: export DEEPSEEK_API_KEY=\"...\""
        )

    profile = load_profile(args.profile)
    try:
        _, response = run_pipeline(profile, args.run_id)
    except RuntimeError as exc:
        raise SystemExit(f"Pipeline failed in strict DeepSeek API mode: {exc}") from None
    summary = response.get("final_summary") or {
        "status": "complete",
        "mode": response.get("mode", "real_deepseek_api"),
        "selected_opportunity": response.get("selected_opportunity", {}).get("name"),
        "generated_app": response.get("prototype_manifest", {}).get("app_dir"),
        "evaluation_success": response.get("evaluation_results", {}).get("success"),
        "sandbox_success": response.get("sandbox_report", {}).get("success"),
        "review_score": response.get("review", {}).get("overall_score"),
        "outputs": "",
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
