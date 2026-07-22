"""
GitHub source module — reference code index.

Uses the public GitHub API (no auth; rate-limited) to locate algorithm
implementations across popular repos (TheAlgorithms/* and general search).
Stores repo/code references in the index; bodies are lazy-fetched.
"""
from __future__ import annotations

import time
from typing import Optional

import httpx

from config import USER_AGENT, REQUEST_TIMEOUT, CACHE_DIR

CACHE_SUB = CACHE_DIR / "github"
CACHE_SUB.mkdir(exist_ok=True)
GH_API = "https://api.github.com"


def _client() -> httpx.Client:
    return httpx.Client(headers={"User-Agent": USER_AGENT,
                                "Accept": "application/vnd.github+json"},
                        timeout=REQUEST_TIMEOUT, follow_redirects=True,
                        transport=httpx.HTTPTransport(retries=3))


def search_repos(query: str, limit: int = 20) -> list[dict]:
    out: list[dict] = []
    with _client() as c:
        try:
            r = c.get(f"{GH_API}/search/repositories",
                      params={"q": f"{query} algorithm in:name,description,topics",
                              "sort": "stars", "order": "desc", "per_page": limit})
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            return [{"error": str(e)}]
    for repo in data.get("items", []):
        out.append({
            "name": repo["full_name"],
            "stars": repo.get("stargazers_count", 0),
            "language": repo.get("language", ""),
            "description": repo.get("description", ""),
            "url": repo.get("html_url", ""),
            "clone": repo.get("clone_url", ""),
        })
    return out


def ingest(ix, query: str = "algorithm", limit: int = 20) -> int:
    repos = search_repos(query, limit=limit)
    n = 0
    for r in repos:
        if "error" in r:
            continue
        ix.upsert(name=r["name"], source="github", kind="algorithm",
                  summary=r.get("description", "")[:300],
                  ref=r.get("url", ""),
                  extra={"stars": r.get("stars"), "language": r.get("language"),
                         "clone": r.get("clone")})
        n += 1
    return n


if __name__ == "__main__":
    import json
    from index import Index
    ix = Index()
    res = search_repos("sorting", limit=5)
    print(json.dumps(res, ensure_ascii=False, indent=1)[:1200])
    ix.close()
