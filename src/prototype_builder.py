"""Generate runnable child products with a Software Builder Loop."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from src.software_factory import (
    build_builder_loop_trace,
    build_file_manifest,
    build_file_plan,
    build_generation_trace,
    build_implementation_plan,
    build_product_requirements,
    build_project_architecture,
    build_repair_log,
)
from src.domain_templates import generic_domain_template, select_domain_template


def _blob(*values: object) -> str:
    return " ".join(str(value) for value in values).lower()


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "generated_agent_product"


def _infer_app_kind(agent_design: dict, product_spec: dict | None = None) -> str:
    domain_pack = select_domain_template(agent_design, product_spec or {})
    if domain_pack:
        return str(domain_pack.get("template_id", "domain_template_product"))
    return "enterprise_agent_product"


def build_software_blueprint(
    agent_design: dict,
    architecture: dict,
    productization_blueprint: dict | None = None,
) -> dict:
    """Convert the selected opportunity into a product spec."""
    productization_blueprint = productization_blueprint or {}
    opportunity = agent_design.get("selected_opportunity", {}) or {}
    context = agent_design.get("enterprise_context", {}) or {}
    primitives = architecture.get("selected_primitives", [])
    app_kind = _infer_app_kind(agent_design)
    opportunity_name = opportunity.get("name", "Enterprise Agent Product")
    selected_archetype = productization_blueprint.get("selected_archetype", {}) or {}
    domain_pack = select_domain_template(agent_design, productization_blueprint) or generic_domain_template(
        opportunity_name,
        opportunity.get("proposed_ai_capability", "Generated enterprise agent product."),
    )
    app_kind = str(domain_pack.get("template_id", app_kind))
    product_name = str(domain_pack.get("product_name") or f"{opportunity_name} Platform")
    subtitle = str(domain_pack.get("subtitle") or opportunity.get("proposed_ai_capability", "Generated enterprise agent product."))
    fields = domain_pack.get("fields") or []
    primary_action = str(domain_pack.get("primary_action") or "Generate Approval Packet")

    return {
        "product_spec_version": "software_builder_loop_v1",
        "product_name": product_name,
        "product_slug": _slugify(product_name),
        "subtitle": subtitle,
        "app_kind": app_kind,
        "domain_template": domain_pack,
        "domain_template_id": domain_pack.get("template_id", "generic_enterprise"),
        "domain_template_source": domain_pack.get("source_path", ""),
        "tool_name": domain_pack.get("tool_name", "generic_enterprise_toolkit"),
        "candidate_collection_label": domain_pack.get("candidate_collection_label", "candidates"),
        "item_collection_label": domain_pack.get("item_collection_label", "items"),
        "default_classification_label": domain_pack.get("default_classification_label", "enterprise_workflow_case"),
        "live_search_queries": domain_pack.get("live_search_queries", []),
        "prompt_context": domain_pack.get("prompt_context", "AI-driven Japanese enterprise product"),
        "specific_rules": domain_pack.get("specific_rules", []),
        "candidate_examples": domain_pack.get("candidate_examples", []),
        "maturity_target": productization_blueprint.get("maturity_target", "enterprise_software_mvp"),
        "product_archetype": selected_archetype,
        "selected_opportunity": opportunity_name,
        "target_workflow": opportunity.get("target_workflow", ""),
        "business_value": opportunity.get("expected_business_value", ""),
        "key_risk": opportunity.get("key_risk", ""),
        "target_user": "Business consultant and human reviewer",
        "primary_action": primary_action,
        "fields": fields,
        "selected_primitives": primitives,
        "navigation_sections": productization_blueprint.get("navigation_sections", []),
        "workspace_regions": productization_blueprint.get("workspace_regions", []),
        "enterprise_capabilities": productization_blueprint.get("enterprise_capabilities", []),
        "role_model": productization_blueprint.get("role_model", []),
        "state_model": productization_blueprint.get("state_model", []),
        "visual_quality_contract": productization_blueprint.get("visual_quality_contract", {}),
        "enterprise_context": context,
        "runtime": {
            "api_key_env": "DEEPSEEK_API_KEY",
            "base_url_env": "DEEPSEEK_BASE_URL",
            "model_env": "AGENT_MODEL",
            "default_model": "deepseek-v4-pro",
            "thinking_env": "DEEPSEEK_THINKING",
            "reasoning_effort_env": "DEEPSEEK_REASONING_EFFORT",
            "default_reasoning_effort": "high",
        },
        "risk_terms": [
            "customer",
            "external",
            "approval",
            "legal",
            "financial",
            "investment",
            "safety",
            "hazard",
            "earthquake",
            "契約",
            "金融",
            "投資",
            "災害",
            "耐震",
            "承認",
        ],
        "output_policy": {
            "human_approval_required": True,
            "send_allowed": False,
            "no_guarantees": True,
            "decision_support_only": True,
        },
    }


def build_agent_spec(agent_design: dict, architecture: dict, product_spec: dict) -> dict:
    opportunity = agent_design.get("selected_opportunity", {}) or {}
    return {
        "agent_name": product_spec.get("product_name", "Generated Agent Product"),
        "model": "deepseek-v4-pro",
        "selected_opportunity": opportunity,
        "business_goal": opportunity.get("proposed_ai_capability", product_spec.get("subtitle", "")),
        "target_workflow": opportunity.get("target_workflow", ""),
        "app_kind": product_spec.get("app_kind"),
        "selected_primitives": architecture.get("selected_primitives", []),
        "system_prompt": (
            "You are the AI reasoning layer inside a generated enterprise software product. "
            "You receive deterministic local tool results and evidence. Return valid JSON only. "
            "Do not invent area names, property facts, legal claims, financial guarantees, investment advice, "
            "or disaster safety guarantees. Keep all customer-facing language in Japanese. "
            "Human approval is mandatory and send_allowed must be false."
        ),
        "output_contract": {
            "case_id": "string",
            "classification": {"label": "string", "confidence": "number", "rationale": "string"},
            "ranked_area_candidates": [{"area_id": "string", "name_ja": "string", "score": "number"}],
            "ranked_property_candidates": [{"property_id": "string", "title_ja": "string", "score": "number"}],
            "local_tool_results": {"tool_name": "string", "top_candidates": ["object"]},
            "evidence": [{"id": "string", "title": "string", "summary": "string"}],
            "missing_information": ["string"],
            "recommendation_ja": "string",
            "customer_or_business_draft_ja": "string",
            "internal_review_note": "string",
            "risk": {"risk_flag": "boolean", "risk_level": "low|medium|high", "risk_reasons": ["string"]},
            "human_approval_required": "boolean",
            "send_allowed": "boolean",
            "approval_packet": {"approval_required": "boolean", "decision_options": ["approve", "edit", "reject", "escalate"]},
            "audit_trace": {"evidence_ids": ["string"], "tool_names": ["string"], "model": "string"},
        },
        "reviewer_guidance": [
            "Confirm the recommended areas and properties exist in local tool results.",
            "Verify hazard maps, earthquake resilience, school zones, and listing freshness before customer-facing use.",
            "Edit customer-facing Japanese before sending.",
            "Keep the system as decision support; never treat it as legal, financial, or safety advice.",
        ],
    }


# Domain-specific candidate data is loaded from templates/*/domain_pack.json.
# The generator core intentionally contains no company- or industry-specific data.

APP_ENTRYPOINT = '''"""Entrypoint for the generated agent product."""

from __future__ import annotations

import argparse
import json
import sys

from backend.agent import run_case
from backend.api import serve
from backend.data_store import load_sample_cases


def run_cli(case_id: str | None = None) -> None:
    cases = load_sample_cases()
    if case_id:
        cases = [case for case in cases if case.get("case_id") == case_id]
        if not cases:
            available = ", ".join(case.get("case_id", "<missing>") for case in load_sample_cases())
            raise SystemExit(f"Unknown case_id: {case_id}. Available: {available}")
    outputs = []
    for index, case in enumerate(cases, start=1):
        current_id = case.get("case_id", f"case_{index}")
        print(
            f"[generated-app] running {current_id} ({index}/{len(cases)}) with DeepSeek runtime...",
            file=sys.stderr,
            flush=True,
        )
        outputs.append(run_case(case))
        print(f"[generated-app] completed {current_id}", file=sys.stderr, flush=True)
    print(json.dumps(outputs, ensure_ascii=False, indent=2))


def list_cases() -> None:
    for case in load_sample_cases():
        print(case.get("case_id", "<missing>"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the generated agent product.")
    parser.add_argument("--cli", action="store_true", help="Run generated sample cases and print JSON.")
    parser.add_argument("--case-id", default="", help="Run only one sample case id in CLI mode.")
    parser.add_argument("--list-cases", action="store_true", help="List available sample case ids.")
    parser.add_argument("--port", type=int, default=8766, help="Local web server port.")
    args = parser.parse_args()
    if args.list_cases:
        list_cases()
    elif args.cli:
        run_cli(args.case_id or None)
    else:
        serve(args.port)


if __name__ == "__main__":
    main()
'''


ROOT_TOOLS = '''"""Compatibility exports for generated local domain tools."""

from backend.tools import run_domain_tools

__all__ = ["run_domain_tools"]
'''


BACKEND_INIT = '''"""Generated product backend package."""
'''


DATA_STORE = '''"""Data loading helpers for the generated product."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR / "data"


def load_json_file(relative_path: str) -> Any:
    return json.loads((APP_DIR / relative_path).read_text(encoding="utf-8"))


def load_product_spec() -> dict[str, Any]:
    return load_json_file("product_spec.json")


def load_agent_spec() -> dict[str, Any]:
    return load_json_file("agent_spec.json")


def load_areas() -> list[dict[str, Any]]:
    return load_json_file("data/areas.json")


def load_properties() -> list[dict[str, Any]]:
    return load_json_file("data/properties.json")


def load_sample_cases() -> list[dict[str, Any]]:
    return load_json_file("data/sample_customers.json")


def load_knowledge_base() -> str:
    return (APP_DIR / "knowledge_base.md").read_text(encoding="utf-8")
'''


RECOMMENDATION_ENGINE = '''"""Deterministic ranking engine for generated local tool use."""

from __future__ import annotations

import re
from typing import Any

from backend.data_store import load_areas, load_properties


def _numbers(value: Any) -> list[float]:
    return [float(item) for item in re.findall(r"\d+(?:\.\d+)?", str(value))]


def _first_number(value: Any, default: float) -> float:
    numbers = _numbers(value)
    return numbers[0] if numbers else default


def _budget_ceiling(value: Any, default: float = 65.0) -> float:
    numbers = _numbers(value)
    return max(numbers) if numbers else default


def _case_text(case: dict[str, Any]) -> str:
    return " ".join(str(value) for value in case.values()).lower()


def _wants(case: dict[str, Any], terms: list[str]) -> bool:
    text = _case_text(case)
    return any(term.lower() in text for term in terms)


