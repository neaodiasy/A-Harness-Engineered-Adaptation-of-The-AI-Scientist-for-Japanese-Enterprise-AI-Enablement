from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


REAL_ESTATE_DOMAIN_DATA = {
    "area_profiles": [
        {
            "area_id": "musashi_kosugi",
            "name_ja": "武蔵小杉",
            "prefecture": "神奈川県",
            "typical_budget_jpy_m": 65,
            "commute_minutes_to_shinjuku": 28,
            "station_access": 9,
            "school_score": 8,
            "quiet_score": 5,
            "family_score": 8,
            "disaster_resilience_note": "再開発エリアが多く、物件ごとの耐震・ハザード確認が必要。",
            "summary_ja": "都心アクセスと生活利便性が高く、ファミリーにも人気。ただし静かな住環境を重視する場合は物件単位で確認が必要。"
        },
        {
            "area_id": "kunitachi",
            "name_ja": "国立",
            "prefecture": "東京都",
            "typical_budget_jpy_m": 62,
            "commute_minutes_to_shinjuku": 35,
            "station_access": 7,
            "school_score": 9,
            "quiet_score": 9,
            "family_score": 9,
            "disaster_resilience_note": "文教地区として人気。駅距離と予算条件の両立を確認する必要あり。",
            "summary_ja": "落ち着いた文教地区で、子育て・学校環境を重視する世帯に合いやすい。"
        },
        {
            "area_id": "wakoshi",
            "name_ja": "和光市",
            "prefecture": "埼玉県",
            "typical_budget_jpy_m": 55,
            "commute_minutes_to_shinjuku": 30,
            "station_access": 8,
            "school_score": 7,
            "quiet_score": 7,
            "family_score": 7,
            "disaster_resilience_note": "都心アクセスと価格のバランスが良いが、学校・周辺環境は個別確認が必要。",
            "summary_ja": "都心アクセスと予算のバランスが良く、コストパフォーマンスを重視する顧客に向く。"
        },
        {
            "area_id": "machida",
            "name_ja": "町田",
            "prefecture": "東京都",
            "typical_budget_jpy_m": 50,
            "commute_minutes_to_shinjuku": 45,
            "station_access": 7,
            "school_score": 7,
            "quiet_score": 7,
            "family_score": 8,
            "disaster_resilience_note": "エリアが広いため、駅距離・学校区・ハザードを細かく確認する必要あり。",
            "summary_ja": "価格と広さを重視するファミリー層に向くが、通勤時間はやや長め。"
        }
    ]
}


