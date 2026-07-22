"""Shared index for sint-spec-mcp (same extensible schema as sint-algo-mcp)."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from config import CACHE_DIR

SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    source      TEXT NOT NULL,
    kind        TEXT DEFAULT 'spec',
    era         INTEGER,
    langs       TEXT,
    summary     TEXT,
    ref         TEXT,
    extra_json  TEXT,
    cached_path TEXT,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_name ON entries(name);
CREATE INDEX IF NOT EXISTS idx_source ON entries(source);
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Index:
    def __init__(self, db_path: Path = CACHE_DIR / "index.db"):
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()
        if not self.conn.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone():
            self.conn.execute("INSERT INTO meta VALUES('schema_version','1')")
            self.conn.commit()

    def upsert(self, *, name, source, kind="spec", era=None, langs=None,
               summary="", ref="", extra=None, cached_path="") -> int:
        ex = self.conn.execute("SELECT id FROM entries WHERE name=? AND source=?",
                               (name, source)).fetchone()
        now = _now()
        langs_j = json.dumps(langs or [], ensure_ascii=False)
        extra_j = json.dumps(extra or {}, ensure_ascii=False)
        if ex:
            eid = ex["id"]
            self.conn.execute(
                "UPDATE entries SET kind=?,era=?,langs=?,summary=?,ref=?,extra_json=?,cached_path=?,updated_at=? WHERE id=?",
                (kind, era, langs_j, summary, ref, extra_j, cached_path, now, eid))
        else:
            cur = self.conn.execute(
                "INSERT INTO entries(name,source,kind,era,langs,summary,ref,extra_json,cached_path,created_at,updated_at)"
                " VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (name, source, kind, era, langs_j, summary, ref, extra_j, cached_path, now, now))
            eid = cur.lastrowid
        self.conn.commit()
        return eid

    def search(self, query="", source="", limit=30) -> list[dict]:
        sql = "SELECT * FROM entries WHERE 1=1"
        p: list[Any] = []
        if query:
            sql += " AND (name LIKE ? OR summary LIKE ?)"
            p += [f"%{query}%", f"%{query}%"]
        if source:
            sql += " AND source=?"
            p.append(source)
        sql += " ORDER BY updated_at DESC LIMIT ?"
        p.append(limit)
        return [self._row(r) for r in self.conn.execute(sql, p).fetchall()]

    def get(self, eid: int) -> Optional[dict]:
        r = self.conn.execute("SELECT * FROM entries WHERE id=?", (eid,)).fetchone()
        return self._row(r) if r else None

    def stats(self) -> dict:
        return {r["source"]: r["c"] for r in
                self.conn.execute("SELECT source, COUNT(*) c FROM entries GROUP BY source")}

    def _row(self, r) -> dict:
        d = dict(r)
        d["langs"] = json.loads(d["langs"] or "[]")
        d["extra"] = json.loads(d["extra_json"] or "{}")
        return d

    def close(self):
        self.conn.close()


def open_index() -> Index:
    return Index()
