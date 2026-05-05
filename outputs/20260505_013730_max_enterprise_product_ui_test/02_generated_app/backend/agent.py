"""Agent orchestration for the generated product."""

from __future__ import annotations

import json
from typing import Any

from backend.data_store import load_agent_spec, load_knowledge_base, load_product_spec
from backend.guardrails import enforce_output_contract
from backend.llm_client import complete_json
from backend.tools import run_domain_tools
from backend.web_search import search_web_evidence


PRODUCT_SPEC = load_product_spec()
AGENT_SPEC = load_agent_spec()
KNOWLEDGE_BASE = load_knowledge_base()


def retrieve_evidence(case: dict[str, Any], local_tool_results: dict[str, Any]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = [
        {
            "id": "local_area_profiles",
            "title": "Generated local area profiles",
            "summary": "Area candidates and scoring inputs loaded from data/areas.json.",
        },
        {
            "id": "local_property_listings",
            "title": "Generated local property listings",
            "summary": "Property candidates and scoring inputs loaded from data/properties.json.",
        },
        {
            "id": "knowledge_base",
            "title": "Generated knowledge base",
            "summary": KNOWLEDGE_BASE[:700],
        },
    ]
    for area in local_tool_results.get("ranked_area_candidates", [])[:3]:
        evidence.append({
            "id": f"area_{area['area_id']}",
            "title": area["name_ja"],
            "summary": f"{area.get('summary_ja', '')} {area.get('risk_note_ja', '')}",
        })
    live_pack = search_web_evidence(case, PRODUCT_SPEC, local_tool_results)
    for item in live_pack.get("results", []):
        evidence.append(item)
    evidence.append({
        "id": "runtime_live_search_metadata",
        "title": "Runtime live web search metadata",
        "summary": json.dumps(live_pack.get("metadata", {}), ensure_ascii=False),
        "retrieval_method": "runtime_live_web_search_metadata",
    })
    return evidence


def build_prompt(case: dict[str, Any], local_tool_results: dict[str, Any], evidence: list[dict[str, Any]]) -> str:
    return f"""You are drafting the reasoning layer for an AI-driven real-estate recommendation platform.

Product spec:
{json.dumps(PRODUCT_SPEC, ensure_ascii=False, indent=2)}

Customer case:
{json.dumps(case, ensure_ascii=False, indent=2)}

Deterministic local tool results. You must use these concrete area and property names:
{json.dumps(local_tool_results, ensure_ascii=False, indent=2)}

Evidence:
{json.dumps(evidence, ensure_ascii=False, indent=2)}

Return one JSON object with these keys:
case_id, classification, evidence, missing_information, recommendation_ja,
customer_or_business_draft_ja, internal_review_note, risk, approval_packet.

Rules:
- Use concrete local tool candidate names such as 武蔵小杉, 国立, 和光市, 町田 when relevant.
- Use runtime_live_web_search evidence when available, but describe it as supporting context that requires human verification.
- Do not say エリアA, エリアB, エリアC, Area A, Area B, or Area C.
- Do not claim legal, financial, investment, disaster-safety, or earthquake-resilience guarantees.
- Use Japanese for recommendation_ja, customer_or_business_draft_ja, and internal_review_note.
- Mention missing hazard map, earthquake resilience, school zone, listing freshness, and human review needs.
- The final app will force human_approval_required=true and send_allowed=false.
"""


def run_case(case: dict[str, Any]) -> dict[str, Any]:
    local_tool_results = run_domain_tools(PRODUCT_SPEC, case)
    evidence = retrieve_evidence(case, local_tool_results)
    llm_output = complete_json(AGENT_SPEC["system_prompt"], build_prompt(case, local_tool_results, evidence))
    return enforce_output_contract(case, llm_output, local_tool_results, evidence, AGENT_SPEC)
