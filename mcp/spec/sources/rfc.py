"""RFC source module — IETF protocol specifications.

Search via IETF datatracker API (free); full text via rfc-editor.org.
"""
from __future__ import annotations

import re
import time
from pathlib import Path

import httpx

from config import CACHE_DIR, USER_AGENT, REQUEST_TIMEOUT

CACHE_SUB = CACHE_DIR / "rfc"
CACHE_SUB.mkdir(exist_ok=True)
DT_API = "https://datatracker.ietf.org/api/v1/doc/document/"
RFC_TEXT = "https://www.rfc-editor.org/rfc/rfc{num}.txt"


def _client() -> httpx.Client:
    return httpx.Client(headers={"User-Agent": USER_AGENT},
                        timeout=REQUEST_TIMEOUT, follow_redirects=True,
                        transport=httpx.HTTPTransport(retries=3))


def search(query: str, limit: int = 10) -> list[dict]:
    out: list[dict] = []
    with _client() as c:
        try:
            r = c.get(DT_API, params={"format": "json",
                                      "title__icontains": query,
                                      "limit": limit, "ordering": "-time"})
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            return [{"error": str(e)}]
    for d in data.get("objects", []):
        rfcno = d.get("rfc") or ""
        out.append({
            "rfc": rfcno,
            "name": d.get("name", ""),
            "title": d.get("title", ""),
            "year": int(d.get("time", "0000")[:4]) if d.get("time") else None,
            "url": f"https://www.rfc-editor.org/rfc/rfc{rfcno}.txt" if rfcno else "",
            "abstract": (d.get("abstract") or "")[:400],
        })
    return out[:limit]


def get_text(num: int) -> dict:
    cache_file = CACHE_SUB / f"rfc{num}.txt"
    if cache_file.exists():
        text = cache_file.read_text(encoding="utf-8", errors="replace")
    else:
        with _client() as c:
            try:
                r = c.get(RFC_TEXT.format(num=num))
                r.raise_for_status()
                text = r.text
                cache_file.write_text(text, encoding="utf-8")
            except Exception as e:
                return {"error": str(e), "rfc": num}
    # extract title + first meaningful lines (skip leading blank/header noise)
    lines = [ln.rstrip() for ln in text.splitlines()]
    title = ""
    for ln in lines[:40]:
        if ln.strip():
            title = ln.strip()
            break
    return {"rfc": num, "title": title, "chars": len(text),
            "cached_path": str(cache_file),
            "head": "\n".join(lines[:60])}


def ingest(ix, query: str = "transport", limit: int = 10) -> int:
    res = search(query, limit=limit)
    n = 0
    for r in res:
        if "error" in r or not r.get("rfc"):
            continue
        ix.upsert(name=f"RFC {r.get('rfc')}: {r.get('title','')}", source="rfc",
                  kind="spec", era=r.get("year"),
                  summary=(r.get("abstract") or "")[:300],
                  ref=r.get("url", ""), extra=r)
        n += 1
    return n


if __name__ == "__main__":
    import json
    from index import Index
    ix = Index()
    print(json.dumps(search("TLS", limit=3), ensure_ascii=False, indent=1)[:900])
    ix.close()
