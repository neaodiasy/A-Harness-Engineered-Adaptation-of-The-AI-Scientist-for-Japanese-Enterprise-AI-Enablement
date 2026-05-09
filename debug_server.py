"""Local debug UI server for J-Enterprise Agent Scientist.

This server intentionally uses only the Python standard library. It exposes a
small API for inspecting pipeline artifacts and running a general Japanese
enterprise AI enablement consultation flow.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from src.agent_design import design_agent_workflow, render_agent_design_markdown
from src.architecture_composer import compose_architecture
from src.candidate_search import run_candidate_search
from src.domain_pack_builder import build_domain_pack, validate_domain_pack
from src.domain_templates import select_domain_template
from src.evidence_search import build_evidence_pack
from src.feasibility import score_opportunities
from src.harness.json_utils import dump_json, parse_jsonish
from src.harness.llm import ModelRouter
from src.proposal import review_result, write_proposal, write_review_markdown
from src.productization import build_productization_blueprint, render_productization_markdown
from src.prototype_builder import build_prototype
from src.sandbox_eval import run_generated_evaluation
from src.software_factory import build_repair_log
from src.visualization import (
    write_architecture_diagram,
    write_opportunity_score_chart,
    write_solution_pipeline_diagram,
)

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


PROJECT_ROOT = Path(__file__).resolve().parent
FRONTEND_ROOT = PROJECT_ROOT / "frontend"
OUTPUT_ROOT = PROJECT_ROOT / "outputs"
OUTPUT_DIR = OUTPUT_ROOT / "not_started"
GENERATED_APP_DIR = OUTPUT_DIR / "02_generated_app"

ARTIFACTS = {
    "consultation": OUTPUT_DIR / "01_consulting" / "consultation_result.json",
    "llm_consultation_raw": OUTPUT_DIR / "01_consulting" / "llm_consultation_raw.txt",
    "llm_consultation_repair_raw": OUTPUT_DIR / "01_consulting" / "llm_consultation_repair_raw.txt",
    "evidence_pack": OUTPUT_DIR / "01_consulting" / "evidence_pack.json",
    "opportunities": OUTPUT_DIR / "01_consulting" / "opportunities.json",
    "feasibility": OUTPUT_DIR / "01_consulting" / "feasibility_results.json",
    "search_trace": OUTPUT_DIR / "01_consulting" / "search_trace.json",
    "tree_search_trace": OUTPUT_DIR / "01_consulting" / "tree_search_trace.json",
    "selected_opportunity": OUTPUT_DIR / "01_consulting" / "selected_opportunity.json",
    "domain_pack_candidate": OUTPUT_DIR / "01_consulting" / "domain_pack_candidate.json",
    "domain_pack_validation": OUTPUT_DIR / "01_consulting" / "domain_pack_validation.json",
    "product_brief": OUTPUT_DIR / "02_generated_app" / "product_brief.json",
    "product_spec": OUTPUT_DIR / "02_generated_app" / "product_spec.json",
    "product_requirements": OUTPUT_DIR / "02_generated_app" / "product_requirements.json",
    "product_readiness": OUTPUT_DIR / "02_generated_app" / "product_readiness.json",
    "production_readiness_md": OUTPUT_DIR / "02_generated_app" / "production_readiness.md",
    "project_architecture": OUTPUT_DIR / "02_generated_app" / "project_architecture.json",
    "file_manifest": OUTPUT_DIR / "02_generated_app" / "file_manifest.json",
    "builder_loop_trace": OUTPUT_DIR / "02_generated_app" / "builder_loop_trace.json",
    "architecture": OUTPUT_DIR / "02_generated_app" / "architecture.json",
    "primitive_trace": OUTPUT_DIR / "02_generated_app" / "_generator_context" / "primitive_trace.json",
    "agent_design": OUTPUT_DIR / "02_generated_app" / "_generator_context" / "agent_design.json",
    "agent_design_md": OUTPUT_DIR / "02_generated_app" / "_generator_context" / "agent_design.md",
    "productization_blueprint": OUTPUT_DIR / "02_generated_app" / "productization_blueprint.json",
    "productization_blueprint_md": OUTPUT_DIR / "02_generated_app" / "productization_blueprint.md",
    "prototype_manifest": OUTPUT_DIR / "02_generated_app" / "_generator_context" / "prototype_manifest.json",
    "software_blueprint": GENERATED_APP_DIR / "software_blueprint.json",
    "implementation_plan": GENERATED_APP_DIR / "implementation_plan.json",
    "file_plan": GENERATED_APP_DIR / "file_plan.json",
    "generation_trace": GENERATED_APP_DIR / "generation_trace.json",
    "repair_log": GENERATED_APP_DIR / "repair_log.json",
    "sandbox_report": OUTPUT_DIR / "03_sandbox" / "sandbox_report.json",
    "evaluation_results": OUTPUT_DIR / "03_sandbox" / "evaluation_results.json",
    "proposal_report": OUTPUT_DIR / "04_review" / "proposal_report.md",
    "review": OUTPUT_DIR / "04_review" / "review.json",
    "review_md": OUTPUT_DIR / "04_review" / "review.md",
    "opportunity_score_chart": OUTPUT_DIR / "05_visuals" / "opportunity_score_chart.svg",
    "solution_pipeline_diagram": OUTPUT_DIR / "05_visuals" / "solution_pipeline_diagram.svg",
    "architecture_diagram": OUTPUT_DIR / "05_visuals" / "architecture_diagram.svg",
    "final_summary": OUTPUT_DIR / "final_summary.json",
}


def _slugify_name(name: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "_", str(name).lower())
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "generated_enterprise_agent"


def _run_output_dir(run_id: str = "") -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = _slugify_name(run_id) if run_id else "api_run"
    return OUTPUT_ROOT / f"{timestamp}_{suffix}"


def _refresh_output_artifacts(output_dir: Path) -> None:
    global OUTPUT_DIR
    OUTPUT_DIR = output_dir
    ARTIFACTS.update({
        "consultation": output_dir / "01_consulting" / "consultation_result.json",
        "llm_consultation_raw": output_dir / "01_consulting" / "llm_consultation_raw.txt",
        "llm_consultation_repair_raw": output_dir / "01_consulting" / "llm_consultation_repair_raw.txt",
        "evidence_pack": output_dir / "01_consulting" / "evidence_pack.json",
        "opportunities": output_dir / "01_consulting" / "opportunities.json",
        "feasibility": output_dir / "01_consulting" / "feasibility_results.json",
        "search_trace": output_dir / "01_consulting" / "search_trace.json",
        "tree_search_trace": output_dir / "01_consulting" / "tree_search_trace.json",
        "selected_opportunity": output_dir / "01_consulting" / "selected_opportunity.json",
        "domain_pack_candidate": output_dir / "01_consulting" / "domain_pack_candidate.json",
        "domain_pack_validation": output_dir / "01_consulting" / "domain_pack_validation.json",
        "product_brief": output_dir / "02_generated_app" / "product_brief.json",
        "product_spec": output_dir / "02_generated_app" / "product_spec.json",
        "product_requirements": output_dir / "02_generated_app" / "product_requirements.json",
        "product_readiness": output_dir / "02_generated_app" / "product_readiness.json",
        "production_readiness_md": output_dir / "02_generated_app" / "production_readiness.md",
        "project_architecture": output_dir / "02_generated_app" / "project_architecture.json",
        "file_manifest": output_dir / "02_generated_app" / "file_manifest.json",
        "builder_loop_trace": output_dir / "02_generated_app" / "builder_loop_trace.json",
        "architecture": output_dir / "02_generated_app" / "architecture.json",
        "primitive_trace": output_dir / "02_generated_app" / "_generator_context" / "primitive_trace.json",
        "agent_design": output_dir / "02_generated_app" / "_generator_context" / "agent_design.json",
        "agent_design_md": output_dir / "02_generated_app" / "_generator_context" / "agent_design.md",
        "productization_blueprint": output_dir / "02_generated_app" / "productization_blueprint.json",
        "productization_blueprint_md": output_dir / "02_generated_app" / "productization_blueprint.md",
        "prototype_manifest": output_dir / "02_generated_app" / "_generator_context" / "prototype_manifest.json",
        "sandbox_report": output_dir / "03_sandbox" / "sandbox_report.json",
        "evaluation_results": output_dir / "03_sandbox" / "evaluation_results.json",
        "proposal_report": output_dir / "04_review" / "proposal_report.md",
        "review": output_dir / "04_review" / "review.json",
        "review_md": output_dir / "04_review" / "review.md",
        "opportunity_score_chart": output_dir / "05_visuals" / "opportunity_score_chart.svg",
        "solution_pipeline_diagram": output_dir / "05_visuals" / "solution_pipeline_diagram.svg",
        "architecture_diagram": output_dir / "05_visuals" / "architecture_diagram.svg",
        "final_summary": output_dir / "final_summary.json",
    })


def _refresh_generated_artifacts(app_dir: Path) -> None:
    global GENERATED_APP_DIR
    GENERATED_APP_DIR = app_dir
    ARTIFACTS.update({
        "software_blueprint": app_dir / "software_blueprint.json",
        "implementation_plan": app_dir / "implementation_plan.json",
        "file_plan": app_dir / "file_plan.json",
        "generation_trace": app_dir / "generation_trace.json",
        "repair_log": app_dir / "repair_log.json",
        "product_spec": app_dir / "product_spec.json",
        "product_requirements": app_dir / "product_requirements.json",
        "product_readiness": app_dir / "product_readiness.json",
        "production_readiness_md": app_dir / "production_readiness.md",
        "project_architecture": app_dir / "project_architecture.json",
        "file_manifest": app_dir / "file_manifest.json",
        "builder_loop_trace": app_dir / "builder_loop_trace.json",
        "productization_blueprint": app_dir / "productization_blueprint.json",
        "productization_blueprint_md": app_dir / "productization_blueprint.md",
    })


def _write_case_outputs(app_dir: Path, sandbox_dir: Path) -> Path:
    """Extract final case outputs into a small reviewer-friendly file."""
    results_path = app_dir / "evaluation_results.json"
    case_outputs = []
    if results_path.exists():
        try:
            for item in json.loads(results_path.read_text(encoding="utf-8")):
                case_outputs.append({
                    "case_id": item.get("case_id"),
                    "passed": item.get("passed"),
                    "output": item.get("output"),
                    "error": item.get("error"),
                })
        except json.JSONDecodeError:
            case_outputs.append({"error": "evaluation_results.json was not valid JSON"})
    output_path = sandbox_dir / "case_outputs.json"
    dump_json(output_path, case_outputs)
    return output_path


def _evidence_source_documents(evidence_pack: dict) -> list[str]:
    """Compress evidence items into source notes for runtime domain-pack drafting."""
    docs: list[str] = []
    for item in evidence_pack.get("evidence_items", [])[:8]:
        docs.append(
            "\n".join(
                str(value)
                for value in (
                    item.get("title", ""),
                    item.get("summary", ""),
                    item.get("source", ""),
                    item.get("url", ""),
                )
                if value
            )
        )
    return docs


def _prepare_runtime_domain_pack(
    profile: dict,
    agent_design: dict,
    architecture: dict,
    evidence_pack: dict,
    consulting_dir: Path,
) -> dict[str, object]:
    """Select an existing pack or auto-build a runtime pack for this run."""
    existing_pack = select_domain_template(profile, agent_design, architecture)
    if existing_pack:
        pack = dict(existing_pack)
        pack["autobuilder"] = {
            "status": "accepted_existing_template",
            "human_review_required": False,
            "runtime_selection": True,
        }
        result = {
            "mode": "existing_domain_pack",
            "domain_pack": pack,
            "validation": {"valid": True, "errors": [], "warnings": [], "human_review_required": False},
        }
    else:
        draft_pack = build_domain_pack(profile, _evidence_source_documents(evidence_pack))
        result = {
            "mode": "auto_built_runtime_domain_pack",
            "domain_pack": draft_pack,
            "validation": validate_domain_pack(draft_pack),
        }
    dump_json(consulting_dir / "domain_pack_candidate.json", result["domain_pack"])
    dump_json(consulting_dir / "domain_pack_validation.json", result["validation"])
    return result


def _write_run_index(
    output_dir: Path,
    app_dir: Path,
    case_outputs_path: Path,
) -> Path:
    index_path = output_dir / "00_README.md"
    index_path.write_text(
        f"""# Run Output Index

