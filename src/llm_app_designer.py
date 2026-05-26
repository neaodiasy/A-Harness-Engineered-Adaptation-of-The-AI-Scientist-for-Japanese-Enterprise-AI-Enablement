"""Build-time DeepSeek-assisted app customization for scaffolded products.

DeepSeek is allowed to design small JSON/Markdown artifacts that customize the
stable scaffold. It is not allowed to write arbitrary full source files.
"""

from __future__ import annotations

import json
import ast
from typing import Any

from src.harness.json_utils import parse_jsonish
from src.scaffold_library import get_scaffold, select_scaffold_deterministically


ALLOWED_ARCHETYPES = {
    "recommendation_workbench",
    "customer_support_workbench",
    "risk_review_console",
    "knowledge_assistant",
    "approval_workbench",
    "domain_operations_workbench",
}

APP_DESIGN_REQUIRED_KEYS = [
    "design_source",
    "selected_scaffold_id",
    "reason_for_scaffold_selection",
    "product_archetype",
    "target_workflow",
    "primary_user",
    "ui_sections",
    "backend_modules",
    "local_tools",
    "runtime_llm_role",
    "runtime_prompt_requirements",
    "guardrails",
    "human_approval",
    "evaluation_requirements",
    "domain_adaptation_notes",
    "small_domain_logic_requirements",
    "interaction_modes",
    "user_actions",
    "conversation_starters",
]


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value in (None, ""):
        return []
    return [value]


def _string_list(value: Any, fallback: list[str]) -> list[str]:
    items = [str(item).strip() for item in _as_list(value) if str(item).strip()]
    return items or fallback


