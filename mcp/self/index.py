"""Vector store for sint-self (sqlite + embeddings blob)."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from config import CACHE_DIR


SCHEMA = """
CREATE TABLE IF NOT EXISTS self (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    text        TEXT NOT NULL,
    tag         TEXT,
    source      TEXT,
    voice       TEXT DEFAULT 'any',   -- which voice this note applies to
    emb         BLOB,                       -- float32 vector bytes
    created_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tag ON self(tag);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SelfStore:
    def __init__(self, db_path: Path = CACHE_DIR / "self.db"):
        self.conn = sqlite3.connect(str(db_path))
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def add(self, text: str, tag: str, source: str, voice: str = "any",
            emb: list[float] | None = None) -> int:
        import numpy as np
        if emb is None:
            from embed import embed
            emb = embed(text)
        blob = np.asarray(emb, dtype=np.float32).tobytes()
        cur = self.conn.execute(
            "INSERT INTO self(text,tag,source,voice,emb,created_at) VALUES(?,?,?,?,?,?)",
            (text, tag, source, voice, blob, _now()))
        self.conn.commit()
        return cur.lastrowid

    def all(self) -> list[dict]:
        rows = self.conn.execute(
            "SELECT id,text,tag,source,voice FROM self").fetchall()
        return [dict(zip(("id", "text", "tag", "source", "voice"), r)) for r in rows]

    def count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM self").fetchone()[0]

    def close(self):
        self.conn.close()
