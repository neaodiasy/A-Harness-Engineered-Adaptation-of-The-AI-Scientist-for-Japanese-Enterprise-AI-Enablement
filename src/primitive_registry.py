"""Reusable agent design primitives.

The project uses bounded compositionality: primitives are stable, auditable
building blocks, while each enterprise gets a custom composition.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class Primitive:
    id: str
    name: str
    purpose: str
    triggers: tuple[str, ...]
    risks: tuple[str, ...]
    outputs: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


PRIMITIVES: tuple[Primitive, ...] = (
    Primitive(
        id="intake",
        name="Enterprise Intake",
        purpose="Collect user request, business context, available data, and constraints.",
        triggers=("workflow", "business", "pain", "context", "企業", "業務", "課題"),
        risks=("Ambiguous scope", "Missing stakeholder constraints"),
        outputs=("normalized_request", "enterprise_profile"),
    ),
    Primitive(
        id="retrieval",
        name="Evidence Retrieval",
        purpose="Retrieve grounded evidence from internal documents, manuals, tickets, or external sources.",
        triggers=("manual", "knowledge", "faq", "policy", "document", "規程", "マニュアル", "ナレッジ"),
        risks=("Outdated evidence", "Conflicting documents", "Weak source attribution"),
        outputs=("evidence_items", "citations"),
    ),
    Primitive(
        id="classification",
        name="Workflow Classification",
        purpose="Classify request type, workflow category, urgency, or routing destination.",
        triggers=("classify", "triage", "route", "問い合わせ", "分類", "振り分け"),
        risks=("Misrouting", "Overconfident low-quality labels"),
        outputs=("class_label", "confidence", "routing_hint"),
    ),
    Primitive(
        id="extraction",
        name="Structured Extraction",
        purpose="Extract fields from documents, emails, forms, tables, or screenshots.",
        triggers=("invoice", "contract", "pdf", "form", "請求書", "契約", "申請", "帳票"),
        risks=("OCR errors", "Missing field validation"),
        outputs=("structured_fields", "missing_fields"),
    ),
    Primitive(
        id="checklist",
        name="Checklist Validation",
        purpose="Check completeness, process compliance, or required next steps.",
        triggers=("check", "missing", "approval", "不備", "不足", "確認", "承認"),
        risks=("False pass on incomplete case", "Rigid checklist misses exceptions"),
        outputs=("check_results", "missing_items", "next_actions"),
    ),
    Primitive(
        id="drafting",
        name="Draft Generation",
        purpose="Draft emails, reports, proposals, meeting notes, or customer/staff responses.",
        triggers=("email", "reply", "proposal", "report", "draft", "返信", "提案", "報告書"),
        risks=("Hallucinated claims", "Tone mismatch", "Unapproved external communication"),
        outputs=("draft_text", "assumptions"),
    ),
    Primitive(
        id="risk_check",
        name="Risk and Compliance Check",
        purpose="Detect sensitive decisions, regulated advice, compliance issues, and escalation needs.",
        triggers=("risk", "compliance", "legal", "finance", "medical", "金融", "法務", "医療", "監査"),
        risks=("False negatives", "Insufficient escalation"),
        outputs=("risk_level", "risk_reasons", "escalation_required"),
    ),
    Primitive(
        id="human_approval",
        name="Human Approval Gate",
        purpose="Prevent automatic external or irreversible actions; require explicit human decision.",
        triggers=("approval", "external", "customer", "decision", "承認", "稟議", "顧客"),
        risks=("Rubber-stamping", "Approval trail gaps"),
        outputs=("approval_required", "approval_packet"),
    ),
    Primitive(
        id="audit_log",
        name="Audit Trace",
        purpose="Record evidence, model output, human edits, decisions, and reviewer results.",
        triggers=("audit", "trace", "governance", "監査", "証跡", "ガバナンス"),
        risks=("Incomplete trace", "Sensitive data retention"),
        outputs=("trace_record", "review_log"),
    ),
    Primitive(
        id="evaluation",
        name="Evaluation Harness",
        purpose="Generate sample cases, run simulations, score outputs, and trigger repair.",
        triggers=("test", "evaluate", "simulation", "検証", "評価", "テスト"),
        risks=("Narrow test coverage", "Overfitting to examples"),
        outputs=("test_cases", "evaluation_results", "repair_notes"),
    ),
)


def list_primitives() -> list[dict]:
    return [primitive.to_dict() for primitive in PRIMITIVES]


def get_primitive(primitive_id: str) -> Primitive:
    for primitive in PRIMITIVES:
        if primitive.id == primitive_id:
            return primitive
    raise KeyError(f"Unknown primitive: {primitive_id}")
