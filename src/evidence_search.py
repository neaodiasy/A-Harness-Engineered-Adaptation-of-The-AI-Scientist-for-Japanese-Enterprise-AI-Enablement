"""Evidence pack generation for Japanese enterprise AI enablement.

The v1 project used a curated evidence library only. This branch keeps those
high-trust sources, but can also run a live web evidence layer when
`ENABLE_LIVE_SEARCH=1` is set. The downstream schema stays the same:
`evidence_pack["evidence_items"]` is a ranked list of evidence objects.
"""

from __future__ import annotations

import html
import os
import re
import ssl
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from urllib.error import URLError

from src.domain_templates import select_domain_template

try:
    import certifi
except Exception:  # pragma: no cover
    certifi = None


def _ssl_context() -> ssl.SSLContext:
    if certifi is not None:
        return ssl.create_default_context(cafile=certifi.where())
    return ssl.create_default_context()


EVIDENCE_LIBRARY: tuple[dict, ...] = (
    {
        "id": "evidence_oecd_ai_labour_japan_2025",
        "title": "OECD: Artificial Intelligence and the Labour Market in Japan",
        "url": "https://www.oecd.org/en/publications/artificial-intelligence-and-the-labour-market-in-japan_b825563e-en/full-report.html",
        "source_type": "policy_report",
        "themes": ("labor_shortage", "productivity", "skills", "sme", "workplace_ai"),
        "industry_terms": ("general", "manufacturing", "finance", "insurance", "services"),
        "summary": (
            "Japan faces labour and skills shortages, while AI adoption in workplaces remains comparatively low. "
            "The report frames AI as a way to improve productivity, job quality, and access to work when introduced safely."
        ),
        "supports": ("opportunity_generation", "business_value", "japan_fit"),
    },
    {
        "id": "evidence_meti_genai_dx_skills_2024",
        "title": "METI: Human Resources and Skills Required for DX Promotion in the Age of Generative AI",
        "url": "https://www.meti.go.jp/english/press/2024/0628_003.html",
        "source_type": "government_report",
        "themes": ("generative_ai", "dx", "skills", "productivity", "transformation"),
        "industry_terms": ("general", "manufacturing", "distribution", "services", "retail"),
        "summary": (
            "METI positions generative AI as a business opportunity for productivity, added value, and social issue solving, "
            "while emphasizing the human skills needed to use AI appropriately and proactively."
        ),
        "supports": ("ai_literacy", "roadmap", "change_management"),
    },
    {
        "id": "evidence_fsa_ai_discussion_2025",
        "title": "FSA: AI Discussion Paper for the Financial Sector",
        "url": "https://www.fsa.go.jp/en/news/2025/20250304/aidp.html",
        "source_type": "regulatory_discussion",
        "themes": ("financial_services", "risk_management", "governance", "customer_convenience", "operational_efficiency"),
        "industry_terms": ("finance", "bank", "insurance", "securities", "regulated"),
        "summary": (
            "Japan's FSA discusses sound AI use in financial institutions, balancing operational efficiency and customer convenience "
            "against misuse, misinformation, and emerging risk concerns."
        ),
        "supports": ("risk_check", "human_approval", "compliance"),
    },
    {
        "id": "evidence_ipa_dx_all_employee_enablement",
        "title": "IPA DX SQUARE: Enterprise DX and all-employee digital skill development examples",
        "url": "https://dx.ipa.go.jp/",
        "source_type": "dx_case_collection",
        "themes": ("dx", "data_utilization", "all_employee_enablement", "kaizen", "skills"),
        "industry_terms": ("general", "manufacturing", "energy", "consumer_goods", "services"),
        "summary": (
            "IPA DX case studies emphasize data utilization, human resource development, digital skill standards, and broad employee enablement."
        ),
        "supports": ("japan_fit", "kaizen", "adoption"),
    },
    {
        "id": "evidence_meti_geniac_multimodal_insurance_case",
        "title": "METI GENIAC case: multimodal LMM for insurance contract operations",
        "url": "https://www.meti.go.jp/policy/mono_info_service/geniac/geniac_magazine/usecase_02.html",
        "source_type": "industry_case",
        "themes": ("multimodal", "document_processing", "insurance", "workflow_efficiency"),
        "industry_terms": ("insurance", "finance", "document", "contract", "regulated"),
        "summary": (
            "A METI GENIAC case highlights multimodal large model development to improve insurance contract operation efficiency."
        ),
        "supports": ("document_processing", "prototype_scope", "multimodal"),
    },
)