This folder contains one complete J-Enterprise Agent Scientist run.

## Start Here

- Final summary: `{output_dir / "final_summary.json"}`
- Generated app code: `{app_dir}`
- Main app code: `{app_dir / "app.py"}`
- Local tools: `{app_dir / "tools.py"}`
- Evaluator: `{app_dir / "evaluation.py"}`
- Final agent case outputs: `{case_outputs_path}`
- Full sandbox report: `{output_dir / "03_sandbox" / "sandbox_report.json"}`
- Product review: `{output_dir / "04_review" / "review.md"}`

## Consulting Agent

- Business analysis: `{output_dir / "01_consulting" / "business_analysis.json"}`
- Opportunities: `{output_dir / "01_consulting" / "opportunities.json"}`
- Selected opportunity: `{output_dir / "01_consulting" / "selected_opportunity.json"}`
- Tree search trace: `{output_dir / "01_consulting" / "tree_search_trace.json"}`
- Raw DeepSeek consultation: `{output_dir / "01_consulting" / "llm_consultation_raw.txt"}`

## Code Agent

- Generated app folder: `{app_dir}`
- Product requirements: `{app_dir / "product_requirements.json"}`
- Productization blueprint: `{app_dir / "productization_blueprint.md"}`
- Production readiness: `{app_dir / "production_readiness.md"}`
- Project architecture: `{app_dir / "project_architecture.json"}`
- File manifest: `{app_dir / "file_manifest.json"}`
- Builder loop trace: `{app_dir / "builder_loop_trace.json"}`
- Product brief: `{app_dir / "product_brief.json"}`
- Product spec: `{app_dir / "product_spec.json"}`
- Backend code: `{app_dir / "backend"}`
- Frontend code: `{app_dir / "frontend"}`
- Local data: `{app_dir / "data"}`
- Deterministic tests: `{app_dir / "tests"}`
- Prototype manifest: `{app_dir / "_generator_context" / "prototype_manifest.json"}`

