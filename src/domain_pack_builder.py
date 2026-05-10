"""Semi-automatic Domain Pack Auto-Builder.

This module turns an enterprise profile plus optional source notes into a draft
domain_pack.json. It is deliberately semi-automatic: generated packs are
validated and written as drafts unless the caller explicitly installs them into
templates/<domain_id>/domain_pack.json.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from src.domain_templates import REPO_ROOT
from src.harness.json_utils import dump_json, load_json


STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "into",
    "their",
    "company",
    "system",
    "business",
    "customer",
    "customers",
    "staff",
    "japan",
    "japanese",
}

RISK_TERMS = {
    "legal": "Legal or contractual interpretation requires human review.",
    "financial": "Financial, investment, pricing, or payment advice requires human approval.",
    "medical": "Medical or health-related judgment must not be automated.",
    "safety": "Safety-critical or irreversible operational actions require an accountable human owner.",
    "employment": "Hiring, firing, promotion, or worker evaluation decisions require human review.",
    "personal": "Personal data use requires privacy and data-minimization review.",
    "regulated": "Regulated-domain outputs require policy evidence and reviewer sign-off.",
}


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "generated_domain"


def _flatten(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(_flatten(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(_flatten(item) for item in value)
    return str(value)


def _keywords(text: str, limit: int = 16) -> list[str]:
    tokens = [
        token.lower()
        for token in re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}|[\u3040-\u30ff\u3400-\u9fff]{2,}", text)
        if token.lower() not in STOPWORDS
    ]
    ranked = [token for token, _ in Counter(tokens).most_common(limit)]
    return ranked


def _as_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if value:
        return [str(value)]
    return []


def infer_input_fields(profile: dict[str, Any], source_text: str) -> list[dict[str, Any]]:
    """Infer a conservative product intake schema from profile and sources."""
    fields: list[dict[str, Any]] = [
        {
            "key": "request",
            "label": "Business request",
            "type": "textarea",
            "required": True,
            "default": "Describe the case, user need, or workflow request.",
        },
        {
            "key": "evidence_summary",
            "label": "Evidence summary",
            "type": "textarea",
            "required": True,
            "default": "Paste trusted internal notes, public guidance, or approved examples.",
        },
    ]
    text = source_text.lower()
    if any(term in text for term in ("budget", "cost", "price", "予算", "費用")):
        fields.append({"key": "budget", "label": "Budget or cost constraint", "type": "text", "required": False, "default": ""})
    if any(term in text for term in ("deadline", "timeline", "sla", "納期", "期限")):
        fields.append({"key": "deadline", "label": "Deadline / SLA", "type": "text", "required": False, "default": ""})
    if any(term in text for term in ("location", "area", "region", "拠点", "地域", "場所")):
        fields.append({"key": "location", "label": "Location / operating area", "type": "text", "required": False, "default": ""})
    if profile.get("target_users"):
        fields.append({"key": "target_user", "label": "Target user", "type": "text", "required": False, "default": str(profile.get("target_users", [""])[0])})
    fields.append({"key": "approval_owner", "label": "Approval owner", "type": "text", "required": True, "default": "Business owner"})
    return fields


def infer_missing_information_rules(text: str) -> list[dict[str, Any]]:
    """Infer evidence gaps that the generated app should surface."""
    rules = [
        {
            "terms": ["customer", "external", "send", "顧客", "送信"],
            "message": "Customer-facing use requires approved source evidence and human review.",
        },
        {
            "terms": ["risk", "approval", "legal", "financial", "safety", "リスク", "承認"],
            "message": "Approval boundary, risk owner, and current policy evidence must be verified.",
        },
    ]
    lowered = text.lower()
    for term, message in RISK_TERMS.items():
        if term in lowered:
            rules.append({"terms": [term], "message": message})
    return rules


def build_candidate_records(profile: dict[str, Any], keywords: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Create generic local-tool candidates and execution options."""
    workflows = _as_list(profile.get("pain_points"))[:3] or _as_list(profile.get("available_data"))[:3]
    if not workflows:
        workflows = ["knowledge retrieval", "approval packet drafting", "exception triage"]

    candidates: list[dict[str, Any]] = []
    items: list[dict[str, Any]] = []
    for index, workflow in enumerate(workflows, start=1):
        candidate_id = f"candidate_{index}"
        candidates.append(
            {
                "area_id": candidate_id,
                "name_ja": f"業務候補 {index}",
                "summary_ja": str(workflow),
                "typical_budget_jpy_m": max(30, 60 - index * 5),
                "time_or_effort_index": 20 + index * 5,
                "access_score": 5 + index,
                "relevance_score": 5 + index,
                "user_fit_score": 6,
                "stability_score": 6,
                "risk_readiness_score": 5,
                "risk_note_ja": "根拠資料、承認境界、例外処理を人間が確認してください。",
                "source_terms": keywords[:6],
            }
        )
        items.append(
            {
                "property_id": f"workflow_option_{index}",
                "area_id": candidate_id,
                "title_ja": f"実装オプション {index}",
                "price_jpy_m": max(30, 55 - index * 4),
                "access_minutes": 5 + index,
                "relevance_score": 5 + index,
                "user_fit_score": 6,
                "stability_score": 6,
                "risk_readiness_score": 5,
                "risk_note_ja": "自動実行ではなく、承認パケットとして提示してください。",
            }
        )
    return candidates, items


