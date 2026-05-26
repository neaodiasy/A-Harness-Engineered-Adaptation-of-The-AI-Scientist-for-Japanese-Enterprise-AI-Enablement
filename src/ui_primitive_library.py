"""Reusable UI primitives for generated enterprise AI products.

The builder keeps these primitives deterministic and responsive, while the
build-time app designer decides which primitives should be composed for a
specific enterprise workflow.
"""

from __future__ import annotations

from typing import Any


UI_PRIMITIVE_LIBRARY: dict[str, dict[str, Any]] = {
    "case_intake": {
        "primitive_id": "case_intake",
        "purpose": "Collect structured business context and case inputs.",
        "default_span": "narrow",
    },
    "ai_copilot": {
        "primitive_id": "ai_copilot",
        "purpose": "Interactive DeepSeek-backed business copilot.",
        "default_span": "wide",
    },
    "chat_thread": {
        "primitive_id": "chat_thread",
        "purpose": "Conversation-first interface for knowledge or support workflows.",
        "default_span": "wide",
    },
    "candidate_table": {
        "primitive_id": "candidate_table",
        "purpose": "Rank, compare, and explain candidate options.",
        "default_span": "wide",
    },
    "comparison_matrix": {
        "primitive_id": "comparison_matrix",
        "purpose": "Compare alternatives across criteria and trade-offs.",
        "default_span": "wide",
    },
    "evidence_panel": {
        "primitive_id": "evidence_panel",
        "purpose": "Display local and live evidence sources.",
        "default_span": "medium",
    },
    "draft_editor": {
        "primitive_id": "draft_editor",
        "purpose": "Edit AI-generated drafts before approval.",
        "default_span": "wide",
    },
    "approval_panel": {
        "primitive_id": "approval_panel",
        "purpose": "Show approval status, owner, and decision options.",
        "default_span": "medium",
    },
    "risk_checklist": {
        "primitive_id": "risk_checklist",
        "purpose": "Surface risk flags, missing information, and escalation rules.",
        "default_span": "medium",
    },
    "metrics_strip": {
        "primitive_id": "metrics_strip",
        "purpose": "Summarize classification, confidence, risk, evidence, and send status.",
        "default_span": "wide",
    },
    "timeline": {
        "primitive_id": "timeline",
        "purpose": "Show activity, audit, or process milestones.",
        "default_span": "medium",
    },
    "document_viewer": {
        "primitive_id": "document_viewer",
        "purpose": "Inspect policy, FAQ, manual, or knowledge excerpts.",
        "default_span": "wide",
    },
    "checklist": {
        "primitive_id": "checklist",
        "purpose": "Track workflow-specific validation tasks.",
        "default_span": "medium",
    },
    "kanban_queue": {
        "primitive_id": "kanban_queue",
        "purpose": "Group cases by state, owner, or escalation lane.",
        "default_span": "wide",
    },
    "map_context": {
        "primitive_id": "map_context",
        "purpose": "Represent area, location, route, or field context without external maps.",
        "default_span": "medium",
    },
}


INTERFACE_DEFAULT_PRIMITIVES: dict[str, list[str]] = {
    "support_desk": ["case_intake", "ai_copilot", "draft_editor", "evidence_panel", "risk_checklist", "approval_panel", "timeline"],
    "recommendation_dashboard": ["case_intake", "candidate_table", "comparison_matrix", "ai_copilot", "evidence_panel", "draft_editor", "approval_panel"],
    "risk_review_console": ["case_intake", "risk_checklist", "evidence_panel", "ai_copilot", "approval_panel", "timeline"],
    "chat_console": ["chat_thread", "ai_copilot", "document_viewer", "evidence_panel", "approval_panel"],
    "approval_queue": ["kanban_queue", "draft_editor", "evidence_panel", "risk_checklist", "approval_panel", "timeline"],
    "operations_console": ["case_intake", "ai_copilot", "evidence_panel", "draft_editor", "approval_panel", "timeline"],
    "custom_workbench": ["case_intake", "ai_copilot", "metrics_strip", "evidence_panel", "checklist", "draft_editor", "approval_panel"],
}


def load_ui_primitive_library() -> dict[str, dict[str, Any]]:
    """Return the primitive library as plain dictionaries."""
    return {key: dict(value) for key, value in UI_PRIMITIVE_LIBRARY.items()}


def default_primitives_for_interface(interface_type: str) -> list[str]:
    """Return primitive IDs for an interface type, falling back to custom."""
    return list(INTERFACE_DEFAULT_PRIMITIVES.get(interface_type) or INTERFACE_DEFAULT_PRIMITIVES["custom_workbench"])


def build_ui_primitive_plan(interface_type: str, feature_plan: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build a safe primitive plan from interface type and feature cards."""
    primitive_ids = default_primitives_for_interface(interface_type)
    plan: list[dict[str, Any]] = []
    for index, primitive_id in enumerate(primitive_ids, start=1):
        primitive = UI_PRIMITIVE_LIBRARY.get(primitive_id, UI_PRIMITIVE_LIBRARY["ai_copilot"])
        feature = feature_plan[(index - 1) % len(feature_plan)] if feature_plan else {}
        plan.append({
            "id": primitive_id,
            "type": primitive_id,
            "label": feature.get("label") or primitive_id.replace("_", " ").title(),
            "purpose": feature.get("purpose") or primitive["purpose"],
            "span": primitive.get("default_span", "medium"),
            "priority": index,
            "bound_action": feature.get("user_interaction", ""),
            "source": "ui_primitive_library",
        })
    return plan
