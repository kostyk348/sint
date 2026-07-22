"""
Papers source module — academic works via Semantic Scholar (free, no key).

Era filter surfaces "forgotten ideas" from 1950-1990.
"""
from __future__ import annotations

import time
from typing import Optional

import httpx

from config import USER_AGENT, REQUEST_TIMEOUT, CACHE_DIR
import re

CACHE_SUB = CACHE_DIR / "papers"
CACHE_SUB.mkdir(exist_ok=True)
S2_API = "https://api.semanticscholar.org/graph/v1/paper/search"
ARXIV_API = "http://export.arxiv.org/api/query"


def _client() -> httpx.Client:
    return httpx.Client(headers={"User-Agent": USER_AGENT},
                        timeout=REQUEST_TIMEOUT, follow_redirects=True,
                        transport=httpx.HTTPTransport(retries=3))


def _search_arxiv(query: str, era_min: int, era_max: int, limit: int) -> list[dict]:
    """arXiv is free, no key, good historical coverage (cs.prehistory via old IDs)."""
    out: list[dict] = []
    with _client() as c:
        try:
            r = c.get(ARXIV_API, params={
                "search_query": f'all:"{query}"',
                "start": 0, "max_results": min(limit * 3, 100),
                "sortBy": "relevance",
            })
            r.raise_for_status()
            raw = r.text
        except Exception as e:
            return [{"error": str(e)}]
    # minimal XML parse (no lxml dependency)
    import re
    entries = re.findall(r"<entry>(.*?)</entry>", raw, re.S)
    for e in entries:
        def g(tag):
            m = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", e, re.S)
            return m.group(1).strip() if m else ""
        title = re.sub(r"\s+", " ", g("title"))
        summary = re.sub(r"\s+", " ", g("summary"))
        published = g("published")[:4]
        try:
            year = int(published)
        except Exception:
            year = 0
        if year and not (era_min <= year <= era_max):
            continue
        authors = ", ".join(re.findall(r"<name>(.*?)</name>", e))
        link = ""
        m = re.search(r'<id>(.*?)</id>', e)
        if m:
            link = m.group(1)
        out.append({
            "title": title, "year": year, "authors": authors,
            "abstract": summary[:1000], "url": link, "venue": "arXiv",
            "source": "arxiv",
        })
        if len(out) >= limit:
            break
    return out


def search(query: str, era_min: int = 1950, era_max: int = 1990,
           limit: int = 10) -> list[dict]:
    # Primary: arXiv (free, no key). Fallback: Semantic Scholar if empty.
    out = _search_arxiv(query, era_min, era_max, limit)
    if out and "error" not in out[0]:
        return out[:limit]
    # fallback to S2
    out2: list[dict] = []
    with _client() as c:
        params = {
            "query": query,
            "limit": min(limit, 100),
            "fields": "title,year,authors,abstract,url,venue,publicationDate",
        }
        try:
            r = c.get(S2_API, params=params)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            return [{"error": str(e)}]
    for p in data.get("data", []):
        year = p.get("year") or 0
        if year and not (era_min <= year <= era_max):
            continue
        authors = ", ".join((a.get("name", "") for a in p.get("authors", [])[:4]))
        out2.append({
            "title": p.get("title", ""),
            "year": year,
            "authors": authors,
            "abstract": (p.get("abstract") or "")[:1000],
            "url": p.get("url") or (f"https://www.semanticscholar.org/paper/{p.get('paperId','')}" if p.get('paperId') else ""),
            "venue": p.get("venue", ""),
            "source": "semanticscholar",
        })
    return out2[:limit]


def ingest(ix, query: str = "algorithm", limit: int = 20,
           era_min: int = 1950, era_max: int = 1990) -> int:
    results = search(query, era_min=era_min, era_max=era_max, limit=limit)
    n = 0
    for r in results:
        if "error" in r:
            continue
        ix.upsert(name=r.get("title", query), source="papers", kind="paper",
                  era=r.get("year"), summary=(r.get("abstract") or "")[:300],
                  ref=r.get("url", ""), extra=r)
        n += 1
    return n


if __name__ == "__main__":
    import json
    from index import Index
    ix = Index()
    res = search("sorting network", era_min=1960, era_max=1990, limit=5)
    print(json.dumps(res, ensure_ascii=False, indent=1)[:1500])
    ix.close()
