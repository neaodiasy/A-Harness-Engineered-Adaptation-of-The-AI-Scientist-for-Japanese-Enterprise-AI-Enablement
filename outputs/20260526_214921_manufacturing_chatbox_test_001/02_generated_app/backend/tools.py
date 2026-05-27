"""Local deterministic tools used before DeepSeek drafting."""

from __future__ import annotations

from typing import Any

from backend.recommendation_engine import rank_domain_candidates, rank_items


def _missing_information(product_spec: dict[str, Any], case: dict[str, Any]) -> list[str]:
    text = " ".join(str(value) for value in case.values()).lower()
    domain_template = product_spec.get("domain_template", {}) if isinstance(product_spec.get("domain_template"), dict) else {}
    missing: list[str] = []
    for rule in domain_template.get("missing_information_rules", []):
        terms = [str(term).lower() for term in rule.get("terms", [])]
        if any(term and term in text for term in terms):
            missing.append(str(rule.get("message", "Additional source evidence and human approval required.")))
    missing.extend(str(item) for item in domain_template.get("always_missing_information", []))
    return sorted(set(item for item in missing if item.strip()))


def run_domain_tools(product_spec: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    ranked_candidates = rank_domain_candidates(case)
    ranked_items = rank_items(case, ranked_candidates)
    domain_template = product_spec.get("domain_template", {}) if isinstance(product_spec.get("domain_template"), dict) else {}
    return {
        "tool_name": product_spec.get("tool_name") or domain_template.get("tool_name") or "local_domain_toolkit",
        "app_kind": product_spec.get("app_kind"),
        "ranked_area_candidates": ranked_candidates[:4],
        "ranked_property_candidates": ranked_items[:4],
        "ranked_candidates": ranked_candidates[:4],
        "ranked_items": ranked_items[:4],
        "top_candidates": ranked_candidates[:4],
        "missing_information": _missing_information(product_spec, case),
        "scoring_summary_ja": domain_template.get("scoring_summary_ja") or "ローカル候補、証拠、リスク、人間承認条件をスコアリングしました。",
    }
