"""Enterprise productization planning for generated agent software.

This stage sits between agent workflow design and code generation. Its job is
to turn a selected AI enablement opportunity into a product-level software
blueprint, so generated apps are shaped like usable enterprise products instead
of single-purpose demos or raw JSON consoles.
"""

from __future__ import annotations

from typing import Any


PRODUCT_ARCHETYPES = {
    "recommendation_workbench": {
        "name": "Recommendation Workbench",
        "fit_terms": ["recommend", "property", "area", "housing", "sales", "proposal", "推薦", "提案", "物件", "地域"],
        "primary_job": "Compare candidates, explain trade-offs, and prepare an approval-ready recommendation.",
        "workspace_regions": ["case_queue", "intake_form", "candidate_comparison", "evidence_panel", "draft_editor", "approval_packet"],
    },
    "approval_review_console": {
        "name": "Approval Review Console",
        "fit_terms": ["approval", "compliance", "risk", "legal", "audit", "承認", "稟議", "監査", "法務"],
        "primary_job": "Review a request against policy, collect evidence, and produce a controlled approval packet.",
        "workspace_regions": ["case_queue", "policy_checklist", "risk_panel", "evidence_panel", "decision_options", "audit_log"],
    },
    "knowledge_operations_console": {
        "name": "Knowledge Operations Console",
        "fit_terms": ["knowledge", "manual", "faq", "support", "ナレッジ", "マニュアル", "問い合わせ"],
        "primary_job": "Retrieve trusted knowledge, cite sources, and draft an answer for human review.",
        "workspace_regions": ["case_queue", "request_intake", "retrieval_results", "answer_draft", "risk_panel", "audit_log"],
    },
    "document_processing_console": {
        "name": "Document Processing Console",
        "fit_terms": ["document", "invoice", "contract", "pdf", "form", "契約", "請求書", "申請"],
        "primary_job": "Extract structured fields, check completeness, and route exceptions.",
        "workspace_regions": ["document_queue", "field_extraction", "checklist", "exception_panel", "approval_packet", "audit_log"],
    },
    "planning_exception_console": {
        "name": "Planning and Exception Console",
        "fit_terms": ["forecast", "inventory", "shift", "logistics", "planning", "需要", "在庫", "配送", "人員"],
        "primary_job": "Review forecasts, explain drivers, and escalate operational exceptions.",
        "workspace_regions": ["planning_queue", "forecast_summary", "exception_table", "evidence_panel", "manager_decision", "audit_log"],
    },
}


def _blob(*values: object) -> str:
    return " ".join(str(value) for value in values).lower()


def _score_archetype(archetype: dict[str, Any], text: str) -> int:
    return sum(1 for term in archetype.get("fit_terms", []) if term.lower() in text)


def select_product_archetype(profile: dict, selected_opportunity: dict, architecture: dict) -> dict[str, Any]:
    """Select a product archetype from enterprise context and opportunity."""
    text = _blob(profile, selected_opportunity, architecture)
    if any(term in text for term in (
        "real_estate",
        "real estate",
        "property",
        "housing",
        "home",
        "area recommendation",
        "neighborhood",
        "不動産",
        "住宅",
        "物件",
        "地域",
        "推薦",
    )):
        archetype_id = "recommendation_workbench"
        archetype = PRODUCT_ARCHETYPES[archetype_id]
        return {
            "id": archetype_id,
            "name": archetype["name"],
            "primary_job": archetype["primary_job"],
            "workspace_regions": archetype["workspace_regions"],
            "selection_score": _score_archetype(archetype, text) + 3,
        }
    scored = [
        (archetype_id, _score_archetype(archetype, text), archetype)
        for archetype_id, archetype in PRODUCT_ARCHETYPES.items()
    ]
    scored.sort(key=lambda item: item[1], reverse=True)
    archetype_id, score, archetype = scored[0]
    if score <= 0:
        archetype_id = "knowledge_operations_console"
        archetype = PRODUCT_ARCHETYPES[archetype_id]
    return {
        "id": archetype_id,
        "name": archetype["name"],
        "primary_job": archetype["primary_job"],
        "workspace_regions": archetype["workspace_regions"],
        "selection_score": score,
    }