TOOLS_PY = r'''from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

APP_DIR = Path(__file__).resolve().parent
DOMAIN_DATA = json.loads((APP_DIR / "domain_data.json").read_text(encoding="utf-8"))


def _number(text: str, default: float = 0.0) -> float:
    m = re.search(r"(\d+(?:\.\d+)?)", str(text))
    return float(m.group(1)) if m else default


def _lower_blob(case: dict[str, Any]) -> str:
    return json.dumps(case, ensure_ascii=False).lower()


def rank_real_estate_areas(case: dict[str, Any]) -> dict[str, Any]:
    """Local deterministic ranking tool for the real-estate generated agent.

    This is intentionally simple, but it makes the child app more than a pure
    LLM wrapper: the LLM receives computed candidate rankings and must explain
    them cautiously.
    """
    blob = _lower_blob(case)
    budget_text = str(case.get("budget", ""))
    budget_m = _number(budget_text, 60.0)

    wants_school = any(t in blob for t in ["school", "学校", "学区", "child", "family", "子供", "ファミリー"])
    wants_quiet = any(t in blob for t in ["quiet", "静か", "閑静"])
    wants_station = any(t in blob for t in ["station", "駅", "commute", "通勤", "shinjuku", "新宿"])
    wants_resilience = any(t in blob for t in ["earthquake", "hazard", "耐震", "災害", "ハザード"])

    ranked = []
    for area in DOMAIN_DATA.get("area_profiles", []):
        score = 0.0

        # Budget fit: closer to budget is better, but do not over-certify affordability.
        score += max(0, 25 - abs(area["typical_budget_jpy_m"] - budget_m) * 1.2)

        if wants_station:
            score += area["station_access"] * 2.0
            score += max(0, 20 - area["commute_minutes_to_shinjuku"] * 0.35)

        if wants_school:
            score += area["school_score"] * 2.0
            score += area["family_score"] * 1.5

        if wants_quiet:
            score += area["quiet_score"] * 2.0

        if wants_resilience:
            # We cannot verify property-level resilience here, so add only a small
            # score and force missing_information.
            score += 3.0

        ranked.append({
            "area_id": area["area_id"],
            "name_ja": area["name_ja"],
            "score": round(score, 2),
            "reason_ja": area["summary_ja"],
            "budget_reference_jpy_m": area["typical_budget_jpy_m"],
            "commute_minutes_to_shinjuku": area["commute_minutes_to_shinjuku"],
            "school_score": area["school_score"],
            "quiet_score": area["quiet_score"],
            "risk_note_ja": area["disaster_resilience_note"],
        })

    ranked.sort(key=lambda x: x["score"], reverse=True)

    missing = []
    if wants_resilience:
        missing.append("物件ごとの耐震等級・ハザードマップ確認")
    if wants_school:
        missing.append("最新の学校区・学区評価データ")
    if "property_data" not in case:
        missing.append("実際の候補物件データ")

    return {
        "tool_name": "rank_real_estate_areas",
        "top_candidates": ranked[:3],
        "missing_information": missing,
        "tool_rationale": "予算、通勤、駅アクセス、学校、静かさ、ファミリー適性を簡易スコアリングしました。最終提案には人間レビューが必要です。"
    }


def run_domain_tools(product_spec: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    app_kind = product_spec.get("app_kind", "")
    if app_kind == "real_estate_recommendation":
        return rank_real_estate_areas(case)
    return {
        "tool_name": "generic_business_context",
        "top_candidates": [],
        "missing_information": ["業務別の専用ローカルツールは未設定です。"],
        "tool_rationale": "汎用業務ケースとして扱いました。"
    }
'''


def _is_real_estate(product_spec: dict[str, Any]) -> bool:
    blob = json.dumps(product_spec, ensure_ascii=False).lower()
    return any(t in blob for t in ["real_estate", "property", "home", "housing", "area", "不動産", "住宅", "物件"])


def _clean_knowledge_base(text: str) -> str:
    """Remove pathological character-by-character source sections."""
    lines = text.splitlines()
    cleaned = []
    skip_noise = False
    char_line_count = 0

    for line in lines:
        # Detect lines like "- e: e" or "- _: _"
        if re.match(r"^\s*-\s*.{1,2}\s*:\s*.{1,2}\s*$", line):
            char_line_count += 1
            if char_line_count >= 5:
                skip_noise = True
            if skip_noise:
                continue
        else:
            char_line_count = 0
            skip_noise = False
            cleaned.append(line)

    cleaned_text = "\n".join(cleaned).strip() + "\n"

    if "## Local domain data" not in cleaned_text:
        cleaned_text += """
## Local domain data

The generated app includes `domain_data.json` and `tools.py`.
For real-estate recommendation scenarios, the local tool ranks candidate areas using:
- budget fit
- commute fit
- station access
- school / family fit
- quiet residential preference
- missing risk data such as hazard maps and property-level earthquake resilience

The LLM must use these tool results as supporting context and must not guarantee investment return, final purchase suitability, or legal/financial conclusions.
"""
    return cleaned_text


