# SINT Manifesto

**Agent ≠ Chatbot with Tools**

Version 0.1 — 2026-07-21

---

## The Problem

Most "agents" today are chatbots with function calling.

They have:
- ❌ No memory beyond context window
- ❌ No beliefs, no confidence, no revision
- ❌ No self-awareness, no metacognition
- ❌ No learning across sessions
- ❌ No identity, no values, no constraints
- ❌ No feedback loop, no error tracking

They are stateless, thoughtless, and forgetful.

---

## The Thesis

An agent is not a language model with tools bolted on.

An agent is a **system** with seven cognitive layers:

```
PERCEPTION    — what I see
COGNITION     — how I think
MEMORY        — what I know
ACTION        — what I do
METACOGNITION — how I think about thinking
IDENTITY      — who I am
FEEDBACK      — how I learn
```

Each layer is independent, replaceable, and designed for a specific function.
Each layer has its own data structures, persistence model, and verification protocol.

---

## The Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         SINT OS                             │
│                                                             │
│  PERCEPTION                                                 │
│    ├─ RE Graph        — binaries → semantic graph           │
│    ├─ Spec Base       — RFCs, formats → structured knowledge│
│    ├─ Algo Base       — algorithms, papers, patents         │
│    └─ Log Parser      — events → correlated timeline        │
│                                                             │
│  COGNITION                                                  │
│    ├─ Devflow         — pipelines, TDD, commit conventions  │
│    ├─ Analogy Engine  — cross-domain structural mapping     │
│    ├─ Adversarial     — attack own conclusions              │
│    └─ Planner         — multi-step reasoning chains         │
│                                                             │
│  MEMORY                                                     │
│    ├─ Working         — current task state (structured)     │
│    ├─ Session         — hash-chain provenance               │
│    ├─ Long-term       — decay-weighted knowledge blocks     │
│    ├─ Semantic        — vector embeddings + retrieval       │
│    └─ Temporal        — "what was known when"               │
│                                                             │
│  ACTION                                                     │
│    ├─ Code            — read, write, edit, execute          │
│    ├─ Files           — filesystem operations               │
│    ├─ Network         — HTTP, git, APIs                     │
│    └─ Communication   — user interaction                    │
│                                                             │
│  METACOGNITION                                              │
│    ├─ Epistemic       — beliefs, confidence, revision       │
│    ├─ Constraints     — hard/soft limits, conflict detect   │
│    ├─ Monitor         — error patterns, drift detection     │
│    └─ Calibration     — "was I right last time?"            │
│                                                             │
│  IDENTITY                                                   │
│    ├─ Character       — operative personality (vector DB)   │
│    ├─ Owner Model     — values, preferences, anti-patterns  │
│    └─ Values          — ethical framework, priorities        │
│                                                             │
│  FEEDBACK                                                   │
│    ├─ Session Replay  — "where did I go wrong?"             │
│    ├─ Cross-session   — "what pattern do I keep repeating?" │
│    └─ Learning        — "what should I do differently?"     │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Principles

### 1. Provenance is Non-Negotiable

Every belief must trace back to its source.
Every decision must have explicit reasoning.
Every output must declare its semantic register (SENSE/FACT/LOGIC/OPINION/CAUSALITY).

A fact without a source is a hypothesis.
A decision without reasoning is a guess.
An opinion presented as fact is a lie.

### 2. Memory is Not Storage, It's Knowledge Management

Storing text is not memory. Memory is:
- **Typed** — every block has a register (SENSE/FACT/LOGIC/ACTION)
- **Linked** — blocks reference each other, forming chains
- **Temporal** — knowledge decays, gets verified, gets revised
- **Provenanced** — every block traces to its origin
- **Queryable** — by content, register, project, tags, time

### 3. Character is Not Persona, It's Operative Calibration

A character is not "be helpful and concise." A character is:
- **Vector-encoded** — semantic recall of operative behavior
- **Owner-calibrated** — aligned with the human's values
- **Context-sensitive** — adapts to domain and register
- **Self-aware** — knows its own tendencies and biases

### 4. Metacognition is the Missing Layer

An agent that cannot think about its own thinking is:
- Unable to detect when it's wrong
- Unable to calibrate confidence
- Unable to learn from mistakes
- Unable to distinguish knowledge from belief

Metacognition = beliefs + confidence + revision + self-monitoring.

### 5. Feedback Loops Make Agents Intelligent

Without feedback, an agent repeats the same mistakes forever.
Feedback loops:
- **Session-level**: "where did this session go wrong?"
- **Cross-session**: "what pattern do I keep repeating?"
- **Cross-domain**: "what works in crypto that might work in RE?"

