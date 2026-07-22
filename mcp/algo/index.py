"""
Index + cache manager for sint-algo-mcp.

Schema is intentionally extensible:
  - `entries` holds one row per discovered algorithm/idea/doc, tagged by source.
  - `extra_json` carries source-specific fields without migrations.
  - `ingest` / `add_*` let the agent or user grow the base at runtime.

All lookups go through here so the agent always sees a unified view
regardless of which source a record came from.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from config import CACHE_DIR, INDEX_DB, SOURCES, OPTIONAL_SOURCES

SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    source      TEXT NOT NULL,            -- rosetta|github|papers|patents|docs|docs-tools|user|...
    kind        TEXT DEFAULT 'algorithm', -- algorithm|paper|patent|doc|middleware|note
    era         INTEGER,                  -- year, for forgotten-ideas filtering
    langs       TEXT,                     -- JSON list of languages (for code sources)
    summary     TEXT,                     -- short distilled description
    ref         TEXT,                     -- canonical URL / identifier
    extra_json  TEXT,                     -- source-specific payload
    cached_path TEXT,                     -- local file path if body cached
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_entries_name ON entries(name);
CREATE INDEX IF NOT EXISTS idx_entries_source ON entries(source);
CREATE INDEX IF NOT EXISTS idx_entries_era ON entries(era);
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Index:
    def __init__(self, db_path: Path = INDEX_DB):
        self.db = db_path
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()
        self._init_meta()

    def _init_meta(self):
        cur = self.conn.execute("SELECT value FROM meta WHERE key='schema_version'")
        if cur.fetchone() is None:
            self.conn.execute(
                "INSERT INTO meta(key,value) VALUES('schema_version','1')"
            )
            self.conn.execute(
                "INSERT INTO meta(key,value) VALUES('created_at',?)", (_now(),)
            )
            self.conn.commit()

    # ---- write ---------------------------------------------------------
    def upsert(self, *, name: str, source: str, kind: str = "algorithm",
               era: Optional[int] = None, langs: Optional[list[str]] = None,
               summary: str = "", ref: str = "", extra: Optional[dict] = None,
               cached_path: str = "") -> int:
        existing = self.conn.execute(
            "SELECT id FROM entries WHERE name=? AND source=?", (name, source)
        ).fetchone()
        now = _now()
        langs_json = json.dumps(langs or [], ensure_ascii=False)
        extra_json = json.dumps(extra or {}, ensure_ascii=False)
        if existing:
            eid = existing["id"]
            self.conn.execute(
                """UPDATE entries SET kind=?, era=?, langs=?, summary=?, ref=?,
                   extra_json=?, cached_path=?, updated_at=? WHERE id=?""",
                (kind, era, langs_json, summary, ref, extra_json, cached_path, now, eid),
            )
        else:
            cur = self.conn.execute(
                """INSERT INTO entries
                   (name,source,kind,era,langs,summary,ref,extra_json,cached_path,created_at,updated_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                (name, source, kind, era, langs_json, summary, ref, extra_json,
                 cached_path, now, now),
            )
            eid = cur.lastrowid
        self.conn.commit()
        return eid

    def add_user_note(self, *, name: str, note: str, refs: Optional[list[str]] = None,
                      kind: str = "note") -> int:
        return self.upsert(name=name, source="user", kind=kind,
                           summary=note, ref=json.dumps(refs or []),
                           extra={"refs": refs or []})

    # ---- read ----------------------------------------------------------
    def search(self, query: str, source: str = "", era_min: int = 0,
               era_max: int = 9999, limit: int = 30) -> list[dict]:
        sql = "SELECT * FROM entries WHERE 1=1"
        params: list[Any] = []
        if query:
            sql += " AND (name LIKE ? OR summary LIKE ?)"
            params += [f"%{query}%", f"%{query}%"]
        if source:
            sql += " AND source=?"
            params.append(source)
        if era_min > 0 or era_max < 9999:
            sql += " AND (era IS NULL OR (era >= ? AND era <= ?))"
            params += [era_min, era_max]
        sql += " ORDER BY updated_at DESC LIMIT ?"
        params.append(limit)
        rows = self.conn.execute(sql, params).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def get(self, eid: int) -> Optional[dict]:
        r = self.conn.execute("SELECT * FROM entries WHERE id=?", (eid,)).fetchone()
        return self._row_to_dict(r) if r else None

    def by_source(self, source: str, limit: int = 50) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM entries WHERE source=? ORDER BY name LIMIT ?",
            (source, limit),
        ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def stats(self) -> dict:
        rows = self.conn.execute(
            "SELECT source, COUNT(*) c FROM entries GROUP BY source"
        ).fetchall()
        return {r["source"]: r["c"] for r in rows}

    def _row_to_dict(self, r: sqlite3.Row) -> dict:
        d = dict(r)
        d["langs"] = json.loads(d["langs"] or "[]")
        d["extra"] = json.loads(d["extra_json"] or "{}")
        return d

    def close(self):
        self.conn.close()


# convenience singleton for modules
def open_index() -> Index:
    return Index()