TRUSTED_DOMAINS = (
    "meti.go.jp",
    "ipa.go.jp",
    "digital.go.jp",
    "fsa.go.jp",
    "boj.or.jp",
    "mhlw.go.jp",
    "mlit.go.jp",
    "gsi.go.jp",
    "cao.go.jp",
    "jpc-net.jp",
    "oecd.org",
)

LIVE_SEARCH_TOPICS = (
    "Japan generative AI enterprise productivity",
    "Japan DX AI workforce productivity",
    "Japan AI governance human approval enterprise",
)


def _profile_blob(profile: dict) -> str:
    return " ".join(str(value) for value in profile.values()).lower()


def _profile_terms(profile: dict) -> list[str]:
    blob = " ".join(str(value) for value in profile.values())
    terms: list[str] = []
    for candidate in (
        profile.get("industry"),
        profile.get("main_business"),
        profile.get("ai_objective"),
        profile.get("business_goal"),
    ):
        if candidate:
            terms.append(str(candidate)[:120])
    if any(term in blob.lower() for term in ("manufacturing", "factory", "maintenance", "engineer", "製造", "工場", "保守")):
        terms.append("Japan manufacturing AI maintenance knowledge retrieval")
    domain_pack = select_domain_template(profile)
    if domain_pack:
        terms.extend(str(query) for query in domain_pack.get("live_search_queries", [])[:2])
    if any(term in blob.lower() for term in ("finance", "bank", "insurance", "金融", "銀行", "保険")):
        terms.append("Japan financial sector AI governance customer service")
    return terms[:4]


def _score_evidence(item: dict, blob: str) -> float:
    score = 0.0
    for term in item["themes"] + item["industry_terms"] + item["supports"]:
        if term.lower().replace("_", " ") in blob or term.lower() in blob:
            score += 1.0
    if "japan" in blob or "japanese" in blob or "日本" in blob:
        score += 0.5
    if any(term in blob for term in ("bank", "finance", "financial", "金融", "銀行")) and "finance" in item["industry_terms"]:
        score += 2.0
    if any(term in blob for term in ("manufacturing", "factory", "製造", "工場")) and "manufacturing" in item["industry_terms"]:
        score += 1.5
    if any(term in blob for term in ("document", "contract", "pdf", "帳票", "契約")) and "document_processing" in item["themes"]:
        score += 1.5
    return round(score, 2)


def _trusted_domain(url: str) -> bool:
    host = urllib.parse.urlparse(url).netloc.lower()
    return any(host == domain or host.endswith("." + domain) for domain in TRUSTED_DOMAINS)


def _result_id(url: str, index: int) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", urllib.parse.urlparse(url).netloc.lower()).strip("_")
    return f"live_evidence_{slug or 'source'}_{index}"


def _duckduckgo_html(query: str, max_results: int = 6) -> list[dict]:
    """Query DuckDuckGo HTML using stdlib only.

    This is deliberately simple and inspectable. It avoids browser automation
    and keeps live search as an optional harness feature.
    """
    encoded = urllib.parse.urlencode({"q": query})
    request = urllib.request.Request(
        "https://duckduckgo.com/html/?" + encoded,
        headers={
            "User-Agent": "Mozilla/5.0 J-Enterprise-Agent-Scientist/0.2",
            "Accept": "text/html",
        },
    )
    with urllib.request.urlopen(request, timeout=20, context=_ssl_context()) as response:
        body = response.read().decode("utf-8", errors="replace")

    results: list[dict] = []
    pattern = re.compile(
        r'<a[^>]+class="result__a"[^>]+href="(?P<href>[^"]+)"[^>]*>(?P<title>.*?)</a>',
        flags=re.DOTALL | re.IGNORECASE,
    )
    snippets = re.findall(
        r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>|<div[^>]+class="result__snippet"[^>]*>(.*?)</div>',
        body,
        flags=re.DOTALL | re.IGNORECASE,
    )
    snippet_texts = [
        re.sub(r"\s+", " ", re.sub(r"<.*?>", "", html.unescape(a or b))).strip()
        for a, b in snippets
    ]

    for match in pattern.finditer(body):
        href = html.unescape(match.group("href"))
        parsed = urllib.parse.urlparse(href)
        if parsed.netloc.endswith("duckduckgo.com"):
            qs = urllib.parse.parse_qs(parsed.query)
            href = qs.get("uddg", [href])[0]
        title = re.sub(r"\s+", " ", re.sub(r"<.*?>", "", html.unescape(match.group("title")))).strip()
        if not title or not href.startswith("http") or not _trusted_domain(href):
            continue
        summary = snippet_texts[len(results)] if len(results) < len(snippet_texts) else title
        results.append({"title": title, "url": href, "summary": summary})
        if len(results) >= max_results:
            break
    return results