def build_domain_pack(profile: dict[str, Any], source_documents: list[str]) -> dict[str, Any]:
    """Build a candidate domain_pack.json from enterprise and source context."""
    source_text = "\n".join([_flatten(profile), *source_documents])
    industry = str(profile.get("industry") or profile.get("main_business") or "enterprise")
    domain_id = _slugify(industry)[:64]
    terms = _keywords(source_text, limit=18)
    candidates, items = build_candidate_records(profile, terms)
    product_name = f"{profile.get('company_name', 'Enterprise')} AI Workbench"
    objective = str(profile.get("business_goal") or profile.get("ai_objective") or "Generate approval-ready enterprise AI workflow outputs.")

    return {
        "template_id": domain_id,
        "description": "Candidate domain pack generated by Domain Pack Auto-Builder. Human review required before production use.",
        "autobuilder": {
            "status": "draft",
            "human_review_required": True,
            "source_count": len(source_documents),
            "generation_method": "keyword_and_profile_extraction",
        },
        "match_terms": terms,
        "product_name": product_name,
        "subtitle": objective,
        "primary_action": "Generate Approval Packet",
        "tool_name": f"{domain_id}_toolkit",
        "candidate_collection_label": "workflow candidates",
        "item_collection_label": "implementation options",
        "default_classification_label": f"{domain_id}_workflow_case",
        "prompt_context": f"AI-driven Japanese enterprise enablement product for {industry}",
        "candidate_examples": [item["name_ja"] for item in candidates],
        "fields": infer_input_fields(profile, source_text),
        "specific_rules": [
            "Use concrete local tool candidate names from the loaded domain data when relevant.",
            "Use source evidence as supporting context, not as final authority.",
            "Do not make final legal, financial, safety, employment, medical, or regulated decisions.",
            "Escalate ambiguous, irreversible, customer-facing, or regulated outputs to a human owner.",
        ],
        "missing_information_rules": infer_missing_information_rules(source_text),
        "always_missing_information": [
            "Current internal policy evidence",
            "Business owner approval",
            "Final human review result",
        ],
        "scoring_summary_ja": "業務候補、証拠、リスク、人間承認条件をローカルデータでスコアリングしました。",
        "live_search_queries": [
            f"{industry} AI governance Japan enterprise",
            f"{industry} DX AI use case Japan",
        ],
        "reviewer_guidance": [
            "Check that the domain pack was reviewed by a human owner before installation.",
            "Verify that risk boundaries and approval rules match the actual enterprise context.",
            "Confirm that sample cases do not include confidential or personal data.",
            "Run schema validation and generated-app smoke tests before accepting the pack.",
        ],
        "domain_candidates": candidates,
        "item_records": items,
        "area_profiles": candidates,
        "property_listings": items,
        "sample_customers": [
            {
                "case_id": f"{domain_id}_case_001",
                "request": str(profile.get("business_goal") or profile.get("preferred_enablement_direction") or "Prepare an approval-ready workflow recommendation."),
                "evidence_summary": "; ".join(_as_list(profile.get("available_data"))[:4]) or "Public and internal evidence to be reviewed.",
                "approval_owner": "Business owner",
            }
        ],
    }


def validate_domain_pack(pack: dict[str, Any]) -> dict[str, Any]:
    """Validate schema shape and safety constraints for a candidate domain pack."""
    required = [
        "template_id",
        "match_terms",
        "product_name",
        "fields",
        "specific_rules",
        "missing_information_rules",
        "reviewer_guidance",
        "area_profiles",
        "property_listings",
        "sample_customers",
    ]
    errors: list[str] = []
    warnings: list[str] = []
    for key in required:
        if key not in pack or pack[key] in ("", [], None):
            errors.append(f"Missing required key: {key}")
    if not pack.get("autobuilder", {}).get("human_review_required", False):
        errors.append("Auto-built packs must require human review.")
    if "send_allowed" in json.dumps(pack, ensure_ascii=False).lower():
        warnings.append("Pack text mentions send_allowed; generated app should still force send_allowed=false.")
    for field in pack.get("fields", []):
        if not isinstance(field, dict) or not field.get("key") or not field.get("label"):
            errors.append("Every field must include key and label.")
    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "human_review_required": True,
    }


def read_source_documents(paths: list[str]) -> list[str]:
    docs: list[str] = []
    for raw_path in paths:
        path = Path(raw_path).expanduser()
        docs.append(path.read_text(encoding="utf-8"))
    return docs


def write_domain_pack_draft(
    profile_path: Path,
    source_paths: list[str],
    output_path: Path,
    install_template: bool = False,
) -> dict[str, Any]:
    profile = load_json(profile_path)
    source_docs = read_source_documents(source_paths)
    pack = build_domain_pack(profile, source_docs)
    validation = validate_domain_pack(pack)
    target = output_path
    if install_template:
        target = REPO_ROOT / "templates" / str(pack["template_id"]) / "domain_pack.json"
    dump_json(target, pack)
    dump_json(target.with_name("validation_report.json"), validation)
    return {"domain_pack": str(target), "validation_report": str(target.with_name("validation_report.json")), "validation": validation}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a draft domain_pack.json from an enterprise profile and optional source documents.")
    parser.add_argument("--profile", required=True, help="Path to enterprise profile JSON.")
    parser.add_argument("--source", action="append", default=[], help="Optional source text/markdown file. Can be passed multiple times.")
    parser.add_argument("--output", default="outputs/domain_pack_drafts/domain_pack.json", help="Draft output path.")
    parser.add_argument("--install-template", action="store_true", help="Install under templates/<template_id>/domain_pack.json after validation draft generation.")
    args = parser.parse_args()
    result = write_domain_pack_draft(
        profile_path=Path(args.profile),
        source_paths=args.source,
        output_path=Path(args.output),
        install_template=args.install_template,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
