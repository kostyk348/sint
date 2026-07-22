---
name: wiki
description: Use when creating a new artifact or checking if something already exists. Artifact registry of all created scripts, benchmarks, prototypes, data, templates. Cross-reference with dso.md for verified patterns.
---

> Registry of all created artifacts: scripts, benchmarks, prototypes, data.
> Agent registers every created artifact here. Never create something without checking if it exists.

## HOW TO USE

**Before creating anything**, search this file:
- Same functionality already exists? → reuse or extend, don't recreate
- Similar exists? → note the difference, extend if possible
- Nothing exists? → create, then register here

**After creating anything** that is more than a throwaway snippet:
- Add entry to the relevant section
- Fill all fields
- Update "Last updated" at top

**Status values**: `active` | `deprecated` | `broken` | `experimental`

## SCRIPTS & TOOLS

> Reusable scripts, CLI tools, utilities.

| Name | Path | What it does | Language | Status | Notes |
|---|---|---|---|---|---|---|
| steam-with-dsa.sh | /home/lain/dsa/steam-with-dsa.sh | Launch Steam game with DSA audio via LD_PRELOAD | bash | active | Usage: ./steam-with-dsa.sh <appid> |
| DSA Makefile | /home/lain/dsa/Makefile | Build libdsa.so + libfmod.so + libfmodstudio.so | make | active | ALSA + pthread linking |

## PROTOTYPES & EXPERIMENTS

> Working prototypes, proof-of-concepts, experimental implementations.

| Name | Path | Project | Status | Last touched | Notes |
|---|---|---|---|---|---|
| HL2 Vita Physics Design Doc | /home/lain/HL2_VITA_PHYSICS_DSO.md | HL2 on Vita | active | 2026-07-06 | Bullet Physics + DSO patterns for PS Vita homebrew |
| DSA — Data-oriented Streaming Audio | /home/lain/dsa/ | DSA | active | 2026-07-06 | Open FMOD replacement. ALSA, SoA mixer, 205 C++ ABI symbols. STS2 verified. |
| DSA FMOD Core C ABI | /home/lain/dsa/src/fmod_compat.c | DSA | active | 2026-07-06 | 69 FMOD5_* symbols exported |
| DSA FMOD Core C++ ABI | /home/lain/dsa/src/fmod_cxxabi.c | DSA | active | 2026-07-06 | 135 _ZN4FMOD* symbols for C++ ABI compat |
| DSA FMOD Studio C ABI | /home/lain/dsa/src/studio_compat.c | DSA | active | 2026-07-06 | 40 FMOD_Studio_* + 41 Studio C++ ABI symbols |
| PDF Translate | /home/lain/pdf-translate/pdf-translate.py | pdf-translate | active | 2026-07-08 | Layout‑preserving PDF translation. SENSE→FACT→LOGIC→CAUSALITY pipeline. argos-translate, auto‑venv, rotated text, overflow scaling, hash‑chain audit, optional OCR. |
 
## BENCHMARKS

> Performance measurement scripts. Always note what they measure and last known result.

| Name | Path | Measures | Last run | Result | Notes |
|---|---|---|---|---|---|
| — | — | — | — | — | — |

## PROTOTYPES & EXPERIMENTS

> Working prototypes, proof-of-concepts, experimental implementations.

| Name | Path | Project | Status | Last touched | Notes |
|---|---|---|---|---|---|
| HL2 Vita Physics Design Doc | /home/lain/HL2_VITA_PHYSICS_DSO.md | HL2 on Vita | active | 2026-07-06 | Bullet Physics + DSO patterns for PS Vita homebrew |

## DATA & RESULTS

> Benchmark outputs, measurement data, experiment results worth keeping.

| Name | Path | Description | Date | Linked to |
|---|---|---|---|---|
| — | — | — | — | — |

## TEMPLATES & SKELETONS

> Reusable code templates, project skeletons, boilerplate.

| Name | Path | Use for | Language | Notes |
|---|---|---|---|---|
| — | — | — | — | — |

## DEPRECATED

> No longer used but kept for reference. Do not delete — they may explain why something was tried and abandoned.

| Name | Path | Was used for | Deprecated | Why deprecated |
|---|---|---|---|---|
| — | — | — | — | — |

## AGENT INSTRUCTIONS

When registering a new artifact, use this format check:
```
□ Name is descriptive (not "script.py" or "test2.py")
□ Path is correct and file actually exists
□ "What it does" is one sentence, concrete
□ Status is set
□ If benchmark: result field has actual numbers, not "fast"
□ If deprecated: reason is filled
```

Cross-reference with dso.md when a benchmark confirms or refutes a candidate pattern.
