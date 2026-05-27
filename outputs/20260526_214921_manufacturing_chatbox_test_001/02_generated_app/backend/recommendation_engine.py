"""Deterministic ranking engine for generated local tool use."""

from __future__ import annotations

import re
from typing import Any

from backend.data_store import load_areas, load_properties


def _numbers(value: Any) -> list[float]:
    return [float(item) for item in re.findall(r"\d+(?:\.\d+)?", str(value))]


def _first_number(value: Any, default: float) -> float:
    numbers = _numbers(value)
    return numbers[0] if numbers else default


def _budget_ceiling(value: Any, default: float = 65.0) -> float:
    numbers = _numbers(value)
    return max(numbers) if numbers else default


def _case_text(case: dict[str, Any]) -> str:
    return " ".join(str(value) for value in case.values()).lower()


def _wants(case: dict[str, Any], terms: list[str]) -> bool:
    text = _case_text(case)
    return any(term.lower() in text for term in terms)


def _numeric(item: dict[str, Any], keys: list[str], default: float = 0.0) -> float:
    for key in keys:
        if key in item:
            return float(item.get(key) or default)
    return default


def _time_or_effort_value(candidate: dict[str, Any]) -> float:
    for key, value in candidate.items():
        if key.startswith("commute_minutes"):
            return float(value or 0)
    return float(candidate.get("commute_minutes", candidate.get("time_or_effort_index", 0)) or 0)


def score_candidate(candidate: dict[str, Any], case: dict[str, Any]) -> tuple[float, list[str]]:
    ceiling = _budget_ceiling(case.get("budget"))
    effort_limit = _first_number(case.get("max_commute_minutes", case.get("max_effort_index", "")), 45.0)
    score = 0.0
    reasons: list[str] = []

    cost = _numeric(candidate, ["typical_budget_jpy_m", "estimated_cost", "cost_score_base"], 50.0)
    budget_score = max(0.0, 25.0 - abs(cost - ceiling) * 1.1)
    score += budget_score
    reasons.append(f"予算・コスト目安 {cost:g} に対して適合度を評価")

    effort_value = _time_or_effort_value(candidate)
    if effort_value:
        effort_gap = max(0.0, effort_value - effort_limit)
        effort_score = max(0.0, 22.0 - effort_gap * 1.8)
        score += effort_score
        reasons.append(f"時間・工数・アクセス指標 {effort_value:g} を条件と比較")

    if _wants(case, ["school", "学校", "学区", "子ども", "子供", "family", "ファミリー"]):
        score += _numeric(candidate, ["relevance_score", "school_score"], 5.0) * 2.0 + _numeric(candidate, ["user_fit_score", "family_score"], 5.0) * 1.5
        reasons.append("家族・教育・利用者適合に関する指標を加点")

    if _wants(case, ["quiet", "静か", "閑静", "落ち着", "stable", "安定"]):
        score += _numeric(candidate, ["quiet_score", "stability_score"], 5.0) * 2.1
        reasons.append("安定性・静穏性・運用品質に関する指標を加点")

    if _wants(case, ["risk", "safety", "resilience", "exception", "災害", "リスク", "例外"]):
        score += _numeric(candidate, ["risk_readiness_score", "family_score"], 5.0) * 0.4
        reasons.append("リスク確認は個別証拠と人間承認が必要")

    return round(score, 2), reasons


def rank_domain_candidates(case: dict[str, Any]) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    for candidate in load_areas():
        score, reasons = score_candidate(candidate, case)
        item = dict(candidate)
        item.update({"score": score, "reason_ja": "。".join(reasons) + "。"})
        ranked.append(item)
    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked


def score_item(item: dict[str, Any], candidate_rank: dict[str, dict[str, Any]], case: dict[str, Any]) -> tuple[float, list[str]]:
    ceiling = _budget_ceiling(case.get("budget"))
    score = 0.0
    reasons: list[str] = []
    parent = candidate_rank.get(str(item.get("area_id", "")), {})

    score += float(parent.get("score", 0)) * 0.45
    reasons.append(f"上位候補評価を反映: {parent.get('name_ja', item.get('area_id', 'candidate'))}")

    price = _numeric(item, ["price_jpy_m", "estimated_cost", "cost"], ceiling)
    price_gap = max(0.0, price - ceiling)
    score += 22.0 if price_gap == 0 else max(0.0, 22.0 - price_gap * 3.0)
    reasons.append(f"コスト・価格指標 {price:g}")

    if _wants(case, ["station", "駅", "通勤", "commute", "access"]):
        score += max(0.0, 18.0 - _numeric(item, ["station_walk_minutes", "access_minutes"], 8.0) * 0.8)
        reasons.append("アクセス条件を評価")

    if _wants(case, ["school", "学校", "family", "子ども", "ファミリー"]):
        score += _numeric(item, ["relevance_score", "school_score"], 5.0) * 1.5 + _numeric(item, ["user_fit_score", "family_score"], 5.0) * 1.5
        reasons.append("利用者適合・家族条件を評価")

    if _wants(case, ["risk", "safety", "resilience", "exception", "災害", "リスク", "例外"]):
        score += _numeric(item, ["earthquake_score", "risk_readiness_score"], 5.0) * 1.4
        reasons.append("リスク関連指標を評価")

    return round(score, 2), reasons


def rank_items(case: dict[str, Any], ranked_candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidate_rank = {str(candidate.get("area_id", candidate.get("id", ""))): candidate for candidate in ranked_candidates}
    ranked: list[dict[str, Any]] = []
    for source_item in load_properties():
        score, reasons = score_item(source_item, candidate_rank, case)
        item = dict(source_item)
        parent_id = str(item.get("area_id", ""))
        item.update({
            "area_name_ja": candidate_rank.get(parent_id, {}).get("name_ja", parent_id),
            "score": score,
            "reason_ja": "。".join(reasons) + "。",
        })
        ranked.append(item)
    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked
