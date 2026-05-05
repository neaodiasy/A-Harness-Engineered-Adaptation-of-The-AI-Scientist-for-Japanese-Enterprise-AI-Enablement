"""Local deterministic tools used before DeepSeek drafting."""

from __future__ import annotations

from typing import Any

from backend.recommendation_engine import rank_properties, rank_real_estate_areas


def _missing_information(case: dict[str, Any]) -> list[str]:
    text = " ".join(str(value) for value in case.values()).lower()
    missing: list[str] = []
    if any(term in text for term in ["hazard", "災害", "ハザード", "earthquake", "耐震"]):
        missing.append("物件ごとのハザードマップ、浸水想定、耐震等級、管理状況")
    if any(term in text for term in ["school", "学校", "学区", "子ども", "子供"]):
        missing.append("最新の学校区、通学距離、保育園・学童の空き状況")
    if any(term in text for term in ["commute", "通勤", "新宿"]):
        missing.append("実際の通勤時間帯での混雑、乗換、終電情報")
    missing.append("掲載価格、販売状況、重要事項説明、現地確認結果")
    return sorted(set(missing))


def run_domain_tools(product_spec: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    ranked_areas = rank_real_estate_areas(case)
    ranked_properties = rank_properties(case, ranked_areas)
    return {
        "tool_name": "real_estate_recommendation_toolkit",
        "app_kind": product_spec.get("app_kind"),
        "ranked_area_candidates": ranked_areas[:4],
        "ranked_property_candidates": ranked_properties[:4],
        "top_candidates": ranked_areas[:4],
        "missing_information": _missing_information(case),
        "scoring_summary_ja": (
            "予算、通勤、駅アクセス、学校・ファミリー適性、静かな住環境、耐震・災害確認の必要性を"
            "ローカルデータでスコアリングしました。"
        ),
    }