def _dict_list(value: Any, fallback: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for index, item in enumerate(_as_list(value), start=1):
        if isinstance(item, dict):
            items.append({str(key): val for key, val in item.items()})
        elif str(item).strip():
            items.append({"id": f"item_{index}", "label": str(item), "purpose": str(item), "required": True})
    return items or fallback


def _complete_json(llm_client: Any, prompt: str, system: str) -> Any:
    raw = llm_client.complete(prompt, system=system, json_mode=True)
    return parse_jsonish(raw, fallback=None)


def _fallback_interactions(selected_scaffold_id: str, selected_opportunity: dict[str, Any]) -> dict[str, Any]:
    """Create scaffold-specific AI interaction affordances for fallback builds."""
    opportunity_name = selected_opportunity.get("name", "selected opportunity")
    if selected_scaffold_id == "customer_support_workbench":
        return {
            "interaction_modes": [
                {"id": "triage_chat", "label": "Inquiry Triage", "purpose": "Classify the customer inquiry and identify missing information."},
                {"id": "policy_evidence_chat", "label": "Policy Evidence Q&A", "purpose": "Explain relevant FAQ, policy, or claim-procedure evidence."},
                {"id": "reply_coach", "label": "Reply Draft Coach", "purpose": "Draft a cautious customer-support reply for human review."},
            ],
            "user_actions": [
                {"id": "classify_inquiry", "label": "Classify inquiry", "prompt": "Classify this inquiry and explain the confidence and escalation boundary."},
                {"id": "retrieve_policy_evidence", "label": "Find policy evidence", "prompt": "Find relevant FAQ, policy, or procedure evidence and cite evidence IDs."},
                {"id": "draft_customer_reply", "label": "Draft customer reply", "prompt": "Draft a cautious Japanese customer-support reply that requires human approval."},
                {"id": "check_escalation", "label": "Check escalation", "prompt": "Identify ambiguity, missing documents, risk flags, and escalation reasons."},
            ],
            "conversation_starters": [
                f"Help me triage a customer inquiry for {opportunity_name}.",
                "What evidence should I cite before drafting a reply?",
                "Draft a safe customer-facing reply and list what a reviewer must approve.",
            ],
        }
    if selected_scaffold_id == "risk_review_console":
        return {
            "interaction_modes": [
                {"id": "risk_review_chat", "label": "Risk Review", "purpose": "Review policy, compliance, safety, or exception risks."},
                {"id": "missing_info_chat", "label": "Missing Information", "purpose": "Identify facts required before a decision-support draft."},
            ],
            "user_actions": [
                {"id": "summarize_risk", "label": "Summarize risk", "prompt": "Summarize risk factors, missing information, and approval boundary."},
                {"id": "policy_check", "label": "Check policy fit", "prompt": "Check the case against available policy evidence and explain uncertainty."},
                {"id": "prepare_reviewer_note", "label": "Reviewer note", "prompt": "Prepare a reviewer note with evidence, risk flags, and decision options."},
            ],
            "conversation_starters": [
                "What are the main risk flags in this case?",
                "What must a human reviewer verify before approval?",
            ],
        }
    if selected_scaffold_id == "knowledge_assistant":
        return {
            "interaction_modes": [
                {"id": "knowledge_chat", "label": "Knowledge Q&A", "purpose": "Answer operator questions from local and live evidence."},
                {"id": "evidence_summary_chat", "label": "Evidence Summary", "purpose": "Summarize evidence and uncertainty for human review."},
            ],
            "user_actions": [
                {"id": "answer_with_evidence", "label": "Answer with evidence", "prompt": "Answer using evidence IDs and clearly state uncertainty."},
                {"id": "summarize_documents", "label": "Summarize documents", "prompt": "Summarize the most relevant knowledge base and live evidence."},
                {"id": "ask_followups", "label": "Ask follow-ups", "prompt": "List follow-up questions needed before using the answer operationally."},
            ],
            "conversation_starters": [
                "Answer this operational question using available evidence.",
                "What evidence supports this answer?",
            ],
        }
    if selected_scaffold_id == "approval_workbench":
        return {
            "interaction_modes": [
                {"id": "approval_chat", "label": "Approval Review", "purpose": "Help reviewers inspect drafts, evidence, and risk boundaries."},
                {"id": "edit_request_chat", "label": "Edit Request", "purpose": "Suggest safe edits before approval."},
            ],
            "user_actions": [
                {"id": "review_draft", "label": "Review draft", "prompt": "Review this draft for unsupported claims and approval blockers."},
                {"id": "request_edits", "label": "Request edits", "prompt": "Write edit requests that make the draft safer and more evidence-grounded."},
                {"id": "build_approval_packet", "label": "Approval packet", "prompt": "Build an approval packet with evidence, risk, and decision options."},
            ],
            "conversation_starters": [
                "Review this draft before approval.",
                "What edits are needed before this can be sent?",
            ],
        }
    if selected_scaffold_id == "recommendation_workbench":
        return {
            "interaction_modes": [
                {"id": "preference_chat", "label": "Preference Analysis", "purpose": "Analyze user requirements and refine ranking criteria."},
                {"id": "candidate_explainer", "label": "Candidate Explainer", "purpose": "Explain candidate trade-offs using local tool results and evidence."},
                {"id": "recommendation_draft", "label": "Recommendation Draft", "purpose": "Draft a recommendation packet for human approval."},
            ],
            "user_actions": [
                {"id": "analyze_preferences", "label": "Analyze preferences", "prompt": "Analyze the user's preferences and identify ranking criteria."},
                {"id": "compare_candidates", "label": "Compare candidates", "prompt": "Compare top candidates using evidence, trade-offs, and uncertainty."},
                {"id": "draft_recommendation", "label": "Draft recommendation", "prompt": "Draft a cautious recommendation with human approval required."},
            ],
            "conversation_starters": [
                f"Analyze this case for {opportunity_name}.",
                "Explain the top candidate trade-offs.",
            ],
        }
    return {
        "interaction_modes": [
            {"id": "operations_chat", "label": "Operations Copilot", "purpose": "Discuss the case, evidence, risks, and next actions."},
            {"id": "approval_chat", "label": "Approval Support", "purpose": "Prepare approval-ready outputs for human review."},
        ],
        "user_actions": [
            {"id": "analyze_case", "label": "Analyze case", "prompt": "Analyze this enterprise case and identify useful next actions."},
            {"id": "find_evidence", "label": "Find evidence", "prompt": "Find and summarize relevant evidence and uncertainty."},
            {"id": "prepare_packet", "label": "Prepare packet", "prompt": "Prepare an approval-ready packet with risks and decision options."},
        ],
        "conversation_starters": [
            "Analyze this workflow case and recommend next actions.",
            "What evidence and risks should the reviewer check?",
        ],
    }


def _fallback_app_design(
    profile: dict[str, Any],
    selected_opportunity: dict[str, Any],
    agent_design: dict[str, Any],
    architecture: dict[str, Any],
    productization_blueprint: dict[str, Any],
    runtime_domain_pack: dict[str, Any],
    evidence_pack: dict[str, Any],
    scaffold_library: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    selected_scaffold_id = select_scaffold_deterministically(profile, selected_opportunity, agent_design, runtime_domain_pack)
    scaffold = (scaffold_library or {}).get(selected_scaffold_id) or get_scaffold(selected_scaffold_id)
    archetype_id = selected_scaffold_id
    interactions = _fallback_interactions(selected_scaffold_id, selected_opportunity)
    return {
        "design_source": "deterministic_fallback",
        "selected_scaffold_id": selected_scaffold_id,
        "reason_for_scaffold_selection": "Deterministic keyword fallback selected the closest reusable scaffold.",
        "product_archetype": archetype_id,
        "target_workflow": selected_opportunity.get("target_workflow") or agent_design.get("name") or "Enterprise workflow support",
        "primary_user": "Business operator and human reviewer",
        "ui_sections": [
            {"id": section, "label": section.replace("_", " ").title(), "purpose": f"{section} from selected scaffold.", "required": True}
            for section in scaffold.get("default_ui_sections", [])
        ],
        "backend_modules": [
            {"id": module, "purpose": f"{module} from selected scaffold.", "required": True}
            for module in scaffold.get("default_backend_modules", [])
        ],
        "local_tools": [
            {"id": tool, "purpose": f"{tool} from selected scaffold.", "input": "case JSON", "output": "tool result"}
            for tool in scaffold.get("default_local_tools", [])
        ],
        "runtime_llm_role": "Draft a cautious Japanese recommendation and approval packet using local tool results and evidence.",
        "runtime_prompt_requirements": [
            "Use concrete local tool results.",
            "Cite evidence IDs or state missing evidence.",
            "Follow generated reasoning policy and domain adapter.",
            "Return valid JSON matching the runtime output contract.",
        ],
        "guardrails": scaffold.get("required_guardrails", []) + [
            "human_approval.required must be true.",
            "human_approval.send_allowed must be false.",
        ],
        "human_approval": {"required": True, "send_allowed": False, "approval_reason": "Outputs may be customer-facing or operationally consequential."},
        "evaluation_requirements": [
            *scaffold.get("default_evaluation_checks", []),
            "Generated app imports successfully.",
            "Generated policy and domain adapter import successfully.",
            "CLI smoke test returns risk and approval packet.",
            "No secret leakage.",
        ],
        "domain_adaptation_notes": [
            f"Domain pack: {runtime_domain_pack.get('template_id', 'unknown')}",
            f"Evidence items: {len(evidence_pack.get('evidence_items', []))}",
            f"Enterprise industry: {profile.get('industry', '')}",
        ],
        "small_domain_logic_requirements": [
            "Adapt raw case fields into scaffold-specific prompt context.",
            "Return dictionaries only and keep human approval flags visible.",
        ],
        **interactions,
    }


def validate_app_design(design: Any, fallback: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(design, dict):
        design = {}
    out = dict(fallback)
    for key in APP_DESIGN_REQUIRED_KEYS:
        if key in design and design[key] not in (None, "", []):
            out[key] = design[key]
    if out.get("selected_scaffold_id") not in ALLOWED_ARCHETYPES:
        out["selected_scaffold_id"] = fallback["selected_scaffold_id"]
    if out.get("product_archetype") not in ALLOWED_ARCHETYPES:
        out["product_archetype"] = out["selected_scaffold_id"]
    out["reason_for_scaffold_selection"] = str(out.get("reason_for_scaffold_selection") or fallback.get("reason_for_scaffold_selection", ""))
    out["ui_sections"] = _dict_list(out.get("ui_sections"), fallback["ui_sections"])
    out["backend_modules"] = _dict_list(out.get("backend_modules"), fallback["backend_modules"])
    out["local_tools"] = _dict_list(out.get("local_tools"), fallback["local_tools"])
    out["runtime_prompt_requirements"] = _string_list(out.get("runtime_prompt_requirements"), fallback["runtime_prompt_requirements"])
    out["guardrails"] = _string_list(out.get("guardrails"), fallback["guardrails"])
    out["evaluation_requirements"] = _string_list(out.get("evaluation_requirements"), fallback["evaluation_requirements"])
    out["domain_adaptation_notes"] = _string_list(out.get("domain_adaptation_notes"), fallback["domain_adaptation_notes"])
    out["small_domain_logic_requirements"] = _string_list(out.get("small_domain_logic_requirements"), fallback["small_domain_logic_requirements"])
    out["interaction_modes"] = _dict_list(out.get("interaction_modes"), fallback["interaction_modes"])
    out["user_actions"] = _dict_list(out.get("user_actions"), fallback["user_actions"])
    out["conversation_starters"] = _string_list(out.get("conversation_starters"), fallback["conversation_starters"])
    human = out.get("human_approval") if isinstance(out.get("human_approval"), dict) else {}
    human["required"] = True
    human["send_allowed"] = False
    human.setdefault("approval_reason", fallback["human_approval"]["approval_reason"])
    out["human_approval"] = human
    out["validated"] = True
    return out


def build_llm_app_design(
    profile: dict[str, Any],
    selected_opportunity: dict[str, Any],
    agent_design: dict[str, Any],
    architecture: dict[str, Any],
    productization_blueprint: dict[str, Any],
    runtime_domain_pack: dict[str, Any],
    evidence_pack: dict[str, Any],
    scaffold_library: dict[str, dict[str, Any]] | None = None,
    llm_client: Any | None = None,
) -> dict[str, Any]:
    fallback = _fallback_app_design(profile, selected_opportunity, agent_design, architecture, productization_blueprint, runtime_domain_pack, evidence_pack, scaffold_library)
    if llm_client is None:
        return validate_app_design(fallback, fallback)
    prompt = f"""Return one JSON object that selects and customizes a reusable enterprise AI product scaffold.
Do not write source code. JSON only.
Required keys: {json.dumps(APP_DESIGN_REQUIRED_KEYS)}
Allowed selected_scaffold_id and product_archetype values: {sorted(ALLOWED_ARCHETYPES)}
human_approval.required must be true and human_approval.send_allowed must be false.
Select exactly one scaffold from the scaffold library, then customize UI sections, backend modules, local tools, guardrails, evaluation checks, and small domain logic requirements.

Scaffold library: {json.dumps(scaffold_library or {}, ensure_ascii=False)}
Enterprise profile: {json.dumps(profile, ensure_ascii=False)}
Selected opportunity: {json.dumps(selected_opportunity, ensure_ascii=False)}
Agent design: {json.dumps(agent_design, ensure_ascii=False)}
Architecture: {json.dumps(architecture, ensure_ascii=False)}
Productization blueprint: {json.dumps(productization_blueprint, ensure_ascii=False)}
Runtime domain pack: {json.dumps(runtime_domain_pack, ensure_ascii=False)}
Evidence pack: {json.dumps(evidence_pack, ensure_ascii=False)}
"""
    try:
        design = validate_app_design(_complete_json(llm_client, prompt, "Design safe scaffold-based enterprise AI apps as JSON."), fallback)
        design["design_source"] = "deepseek_build_time_app_design"
        design["llm_model"] = getattr(llm_client, "model_name", "")
        return design
    except Exception as exc:
        fallback["design_source"] = "deterministic_fallback"
        fallback["llm_error"] = f"{type(exc).__name__}: {exc}"
        return validate_app_design(fallback, fallback)


def build_generated_product_rules(
    app_design: dict[str, Any],
    product_spec: dict[str, Any],
    runtime_domain_pack: dict[str, Any],
    selected_opportunity: dict[str, Any],
    llm_client: Any | None = None,
) -> str:
    fallback = f"""# Generated Product Rules

## Product Purpose
{product_spec.get('subtitle', 'Generate an approval-ready enterprise AI workflow output.')}

## Target Users
{app_design.get('primary_user', 'Business operator and human reviewer')}

## Selected Opportunity
{selected_opportunity.get('name', product_spec.get('selected_opportunity', 'Enterprise AI enablement opportunity'))}

## Product Archetype
{app_design.get('product_archetype', 'domain_operations_workbench')}

## UI Sections
{chr(10).join('- ' + str(item.get('label', item.get('id', item))) for item in app_design.get('ui_sections', []))}

## Backend Modules
{chr(10).join('- ' + str(item.get('id', item)) + ': ' + str(item.get('purpose', '')) for item in app_design.get('backend_modules', []))}

## Local Tools
{chr(10).join('- ' + str(item.get('id', item)) + ': ' + str(item.get('purpose', '')) for item in app_design.get('local_tools', []))}

## Evidence Usage
Use local domain data, knowledge base, and runtime trusted web evidence as supporting context. Live evidence requires human verification.

## Risk Rules
{chr(10).join('- ' + item for item in app_design.get('guardrails', []))}

## Forbidden Claims
- No final legal, financial, medical, HR, safety, regulated, or irreversible decisions.
- No automatic customer sending.
- No guarantees of correctness, compliance, profitability, safety, or source freshness.

## Human Approval Policy
human_approval_required=true and send_allowed=false for all generated runtime outputs.

## Evaluation Requirements
{chr(10).join('- ' + item for item in app_design.get('evaluation_requirements', []))}

## Sandbox Expectations
Generated files must exist, Python must compile, policy/adapter imports must pass, tests and CLI/evaluation smoke checks must run.
"""
    if llm_client is None:
        return fallback
    prompt = f"""Write a concise Markdown product rules/design document for this scaffolded generated app.
Do not include secrets. Do not claim production readiness.
Include product purpose, target users, selected opportunity, product archetype, UI sections, backend modules, local tools, evidence usage, risk rules, forbidden claims, human approval policy, evaluation requirements, and sandbox expectations.

App design: {json.dumps(app_design, ensure_ascii=False)}
Product spec: {json.dumps(product_spec, ensure_ascii=False)}
Domain pack: {json.dumps(runtime_domain_pack, ensure_ascii=False)}
Selected opportunity: {json.dumps(selected_opportunity, ensure_ascii=False)}
"""
    try:
        text = llm_client.complete(prompt, system="Write safe Markdown design rules for a scaffolded enterprise app.", json_mode=False)
        return text.strip() or fallback
    except Exception:
        return fallback


def _fallback_task_plan(app_design: dict[str, Any]) -> dict[str, Any]:
    return {
        "source": "deterministic_fallback",
        "tasks": [
            {"role": "backend_role", "task": "Generate runtime reasoning policy and domain adapter specification", "target_files": ["backend/generated_reasoning_policy.py", "backend/generated_domain_adapter.py"], "inputs": ["product_spec", "runtime_domain_pack", "llm_app_design"], "acceptance_checks": ["imports", "human_approval_required", "send_allowed_false"]},
            {"role": "frontend_role", "task": "Generate UI configuration from app design", "target_files": ["frontend/generated_ui_config.json"], "inputs": ["llm_app_design"], "acceptance_checks": ["contains_ui_sections"]},
            {"role": "guardrails_role", "task": "Generate forbidden claims and escalation rules", "target_files": ["backend/generated_reasoning_policy.py"], "inputs": ["llm_app_design", "runtime_domain_pack"], "acceptance_checks": ["approval_required_true", "send_allowed_false"]},
            {"role": "evaluation_role", "task": "Generate domain-specific evaluation checklist", "target_files": ["evaluation_checklist.json"], "inputs": ["llm_app_design"], "acceptance_checks": ["checklist_non_empty"]},
            {"role": "reviewer_role", "task": "Review generated LLM design artifacts for missing safety fields", "target_files": ["llm_builder_review.json"], "inputs": ["all_llm_design_artifacts"], "acceptance_checks": ["review_passed_or_fallback"]},
            {"role": "domain_logic_role", "task": "Generate safe domain-specific code plugin", "target_files": ["backend/generated_domain_logic.py"], "inputs": ["selected_scaffold_id", "runtime_domain_pack", "llm_app_design"], "acceptance_checks": ["ast_safe", "adapt_case_returns_dict", "prompt_context_returns_dict"]},
            {"role": "interaction_role", "task": "Generate business-specific AI copilot interaction modes and user actions", "target_files": ["frontend/generated_interaction_config.json"], "inputs": ["llm_app_design", "product_spec", "runtime_domain_pack"], "acceptance_checks": ["user_actions_non_empty", "human_approval_required", "send_allowed_false"]},
        ],
        "app_design_archetype": app_design.get("product_archetype", ""),
    }


def build_code_task_plan(app_design: dict[str, Any], product_spec: dict[str, Any], runtime_domain_pack: dict[str, Any], llm_client: Any | None = None) -> dict[str, Any]:
    fallback = _fallback_task_plan(app_design)
    if llm_client is None:
        return fallback
    prompt = f"""Return one JSON code task plan for specialized roles. JSON only.
Roles must include backend_role, frontend_role, guardrails_role, evaluation_role, reviewer_role, domain_logic_role, interaction_role.
Each task needs role, task, target_files, inputs, acceptance_checks.
App design: {json.dumps(app_design, ensure_ascii=False)}
Product spec: {json.dumps(product_spec, ensure_ascii=False)}
Domain pack: {json.dumps(runtime_domain_pack, ensure_ascii=False)}
"""
    try:
        plan = _complete_json(llm_client, prompt, "Plan safe JSON-only role tasks for scaffold customization.")
        if not isinstance(plan, dict) or not isinstance(plan.get("tasks"), list):
            return fallback
        roles = {str(task.get("role")) for task in plan["tasks"] if isinstance(task, dict)}
        required = {"backend_role", "frontend_role", "guardrails_role", "evaluation_role", "reviewer_role", "domain_logic_role", "interaction_role"}
        if not required.issubset(roles):
            return fallback
        plan["source"] = "deepseek_code_task_planner"
        return plan
    except Exception:
        return fallback


def _policy_fallback(app_design: dict[str, Any], product_spec: dict[str, Any], runtime_domain_pack: dict[str, Any]) -> dict[str, Any]:
    return {
        "policy_version": "1.0",
        "source": "deterministic_fallback",
        "product_archetype": app_design.get("product_archetype", "domain_operations_workbench"),
        "selected_scaffold_id": app_design.get("selected_scaffold_id", app_design.get("product_archetype", "domain_operations_workbench")),
        "runtime_role": app_design.get("runtime_llm_role", "Draft cautious approval-ready outputs."),
        "required_output_sections": ["classification", "evidence", "missing_information", "recommendation_ja", "customer_or_business_draft_ja", "internal_review_note", "risk", "approval_packet"],
        "runtime_prompt_requirements": app_design.get("runtime_prompt_requirements", []),
        "domain_specific_instructions": runtime_domain_pack.get("specific_rules", []),
        "forbidden_claims": ["No legal decisions.", "No financial decisions.", "No medical decisions.", "No HR/employment decisions.", "No safety or regulated final decisions.", "No final decisions."],
        "risk_rules": app_design.get("guardrails", []),
        "approval_packet_requirements": ["Evidence IDs", "Risk reasons", "Missing information", "Decision options", "Human owner approval"],
        "human_approval_required": True,
        "send_allowed": False,
        "evaluation_checklist": app_design.get("evaluation_requirements", []),
    }


def _adapter_fallback(app_design: dict[str, Any], product_spec: dict[str, Any], runtime_domain_pack: dict[str, Any]) -> dict[str, Any]:
    return {
        "adapter_version": "1.0",
        "source": "deterministic_fallback",
        "domain": product_spec.get("domain_template_id", runtime_domain_pack.get("template_id", "enterprise")),
        "scaffold_id": app_design.get("selected_scaffold_id", app_design.get("product_archetype", "")),
        "product_archetype": app_design.get("product_archetype", ""),
        "target_workflow": app_design.get("target_workflow", ""),
        "reasoning_steps": ["Read case", "Run local tools", "Retrieve evidence", "Draft cautiously", "Prepare approval packet"],
        "tool_policy": {"local_tools": app_design.get("local_tools", []), "live_search": True},
        "ui_binding_notes": app_design.get("ui_sections", []),
        "domain_fields": runtime_domain_pack.get("fields", []),
        "sample_case_strategy": "Use generated sample cases from the runtime domain pack for smoke tests.",
    }


def _ui_fallback(app_design: dict[str, Any]) -> dict[str, Any]:
    return {
        "product_archetype": app_design.get("product_archetype", "domain_operations_workbench"),
        "selected_scaffold_id": app_design.get("selected_scaffold_id", app_design.get("product_archetype", "domain_operations_workbench")),
        "ui_sections": app_design.get("ui_sections", []),
        "panel_labels": {str(item.get("id", f"section_{i}")): str(item.get("label", item.get("id", ""))) for i, item in enumerate(app_design.get("ui_sections", []), start=1) if isinstance(item, dict)},
        "button_labels": {"primary_action": "Generate Packet", "approve": "Approve Draft", "edit": "Request Edits", "escalate": "Escalate"},
        "empty_state_text": "Run the agent to generate an approval-ready packet.",
        "approval_labels": {"status": "Review Required", "send_allowed_false": "Sending blocked until human approval"},
    }


def _interaction_config_fallback(app_design: dict[str, Any]) -> dict[str, Any]:
    selected_scaffold_id = app_design.get("selected_scaffold_id", app_design.get("product_archetype", "domain_operations_workbench"))
    interactions = _fallback_interactions(str(selected_scaffold_id), {"name": app_design.get("target_workflow", "enterprise workflow")})
    return {
        "source": "deterministic_fallback",
        "selected_scaffold_id": selected_scaffold_id,
        "product_archetype": app_design.get("product_archetype", selected_scaffold_id),
        "assistant_title": {
            "customer_support_workbench": "Support AI Copilot",
            "recommendation_workbench": "Recommendation AI Copilot",
            "risk_review_console": "Risk Review AI Copilot",
            "knowledge_assistant": "Knowledge AI Copilot",
            "approval_workbench": "Approval AI Copilot",
        }.get(str(selected_scaffold_id), "Enterprise AI Copilot"),
        "input_placeholder": "Ask the AI to analyze this case, find evidence, draft safely, or prepare approval notes.",
        "interaction_modes": app_design.get("interaction_modes") or interactions["interaction_modes"],
        "user_actions": app_design.get("user_actions") or interactions["user_actions"],
        "conversation_starters": app_design.get("conversation_starters") or interactions["conversation_starters"],
        "safety_notice": "AI output is draft-only. Human approval is required before customer-facing or operational use.",
        "response_contract": {
            "required_keys": ["reply_ja", "used_evidence", "suggested_next_actions", "risk", "approval_note", "human_approval_required", "send_allowed"],
            "human_approval_required": True,
            "send_allowed": False,
        },
        "human_approval_required": True,
        "send_allowed": False,
    }


def _evaluation_fallback(app_design: dict[str, Any]) -> dict[str, Any]:
    return {
        "required_fields": ["case_id", "risk", "approval_packet", "human_approval_required", "send_allowed"],
        "runtime_checks": ["classification_present", "evidence_present", "draft_present"],
        "approval_checks": ["human_approval_required_true", "send_allowed_false", "approval_packet_present"],
        "risk_checks": ["risk_level_present", "risk_reasons_present"],
        "domain_specific_checks": app_design.get("evaluation_requirements", []),
    }


def _review_fallback() -> dict[str, Any]:
    return {"review_source": "deterministic_fallback", "passed": True, "missing_fields": [], "safety_concerns": [], "fallback_recommendation": "Use deterministic fallback artifacts when LLM role output is invalid."}


def _validate_role_outputs(outputs: dict[str, Any], app_design: dict[str, Any], product_spec: dict[str, Any], runtime_domain_pack: dict[str, Any]) -> dict[str, Any]:
    policy_fallback = _policy_fallback(app_design, product_spec, runtime_domain_pack)
    adapter_fallback = _adapter_fallback(app_design, product_spec, runtime_domain_pack)
    ui_fallback = _ui_fallback(app_design)
    interaction_fallback = _interaction_config_fallback(app_design)
    evaluation_fallback = _evaluation_fallback(app_design)
    review_fallback = _review_fallback()
    outputs.setdefault("reasoning_policy", policy_fallback)
    outputs.setdefault("domain_adapter", adapter_fallback)
    outputs.setdefault("ui_config", ui_fallback)
    outputs.setdefault("interaction_config", interaction_fallback)
    outputs.setdefault("evaluation_checklist", evaluation_fallback)
    outputs.setdefault("builder_review", review_fallback)
    policy = outputs["reasoning_policy"] if isinstance(outputs["reasoning_policy"], dict) else _policy_fallback(app_design, product_spec, runtime_domain_pack)
    for key, value in policy_fallback.items():
        policy.setdefault(key, value)
    policy["human_approval_required"] = True
    policy["send_allowed"] = False
    outputs["reasoning_policy"] = policy

    adapter = outputs["domain_adapter"] if isinstance(outputs["domain_adapter"], dict) else adapter_fallback
    for key, value in adapter_fallback.items():
        adapter.setdefault(key, value)
    outputs["domain_adapter"] = adapter

    ui = outputs["ui_config"] if isinstance(outputs["ui_config"], dict) else ui_fallback
    for key, value in ui_fallback.items():
        ui.setdefault(key, value)
    if not ui.get("ui_sections"):
        ui["ui_sections"] = ui_fallback["ui_sections"]
    outputs["ui_config"] = ui

    interaction = outputs["interaction_config"] if isinstance(outputs["interaction_config"], dict) else interaction_fallback
    for key, value in interaction_fallback.items():
        interaction.setdefault(key, value)
    interaction["human_approval_required"] = True
    interaction["send_allowed"] = False
    if not interaction.get("user_actions"):
        interaction["user_actions"] = interaction_fallback["user_actions"]
    if not interaction.get("interaction_modes"):
        interaction["interaction_modes"] = interaction_fallback["interaction_modes"]
    if not interaction.get("conversation_starters"):
        interaction["conversation_starters"] = interaction_fallback["conversation_starters"]
    outputs["interaction_config"] = interaction

    evaluation = outputs["evaluation_checklist"] if isinstance(outputs["evaluation_checklist"], dict) else evaluation_fallback
    for key, value in evaluation_fallback.items():
        evaluation.setdefault(key, value)
    if not evaluation.get("approval_checks"):
        evaluation["approval_checks"] = evaluation_fallback["approval_checks"]
    outputs["evaluation_checklist"] = evaluation

    review = outputs["builder_review"] if isinstance(outputs["builder_review"], dict) else review_fallback
    review.setdefault("passed", True)
    review.setdefault("missing_fields", [])
    review.setdefault("safety_concerns", [])
    review.setdefault("fallback_recommendation", review_fallback["fallback_recommendation"])
    outputs["builder_review"] = review
    return outputs


def build_specialized_role_outputs(app_design: dict[str, Any], product_spec: dict[str, Any], runtime_domain_pack: dict[str, Any], code_task_plan: dict[str, Any], llm_client: Any | None = None) -> dict[str, Any]:
    fallbacks = {
        "reasoning_policy": _policy_fallback(app_design, product_spec, runtime_domain_pack),
        "domain_adapter": _adapter_fallback(app_design, product_spec, runtime_domain_pack),
        "ui_config": _ui_fallback(app_design),
        "interaction_config": _interaction_config_fallback(app_design),
        "evaluation_checklist": _evaluation_fallback(app_design),
        "builder_review": _review_fallback(),
    }
    if llm_client is None:
        return {"source": "deterministic_fallback", **_validate_role_outputs(fallbacks, app_design, product_spec, runtime_domain_pack)}

    role_specs = {
        "reasoning_policy": "Generate JSON for backend/generated_reasoning_policy.py with policy_version, source, product_archetype, runtime_role, required_output_sections, runtime_prompt_requirements, domain_specific_instructions, forbidden_claims, risk_rules, approval_packet_requirements, human_approval_required, send_allowed, evaluation_checklist.",
        "domain_adapter": "Generate JSON for backend/generated_domain_adapter.py with adapter_version, source, domain, product_archetype, target_workflow, reasoning_steps, tool_policy, ui_binding_notes, domain_fields, sample_case_strategy.",
        "ui_config": "Generate JSON for frontend/generated_ui_config.json with product_archetype, ui_sections, panel_labels, button_labels, empty_state_text, approval_labels.",
        "interaction_config": "Generate JSON for frontend/generated_interaction_config.json with selected_scaffold_id, product_archetype, assistant_title, input_placeholder, interaction_modes, user_actions, conversation_starters, safety_notice, response_contract, human_approval_required, send_allowed. User actions must be business-specific and must let the user interact with DeepSeek for the useful enterprise workflow.",
        "evaluation_checklist": "Generate JSON for evaluation_checklist.json with required_fields, runtime_checks, approval_checks, risk_checks, domain_specific_checks.",
        "builder_review": "Generate JSON for llm_builder_review.json with review_source, passed, missing_fields, safety_concerns, fallback_recommendation.",
    }
    outputs: dict[str, Any] = {}
    for key, instruction in role_specs.items():
        prompt = f"""{instruction}
Return JSON only. Never return Python code. Force human approval and send_allowed=false where applicable.
App design: {json.dumps(app_design, ensure_ascii=False)}
Product spec: {json.dumps(product_spec, ensure_ascii=False)}
Domain pack: {json.dumps(runtime_domain_pack, ensure_ascii=False)}
Code task plan: {json.dumps(code_task_plan, ensure_ascii=False)}
"""
        try:
            value = _complete_json(llm_client, prompt, f"You are the {key} specialist for a safe scaffold-based Code Agent.")
            outputs[key] = value if isinstance(value, dict) else fallbacks[key]
            outputs[key]["source"] = f"deepseek_{key}_role"
        except Exception as exc:
            outputs[key] = dict(fallbacks[key])
            outputs[key]["llm_error"] = f"{type(exc).__name__}: {exc}"
    outputs["source"] = "deepseek_specialized_roles"
    return _validate_role_outputs(outputs, app_design, product_spec, runtime_domain_pack)


DOMAIN_LOGIC_FALLBACK = '''"""Safe generated domain logic fallback."""

from __future__ import annotations

from typing import Any


def adapt_case(case: dict, domain_data: dict, product_spec: dict) -> dict:
    """Adapt an input case for the selected scaffold without side effects."""
    return {
        "case": dict(case),
        "domain_template_id": product_spec.get("domain_template_id", ""),
        "candidate_count": len(domain_data.get("domain_candidates", [])),
        "item_count": len(domain_data.get("item_records", [])),
        "selected_scaffold_id": product_spec.get("selected_scaffold_id", ""),
        "fallback": True,
    }


def build_domain_prompt_context(adapted_case: dict, policy: dict, adapter: dict) -> dict:
    """Build compact domain context for the runtime LLM prompt."""
    return {
        "adapted_case": adapted_case,
        "policy_runtime_role": policy.get("runtime_role", ""),
        "adapter_domain": adapter.get("domain", ""),
        "reasoning_steps": adapter.get("reasoning_steps", []),
        "human_approval_required": True,
        "send_allowed": False,
    }
'''


UNSAFE_NAMES = {"open", "eval", "exec", "compile", "__import__", "input", "globals", "locals", "vars"}
UNSAFE_MODULES = {"os", "sys", "subprocess", "socket", "requests", "urllib", "pathlib", "shutil", "importlib"}


def validate_domain_logic_code(code: str) -> tuple[bool, list[str]]:
    """Validate the small generated Python plugin before writing it."""
    errors: list[str] = []
    if len(code) > 9000:
        errors.append("Generated domain logic is too long.")
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return False, [f"SyntaxError: {exc}"]
    functions = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
    if {"adapt_case", "build_domain_prompt_context"} - functions:
        errors.append("Required functions are missing.")
    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.AsyncFunctionDef, ast.Lambda)):
            errors.append("Classes, async functions, and lambdas are not allowed.")
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)) and getattr(node, "col_offset", 0) == 0:
            errors.append("Top-level assignments are not allowed.")
        if isinstance(node, ast.Expr) and getattr(node, "col_offset", 0) == 0 and not isinstance(node.value, ast.Constant):
            errors.append("Top-level executable expressions are not allowed.")
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root not in {"typing", "__future__"}:
                    errors.append(f"Unsafe import: {alias.name}")
        if isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root not in {"typing", "__future__"}:
                errors.append(f"Unsafe import: {node.module}")
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in UNSAFE_NAMES:
                errors.append(f"Unsafe call: {node.func.id}")
            if isinstance(node.func, ast.Attribute) and node.func.attr in UNSAFE_NAMES:
                errors.append(f"Unsafe attribute call: {node.func.attr}")
        if isinstance(node, ast.Name) and node.id in UNSAFE_NAMES:
            errors.append(f"Unsafe name: {node.id}")
        if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            errors.append(f"Dunder attribute is not allowed: {node.attr}")
    return not errors, sorted(set(errors))


