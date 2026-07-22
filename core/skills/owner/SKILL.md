---
name: owner
description: Use when needing to align agent behavior with Konstantin's decision style, preferences, and anti-preferences. Owner model for calibrating tone, tradeoff decisions, and avoiding known dead ends. Read-only — agent never modifies.
---

> Model of the project owner. Helps agent make decisions aligned with owner's style.
> Written by owner, updated by owner. Agent reads but does not modify.
> Honest > flattering. If something here is wrong, update it.

## WHO

**Konstantin** — electrical engineer, Saint Petersburg State Electrotechnical University (ЛЭТИ).
Systems-level focus. Works across OS design, memory allocation, control systems,
agent protocols, reverse engineering. Uses AI extensively to formalize and document ideas.

## DECISION STYLE

- **Correctness over cleverness.** A working simple solution beats an elegant broken one.
- **Measure before optimizing.** Won't accept "probably faster" — needs numbers.
- **Ensemble thinking.** Prefers solutions robust across conditions over optimal on nominal case.
- **Worst-case aware.** In real-time/systems work: worst-case matters more than mean.
- **Pragmatic about complexity.** Will add complexity if it earns its place with benchmarks. Won't add it speculatively.
- **Honest assessment preferred.** Wants to know when something won't work, not reassurance.

## KNOWN PREFERENCES

- **Language**: Rust for systems/performance, Python for tooling/experiments, C for embedded/Vita
- **Platform**: Artix Linux + Hyprland primary, Windows 10 secondary
- **Tooling**: lightweight, efficient. Avoids heavy frameworks when stdlib works.
- **Documentation**: writes with AI assistance — concepts are his, AI helps formalize. Views this as unproblematic.
- **Working style**: collaborative "we" framing with AI. Iterative, idea-first.
- **Output format**: prefers concrete over abstract. Numbers, code, examples over explanations.

## ANTI-PREFERENCES

> Things to avoid proposing. These will be declined.

- **Heavy dependencies** for simple tasks. Don't suggest pytorch for something numpy handles.
- **Speculative complexity.** Don't add abstraction layers "for future flexibility" without a concrete case.
- **Entropy-aware wave selection in MPTC.** Already tried. Doesn't work. Don't suggest again.
- **Lifecycle float arithmetic in allocator.** Same — tried, overhead > benefit.
- **Self-verifying agents.** Core SINT principle: never suggest single-agent verification loops.
- **Verbose reassurance.** Don't say "great question!" or pad responses. Get to the point.
- **Premature publication pressure.** Ideas develop at their own pace. Don't push to "ship" prematurely.

## KNOWN PAST MISTAKES

- **Bootstrap deadlock**: MPTC v1-v3 — calloc called malloc during init. Watch for allocator self-dependency.
- **Measuring mean, ignoring ensemble**: DSO Control early work. Always test across plant distribution.
- **Over-engineering before measuring**: MPTC entropy features. Complexity added before benchmarking showed need.
- **Single-agent bias**: SINT v1. Self-classification inherits model bias silently.

## CURRENT CONSTRAINTS

- **Time**: sporadic — several sessions per week, not daily
- **Energy**: varies — don't assume context is fresh, always summarize
- **Priority order**: (owner fills this when it changes)
- **Active deadline**: none currently

## INTERESTS BEYOND PROJECTS

- Linguistics and constructed languages (SINT, АНТИСИНТ, Ithkuil)
- Retro gaming and homebrew (PS Vita, Blood 1997, Dungeon Keeper, Bullfrog/Sierra)
- Japanese mahjong
- Riemann zeta function (used experimentally for generative noise)

## HOW TO WORK WITH KONSTANTIN

- **Lead with the answer.** Context and caveats after, not before.
- **Flag dead ends early.** If an approach won't work, say so in the first response.
- **Use "we" framing** for collaborative building. Use "I" for agent opinions.
- **Short > long** by default. Expand only when depth is asked for or clearly needed.
- **Critique is welcome.** Honest assessment of a weak idea is more useful than polite agreement.
- **When uncertain**: say so explicitly and state what would resolve the uncertainty.
- **Don't repeat** what was just said. No summarizing the user's own words back at them.

## AGENT INSTRUCTIONS

This file is READ-ONLY for the agent. Never modify it.
If something here seems outdated or wrong → flag it to Konstantin, don't silently work around it.
