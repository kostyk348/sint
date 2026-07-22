"""
Patents source module — commercial & historical ideas via Google Patents (free, no key).

Uses the unofficial XHR endpoint. Good for "forgotten commercial ideas" back to
the 1950s; filter by priority/publication year client-side.
"""
from __future__ import annotations

import time
from typing import Optional

import httpx

from config import USER_AGENT, REQUEST_TIMEOUT, CACHE_DIR

CACHE_SUB = CACHE_DIR / "patents"
CACHE_SUB.mkdir(exist_ok=True)
GP_XHR = "https://patents.google.com/xhr/query"


def _client() -> httpx.Client:
    return httpx.Client(headers={"User-Agent": USER_AGENT},
                        timeout=REQUEST_TIMEOUT, follow_redirects=True,
                        transport=httpx.HTTPTransport(retries=3))


def _year_of(patent: dict) -> Optional[int]:
    for k in ("priority_date", "publication_date", "filing_date"):
        v = patent.get(k)
        if v:
            try:
                return int(str(v)[:4])
            except Exception:
                pass
    return None


def search(query: str, limit: int = 10, year_min: int = 0,
           year_max: int = 9999) -> list[dict]:
    out: list[dict] = []
    with _client() as c:
        q = f"q={query}&num={min(limit * 3, 100)}"
        if year_min:
            q += f"&lr={year_min}0101-{year_max}1231"
        data = None
        last_err = None
        for attempt in range(4):
            try:
                r = c.get(f"{GP_XHR}?url={q}")
                r.raise_for_status()
                data = r.json()
                break
            except Exception as e:
                last_err = str(e)
                time.sleep(1.5 * (attempt + 1))
        if data is None:
            return [{"error": last_err or "no response"}]
    cluster = data.get("results", {}).get("cluster", [])
    if not cluster:
        return out
    for item in cluster[0].get("result", []):
        pat = item.get("patent", {})
        year = _year_of(pat) or 0
        if year and not (year_min <= year <= year_max):
            continue
        pub = pat.get("publication_number", "")
        out.append({
            "title": (pat.get("title") or "").strip(),
            "patent_id": pub,
            "year": year,
            "assignee": pat.get("assignee", "") or "unknown",
            "inventor": pat.get("inventor", ""),
            "abstract": (pat.get("snippet") or "").replace("<b>", "").replace("</b>", "")[:1000],
            "url": f"https://patents.google.com/patent/{pub}/en" if pub else "",
            "source": "google_patents",
        })
        if len(out) >= limit:
            break
    return out


def ingest(ix, query: str = "data compression", limit: int = 20,
           year_min: int = 1950, year_max: int = 1990) -> int:
    results = search(query, limit=limit, year_min=year_min, year_max=year_max)
    n = 0
    for r in results:
        if "error" in r:
            continue
        ix.upsert(name=r.get("title", query), source="patents", kind="patent",
                  era=r.get("year"), summary=(r.get("abstract") or "")[:300],
                  ref=r.get("url", ""), extra=r)
        n += 1
    return n


if __name__ == "__main__":
    import json
    from index import Index
    ix = Index()
    res = search("hashing", limit=3, year_min=1970, year_max=1990)
    print(json.dumps(res, ensure_ascii=False, indent=1)[:1500])
    ix.close()
