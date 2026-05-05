"""Generate visual artifacts for the enterprise scientist pipeline."""

from __future__ import annotations

from html import escape
from pathlib import Path


def _selected(result: dict) -> dict:
    return result.get("selected_opportunity") or result.get("recommended_agent") or {}


def _product_name(result: dict) -> str:
    manifest = result.get("prototype_manifest") or {}
    product_spec = manifest.get("product_spec") or {}
    selected = _selected(result)
    return product_spec.get("product_name") or selected.get("name") or "Generated Agent Product"


def _profile_label(result: dict) -> str:
    profile = result.get("company_profile") or {}
    return profile.get("company_name") or profile.get("industry") or profile.get("main_business") or "Current enterprise profile"


def _box(x: int, y: int, w: int, h: int, title: str, subtitle: str, fill: str) -> str:
    return f"""
  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="#264653" stroke-width="1.4"/>
  <text x="{x + 16}" y="{y + 28}" font-size="15" font-weight="700" fill="#172026">{escape(title)}</text>
  <text x="{x + 16}" y="{y + 52}" font-size="11" fill="#46515c">{escape(subtitle[:72])}</text>
"""


def _arrow(x1: int, y1: int, x2: int, y2: int) -> str:
    return f"""
  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#607080" stroke-width="1.6" marker-end="url(#arrow)"/>
"""


def write_architecture_diagram(result: dict, output_path: Path) -> Path:
    """Write an SVG diagram that visualizes the selected opportunity and primitives."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    agent = _selected(result)
    product_name = _product_name(result)
    profile_label = _profile_label(result)
    architecture = result.get("recommended_architecture") or {}
    primitives = architecture.get("selected_primitives", [])
    primitive_text = " -> ".join(primitives[:8]) + (" -> ..." if len(primitives) > 8 else "")

    boxes = [
        ("Company Profile", profile_label, "#e8f4f1"),
        ("Consulting Evidence", "Company context + Japan AI/DX evidence", "#eef2ff"),
        ("Opportunity Search", agent.get("name", "Selected AI enablement opportunity"), "#fff7ed"),
        ("Primitive Composition", primitive_text or "Harness primitives", "#f0fdf4"),
        ("Generated Product", product_name, "#fdf2f8"),
    ]

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="420" viewBox="0 0 1180 420">',
        "<defs>",
        '<marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">',
        '<path d="M0,0 L0,6 L9,3 z" fill="#607080"/>',
        "</marker>",
        "</defs>",
        '<rect width="1180" height="420" fill="#f8fafc"/>',
        f'<text x="34" y="42" font-size="24" font-weight="800" fill="#172026">{escape(product_name)} Architecture</text>',
        f'<text x="34" y="70" font-size="13" fill="#53606b">Selected opportunity: {escape(agent.get("name", "selected opportunity"))}</text>',
        f'<text x="34" y="92" font-size="12" fill="#53606b">Business value: {escape(agent.get("expected_business_value", "Evidence-grounded enterprise AI enablement workflow"))}</text>',
    ]

    x = 34
    for index, (title, subtitle, fill) in enumerate(boxes):
        parts.append(_box(x, 118, 200, 96, title, subtitle, fill))
        if index < len(boxes) - 1:
            parts.append(_arrow(x + 200, 166, x + 238, 166))
        x += 238

    review = result.get("review", {})
    evaluation = result.get("evaluation_results", {})
    parts.append(_box(154, 282, 260, 76, "Human Approval Gate", "Blocks external, regulated, or irreversible actions", "#ecfeff"))
    parts.append(_box(460, 282, 260, 76, "Evaluation", f"{evaluation.get('passed', '--')}/{evaluation.get('total', '--')} checks passed", "#f7fee7"))
    parts.append(_box(766, 282, 260, 76, "Automated Reviewer", f"Score: {review.get('overall_score', '--')}", "#faf5ff"))
    parts.append(_arrow(560, 214, 560, 282))
    parts.append(_arrow(414, 320, 460, 320))
    parts.append(_arrow(720, 320, 766, 320))
    parts.append("</svg>")

    output_path.write_text("\n".join(parts) + "\n", encoding="utf-8")
    return output_path


def write_opportunity_score_chart(
    opportunities: list[dict],
    feasibility_results: list[dict],
    output_path: Path,
    *,
    selected_name: str = "",
    profile_label: str = "",
) -> Path:
    """Write a compact SVG bar chart of opportunity scores."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    feasibility_lookup = {item.get("name"): item for item in feasibility_results}
    rows = []
    for opportunity in opportunities[:8]:
        score = feasibility_lookup.get(opportunity.get("name"), {}).get("overall_score", opportunity.get("score", 0))
        rows.append((opportunity.get("name", "Opportunity"), float(score or 0)))
    if not rows:
        rows = [("No opportunities generated", 0.0)]

    height = 110 + len(rows) * 42
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1040" height="{height}" viewBox="0 0 1040 {height}">',
        f'<rect width="1040" height="{height}" fill="#f8fafc"/>',
        f'<text x="28" y="38" font-size="22" font-weight="800" fill="#172026">Opportunity Scores for {escape(profile_label or "Current Profile")}</text>',
        f'<text x="28" y="64" font-size="12" fill="#53606b">Selected: {escape(selected_name or "highest reviewed opportunity")} | Business value, feasibility, Japan fit, and product buildability.</text>',
    ]
    for index, (name, score) in enumerate(rows):
        y = 94 + index * 42
        width = max(8, int(score * 82))
        color = "#b45309" if selected_name and name == selected_name else "#136f63"
        parts.append(f'<text x="28" y="{y + 16}" font-size="12" font-weight="700" fill="#172026">{escape(name[:82])}</text>')
        parts.append(f'<rect x="430" y="{y}" width="500" height="18" rx="5" fill="#e5eaf0"/>')
        parts.append(f'<rect x="430" y="{y}" width="{width}" height="18" rx="5" fill="{color}"/>')
        parts.append(f'<text x="948" y="{y + 15}" font-size="12" font-weight="700" fill="#172026">{score:.1f}</text>')
    parts.append("</svg>")
    output_path.write_text("\n".join(parts) + "\n", encoding="utf-8")
    return output_path