## Run Generated Product

```bash
cd "{app_dir}"
python3 app.py --cli
python3 -m unittest discover -s tests
python3 evaluation.py
```

## Visuals

- Opportunity score chart: `{output_dir / "05_visuals" / "opportunity_score_chart.svg"}`
- Pipeline diagram: `{output_dir / "05_visuals" / "solution_pipeline_diagram.svg"}`
- Architecture diagram: `{output_dir / "05_visuals" / "architecture_diagram.svg"}`
""",
        encoding="utf-8",
    )
    return index_path


def run_pipeline(profile: dict, run_id: str = "") -> tuple[dict, dict]:
    """Run the full enterprise scientist pipeline and persist artifacts."""
    run_output_dir = _run_output_dir(run_id)
    _refresh_output_artifacts(run_output_dir)
    consulting_dir = OUTPUT_DIR / "01_consulting"
    code_agent_dir = OUTPUT_DIR / "02_generated_app"
    generator_context_dir = code_agent_dir / "_generator_context"
    sandbox_dir = OUTPUT_DIR / "03_sandbox"
    review_dir = OUTPUT_DIR / "04_review"
    visuals_dir = OUTPUT_DIR / "05_visuals"
    for directory in (consulting_dir, code_agent_dir, generator_context_dir, sandbox_dir, review_dir, visuals_dir):
        directory.mkdir(parents=True, exist_ok=True)

    evidence_pack = build_evidence_pack(profile)
    result = _llm_consult(profile, evidence_pack)
    if run_id:
        result["run_id"] = run_id
    result.setdefault("evidence_pack", evidence_pack)
    selected_opportunity = result.get("selected_opportunity", result.get("recommended_agent", {}))
    app_dir = code_agent_dir
    _refresh_generated_artifacts(app_dir)

    dump_json(consulting_dir / "consultation_result.json", result)
    dump_json(consulting_dir / "evidence_pack.json", evidence_pack)
    dump_json(consulting_dir / "business_analysis.json", result.get("business_analysis", {}))
    dump_json(consulting_dir / "opportunities.json", result.get("opportunities", []))
    dump_json(consulting_dir / "feasibility_results.json", result.get("feasibility_results", []))
    dump_json(consulting_dir / "search_trace.json", result.get("search_trace", {}))
    dump_json(consulting_dir / "tree_search_trace.json", result.get("tree_search_trace", result.get("search_trace", {})))
    dump_json(consulting_dir / "selected_opportunity.json", selected_opportunity)
    architecture = result.get("recommended_architecture", {})
    dump_json(generator_context_dir / "architecture.json", architecture)
    dump_json(generator_context_dir / "primitive_trace.json", architecture.get("composition_trace", []))
    agent_design = result.get("agent_design", {})
    dump_json(generator_context_dir / "agent_design.json", agent_design)
    (generator_context_dir / "agent_design.md").write_text(render_agent_design_markdown(agent_design), encoding="utf-8")
    (generator_context_dir / "agent_architecture.md").write_text(render_agent_design_markdown(agent_design), encoding="utf-8")

    domain_pack_result = _prepare_runtime_domain_pack(profile, agent_design, architecture, evidence_pack, consulting_dir)
    productization_blueprint = build_productization_blueprint(profile, agent_design, architecture, evidence_pack)
    productization_blueprint["domain_pack_mode"] = domain_pack_result["mode"]
    productization_blueprint["runtime_domain_pack"] = domain_pack_result["domain_pack"]
    productization_blueprint["domain_pack_validation"] = domain_pack_result["validation"]
    dump_json(code_agent_dir / "productization_blueprint.json", productization_blueprint)
    (code_agent_dir / "productization_blueprint.md").write_text(
        render_productization_markdown(productization_blueprint),
        encoding="utf-8",
    )
    dump_json(generator_context_dir / "productization_blueprint.json", productization_blueprint)

    prototype_manifest = build_prototype(app_dir, agent_design, architecture, productization_blueprint)
    dump_json(generator_context_dir / "prototype_manifest.json", prototype_manifest)
    product_spec = prototype_manifest.get("product_spec", {})
    product_brief = prototype_manifest.get("product_brief", {})
    dump_json(code_agent_dir / "product_spec.json", product_spec)
    dump_json(code_agent_dir / "product_brief.json", product_brief)

    sandbox_report = run_generated_evaluation(app_dir)
    dump_json(sandbox_dir / "sandbox_report.json", sandbox_report)
    evaluation_summary = sandbox_report.get("evaluation_summary", {})
    evaluation_results = {
        "success": bool(evaluation_summary.get("success")),
        "summary": evaluation_summary,
        "cases": sandbox_report.get("evaluation_results", []),
    }
    dump_json(sandbox_dir / "evaluation_results.json", evaluation_results)
    dump_json(app_dir / "repair_log.json", build_repair_log(sandbox_report))
    case_outputs_path = _write_case_outputs(app_dir, sandbox_dir)
    dump_json(generator_context_dir / "prototype_manifest.json", prototype_manifest)

    proposal = write_proposal(result, sandbox_report)
    (review_dir / "proposal_report.md").write_text(proposal, encoding="utf-8")
    review = review_result(result, evaluation_summary, app_dir=app_dir, sandbox_report=sandbox_report)
    dump_json(review_dir / "review.json", review)
    (review_dir / "review.md").write_text(write_review_markdown(review), encoding="utf-8")

    result["prototype_manifest"] = prototype_manifest
    result["productization_blueprint"] = productization_blueprint
    result["domain_pack_mode"] = domain_pack_result["mode"]
    result["domain_pack_validation"] = domain_pack_result["validation"]
    result["generated_app"] = str(app_dir.resolve())
    result["sandbox_report"] = sandbox_report
    result["evaluation_results"] = evaluation_results
    result["proposal_report"] = proposal
    result["review"] = review

    score_chart = write_opportunity_score_chart(
        result.get("opportunities", []),
        result.get("feasibility_results", []),
        visuals_dir / "opportunity_score_chart.svg",
        selected_name=selected_opportunity.get("name", ""),
        profile_label=profile.get("company_name") or profile.get("industry") or profile.get("main_business", ""),
    )
    pipeline_diagram = write_solution_pipeline_diagram(result, visuals_dir / "solution_pipeline_diagram.svg")
    diagram_path = write_architecture_diagram(result, visuals_dir / "architecture_diagram.svg")
    result["opportunity_score_chart"] = str(score_chart)
    result["solution_pipeline_diagram"] = str(pipeline_diagram)
    result["architecture_diagram"] = str(diagram_path)

    final_summary = {
        "status": "complete",
        "mode": result.get("mode", "real_deepseek_api"),
        "selected_opportunity": selected_opportunity.get("name", ""),
        "generated_app": str(app_dir.resolve()),
        "evaluation_success": bool(evaluation_summary.get("success")),
        "sandbox_success": bool(sandbox_report.get("success")),
        "review_score": review.get("overall_score"),
        "outputs": str(OUTPUT_DIR.resolve()),
        "output_sections": {
            "consulting": str(consulting_dir.resolve()),
            "generated_app": str(code_agent_dir.resolve()),
            "sandbox": str(sandbox_dir.resolve()),
            "review": str(review_dir.resolve()),
            "visuals": str(visuals_dir.resolve()),
        },
    }
    dump_json(OUTPUT_DIR / "final_summary.json", final_summary)
    _write_run_index(OUTPUT_DIR, app_dir, case_outputs_path)
    result["final_summary"] = final_summary
    dump_json(consulting_dir / "consultation_result.json", result)
    response_result = {
        "run_id": result.get("run_id", ""),
        "mode": result.get("mode", "real_deepseek_api"),
        "company_profile": result.get("company_profile", {}),
        "opportunities": result.get("opportunities", []),
        "feasibility_results": result.get("feasibility_results", []),
        "search_trace": result.get("search_trace", {}),
        "tree_search_trace": result.get("tree_search_trace", result.get("search_trace", {})),
        "selected_opportunity": result.get("selected_opportunity", result.get("recommended_agent", {})),
        "recommended_agent": result.get("recommended_agent", result.get("selected_opportunity", {})),
        "recommended_architecture": result.get("recommended_architecture", {}),
        "agent_design": result.get("agent_design", {}),
        "productization_blueprint": result.get("productization_blueprint", {}),
        "roadmap": result.get("roadmap", []),
        "prototype_manifest": prototype_manifest,
        "sandbox_report": sandbox_report,
        "evaluation_results": evaluation_results,
        "review": review,
        "final_summary": final_summary,
    }
    return result, response_result

JAPAN_AI_TRENDS = [
    {
        "name": "Labor-saving and productivity improvement",
        "why_it_matters": "Japan's labor shortage makes AI-enabled workflow redesign more valuable than isolated chatbots.",
        "source": "OECD 2025; Digital Agency Government AI initiatives",
    },
    {
        "name": "Knowledge retrieval over fragmented internal documents",
        "why_it_matters": "Many Japanese enterprises have valuable rules, manuals, and tacit procedures trapped in PDFs, shared drives, and legacy systems.",
        "source": "IPA and METI DX guidance",
    },
    {
        "name": "Human-in-the-loop governance for regulated workflows",
        "why_it_matters": "Financial, healthcare, insurance, and public-sector workflows need auditability, approval gates, and risk controls.",
        "source": "Bank of Japan and FSA AI governance discussions",
    },
    {
        "name": "AI literacy and standardized prompt/workflow templates",
        "why_it_matters": "Enterprise adoption often stalls when only individual power users benefit; reusable templates make adoption organization-wide.",
        "source": "METI generative AI human resources guidance",
    },
]

OPPORTUNITY_PATTERNS = [
    {
        "name": "Automated Preference-Based Area Recommendation",
        "fit_terms": [
            "real_estate",
            "real estate",
            "property",
            "housing",
            "home",
            "area",
            "neighborhood",
            "budget",
            "commute",
            "school",
            "不動産",
            "住宅",
            "物件",
            "地域",
            "通勤",
            "学校",
        ],
        "target_workflow": "Preference intake, area comparison, neighborhood ranking, and consultant approval packet preparation",
        "capability": "Analyze customer preferences, rank suitable areas using local data, draft Japanese recommendations, and prepare a human approval packet.",
        "value": "Reduce manual neighborhood comparison time while making recommendation reasoning consistent across consultants.",
        "risk": "Area suitability, hazards, legal, financial, and property-level facts must be reviewed by a human consultant.",
    },
    {
        "name": "Internal Knowledge Navigation Agent",
        "fit_terms": ["manual", "knowledge", "faq", "規程", "マニュアル", "問い合わせ", "ナレッジ"],
        "target_workflow": "Internal search, rule lookup, and answer drafting",
        "capability": "Retrieve trusted internal knowledge, cite sources, and draft staff-facing answers.",
        "value": "Reduce search time and make answers more consistent across teams.",
        "risk": "Outdated or conflicting documents can lead to incorrect guidance.",
    },
    {
        "name": "Customer Response Drafting Agent",
        "fit_terms": ["customer", "support", "email", "問い合わせ", "顧客", "コールセンター", "営業"],
        "target_workflow": "Customer inquiry triage and response drafting",
        "capability": "Classify inquiries, retrieve evidence, draft cautious replies, and route risky cases for approval.",
        "value": "Shorten first-draft time while preserving human ownership of customer-facing communication.",
        "risk": "Poorly reviewed drafts could create reputational or compliance risk.",
    },
    {
        "name": "Back-office Document Processing Agent",
        "fit_terms": ["invoice", "contract", "document", "pdf", "申請", "請求書", "契約", "経理", "人事"],
        "target_workflow": "Document intake, extraction, checklisting, and routing",
        "capability": "Extract key fields, compare against rules, flag missing items, and prepare approval packets.",
        "value": "Reduce repetitive clerical work and improve traceability.",
        "risk": "OCR or extraction errors require validation before downstream use.",
    },
    {
        "name": "Sales and Proposal Enablement Agent",
        "fit_terms": ["sales", "proposal", "提案", "営業", "見積", "競合", "顧客分析"],
        "target_workflow": "Sales research, proposal drafting, and competitive preparation",
        "capability": "Summarize customer context, retrieve past proposals, draft tailored materials, and surface competitive risks.",
        "value": "Improve proposal speed and quality without replacing account-owner judgment.",
        "risk": "Confidential data leakage and inaccurate claims need strong guardrails.",
    },
    {
        "name": "Operational Forecasting and Exception Agent",
        "fit_terms": ["forecast", "inventory", "shift", "logistics", "需要", "在庫", "配送", "人員", "予測"],
        "target_workflow": "Planning, resource allocation, and exception detection",
        "capability": "Forecast demand or workload, explain drivers, and flag exceptions for managers.",
        "value": "Improve planning under labor constraints and reduce avoidable overtime.",
        "risk": "Forecast uncertainty must be visible so managers do not over-trust the system.",
    },
    {
        "name": "Compliance and Approval Review Agent",
        "fit_terms": ["compliance", "risk", "audit", "承認", "稟議", "監査", "法務", "金融", "医療"],
        "target_workflow": "Policy review, approval preparation, and audit evidence collection",
        "capability": "Check drafts or requests against policies, prepare evidence, and enforce approval gates.",
        "value": "Reduce review burden and strengthen governance in regulated processes.",
        "risk": "False negatives are high impact; use as decision support only.",
    },
]


def _read_json(path: Path) -> object | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _load_model_config() -> dict:
    defaults = {
        "model": {
            "provider": "deepseek",
            "base_url": "https://api.deepseek.com",
            "api_key_env": "DEEPSEEK_API_KEY",
            "cheap_model": "deepseek-v4-pro",
            "strong_model": "deepseek-v4-pro",
            "temperature": 0.1,
            "max_tokens": 4096,
            "timeout_seconds": 120,
            "retries": 2,
            "stage_models": {"consultation": "strong"},
        },
    }
    config_path = PROJECT_ROOT / "config.yaml"
    if yaml is None or not config_path.exists():
        return defaults
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    defaults.update(config)
    return defaults


def _text_blob(profile: dict) -> str:
    return " ".join(str(value) for value in profile.values()).lower()


def _score_opportunity(pattern: dict, profile: dict) -> float:
    blob = _text_blob(profile)
    hits = sum(1 for term in pattern["fit_terms"] if term.lower() in blob)
    baseline = 5.5 + min(hits, 4) * 0.9
    name = pattern["name"].lower()
    if any(term in blob for term in ["bank", "financial", "finance", "金融", "銀行", "loan", "lending"]):
        if "compliance" in name or "approval" in name:
            baseline += 2.0
        if "document" in name or "knowledge" in name:
            baseline += 0.8
    if any(term in blob for term in ["manufacturing", "factory", "quality", "engineer", "製造", "工場", "品質"]):
        if "knowledge" in name:
            baseline += 1.2
        if "document" in name or "operational" in name:
            baseline += 0.6
    if any(term in blob for term in ["retail", "store", "inventory", "小売", "店舗", "在庫"]):
        if "customer" in name or "operational" in name:
            baseline += 1.2
    if any(term in blob for term in ["logistics", "warehouse", "route", "delivery", "物流", "倉庫", "配送"]):
        if "operational" in name:
            baseline += 1.8
        if "customer" in name:
            baseline += 0.6
    if "regulated" in blob or "保険" in blob or "医療" in blob:
        baseline += 0.4 if "approval" in name or "customer" in name else 0
    return round(min(baseline, 9.3), 1)


def _evidence_ids(evidence_pack: dict, support_key: str | None = None) -> list[str]:
    items = evidence_pack.get("evidence_items", [])
    if not support_key:
        return [item["id"] for item in items[:2]]
    matched = [
        item["id"]
        for item in items
        if support_key in item.get("supports", ()) or support_key in item.get("themes", ())
    ]
    return matched[:3] or [item["id"] for item in items[:2]]


def _as_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if value in (None, ""):
        return []
    return [str(value)]


def _build_business_analysis(profile: dict) -> dict:
    pain_points = _as_list(profile.get("pain_points"))
    constraints = _as_list(profile.get("constraints"))
    workflows = [
        str(profile.get("current_workflow", "")).strip(),
        str(profile.get("main_business", "")).strip(),
    ]
    workflows = [item for item in workflows if item]
    return {
        "company_name": profile.get("company_name", "Enterprise profile"),
        "industry": profile.get("industry", "general Japanese enterprise"),
        "main_business": profile.get("main_business", ""),
        "workflows": workflows,
        "pain_points": pain_points,
        "available_data": _as_list(profile.get("available_data")),
        "constraints": constraints,
        "ai_objective": profile.get("ai_objective", profile.get("business_goal", "")),
        "consulting_agent_summary": (
            "The consulting agent looks for bounded AI enablement opportunities where local evidence, "
            "deterministic tools, LLM drafting, and human approval can improve a real workflow without full automation."
        ),
    }


def _opportunity_from_pattern(pattern: dict, profile: dict, evidence_pack: dict) -> dict:
    score = _score_opportunity(pattern, profile)
    return {
        "name": pattern["name"],
        "score": score,
        "target_workflow": pattern["target_workflow"],
        "proposed_ai_capability": pattern["capability"],
        "expected_business_value": pattern["value"],
        "key_risk": pattern["risk"],
        "human_approval_requirement": "Human review is required before customer-facing, regulated, financial, legal, safety, or irreversible use.",
        "required_data": profile.get("available_data", "Representative cases, internal manuals, approved examples, and workflow constraints."),
        "japan_enterprise_fit": "Fits Japan-style careful rollout because it preserves human approval, auditability, and kaizen-friendly workflow adoption.",
        "evidence_support": _evidence_ids(evidence_pack, "business_value"),
        "why_now": "Labor constraints, generative AI maturity, and growing DX expectations make bounded workflow enablement practical now.",
    }


def _deterministic_opportunities(profile: dict, evidence_pack: dict) -> list[dict]:
    opportunities = [
        _opportunity_from_pattern(pattern, profile, evidence_pack)
        for pattern in OPPORTUNITY_PATTERNS
    ]
    opportunities.sort(key=lambda item: item.get("score", 0), reverse=True)
    return opportunities[:5]


def _finalize_consultation(parsed: dict, profile: dict, evidence_pack: dict, mode: str) -> dict:
    parsed = dict(parsed)
    parsed["mode"] = mode
    parsed.setdefault("company_profile", profile)
    parsed.setdefault("business_analysis", _build_business_analysis(profile))
    parsed.setdefault("evidence_pack", evidence_pack)
    parsed.setdefault("market_context", JAPAN_AI_TRENDS)

    opportunities = parsed.get("opportunities", [])
    if not isinstance(opportunities, list):
        opportunities = []
    if len(opportunities) < 5:
        raise RuntimeError("DeepSeek consultation returned fewer than 5 opportunities.")
    parsed["opportunities"] = opportunities[:5]

    feasibility = score_opportunities(profile, parsed["opportunities"])
    parsed["feasibility_results"] = feasibility
    search_trace = run_candidate_search(parsed["opportunities"], feasibility)
    parsed["search_trace"] = search_trace
    parsed["tree_search_trace"] = search_trace
    parsed["selected_opportunity"] = search_trace["selected_opportunity"]
    parsed["recommended_agent"] = search_trace["selected_opportunity"]
    parsed["recommended_architecture"] = compose_architecture(profile, parsed["recommended_agent"])
    parsed["agent_design"] = design_agent_workflow(
        profile,
        parsed["recommended_agent"],
        parsed["recommended_architecture"],
        evidence_pack,
    )
    parsed.setdefault("roadmap", [
        "Generate and sandbox a local child agent product.",
        "Review sample outputs with business owners.",
        "Replace sample cases with sanitized real workflow cases.",
        "Pilot with human approval and audit logging before integration.",
    ])
    parsed.setdefault("ai_scientist_mapping", {
        "template": "company profile",
        "idea_generation": "enterprise AI enablement opportunities",
        "feasibility_check": "opportunity scoring",
        "tree_search": "LATS-lite opportunity selection",
        "code_generation": "Code Agent generated API-backed child product",
        "experiment_execution": "real API sandbox evaluation",
        "result_analysis": "evaluation_summary.json",
        "automated_review": "review.json and review.md",
    })
    return parsed


def _llm_consult(profile: dict, evidence_pack: dict) -> dict:
    if not os.environ.get("DEEPSEEK_API_KEY"):
        raise RuntimeError("DEEPSEEK_API_KEY is required for strict API mode.")
    router = ModelRouter.from_config(_load_model_config())
    prompt = f"""You are J-Enterprise Agent Scientist, a general AI enablement consultant for Japanese enterprises.
