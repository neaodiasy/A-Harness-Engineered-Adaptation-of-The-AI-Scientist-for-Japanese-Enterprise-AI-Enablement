"""Software Builder Loop for generated enterprise agent products.

The original AI Scientist plans, writes, runs, reviews, and repairs experiment
code. This module applies the same shape to enterprise software generation:
an opportunity becomes a product requirement document, project architecture,
file manifest, implementation plan, runnable app, sandbox report, and repair
trace.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BuilderLoopStage:
    """One auditable software construction stage."""

    name: str
    purpose: str
    outputs: list[str]
    ai_scientist_analogy: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "stage": self.name,
            "purpose": self.purpose,
            "outputs": self.outputs,
            "ai_scientist_analogy": self.ai_scientist_analogy,
        }


BUILDER_LOOP_STAGES: tuple[BuilderLoopStage, ...] = (
    BuilderLoopStage(
        "productization_blueprint",
        "Translate the selected opportunity into an enterprise software product archetype, role model, workbench layout, state model, and UI quality contract.",
        ["productization_blueprint.json", "productization_blueprint.md"],
        "experiment environment design / template shaping",
    ),
    BuilderLoopStage(
        "product_requirements",
        "Turn the selected enterprise opportunity into users, jobs-to-be-done, workflows, acceptance criteria, and safety boundaries.",
        ["product_requirements.json", "product_brief.json"],
        "idea refinement / experiment objective",
    ),
    BuilderLoopStage(
        "project_architecture",
        "Design a runnable product with backend modules, local tools, data files, frontend surface, tests, evaluation, and review artifacts.",
        ["project_architecture.json", "architecture.md"],
        "experiment design / method architecture",
    ),
    BuilderLoopStage(
        "file_manifest",
        "Define every generated source, data, test, evaluation, and documentation file before writing code.",
        ["file_manifest.json", "file_plan.json"],
        "code generation plan",
    ),
    BuilderLoopStage(
        "code_generation",
        "Generate the full project package, not a single demo script: API server, agent runtime, deterministic tools, data, UI, tests, and docs.",
        ["app.py", "backend/", "frontend/", "data/", "tests/", "evaluation.py"],
        "LLM-written experiment code",
    ),
    BuilderLoopStage(
        "sandbox_execution",
        "Compile, import, run CLI, run deterministic tests, run API-backed evaluation, and collect generated case outputs.",
        ["sandbox_report.json", "evaluation_results.json", "case_outputs.json"],
        "experiment execution",
    ),
    BuilderLoopStage(
        "repair_loop",
        "Inspect failures and record the next patch/regeneration action until the generated project is runnable.",
        ["repair_log.json", "builder_loop_trace.json"],
        "debug, refine, and iterate",
    ),
    BuilderLoopStage(
        "product_review",
        "Score the generated product for business alignment, technical completeness, tool use, API behavior, Japan fit, and governance.",
        ["review.json", "review.md"],
        "automated review",
    ),
)


def _opportunity(agent_design: dict) -> dict:
    return agent_design.get("selected_opportunity", {}) or {}


def _context(agent_design: dict) -> dict:
    return agent_design.get("enterprise_context", {}) or {}


def build_product_requirements(agent_design: dict, product_spec: dict) -> dict:
    """Create a compact PRD for the generated child product."""
    opportunity = _opportunity(agent_design)
    context = _context(agent_design)
    app_kind = product_spec.get("app_kind", "enterprise_agent_product")
    domain_template = product_spec.get("domain_template", {}) if isinstance(product_spec.get("domain_template"), dict) else {}
    if product_spec.get("domain_template_id") and product_spec.get("domain_template_id") != "generic_enterprise":
        candidate_label = product_spec.get("candidate_collection_label", "domain candidates")
        item_label = product_spec.get("item_collection_label", "related items")
        user_roles = [
            "Business consultant",
            "Manager / reviewer",
            "Customer-facing or operational advisor",
        ]
        core_workflows = [
            "Capture user preferences, constraints, and business context.",
            f"Rank local {candidate_label} and {item_label} with deterministic tools.",
            "Ask DeepSeek to draft a Japanese recommendation using only local tool results and evidence.",
            "Block external sending until a human reviewer approves the packet.",
        ]
        examples = [str(item) for item in domain_template.get("candidate_examples", [])[:4]]
        acceptance_criteria = [
            "The app exposes a real CLI and local web UI.",
            "The backend includes separate agent, tool, data, guardrail, and API modules.",
            "Outputs include local_tool_results and ranked_area_candidates.",
            "Recommendations use concrete candidate names from the selected domain template.",
            "The system never returns send_allowed=true in the local product runtime.",
        ]
        if examples:
            acceptance_criteria.append(f"Candidate examples are loaded from template data, e.g. {', '.join(examples)}.")
    else:
        user_roles = ["Business operator", "Reviewer / approver", "Workflow owner"]
        core_workflows = [
            "Capture a business case.",
            "Run deterministic local checks and evidence retrieval.",
            "Use DeepSeek to draft a structured recommendation.",
            "Apply guardrails and prepare a human approval packet.",
        ]
        acceptance_criteria = [
            "The app exposes a real CLI and local web UI.",
            "The backend is split into agent, tools, data, guardrail, and API modules.",
            "Outputs include local tool results, evidence, risk, approval packet, and audit trace.",
            "The system never returns send_allowed=true in the local product runtime.",
        ]
    return {
        "prd_version": "software_builder_loop_v1",
        "product_name": product_spec.get("product_name", opportunity.get("name", "Generated Agent Product")),
        "app_kind": app_kind,
        "source_opportunity": opportunity.get("name", ""),
        "company_context": {
            "industry": context.get("industry", ""),
            "main_business": context.get("main_business", ""),
            "ai_objective": context.get("ai_objective", ""),
            "constraints": context.get("constraints", ""),
        },
        "problem_statement": opportunity.get("target_workflow", ""),
        "proposed_capability": opportunity.get("proposed_ai_capability", ""),
        "primary_users": user_roles,
        "core_workflows": core_workflows,
        "acceptance_criteria": acceptance_criteria,
        "non_goals": [
            "No production database or external CRM integration in the local product runtime.",
            "No automatic customer sending or irreversible action.",
            "No legal, financial, disaster-safety, or investment guarantee.",
        ],
        "safety_policy": "Human approval is required before customer-facing, financial, legal, safety, or operationally consequential use.",
    }


def build_project_architecture(agent_design: dict, architecture: dict, product_spec: dict) -> dict:
    """Describe the generated project as a real multi-file app."""
    return {
        "architecture_version": "software_builder_loop_v1",
        "product_name": product_spec.get("product_name", ""),
        "app_kind": product_spec.get("app_kind", "enterprise_agent_product"),
        "runtime": "Python standard library HTTP API + static frontend + DeepSeek chat completions",
        "entrypoints": {
            "cli": "python3 app.py --cli",
            "server": "python3 app.py",
            "evaluation": "python3 evaluation.py",
            "deterministic_tests": "python3 -m unittest discover -s tests",
        },
        "backend_modules": [
            {"path": "backend/agent.py", "responsibility": "Orchestrates case -> tools -> evidence -> DeepSeek -> guardrails."},
            {"path": "backend/api.py", "responsibility": "Local JSON API and static frontend server."},
            {"path": "backend/data_store.py", "responsibility": "Loads generated domain data and sample cases."},
            {"path": "backend/llm_client.py", "responsibility": "DeepSeek/OpenAI-compatible JSON client with retry."},
            {"path": "backend/web_search.py", "responsibility": "Runtime trusted-domain web evidence search."},
            {"path": "backend/recommendation_engine.py", "responsibility": "Deterministic ranking algorithms."},
            {"path": "backend/tools.py", "responsibility": "Local tool interface used before LLM drafting."},
            {"path": "backend/guardrails.py", "responsibility": "Schema normalization, placeholder prevention, approval enforcement."},
        ],
        "frontend_modules": [
            {"path": "frontend/index.html", "responsibility": "Usable product surface."},
            {"path": "frontend/styles.css", "responsibility": "Work-focused interface styling."},
            {"path": "frontend/app.js", "responsibility": "Calls local API and displays recommendation packets."},
        ],
        "data_modules": [
            {"path": "data/areas.json", "responsibility": "Generated local domain candidates."},
            {"path": "data/properties.json", "responsibility": "Generated related item records."},
            {"path": "data/sample_customers.json", "responsibility": "Generated evaluation cases."},
        ],
        "quality_gates": [
            "All Python files compile.",
            "App imports successfully.",
            "CLI smoke test produces structured JSON for one representative case using the real DeepSeek API.",
            "Deterministic unit tests pass.",
            "API-backed smoke evaluation passes for one representative case; full multi-case evaluation remains available.",
            "Frontend responsiveness harness passes.",
            "No API key or secret is written into generated files.",
        ],
        "selected_primitives": architecture.get("selected_primitives", []),
    }


def build_file_manifest(product_spec: dict) -> dict:
    """Return the authoritative generated file list."""
    files = [
        ("README.md", "Human-readable usage and inspection guide."),
        ("requirements.txt", "Runtime dependency note; stdlib-first local product MVP."),
        ("app.py", "CLI/server entrypoint."),
        ("tools.py", "Compatibility wrapper for local domain tools."),
        ("evaluation.py", "API-backed product evaluator."),
        ("product_spec.json", "Generated product specification."),
        ("software_blueprint.json", "Backward-compatible copy of the product specification."),
        ("product_requirements.json", "Generated PRD."),
        ("productization_blueprint.json", "Enterprise software productization blueprint."),
        ("productization_blueprint.md", "Human-readable productization blueprint."),
        ("product_readiness.json", "Production-readiness checklist and gap analysis."),
        ("production_readiness.md", "Human-readable production-readiness report."),
        ("project_architecture.json", "Generated project architecture."),
        ("architecture.json", "Primitive architecture selected by the consulting/search layer."),
        ("architecture.md", "Readable generated project architecture."),
        ("implementation_plan.json", "Software Builder Loop implementation plan."),
        ("file_manifest.json", "Authoritative file manifest."),
        ("file_plan.json", "Backward-compatible copy of the file manifest."),
        ("llm_app_design.json", "Build-time DeepSeek or fallback application design contract."),
        ("app_design.json", "Backward-compatible copy of the generated application design contract."),
        ("generated_product_rules.md", "Build-time generated product rules and design document."),
        ("code_task_plan.json", "Build-time generated specialized-role task plan."),
        ("component_plan.json", "Plan-driven component assembly contract consumed by the generated product package."),
        ("generation_trace.json", "Generation trace for reviewer inspection."),
        ("builder_loop_trace.json", "Software Builder Loop trace."),
        ("repair_log.json", "Repair-loop status and planned actions."),
        ("agent_spec.json", "Agent runtime contract and prompts."),
        ("generated_reasoning_policy.json", "Build-time LLM or fallback JSON policy used by the runtime reasoning prompt."),
        ("generated_domain_logic_validation.json", "Validation report for the small build-time generated domain logic plugin."),
        ("generated_layout_config.json", "Build-time generated frontend layout and visual experience configuration."),
        ("generated_interaction_config.json", "Build-time generated interactive AI copilot configuration."),
        ("evaluation_checklist.json", "Build-time generated domain evaluation checklist."),
        ("llm_builder_review.json", "Build-time review of generated design artifacts."),
        ("domain_data.json", "Compatibility aggregate of generated domain data."),
        ("sample_cases.json", "Compatibility copy of generated sample cases."),
        ("knowledge_base.md", "Generated product knowledge base."),
        ("pipeline_diagram.svg", "Generated agent flow diagram."),
        ("analysis_charts.svg", "Generated local data chart."),
        ("backend/__init__.py", "Backend package marker."),
        ("backend/agent.py", "Agent orchestration."),
        ("backend/api.py", "Local API and frontend server."),
        ("backend/data_store.py", "Data loading helpers."),
        ("backend/guardrails.py", "Safety and output contract enforcement."),
        ("backend/llm_client.py", "DeepSeek JSON client."),
        ("backend/generated_reasoning_policy.py", "Validated build-time generated runtime reasoning policy constant."),
        ("backend/generated_domain_adapter.py", "Validated build-time generated domain adapter constant."),
        ("backend/generated_domain_logic.py", "Validated small build-time generated domain-specific logic plugin."),
        ("backend/web_search.py", "Runtime trusted-domain live web evidence search."),
        ("backend/recommendation_engine.py", "Deterministic ranking engine."),
        ("backend/tools.py", "Domain tool interface."),
        ("frontend/index.html", "Generated product UI."),
        ("frontend/generated_ui_config.json", "Build-time generated UI configuration consumed by the frontend."),
        ("frontend/generated_layout_config.json", "Build-time generated frontend layout configuration consumed by the frontend."),
        ("frontend/generated_interaction_config.json", "Build-time generated AI copilot interactions consumed by the frontend."),
        ("frontend/styles.css", "Generated product styling."),
        ("frontend/app.js", "Generated product UI behavior."),
        ("data/areas.json", "Domain candidate records."),
        ("data/properties.json", "Related item records."),
        ("data/sample_customers.json", "Sample customer cases."),
        ("tests/test_recommendations.py", "Deterministic ranking tests."),
    ]
    return {
        "manifest_version": "software_builder_loop_v1",
        "product_name": product_spec.get("product_name", ""),
        "files": [
            {"path": path, "role": role, "required": True}
            for path, role in files
        ],
    }


def build_implementation_plan(agent_design: dict, architecture: dict, blueprint: dict) -> dict:
    """Create an executable construction plan from analysis artifacts."""
    opportunity = _opportunity(agent_design)
    return {
        "method": "software_builder_loop_v1",
        "source_artifacts": [
            "business_analysis.json",
            "opportunities.json",
            "feasibility_results.json",
            "tree_search_trace.json",
            "selected_opportunity.json",
            "productization_blueprint.json",
            "llm_app_design.json",
            "generated_product_rules.md",
            "code_task_plan.json",
            "component_plan.json",
            "product_brief.json",
            "agent_design.json",
        ],
        "source_opportunity": opportunity.get("name", ""),
        "product_name": blueprint.get("product_name", ""),
        "goal": "Generate a runnable multi-file enterprise agent product, execute it, evaluate it, and review it.",
        "work_breakdown": [stage.as_dict() for stage in BUILDER_LOOP_STAGES],
        "selected_primitives": architecture.get("selected_primitives", []),
        "quality_gates": [
            "Generated app must be a project package, not a single demo script.",
            "Generated app must have backend, frontend, data, tests, evaluation, and documentation.",
            "Generated app must use deterministic local tools before DeepSeek drafting.",
            "Generated app must call DeepSeek in real API mode.",
            "Generated app must enforce human approval and send_allowed=false.",
            "Sandbox evaluation must pass before the generated product is considered usable.",
        ],
        "human_approval_policy": "Generated software must not send external messages or perform irreversible actions.",
    }


def build_file_plan(blueprint: dict) -> dict:
    """Backward-compatible alias for the richer file manifest."""
    return build_file_manifest(blueprint)


def build_generation_trace(implementation_plan: dict, blueprint: dict) -> dict:
    """Return an auditable trace for the generated app construction stage."""
    return {
        "method": implementation_plan.get("method", "software_builder_loop_v1"),
        "source": "selected_opportunity + productization_blueprint + component_plan + product_requirements + project_architecture + file_manifest",
        "generated_product": blueprint.get("product_name", ""),
        "stages": implementation_plan.get("work_breakdown", []),
        "quality_gates": implementation_plan.get("quality_gates", []),
        "note": "The Code Agent now generates a complete runnable project package and validates it through sandbox execution.",
    }


def build_builder_loop_trace(
    product_requirements: dict,
    project_architecture: dict,
    file_manifest: dict,
    implementation_plan: dict,
) -> dict:
    """Create the top-level builder trace used by reviewers."""
    return {
        "trace_version": "software_builder_loop_v1",
        "loop": [stage.as_dict() for stage in BUILDER_LOOP_STAGES],
        "product_requirements": {
            "product_name": product_requirements.get("product_name"),
            "acceptance_criteria": product_requirements.get("acceptance_criteria", []),
        },
        "project_architecture": {
            "runtime": project_architecture.get("runtime"),
            "entrypoints": project_architecture.get("entrypoints", {}),
            "backend_modules": [item["path"] for item in project_architecture.get("backend_modules", [])],
            "frontend_modules": [item["path"] for item in project_architecture.get("frontend_modules", [])],
        },
        "file_count": len(file_manifest.get("files", [])),
        "quality_gates": implementation_plan.get("quality_gates", []),
    }


def build_repair_log(evaluation: dict | None = None) -> dict:
    """Create a repair log compatible with generate-run-repair iterations."""
    if not evaluation:
        return {
            "repairs": [],
            "status": "not_yet_evaluated",
            "note": "The generated project has been written; sandbox execution will fill this after evaluation.",
        }
    if evaluation.get("success"):
        return {
            "repairs": [],
            "status": "passed",
            "summary": {
                "passed": evaluation.get("passed"),
                "total": evaluation.get("total"),
                "pass_rate": evaluation.get("pass_rate"),
            },
        }
    failed_checks = [
        check.get("name", "unknown_check")
        for check in evaluation.get("checks", [])
        if not check.get("success")
    ]
    return {
        "status": "repair_required",
        "failed_checks": failed_checks,
        "repairs": [
            {
                "trigger": "sandbox_evaluation_failed",
                "failed_checks": failed_checks,
                "action": "Patch generated source files, rerun deterministic tests, then rerun API-backed evaluation.",
            }
        ],
    }
