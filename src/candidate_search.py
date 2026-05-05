"""LATS-lite candidate search for enterprise AI enablement opportunities.

This is intentionally lightweight: each opportunity becomes a node, top nodes
are expanded through practical refinement actions, critiqued, rescored, and the
best PoC candidate is selected. The trace is designed to be auditable.
"""

from __future__ import annotations


EXPANSION_ACTIONS = (
    "narrow_poc_scope",
    "strengthen_human_approval",
    "improve_evidence_grounding",
    "reduce_integration_dependency",
)


def _feasibility_by_name(feasibility_results: list[dict]) -> dict:
    return {item["name"]: item for item in feasibility_results}


def _expand_node(opportunity: dict, feasibility: dict, action: str) -> dict:
    refined = dict(opportunity)
    refinement_notes = []
    score_delta = 0.0
    if action == "narrow_poc_scope":
        refinement_notes.append("Limit PoC to one high-frequency workflow and sanitized representative cases.")
        score_delta += 0.25
    elif action == "strengthen_human_approval":
        refinement_notes.append("Make approval packet mandatory for all external, regulated, or irreversible outputs.")
        score_delta += 0.35 if feasibility.get("risk_controllability", 0) < 8 else 0.15
    elif action == "improve_evidence_grounding":
        refinement_notes.append("Require every output to cite evidence IDs from the evidence pack or internal documents.")
        score_delta += 0.30 if feasibility.get("evidence_strength", 0) < 8 else 0.15
    elif action == "reduce_integration_dependency":
        refinement_notes.append("Use generated sample cases and file-based inputs for PoC before connecting to production systems.")
        score_delta += 0.30 if feasibility.get("technical_feasibility", 0) < 7 else 0.10
    refined["refinement_action"] = action
    refined["refinement_notes"] = refinement_notes
    return {
        "opportunity": refined,
        "score_delta": round(score_delta, 2),
        "action": action,
    }


def _critique_node(node: dict, feasibility: dict) -> dict:
    critiques = []
    if feasibility.get("data_readiness", 0) < 7:
        critiques.append("Data readiness is not yet proven; PoC should start with curated sample cases.")
    if feasibility.get("risk_controllability", 0) < 7:
        critiques.append("Risk controls require clearer human approval and audit boundaries.")
    if feasibility.get("evidence_strength", 0) < 7:
        critiques.append("Opportunity needs stronger external or internal evidence grounding.")
    if not critiques:
        critiques.append("Candidate is suitable for bounded PoC exploration.")
    return {
        "critiques": critiques,
        "poc_suitability": "high" if len(critiques) == 1 else "medium",
    }


def run_candidate_search(
    opportunities: list[dict],
    feasibility_results: list[dict],
    beam_width: int = 3,
) -> dict:
    """Run expand/critique/refine search and select a PoC candidate."""
    feasibility_lookup = _feasibility_by_name(feasibility_results)
    root_nodes = []
    for opportunity in opportunities:
        feasibility = feasibility_lookup.get(opportunity.get("name"), {})
        root_nodes.append({
            "node_id": f"root_{len(root_nodes) + 1}",
            "name": opportunity.get("name"),
            "opportunity": opportunity,
            "base_score": feasibility.get("overall_score", opportunity.get("score", 0)),
            "feasibility": feasibility,
            "depth": 0,
        })
    root_nodes.sort(key=lambda item: item["base_score"], reverse=True)
    frontier = root_nodes[:beam_width]

    expanded_nodes = []
    for root in frontier:
        for action in EXPANSION_ACTIONS:
            expanded = _expand_node(root["opportunity"], root["feasibility"], action)
            critique = _critique_node(expanded, root["feasibility"])
            total_score = round(root["base_score"] + expanded["score_delta"], 2)
            expanded_nodes.append({
                "node_id": f"{root['node_id']}::{action}",
                "parent": root["node_id"],
                "name": root["name"],
                "action": action,
                "depth": 1,
                "score": total_score,
                "opportunity": expanded["opportunity"],
                "critique": critique,
            })

    expanded_nodes.sort(key=lambda item: item["score"], reverse=True)
    selected_node = expanded_nodes[0] if expanded_nodes else root_nodes[0]
    selected_opportunity = selected_node["opportunity"]
    selected_opportunity["search_selection_reason"] = (
        "Selected after LATS-lite expansion because it has the strongest combination of feasibility, "
        "risk controllability, evidence grounding, and PoC buildability."
    )
    return {
        "method": "lats_lite_expand_critique_refine_v1",
        "beam_width": beam_width,
        "expansion_actions": list(EXPANSION_ACTIONS),
        "root_nodes": root_nodes,
        "expanded_nodes": expanded_nodes,
        "selected_node": selected_node,
        "selected_opportunity": selected_opportunity,
    }
