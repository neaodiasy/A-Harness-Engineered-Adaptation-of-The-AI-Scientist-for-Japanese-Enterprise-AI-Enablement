"""Plan-driven component selection for generated enterprise agent products.

The Code Agent should not behave like a one-off fixed demo writer. This module
turns upstream planning artifacts into an explicit component plan that the
software builder can save, inspect, and use as the contract for generated files.
"""

from __future__ import annotations

from typing import Any


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if value in (None, ""):
        return []
    return [value]


def _contains(values: list[Any], term: str) -> bool:
    term = term.lower()
    return any(term in str(value).lower() for value in values)


def build_component_plan(
    agent_design: dict[str, Any],
    architecture: dict[str, Any],
    product_spec: dict[str, Any],
    productization_blueprint: dict[str, Any],
    llm_app_design: dict[str, Any] | None = None,
    code_task_plan: dict[str, Any] | None = None,
    role_outputs: dict[str, Any] | None = None,
    selected_scaffold: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the component assembly plan consumed by the generated app package."""
    selected_primitives = _as_list(architecture.get("selected_primitives"))
    capabilities = _as_list(productization_blueprint.get("enterprise_capabilities"))
    workspace_regions = _as_list(productization_blueprint.get("workspace_regions"))
    archetype = productization_blueprint.get("selected_archetype", {}) or {}
    domain_template = product_spec.get("domain_template", {}) if isinstance(product_spec.get("domain_template"), dict) else {}
    llm_app_design = llm_app_design or {}
    code_task_plan = code_task_plan or {}
    role_outputs = role_outputs or {}
    selected_scaffold = selected_scaffold or {}
    selected_scaffold_id = str(llm_app_design.get("selected_scaffold_id") or selected_scaffold.get("scaffold_id") or "domain_operations_workbench")
    design_ui_sections = _as_list(llm_app_design.get("ui_sections"))
    design_backend_modules = _as_list(llm_app_design.get("backend_modules"))
    design_local_tools = _as_list(llm_app_design.get("local_tools"))
    design_guardrails = _as_list(llm_app_design.get("guardrails"))
    design_evaluation = _as_list(llm_app_design.get("evaluation_requirements"))
    product_feature_plan = _as_list(llm_app_design.get("product_feature_plan"))
    frontend_experience = llm_app_design.get("frontend_experience", {}) if isinstance(llm_app_design.get("frontend_experience"), dict) else {}
    specialized_roles = [
        task.get("role", "")
        for task in _as_list(code_task_plan.get("tasks"))
        if isinstance(task, dict) and task.get("role")
    ]

    modules: list[dict[str, Any]] = [
        {
            "component": "local_api_server",
            "reason": "Every generated product needs a runnable API and web entrypoint.",
            "files": ["app.py", "backend/api.py"],
            "source": "deterministic scaffold",
        },
        {
            "component": "agent_orchestrator",
            "reason": "Coordinates case input, local tools, evidence, build-time policy, domain logic plugin, runtime LLM reasoning, and guardrails.",
            "files": ["backend/agent.py", "backend/llm_client.py", "backend/generated_reasoning_policy.py", "backend/generated_domain_logic.py"],
            "source": "selected scaffold plus validated build-time policy/config/code plugin and runtime DeepSeek usage",
        },
        {
            "component": "domain_data_adapter",
            "reason": "Loads runtime domain pack data selected or auto-built for the submitted enterprise profile.",
            "files": ["domain_data.json", "data/areas.json", "data/properties.json", "data/sample_customers.json"],
            "source": "domain pack injection",
        },
        {
            "component": "approval_guardrails",
            "reason": "The planning layer requires human review for customer-facing or consequential outputs.",
            "files": ["backend/guardrails.py", "agent_spec.json"],
            "source": "deterministic scaffold plus domain risk rules",
        },
        {
            "component": "evaluation_harness",
            "reason": "The generated product must be testable through unit tests, CLI smoke tests, and API-backed evaluation.",
            "files": ["evaluation.py", "tests/test_recommendations.py"],
            "source": "deterministic scaffold",
        },
    ]

    if _contains(capabilities, "runtime_live_web_evidence_search") or _contains(selected_primitives, "search"):
        modules.append({
            "component": "runtime_evidence_search",
            "reason": "The selected workflow needs external supporting context and source freshness checks.",
            "files": ["backend/web_search.py"],
            "source": "deterministic scaffold with runtime web requests",
        })

    if _contains(capabilities, "candidate_or_result_comparison") or _contains(workspace_regions, "candidate"):
        modules.append({
            "component": "candidate_ranking_tool",
            "reason": "The productization plan asks for candidate comparison or ranked recommendations.",
            "files": ["backend/recommendation_engine.py", "backend/tools.py"],
            "source": "deterministic scaffold using domain pack records",
        })

    if _contains(capabilities, "structured_intake_form") or domain_template.get("fields"):
        modules.append({
            "component": "structured_intake_ui",
            "reason": "The domain pack defines fields that should appear as a usable product form.",
            "files": ["frontend/index.html", "frontend/app.js", "frontend/styles.css"],
            "source": "deterministic scaffold with product_spec field injection at runtime",
        })

    if _contains(capabilities, "human_approval_packet") or _contains(workspace_regions, "approval"):
        modules.append({
            "component": "approval_packet_workflow",
            "reason": "The generated app must prepare review packets instead of sending outputs automatically.",
            "files": ["backend/guardrails.py", "frontend/app.js"],
            "source": "deterministic scaffold plus runtime LLM draft",
        })

    if llm_app_design:
        modules.append({
            "component": "llm_app_design_adapter",
            "reason": "Translates DeepSeek build-time application design into generated workbench requirements.",
            "files": ["llm_app_design.json", "app_design.json", "component_plan.json", "product_spec.json"],
            "source": "validated build-time DeepSeek JSON design",
        })

    return {
        "component_plan_version": "plan_driven_builder_v1",
        "builder_mode": "deepseek_selected_scaffold_customization",
        "selected_scaffold_id": selected_scaffold_id,
        "scaffold_selection_reason": llm_app_design.get("reason_for_scaffold_selection", ""),
        "selected_archetype": {
            **archetype,
            "llm_app_design_product_archetype": llm_app_design.get("product_archetype", ""),
        },
        "source_artifacts": [
            "selected_opportunity.json",
            "agent_design.json",
            "recommended_architecture",
            "productization_blueprint.json",
            "runtime_domain_pack",
            "llm_app_design.json",
            "code_task_plan.json",
            "generated_product_rules.md",
        ],
        "inputs_consumed": {
            "selected_primitives": selected_primitives,
            "enterprise_capabilities": capabilities,
            "workspace_regions": workspace_regions,
            "domain_template_id": product_spec.get("domain_template_id", ""),
            "domain_pack_mode": productization_blueprint.get("domain_pack_mode", ""),
            "llm_app_design_source": llm_app_design.get("design_source", ""),
            "llm_ui_section_count": len(design_ui_sections),
            "llm_backend_module_count": len(design_backend_modules),
            "llm_local_tool_count": len(design_local_tools),
            "code_task_plan_source": code_task_plan.get("source", ""),
            "specialized_roles": specialized_roles,
            "selected_scaffold_id": selected_scaffold_id,
        },
        "planned_ui_sections": design_ui_sections,
        "planned_backend_modules": design_backend_modules,
        "planned_local_tools": design_local_tools,
        "planned_guardrails": design_guardrails,
        "planned_evaluation_checks": design_evaluation,
        "llm_app_design_requirements": {
            "product_archetype": llm_app_design.get("product_archetype", ""),
            "target_workflow": llm_app_design.get("target_workflow", ""),
            "primary_user": llm_app_design.get("primary_user", ""),
            "ui_sections": design_ui_sections,
            "backend_modules": design_backend_modules,
            "local_tools": design_local_tools,
            "guardrails": design_guardrails,
            "evaluation_requirements": design_evaluation,
            "domain_adaptation_notes": _as_list(llm_app_design.get("domain_adaptation_notes")),
            "small_domain_logic_requirements": _as_list(llm_app_design.get("small_domain_logic_requirements")),
            "product_feature_plan": product_feature_plan,
            "frontend_experience": frontend_experience,
        },
        "code_task_plan_source": code_task_plan.get("source", ""),
        "specialized_roles": specialized_roles,
        "generated_artifacts": [
            "llm_app_design.json",
            "generated_product_rules.md",
            "code_task_plan.json",
            "backend/generated_reasoning_policy.py",
            "backend/generated_domain_adapter.py",
            "backend/generated_domain_logic.py",
            "frontend/generated_ui_config.json",
            "frontend/generated_layout_config.json",
            "frontend/generated_interaction_config.json",
            "evaluation_checklist.json",
            "llm_builder_review.json",
        ],
        "deepseek_controls": [
            "selected_scaffold_id",
            "reason_for_scaffold_selection",
            "product_archetype",
            "target_workflow",
            "ui_sections",
            "backend_modules",
            "local_tools",
            "runtime_llm_role",
            "runtime_prompt_requirements",
            "guardrails",
            "evaluation_requirements",
            "domain-specific policy/config/adapter artifacts",
            "interactive AI copilot modes and user actions",
            "frontend experience type, layout variant, and product feature cards",
            "small generated domain logic plugin",
        ],
        "scaffold_provided_components": {
            "scaffold_id": selected_scaffold.get("scaffold_id", selected_scaffold_id),
            "purpose": selected_scaffold.get("purpose", ""),
            "default_ui_sections": selected_scaffold.get("default_ui_sections", []),
            "default_backend_modules": selected_scaffold.get("default_backend_modules", []),
            "default_local_tools": selected_scaffold.get("default_local_tools", []),
            "required_guardrails": selected_scaffold.get("required_guardrails", []),
            "default_evaluation_checks": selected_scaffold.get("default_evaluation_checks", []),
        },
        "deepseek_customized_components": {
            "ui_sections": design_ui_sections,
            "backend_modules": design_backend_modules,
            "local_tools": design_local_tools,
            "guardrails": design_guardrails,
            "evaluation_requirements": design_evaluation,
            "product_feature_plan": product_feature_plan,
            "frontend_experience": frontend_experience,
            "role_outputs": sorted(key for key in role_outputs if key != "source"),
        },
        "scaffolded_components": [
            "app.py entrypoint",
            "backend/api.py local server",
            "frontend shell",
            "guardrail framework",
            "evaluation framework",
            "sandbox compatibility",
        ],
        "modules": modules,
        "generation_contract": {
            "source_code_generation": "selected_deterministic_scaffold_with_validated_build_time_design_and_small_domain_logic_plugin",
            "build_time_llm_scope": "scaffold selection, app design, task planning, JSON policy/config artifacts, and one validated small domain logic module; no full-source app generation",
            "domain_behavior": "configured_by_runtime_domain_pack",
            "runtime_llm_usage": "backend/agent.py calls DeepSeek after the app is generated",
            "automatic_code_repair": False,
            "human_approval_required": True,
        },
        "interview_note": (
            "The planning agents are used to choose product archetype, domain pack, "
            "capabilities, UI regions, risk controls, and generated artifacts. The current "
            "implementation assembles a planned product scaffold rather than asking one LLM "
            "conversation to write arbitrary source code."
        ),
    }
