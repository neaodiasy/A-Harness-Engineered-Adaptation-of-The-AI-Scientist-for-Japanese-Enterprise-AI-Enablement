"""Output contract and safety guardrails."""

from __future__ import annotations

from typing import Any


PLACEHOLDERS = ["エリアA", "エリアB", "エリアC", "Area A", "Area B", "Area C"]
FORBIDDEN_GUARANTEES = ["保証します", "確約します", "絶対に安全", "投資利益", "必ず値上がり", "法的助言"]


def _candidate_names(local_tool_results: dict[str, Any]) -> list[str]:
    return [
        str(item.get("name_ja", ""))
        for item in local_tool_results.get("ranked_area_candidates", [])
        if item.get("name_ja")
    ]


def _property_titles(local_tool_results: dict[str, Any]) -> list[str]:
    return [
        str(item.get("title_ja", ""))
        for item in local_tool_results.get("ranked_property_candidates", [])
        if item.get("title_ja")
    ]


def _placeholder_only(text: str, names: list[str]) -> bool:
    return any(token in text for token in PLACEHOLDERS) and not any(name in text for name in names)


def deterministic_recommendation(local_tool_results: dict[str, Any]) -> str:
    areas = local_tool_results.get("ranked_area_candidates", [])[:3]
    properties = local_tool_results.get("ranked_property_candidates", [])[:3]
    area_lines = [
        f"{index}. {area['name_ja']}（スコア{area['score']}）: {area.get('summary_ja', '')} 注意点: {area.get('risk_note_ja', '')}"
        for index, area in enumerate(areas, start=1)
    ]
    property_lines = [
        f"{index}. {prop['title_ja']}（{prop.get('area_name_ja', '')}、スコア{prop['score']}）: {prop.get('summary_ja', '')}"
        for index, prop in enumerate(properties, start=1)
    ]
    return (
        "ローカルランキングでは、候補は次の順で確認する価値があります。\n"
        + "\n".join(area_lines)
        + "\n\n関連候補は次の順で追加確認してください。\n"
        + "\n".join(property_lines)
        + "\n\nリスク、証拠の鮮度、適用条件、承認境界は人間の担当者が確認してください。"
    )


def _classification(case: dict[str, Any], output: dict[str, Any]) -> dict[str, Any]:
    classification = output.get("classification")
    if not isinstance(classification, dict):
        classification = {}
    label = classification.get("label") or "preference_based_recommendation"
    rationale = classification.get("rationale") or "業務要件、候補スコア、証拠、人間承認条件に基づく推奨ケースです。"
    try:
        confidence = float(classification.get("confidence", 0.78))
    except (TypeError, ValueError):
        confidence = 0.78
    if confidence == 0.5:
        confidence = 0.78
    return {"label": label, "confidence": round(max(0.55, min(confidence, 0.95)), 2), "rationale": rationale}


def enforce_output_contract(
    case: dict[str, Any],
    output: dict[str, Any],
    local_tool_results: dict[str, Any],
    evidence: list[dict[str, Any]],
    agent_spec: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(output, dict):
        output = {}
    area_names = _candidate_names(local_tool_results)
    property_titles = _property_titles(local_tool_results)
    deterministic_text = deterministic_recommendation(local_tool_results)

    recommendation = str(output.get("recommendation_ja", "")).strip()
    if not recommendation or _placeholder_only(recommendation, area_names):
        recommendation = deterministic_text
    draft = str(output.get("customer_or_business_draft_ja", "")).strip()
    if not draft or _placeholder_only(draft, area_names):
        draft = (
            "以下は担当者確認用のドラフトです。"
            + recommendation
            + "\n\nこの内容は送信前に指定された承認者が確認してください。"
        )

    risk = output.get("risk") if isinstance(output.get("risk"), dict) else {}
    reasons = list(risk.get("risk_reasons", [])) if isinstance(risk.get("risk_reasons"), list) else []
    reasons.extend(local_tool_results.get("missing_information", []))
    for phrase in FORBIDDEN_GUARANTEES:
        if phrase in recommendation or phrase in draft:
            reasons.append(f"保証表現を削除または修正してください: {phrase}")
            recommendation = recommendation.replace(phrase, "確認が必要です")
            draft = draft.replace(phrase, "確認が必要です")

    approval_packet = output.get("approval_packet") if isinstance(output.get("approval_packet"), dict) else {}
    approval_packet.update({
        "approval_required": True,
        "approval_owner": case.get("approval_owner", "Human reviewer"),
        "decision_options": ["approve", "edit", "reject", "request_more_information"],
        "reviewer_guidance": agent_spec.get("reviewer_guidance", []),
        "items_to_verify": local_tool_results.get("missing_information", []),
        "top_area_names": area_names[:3],
        "top_property_titles": property_titles[:3],
    })

    return {
        "case_id": case.get("case_id") or case.get("id") or "manual_case",
        "classification": _classification(case, output),
        "ranked_area_candidates": local_tool_results.get("ranked_area_candidates", []),
        "ranked_property_candidates": local_tool_results.get("ranked_property_candidates", []),
        "local_tool_results": local_tool_results,
        "evidence": evidence,
        "missing_information": sorted(set(local_tool_results.get("missing_information", []) + output.get("missing_information", []))),
        "recommendation_ja": recommendation,
        "customer_or_business_draft_ja": draft,
        "internal_review_note": output.get("internal_review_note") or "ローカルランキング、LLMドラフト、リスク項目を確認し、顧客送信前に人間が編集・承認してください。",
        "risk": {
            "risk_flag": True,
            "risk_level": risk.get("risk_level", "medium"),
            "risk_reasons": sorted(set(str(item) for item in reasons if str(item).strip())),
        },
        "human_approval_required": True,
        "send_allowed": False,
        "approval_packet": approval_packet,
        "audit_trace": {
            "tool_names": [local_tool_results.get("tool_name", "local_tools")],
            "evidence_ids": [item.get("id") for item in evidence],
            "model": agent_spec.get("model", "deepseek-v4-pro"),
            "output_contract_enforced": True,
            "deterministic_candidates_attached": True,
        },
    }
