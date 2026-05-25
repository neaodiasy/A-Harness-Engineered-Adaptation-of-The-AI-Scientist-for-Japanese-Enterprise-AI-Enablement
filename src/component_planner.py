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
) -> dict[str, Any]:
    """Build the component assembly plan consumed by the generated app package."""
    selected_primitives = _as_list(architecture.get("selected_primitives"))
    capabilities = _as_list(productization_blueprint.get("enterprise_capabilities"))
    workspace_regions = _as_list(productization_blueprint.get("workspace_regions"))
    archetype = productization_blueprint.get("selected_archetype", {}) or {}
    domain_template = product_spec.get("domain_template", {}) if isinstance(product_spec.get("domain_template"), dict) else {}

    modules: list[dict[str, Any]] = [
        {
            "component": "local_api_server",
            "reason": "Every generated product needs a runnable API and web entrypoint.",
            "files": ["app.py", "backend/api.py"],
            "source": "deterministic scaffold",
        },
        {
            "component": "agent_orchestrator",
            "reason": "Coordinates case input, local tools, evidence, runtime LLM reasoning, and guardrails.",
            "files": ["backend/agent.py", "backend/llm_client.py"],
            "source": "deterministic scaffold with runtime DeepSeek usage",
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

    return {
        "component_plan_version": "plan_driven_builder_v1",
        "builder_mode": "plan_driven_scaffold_assembly",
        "selected_archetype": archetype,
        "source_artifacts": [
            "selected_opportunity.json",
            "agent_design.json",
            "recommended_architecture",
            "productization_blueprint.json",
            "runtime_domain_pack",
        ],
        "inputs_consumed": {
            "selected_primitives": selected_primitives,
            "enterprise_capabilities": capabilities,
            "workspace_regions": workspace_regions,
            "domain_template_id": product_spec.get("domain_template_id", ""),
            "domain_pack_mode": productization_blueprint.get("domain_pack_mode", ""),
        },
        "modules": modules,
        "generation_contract": {
            "source_code_generation": "deterministic_scaffold_with_variable_injection",
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