Analyze this company profile and produce one valid JSON object only. Do not use Markdown. Do not include commentary.

Company profile:
{json.dumps(profile, ensure_ascii=False, indent=2)}

Evidence pack:
{json.dumps(evidence_pack, ensure_ascii=False, indent=2)}

Use current Japanese enterprise AI themes:
- labor shortage and productivity improvement
- internal knowledge retrieval and workflow redesign
- regulated workflow governance and human approval
- DX, AI literacy, and kaizen-style rollout

Return JSON with keys:
company_profile, evidence_pack, market_context, opportunities, recommended_agent, feasibility_check,
agent_workflow, roadmap, ai_scientist_mapping.
Generate exactly 5 opportunities. Each opportunity must include name, score, target_workflow, proposed_ai_capability,
expected_business_value, key_risk, human_approval_requirement, required_data,
japan_enterprise_fit, evidence_support, why_now.
Keep each string concise. Do not assume one fixed industry. Do not make final legal, medical, financial, HR, or customer-facing decisions automatic."""
    client = router.for_stage("consultation")
    raw = client.complete(prompt, json_mode=True)
    raw_path = OUTPUT_DIR / "01_consulting" / "llm_consultation_raw.txt"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(raw, encoding="utf-8")
    parsed = parse_jsonish(raw, fallback=None)
    if not isinstance(parsed, dict) or "opportunities" not in parsed or "recommended_agent" not in parsed:
        repair_prompt = f"""Repair the following model output into one valid JSON object only.
