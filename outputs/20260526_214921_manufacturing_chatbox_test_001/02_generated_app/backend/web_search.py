"""Runtime trusted-domain web evidence search for the generated product.

The generated child product uses this module directly, so the product itself can
retrieve fresh public evidence before calling the LLM. Set
GENERATED_APP_LIVE_SEARCH=0 to disable it for offline demos.
"""

from __future__ import annotations

import html
import os
import re
import ssl
import time
import urllib.parse
import urllib.request
from typing import Any

try:
    import certifi
except Exception:  # pragma: no cover
    certifi = None


def _ssl_context():
    if certifi is not None:
        return ssl.create_default_context(cafile=certifi.where())
    return ssl.create_default_context()


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
    with urllib.request.urlopen(request, timeout=timeout, context=_ssl_context()) as response:
        return response.read().decode("utf-8", errors="replace")


def _domain_allowed(url: str) -> bool:
    host = urllib.parse.urlparse(url).netloc.lower()
    return any(host == domain or host.endswith("." + domain) for domain in TRUSTED_DOMAINS)


def _extract_results(raw_html: str, limit: int) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for match in re.finditer(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', raw_html, re.I | re.S):
        href = html.unescape(match.group(1))
        title = re.sub(r"<.*?>", "", match.group(2), flags=re.S)
        title = html.unescape(re.sub(r"\s+", " ", title)).strip()
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
