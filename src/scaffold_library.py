"""Reusable enterprise AI product scaffold patterns."""

from __future__ import annotations

from typing import Any


SCAFFOLD_LIBRARY: dict[str, dict[str, Any]] = {
    "recommendation_workbench": {
        "scaffold_id": "recommendation_workbench",
        "purpose": "Compare candidates, explain trade-offs, cite evidence, and prepare approval-ready recommendations.",
        "default_ui_sections": ["intake_panel", "candidate_comparison", "evidence_panel", "risk_panel", "approval_packet"],
        "default_backend_modules": ["recommendation_engine", "evidence_helper", "runtime_drafting_agent", "guardrails"],
        "default_local_tools": ["candidate_ranker", "evidence_lookup"],
        "required_guardrails": ["candidate names must come from local data", "human approval required", "send_allowed false"],
        "default_evaluation_checks": ["candidate output exists", "evidence exists", "risk flags exist", "approval required"],
        "compatible_opportunity_keywords": ["recommend", "recommendation", "ranking", "rank", "match", "matching", "compare", "preference", "suitable", "property", "real estate", "area", "候補", "推薦", "比較"],
    },
    "customer_support_workbench": {
        "scaffold_id": "customer_support_workbench",
        "purpose": "Analyze support inquiries, retrieve FAQ or policy evidence, draft cautious replies, and escalate risky cases.",
        "default_ui_sections": ["ticket_intake", "faq_policy_evidence", "response_draft", "escalation_risk", "approval_panel"],
        "default_backend_modules": ["ticket_analyzer", "faq_matcher", "response_drafter", "escalation_checker", "guardrails"],
        "default_local_tools": ["faq_matcher", "policy_lookup"],
        "required_guardrails": ["do not automatically send replies", "escalate ambiguous cases", "human approval required"],
        "default_evaluation_checks": ["response draft exists", "evidence exists", "escalation flags exist", "approval required"],
        "compatible_opportunity_keywords": ["support", "ticket", "faq", "inquiry", "email", "reply", "問い合わせ", "返信"],
    },
    "risk_review_console": {
        "scaffold_id": "risk_review_console",
        "purpose": "Review cases against policies, detect missing information and risk, and prepare reviewer decisions.",
        "default_ui_sections": ["case_intake", "policy_review", "risk_checklist", "evidence_panel", "reviewer_approval"],
        "default_backend_modules": ["risk_analyzer", "policy_checker", "missing_information_detector", "guardrails"],
        "default_local_tools": ["risk_classifier", "policy_condition_checker"],
        "required_guardrails": ["risk flags required", "missing information checked", "human approval required"],
        "default_evaluation_checks": ["risk flags exist", "missing info checked", "approval required"],
        "compatible_opportunity_keywords": ["risk", "compliance", "claim", "legal", "financial", "hr", "監査", "承認", "リスク"],
    },
    "knowledge_assistant": {
        "scaffold_id": "knowledge_assistant",
        "purpose": "Retrieve knowledge, summarize evidence, draft grounded answers, and flag uncertainty.",
        "default_ui_sections": ["query_intake", "document_evidence", "answer_draft", "uncertainty_flags", "approval"],
        "default_backend_modules": ["knowledge_lookup", "evidence_summarizer", "answer_drafter", "guardrails"],
        "default_local_tools": ["doc_lookup", "evidence_matcher"],
        "required_guardrails": ["cite evidence", "flag uncertainty", "approval when needed"],
        "default_evaluation_checks": ["evidence-grounded answer", "uncertainty flags", "approval when needed"],
        "compatible_opportunity_keywords": ["knowledge", "document", "manual", "faq", "policy", "ナレッジ", "マニュアル"],
    },
    "approval_workbench": {
        "scaffold_id": "approval_workbench",
        "purpose": "Prepare draft outputs, evidence packets, risk notes, and approval controls for human reviewers.",
        "default_ui_sections": ["draft_review", "evidence_review", "risk_notes", "approval_controls"],
        "default_backend_modules": ["draft_generator", "approval_packet_builder", "guardrails"],
        "default_local_tools": ["approval_checker"],
        "required_guardrails": ["send_allowed false", "approval_required true", "reviewer decision recorded"],
        "default_evaluation_checks": ["send_allowed false", "approval_required true"],
        "compatible_opportunity_keywords": ["approval", "review", "draft", "稟議", "承認", "レビュー"],
    },
    "domain_operations_workbench": {
        "scaffold_id": "domain_operations_workbench",
        "purpose": "Generic fallback scaffold for domain-specific workflow analysis, evidence, drafting, and approval.",
        "default_ui_sections": ["case_intake", "analysis", "evidence", "draft", "approval"],
        "default_backend_modules": ["domain_tools", "runtime_drafting_agent", "guardrails", "evaluation"],
        "default_local_tools": ["domain_candidate_ranker", "evidence_lookup"],
        "required_guardrails": ["human approval required", "send_allowed false", "audit trace required"],
        "default_evaluation_checks": ["structured output exists", "evidence exists", "approval required"],
        "compatible_opportunity_keywords": [],
    },
}


def load_scaffold_library() -> dict[str, dict[str, Any]]:
    """Return reusable scaffold patterns."""
    return {key: dict(value) for key, value in SCAFFOLD_LIBRARY.items()}


def get_scaffold(scaffold_id: str) -> dict[str, Any]:
    """Return one scaffold pattern, falling back to the generic scaffold."""
    return dict(SCAFFOLD_LIBRARY.get(scaffold_id) or SCAFFOLD_LIBRARY["domain_operations_workbench"])


def select_scaffold_deterministically(*contexts: object) -> str:
    """Select a scaffold from keyword overlap for no-LLM fallback."""
    text = " ".join(str(item) for item in contexts).lower()
    best_id = "domain_operations_workbench"
    best_score = 0
    priority = {
        "customer_support_workbench": 5,
        "risk_review_console": 4,
        "knowledge_assistant": 3,
        "approval_workbench": 2,
        "recommendation_workbench": 1,
    }
    for scaffold_id, scaffold in SCAFFOLD_LIBRARY.items():
        if scaffold_id == "domain_operations_workbench":
            continue
        terms = [str(term).lower() for term in scaffold.get("compatible_opportunity_keywords", [])]
        score = sum(1 for term in terms if term and term in text)
        if scaffold_id == "customer_support_workbench" and any(term in text for term in ("support", "inquiry", "faq", "reply", "customer")):
            score += 2
        if scaffold_id == "recommendation_workbench" and any(term in text for term in ("recommendation", "preference", "ranking", "matching", "property", "real estate", "suitable")):
            score += 3
        if scaffold_id == "risk_review_console" and any(term in text for term in ("claim", "compliance", "policy review", "risk review", "legal", "financial", "hr")):
            score += 1
        if score > best_score or (score == best_score and score > 0 and priority.get(scaffold_id, 0) > priority.get(best_id, 0)):
            best_id = scaffold_id
            best_score = score
    return best_id
