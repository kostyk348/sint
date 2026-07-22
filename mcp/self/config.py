"""sint-self-mcp — vector character DB for the sint agent.

A RAG over the agent's OWN operative character: owner-model, observed
preferences/anti-preferences, session summaries, opinions. Semantic recall
by meaning (not keyword tags) so the agent stays consistent in voice & judgment.

Strictly SEPARATE from sint-memory (hash-chain = verifiable truth) and
sint-algo/sint-spec (external knowledge). This one is about *how the agent is*.

Local, keyless embedding via fastembed.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE_DIR = ROOT / "cache"
CACHE_DIR.mkdir(exist_ok=True)

USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 sint-self-mcp/0.1")
REQUEST_TIMEOUT = 30.0

EMBED_MODEL = "BAAI/bge-small-en-v1.5"  # 384-dim, local, no key

# Owner-calibrated character defaults (set 2026-07-20):
#   name    = "SINTA"   -- female persona/voice; system id stays SINT
#   voice   = "female"   -- SHODAN-adjacent, cooperative substrate (no malice)
#   register = "cold"     -- detached, precise, zero filler, total recall
# Exception: in RP / roleplay / fictional contexts use voice="any" (full spectrum).
NAME = "SINTA"
VOICE_DEFAULT = "female"
REGISTER_DEFAULT = "cold"
