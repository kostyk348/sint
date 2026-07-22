"""sint-spec-mcp server (fastmcp).

Tools over RFC + format specifications with local hybrid cache.
Run: fastmcp run server.py  (stdio)
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

from config import CACHE_DIR, SOURCES
from index import Index

mcp = FastMCP("sint-spec-mcp")

import sources.rfc as rfc
import sources.formats as formats


def _ix() -> Index:
    return Index()


@mcp.tool()
def search_spec(query: str, source: str = "", limit: int = 30) -> str:
    """Search the spec index (RFC titles + format names).

    Args: source: 'rfc' | 'formats' | '' (all)."""
    ix = _ix()
    rows = ix.search(query, source=source, limit=limit)
    ix.close()
    return json.dumps(rows, ensure_ascii=False, indent=1)


@mcp.tool()
def get_rfc(num: int) -> str:
    """Fetch full RFC text (cached). Returns title, head (first 60 lines), path."""
    r = rfc.get_text(num)
    ix = _ix()
    if "error" not in r:
        ix.upsert(name=f"RFC {num}", source="rfc", kind="spec",
                  summary=(r.get("title") or "")[:300],
                  ref=f"https://www.rfc-editor.org/rfc/rfc{num}.txt",
                  cached_path=r.get("cached_path", ""), extra=r)
    ix.close()
    return json.dumps(r, ensure_ascii=False, indent=1)


@mcp.tool()
def describe_format(name: str) -> str:
    """Describe a binary/container format: authoritative spec URL + Wikipedia overview."""
    r = formats.describe(name)
    ix = _ix()
    if "error" not in r:
        ix.upsert(name=f"{name.upper()} format", source="formats", kind="spec",
                  summary=(r.get("summary") or "")[:300],
                  ref=r.get("spec_url", ""), cached_path=r.get("cached_path", ""),
                  extra=r)
    ix.close()
    return json.dumps(r, ensure_ascii=False, indent=1)


@mcp.tool()
def ingest(source: str, query: str = "", limit: int = 10) -> str:
    """Grow the spec base. source: 'rfc' | 'formats'."""
    ix = _ix()
    n = 0
    if source == "rfc":
        n = rfc.ingest(ix, query=query or "transport", limit=limit)
    elif source == "formats":
        n = formats.ingest(ix, query=query, limit=limit)
    else:
        ix.close()
        return json.dumps({"error": f"unknown source '{source}'"}, ensure_ascii=False)
    st = ix.stats()
    ix.close()
    return json.dumps({"ingested": n, "stats": st}, ensure_ascii=False)


@mcp.tool()
def add_note(name: str, note: str, refs: Optional[list[str]] = None,
             kind: str = "note") -> str:
    """Add a user/agent spec note (persists across sessions)."""
    ix = _ix()
    ix.upsert(name=name, source="user", kind=kind, summary=note,
               ref=json.dumps(refs or []), extra={"refs": refs or []})
    ix.close()
    return json.dumps({"status": "ok"}, ensure_ascii=False)


@mcp.tool()
def stats() -> str:
    """Show cached spec counts per source."""
    ix = _ix()
    st = ix.stats()
    ix.close()
    return json.dumps({"cache_dir": str(CACHE_DIR), "stats": st, "sources": SOURCES},
                      ensure_ascii=False, indent=1)


if __name__ == "__main__":
    mcp.run(transport="stdio")
