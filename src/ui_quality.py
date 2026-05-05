"""Static UI quality gates for generated enterprise product frontends."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


REQUIRED_CSS_PATTERNS = {
    "global_border_box": r"\*\s*\{[^}]*box-sizing\s*:\s*border-box",
    "no_horizontal_page_overflow": r"overflow-x\s*:\s*hidden",
    "safe_text_wrapping": r"overflow-wrap\s*:\s*anywhere",
    "responsive_kpi_grid": r"\.kpi-strip\s*\{[^}]*repeat\(auto-fit,\s*minmax\(",
    "tablet_breakpoint": r"@media\s*\(min-width:\s*881px\)\s*and\s*\(max-width:\s*1280px\)",
    "desktop_mid_breakpoint": r"@media\s*\(min-width:\s*1281px\)\s*and\s*\(max-width:\s*1560px\)",
    "mobile_breakpoint": r"@media\s*\(max-width:\s*880px\)",
    "panel_min_width_zero": r"\.panel\s*\{[^}]*min-width\s*:\s*0",
    "workspace_overflow_guard": r"\.workspace\s*\{[^}]*overflow\s*:\s*hidden",
}


REQUIRED_HTML_MARKERS = [
    "app-shell",
    "sidebar",
    "caseQueue",
    "summaryCards",
    "draftEditor",
    "evidenceSources",
]


def check_frontend_responsiveness(app_dir: Path) -> dict[str, Any]:
    """Check that generated CSS/HTML include responsive enterprise UI guards."""
    app_dir = Path(app_dir)
    css_path = app_dir / "frontend" / "styles.css"
    html_path = app_dir / "frontend" / "index.html"
    js_path = app_dir / "frontend" / "app.js"
    missing_files = [
        str(path.relative_to(app_dir))
        for path in (css_path, html_path, js_path)
        if not path.exists()
    ]
    if missing_files:
        return {
            "name": "frontend_responsiveness_harness",
            "success": False,
            "missing_files": missing_files,
            "missing_css_patterns": list(REQUIRED_CSS_PATTERNS),
            "missing_html_markers": REQUIRED_HTML_MARKERS,
        }

    css = css_path.read_text(encoding="utf-8")
    html = html_path.read_text(encoding="utf-8")
    missing_css_patterns = [
        name
        for name, pattern in REQUIRED_CSS_PATTERNS.items()
        if not re.search(pattern, css, flags=re.IGNORECASE | re.DOTALL)
    ]
    missing_html_markers = [marker for marker in REQUIRED_HTML_MARKERS if marker not in html]
    fixed_six_col_kpi = bool(re.search(r"\.kpi-strip\s*\{[^}]*repeat\(6,\s*minmax", css, flags=re.I | re.S))
    fixed_desktop_only_workgrid = bool(
        re.search(r"\.work-grid\s*\{[^}]*minmax\(340px", css, flags=re.I | re.S)
    )
    global_header_or_main = bool(re.search(r"(^|\n)\s*(header|main)\s*\{", css))
    return {
        "name": "frontend_responsiveness_harness",
        "success": (
            not missing_css_patterns
            and not missing_html_markers
            and not fixed_six_col_kpi
            and not fixed_desktop_only_workgrid
            and not global_header_or_main
        ),
        "checked_files": ["frontend/index.html", "frontend/styles.css", "frontend/app.js"],
        "missing_css_patterns": missing_css_patterns,
        "missing_html_markers": missing_html_markers,
        "anti_patterns": {
            "fixed_six_column_kpi": fixed_six_col_kpi,
            "fixed_desktop_only_workgrid": fixed_desktop_only_workgrid,
            "unscoped_global_header_or_main": global_header_or_main,
        },
        "contract": {
            "kpi_cards_must_wrap": True,
            "tablet_breakpoint_required": True,
            "mobile_breakpoint_required": True,
            "raw_json_secondary": True,
            "no_horizontal_overflow": True,
        },
    }
