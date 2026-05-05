"""Feasibility and risk scoring for AI enablement opportunities."""

from __future__ import annotations


def _profile_blob(profile: dict, opportunity: dict) -> str:
    return " ".join(str(value) for value in list(profile.values()) + list(opportunity.values())).lower()


def _bounded(value: float) -> float:
    return round(max(1.0, min(10.0, value)), 1)


def score_opportunity(profile: dict, opportunity: dict) -> dict:
    """Score one opportunity on business, feasibility, risk, and Japan fit."""
    blob = _profile_blob(profile, opportunity)
    evidence_count = len(opportunity.get("evidence_support", []))
    business_value = float(opportunity.get("score", 6.0))
    evidence_strength = _bounded(5.0 + evidence_count * 1.2)
    data_readiness = 5.0
    if any(term in blob for term in ("manual", "faq", "policy", "ticket", "email", "document", "マニュアル", "規程")):
        data_readiness += 1.5
    if any(term in blob for term in ("database", "api", "structured", "csv", "excel")):
        data_readiness += 1.0
    technical_feasibility = 7.0
    if any(term in blob for term in ("forecast", "prediction", "multimodal", "real-time", "画像", "予測")):
        technical_feasibility -= 1.0
    risk_controllability = 6.0
    if "human" in blob or "approval" in blob or "承認" in blob:
        risk_controllability += 1.5
    if any(term in blob for term in ("financial", "medical", "legal", "loan", "金融", "医療", "法務")):
        risk_controllability -= 0.7
    japan_fit = 7.0
    if any(term in blob for term in ("japan", "japanese", "日本", "ringi", "稟議", "kaizen")):
        japan_fit += 1.2
    poc_buildability = 7.0
    if any(term in blob for term in ("available", "faq", "manual", "tickets", "approved", "既存")):
        poc_buildability += 0.8
    overall = (
        business_value * 0.22
        + evidence_strength * 0.16
        + data_readiness * 0.16
        + technical_feasibility * 0.16
        + risk_controllability * 0.14
        + japan_fit * 0.10
        + poc_buildability * 0.06
    )
    return {
        "name": opportunity.get("name"),
        "business_value": _bounded(business_value),
        "evidence_strength": _bounded(evidence_strength),
        "data_readiness": _bounded(data_readiness),
        "technical_feasibility": _bounded(technical_feasibility),
        "risk_controllability": _bounded(risk_controllability),
        "japan_enterprise_fit": _bounded(japan_fit),
        "poc_buildability": _bounded(poc_buildability),
        "overall_score": _bounded(overall),
        "recommendation": "advance" if overall >= 7.0 else "consider" if overall >= 6.0 else "hold",
        "key_risks": [
            opportunity.get("key_risk", "Risk requires validation."),
            "Human approval and audit logging should be included before any production use.",
        ],
        "required_next_validation": [
            "Confirm representative data availability.",
            "Create 10-20 sample cases for simulation.",
            "Review human approval boundary with business owner.",
        ],
    }


def score_opportunities(profile: dict, opportunities: list[dict]) -> list[dict]:
    return [score_opportunity(profile, opportunity) for opportunity in opportunities]
