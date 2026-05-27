"""Agent orchestration for the generated product."""

from __future__ import annotations

import json
import os
from typing import Any

from backend.data_store import load_agent_spec, load_domain_data, load_interaction_config, load_knowledge_base, load_llm_app_design, load_product_spec
from backend.guardrails import enforce_output_contract
from backend.llm_client import complete_json
from backend.tools import run_domain_tools
from backend.web_search import search_web_evidence

try:
    from backend.generated_reasoning_policy import GENERATED_REASONING_POLICY
except Exception:
    GENERATED_REASONING_POLICY = {}

try:
    from backend.generated_domain_adapter import GENERATED_DOMAIN_ADAPTER
except Exception:
    GENERATED_DOMAIN_ADAPTER = {}

try:
    from backend.generated_domain_logic import adapt_case, build_domain_prompt_context
except Exception:
    def adapt_case(case: dict, domain_data: dict, product_spec: dict) -> dict:
        return {"case": case, "fallback": True}

    def build_domain_prompt_context(adapted_case: dict, policy: dict, adapter: dict) -> dict:
        return {"adapted_case": adapted_case, "policy": policy, "adapter": adapter}


PRODUCT_SPEC = load_product_spec()
AGENT_SPEC = load_agent_spec()
DOMAIN_DATA = load_domain_data()
LLM_APP_DESIGN = load_llm_app_design()
INTERACTION_CONFIG = load_interaction_config()
KNOWLEDGE_BASE = load_knowledge_base()