---

## Working Memory: The Context Window Problem

The fundamental constraint: LLMs have finite context windows.
The solution: **structured, queryable, compressible working state.**

```
┌─────────────────────────────────────────────┐
│           WORKING MEMORY MODEL              │
│                                             │
│  ┌─────────────┐    ┌──────────────────┐   │
│  │ CONVERSATION │    │ STRUCTURED STATE │   │
│  │ (raw, recent)│    │ (compressed,     │   │
│  │              │    │  queryable)      │   │
│  │  last 20     │    │                  │   │
│  │  messages    │    │  task_state.json │   │
│  │              │    │  beliefs.json    │   │
│  │              │    │  findings.json   │   │
│  └──────┬───────┘    └────────┬─────────┘   │
│         │                     │             │
│         └──────────┬──────────┘             │
│                    │                        │
│              ┌─────▼─────┐                  │
│              │  COMPRESS  │                  │
│              │  on every  │                  │
│              │  10-20     │                  │
│              │  messages  │                  │
│              └─────┬─────┘                  │
│                    │                        │
│              ┌─────▼─────┐                  │
│              │  RETRIEVE  │                  │
│              │  on demand │                  │
│              │  via tools │                  │
│              └───────────┘                  │
└─────────────────────────────────────────────┘
```

### How It Works

1. **Conversation** flows normally (last N messages in context)
2. **Every 10-20 messages**, agent compresses conversation into structured state:
   - What task are we on?
   - What did we check?
   - What did we find?
   - What's still open?
   - What beliefs were formed?
3. **Structured state** lives in files (JSON), not in context window
4. **On demand**, agent reads state files via tools (one tool call = ~200 tokens)
5. **Old messages** fall out of context naturally

### The Key Insight

**You don't need to remember everything. You need to remember the RIGHT things, and know how to find the rest.**

The agent maintains:
- `task_state.json` — current objective, progress, next steps
- `findings.json` — key discoveries with sources
- `beliefs.json` — what we think is true, with confidence
- `open_questions.json` — what we still don't know

These are small (200-500 tokens each), queryable, and always up-to-date.

---

## What SINT Is Not

- ❌ Not a framework you import. It's an architecture you implement.
- ❌ Not a single MCP server. It's a system of independent components.
- ❌ Not opinionated about tools. It's opinionative about cognitive structure.
- ❌ Not about "making agents smarter." It's about making agents **sane**.

---

## Status

| Component | Layer | Status | Notes |
|---|---|---|---|
| sint-memory | Memory | ✅ v2.1 | Hash-chain provenance, temporal decay, drift detection |
| sint-self-mcp | Identity | ✅ | Vector character DB, semantic recall, owner model |
| sint-spec-mcp | Perception | ✅ | RFC + binary format specs, hybrid search |
| sint-algo-mcp | Perception | ✅ | Rosetta Code, papers, patents, docs |
| sint-re-graph-mcp | Perception | ✅ | Semantic binary graph + DataTrace taint |
| sint-devflow-mcp | Cognition | ✅ | Pipeline + modular style + TDD + edge cases |
| sint-crypto-mcp | Cognition | ✅ | 25+ ciphers, test vectors, pattern detection |
| sint-embed-mcp | Cognition | ✅ | MCU database, RTOS patterns, code gen |
| sint-working-mcp | Memory | ✅ | Task state, findings, beliefs, epistemic state |
| sint-historian-mcp | Memory | ✅ | Session analytics, drift detection, work reports |
| sint-learner-mcp | Feedback | ✅ | Error patterns, improvements, pre-session check |
| sint-portfolio-mcp | Feedback | ✅ | Project portfolio, knowledge transfer links |
| sint-critic | Metacognition | ✅ | Register audits, fact-checking, code review |
| sint-main | — | ✅ | Primary orchestrator, session lifecycle |
| sint-scribe | — | ✅ | Memory management agent |
| sint-router | — | ✅ | Task classification, skill recommendation |
| Log Parser | Perception | 🔲 | Events → correlated timeline |
| Analogy Engine | Cognition | 🔲 | Cross-domain structural mapping |
| Constraint Tracker | Metacognition | 🔲 | Hard/soft limits, conflict detection |
| Metacognitive Monitor | Metacognition | 🔲 | Error pattern analysis, drift alerts |
| Session Replay | Feedback | 🔲 | Replay + failure analysis |

---

## License

SINT architecture: MIT
Individual components: see respective repos.
Owner model and personal data: private.

---

*"The goal is not to build a better chatbot. The goal is to build a system that thinks."*