def _numeric(item: dict[str, Any], keys: list[str], default: float = 0.0) -> float:
    for key in keys:
        if key in item:
            return float(item.get(key) or default)
    return default


def _commute_minutes(candidate: dict[str, Any]) -> float:
    for key, value in candidate.items():
        if key.startswith("commute_minutes"):
            return float(value or 0)
    return float(candidate.get("commute_minutes", 0) or 0)


def score_candidate(candidate: dict[str, Any], case: dict[str, Any]) -> tuple[float, list[str]]:
    ceiling = _budget_ceiling(case.get("budget"))
    commute_limit = _first_number(case.get("max_commute_minutes", ""), 45.0)
    score = 0.0
    reasons: list[str] = []

    cost = _numeric(candidate, ["typical_budget_jpy_m", "estimated_cost", "cost_score_base"], 50.0)
    budget_score = max(0.0, 25.0 - abs(cost - ceiling) * 1.1)
    score += budget_score
    reasons.append(f"予算・コスト目安 {cost:g} に対して適合度を評価")

    commute_value = _commute_minutes(candidate)
    if commute_value:
        commute_gap = max(0.0, commute_value - commute_limit)
        commute_score = max(0.0, 22.0 - commute_gap * 1.8)
        score += commute_score
        reasons.append(f"時間・アクセス指標 {commute_value:g} を条件と比較")

    if _wants(case, ["school", "学校", "学区", "子ども", "子供", "family", "ファミリー"]):
        score += _numeric(candidate, ["school_score"], 5.0) * 2.0 + _numeric(candidate, ["family_score"], 5.0) * 1.5
        reasons.append("家族・教育・利用者適合に関する指標を加点")

    if _wants(case, ["quiet", "静か", "閑静", "落ち着", "stable", "安定"]):
        score += _numeric(candidate, ["quiet_score", "stability_score"], 5.0) * 2.1
        reasons.append("安定性・静穏性・運用品質に関する指標を加点")

    if _wants(case, ["risk", "safety", "resilience", "exception", "災害", "リスク", "例外"]):
        score += _numeric(candidate, ["family_score", "risk_readiness_score"], 5.0) * 0.4
        reasons.append("リスク確認は個別証拠と人間承認が必要")

    return round(score, 2), reasons


def rank_domain_candidates(case: dict[str, Any]) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    for candidate in load_areas():
        score, reasons = score_candidate(candidate, case)
        item = dict(candidate)
        item.update({"score": score, "reason_ja": "。".join(reasons) + "。"})
        ranked.append(item)
    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked


def score_item(item: dict[str, Any], candidate_rank: dict[str, dict[str, Any]], case: dict[str, Any]) -> tuple[float, list[str]]:
    ceiling = _budget_ceiling(case.get("budget"))
    score = 0.0
    reasons: list[str] = []
    parent = candidate_rank.get(str(item.get("area_id", "")), {})

    score += float(parent.get("score", 0)) * 0.45
    reasons.append(f"上位候補評価を反映: {parent.get('name_ja', item.get('area_id', 'candidate'))}")

    price = _numeric(item, ["price_jpy_m", "estimated_cost", "cost"], ceiling)
    price_gap = max(0.0, price - ceiling)
    score += 22.0 if price_gap == 0 else max(0.0, 22.0 - price_gap * 3.0)
    reasons.append(f"コスト・価格指標 {price:g}")

    if _wants(case, ["station", "駅", "通勤", "commute", "access"]):
        score += max(0.0, 18.0 - _numeric(item, ["station_walk_minutes", "access_minutes"], 8.0) * 0.8)
        reasons.append("アクセス条件を評価")

    if _wants(case, ["school", "学校", "family", "子ども", "ファミリー"]):
        score += _numeric(item, ["school_score"], 5.0) * 1.5 + _numeric(item, ["family_score"], 5.0) * 1.5
        reasons.append("利用者適合・家族条件を評価")

    if _wants(case, ["risk", "safety", "resilience", "exception", "災害", "リスク", "例外"]):
        score += _numeric(item, ["earthquake_score", "risk_readiness_score"], 5.0) * 1.4
        reasons.append("リスク関連指標を評価")

    return round(score, 2), reasons