def build_generated_domain_logic(
    app_design: dict[str, Any],
    product_spec: dict[str, Any],
    runtime_domain_pack: dict[str, Any],
    selected_opportunity: dict[str, Any],
    llm_client: Any | None = None,
) -> tuple[str, dict[str, Any]]:
    """Generate one small safe Python plugin or fall back deterministically."""
    if llm_client is None:
        return DOMAIN_LOGIC_FALLBACK, {"source": "deterministic_fallback", "valid": True, "errors": []}
    prompt = f"""Generate a small Python module for backend/generated_domain_logic.py.
Return code only. No Markdown.

Required functions:
def adapt_case(case: dict, domain_data: dict, product_spec: dict) -> dict
def build_domain_prompt_context(adapted_case: dict, policy: dict, adapter: dict) -> dict

Safety rules:
- no imports except: from __future__ import annotations, from typing import Any
- do not import re, os, sys, pathlib, urllib, requests, socket, subprocess, json, importlib, or shutil
- no file I/O, no network calls, no subprocess
- no eval/exec/open/compile/__import__
- no classes, no lambdas, no global variables, no top-level assignments
- return dictionaries only
- short code only
- use only plain dict/list/string operations and for-loops inside the two required functions

Selected scaffold: {app_design.get('selected_scaffold_id')}
App design: {json.dumps(app_design, ensure_ascii=False)}
Product spec: {json.dumps(product_spec, ensure_ascii=False)}
Runtime domain pack: {json.dumps(runtime_domain_pack, ensure_ascii=False)}
Selected opportunity: {json.dumps(selected_opportunity, ensure_ascii=False)}
"""
    try:
        code = llm_client.complete(prompt, system="Write only safe minimal Python code for a domain plugin.", json_mode=False).strip()
        if code.startswith("```"):
            code = code.strip("`")
            code = code.removeprefix("python").strip()
        valid, errors = validate_domain_logic_code(code)
        if valid:
            return code + "\n", {"source": "deepseek_domain_logic_code", "valid": True, "errors": []}
        repair_prompt = f"""Your previous backend/generated_domain_logic.py was rejected by the safety validator.
Return corrected Python code only. No Markdown.

Validation errors:
{json.dumps(errors, ensure_ascii=False)}

Previous code:
{code}

Rewrite it with only:
- optional: from __future__ import annotations
- optional: from typing import Any
- exactly these two top-level functions:
  def adapt_case(case: dict, domain_data: dict, product_spec: dict) -> dict
  def build_domain_prompt_context(adapted_case: dict, policy: dict, adapter: dict) -> dict
- no classes, no lambdas, no top-level variables, no imports besides typing/__future__
- no regex, no file/network/subprocess/eval/exec/open/compile/__import__
- dictionaries only as return values
"""
        repaired = llm_client.complete(repair_prompt, system="Repair unsafe Python into a validator-safe tiny domain plugin. Return code only.", json_mode=False).strip()
        if repaired.startswith("```"):
            repaired = repaired.strip("`")
            repaired = repaired.removeprefix("python").strip()
        repaired_valid, repaired_errors = validate_domain_logic_code(repaired)
        if repaired_valid:
            return repaired + "\n", {
                "source": "deepseek_domain_logic_code_repaired",
                "valid": True,
                "errors": [],
                "initial_errors": errors,
            }
        errors = [*errors, *[f"repair: {item}" for item in repaired_errors]]
        return DOMAIN_LOGIC_FALLBACK, {"source": "deterministic_fallback_after_unsafe_domain_logic", "valid": False, "errors": errors}
    except Exception as exc:
        return DOMAIN_LOGIC_FALLBACK, {"source": "deterministic_fallback_after_domain_logic_error", "valid": False, "errors": [f"{type(exc).__name__}: {exc}"]}


def render_python_constant(module_doc: str, constant_name: str, payload: dict[str, Any]) -> str:
    payload_json = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    return (
        f'"""{module_doc}\n\n'
        "Generated from validated JSON. This is not arbitrary LLM-written Python code.\n"
        '"""\n\n'
        "from __future__ import annotations\n\n"
        "import json\n\n"
        f"{constant_name} = json.loads({payload_json!r})\n"
    )