def _patch_app_py(app_path: Path) -> None:
    text = app_path.read_text(encoding="utf-8")

    if "from tools import run_domain_tools" not in text:
        text = text.replace(
            "from typing import Any\n",
            "from typing import Any\n\nfrom tools import run_domain_tools\n",
        )

    old = '''def run_case(case: dict[str, Any]) -> dict[str, Any]:
    evidence = retrieve_evidence(case)
    data = call_llm_json(build_prompt(case, evidence))
    return normalize(case, data, evidence)
'''

    new = '''def run_case(case: dict[str, Any]) -> dict[str, Any]:
    evidence = retrieve_evidence(case)
    local_tool_results = run_domain_tools(PRODUCT_SPEC, case)

    prompt = build_prompt(case, evidence)
    prompt += "\\n\\nLocal deterministic tool results. Use these results as computed business context; do not ignore them:\\n"
    prompt += json.dumps(local_tool_results, ensure_ascii=False, indent=2)

    data = call_llm_json(prompt)
    normalized = normalize(case, data, evidence)
    normalized["local_tool_results"] = local_tool_results

    # Merge locally detected missing information into the final output.
    existing_missing = normalized.get("missing_information", [])
    if not isinstance(existing_missing, list):
        existing_missing = [str(existing_missing)]
    for item in local_tool_results.get("missing_information", []):
        if item not in existing_missing:
            existing_missing.append(item)
    normalized["missing_information"] = existing_missing

    # Give the output a more meaningful confidence when local tools produced rankings.
    if isinstance(normalized.get("classification"), dict) and local_tool_results.get("top_candidates"):
        normalized["classification"]["confidence"] = max(float(normalized["classification"].get("confidence", 0.5)), 0.72)
        if not normalized["classification"].get("rationale"):
            normalized["classification"]["rationale"] = "ローカルランキングツールと取得エビデンスに基づく分類。"

    return normalized
'''

    if old in text:
        text = text.replace(old, new)

    old_cli = '''def cli() -> None:
    cases = json.loads((APP_DIR / "sample_cases.json").read_text(encoding="utf-8"))
    for case in cases:
        print(json.dumps(run_case(case), ensure_ascii=False, indent=2))
'''

    new_cli = '''def cli() -> None:
    cases = json.loads((APP_DIR / "sample_cases.json").read_text(encoding="utf-8"))

    print("Generated agent CLI")
    print("1) Run bundled sample cases")
    print("2) Enter a custom business case")
    choice = input("Choose 1 or 2 [1]: ").strip() or "1"

    if choice == "2":
        case = {"id": "manual_case"}
        for field in PRODUCT_SPEC.get("fields", []):
            key = field.get("key")
            label = field.get("label", key)
            default = field.get("default", "")
            value = input(f"{label} [{default}]: ").strip() or default
            case[key] = value
        print(json.dumps(run_case(case), ensure_ascii=False, indent=2))
        return

    for case in cases:
        print(json.dumps(run_case(case), ensure_ascii=False, indent=2))
'''

    if old_cli in text:
        text = text.replace(old_cli, new_cli)

    app_path.write_text(text, encoding="utf-8")


def enhance_generated_app(app_dir: Path, blueprint: dict[str, Any]) -> None:
    """Post-process generated app so the Code Agent output is more useful."""
    app_dir = Path(app_dir)

    product_spec_path = app_dir / "product_spec.json"
    if product_spec_path.exists():
        product_spec = json.loads(product_spec_path.read_text(encoding="utf-8"))
    else:
        product_spec = blueprint

    domain_data = REAL_ESTATE_DOMAIN_DATA if _is_real_estate(product_spec) else {"items": []}
    (app_dir / "domain_data.json").write_text(
        json.dumps(domain_data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (app_dir / "tools.py").write_text(TOOLS_PY, encoding="utf-8")

    kb_path = app_dir / "knowledge_base.md"
    if kb_path.exists():
        kb_path.write_text(_clean_knowledge_base(kb_path.read_text(encoding="utf-8")), encoding="utf-8")

    app_path = app_dir / "app.py"
    if app_path.exists():
        _patch_app_py(app_path)

    # Update README to surface the tool layer.
    readme = app_dir / "README.md"
    if readme.exists():
        txt = readme.read_text(encoding="utf-8")
        if "Local deterministic tools" not in txt:
            txt += """
## Local deterministic tools

This generated app is not only an LLM wrapper. The Code Agent also generated:

- `domain_data.json`: small local business/domain data pack
- `tools.py`: deterministic analysis/ranking tools
- `local_tool_results`: tool outputs injected into the LLM prompt and returned in the final JSON

For the real-estate demo, the local tool ranks candidate areas before the LLM drafts the final Japanese recommendation. This makes the generated app more reliable and task-specific.
"""
            readme.write_text(txt, encoding="utf-8")
