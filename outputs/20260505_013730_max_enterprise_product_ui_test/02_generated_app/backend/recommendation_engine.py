"""Deterministic recommendation engine for local tool use."""

from __future__ import annotations

import re
from typing import Any

from backend.data_store import load_areas, load_properties


def _numbers(value: Any) -> list[float]:
    return [float(item) for item in re.findall(r"\d+(?:\.\d+)?", str(value))]


def budget_ceiling_m(value: Any, default: float = 65.0) -> float:
    numbers = _numbers(value)
    if not numbers:
        return default
    return max(numbers)


def max_commute_minutes(case: dict[str, Any], default: float = 45.0) -> float:
    numbers = _numbers(case.get("max_commute_minutes", ""))
    return numbers[0] if numbers else default


def _case_text(case: dict[str, Any]) -> str:
    return " ".join(str(value) for value in case.values()).lower()


def _wants(case: dict[str, Any], terms: list[str]) -> bool:
    text = _case_text(case)
    return any(term.lower() in text for term in terms)


def score_area(area: dict[str, Any], case: dict[str, Any]) -> tuple[float, list[str]]:
    ceiling = budget_ceiling_m(case.get("budget"))
    commute_limit = max_commute_minutes(case)
    score = 0.0
    reasons: list[str] = []

    price_gap = abs(float(area["typical_budget_jpy_m"]) - ceiling)
    budget_score = max(0.0, 25.0 - price_gap * 1.1)
    score += budget_score
    reasons.append(f"予算上限{ceiling:.0f}百万円に対してエリア目安は{area['typical_budget_jpy_m']}百万円")

    commute_gap = max(0.0, float(area["commute_minutes_to_shinjuku"]) - commute_limit)
    commute_score = max(0.0, 22.0 - commute_gap * 1.8)
    if _wants(case, ["commute", "通勤", "新宿", "access", "駅"]):
        commute_score += float(area["station_access"]) * 1.3
    score += commute_score
    reasons.append(f"新宿まで約{area['commute_minutes_to_shinjuku']}分、駅アクセス{area['station_access']}/10")

    if _wants(case, ["school", "学校", "学区", "子ども", "子供", "family", "ファミリー"]):
        score += float(area["school_score"]) * 2.0 + float(area["family_score"]) * 1.5
        reasons.append(f"学校評価{area['school_score']}/10、ファミリー適性{area['family_score']}/10")

    if _wants(case, ["quiet", "静か", "閑静", "落ち着"]):
        score += float(area["quiet_score"]) * 2.1
        reasons.append(f"静かな住環境評価{area['quiet_score']}/10")

    if _wants(case, ["hazard", "earthquake", "resilience", "災害", "耐震", "ハザード"]):
        score += float(area.get("family_score", 0)) * 0.4
        reasons.append("災害・耐震は物件単位の追加確認が必要")

    return round(score, 2), reasons


def rank_real_estate_areas(case: dict[str, Any]) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    for area in load_areas():
        score, reasons = score_area(area, case)
        item = dict(area)
        item.update({
            "score": score,
            "reason_ja": "。".join(reasons) + "。",
        })
        ranked.append(item)
    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked


def score_property(prop: dict[str, Any], area_rank: dict[str, dict[str, Any]], case: dict[str, Any]) -> tuple[float, list[str]]:
    ceiling = budget_ceiling_m(case.get("budget"))
    score = 0.0
    reasons: list[str] = []
    area = area_rank.get(prop["area_id"], {})

    area_score = float(area.get("score", 0)) * 0.45
    score += area_score
    reasons.append(f"エリア評価を反映: {area.get('name_ja', prop['area_id'])}")

    price_gap = max(0.0, float(prop["price_jpy_m"]) - ceiling)
    price_score = 22.0 if price_gap == 0 else max(0.0, 22.0 - price_gap * 3.0)
    score += price_score
    reasons.append(f"価格{prop['price_jpy_m']}百万円")

    if _wants(case, ["station", "駅", "通勤", "commute"]):
        walk_score = max(0.0, 18.0 - float(prop["station_walk_minutes"]) * 0.8)
        score += walk_score
        reasons.append(f"駅徒歩{prop['station_walk_minutes']}分")

    if _wants(case, ["school", "学校", "family", "子ども", "ファミリー"]):
        score += float(prop["school_score"]) * 1.5 + float(prop["family_score"]) * 1.5
        reasons.append(f"学校・ファミリー評価 {prop['school_score']}/{prop['family_score']}")

    if _wants(case, ["quiet", "静か", "閑静"]):
        score += float(prop["quiet_score"]) * 1.5
        reasons.append(f"静かさ評価{prop['quiet_score']}/10")

    if _wants(case, ["earthquake", "耐震", "災害", "hazard"]):
        score += float(prop["earthquake_score"]) * 1.4
        reasons.append(f"耐震関連評価{prop['earthquake_score']}/10")

    return round(score, 2), reasons


def rank_properties(case: dict[str, Any], ranked_areas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    area_rank = {area["area_id"]: area for area in ranked_areas}
    ranked: list[dict[str, Any]] = []
    for prop in load_properties():
        score, reasons = score_property(prop, area_rank, case)
        item = dict(prop)
        item.update({
            "area_name_ja": area_rank.get(prop["area_id"], {}).get("name_ja", prop["area_id"]),
            "score": score,
            "reason_ja": "。".join(reasons) + "。",
        })
        ranked.append(item)
    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked
