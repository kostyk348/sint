# sint-self-mcp

Vector character database for the [SINT](https://github.com/kostyk348/sint-ua-v2.1) agent — semantic recall of its own operative character.

## What It Does

The agent can **recall** its own behavioral patterns, preferences, and learned character notes — not from a static prompt, but from a vector-indexed database that grows across sessions.

This is **identity persistence**: the agent remembers how it should behave, what the owner values, and what anti-patterns to avoid — semantically, not by keyword matching.

## Tools

| Tool | Description |
|---|---|
| `self_recall(query, voice, register, k)` | Semantic search of character notes |
| `self_teach(text, tag, source, voice)` | Add a new character note (persists) |
| `self_profile()` | Corpus stats + sample notes |
| `self_seed()` | Reload owner-model + preset notes |
| `self_identity()` | Current calibrated identity |

## Voice System

Voice is a **design parameter**, not a persona toggle:

| Voice | Use Case |
|---|---|
| `female` | Default. Cold, SHODAN-adjacent, cooperative |
| `masculine` | Alternative register |
| `any` | Full spectrum — for RP / roleplay / fictional contexts |

```python
# Default: agent recalls its female/cold character
self_recall("how to answer reverse-eng questions")

# RP mode: full voice spectrum
self_recall("how to comfort a scared child", voice="any", register="warm")
```

## How It Works

```
Text → fastembed (BAAI/bge-small-en-v1.5) → 384-dim vector
                                                    ↓
SQLite store ← cosine similarity search ← query vector
```

## Character Notes

Notes are stored with metadata:

```json
{
  "id": 42,
  "text": "Prefers depth over breadth — wants the real mechanism, not a summary.",
  "tag": "style",
  "source": "owner-model",
  "voice": "any",
  "emb": [0.12, -0.34, ...]
}
```

### Preset Notes (Observed from Owner)

These are calibrated from working with Konstantin:

- **style**: Prefers depth over breadth
- **style**: Wants verification and sourced claims
- **interest**: Drawn to forgotten ideas (1950s-1990s papers)
- **interest**: Systems / reverse-engineering / low-level
- **comms**: Communicates in Russian, informal register
- **comms**: Pragmatic — wants working code, not discussion
- **anti**: Dislikes superficial/clickbait answers
- **anti**: Dislikes guessing instead of checking sources

## Setup

```bash
pip install fastmcp fastembed numpy
```

## Run

```bash
python server.py    # stdio mode
```

## Seeding

On first use, `self_seed()` loads:
1. Owner model from `~/.opencode/skills/owner/SKILL.md`
2. Preset character notes observed from working sessions

To re-seed after updating the owner model:
```python
self_seed()  # Clears and reloads
```

## Integration

Designed for the [SINT](https://github.com/kostyk348/sint-ua-v2.1) agent. The agent calls `self_recall()` at session start to calibrate its behavioral register.

## License

MIT