def write_solution_pipeline_diagram(result: dict, output_path: Path) -> Path:
    """Write an SVG of the consulting-agent to code-agent workflow."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    selected = _selected(result)
    product_name = _product_name(result)
    profile_label = _profile_label(result)
    steps = [
        ("Company Profile", profile_label),
        ("Consulting Agent", "business analysis and opportunity discovery"),
        ("Tree Search", "score, critique, refine, select"),
        ("Software Builder", product_name),
        ("Sandbox", "compile, tests, CLI, API evaluation"),
        ("Reviewer", "score product and architecture"),
    ]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="340" viewBox="0 0 1180 340">',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#607080"/></marker></defs>',
        '<rect width="1180" height="340" fill="#f8fafc"/>',
        f'<text x="30" y="42" font-size="24" font-weight="800" fill="#172026">{escape(product_name)} Generation Pipeline</text>',
        f'<text x="30" y="70" font-size="13" fill="#53606b">Selected opportunity: {escape(selected.get("name", "selected opportunity"))}</text>',
    ]
    x = 30
    fills = ["#e8f4f1", "#eef2ff", "#fff7ed", "#f0fdf4", "#fdf2f8", "#ecfeff"]
    for index, (title, subtitle) in enumerate(steps):
        parts.append(_box(x, 126, 160, 78, title, subtitle, fills[index]))
        if index < len(steps) - 1:
            parts.append(_arrow(x + 160, 165, x + 194, 165))
        x += 194
    parts.append(_box(230, 250, 260, 58, "AI Scientist Analogy", "idea -> plan -> code -> run -> review -> repair", "#f7fee7"))
    parts.append(_box(560, 250, 320, 58, "Software Builder Loop", "PRD -> architecture -> files -> tests -> evaluation", "#faf5ff"))
    parts.append("</svg>")
    output_path.write_text("\n".join(parts) + "\n", encoding="utf-8")
    return output_path