Do not add Markdown or explanations.
Required top-level keys:
company_profile, evidence_pack, market_context, opportunities, recommended_agent, feasibility_check,
agent_workflow, roadmap, ai_scientist_mapping.
The repaired JSON must preserve the enterprise analysis content where possible.

Original model output:
{raw}
        """
        repaired = client.complete(repair_prompt, json_mode=True)
        (OUTPUT_DIR / "01_consulting" / "llm_consultation_repair_raw.txt").write_text(repaired, encoding="utf-8")
        parsed = parse_jsonish(repaired, fallback=None)
    if isinstance(parsed, dict) and "opportunities" in parsed and "recommended_agent" in parsed:
        return _finalize_consultation(parsed, profile, evidence_pack, "real_deepseek_api")
    raise RuntimeError("DeepSeek returned invalid consultation JSON after repair.")


class DebugHandler(SimpleHTTPRequestHandler):
    """HTTP handler for static files and local harness APIs."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, directory=str(FRONTEND_ROOT), **kwargs)

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        print(f"[debug_ui] {self.address_string()} - {format % args}")

    def _send_json(self, payload: object, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error_json(self, message: str, status: int = 400) -> None:
        self._send_json({"error": message}, status)

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw or "{}")

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/status":
            self._send_json({
                "config": _read_text(PROJECT_ROOT / "config.yaml"),
                "has_deepseek_key": bool(os.environ.get("DEEPSEEK_API_KEY")),
                "artifacts": {name: path.exists() for name, path in ARTIFACTS.items()},
            })
            return
        if parsed.path == "/api/artifact":
            params = parse_qs(parsed.query)
            name = params.get("name", [""])[0]
            path = ARTIFACTS.get(name)
            if path is None:
                self._send_error_json(f"Unknown artifact: {name}", 404)
                return
            if path.suffix == ".json":
                self._send_json({"name": name, "type": "json", "content": _read_json(path)})
            elif path.suffix == ".svg":
                self._send_json({"name": name, "type": "svg", "content": _read_text(path)})
            else:
                self._send_json({"name": name, "type": "text", "content": _read_text(path)})
            return
        if parsed.path == "/api/consult_start":
            params = parse_qs(parsed.query)
            body = {key: values[0] if values else "" for key, values in params.items()}
            profile = {
                "company_description": str(body.get("company_description", "")).strip(),
                "industry": str(body.get("industry", "")).strip(),
                "main_business": str(body.get("main_business", "")).strip(),
                "ai_objective": str(body.get("ai_objective", "")).strip(),
                "pain_points": str(body.get("pain_points", "")).strip(),
                "available_data": str(body.get("available_data", "")).strip(),
                "constraints": str(body.get("constraints", "")).strip(),
            }
            if not profile["company_description"] and not profile["main_business"]:
                self._send_error_json("Company description or main business is required.")
                return
            _, response_result = run_pipeline(profile, str(body.get("_run_id", "")).strip())
            self._send_json(response_result)
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/consult":
            body = self._read_body()
            run_id = str(body.get("_run_id", "")).strip()
            profile = {
                "company_description": str(body.get("company_description", "")).strip(),
                "industry": str(body.get("industry", "")).strip(),
                "main_business": str(body.get("main_business", "")).strip(),
                "ai_objective": str(body.get("ai_objective", "")).strip(),
                "pain_points": str(body.get("pain_points", "")).strip(),
                "available_data": str(body.get("available_data", "")).strip(),
                "constraints": str(body.get("constraints", "")).strip(),
            }
            if not profile["company_description"] and not profile["main_business"]:
                self._send_error_json("Company description or main business is required.")
                return
            _, response_result = run_pipeline(profile, run_id)
            self._send_json(response_result)
            return
        self._send_error_json(f"Unknown endpoint: {parsed.path}", 404)


def main() -> None:
    port = int(os.environ.get("JENTERPRISE_DEBUG_PORT", "8765"))
    for candidate_port in range(port, port + 20):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", candidate_port), DebugHandler)
            print(f"J-Enterprise Agent Scientist debug UI: http://127.0.0.1:{candidate_port}")
            server.serve_forever()
            return
        except OSError as error:
            if getattr(error, "errno", None) != 48:
                raise
            print(f"Port {candidate_port} is already in use; trying {candidate_port + 1}...")
    raise OSError(f"No available local port found in range {port}-{port + 19}")


if __name__ == "__main__":
    main()
