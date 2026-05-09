"""Domain template loading for generated enterprise products.

The core harness must stay domain-neutral. Concrete case-study data lives under
templates/*/domain_pack.json and is selected at runtime from the enterprise
profile, opportunity, and product plan.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = REPO_ROOT / "templates"


def _blob(*values: object) -> str:
    return " ".join(str(value) for value in values).lower()


def load_domain_templates(template_root: Path = TEMPLATE_ROOT) -> list[dict[str, Any]]:
    """Load all available domain packs from templates/*/domain_pack.json."""
    packs: list[dict[str, Any]] = []
    for path in sorted(template_root.glob("*/domain_pack.json")):
        try:
            pack = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        pack.setdefault("template_id", path.parent.name)
        pack.setdefault("source_path", str(path.relative_to(REPO_ROOT)))
        packs.append(pack)
    return packs


def select_domain_template(*context: object) -> dict[str, Any] | None:
    """Select the best matching domain pack, if any match the current context."""
    text = _blob(*context)
    best_pack: dict[str, Any] | None = None
    best_score = 0
    for pack in load_domain_templates():
        terms = [str(term).lower() for term in pack.get("match_terms", [])]
        score = sum(1 for term in terms if term and term in text)
        if score > best_score:
            best_score = score
            best_pack = pack
    return best_pack if best_score > 0 else None


def generic_domain_template(opportunity_name: str, subtitle: str) -> dict[str, Any]:
    """Return a domain-neutral template for non-demo enterprise profiles."""
    return {
        "template_id": "generic_enterprise",
        "source_path": "generated_generic_template",
        "product_name": f"{opportunity_name} Platform",
        "subtitle": subtitle or "Generated enterprise agent product.",
        "primary_action": "Generate Approval Packet",
        "tool_name": "generic_enterprise_toolkit",
        "candidate_collection_label": "workflow candidates",
        "item_collection_label": "execution options",
        "default_classification_label": "enterprise_workflow_case",
        "prompt_context": "AI-driven Japanese enterprise enablement product",
        "candidate_examples": [],
        "fields": [
            {
                "key": "request",
                "label": "Business request",
                "type": "textarea",
                "required": True,
                "default": "Describe the workflow case to process.",
            },
            {
                "key": "evidence_summary",
                "label": "Evidence summary",
                "type": "textarea",
                "required": True,
                "default": "Paste relevant evidence, policy, ticket, or approved example notes.",
            },
            {
                "key": "approval_owner",
                "label": "Approval owner",
                "type": "text",
                "required": True,
                "default": "Business owner",
            },
        ],
        "specific_rules": [
            "Use only the case, loaded business evidence, and local tool outputs.",
            "Do not make final legal, financial, safety, employment, medical, or regulated decisions.",
            "State uncertainty and human approval requirements clearly.",
        ],
        "missing_information_rules": [
            {
                "terms": ["customer", "external", "send", "顧客", "送信"],
                "message": "Customer-facing use requires human review and approved source evidence.",
            },
            {
                "terms": ["risk", "approval", "legal", "financial", "safety", "リスク", "承認"],
                "message": "Risk owner, approval boundary, and source evidence must be verified.",
            },
        ],
        "always_missing_information": [
            "Business owner approval, current policy evidence, and final human review result",
        ],
        "scoring_summary_ja": "業務要件、証拠、リスク、人間承認条件に基づきローカル候補をスコアリングしました。",
        "live_search_queries": [],
        "reviewer_guidance": [
            "Verify that all recommendations cite evidence.",
            "Check that the draft does not cross the human approval boundary.",
            "Confirm the workflow is useful for the submitted enterprise profile.",
        ],
        "area_profiles": [
            {
                "area_id": "workflow_standardization",
                "name_ja": "業務標準化候補",
                "summary_ja": "反復的な判断、文書作成、証拠確認を標準化する候補です。",
                "typical_budget_jpy_m": 50,
                "commute_minutes": 30,
                "station_access": 6,
                "school_score": 5,
                "family_score": 6,
                "quiet_score": 5,
                "risk_note_ja": "業務責任者による承認境界と例外処理の確認が必要です。",
            },
            {
                "area_id": "knowledge_navigation",
                "name_ja": "ナレッジ検索候補",
                "summary_ja": "社内文書、FAQ、過去事例から根拠を検索して回答案を作る候補です。",
                "typical_budget_jpy_m": 40,
                "commute_minutes": 25,
                "station_access": 7,
                "school_score": 6,
                "family_score": 7,
                "quiet_score": 6,
                "risk_note_ja": "古い文書や未承認文書の混入を避ける検証が必要です。",
            },
        ],
        "property_listings": [
            {
                "property_id": "approval_packet_workflow",
                "area_id": "workflow_standardization",
                "title_ja": "承認パケット生成ワークフロー",
                "price_jpy_m": 45,
                "station_walk_minutes": 8,
                "school_score": 6,
                "family_score": 7,
                "quiet_score": 6,
                "earthquake_score": 5,
                "risk_note_ja": "承認前の自動送信は禁止です。",
            },
            {
                "property_id": "evidence_answer_workflow",
                "area_id": "knowledge_navigation",
                "title_ja": "根拠付き回答ドラフトワークフロー",
                "price_jpy_m": 42,
                "station_walk_minutes": 6,
                "school_score": 7,
                "family_score": 7,
                "quiet_score": 6,
                "earthquake_score": 5,
                "risk_note_ja": "根拠の鮮度と業務適合性を人間が確認してください。",
            },
        ],
        "sample_customers": [
            {
                "case_id": "generic_case_001",
                "request": "社内ナレッジを根拠に顧客回答案を作り、承認者に確認してから送信したい。",
                "evidence_summary": "FAQ、過去対応履歴、業務ルールが利用可能。",
                "approval_owner": "Business owner",
            }
        ],
    }
