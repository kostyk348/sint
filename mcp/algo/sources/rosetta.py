"""
Rosetta Code source module.

Uses the MediaWiki API to enumerate tasks and fetch implementations
grouped by language. Caches raw wikitext + parsed (lang -> code) locally.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Optional

import httpx

from config import CACHE_DIR, USER_AGENT, REQUEST_TIMEOUT
from index import Index

ROSETTA_API = "https://rosettacode.org/w/api.php"
CACHE_SUB = CACHE_DIR / "rosetta"
CACHE_SUB.mkdir(exist_ok=True)

# MediaWiki {{works with|Lang}} / =={{header|Lang}}== section splitter
HEADER_RE = re.compile(r"^==+\s*\{\{header\|([^}]+)\}\}\s*==+", re.MULTILINE)
WORKS_WITH_RE = re.compile(r"\{\{works with\|([^}]+)\}\}")


def _client() -> httpx.Client:
    transport = httpx.HTTPTransport(retries=3)
    return httpx.Client(
        headers={"User-Agent": USER_AGENT},
        timeout=REQUEST_TIMEOUT,
        follow_redirects=True,
        transport=transport,
    )


def fetch_task_list(limit: int = 2000) -> list[str]:
    """List all task titles via MediaWiki API (category: Programming Tasks)."""
    cache_file = CACHE_SUB / "task_list.json"
    if cache_file.exists():
        try:
            return json.loads(cache_file.read_text())
        except Exception:
            pass
    titles: list[str] = []
    apcontinue = None
    with _client() as c:
        while True:
            params = {
                "action": "query",
                "format": "json",
                "list": "categorymembers",
                "cmtitle": "Category:Programming Tasks",
                "cmlimit": "500",
            }
            if apcontinue:
                params["cmcontinue"] = apcontinue
            r = c.get(ROSETTA_API, params=params)
            r.raise_for_status()
            data = r.json()
            for m in data.get("query", {}).get("categorymembers", []):
                titles.append(m["title"])
            apcontinue = data.get("continue", {}).get("cmcontinue")
            if not apcontinue or len(titles) >= limit:
                break
            time.sleep(0.3)
    titles = titles[:limit]
    cache_file.write_text(json.dumps(titles, ensure_ascii=False, indent=1))
    return titles


def fetch_task_wikitext(title: str) -> Optional[str]:
    """Fetch raw wikitext for a task page (cached per title)."""
    safe = re.sub(r"[^\w\-]", "_", title)
    cache_file = CACHE_SUB / f"{safe}.wiki.txt"
    if cache_file.exists():
        return cache_file.read_text(encoding="utf-8", errors="replace")
    with _client() as c:
        params = {
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "rvprop": "content",
            "rvslots": "main",
            "titles": title,
        }
        r = c.get(ROSETTA_API, params=params)
        r.raise_for_status()
        data = r.json()
        pages = data.get("query", {}).get("pages", {})
        for pid, page in pages.items():
            revs = page.get("revisions")
            if not revs:
                continue
            content = revs[0].get("slots", {}).get("main", {}).get("*", "")
            cache_file.write_text(content, encoding="utf-8")
            return content
    return None


# <syntaxhighlight lang="X">...</syntaxhighlight> (modern) and
# <lang X>...</lang> (legacy Rosetta markup)
_SYNTAX_RE = re.compile(
    r"<syntaxhighlight[^>]*lang=[\"']?([\w+#.\- ]+)[\"']?[^>]*>(.*?)</syntaxhighlight>",
    re.IGNORECASE | re.DOTALL,
)
_LANG_RE = re.compile(r"<lang\s+([\w+#.\- ]+)\s*>(.*?)</lang>", re.IGNORECASE | re.DOTALL)


def _clean_code(block: str) -> str:
    """Extract pure source from a section body, stripping wiki markup."""
    # try modern syntaxhighlight first
    parts = _SYNTAX_RE.findall(block)
    if parts:
        # join multiple snippets, tagged by lang
        return "\n\n".join(code.strip() for _, code in parts)
    parts = _LANG_RE.findall(block)
    if parts:
        return "\n\n".join(code.strip() for _, code in parts)
    # fallback: strip any remaining tags/templates, keep text
    txt = re.sub(r"<[^>]+>", "", block)
    txt = re.sub(r"\{\{[^}]+\}\}", "", txt)
    return txt.strip()


def parse_implementations(wikitext: str) -> dict[str, str]:
    """Split wikitext into {language: code_block} using =={{header|Lang}}==.

    Code is cleaned of <syntaxhighlight>/<lang> wiki markup so the stored
    value is usable source (not raw wiki text).
    """
    parts = HEADER_RE.split(wikitext)
    # parts[0] is preamble; then alternating lang, body
    impls: dict[str, str] = {}
    for i in range(1, len(parts), 2):
        lang = parts[i].strip()
        body = parts[i + 1] if i + 1 < len(parts) else ""
        code = _clean_code(body)
        if code:
            impls[lang] = code
    return impls


def ingest(ix: Index, limit: int = 50, index_only: bool = False) -> int:
    """Populate index from Rosetta Code. If index_only, skip fetching bodies
    (fast first pass); otherwise cache wikitext + parsed impls."""
    titles = fetch_task_list()
    count = 0
    for title in titles[:limit]:
        if index_only:
            ix.upsert(name=title, source="rosetta", kind="algorithm",
                      summary="Rosetta Code task", ref=f"https://rosettacode.org/wiki/{title.replace(' ', '_')}")
            count += 1
            continue
        wt = fetch_task_wikitext(title)
        if not wt:
            continue
        impls = parse_implementations(wt)
        langs = list(impls.keys())
        safe = re.sub(r"[^\w\-]", "_", title)
        body_file = CACHE_SUB / f"{safe}.impls.json"
        body_file.write_text(json.dumps(impls, ensure_ascii=False, indent=1))
        works = WORKS_WITH_RE.findall(wt)
        ix.upsert(name=title, source="rosetta", kind="algorithm",
                  langs=langs, summary=f"Rosetta task; {len(langs)} language impls",
                  ref=f"https://rosettacode.org/wiki/{title.replace(' ', '_')}",
                  extra={"works_with": works, "impls_file": str(body_file)},
                  cached_path=str(body_file))
        count += 1
        time.sleep(0.2)
    return count


if __name__ == "__main__":
    ix = Index()
    n = ingest(ix, limit=20, index_only=False)
    print(f"ingested {n} rosetta tasks; stats={ix.stats()}")
    ix.close()
