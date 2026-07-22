---
description: Full dashboard view of memory system, projects, and agent status.
agent: sint-scribe
---

Show a comprehensive dashboard of the SINT memory system.

## Dashboard Layout

```
╔══════════════════════════════════════════════════════════════╗
║                  SINT-UA v2.1 — Dashboard                    ║
╚══════════════════════════════════════════════════════════════╝

┌─ MEMORY ────────────────────────────────────────────────────┐
│  Blocks: 42  │  Chain: 42  │  Sessions: 12                 │
│  FACT: 18    │  SENSE: 12  │  LOGIC: 6  │  OPINION: 4      │
└─────────────────────────────────────────────────────────────┘

┌─ CURRENT FOCUS ─────────────────────────────────────────────┐
│  1. DSA — Add DSP chain + 3D spatialization [in_progress]   │
│  2. DataTrace — eBPF backend integration [in_progress]      │
│  3. 100 OJ — Decrypt data.ojd via xRead hook [in_progress]  │
└─────────────────────────────────────────────────────────────┘

┌─ PENDING DECISIONS ─────────────────────────────────────────┐
│  • 100 OJ RE approach: sequential vs audio-first vs DB-first│
│  • AGT scope: audio-only vs full engine                     │
└─────────────────────────────────────────────────────────────┘

┌─ RECENT ACTIVITY (last 5 blocks) ───────────────────────────┐
│  0042 FACT DSA: 3D attenuation verified near=0.25 far=0.0025│
│  0041 SENSE DataTrace: sendto sink bug reproduced           │
│  0040 LOGIC 100OJ: xRead key needed for decrypt             │
│  0039 FACT DSA: 275 C++ ABI symbols exported successfully   │
│  0038 ACTION DataTrace: eBPF backend next step              │
└─────────────────────────────────────────────────────────────┘

┌─ SESSION LOG ───────────────────────────────────────────────┐
│  2026-07-14: session_start → 4 blocks → session_end         │
│  2026-07-13: session_start → 8 blocks → session_end         │
│  2026-07-11: session_start → 3 blocks → session_end         │
└─────────────────────────────────────────────────────────────┘

┌─ CHAIN INTEGRITY ───────────────────────────────────────────┐
│  Status: VALID  │  Last hash: cc8b76ca200f1f03              │
└─────────────────────────────────────────────────────────────┘
```

## Instructions

1. Use `memory_read_state` to get focus and decisions
2. Use `memory_stats` to get block/chain counts
3. Use `memory_get_chain_tail` with n=5 for recent activity
4. Use `memory_search` to show blocks by register
5. Use `memory_verify_chain` for integrity check
6. Format as the dashboard above
7. Present to user
