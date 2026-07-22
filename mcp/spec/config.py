"""sint-spec-mcp — protocol & file-format specification knowledge MCP.

Sources:
  - rfc    : IETF RFCs (datatracker search + rfc-editor full text)
  - formats: binary/container specs (ELF, PE, PDF, ZIP, PNG, USB, BLE...)
              via curated authoritative URLs + Wikipedia overview
Local hybrid cache (SQLite + files), extensible like sint-algo-mcp.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE_DIR = ROOT / "cache"
CACHE_DIR.mkdir(exist_ok=True)
for sub in ("rfc", "formats"):
    (CACHE_DIR / sub).mkdir(exist_ok=True)

USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 sint-spec-mcp/0.1")
REQUEST_TIMEOUT = 30.0

SOURCES = {
    "rfc": "IETF RFCs — protocol specifications",
    "formats": "Binary/container format specs (ELF, PE, PDF, ZIP, PNG, ...)",
}
