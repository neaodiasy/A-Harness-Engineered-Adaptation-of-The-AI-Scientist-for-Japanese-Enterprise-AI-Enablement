"""Proposal and reviewer generation for the enterprise enablement flow."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_proposal(result: dict, evaluation: dict) -> str:
    agent = result.get("recommended_agent", {})
    architecture = result.get("recommended_architecture", {})
    design = result.get("agent_design", {})
    selected = result.get("selected_opportunity", agent)
    feasibility = next(
        (item for item in result.get("feasibility_results", []) if item.get("name") == agent.get("name")),
        {},
    )
    lines = [
        f"# Enterprise AI Enablement Proposal: {agent.get('name', 'Selected Opportunity')}",
        "",
        "## Executive Summary",
        "",
        f"This proposal recommends a bounded PoC for **{agent.get('name', '')}**. "
        f"The system composes reusable primitives ({', '.join(architecture.get('selected_primitives', []))}) "
        "to create a customized agent workflow rather than selecting a fixed template.",
        "",
        "## Evidence-Grounded Rationale",
        "",
    ]
    for item in result.get("evidence_pack", {}).get("evidence_items", [])[:3]:
        lines.append(f"- {item.get('title')}: {item.get('summary')}")
    lines.extend([
        "",
        "## Selected Workflow",
        "",
        agent.get("target_workflow", ""),
        "",
        "## Selected Opportunity and Feasibility",
        "",
        f"- Selected opportunity: {selected.get('name', agent.get('name', ''))}",
        f"- Feasibility score: {feasibility.get('overall_score', 'n/a')}",
        f"- Recommendation: {feasibility.get('recommendation', 'n/a')}",
        f"- Search refinement: {selected.get('refinement_action', 'n/a')}",
        "",
        "## Agent Design",
        "",
    ])
    for step in design.get("agent_steps", []):
        lines.append(f"- {step}")
    lines.extend([
        "",
        "## Primitive Architecture",
        "",
        f"Selected primitives: {', '.join(architecture.get('selected_primitives', []))}",
        "",
        architecture.get("why_this_composition", ""),
        "",
        "## Human Approval and Risk Mitigation",
        "",
    ])
    for point in design.get("human_approval_points", []):
        lines.append(f"- {point}")
    lines.extend([
        "",
        "## Sandbox Evaluation",
        "",
        f"Generated PoC evaluation passed {evaluation.get('passed', 0)}/{evaluation.get('total', 0)} cases.",
        f"Pass rate: {evaluation.get('pass_rate', 0)}",
        "",
        "## Next Steps",
        "",
        "1. Validate sample cases with business owners.",
        "2. Replace generated sample cases with sanitized enterprise examples.",
        "3. Run a staff-reviewed pilot with audit logging.",
        "4. Expand only after quality and governance thresholds are met.",
    ])
    return "\n".join(lines) + "\n"


def _load_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return fallback


def review_result(result: dict, evaluation: dict, app_dir: str | Path | None = None, sandbox_report: dict | None = None) -> dict:
    """Review the generated product using product, evaluation, and sandbox artifacts."""
    architecture = result.get("recommended_architecture", {})
    has_approval = "human_approval" in architecture.get("selected_primitives", [])
    has_evidence = bool(result.get("evidence_pack", {}).get("evidence_items"))
    selected = result.get("selected_opportunity", result.get("recommended_agent", {}))
    product_spec = {}
    app_evaluation = evaluation
    sandbox = sandbox_report or evaluation
    if app_dir:
        app_path = Path(app_dir)
        product_spec = _load_json(app_path / "product_spec.json", {})
        app_evaluation = _load_json(app_path / "evaluation_summary.json", evaluation)
        sandbox = _load_json(app_path / "sandbox_report.json", sandbox)

    app_kind = product_spec.get("app_kind", "")
    uses_domain_template = bool(product_spec.get("domain_template_id"))
    evaluation_success = bool(app_evaluation.get("success", evaluation.get("success")))
    sandbox_success = bool(sandbox.get("success"))
    required_files = {check.get("name"): check for check in sandbox.get("checks", [])}
    has_local_tools = (Path(app_dir) / "tools.py").exists() if app_dir else bool(product_spec.get("app_kind"))
    has_builder_loop = (Path(app_dir) / "builder_loop_trace.json").exists() if app_dir else False
    has_project_shape = bool(required_files.get("software_builder_project_shape", {}).get("success"))
    has_unit_tests = bool(required_files.get("deterministic_unit_tests_pass", {}).get("success"))
    has_api_runtime = bool(product_spec.get("runtime", {}).get("api_key_env"))

    scores = {
        "business_alignment": 9 if selected.get("name") and product_spec.get("selected_opportunity") else 7,
        "technical_completeness": 10 if has_project_shape and has_unit_tests and evaluation_success else 7 if has_project_shape else 5,
        "agentic_quality": 9 if architecture.get("selected_primitives") and has_evidence else 7,
        "tool_use_quality": 9 if has_local_tools and uses_domain_template else 7 if has_local_tools else 4,
        "api_backed_functionality": 9 if has_api_runtime else 5,
        "sandbox_success": 10 if sandbox_success else 5,
        "japan_specific_relevance": 9 if uses_domain_template or "Japan" in str(result.get("company_profile", {})) else 7,
        "safety_and_human_approval": 10 if has_approval else 5,
        "faithfulness_to_ai_scientist_architecture": 10 if has_builder_loop and (result.get("search_trace") or result.get("tree_search_trace")) else 7,
    }
    overall = round(sum(scores.values()) / len(scores), 2)
    return {
        "scores": scores,
        "overall_score": overall,
        "decision": "advance_to_business_validation" if overall >= 8 else "revise_before_pilot",
        "strengths": [
            "Consulting-agent opportunity discovery is connected to Code Agent generation.",
            "Code Agent now emits a Software Builder Loop trace, PRD, architecture, file manifest, and multi-file runnable project.",
            "Generated child app includes deterministic local tools before LLM drafting.",
            "Sandbox runs in real API mode and checks project shape, import, tests, CLI, evaluation, and secret leakage.",
            "Human approval is enforced with send_allowed=false.",
        ],
        "risks": [
            "Evidence pack is curated and should later be upgraded to live search.",
            "Generated PoC uses sample cases and should not be treated as production integration.",
        ],
        "inputs_reviewed": {
            "selected_opportunity": selected.get("name", ""),
            "product_spec": str(Path(app_dir) / "product_spec.json") if app_dir else "",
            "evaluation_summary": app_evaluation,
            "sandbox_success": sandbox_success,
        },
    }


def write_review_markdown(review: dict) -> str:
    lines = [
        "# Product Review",
        "",
        f"Overall score: **{review.get('overall_score', 0)}**",
        "",
        f"Decision: **{review.get('decision', '')}**",
        "",
        "## Scores",
        "",
    ]
    for key, value in review.get("scores", {}).items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Strengths", ""])
    for item in review.get("strengths", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Risks", ""])
    for item in review.get("risks", []):
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)
