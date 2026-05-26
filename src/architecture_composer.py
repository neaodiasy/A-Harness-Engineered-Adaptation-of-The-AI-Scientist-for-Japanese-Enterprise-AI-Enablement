"""Compose custom agent architectures from reusable primitives."""

from __future__ import annotations

from src.domain_templates import select_domain_template
from src.primitive_registry import PRIMITIVES, get_primitive


BASE_PRIMITIVES = ("intake", "classification", "risk_check", "human_approval", "audit_log", "evaluation")


def _profile_blob(profile: dict, opportunity: dict | None = None) -> str:
    values = list(profile.values())
    if opportunity:
        values.extend(opportunity.values())
    return " ".join(str(value) for value in values).lower()


def _primitive_score(primitive_id: str, blob: str) -> float:
    primitive = get_primitive(primitive_id)
    hits = sum(1 for trigger in primitive.triggers if trigger.lower() in blob)
    score = hits * 1.0
    if primitive_id in BASE_PRIMITIVES:
        score += 2.0
    return score


def compose_architecture(profile: dict, recommended_opportunity: dict) -> dict:
    """Return a bespoke primitive composition for the selected opportunity."""
    blob = _profile_blob(profile, recommended_opportunity)
    scored = [
        (primitive.id, _primitive_score(primitive.id, blob))
        for primitive in PRIMITIVES
    ]
    selected = {primitive_id for primitive_id, score in scored if score > 0}
    selected.update(BASE_PRIMITIVES)
    if any(term in blob for term in ("manual", "knowledge", "faq", "policy", "規程", "マニュアル")):
        selected.add("retrieval")
    if any(term in blob for term in ("email", "reply", "customer", "proposal", "report", "顧客", "返信", "提案")):
        selected.add("drafting")
    if "recommend" in blob or "推薦" in blob or select_domain_template(profile, recommended_opportunity):
        selected.update({"retrieval", "checklist", "drafting"})
    if any(term in blob for term in ("invoice", "contract", "pdf", "form", "請求書", "契約", "申請")):
        selected.update({"extraction", "checklist"})
    if any(term in blob for term in ("triage", "route", "classify", "問い合わせ", "分類")):
        selected.add("classification")

    ordered = [primitive.id for primitive in PRIMITIVES if primitive.id in selected]
    rejected = [
        {
            "primitive": primitive.id,
            "reason": "Not enough signal in the enterprise profile or selected opportunity.",
        }
        for primitive in PRIMITIVES
        if primitive.id not in selected
    ]
    trace = [
        {
            "primitive": primitive_id,
            "score": score,
            "selected": primitive_id in selected,
        }
        for primitive_id, score in scored
    ]
    name = f"{recommended_opportunity.get('name', 'Enterprise AI')} Composition"
    return {
        "name": name,
        "selected_primitives": ordered,
        "primitive_details": [get_primitive(primitive_id).to_dict() for primitive_id in ordered],
        "why_this_composition": (
            "The architecture is composed from stable harness primitives rather than a fixed agent template. "
            "It reflects the enterprise profile, available data, risk constraints, and Japan-specific approval needs."
        ),
        "rejected_alternatives": rejected,
        "composition_trace": trace,
    }