def _live_queries(profile: dict) -> list[str]:
    domain_filter = " OR ".join(f"site:{domain}" for domain in TRUSTED_DOMAINS[:7])
    queries = []
    for topic in LIVE_SEARCH_TOPICS:
        queries.append(f"{topic} {domain_filter}")
    for term in _profile_terms(profile):
        queries.append(f"{term} Japan AI DX {domain_filter}")
    return queries[: int(os.environ.get("LIVE_SEARCH_QUERY_LIMIT", "5"))]


def _build_live_evidence(profile: dict) -> tuple[list[dict], dict]:
    started = datetime.now(timezone.utc).isoformat()
    if os.environ.get("ENABLE_LIVE_SEARCH", "").lower() not in {"1", "true", "yes", "on"}:
        return [], {
            "enabled": False,
            "reason": "Set ENABLE_LIVE_SEARCH=1 to enable live trusted-domain retrieval.",
        }

    live_items: list[dict] = []
    errors: list[dict] = []
    seen_urls: set[str] = set()
    queries = _live_queries(profile)
    for query_index, query in enumerate(queries, start=1):
        try:
            results = _duckduckgo_html(query, max_results=int(os.environ.get("LIVE_SEARCH_RESULTS_PER_QUERY", "4")))
            for result in results:
                if result["url"] in seen_urls:
                    continue
                seen_urls.add(result["url"])
                live_items.append({
                    "id": _result_id(result["url"], len(live_items) + 1),
                    "title": result["title"],
                    "url": result["url"],
                    "source_type": "live_web_result",
                    "themes": ("live_search", "japan_ai", "enterprise_ai"),
                    "industry_terms": ("general",),
                    "summary": result["summary"],
                    "supports": ("live_evidence", "opportunity_generation", "japan_fit"),
                    "query": query,
                    "query_index": query_index,
                })
            time.sleep(float(os.environ.get("LIVE_SEARCH_DELAY_SECONDS", "0.2")))
        except (URLError, TimeoutError, OSError) as exc:
            errors.append({"query": query, "error": str(exc)})
    return live_items, {
        "enabled": True,
        "provider": "duckduckgo_html",
        "trusted_domains": list(TRUSTED_DOMAINS),
        "queries": queries,
        "errors": errors,
        "started_at": started,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "result_count": len(live_items),
    }


def build_evidence_pack(profile: dict, limit: int = 8) -> dict:
    """Rank curated and optional live evidence against an enterprise profile."""
    blob = _profile_blob(profile)
    ranked = []
    for item in EVIDENCE_LIBRARY:
        ranked.append({**item, "retrieval_method": "curated", "relevance_score": _score_evidence(item, blob)})
    live_items, live_metadata = _build_live_evidence(profile)
    for item in live_items:
        ranked.append({
            **item,
            "retrieval_method": "live_web_search",
            "relevance_score": _score_evidence(item, blob) + 1.5,
        })
    ranked.sort(key=lambda item: item["relevance_score"], reverse=True)
    selected = ranked[:limit]
    return {
        "method": "curated_plus_live_trusted_search_v2" if live_metadata.get("enabled") else "curated_source_retrieval_v1",
        "query_context": profile,
        "evidence_items": selected,
        "live_search": live_metadata,
        "coverage_notes": [
            "Evidence prioritizes Japan-specific AI adoption, DX, governance, labour shortage, and regulated workflow themes.",
            "When ENABLE_LIVE_SEARCH=1, the harness adds live trusted-domain search while preserving the same evidence_pack schema.",
        ],
    }
