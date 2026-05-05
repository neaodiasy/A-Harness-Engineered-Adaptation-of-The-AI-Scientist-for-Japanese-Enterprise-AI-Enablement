"""Agent workflow design from selected opportunity and primitive composition."""

from __future__ import annotations


def design_agent_workflow(profile: dict, selected_opportunity: dict, architecture: dict, evidence_pack: dict) -> dict:
    """Create a structured agent workflow design for the selected PoC."""
    primitives = architecture.get("selected_primitives", [])
    evidence_ids = selected_opportunity.get("evidence_support", [])
    evidence_lookup = {item["id"]: item for item in evidence_pack.get("evidence_items", [])}
    knowledge_sources = [
        {
            "id": evidence_id,
            "title": evidence_lookup.get(evidence_id, {}).get("title", evidence_id),
            "url": evidence_lookup.get(evidence_id, {}).get("url", ""),
        }
        for evidence_id in evidence_ids
    ]
    if "available_data" in profile and profile["available_data"]:
        knowledge_sources.append({
            "id": "enterprise_available_data",
            "title": "User-provided enterprise data assets",
            "description": profile["available_data"],
        })

    steps = []
    if "intake" in primitives:
        steps.append("Normalize the business request, user role, target workflow, available data, and constraints.")
    if "classification" in primitives:
        steps.append("Classify the workflow case type, urgency, sensitivity, and routing destination.")
    if "retrieval" in primitives:
        steps.append("Retrieve supporting evidence from approved documents, manuals, policies, or evidence pack sources.")
    if "extraction" in primitives:
        steps.append("Extract structured fields from documents, forms, emails, or screenshots and mark missing fields.")
    if "checklist" in primitives:
        steps.append("Run completeness and process checks against required fields, approval rules, and next actions.")
    if "drafting" in primitives:
        steps.append("Draft the recommended response, report, checklist, or internal note using only available evidence.")
    if "risk_check" in primitives:
        steps.append("Detect regulated, customer-facing, legal, financial, HR, safety, or irreversible decisions.")
    if "human_approval" in primitives:
        steps.append("Assemble an approval packet and block external or irreversible action until a human approves.")
    if "audit_log" in primitives:
        steps.append("Record evidence IDs, model output, risk reasons, human edits, and final decision.")
    if "evaluation" in primitives:
        steps.append("Evaluate the workflow on synthetic business cases and trigger repair if checks fail.")

    design = {
        "name": architecture.get("name", selected_opportunity.get("name", "Enterprise Agent Workflow")),
        "enterprise_context": {
            "industry": profile.get("industry", ""),
            "main_business": profile.get("main_business", ""),
            "ai_objective": profile.get("ai_objective", ""),
            "available_data": profile.get("available_data", ""),
            "constraints": profile.get("constraints", ""),
        },
        "selected_opportunity": selected_opportunity,
        "input": [
            "Enterprise user request or business case",
            "Target workflow description",
            "Available documents, tickets, policies, reports, or sample records",
            "Human approval and compliance constraints",
        ],
        "output": [
            "Recommended action or draft artifact",
            "Evidence packet with source IDs",
            "Risk level and risk reasons",
            "Human approval requirement",
            "Audit trace for review",
        ],
        "selected_primitives": primitives,
        "agent_steps": steps,
        "knowledge_sources": knowledge_sources,
        "tools": [
            "LLM with cheap/strong routing",
            "Evidence pack retriever",
            "Primitive composition registry",
            "Schema validator",
            "Sandbox evaluator",
            "Human approval gate",
        ],
        "validation_checks": [
            "Every recommendation cites evidence or declares evidence missing.",
            "Customer-facing, regulated, HR, legal, financial, safety, or irreversible outputs require human approval.",
            "Risk reasons are explicit and visible to the reviewer.",
            "The workflow can run on local sample data before production integration.",
            "Generated outputs preserve an audit trace.",
        ],
        "human_approval_points": [
            "Before sending external communication",
            "Before making regulated or irreversible decisions",
            "When confidence is low or evidence is missing",
            "When the case affects customers, employees, finance, legal, safety, or compliance",
        ],
        "risk_mitigation": [
            "Use evidence-gated generation.",
            "Prefer bounded PoC scope over broad automation.",
            "Keep human approval mandatory in pilot phase.",
            "Log all model outputs and human edits.",
            "Use synthetic and sanitized samples before real data integration.",
        ],
        "evaluation_criteria": [
            "Evidence relevance",
            "Task classification or routing correctness",
            "Completeness of required fields or checklist items",
            "Risk flag correctness",
            "Human approval enforcement",
            "Clarity and usefulness of generated output",
            "Traceability and auditability",
        ],
    }
    return design


def render_agent_design_markdown(design: dict) -> str:
    """Render structured agent design into Markdown."""
    lines = [
        f"# {design['name']}",
        "",
        "## Selected Opportunity",
        "",
        f"**{design['selected_opportunity'].get('name', '')}**",
        "",
        design["selected_opportunity"].get("target_workflow", ""),
        "",
        "## Inputs",
        "",
        *[f"- {item}" for item in design["input"]],
        "",
        "## Outputs",
        "",
        *[f"- {item}" for item in design["output"]],
        "",
        "## Selected Primitives",
        "",
        " -> ".join(design["selected_primitives"]),
        "",
        "## Agent Steps",
        "",
        *[f"{index + 1}. {step}" for index, step in enumerate(design["agent_steps"])],
        "",
        "## Knowledge Sources",
        "",
        *[f"- {item.get('id')}: {item.get('title')}" for item in design["knowledge_sources"]],
        "",
        "## Validation Checks",
        "",
        *[f"- {item}" for item in design["validation_checks"]],
        "",
        "## Human Approval Points",
        "",
        *[f"- {item}" for item in design["human_approval_points"]],
        "",
        "## Risk Mitigation",
        "",
        *[f"- {item}" for item in design["risk_mitigation"]],
        "",
        "## Evaluation Criteria",
        "",
        *[f"- {item}" for item in design["evaluation_criteria"]],
        "",
    ]
    return "\n".join(lines)
