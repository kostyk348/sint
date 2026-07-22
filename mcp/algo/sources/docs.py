"""
Docs / docs-tools source module.

Fetches documentation for libraries, middleware, and tools (Android, PS Vita,
Ghidra, Linux, etc.) and extracts readable text into the cache.

For discovery without a search API key, we keep a curated map of authoritative
doc URLs per topic. The agent can also pass a direct URL via ingest.
"""
from __future__ import annotations

import html
import re
import time
from typing import Optional

import httpx

from config import USER_AGENT, REQUEST_TIMEOUT, CACHE_DIR

CACHE_SUB = CACHE_DIR / "docs"
CACHE_SUB.mkdir(exist_ok=True)

# Curated authoritative doc roots per topic (docs-tools + general middleware).
DOC_SITES = {
    # docs-tools
    "android": "https://developer.android.com/reference", "android ndk": "https://developer.android.com/ndk",
    "ps vita": "https://vitasdk.org/", "vita": "https://vitasdk.org/",
    "ghidra": "https://ghidra-sre.org/", "ghidra api": "https://ghidra.re/ghidra_docs/api/",
    "linux man": "https://man7.org/linux/man-pages/", "man7": "https://man7.org/linux/man-pages/",
    "systemd": "https://www.freedesktop.org/wiki/Software/systemd/",
    "ebpf": "https://docs.ebpf.io/", "bpf": "https://docs.ebpf.io/",
    "kernel": "https://www.kernel.org/doc/html/latest/",
    # general middleware / libs
    "redis": "https://redis.io/docs/latest/", "nginx": "https://nginx.org/en/docs/",
    "kafka": "https://kafka.apache.org/documentation/", "grpc": "https://grpc.io/docs/",
    "rabbitmq": "https://www.rabbitmq.com/documentation.html",
    "postgres": "https://www.postgresql.org/docs/current/",
    "sqlite": "https://www.sqlite.org/docs.html", "docker": "https://docs.docker.com/",
    "kubernetes": "https://kubernetes.io/docs/home/",
}

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")

_CLIENT = None


def _client() -> httpx.Client:
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = httpx.Client(headers={"User-Agent": USER_AGENT},
                               timeout=REQUEST_TIMEOUT, follow_redirects=True,
                               transport=httpx.HTTPTransport(retries=3))
    return _CLIENT


def _extract_text(raw: str) -> str:
    raw = re.sub(r"(?is)<(script|style|head|nav|footer).*?</\1>", " ", raw)
    raw = _TAG_RE.sub(" ", raw)
    raw = html.unescape(raw)
    return _WS_RE.sub(" ", raw).strip()


def _resolve_url(query: str) -> Optional[str]:
    q = query.lower().strip()
    if q.startswith("http://") or q.startswith("https://"):
        return query
    for key, url in DOC_SITES.items():
        if key in q:
            return url
    return None


def _wiki_summary(topic: str) -> Optional[dict]:
    """Clean 'how it works' description from Wikipedia REST summary API."""
    title = topic.replace(" ", "_")
    try:
        r = _client().get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}",
            headers={"Accept": "application/json"})
        if r.status_code == 200:
            d = r.json()
            extract = d.get("extract", "")
            if extract:
                return {"query": topic, "url": d.get("content_urls", {}).get("desktop", {}).get("page", ""),
                        "summary": extract[:600], "full": extract, "source": "wikipedia"}
    except Exception:
        pass
    return None


def describe(query: str, source: str = "docs-tools", url: str = "") -> dict:
    # 1) Wikipedia clean summary (best for "how it works")
    if not url:
        w = _wiki_summary(query)
        if w:
            safe = re.sub(r"[^\w\-]", "_", query)[:60]
            cache_file = CACHE_SUB / f"{source}_{safe}.txt"
            cache_file.write_text(w["full"], encoding="utf-8")
            return {"query": query, "url": w["url"], "summary": w["summary"],
                    "cached_path": str(cache_file), "chars": len(w["full"]),
                    "source": "wikipedia"}
    # 2) fallback: curated doc site fetch + strip
    target = url or _resolve_url(query)
    if not target:
        return {"error": "no curated doc site for this query; pass a direct URL",
                "known_topics": sorted(DOC_SITES.keys())}
    try:
        r = _client().get(target)
        r.raise_for_status()
        text = _extract_text(r.text)
    except Exception as e:
        return {"error": str(e), "url": target}
    summary = text[:600]
    safe = re.sub(r"[^\w\-]", "_", query)[:60]
    cache_file = CACHE_SUB / f"{source}_{safe}.txt"
    cache_file.write_text(text, encoding="utf-8")
    return {"query": query, "url": str(r.url), "summary": summary,
            "cached_path": str(cache_file), "chars": len(text),
            "source": "web"}


def ingest(ix, query: str = "", source: str = "docs-tools", limit: int = 1,
           url: str = "") -> int:
    if not query and not url:
        return 0
    res = describe(query, source=source, url=url)
    if "error" in res:
        return 0
    ix.upsert(name=query or res.get("url", ""), source=source, kind="doc",
              summary=res.get("summary", "")[:300], ref=res.get("url", ""),
              cached_path=res.get("cached_path", ""), extra=res)
    return 1


if __name__ == "__main__":
    import json
    from index import Index
    ix = Index()
    print(json.dumps(describe("ghidra"), ensure_ascii=False, indent=1)[:800])
    ix.close()
