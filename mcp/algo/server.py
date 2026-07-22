"""
sint-algo-mcp server (fastmcp).

Unified tools over multiple knowledge sources with a local hybrid cache.
Sources: rosetta, github, papers, patents, docs, docs-tools.

Run:  fastmcp run server.py
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

from config import CACHE_DIR, SOURCES, OPTIONAL_SOURCES, ERA_MIN, ERA_MAX
from index import Index

mcp = FastMCP("sint-algo-mcp")

# import source modules lazily so a single broken source never kills the server
import sources.rosetta as rosetta
import sources.papers as papers
import sources.patents as patents
import sources.github as github
import sources.docs as docs


def _ix() -> Index:
    """Fresh connection per call (MCP may run handlers in a threadpool)."""
    return Index()


@mcp.tool()
def search_algorithm(query: str, source: str = "", era_min: int = 0,
                     era_max: int = 9999, limit: int = 30) -> str:
    """Search the unified index for algorithms / ideas / docs.

    Args:
        query: name or keyword (e.g. "quick sort", "ray casting").
        source: filter by source (rosetta|github|papers|patents|docs|docs-tools|user).
        era_min, era_max: year range filter (use 1950-1990 for forgotten ideas).
        limit: max results.
    Returns: JSON list of matching records (name, source, kind, era, langs, summary, ref).
    """
    ix = _ix()
    rows = ix.search(query, source=source, era_min=era_min, era_max=era_max, limit=limit)
    ix.close()
    return json.dumps(rows, ensure_ascii=False, indent=1)


@mcp.tool()
def get_implementations(name: str, lang: str = "") -> str:
    """Get code implementations for a Rosetta Code task.

    Args:
        name: exact or partial task name (e.g. "Quick sort").
        lang: optional language filter (e.g. "Python", "C").
    Returns: JSON {task, ref, implementations: {lang: code}} (code truncated to 4k chars each).
    """
    ix = _ix()
    rows = ix.search(name, source="rosetta", limit=5)
    if not rows:
        return json.dumps({"error": "not in index; run ingest_rosetta first"}, ensure_ascii=False)
    best = rows[0]
    impls_file = best.get("extra", {}).get("impls_file") or best.get("cached_path")
    if not impls_file or not Path(impls_file).exists():
        return json.dumps({"error": "body not cached"}, ensure_ascii=False)
    impls = json.loads(Path(impls_file).read_text())
    if lang:
        impls = {k: v for k, v in impls.items() if lang.lower() in k.lower()}
    # truncate long bodies
    out = {k: (v[:4000] + ("\n...[truncated]" if len(v) > 4000 else "")) for k, v in impls.items()}
    ix.close()
    return json.dumps({"task": best["name"], "ref": best["ref"],
                       "implementations": out}, ensure_ascii=False, indent=1)


@mcp.tool()
def get_paper(query: str, era_min: int = ERA_MIN, era_max: int = ERA_MAX,
              limit: int = 10) -> str:
    """Search academic papers (arXiv/Semantic Scholar) with era filter.

    Use era_min=1950, era_max=1990 to surface forgotten ideas.
    Returns JSON list of {title, year, authors, abstract, url, source}.
    """
    ix = _ix()
    results = papers.search(query, era_min=era_min, era_max=era_max, limit=limit)
    # cache into index
    for r in results:
        ix.upsert(name=r.get("title", query), source="papers", kind="paper",
                  era=r.get("year"), summary=r.get("abstract", "")[:300],
                  ref=r.get("url", ""), extra=r)
    ix.close()
    return json.dumps(results, ensure_ascii=False, indent=1)


@mcp.tool()
def get_patent(query: str, limit: int = 10) -> str:
    """Search patents (PatentsView / Google Patents) for commercial & historical ideas.

    Returns JSON list of {title, patent_id, year, abstract, url, assignee}.
    """
    ix = _ix()
    results = patents.search(query, limit=limit)
    for r in results:
        ix.upsert(name=r.get("title", query), source="patents", kind="patent",
                  era=r.get("year"), summary=r.get("abstract", "")[:300],
                  ref=r.get("url", ""), extra=r)
    ix.close()
    return json.dumps(results, ensure_ascii=False, indent=1)


@mcp.tool()
def describe_middleware(query: str, source: str = "docs") -> str:
    """Fetch a description of how a library / middleware / tool works.

    source: 'docs' (general libs/middleware) or 'docs-tools' (Android, PS Vita,
    Ghidra, Linux, etc.). Returns distilled markdown description + source URL.
    """
    ix = _ix()
    result = docs.describe(query, source=source)
    if result:
        ix.upsert(name=query, source=source, kind="doc",
                  summary=result.get("summary", "")[:300],
                  ref=result.get("url", ""), extra=result)
    ix.close()
    return json.dumps(result, ensure_ascii=False, indent=1)


@mcp.tool()
def ingest(source: str, limit: int = 50, query: str = "", index_only: bool = False) -> str:
    """Grow the local base at runtime.

    source: rosetta|github|papers|patents|docs|docs-tools.
    For papers/patents a query is recommended. Returns count ingested.
    """
    ix = _ix()
    n = 0
    if source == "rosetta":
        n = rosetta.ingest(ix, limit=limit, index_only=index_only)
    elif source == "github":
        n = github.ingest(ix, query=query, limit=limit)
    elif source == "papers":
        n = papers.ingest(ix, query=query, limit=limit, era_min=ERA_MIN, era_max=ERA_MAX)
    elif source == "patents":
        n = patents.ingest(ix, query=query, limit=limit)
    elif source in ("docs", "docs-tools"):
        n = docs.ingest(ix, query=query, source=source, limit=limit)
    else:
        ix.close()
        return json.dumps({"error": f"unknown source '{source}'"}, ensure_ascii=False)
    stats = ix.stats()
    ix.close()
    return json.dumps({"ingested": n, "stats": stats}, ensure_ascii=False)


@mcp.tool()
def add_note(name: str, note: str, refs: Optional[list[str]] = None,
             kind: str = "note") -> str:
    """Add a user/agent note or found solution to the base (persists across sessions)."""
    ix = _ix()
    eid = ix.add_user_note(name=name, note=note, refs=refs, kind=kind)
    ix.close()
    return json.dumps({"id": eid, "status": "ok"}, ensure_ascii=False)


@mcp.tool()
def stats() -> str:
    """Show how many records per source are cached."""
    ix = _ix()
    st = ix.stats()
    ix.close()
    return json.dumps({"cache_dir": str(CACHE_DIR), "stats": st,
                       "sources": SOURCES, "optional": OPTIONAL_SOURCES},
                      ensure_ascii=False, indent=1)


if __name__ == "__main__":
    mcp.run(transport="stdio")
