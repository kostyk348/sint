"""
sint-algo-mcp — unified algorithm knowledge MCP server.

Sources (all enabled, hybrid cache):
  - rosetta   : Rosetta Code (MediaWiki API) — tasks x languages
  - github    : TheAlgorithms/* + RosettaCodeData (code)
  - papers    : arXiv / Semantic Scholar / CiteSeerX (era filter 1950-1990)
  - patents   : Google Patents (commercial / forgotten ideas)
  - docs      : middleware & library descriptions (web fetch + extract)

Cache model:
  - metadata + abstracts + code are cached locally (SQLite + files)
  - full PDFs are lazy-fetched only on explicit get_full()
"""
from __future__ import annotations

import os
from pathlib import Path

# ---- paths -------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
CACHE_DIR = ROOT / "cache"
CACHE_DIR.mkdir(exist_ok=True)
INDEX_DB = CACHE_DIR / "index.db"

# per-source cache subdirectories
for sub in ("rosetta", "github", "papers", "patents", "docs", "full"):
    (CACHE_DIR / sub).mkdir(exist_ok=True)

# ---- network -----------------------------------------------------------
USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 sint-algo-mcp/0.1")
REQUEST_TIMEOUT = 30.0

# ---- era filter (forgotten ideas) -------------------------------------
ERA_MIN = 1950
ERA_MAX = 1990

# ---- source registry ---------------------------------------------------
# Core sources (enabled at launch).
SOURCES = {
    "rosetta":    "Rosetta Code — tasks implemented across languages",
    "github":     "TheAlgorithms/* + RosettaCodeData — reference code",
    "papers":     "arXiv / Semantic Scholar / CiteSeerX — academic works",
    "patents":    "Google Patents — commercial & historical ideas",
    "docs":       "Middleware & library descriptions (general)",
    "docs-tools": "Tool/system docs: Android, PS Vita, Ghidra, Linux, etc.",
}

# Optional modules — schema is extensible, add a file + registry line to enable.
OPTIONAL_SOURCES = {
    "specs": "Protocol & file-format specifications (HTTP/TLS/USB/BLE/...)",
    "cve":   "NVD CVE / advisory metadata",
    "datasets": "Benchmark/dataset registry (from wiki skill)",
    "user":  "User-added notes, PDFs, private repos via ingest_file/add_*",
}
