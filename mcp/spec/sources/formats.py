"""Formats source module — binary/container format specifications.

Curated authoritative spec URLs + clean Wikipedia overview ("how the format works").
"""
from __future__ import annotations

import re
from pathlib import Path

import httpx

from config import CACHE_DIR, USER_AGENT, REQUEST_TIMEOUT

CACHE_SUB = CACHE_DIR / "formats"
CACHE_SUB.mkdir(exist_ok=True)

# name -> {spec: authoritative spec URL, wiki: wikipedia title}
FORMATS = {
    "elf":   {"spec": "https://refspecs.linuxbase.org/elf/elf.pdf",
               "wiki": "Executable and Linkable Format"},
    "pe":    {"spec": "https://learn.microsoft.com/en-us/windows/win32/debug/pe-format",
               "wiki": "Portable Executable"},
    "mach-o": {"spec": "https://developer.apple.com/library/archive/documentation/DeveloperTools/Conceptual/MachORuntime.pdf",
                "wiki": "Mach-O"},
    "pdf":   {"spec": "https://pdfa.org/norm-refs/PDF32000_2008.pdf",
               "wiki": "PDF"},
    "zip":   {"spec": "https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT",
               "wiki": "Zip (file format)"},
    "png":   {"spec": "https://www.w3.org/TR/png-3/", "wiki": "PNG"},
    "gif":   {"spec": "https://www.w3.org/Graphics/GIF/spec-gif89a.txt", "wiki": "GIF"},
    "jpeg":  {"spec": "https://www.w3.org/Graphics/JPEG/ITU-T81.pdf", "wiki": "JPEG"},
    "usb":   {"spec": "https://www.usb.org/document-library/usb-2_0", "wiki": "USB"},
    "ble":   {"spec": "https://www.bluetooth.com/specifications/specs/core-specification-5-4/", "wiki": "Bluetooth Low Energy"},
    "tls":   {"spec": "https://www.rfc-editor.org/rfc/rfc8446.txt", "wiki": "Transport Layer Security"},
    "http":  {"spec": "https://www.rfc-editor.org/rfc/rfc9110.txt", "wiki": "HTTP"},
    "dns":   {"spec": "https://www.rfc-editor.org/rfc/rfc1035.txt", "wiki": "Domain Name System"},
    "tcp":   {"spec": "https://www.rfc-editor.org/rfc/rfc9293.txt", "wiki": "Transmission Control Protocol"},
    "ip":    {"spec": "https://www.rfc-editor.org/rfc/rfc791.txt", "wiki": "Internet Protocol"},
    "coff":  {"spec": "https://learn.microsoft.com/en-us/windows/win32/debug/pe-format", "wiki": "COFF"},
    "wasm":  {"spec": "https://webassembly.github.io/spec/core/_download/WebAssembly.pdf", "wiki": "WebAssembly"},
}


def _client() -> httpx.Client:
    return httpx.Client(headers={"User-Agent": USER_AGENT},
                        timeout=REQUEST_TIMEOUT, follow_redirects=True,
                        transport=httpx.HTTPTransport(retries=3))


def _wiki(title: str) -> str:
    try:
        r = _client().get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}",
            headers={"Accept": "application/json"})
        if r.status_code == 200:
            return r.json().get("extract", "")
    except Exception:
        pass
    return ""


def describe(name: str) -> dict:
    key = name.lower().strip()
    info = FORMATS.get(key)
    if not info:
        # try partial match
        for k, v in FORMATS.items():
            if k in key or key in k:
                info = v
                key = k
                break
    if not info:
        return {"error": "unknown format", "known": sorted(FORMATS.keys())}
    summary = _wiki(info["wiki"])
    cache_file = CACHE_SUB / f"{key}.txt"
    cache_file.write_text(summary or "(no wiki summary)", encoding="utf-8")
    return {"format": key, "spec_url": info["spec"], "wiki": info["wiki"],
            "summary": summary[:600], "chars": len(summary),
            "cached_path": str(cache_file)}


def ingest(ix, query: str = "", limit: int = 50) -> int:
    keys = [query.lower()] if query else list(FORMATS.keys())
    n = 0
    for k in keys:
        if k not in FORMATS:
            continue
        r = describe(k)
        if "error" in r:
            continue
        ix.upsert(name=f"{k.upper()} format", source="formats", kind="spec",
                  summary=(r.get("summary") or "")[:300],
                  ref=r.get("spec_url", ""), extra=r)
        n += 1
    return n


if __name__ == "__main__":
    import json
    from index import Index
    ix = Index()
    print(json.dumps(describe("elf"), ensure_ascii=False, indent=1)[:600])
    ix.close()