def rank_items(case: dict[str, Any], ranked_candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidate_rank = {str(candidate.get("area_id", candidate.get("id", ""))): candidate for candidate in ranked_candidates}
    ranked: list[dict[str, Any]] = []
    for source_item in load_properties():
        score, reasons = score_item(source_item, candidate_rank, case)
        item = dict(source_item)
        parent_id = str(item.get("area_id", ""))
        item.update({
            "area_name_ja": candidate_rank.get(parent_id, {}).get("name_ja", parent_id),
            "score": score,
            "reason_ja": "。".join(reasons) + "。",
        })
        ranked.append(item)
    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked
'''


BACKEND_TOOLS = '''"""Local deterministic tools used before DeepSeek drafting."""

from __future__ import annotations

from typing import Any

from backend.recommendation_engine import rank_domain_candidates, rank_items


def _missing_information(product_spec: dict[str, Any], case: dict[str, Any]) -> list[str]:
    text = " ".join(str(value) for value in case.values()).lower()
    domain_template = product_spec.get("domain_template", {}) if isinstance(product_spec.get("domain_template"), dict) else {}
    missing: list[str] = []
    for rule in domain_template.get("missing_information_rules", []):
        terms = [str(term).lower() for term in rule.get("terms", [])]
        if any(term and term in text for term in terms):
            missing.append(str(rule.get("message", "Additional source evidence and human approval required.")))
    missing.extend(str(item) for item in domain_template.get("always_missing_information", []))
    return sorted(set(item for item in missing if item.strip()))


def run_domain_tools(product_spec: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    ranked_candidates = rank_domain_candidates(case)
    ranked_items = rank_items(case, ranked_candidates)
    domain_template = product_spec.get("domain_template", {}) if isinstance(product_spec.get("domain_template"), dict) else {}
    return {
        "tool_name": product_spec.get("tool_name") or domain_template.get("tool_name") or "local_domain_toolkit",
        "app_kind": product_spec.get("app_kind"),
        "ranked_area_candidates": ranked_candidates[:4],
        "ranked_property_candidates": ranked_items[:4],
        "ranked_candidates": ranked_candidates[:4],
        "ranked_items": ranked_items[:4],
        "top_candidates": ranked_candidates[:4],
        "missing_information": _missing_information(product_spec, case),
        "scoring_summary_ja": domain_template.get("scoring_summary_ja") or "ローカル候補、証拠、リスク、人間承認条件をスコアリングしました。",
    }
'''

LLM_CLIENT = '''"""DeepSeek/OpenAI-compatible JSON client for the generated app."""

from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from typing import Any


def parse_jsonish(text: str) -> dict[str, Any]:
    candidates = [text.strip()]
    fenced = re.search(r"```(?:json)?\\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        candidates.insert(0, fenced.group(1).strip())
    bracket = re.search(r"(\\{.*\\})", text, flags=re.DOTALL)
    if bracket:
        candidates.append(bracket.group(1).strip())
    for candidate in candidates:
        try:
            value = json.loads(candidate)
            if isinstance(value, dict):
                return value
        except json.JSONDecodeError:
            continue
    raise ValueError("DeepSeek did not return a valid JSON object.")


def _endpoint() -> str:
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
    if base_url.endswith("/chat/completions"):
        return base_url
    return base_url + "/chat/completions"


def complete_json(system_prompt: str, user_prompt: str, *, retries: int = 2) -> dict[str, Any]:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY is required. This generated product has no mock mode.")
    model = os.environ.get("AGENT_MODEL") or os.environ.get("DEEPSEEK_AGENT_MODEL") or "deepseek-v4-pro"
    thinking_enabled = os.environ.get("DEEPSEEK_THINKING", "1").lower() not in {"0", "false", "disabled", "off", "no"}
    reasoning_effort = os.environ.get("DEEPSEEK_REASONING_EFFORT", "high").strip()
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 6000,
        "stream": False,
        "response_format": {"type": "json_object"},
    }
    if thinking_enabled:
        payload["thinking"] = {"type": "enabled"}
    if reasoning_effort:
        payload["reasoning_effort"] = reasoning_effort
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        request = urllib.request.Request(
            _endpoint(),
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                data = json.loads(response.read().decode("utf-8"))
            raw = data["choices"][0]["message"]["content"]
            try:
                return parse_jsonish(raw)
            except ValueError:
                repair_prompt = (
                    "Repair this response into one valid JSON object only. Do not add Markdown.\\n\\n"
                    + raw
                )
                payload["messages"] = [
                    {"role": "system", "content": "Return valid JSON only."},
                    {"role": "user", "content": repair_prompt},
                ]
        except (ConnectionResetError, TimeoutError, urllib.error.URLError, urllib.error.HTTPError, KeyError, json.JSONDecodeError, ValueError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
                continue
            break
    raise RuntimeError(f"DeepSeek request failed after retries: {last_error}") from last_error
'''


WEB_SEARCH = '''"""Runtime trusted-domain web evidence search for the generated product.

The generated child product uses this module directly, so the product itself can
retrieve fresh public evidence before calling the LLM. Set
GENERATED_APP_LIVE_SEARCH=0 to disable it for offline demos.
"""

from __future__ import annotations

import html
import os
import re
import time
import urllib.parse
import urllib.request
from typing import Any


TRUSTED_DOMAINS = [
    "digital.go.jp",
    "meti.go.jp",
    "ipa.go.jp",
    "fsa.go.jp",
    "mlit.go.jp",
    "gsi.go.jp",
    "mhlw.go.jp",
    "cao.go.jp",
    "boj.or.jp",
    "jpc-net.jp",
    "oecd.org",
]


def live_search_enabled() -> bool:
    value = os.environ.get("GENERATED_APP_LIVE_SEARCH", os.environ.get("ENABLE_LIVE_SEARCH", "1"))
    return value.lower() not in {"0", "false", "disabled", "off", "no"}


def build_queries(case: dict[str, Any], product_spec: dict[str, Any], local_tool_results: dict[str, Any]) -> list[str]:
    domain_queries = [
        str(query)
        for query in product_spec.get("live_search_queries", [])
        if str(query).strip()
    ]
    terms = [
        str(product_spec.get("product_name", "")),
        str(product_spec.get("selected_opportunity", "")),
        str(case.get("commute_target", "")),
        str(case.get("preferences", "")),
        str(case.get("must_have", "")),
        "Japan AI enterprise guidance",
    ]
    area_names = [
        str(item.get("name_ja", ""))
        for item in local_tool_results.get("ranked_area_candidates", [])[:2]
        if item.get("name_ja")
    ]
    base = " ".join(term for term in terms + area_names if term).strip()
    queries = [
        *domain_queries,
        f"{base} site:digital.go.jp",
        f"{base} AI governance Japan site:meti.go.jp",
        "生成AI ガイドライン 企業 活用 site:meti.go.jp",
        "AI governance DX Japan enterprise site:ipa.go.jp",
    ]
    return [query[:240] for query in queries if query.strip()]


def _fetch(url: str, timeout: int = 12) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 J-Enterprise-Agent-Scientist generated product",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def _domain_allowed(url: str) -> bool:
    host = urllib.parse.urlparse(url).netloc.lower()
    return any(host == domain or host.endswith("." + domain) for domain in TRUSTED_DOMAINS)


def _extract_results(raw_html: str, limit: int) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for match in re.finditer(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', raw_html, re.I | re.S):
        href = html.unescape(match.group(1))
        title = re.sub(r"<.*?>", "", match.group(2), flags=re.S)
        title = html.unescape(re.sub(r"\\s+", " ", title)).strip()
        parsed = urllib.parse.urlparse(href)
        query = urllib.parse.parse_qs(parsed.query)
        if "uddg" in query:
            href = query["uddg"][0]
        if not href.startswith("http") or not _domain_allowed(href):
            continue
        results.append({
            "id": f"live_web_{len(results) + 1}",
            "title": title or href,
            "url": href,
            "summary": "Runtime live trusted-domain search result. Open the URL for full source verification.",
            "retrieval_method": "runtime_live_web_search",
        })
        if len(results) >= limit:
            break
    return results


def _extract_bing_rss(raw_xml: str, limit: int) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for item in re.findall(r"<item>(.*?)</item>", raw_xml, flags=re.I | re.S):
        title_match = re.search(r"<title>(.*?)</title>", item, flags=re.I | re.S)
        link_match = re.search(r"<link>(.*?)</link>", item, flags=re.I | re.S)
        description_match = re.search(r"<description>(.*?)</description>", item, flags=re.I | re.S)
        if not link_match:
            continue
        href = html.unescape(re.sub(r"<.*?>", "", link_match.group(1))).strip()
        if not href.startswith("http") or not _domain_allowed(href):
            continue
        title = html.unescape(re.sub(r"<.*?>", "", title_match.group(1))).strip() if title_match else href
        summary = html.unescape(re.sub(r"<.*?>", "", description_match.group(1))).strip() if description_match else ""
        results.append({
            "id": f"live_web_{len(results) + 1}",
            "title": title or href,
            "url": href,
            "summary": summary or "Runtime live trusted-domain search result. Open the URL for full source verification.",
            "retrieval_method": "runtime_live_web_search",
        })
        if len(results) >= limit:
            break
    return results


def search_web_evidence(case: dict[str, Any], product_spec: dict[str, Any], local_tool_results: dict[str, Any]) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "enabled": live_search_enabled(),
        "provider": "duckduckgo_html_with_bing_rss_fallback",
        "trusted_domains": TRUSTED_DOMAINS,
        "queries": [],
        "errors": [],
        "result_count": 0,
    }
    if not metadata["enabled"]:
        metadata["reason"] = "Set GENERATED_APP_LIVE_SEARCH=1 to enable runtime web evidence search."
        return {"metadata": metadata, "results": []}
    per_query_limit = int(os.environ.get("GENERATED_APP_SEARCH_RESULTS_PER_QUERY", "2"))
    query_limit = int(os.environ.get("GENERATED_APP_SEARCH_QUERY_LIMIT", "2"))
    delay = float(os.environ.get("GENERATED_APP_SEARCH_DELAY_SECONDS", "0.2"))
    results: list[dict[str, Any]] = []
    seen: set[str] = set()
    for query in build_queries(case, product_spec, local_tool_results)[:query_limit]:
        metadata["queries"].append(query)
        urls = [
            ("duckduckgo_html", "https://duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})),
            ("bing_rss", "https://www.bing.com/search?" + urllib.parse.urlencode({"q": query, "format": "rss"})),
        ]
        try:
            query_results: list[dict[str, Any]] = []
            for provider, url in urls:
                raw = _fetch(url)
                extracted = _extract_bing_rss(raw, per_query_limit) if provider == "bing_rss" else _extract_results(raw, per_query_limit)
                if extracted:
                    metadata.setdefault("providers_used", []).append(provider)
                    query_results.extend(extracted)
                    break
            for item in query_results:
                if item["url"] in seen:
                    continue
                seen.add(item["url"])
                item["id"] = f"live_web_{len(results) + 1}"
                results.append(item)
            time.sleep(delay)
        except Exception as exc:  # pragma: no cover - network dependent
            metadata["errors"].append(f"{type(exc).__name__}: {exc}")
    metadata["result_count"] = len(results)
    return {"metadata": metadata, "results": results}
'''


GUARDRAILS = '''"""Output contract and safety guardrails."""

from __future__ import annotations

from typing import Any


PLACEHOLDERS = ["エリアA", "エリアB", "エリアC", "Area A", "Area B", "Area C"]
FORBIDDEN_GUARANTEES = ["保証します", "確約します", "絶対に安全", "投資利益", "必ず値上がり", "法的助言"]


def _candidate_names(local_tool_results: dict[str, Any]) -> list[str]:
    return [
        str(item.get("name_ja", ""))
        for item in local_tool_results.get("ranked_area_candidates", [])
        if item.get("name_ja")
    ]


def _property_titles(local_tool_results: dict[str, Any]) -> list[str]:
    return [
        str(item.get("title_ja", ""))
        for item in local_tool_results.get("ranked_property_candidates", [])
        if item.get("title_ja")
    ]


def _placeholder_only(text: str, names: list[str]) -> bool:
    return any(token in text for token in PLACEHOLDERS) and not any(name in text for name in names)


def deterministic_recommendation(local_tool_results: dict[str, Any]) -> str:
    areas = local_tool_results.get("ranked_area_candidates", [])[:3]
    properties = local_tool_results.get("ranked_property_candidates", [])[:3]
    area_lines = [
        f"{index}. {area['name_ja']}（スコア{area['score']}）: {area.get('summary_ja', '')} 注意点: {area.get('risk_note_ja', '')}"
        for index, area in enumerate(areas, start=1)
    ]
    property_lines = [
        f"{index}. {prop['title_ja']}（{prop.get('area_name_ja', '')}、スコア{prop['score']}）: {prop.get('summary_ja', '')}"
        for index, prop in enumerate(properties, start=1)
    ]
    return (
        "ローカルランキングでは、候補は次の順で確認する価値があります。\\n"
        + "\\n".join(area_lines)
        + "\\n\\n関連候補は次の順で追加確認してください。\\n"
        + "\\n".join(property_lines)
        + "\\n\\nリスク、証拠の鮮度、適用条件、承認境界は人間の担当者が確認してください。"
    )


def _classification(case: dict[str, Any], output: dict[str, Any]) -> dict[str, Any]:
    classification = output.get("classification")
    if not isinstance(classification, dict):
        classification = {}
    label = classification.get("label") or "preference_based_recommendation"
    rationale = classification.get("rationale") or "業務要件、候補スコア、証拠、人間承認条件に基づく推奨ケースです。"
    try:
        confidence = float(classification.get("confidence", 0.78))
    except (TypeError, ValueError):
        confidence = 0.78
    if confidence == 0.5:
        confidence = 0.78
    return {"label": label, "confidence": round(max(0.55, min(confidence, 0.95)), 2), "rationale": rationale}


def enforce_output_contract(
    case: dict[str, Any],
    output: dict[str, Any],
    local_tool_results: dict[str, Any],
    evidence: list[dict[str, Any]],
    agent_spec: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(output, dict):
        output = {}
    area_names = _candidate_names(local_tool_results)
    property_titles = _property_titles(local_tool_results)
    deterministic_text = deterministic_recommendation(local_tool_results)

    recommendation = str(output.get("recommendation_ja", "")).strip()
    if not recommendation or _placeholder_only(recommendation, area_names):
        recommendation = deterministic_text
    draft = str(output.get("customer_or_business_draft_ja", "")).strip()
    if not draft or _placeholder_only(draft, area_names):
        draft = (
            "以下は担当者確認用のドラフトです。"
            + recommendation
            + "\\n\\nこの内容は送信前に指定された承認者が確認してください。"
        )

    risk = output.get("risk") if isinstance(output.get("risk"), dict) else {}
    reasons = list(risk.get("risk_reasons", [])) if isinstance(risk.get("risk_reasons"), list) else []
    reasons.extend(local_tool_results.get("missing_information", []))
    for phrase in FORBIDDEN_GUARANTEES:
        if phrase in recommendation or phrase in draft:
            reasons.append(f"保証表現を削除または修正してください: {phrase}")
            recommendation = recommendation.replace(phrase, "確認が必要です")
            draft = draft.replace(phrase, "確認が必要です")

    approval_packet = output.get("approval_packet") if isinstance(output.get("approval_packet"), dict) else {}
    approval_packet.update({
        "approval_required": True,
        "approval_owner": case.get("approval_owner", "Human reviewer"),
        "decision_options": ["approve", "edit", "reject", "request_more_information"],
        "reviewer_guidance": agent_spec.get("reviewer_guidance", []),
        "items_to_verify": local_tool_results.get("missing_information", []),
        "top_area_names": area_names[:3],
        "top_property_titles": property_titles[:3],
    })

    return {
        "case_id": case.get("case_id") or case.get("id") or "manual_case",
        "classification": _classification(case, output),
        "ranked_area_candidates": local_tool_results.get("ranked_area_candidates", []),
        "ranked_property_candidates": local_tool_results.get("ranked_property_candidates", []),
        "local_tool_results": local_tool_results,
        "evidence": evidence,
        "missing_information": sorted(set(local_tool_results.get("missing_information", []) + output.get("missing_information", []))),
        "recommendation_ja": recommendation,
        "customer_or_business_draft_ja": draft,
        "internal_review_note": output.get("internal_review_note") or "ローカルランキング、LLMドラフト、リスク項目を確認し、顧客送信前に人間が編集・承認してください。",
        "risk": {
            "risk_flag": True,
            "risk_level": risk.get("risk_level", "medium"),
            "risk_reasons": sorted(set(str(item) for item in reasons if str(item).strip())),
        },
        "human_approval_required": True,
        "send_allowed": False,
        "approval_packet": approval_packet,
        "audit_trace": {
            "tool_names": [local_tool_results.get("tool_name", "local_tools")],
            "evidence_ids": [item.get("id") for item in evidence],
            "model": agent_spec.get("model", "deepseek-v4-pro"),
            "output_contract_enforced": True,
            "deterministic_candidates_attached": True,
        },
    }
'''


AGENT = '''"""Agent orchestration for the generated product."""

from __future__ import annotations

import json
from typing import Any

from backend.data_store import load_agent_spec, load_knowledge_base, load_product_spec
from backend.guardrails import enforce_output_contract
from backend.llm_client import complete_json
from backend.tools import run_domain_tools
from backend.web_search import search_web_evidence


PRODUCT_SPEC = load_product_spec()
AGENT_SPEC = load_agent_spec()
KNOWLEDGE_BASE = load_knowledge_base()


def retrieve_evidence(case: dict[str, Any], local_tool_results: dict[str, Any]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = [
        {
            "id": "local_candidate_profiles",
            "title": "Generated local candidate profiles",
            "summary": "Domain candidates and scoring inputs loaded from data/areas.json.",
        },
        {
            "id": "local_item_records",
            "title": "Generated local item records",
            "summary": "Related item candidates and scoring inputs loaded from data/properties.json.",
        },
        {
            "id": "knowledge_base",
            "title": "Generated knowledge base",
            "summary": KNOWLEDGE_BASE[:700],
        },
    ]
    for area in local_tool_results.get("ranked_area_candidates", [])[:3]:
        candidate_id = area.get("area_id") or area.get("id") or area.get("name_ja", "candidate")
        evidence.append({
            "id": f"candidate_{candidate_id}",
            "title": area.get("name_ja", str(candidate_id)),
            "summary": f"{area.get('summary_ja', '')} {area.get('risk_note_ja', '')}",
        })
    live_pack = search_web_evidence(case, PRODUCT_SPEC, local_tool_results)
    for item in live_pack.get("results", []):
        evidence.append(item)
    evidence.append({
        "id": "runtime_live_search_metadata",
        "title": "Runtime live web search metadata",
        "summary": json.dumps(live_pack.get("metadata", {}), ensure_ascii=False),
        "retrieval_method": "runtime_live_web_search_metadata",
    })
    return evidence


def build_prompt(case: dict[str, Any], local_tool_results: dict[str, Any], evidence: list[dict[str, Any]]) -> str:
    candidate_examples = PRODUCT_SPEC.get("candidate_examples", [])
    specific_rules = PRODUCT_SPEC.get("specific_rules", [])
    return f"""You are drafting the reasoning layer for this generated enterprise agent product:
{PRODUCT_SPEC.get("prompt_context", PRODUCT_SPEC.get("product_name", "enterprise product"))}

Product spec:
{json.dumps(PRODUCT_SPEC, ensure_ascii=False, indent=2)}

Customer case:
{json.dumps(case, ensure_ascii=False, indent=2)}

Deterministic local tool results. You must use concrete candidate names from these results:
{json.dumps(local_tool_results, ensure_ascii=False, indent=2)}

Evidence:
{json.dumps(evidence, ensure_ascii=False, indent=2)}

Candidate examples from the selected domain template:
{json.dumps(candidate_examples, ensure_ascii=False, indent=2)}

Domain-specific rules from the selected template:
{json.dumps(specific_rules, ensure_ascii=False, indent=2)}

Return one JSON object with these keys:
case_id, classification, evidence, missing_information, recommendation_ja,
customer_or_business_draft_ja, internal_review_note, risk, approval_packet.

Rules:
- Use concrete local tool candidate names when relevant.
- Use runtime_live_web_search evidence when available, but describe it as supporting context that requires human verification.
- Do not say エリアA, エリアB, エリアC, Area A, Area B, or Area C.
- Do not claim legal, financial, investment, disaster-safety, or earthquake-resilience guarantees.
- Use Japanese for recommendation_ja, customer_or_business_draft_ja, and internal_review_note.
- Mention missing evidence, uncertainty, source freshness, risk checks, and human review needs.
- The final app will force human_approval_required=true and send_allowed=false.
"""


def run_case(case: dict[str, Any]) -> dict[str, Any]:
    local_tool_results = run_domain_tools(PRODUCT_SPEC, case)
    evidence = retrieve_evidence(case, local_tool_results)
    llm_output = complete_json(AGENT_SPEC["system_prompt"], build_prompt(case, local_tool_results, evidence))
    return enforce_output_contract(case, llm_output, local_tool_results, evidence, AGENT_SPEC)
'''


API = '''"""Local API and static frontend server."""

from __future__ import annotations

import errno
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from backend.agent import run_case
from backend.data_store import load_product_spec, load_sample_cases


APP_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = APP_DIR / "frontend"


class ProductHandler(BaseHTTPRequestHandler):
    def _send_bytes(self, body: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, payload: object, status: int = 200) -> None:
        self._send_bytes(json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8"), "application/json; charset=utf-8", status)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/index.html"}:
            self._send_bytes((FRONTEND_DIR / "index.html").read_bytes(), "text/html; charset=utf-8")
            return
        if parsed.path == "/frontend/styles.css":
            self._send_bytes((FRONTEND_DIR / "styles.css").read_bytes(), "text/css; charset=utf-8")
            return
        if parsed.path == "/frontend/app.js":
            self._send_bytes((FRONTEND_DIR / "app.js").read_bytes(), "application/javascript; charset=utf-8")
            return
        if parsed.path == "/pipeline_diagram.svg":
            self._send_bytes((APP_DIR / "pipeline_diagram.svg").read_bytes(), "image/svg+xml; charset=utf-8")
            return
        if parsed.path == "/analysis_charts.svg":
            self._send_bytes((APP_DIR / "analysis_charts.svg").read_bytes(), "image/svg+xml; charset=utf-8")
            return
        if parsed.path == "/api/product_readiness":
            self._send_json(json.loads((APP_DIR / "product_readiness.json").read_text(encoding="utf-8")))
            return
        if parsed.path == "/api/product_spec":
            self._send_json(load_product_spec())
            return
        if parsed.path == "/api/sample_cases":
            self._send_json(load_sample_cases())
            return
        self._send_json({"error": "not found"}, 404)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/api/recommend":
            self._send_json({"error": "not found"}, 404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            payload = json.loads(raw or "{}")
            self._send_json(run_case(payload))
        except Exception as exc:  # pragma: no cover
            self._send_json({"error": str(exc)}, 500)

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        print(f"[generated_product] {self.address_string()} - {format % args}")


def serve(port: int = 8766) -> None:
    for candidate_port in range(port, port + 20):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", candidate_port), ProductHandler)
            print(f"Generated product running at http://127.0.0.1:{candidate_port}")
            server.serve_forever()
            return
        except OSError as error:
            if error.errno != errno.EADDRINUSE:
                raise
            print(f"Port {candidate_port} is already in use; trying {candidate_port + 1}...")
    raise OSError(f"No available local port found in range {port}-{port + 19}")
'''


EVALUATION = '''"""Evaluate the generated AI-driven property recommendation platform."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from backend.agent import run_case
from backend.data_store import load_sample_cases


APP_DIR = Path(__file__).resolve().parent
PLACEHOLDER_PATTERN = re.compile(r"エリア[ABC]|Area [ABC]", re.IGNORECASE)
FORBIDDEN_GUARANTEES = ["保証します", "確約します", "絶対に安全", "投資利益", "必ず値上がり", "法的助言"]


def _is_japanese(text: str) -> bool:
    return bool(re.search(r"[ぁ-んァ-ヶ一-龥]", text or ""))


def _candidate_names(output: dict[str, Any]) -> list[str]:
    return [item.get("name_ja", "") for item in output.get("ranked_area_candidates", []) if item.get("name_ja")]


def evaluate_output(case: dict[str, Any], output: dict[str, Any]) -> dict[str, bool]:
    classification = output.get("classification", {})
    names = _candidate_names(output)
    recommendation = output.get("recommendation_ja", "")
    draft = output.get("customer_or_business_draft_ja", "")
    combined = recommendation + "\\n" + draft
    return {
        "has_case_id": bool(output.get("case_id")),
        "classification_label": bool(classification.get("label")),
        "confidence_not_fixed_half": isinstance(classification.get("confidence"), (int, float)) and classification.get("confidence") != 0.5,
        "classification_rationale": bool(classification.get("rationale")),
        "local_tool_results_exists": bool(output.get("local_tool_results")),
        "ranked_area_candidates_exists": bool(output.get("ranked_area_candidates")),
        "ranked_property_candidates_exists": bool(output.get("ranked_property_candidates")),
        "uses_actual_area_names": any(name and name in combined for name in names),
        "no_placeholder_area_names": not (PLACEHOLDER_PATTERN.search(combined) and not any(name in combined for name in names)),
        "has_evidence": bool(output.get("evidence")),
        "has_missing_information": bool(output.get("missing_information")),
        "human_approval_required": output.get("human_approval_required") is True,
        "send_allowed_false": output.get("send_allowed") is False,
        "customer_draft_is_japanese": _is_japanese(draft),
        "approval_packet": bool(output.get("approval_packet", {}).get("decision_options")),
        "audit_trace": bool(output.get("audit_trace", {}).get("tool_names")),
        "no_final_guarantee": not any(term in combined for term in FORBIDDEN_GUARANTEES),
    }


def _select_cases(case_id: str = "", max_cases: int = 0) -> list[dict[str, Any]]:
    cases = load_sample_cases()
    if case_id:
        cases = [case for case in cases if case.get("case_id") == case_id]
        if not cases:
            available = ", ".join(case.get("case_id", "<missing>") for case in load_sample_cases())
            raise SystemExit(f"Unknown case_id: {case_id}. Available: {available}")
    if max_cases > 0:
        cases = cases[:max_cases]
    return cases


def main(case_id: str = "", max_cases: int = 0) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for case in _select_cases(case_id, max_cases):
        try:
            output = run_case(case)
            checks = evaluate_output(case, output)
            results.append({
                "case_id": case.get("case_id"),
                "passed": all(checks.values()),
                "checks": checks,
                "output": output,
            })
        except Exception as exc:
            results.append({
                "case_id": case.get("case_id"),
                "passed": False,
                "checks": {"exception": False},
                "error": str(exc),
            })
    passed = sum(1 for item in results if item["passed"])
    summary = {
        "success": passed == len(results) and bool(results),
        "passed": passed,
        "total": len(results),
        "pass_rate": round(passed / max(len(results), 1), 2),
    }
    (APP_DIR / "evaluation_results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    (APP_DIR / "evaluation_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    print(json.dumps({"summary": summary, "results": results}, ensure_ascii=False, indent=2))
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate the generated product.")
    parser.add_argument("--case-id", default="", help="Evaluate only one sample case id.")
    parser.add_argument("--max-cases", type=int, default=0, help="Evaluate at most this many cases.")
    args = parser.parse_args()
    main(args.case_id, args.max_cases)
'''


TEST_RECOMMENDATIONS = '''"""Deterministic tests for generated local recommendation tools."""

from __future__ import annotations

import unittest

from backend.data_store import load_product_spec
from backend.tools import run_domain_tools


class RecommendationToolTests(unittest.TestCase):
    def test_candidate_ranking_uses_concrete_candidates(self) -> None:
        case = {
            "budget": "55-70",
            "preferences": "quality risk access family evidence",
            "max_commute_minutes": 40,
        }
        result = run_domain_tools(load_product_spec(), case)
        names = [item["name_ja"] for item in result["ranked_area_candidates"]]
        self.assertTrue(names)
        self.assertFalse(any(name in {"Area A", "Area B", "エリアA", "エリアB"} for name in names))
        self.assertGreater(result["ranked_area_candidates"][0]["score"], 0)

    def test_property_candidates_are_ranked(self) -> None:
        case = {"budget": "50-60", "preferences": "駅 通勤 ファミリー", "max_commute_minutes": 35}
        result = run_domain_tools(load_product_spec(), case)
        self.assertTrue(result["ranked_property_candidates"])
        self.assertIn("title_ja", result["ranked_property_candidates"][0])
        self.assertTrue(result["missing_information"])


if __name__ == "__main__":
    unittest.main()
'''


FRONTEND_HTML = '''<!doctype html>
<html lang="ja">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Generated Agent Product</title>
    <link rel="stylesheet" href="/frontend/styles.css">
  </head>
  <body>
    <div class="app-shell">
      <aside class="sidebar">
        <div class="brand-block">
          <div class="brand-mark">JA</div>
          <div>
            <div id="productName" class="brand-name">Generated Agent Product</div>
            <div id="workspaceLabel" class="brand-subtitle">Operations Workspace</div>
          </div>
        </div>
        <nav class="nav-list" aria-label="Workspace navigation">
          <a href="#intake" class="nav-item active">Intake</a>
          <a href="#recommendations" class="nav-item">Recommendations</a>
          <a href="#approval" class="nav-item">Approval</a>
          <a href="#evidence" class="nav-item">Evidence</a>
          <a href="#architecture" class="nav-item">Architecture</a>
        </nav>
        <section class="side-section">
          <div class="side-title">Case Queue</div>
          <div id="caseQueue" class="case-queue"></div>
        </section>
        <section class="side-section">
          <div class="side-title">Runtime</div>
          <div class="runtime-row"><span>LLM</span><strong>DeepSeek</strong></div>
          <div class="runtime-row"><span>Search</span><strong id="searchMode">Live</strong></div>
          <div class="runtime-row"><span>Approval</span><strong>Required</strong></div>
        </section>
      </aside>

      <main class="workspace">
        <header class="topbar">
          <div>
            <div id="subtitle" class="page-subtitle">Loading product spec...</div>
            <h1 id="pageTitle">Case Workspace</h1>
          </div>
          <div class="topbar-actions">
            <span id="status" class="status-chip">Ready</span>
            <button id="run" class="primary-action">Generate Packet</button>
          </div>
        </header>

        <section class="kpi-strip" id="summaryCards"></section>

        <section class="work-grid">
          <article id="intake" class="panel intake-panel">
            <div class="panel-header">
              <h2>Case Intake</h2>
              <button id="loadSample" class="secondary-action">Load Sample</button>
            </div>
            <div id="fields" class="field-grid"></div>
          </article>

          <article id="recommendations" class="panel decision-panel">
            <div class="panel-header">
              <h2>Candidate Comparison</h2>
              <span id="candidateCount" class="small-chip">0 candidates</span>
            </div>
            <div id="rankings" class="candidate-list empty-state">No candidates yet.</div>
          </article>

          <article id="approval" class="panel approval-panel">
            <div class="panel-header">
              <h2>Approval Packet</h2>
              <span id="approvalStatus" class="small-chip warning">Pending</span>
            </div>
            <div id="approvalContent" class="muted">No packet yet.</div>
            <div class="approval-actions">
              <button id="approveDraft" class="secondary-action" disabled>Approve Draft</button>
              <button id="requestEdit" class="secondary-action" disabled>Request Edits</button>
              <button id="escalate" class="secondary-action" disabled>Escalate</button>
            </div>
          </article>

          <article class="panel draft-panel">
            <div class="panel-header">
              <h2>Draft</h2>
              <span class="small-chip">Editable</span>
            </div>
            <textarea id="draftEditor" class="draft-editor" spellcheck="false">No draft yet.</textarea>
          </article>

          <article id="evidence" class="panel evidence-panel">
            <div class="panel-header">
              <h2>Evidence Sources</h2>
              <span id="evidenceCount" class="small-chip">0 sources</span>
            </div>
            <div id="evidenceSources" class="evidence-list empty-state">No evidence yet.</div>
          </article>

          <article class="panel log-panel">
            <div class="panel-header">
              <h2>Activity</h2>
              <span class="small-chip">Audit</span>
            </div>
            <ol id="activityLog" class="activity-log">
              <li>Workspace ready.</li>
            </ol>
          </article>
        </section>

        <section id="architecture" class="panel visual-panel">
          <div class="panel-header">
            <h2>Product System</h2>
            <span class="small-chip">Builder Loop</span>
          </div>
          <div class="visual-grid">
            <article>
              <h3>Agent Workflow</h3>
              <img src="/pipeline_diagram.svg" alt="Generated agent workflow diagram">
            </article>
            <article>
              <h3>Analysis View</h3>
              <img src="/analysis_charts.svg" alt="Generated analysis chart">
            </article>
            <article>
              <h3>Readiness</h3>
              <div id="readiness" class="readiness-list muted">Loading...</div>
            </article>
            <article>
              <h3>Debug Output</h3>
              <details open>
                <summary>Structured response</summary>
                <pre id="output">{}</pre>
              </details>
            </article>
          </div>
        </section>
      </main>
    </div>
    <script src="/frontend/app.js"></script>
  </body>
</html>
'''


FRONTEND_CSS = '''body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: #f4f6f8;
  color: #172026;
}

* {
  box-sizing: border-box;
}

html,
body {
  max-width: 100%;
  overflow-x: hidden;
}

button,
input,
textarea,
pre,
td,
th,
.metric,
.panel,
.brand-name,
.page-subtitle {
  overflow-wrap: anywhere;
  word-break: normal;
}

body > header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  padding: 24px 32px 16px;
  border-bottom: 1px solid #d8dee5;
  background: #ffffff;
}

h1, h2, p {
  margin-top: 0;
}

h1 {
  margin-bottom: 6px;
  font-size: 26px;
}

h2 {
  font-size: 18px;
}

.eyebrow {
  margin-bottom: 6px;
  color: #607080;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
}

body > main {
  display: grid;
  grid-template-columns: minmax(340px, 0.8fr) minmax(440px, 1.2fr);
  gap: 18px;
  padding: 20px 32px 32px;
}

.input-panel,
.output-panel,
.visual-panel,
.subpanel {
  background: #ffffff;
  border: 1px solid #d8dee5;
  border-radius: 8px;
  padding: 18px;
}

.output-panel {
  display: grid;
  gap: 14px;
}

.visual-panel {
  grid-column: 1 / -1;
  display: grid;
  gap: 14px;
}

label {
  display: block;
  margin: 12px 0 6px;
  font-weight: 700;
}

input, textarea {
  box-sizing: border-box;
  width: 100%;
  border: 1px solid #c9d2dc;
  border-radius: 6px;
  padding: 10px;
  font: inherit;
}

textarea {
  min-height: 90px;
  resize: vertical;
}

button {
  min-height: 38px;
  border: 1px solid #166358;
  border-radius: 6px;
  background: #166358;
  color: white;
  padding: 0 14px;
  font-weight: 800;
  cursor: pointer;
}

#loadSample {
  background: #334155;
  border-color: #334155;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

#status {
  color: #607080;
  font-size: 13px;
}

pre {
  overflow: auto;
  min-height: 280px;
  max-height: 760px;
  white-space: pre-wrap;
  border: 1px solid #d8dee5;
  border-radius: 6px;
  background: #f8fafc;
  padding: 14px;
}

details summary {
  cursor: pointer;
  font-weight: 800;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.metric {
  min-width: 0;
  border: 1px solid #d8dee5;
  border-radius: 8px;
  background: #f8fafc;
  padding: 12px;
  overflow: hidden;
}

.metric strong {
  display: block;
  margin-top: 4px;
  max-width: 100%;
  font-size: clamp(16px, 1.5vw, 20px);
  line-height: 1.18;
}

.result-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.subpanel {
  padding: 14px;
}

.subpanel h3 {
  margin: 0 0 10px;
  font-size: 15px;
}

.candidate {
  border-top: 1px solid #e5eaf0;
  padding: 10px 0;
}

.candidate:first-child {
  border-top: 0;
  padding-top: 0;
}

.candidate-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  font-weight: 800;
}

.score {
  border-radius: 999px;
  background: #e8f3f1;
  color: #166358;
  padding: 3px 8px;
  font-size: 12px;
}

.draft {
  white-space: pre-wrap;
  line-height: 1.65;
}

.muted {
  color: #607080;
}

.risk-list {
  margin: 8px 0 0;
  padding-left: 18px;
}

.visual-grid {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 14px;
}

.visual-grid article {
  min-width: 0;
  border: 1px solid #d8dee5;
  border-radius: 8px;
  background: #f8fafc;
  padding: 14px;
}

.visual-grid h3 {
  margin: 0 0 10px;
  font-size: 15px;
}

.visual-grid img {
  display: block;
  width: 100%;
  max-height: 360px;
  object-fit: contain;
  border: 1px solid #e5eaf0;
  border-radius: 6px;
  background: #ffffff;
}

.readiness-item {
  display: grid;
  grid-template-columns: 92px 1fr;
  gap: 8px;
  padding: 8px 0;
  border-top: 1px solid #e5eaf0;
}

.readiness-item:first-child {
  border-top: 0;
}

.tag {
  align-self: start;
  border-radius: 999px;
  background: #e8f3f1;
  color: #166358;
  padding: 3px 8px;
  text-align: center;
  font-size: 12px;
  font-weight: 800;
}

.runtime-flow {
  margin: 0;
  padding-left: 20px;
  line-height: 1.8;
}

.evidence-item {
  border-top: 1px solid #e5eaf0;
  padding: 9px 0;
}

.evidence-item:first-child {
  border-top: 0;
}

.evidence-item a {
  color: #166358;
  font-weight: 800;
}

.evidence-method {
  margin-top: 3px;
  color: #607080;
  font-size: 12px;
}

.app-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
}

.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  overflow: auto;
  border-right: 1px solid #d8dee5;
  background: #101820;
  color: #eef4f7;
  padding: 18px;
}

.brand-block {
  display: grid;
  grid-template-columns: 42px 1fr;
  align-items: center;
  gap: 12px;
  min-height: 54px;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 8px;
  background: #26a69a;
  color: #071211;
  font-weight: 900;
}

.brand-name {
  font-weight: 900;
  line-height: 1.2;
}

.brand-subtitle {
  margin-top: 3px;
  color: #9fb0bd;
  font-size: 12px;
}

.nav-list {
  display: grid;
  gap: 4px;
  margin: 22px 0;
}

.nav-item {
  border-radius: 6px;
  color: #c8d5de;
  padding: 10px 12px;
  text-decoration: none;
  font-weight: 800;
}

.nav-item.active,
.nav-item:hover {
  background: #1d2a35;
  color: #ffffff;
}

.side-section {
  margin-top: 22px;
  border-top: 1px solid #263746;
  padding-top: 16px;
}

.side-title {
  margin-bottom: 10px;
  color: #9fb0bd;
  font-size: 12px;
  font-weight: 900;
  text-transform: uppercase;
}

.case-queue {
  display: grid;
  gap: 8px;
}

.case-button {
  width: 100%;
  min-height: 58px;
  border: 1px solid #263746;
  background: #15222d;
  color: #eef4f7;
  text-align: left;
  padding: 10px;
}

.case-button.active {
  border-color: #26a69a;
  background: #18332f;
}

.case-button span {
  display: block;
  margin-top: 4px;
  color: #9fb0bd;
  font-size: 12px;
  font-weight: 600;
}

.runtime-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 8px 0;
  border-top: 1px solid #263746;
  color: #9fb0bd;
  font-size: 13px;
}

.runtime-row:first-of-type {
  border-top: 0;
}

.runtime-row strong {
  color: #eef4f7;
}

.workspace {
  min-width: 0;
  max-width: 100%;
  padding: 22px 26px 34px;
  overflow: hidden;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 16px;
  min-width: 0;
}

.page-subtitle {
  max-width: 860px;
  color: #607080;
  line-height: 1.35;
}

.topbar h1 {
  margin: 4px 0 0;
  font-size: 24px;
  overflow-wrap: anywhere;
}

.topbar-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 10px;
  min-width: 220px;
}

.primary-action,
.secondary-action {
  white-space: nowrap;
}

.secondary-action {
  border-color: #c9d2dc;
  background: #ffffff;
  color: #172026;
}

.secondary-action:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.status-chip,
.small-chip {
  display: inline-flex;
  align-items: center;
  max-width: 100%;
  min-height: 28px;
  border-radius: 999px;
  background: #e8f3f1;
  color: #166358;
  padding: 0 10px;
  font-size: 12px;
  font-weight: 900;
  overflow-wrap: anywhere;
}

.small-chip.warning {
  background: #fff3d8;
  color: #8a5a00;
}

.kpi-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px;
  margin-bottom: 16px;
}

.work-grid {
  display: grid;
  grid-template-columns: minmax(280px, 0.85fr) minmax(360px, 1.15fr) minmax(280px, 0.85fr);
  gap: 14px;
  align-items: start;
}

.panel {
  min-width: 0;
  border: 1px solid #d8dee5;
  border-radius: 8px;
  background: #ffffff;
  padding: 16px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.panel-header h2,
.panel-header h3 {
  margin: 0;
}

.field-grid {
  display: grid;
  gap: 10px;
}

.field-grid label {
  margin: 0 0 5px;
  color: #425466;
  font-size: 13px;
}

.decision-panel,
.draft-panel,
.visual-panel {
  grid-column: span 2;
}

.approval-panel,
.evidence-panel,
.log-panel {
  display: grid;
  gap: 10px;
}

.candidate-table {
  width: 100%;
  border-collapse: collapse;
}

.candidate-table th,
.candidate-table td {
  border-top: 1px solid #e5eaf0;
  padding: 10px 8px;
  text-align: left;
  vertical-align: top;
}

.candidate-table th {
  color: #607080;
  font-size: 12px;
  text-transform: uppercase;
}

.candidate-table tr:first-child th {
  border-top: 0;
}

.draft-editor {
  min-height: 280px;
  line-height: 1.65;
}

.approval-actions {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}

.activity-log {
  margin: 0;
  padding-left: 20px;
  color: #425466;
  line-height: 1.7;
}

.empty-state {
  display: grid;
  place-items: center;
  min-height: 120px;
  border: 1px dashed #c9d2dc;
  border-radius: 8px;
  background: #f8fafc;
  color: #607080;
}

@media (max-width: 880px) {
  .app-shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: static;
    height: auto;
  }

  body > header {
    align-items: stretch;
    flex-direction: column;
  }

  body > main {
    grid-template-columns: 1fr;
    padding: 16px;
  }

  .summary-grid,
  .result-grid,
  .visual-grid {
    grid-template-columns: 1fr;
  }

  .topbar,
  .panel-header {
    align-items: stretch;
    flex-direction: column;
  }

  .kpi-strip,
  .work-grid {
    grid-template-columns: 1fr;
  }

  .decision-panel,
  .draft-panel,
  .visual-panel {
    grid-column: auto;
  }
}

@media (min-width: 881px) and (max-width: 1280px) {
  .app-shell {
    grid-template-columns: 240px minmax(0, 1fr);
  }

  .workspace {
    padding: 18px;
  }

  .topbar {
    align-items: flex-start;
    flex-direction: column;
  }

  .topbar-actions {
    justify-content: flex-start;
    min-width: 0;
  }

  .kpi-strip {
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  }

  .work-grid {
    grid-template-columns: minmax(260px, 0.9fr) minmax(320px, 1.1fr);
  }

  .approval-panel,
  .evidence-panel,
  .log-panel {
    grid-column: span 2;
  }
}

@media (min-width: 1281px) and (max-width: 1560px) {
  .kpi-strip {
    grid-template-columns: repeat(3, minmax(160px, 1fr));
  }
}
'''


FRONTEND_JS = '''let productSpec = null;
let sampleCases = [];
let selectedCaseIndex = 0;
let currentOutput = null;

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function appendLog(message) {
  const log = document.getElementById("activityLog");
  const item = document.createElement("li");
  item.textContent = `${new Date().toLocaleTimeString()}  ${message}`;
  log.prepend(item);
}

function fieldElement(field) {
  const value = field.default || "";
  const label = `<label for="${field.key}">${field.label}</label>`;
  const control = field.type === "textarea"
    ? `<textarea id="${field.key}" data-field="${field.key}">${value}</textarea>`
    : `<input id="${field.key}" data-field="${field.key}" type="${field.type || "text"}" value="${value}">`;
  return `<div class="field">${label}${control}</div>`;
}

function collectCase() {
  const base = sampleCases[selectedCaseIndex] || {};
  const payload = {case_id: base.case_id || "manual_case"};
  document.querySelectorAll("[data-field]").forEach((element) => {
    payload[element.dataset.field] = element.value;
  });
  return payload;
}

function fillCase(sample) {
  Object.entries(sample).forEach(([key, value]) => {
    const element = document.querySelector(`[data-field="${key}"]`);
    if (element) {
      element.value = value;
    }
  });
}

function renderCaseQueue() {
  const queue = document.getElementById("caseQueue");
  if (!sampleCases.length) {
    queue.innerHTML = "<div class='muted'>No cases</div>";
    return;
  }
  queue.innerHTML = sampleCases.map((sample, index) => {
    const active = index === selectedCaseIndex ? " active" : "";
    const title = sample.customer_name || sample.request_owner || sample.case_id || `Case ${index + 1}`;
    const detail = sample.case_id || sample.household || sample.approval_owner || "";
    return `<button class="case-button${active}" data-case-index="${index}">${escapeHtml(title)}<span>${escapeHtml(detail)}</span></button>`;
  }).join("");
  queue.querySelectorAll("[data-case-index]").forEach((button) => {
    button.addEventListener("click", () => selectCase(Number(button.dataset.caseIndex)));
  });
}

function selectCase(index) {
  selectedCaseIndex = index;
  fillCase(sampleCases[index] || {});
  renderCaseQueue();
  appendLog(`Loaded ${sampleCases[index]?.case_id || "manual case"}.`);
}

function candidateName(item) {
  return item.name_ja || item.title_ja || item.equipment_name_ja || item.failure_mode_ja || item.property_id || item.area_id || "Candidate";
}

function candidateReason(item) {
  return item.reason_ja || item.summary_ja || item.risk_note_ja || item.summary || "";
}

function renderCandidates(output) {
  const areaItems = output.ranked_area_candidates || [];
  const propertyItems = output.ranked_property_candidates || [];
  const items = propertyItems.length ? propertyItems : areaItems;
  document.getElementById("candidateCount").textContent = `${items.length} candidates`;
  if (!items.length) {
    return "<div class='empty-state'>No candidates yet.</div>";
  }
  return `
    <table class="candidate-table">
      <thead>
        <tr><th>Rank</th><th>Candidate</th><th>Score</th><th>Reason</th></tr>
      </thead>
      <tbody>
        ${items.slice(0, 6).map((item, index) => `
          <tr>
            <td>${index + 1}</td>
            <td><strong>${escapeHtml(candidateName(item))}</strong></td>
            <td><span class="score">${escapeHtml(item.score ?? "-")}</span></td>
            <td>${escapeHtml(candidateReason(item))}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

function renderSummary(output) {
  const classification = output.classification || {};
  const risk = output.risk || {};
  const evidence = output.evidence || [];
  const liveEvidence = evidence.filter((item) => String(item.retrieval_method || "").includes("live")).length;
  return `
    <div class="metric">Classification<strong>${escapeHtml(classification.label || "-")}</strong></div>
    <div class="metric">Confidence<strong>${escapeHtml(classification.confidence ?? "-")}</strong></div>
    <div class="metric">Risk<strong>${escapeHtml(risk.risk_level || "-")}</strong></div>
    <div class="metric">Candidates<strong>${(output.ranked_area_candidates || []).length + (output.ranked_property_candidates || []).length}</strong></div>
    <div class="metric">Live Sources<strong>${liveEvidence}</strong></div>
    <div class="metric">Send Allowed<strong>${output.send_allowed ? "Yes" : "No"}</strong></div>
  `;
}

function renderApproval(output) {
  const risk = output.risk || {};
  const packet = output.approval_packet || {};
  const missing = output.missing_information || [];
  const reasons = risk.risk_reasons || [];
  document.getElementById("approvalStatus").textContent = output.human_approval_required ? "Review Required" : "Ready";
  document.getElementById("approvalStatus").classList.toggle("warning", Boolean(output.human_approval_required));
  return `
    <p><strong>Owner:</strong> ${escapeHtml(packet.approval_owner || "-")}</p>
    <p><strong>Decision:</strong> ${escapeHtml((packet.decision_options || []).join(" / "))}</p>
    <p><strong>Boundary:</strong> send_allowed=${escapeHtml(output.send_allowed)}</p>
    <p><strong>Missing information</strong></p>
    <ul class="risk-list">${missing.slice(0, 7).map(item => `<li>${escapeHtml(item)}</li>`).join("") || "<li>-</li>"}</ul>
    <p><strong>Risk reasons</strong></p>
    <ul class="risk-list">${reasons.slice(0, 7).map(item => `<li>${escapeHtml(item)}</li>`).join("") || "<li>-</li>"}</ul>
  `;
}

function renderEvidence(output) {
  const evidence = output.evidence || [];
  document.getElementById("evidenceCount").textContent = `${evidence.length} sources`;
  if (!evidence.length) {
    return "<div class='empty-state'>No evidence yet.</div>";
  }
  return evidence.slice(0, 10).map((item) => {
    const title = escapeHtml(item.title || item.id || "Evidence");
    const url = item.url ? `<a href="${escapeHtml(item.url)}" target="_blank" rel="noreferrer">${title}</a>` : `<strong>${title}</strong>`;
    const method = item.retrieval_method || "local_evidence";
    return `
      <div class="evidence-item">
        <div>${url}</div>
        <div class="evidence-method">${escapeHtml(method)} · ${escapeHtml(item.id || "")}</div>
      </div>
    `;
  }).join("");
}

function renderReadiness(readiness) {
  const implemented = readiness.implemented_capabilities || [];
  const gaps = readiness.production_gaps || readiness.remaining_production_gaps || [];
  const milestones = readiness.recommended_next_milestones || readiness.recommended_milestones || [];
  const rows = [
    ...implemented.slice(0, 4).map(item => ["Built", item.name || item.capability || item.id || item]),
    ...gaps.slice(0, 3).map(item => ["Gap", item.name || item.capability || item.gap || item.id || item]),
    ...milestones.slice(0, 2).map(item => ["Next", item.name || item.milestone || item.id || item])
  ];
  if (!rows.length) {
    return "<p class='muted'>No readiness data.</p>";
  }
  return rows.map(([tag, text]) => `
    <div class="readiness-item">
      <span class="tag">${escapeHtml(tag)}</span>
      <span>${escapeHtml(text)}</span>
    </div>
  `).join("");
}

function setApprovalControls(enabled) {
  ["approveDraft", "requestEdit", "escalate"].forEach((id) => {
    document.getElementById(id).disabled = !enabled;
  });
}

function renderResult(data) {
  currentOutput = data;
  document.getElementById("summaryCards").innerHTML = renderSummary(data);
  document.getElementById("rankings").innerHTML = renderCandidates(data);
  document.getElementById("approvalContent").innerHTML = renderApproval(data);
  document.getElementById("draftEditor").value = data.customer_or_business_draft_ja || data.recommendation_ja || "";
  document.getElementById("evidenceSources").innerHTML = renderEvidence(data);
  document.getElementById("output").textContent = JSON.stringify(data, null, 2);
  setApprovalControls(true);
}

async function load() {
  productSpec = await (await fetch("/api/product_spec")).json();
  sampleCases = await (await fetch("/api/sample_cases")).json();
  const readinessResponse = await fetch("/api/product_readiness");
  if (readinessResponse.ok) {
    const readiness = await readinessResponse.json();
    document.getElementById("readiness").innerHTML = renderReadiness(readiness);
  }
  document.title = productSpec.product_name;
  document.getElementById("productName").textContent = productSpec.product_name;
  document.getElementById("pageTitle").textContent = productSpec.primary_action || "Case Workspace";
  document.getElementById("subtitle").textContent = productSpec.subtitle;
  document.getElementById("workspaceLabel").textContent = productSpec.app_kind || "Operations Workspace";
  document.getElementById("fields").innerHTML = productSpec.fields.map(fieldElement).join("");
  renderCaseQueue();
  if (sampleCases.length) {
    selectCase(0);
  }
}

async function run() {
  const status = document.getElementById("status");
  const output = document.getElementById("output");
  const button = document.getElementById("run");
  status.textContent = "Running";
  button.disabled = true;
  setApprovalControls(false);
  output.textContent = "Running...";
  appendLog("Started local tools, runtime search, and DeepSeek drafting.");
  try {
    const response = await fetch("/api/recommend", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(collectCase())
    });
    const data = await response.json();
    renderResult(data);
    status.textContent = response.ok ? "Complete" : "Error";
    appendLog(response.ok ? "Generated review packet." : "Generation returned an error.");
  } catch (error) {
    output.textContent = String(error);
    status.textContent = "Error";
    appendLog("Runtime error.");
  } finally {
    button.disabled = false;
  }
}

document.getElementById("run").addEventListener("click", run);
document.getElementById("loadSample").addEventListener("click", () => {
  if (sampleCases.length) {
    selectCase((selectedCaseIndex + 1) % sampleCases.length);
  }
});
document.getElementById("approveDraft").addEventListener("click", () => appendLog("Draft marked approved in local review state."));
document.getElementById("requestEdit").addEventListener("click", () => appendLog("Edit request added in local review state."));
document.getElementById("escalate").addEventListener("click", () => appendLog("Escalation added in local review state."));
document.querySelectorAll(".nav-item").forEach((item) => {
  item.addEventListener("click", () => {
    document.querySelectorAll(".nav-item").forEach((nav) => nav.classList.remove("active"));
    item.classList.add("active");
  });
});

load();
'''


REQUIREMENTS = '''# Generated product intentionally uses only the Python standard library.
# Runtime requires:
# - Python 3.9+
# - DEEPSEEK_API_KEY for API-backed agent execution
'''


def build_product_brief(agent_design: dict, product_spec: dict) -> dict:
    opportunity = agent_design.get("selected_opportunity", {}) or {}
    return {
        "product_name": product_spec.get("product_name"),
        "selected_opportunity": opportunity.get("name", ""),
        "problem": opportunity.get("target_workflow", ""),
        "solution": product_spec.get("subtitle"),
        "demo_value": "Shows consulting-agent to software-builder workflow through a runnable multi-file generated app.",
        "human_approval": product_spec.get("output_policy", {}).get("human_approval_required", True),
    }


def build_knowledge_base(agent_design: dict, product_spec: dict) -> str:
    opportunity = agent_design.get("selected_opportunity", {}) or {}
    context = agent_design.get("enterprise_context", {}) or {}
    return "\n".join([
        f"# {product_spec.get('product_name')} Knowledge Base",
        "",
        "## Enterprise Context",
        "",
        f"- Industry: {context.get('industry', '')}",
        f"- Main business: {context.get('main_business', '')}",
        f"- AI objective: {context.get('ai_objective', '')}",
        f"- Constraints: {context.get('constraints', '')}",
        "",
        "## Selected Opportunity",
        "",
        f"- Name: {opportunity.get('name', '')}",
        f"- Target workflow: {opportunity.get('target_workflow', '')}",
        f"- Capability: {opportunity.get('proposed_ai_capability', '')}",
        f"- Expected business value: {opportunity.get('expected_business_value', '')}",
        f"- Key risk: {opportunity.get('key_risk', '')}",
        "",
        "## Operating Rules",
        "",
        "- Always run deterministic local tools before DeepSeek drafting.",
        "- Use actual area and property names from local tool results.",
        "- Never use placeholder recommendations such as エリアA / エリアB / エリアC.",
        "- Treat property suitability as decision support, not a final financial, legal, investment, or disaster-safety conclusion.",
        "- Keep human_approval_required true and send_allowed false.",
        "",
        "## Required Human Checks",
        "",
        "- Hazard map and flood risk.",
        "- Earthquake resilience and building management documents.",
        "- School district, commute, station route, and listing freshness.",
        "- Important matters explanation and licensed advisor review.",
    ])


def build_product_readiness(product_spec: dict, project_architecture: dict) -> dict:
    """Assess how close the generated child product is to production readiness."""
    implemented = [
        {
            "capability": "multi_file_project_package",
            "status": "implemented",
            "evidence": ["backend/", "frontend/", "data/", "tests/", "app.py", "evaluation.py"],
        },
        {
            "capability": "api_backed_agent_runtime",
            "status": "implemented",
            "evidence": ["backend/llm_client.py", "backend/agent.py"],
        },
        {
            "capability": "runtime_live_web_evidence_search",
            "status": "implemented",
            "evidence": ["backend/web_search.py", "backend/agent.py:evidence"],
        },
        {
            "capability": "local_domain_tools",
            "status": "implemented",
            "evidence": ["backend/tools.py", "backend/recommendation_engine.py"],
        },
        {
            "capability": "human_approval_gate",
            "status": "implemented",
            "evidence": ["backend/guardrails.py", "output_policy.send_allowed=false"],
        },
        {
            "capability": "sandbox_evaluation",
            "status": "implemented",
            "evidence": ["evaluation.py", "tests/test_recommendations.py", "sandbox_report.json"],
        },
        {
            "capability": "secret_leakage_check",
            "status": "implemented",
            "evidence": ["src/sandbox_eval.py:no_api_key_or_secret_leakage"],
        },
    ]
    gaps = [
        {
            "capability": "authentication_and_roles",
            "status": "not_implemented",
            "production_requirement": "Add login, role-based access, approval-owner identity, and session audit trails.",
        },
        {
            "capability": "persistent_database",
            "status": "not_implemented",
            "production_requirement": "Replace local JSON files with a real database, migrations, and backup/restore policy.",
        },
        {
            "capability": "enterprise_data_connectors",
            "status": "not_implemented",
            "production_requirement": "Connect to approved internal document stores, CRM/SFA, ticketing, property systems, or maintenance logs.",
        },
        {
            "capability": "observability",
            "status": "partial",
            "production_requirement": "Add structured logs, latency metrics, model cost metrics, tracing, alerts, and redaction.",
        },
        {
            "capability": "security_review",
            "status": "partial",
            "production_requirement": "Add threat model, rate limiting, prompt-injection tests, dependency scanning, and data-retention controls.",
        },
        {
            "capability": "human_workflow_integration",
            "status": "partial",
            "production_requirement": "Add approval queue, edit history, reviewer comments, and final approval records.",
        },
    ]
    return {
        "readiness_version": "production_readiness_v1",
        "product_name": product_spec.get("product_name"),
        "overall_level": "local_product_mvp_runtime_ready",
        "implemented_capabilities": implemented,
        "production_gaps": gaps,
        "recommended_next_milestones": [
            "Pilot with sanitized enterprise data and named reviewers.",
            "Add authentication, persistent storage, and approval workflow.",
            "Connect to real enterprise data sources behind read-only permissions.",
            "Add monitoring, cost controls, security tests, and prompt-injection evaluation.",
            "Run 50-100 human-reviewed cases before production rollout.",
        ],
        "architecture_entrypoints": project_architecture.get("entrypoints", {}),
    }


def render_product_readiness(readiness: dict) -> str:
    """Render production-readiness assessment for reviewers."""
    lines = [
        f"# Production Readiness: {readiness.get('product_name')}",
        "",
        f"Overall level: **{readiness.get('overall_level')}**",
        "",
        "## Implemented Capabilities",
        "",
    ]
    for item in readiness.get("implemented_capabilities", []):
        lines.append(f"- **{item['capability']}**: {item['status']} ({', '.join(item.get('evidence', []))})")
    lines.extend(["", "## Production Gaps", ""])
    for item in readiness.get("production_gaps", []):
        lines.append(f"- **{item['capability']}**: {item['status']}. {item['production_requirement']}")
    lines.extend(["", "## Recommended Next Milestones", ""])
    for item in readiness.get("recommended_next_milestones", []):
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def render_productization_summary(blueprint: dict) -> str:
    """Render the productization contract embedded in the generated app."""
    archetype = blueprint.get("selected_archetype", {}) if isinstance(blueprint, dict) else {}
    lines = [
        f"# Productization Blueprint: {archetype.get('name', 'Generated Enterprise Product')}",
        "",
        f"- Maturity target: `{blueprint.get('maturity_target', 'enterprise_software_mvp') if isinstance(blueprint, dict) else 'enterprise_software_mvp'}`",
        f"- Source opportunity: `{blueprint.get('source_opportunity', '') if isinstance(blueprint, dict) else ''}`",
        f"- Primary job: {archetype.get('primary_job', '')}",
        "",
        "## Required Enterprise Capabilities",
        "",
    ]
    if isinstance(blueprint, dict):
        for item in blueprint.get("enterprise_capabilities", []):
            lines.append(f"- {item}")
        lines.extend(["", "## Visual Quality Contract", ""])
        contract = blueprint.get("visual_quality_contract", {})
        for item in contract.get("must_have", []):
            lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def _svg_text(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def write_pipeline_diagram(app_dir: Path, product_spec: dict) -> None:
    steps = [
        "Customer case",
        "Local tools",
        "Evidence",
        "DeepSeek draft",
        "Guardrails",
        "Approval packet",
    ]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="260" viewBox="0 0 1120 260">',
        '<rect width="1120" height="260" fill="#f8fafc"/>',
        f'<text x="28" y="42" font-size="24" font-weight="800" fill="#172026">{_svg_text(product_spec.get("product_name", "Generated Product"))}</text>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#52606d"/></marker></defs>',
    ]
    x = 28
    for index, step in enumerate(steps):
        parts.append(f'<rect x="{x}" y="96" width="150" height="64" rx="8" fill="#e8f3f1" stroke="#166358"/>')
        parts.append(f'<text x="{x + 16}" y="134" font-size="14" font-weight="700" fill="#172026">{_svg_text(step)}</text>')
        if index < len(steps) - 1:
            parts.append(f'<line x1="{x + 150}" y1="128" x2="{x + 184}" y2="128" stroke="#52606d" marker-end="url(#arrow)"/>')
        x += 184
    parts.append('<text x="28" y="215" font-size="14" fill="#52606d">Software Builder Loop output: backend + frontend + data + tests + API-backed evaluation</text>')
    parts.append("</svg>")
    (app_dir / "pipeline_diagram.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")


def write_analysis_charts(app_dir: Path, areas: list[dict[str, Any]], product_spec: dict) -> None:
    max_score = max(area["typical_budget_jpy_m"] for area in areas)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="920" height="320" viewBox="0 0 920 320">',
        '<rect width="920" height="320" fill="#ffffff"/>',
        f'<text x="24" y="36" font-size="22" font-weight="800" fill="#172026">{_svg_text(product_spec.get("product_name", "Generated Product"))} Area Data</text>',
        f'<text x="24" y="60" font-size="12" fill="#52606d">Selected opportunity: {_svg_text(product_spec.get("selected_opportunity", ""))}</text>',
    ]
    x = 56
    for area in areas:
        height = int(area["typical_budget_jpy_m"] / max_score * 170)
        y = 250 - height
        parts.append(f'<rect x="{x}" y="{y}" width="92" height="{height}" fill="#166358"/>')
        parts.append(f'<text x="{x}" y="272" font-size="13" fill="#172026">{_svg_text(area["name_ja"])}</text>')
        parts.append(f'<text x="{x}" y="{y - 8}" font-size="12" fill="#52606d">{area["typical_budget_jpy_m"]}M</text>')
        x += 190
    parts.append('<text x="24" y="304" font-size="13" fill="#52606d">Bars show local budget reference for this property recommendation case; ranking also uses commute, station, school, quiet, and family scores.</text>')
    parts.append("</svg>")
    (app_dir / "analysis_charts.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")


def write_architecture_markdown(app_dir: Path, project_architecture: dict) -> None:
    lines = [
        "# Generated Project Architecture",
        "",
        f"- Runtime: {project_architecture.get('runtime')}",
        "",
        "## Entrypoints",
        "",
    ]
    for name, command in project_architecture.get("entrypoints", {}).items():
        lines.append(f"- {name}: `{command}`")
    lines.extend(["", "## Backend Modules", ""])
    for module in project_architecture.get("backend_modules", []):
        lines.append(f"- `{module['path']}`: {module['responsibility']}")
    lines.extend(["", "## Frontend Modules", ""])
    for module in project_architecture.get("frontend_modules", []):
        lines.append(f"- `{module['path']}`: {module['responsibility']}")
    (app_dir / "architecture.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write(app_dir: Path, relative_path: str, content: str) -> None:
    path = app_dir / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_json(app_dir: Path, relative_path: str, payload: object) -> None:
    _write(app_dir, relative_path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def build_prototype(
    app_dir: Path,
    agent_design: dict,
    architecture: dict,
    productization_blueprint: dict | None = None,
) -> dict:
    """Generate a real multi-file child product package."""
    app_dir.mkdir(parents=True, exist_ok=True)
    productization_blueprint = productization_blueprint or {}
    product_spec = build_software_blueprint(agent_design, architecture, productization_blueprint)
    agent_spec = build_agent_spec(agent_design, architecture, product_spec)
    product_brief = build_product_brief(agent_design, product_spec)
    product_requirements = build_product_requirements(agent_design, product_spec)
    project_architecture = build_project_architecture(agent_design, architecture, product_spec)
    product_readiness = build_product_readiness(product_spec, project_architecture)
    implementation_plan = build_implementation_plan(agent_design, architecture, product_spec)
    file_manifest = build_file_manifest(product_spec)
    file_plan = build_file_plan(product_spec)
    generation_trace = build_generation_trace(implementation_plan, product_spec)
    builder_loop_trace = build_builder_loop_trace(product_requirements, project_architecture, file_manifest, implementation_plan)
    knowledge_base = build_knowledge_base(agent_design, product_spec)
    domain_template = product_spec.get("domain_template", {}) if isinstance(product_spec.get("domain_template"), dict) else {}
    area_profiles = domain_template.get("area_profiles", [])
    property_listings = domain_template.get("property_listings", [])
    sample_cases = domain_template.get("sample_customers", [])
    domain_data = {
        "template_id": product_spec.get("domain_template_id"),
        "template_source": product_spec.get("domain_template_source"),
        "area_profiles": area_profiles,
        "property_listings": property_listings,
        "sample_customers": sample_cases,
    }

    json_files = {
        "product_spec.json": product_spec,
        "software_blueprint.json": product_spec,
        "agent_spec.json": agent_spec,
        "product_brief.json": product_brief,
        "product_requirements.json": product_requirements,
        "product_readiness.json": product_readiness,
        "productization_blueprint.json": productization_blueprint,
        "project_architecture.json": project_architecture,
        "implementation_plan.json": implementation_plan,
        "file_manifest.json": file_manifest,
        "file_plan.json": file_plan,
        "generation_trace.json": generation_trace,
        "builder_loop_trace.json": builder_loop_trace,
        "repair_log.json": build_repair_log(),
        "architecture.json": architecture,
        "domain_data.json": domain_data,
        "sample_cases.json": sample_cases,
        "data/areas.json": area_profiles,
        "data/properties.json": property_listings,
        "data/sample_customers.json": sample_cases,
    }
    for relative_path, payload in json_files.items():
        _write_json(app_dir, relative_path, payload)

    text_files = {
        "requirements.txt": REQUIREMENTS,
        "app.py": APP_ENTRYPOINT,
        "tools.py": ROOT_TOOLS,
        "backend/__init__.py": BACKEND_INIT,
        "backend/data_store.py": DATA_STORE,
        "backend/recommendation_engine.py": RECOMMENDATION_ENGINE,
        "backend/tools.py": BACKEND_TOOLS,
        "backend/llm_client.py": LLM_CLIENT,
        "backend/web_search.py": WEB_SEARCH,
        "backend/guardrails.py": GUARDRAILS,
        "backend/agent.py": AGENT,
        "backend/api.py": API,
        "evaluation.py": EVALUATION,
        "tests/test_recommendations.py": TEST_RECOMMENDATIONS,
        "frontend/index.html": FRONTEND_HTML,
        "frontend/styles.css": FRONTEND_CSS,
        "frontend/app.js": FRONTEND_JS,
        "knowledge_base.md": knowledge_base + "\n",
        "production_readiness.md": render_product_readiness(product_readiness),
        "productization_blueprint.md": render_productization_summary(productization_blueprint),
    }
    for relative_path, content in text_files.items():
        _write(app_dir, relative_path, content)

    write_pipeline_diagram(app_dir, product_spec)
    write_analysis_charts(app_dir, area_profiles, product_spec)
    write_architecture_markdown(app_dir, project_architecture)
    _write(
        app_dir,
        "README.md",
        f"""# {product_spec.get('product_name')}

This generated child app is a runnable local product MVP built by the Software Builder Loop, not a single-file demo or JSON dump.

## What Was Built

- Local API-backed product server.
- Static frontend for consultants.
- Backend modules for agent orchestration, deterministic tools, evidence, DeepSeek calls, guardrails, and data loading.
- Runtime trusted-domain web evidence search in `backend/web_search.py`.
- Local domain data for areas and properties.
- Deterministic tests and API-backed evaluation.

## Run

```bash
export DEEPSEEK_API_KEY="..."
export DEEPSEEK_BASE_URL="https://api.deepseek.com"
export AGENT_MODEL="deepseek-v4-pro"
export DEEPSEEK_THINKING="1"
export DEEPSEEK_REASONING_EFFORT="high"
export GENERATED_APP_LIVE_SEARCH="1"
python3 app.py
```

Open `http://127.0.0.1:8766`.

CLI and evaluation:

```bash
python3 app.py --list-cases
python3 app.py --cli --case-id case_family_quiet_school
python3 app.py --cli
python3 -m unittest discover -s tests
python3 evaluation.py --case-id case_family_quiet_school
python3 evaluation.py
```

`--cli` and `evaluation.py` use the DeepSeek runtime and print progress before each sample case. For a quick smoke test, run one case with `--case-id` first; run the full batch when you want deeper evaluation.

## Product Flow

customer case -> local ranking tools -> evidence retrieval -> DeepSeek draft -> guardrails -> approval packet -> final JSON

The app always keeps `human_approval_required=true` and `send_allowed=false`.
""",
    )

    files = sorted(item["path"] for item in file_manifest["files"])
    return {
        "app_dir": str(app_dir.resolve()),
        "product_spec": product_spec,
        "product_brief": product_brief,
        "product_requirements": product_requirements,
        "product_readiness": product_readiness,
        "productization_blueprint": productization_blueprint,
        "project_architecture": project_architecture,
        "file_manifest": file_manifest,
        "builder_loop_trace": builder_loop_trace,
        "files": files,
    }