def retrieve_evidence(case: dict[str, Any], local_tool_results: dict[str, Any]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = [
        {
            "id": "local_candidate_profiles",
            "title": "Generated local candidate profiles",
            "summary": "Domain candidates and scoring inputs loaded from data/areas.json.",
        },
        {
            "id": "local_item_records",
            "title": "Generated local item records",
            "summary": "Related item candidates and scoring inputs loaded from data/properties.json.",
        },
        {
            "id": "knowledge_base",
            "title": "Generated knowledge base",
            "summary": KNOWLEDGE_BASE[:700],
        },
    ]
    for area in local_tool_results.get("ranked_area_candidates", [])[:3]:
        candidate_id = area.get("area_id") or area.get("id") or area.get("name_ja", "candidate")
        evidence.append({
            "id": f"candidate_{candidate_id}",
            "title": area.get("name_ja", str(candidate_id)),
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


def build_prompt(
    case: dict[str, Any],
    local_tool_results: dict[str, Any],
    evidence: list[dict[str, Any]],
    domain_prompt_context: dict[str, Any],
) -> str:
    candidate_examples = PRODUCT_SPEC.get("candidate_examples", [])
    specific_rules = PRODUCT_SPEC.get("specific_rules", [])
    policy = GENERATED_REASONING_POLICY if isinstance(GENERATED_REASONING_POLICY, dict) else {}
    adapter = GENERATED_DOMAIN_ADAPTER if isinstance(GENERATED_DOMAIN_ADAPTER, dict) else {}
    return f"""You are drafting the reasoning layer for this generated enterprise agent product:
{PRODUCT_SPEC.get("prompt_context", PRODUCT_SPEC.get("product_name", "enterprise product"))}

Build-time app design summary:
{json.dumps(LLM_APP_DESIGN, ensure_ascii=False, indent=2)}

Build-time generated runtime reasoning policy:
{json.dumps(policy, ensure_ascii=False, indent=2)}

Build-time generated domain adapter:
{json.dumps(adapter, ensure_ascii=False, indent=2)}

Build-time generated domain logic prompt context:
{json.dumps(domain_prompt_context, ensure_ascii=False, indent=2)}

Product spec:
{json.dumps(PRODUCT_SPEC, ensure_ascii=False, indent=2)}

Domain data summary:
{json.dumps({key: len(value) if isinstance(value, list) else value for key, value in DOMAIN_DATA.items()}, ensure_ascii=False, indent=2)}

Customer case:
{json.dumps(case, ensure_ascii=False, indent=2)}

Deterministic local tool results. You must use concrete candidate names from these results:
{json.dumps(local_tool_results, ensure_ascii=False, indent=2)}

Evidence:
{json.dumps(evidence, ensure_ascii=False, indent=2)}

Candidate examples from the selected domain template:
{json.dumps(candidate_examples, ensure_ascii=False, indent=2)}

Domain-specific rules from the selected template:
{json.dumps(specific_rules, ensure_ascii=False, indent=2)}

Return one JSON object with these keys:
case_id, classification, evidence, missing_information, recommendation_ja,
customer_or_business_draft_ja, internal_review_note, risk, approval_packet.

Rules:
- Follow the build-time generated runtime reasoning policy when it is stricter or more domain-specific.
- Use concrete local tool candidate names when relevant.
- Use runtime_live_web_search evidence when available, but describe it as supporting context that requires human verification.
- Do not say エリアA, エリアB, エリアC, Area A, Area B, or Area C.
- Do not claim legal, financial, investment, disaster-safety, or earthquake-resilience guarantees.
- Use Japanese for recommendation_ja, customer_or_business_draft_ja, and internal_review_note.
- Mention missing evidence, uncertainty, source freshness, risk checks, and human review needs.
- The final app will force human_approval_required=true and send_allowed=false.
"""


def _selected_action(action_id: str) -> dict[str, Any]:
    for action in INTERACTION_CONFIG.get("user_actions", []):
        if isinstance(action, dict) and action.get("id") == action_id:
            return action
    actions = INTERACTION_CONFIG.get("user_actions", [])
    return actions[0] if actions and isinstance(actions[0], dict) else {}


def build_interaction_prompt(
    payload: dict[str, Any],
    case: dict[str, Any],
    local_tool_results: dict[str, Any],
    evidence: list[dict[str, Any]],
    domain_prompt_context: dict[str, Any],
) -> str:
    action = _selected_action(str(payload.get("action_id", "")))
    policy = GENERATED_REASONING_POLICY if isinstance(GENERATED_REASONING_POLICY, dict) else {}
    adapter = GENERATED_DOMAIN_ADAPTER if isinstance(GENERATED_DOMAIN_ADAPTER, dict) else {}
    message = str(payload.get("message", "")).strip()
    return f"""You are the interactive AI copilot inside a generated enterprise product.
The user is interacting with the generated app, not asking for a generic chatbot answer.

Selected interaction action:
{json.dumps(action, ensure_ascii=False, indent=2)}

User message:
{message}

Interaction configuration:
{json.dumps(INTERACTION_CONFIG, ensure_ascii=False, indent=2)}

Build-time app design:
{json.dumps(LLM_APP_DESIGN, ensure_ascii=False, indent=2)}

Generated runtime policy:
{json.dumps(policy, ensure_ascii=False, indent=2)}

Generated domain adapter:
{json.dumps(adapter, ensure_ascii=False, indent=2)}

Generated domain prompt context:
{json.dumps(domain_prompt_context, ensure_ascii=False, indent=2)}

Current case:
{json.dumps(case, ensure_ascii=False, indent=2)}

Local tool results:
{json.dumps(local_tool_results, ensure_ascii=False, indent=2)}

Evidence:
{json.dumps(evidence, ensure_ascii=False, indent=2)}

Return one JSON object with these keys:
reply_ja, used_evidence, suggested_next_actions, risk, approval_note,
human_approval_required, send_allowed.

Rules:
- This is an interactive business copilot for the selected scaffold and enterprise scenario.
- Answer the user's actual message and selected action.
- Use local tool results and evidence IDs when relevant.
- Ask for missing information when the request cannot be handled safely.
- Never send messages, approve decisions, or make final legal/financial/medical/HR/safety/regulated decisions.
- human_approval_required must be true and send_allowed must be false.
"""


def enforce_interaction_contract(output: dict[str, Any], evidence: list[dict[str, Any]], action_id: str) -> dict[str, Any]:
    if not isinstance(output, dict):
        output = {}
    risk = output.get("risk") if isinstance(output.get("risk"), dict) else {}
    used_evidence = output.get("used_evidence")
    if not isinstance(used_evidence, list):
        used_evidence = [item.get("id") for item in evidence[:5] if item.get("id")]
    next_actions = output.get("suggested_next_actions")
    if not isinstance(next_actions, list) or not next_actions:
        next_actions = ["Verify evidence", "Edit draft", "Request human approval"]
    return {
        "action_id": action_id,
        "reply_ja": str(output.get("reply_ja") or output.get("answer") or "追加情報と人間の確認が必要です。"),
        "used_evidence": used_evidence,
        "suggested_next_actions": [str(item) for item in next_actions[:6]],
        "risk": {
            "risk_flag": True,
            "risk_level": risk.get("risk_level", "medium"),
            "risk_reasons": risk.get("risk_reasons", ["Human approval is required before operational use."]),
        },
        "approval_note": str(output.get("approval_note") or "この回答はドラフトです。顧客向け・業務上重要な利用前に人間の承認が必要です。"),
        "human_approval_required": True,
        "send_allowed": False,
    }


def run_case(case: dict[str, Any]) -> dict[str, Any]:
    local_tool_results = run_domain_tools(PRODUCT_SPEC, case)
    evidence = retrieve_evidence(case, local_tool_results)
    policy = GENERATED_REASONING_POLICY if isinstance(GENERATED_REASONING_POLICY, dict) else {}
    adapter = GENERATED_DOMAIN_ADAPTER if isinstance(GENERATED_DOMAIN_ADAPTER, dict) else {}
    adapted_case = adapt_case(case, DOMAIN_DATA, PRODUCT_SPEC)
    domain_prompt_context = build_domain_prompt_context(adapted_case, policy, adapter)
    llm_output = complete_json(AGENT_SPEC["system_prompt"], build_prompt(case, local_tool_results, evidence, domain_prompt_context))
    return enforce_output_contract(case, llm_output, local_tool_results, evidence, AGENT_SPEC)


def run_interaction(payload: dict[str, Any]) -> dict[str, Any]:
    case = payload.get("case") if isinstance(payload.get("case"), dict) else {}
    if not case:
        case = {key: value for key, value in payload.items() if key not in {"message", "action_id"}}
    local_tool_results = run_domain_tools(PRODUCT_SPEC, case)
    evidence = retrieve_evidence(case, local_tool_results)
    policy = GENERATED_REASONING_POLICY if isinstance(GENERATED_REASONING_POLICY, dict) else {}
    adapter = GENERATED_DOMAIN_ADAPTER if isinstance(GENERATED_DOMAIN_ADAPTER, dict) else {}
    adapted_case = adapt_case(case, DOMAIN_DATA, PRODUCT_SPEC)
    domain_prompt_context = build_domain_prompt_context(adapted_case, policy, adapter)
    action_id = str(payload.get("action_id", "general"))
    system_prompt = (
        AGENT_SPEC["system_prompt"]
        + "\nYou are now serving the generated app's interactive AI copilot. Return JSON only."
    )
    api_error = ""
    try:
        llm_output = complete_json(system_prompt, build_interaction_prompt(payload, case, local_tool_results, evidence, domain_prompt_context))
    except Exception as exc:
        api_error = f"{type(exc).__name__}: {exc}"
        llm_output = {
            "reply_ja": (
                "DeepSeek API の呼び出しに失敗しました。"
                "この画面は対話リクエストを受け取り、ローカルツールと証拠取得までは実行しましたが、"
                "最終的な AI 応答生成でエラーになりました。"
                "DEEPSEEK_API_KEY、DEEPSEEK_BASE_URL、AGENT_MODEL、ネットワーク、または API 応答形式を確認してください。"
            ),
            "used_evidence": [item.get("id") for item in evidence[:5] if item.get("id")],
            "suggested_next_actions": [
                "Check the generated app server terminal for the DeepSeek error.",
                "Confirm DEEPSEEK_API_KEY is exported in the same terminal that started app.py.",
                "Retry the same Copilot action after the API environment is fixed.",
            ],
            "risk": {"risk_level": "medium", "risk_reasons": ["Runtime DeepSeek API call failed."]},
            "approval_note": "API エラー時の回答は診断用です。業務利用前に人間が確認してください。",
        }
    result = enforce_interaction_contract(llm_output, evidence, action_id)
    if api_error:
        result["api_error"] = api_error
        result["api_attempted"] = True
        result["runtime_status"] = "deepseek_api_error"
    else:
        result["api_attempted"] = True
        result["runtime_status"] = "deepseek_api_success"
    return result