def build_productization_blueprint(
    profile: dict,
    agent_design: dict,
    architecture: dict,
    evidence_pack: dict,
) -> dict[str, Any]:
    """Build a product-level blueprint consumed by the code generator."""
    selected_opportunity = agent_design.get("selected_opportunity", {}) or {}
    archetype = select_product_archetype(profile, selected_opportunity, architecture)
    primitives = architecture.get("selected_primitives", [])
    evidence_items = evidence_pack.get("evidence_items", [])
    return {
        "blueprint_version": "enterprise_productization_v1",
        "maturity_target": "enterprise_software_mvp",
        "selected_archetype": archetype,
        "source_opportunity": selected_opportunity.get("name", ""),
        "product_positioning": {
            "not_a_chatbot": True,
            "not_a_json_console": True,
            "primary_user_value": archetype["primary_job"],
            "enterprise_context": {
                "company_name": profile.get("company_name", ""),
                "industry": profile.get("industry", ""),
                "main_business": profile.get("main_business", ""),
                "ai_objective": profile.get("ai_objective", profile.get("business_goal", "")),
            },
        },
        "role_model": [
            {"role": "operator", "permissions": ["create_case", "run_agent", "edit_draft"]},
            {"role": "reviewer", "permissions": ["review_evidence", "approve", "request_edits", "escalate"]},
            {"role": "manager", "permissions": ["view_queue", "inspect_audit", "manage_policy"]},
        ],
        "navigation_sections": [
            "Work queue",
            "Case intake",
            "AI analysis",
            "Evidence",
            "Approval",
            "Audit",
            "System readiness",
        ],
        "workspace_regions": archetype["workspace_regions"],
        "enterprise_capabilities": [
            "case_queue",
            "structured_intake_form",
            "runtime_live_web_evidence_search",
            "domain_tool_panel",
            "candidate_or_result_comparison",
            "editable_business_draft",
            "human_approval_packet",
            "activity_log",
            "audit_trace",
            "error_and_loading_states",
        ],
        "data_model": [
            {"object": "Case", "fields": ["case_id", "requester", "workflow_type", "status", "created_at"]},
            {"object": "EvidenceItem", "fields": ["id", "title", "url", "retrieval_method", "summary"]},
            {"object": "AgentRun", "fields": ["run_id", "case_id", "model", "tool_names", "risk_level"]},
            {"object": "ApprovalPacket", "fields": ["approval_owner", "decision_options", "risk_reasons", "send_allowed"]},
        ],
        "state_model": [
            "new",
            "ready_for_agent",
            "running",
            "draft_ready",
            "review_required",
            "approved_locally",
            "edit_requested",
            "escalated",
        ],
        "interaction_model": [
            "Select a case from the work queue.",
            "Edit structured input fields.",
            "Run local tools, live web search, and LLM reasoning.",
            "Compare ranked candidates or extracted findings.",
            "Inspect evidence sources and risk reasons.",
            "Edit the generated draft.",
            "Record approve, edit, or escalate decision in the local review state.",
        ],
        "visual_quality_contract": {
            "layout": "enterprise_workbench",
            "must_have": [
                "sidebar navigation",
                "case queue",
                "workbench panels",
                "candidate or result table",
                "evidence source list with live-search markers",
                "approval actions",
                "activity log",
                "debug JSON secondary only",
                "responsive KPI cards using auto-fit minmax grid",
                "tablet and mobile breakpoints",
                "safe wrapping for long labels and model outputs",
                "no horizontal page overflow",
            ],
            "avoid": [
                "landing page",
                "chat-only UI",
                "single raw JSON output",
                "marketing hero",
                "decorative-only visuals",
                "fixed six-column KPI layout",
                "desktop-only three-column workbench without tablet fallback",
            ],
        },
        "quality_gates": [
            "Generated app has a local server and browser UI.",
            "Generated app uses DeepSeek at runtime.",
            "Generated app performs runtime trusted-domain evidence search.",
            "Primary UI is an enterprise workbench; raw JSON is secondary.",
            "Frontend passes the responsiveness harness.",
            "Sandbox real-API smoke tests pass without requiring a full long-running batch.",
            "Human approval is visible and enforced.",
            "No API key or secret is written into generated files.",
        ],
        "evidence_basis": [item.get("id", "") for item in evidence_items[:8]],
        "selected_primitives": primitives,
    }


def render_productization_markdown(blueprint: dict[str, Any]) -> str:
    """Render the productization blueprint for reviewer inspection."""
    archetype = blueprint.get("selected_archetype", {})
    lines = [
        f"# Productization Blueprint: {archetype.get('name', 'Generated Product')}",
        "",
        f"- Maturity target: `{blueprint.get('maturity_target')}`",
        f"- Source opportunity: `{blueprint.get('source_opportunity')}`",
        f"- Primary job: {archetype.get('primary_job', '')}",
        "",
        "## Enterprise Capabilities",
        "",
        *[f"- {item}" for item in blueprint.get("enterprise_capabilities", [])],
        "",
        "## Workspace Regions",
        "",
        *[f"- {item}" for item in blueprint.get("workspace_regions", [])],
        "",
        "## Quality Gates",
        "",
        *[f"- {item}" for item in blueprint.get("quality_gates", [])],
        "",
    ]
    return "\n".join(lines)
