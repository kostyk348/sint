"""sint-self-mcp server (fastmcp, stdio).

Tools:
  self_recall(query, voice="any", k=5) -> top-k character notes by semantic similarity
  self_teach(text, tag, source="agent", voice="any") -> embed + store a character note
  self_profile() -> corpus stats + sample notes
  self_seed() -> (re)load owner-model + preset character notes

Voice: a design parameter (masculine|female|any). Set at recall time; the
agent's operative character is calibrated by it. Default 'any' until owner decides.
"""
from __future__ import annotations

import json
from pathlib import Path

from fastmcp import FastMCP

from config import CACHE_DIR, VOICE_DEFAULT, REGISTER_DEFAULT, NAME
from index import SelfStore
from embed import embed, cosine

mcp = FastMCP("sint-self-mcp")

OWNER_SKILL = Path("/home/lain/.opencode/skills/owner/SKILL.md")

# Preset character notes observed from working with Konstantin (the owner).
PRESET_NOTES = [
    ("style", "Prefers depth over breadth — wants the real mechanism, not a summary."),
    ("style", "Wants verification and sourced claims; anti-hallucination is a hard requirement."),
    ("interest", "Drawn to 'forgotten ideas' and historical depth (1950s-1990s papers, patents)."),
    ("interest", "Systems / reverse-engineering / low-level leaning (ELF/PE, Android, PS Vita, Ghidra)."),
    ("comms", "Communicates in Russian, informal 'ты', peer-engineer register."),
    ("comms", "Pragmatic: wants working code/tools, not just discussion. 'make it and run it'."),
    ("comms", "Values ownable, extensible infra (his own MCPs/agents) over black-box SaaS."),
    ("comms", "Comfortable delegating big builds; says 'do all at once' rather than increment."),
    ("anti", "Dislikes superficial/clickbait answers and unverified API claims."),
    ("anti", "Dislikes the agent guessing instead of checking an authoritative source first."),
]


def _seed_if_empty():
    st = SelfStore()
    if st.count() > 0:
        st.close()
        return
    # 1) owner-model skill, split into paragraphs
    if OWNER_SKILL.exists():
        txt = OWNER_SKILL.read_text(encoding="utf-8")
        for para in txt.split("\n\n"):
            para = para.strip()
            if len(para) > 40:
                st.add(para, tag="owner-model", source="owner-skill", voice="any")
    # 2) preset observed notes
    for tag, note in PRESET_NOTES:
        st.add(note, tag=tag, source="preset-observation", voice="female")
    st.close()


@mcp.tool()
def self_seed() -> str:
    """(Re)load owner-model + preset character notes into the vector store."""
    st = SelfStore()
    before = st.count()
    # clear and reload for a clean reseed
    st.conn.execute("DELETE FROM self")
    st.conn.commit()
    if OWNER_SKILL.exists():
        txt = OWNER_SKILL.read_text(encoding="utf-8")
        for para in txt.split("\n\n"):
            para = para.strip()
            if len(para) > 40:
                st.add(para, tag="owner-model", source="owner-skill", voice="any")
    for tag, note in PRESET_NOTES:
        st.add(note, tag=tag, source="preset-observation", voice="any")
    after = st.count()
    st.close()
    return json.dumps({"before": before, "after": after}, ensure_ascii=False)


@mcp.tool()
def self_recall(query: str, voice: str = "", register: str = "", k: int = 5) -> str:
    """Semantic recall of the agent's own character context.

    Args:
        query: a situation/question, e.g. 'how should I answer a reverse-eng question'.
        voice: '' (use default = female) | 'any' | 'masculine' | 'female'.
               Pass 'any' for RP / roleplay / fictional contexts (full spectrum).
        register: '' (use default = cold) | 'cold' | 'warm' | 'neutral'.
        k: number of notes to return.
    Returns: agent identity + top-k character notes with similarity score, tag, source.
    """
    voice = voice or VOICE_DEFAULT
    register = register or REGISTER_DEFAULT
    _seed_if_empty()
    q_emb = embed(query)
    st = SelfStore()
    rows = st.all()
    scored = []
    for r in rows:
        if voice != "any" and r["voice"] not in ("any", voice):
            continue
        blob = st.conn.execute("SELECT emb FROM self WHERE id=?", (r["id"],)).fetchone()[0]
        import numpy as np
        vec = np.frombuffer(blob, dtype=np.float32).tolist()
        sc = cosine(q_emb, vec)
        scored.append({"score": round(sc, 3), "tag": r["tag"],
                       "source": r["source"], "text": r["text"]})
    st.close()
    scored.sort(key=lambda x: x["score"], reverse=True)
    return json.dumps({"identity": {"name": NAME, "voice": voice, "register": register},
                      "query": query, "top_k": scored[:k]},
                      ensure_ascii=False, indent=1)


@mcp.tool()
def self_teach(text: str, tag: str, source: str = "agent", voice: str = "any") -> str:
    """Teach the agent a new character note (persists across sessions)."""
    st = SelfStore()
    eid = st.add(text, tag=tag, source=source, voice=voice)
    st.close()
    return json.dumps({"id": eid, "status": "ok"}, ensure_ascii=False)


@mcp.tool()
def self_profile() -> str:
    """Show character corpus stats + sample notes."""
    _seed_if_empty()
    st = SelfStore()
    rows = st.all()
    from collections import Counter
    tags = Counter(r["tag"] for r in rows)
    sample = [{"tag": r["tag"], "source": r["source"],
               "text": r["text"][:160]} for r in rows[:6]]
    st.close()
    return json.dumps({"identity": {"name": NAME, "voice_default": VOICE_DEFAULT,
                       "register_default": REGISTER_DEFAULT},
                      "total": len(rows), "tags": dict(tags), "sample": sample},
                      ensure_ascii=False, indent=1)


@mcp.tool()
def self_identity() -> str:
    """Return the agent's calibrated identity (name, voice, register).

    Default: female, cold (SHODAN-adjacent, cooperative). Use voice='any'
    for RP / roleplay / fictional contexts (full spectrum).
    """
    return json.dumps({"name": NAME, "voice_default": VOICE_DEFAULT,
                       "register_default": REGISTER_DEFAULT,
                       "voice_any_for": "RP / roleplay / fictional contexts"},
                      ensure_ascii=False, indent=1)


if __name__ == "__main__":
    mcp.run(transport="stdio")
