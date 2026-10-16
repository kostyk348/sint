# SINT — Structured Intelligence Network Topology

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-stdio_servers-blue)](https://modelcontextprotocol.io)
[![Release](https://img.shields.io/github/v/release/kostyk348/sint?sort=semver&color=blue)](https://github.com/kostyk348/sint/releases)
[![License](https://img.shields.io/badge/license-Apache-2.0-green)](https://github.com/kostyk348/sint/blob/main/LICENSE)
[![Last commit](https://img.shields.io/github/last-commit/kostyk348/sint?branch=main)](https://github.com/kostyk348/sint/commits/main)

> **Agents as systems, not chatbots with tools.**

SINT is an agent architecture built on a core thesis: an agent is not a language model with function calling bolted on. It is a **cognitive system** with seven independent, replaceable layers — each with its own data structures, persistence model, and verification protocol.

This monorepo contains the entire SINT ecosystem: 11 MCP servers, the core memory system, agent definitions, skills, and architecture documentation.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [The Seven Cognitive Layers](#the-seven-cognitive-layers)
- [MCP Servers](#mcp-servers)
- [Agent System](#agent-system)
- [Memory System](#memory-system)
- [Skills](#skills)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Design Principles](#design-principles)
- [Project Status](#project-status)
- [Roadmap](#roadmap)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SINT OS                                        │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  PERCEPTION — what I see                                            │   │
│  │    mcp/re-graph      Binary → semantic graph (RE intelligence)      │   │
│  │    mcp/spec          RFCs + binary formats → structured knowledge   │   │
│  │    mcp/algo          Algorithms, papers, patents → queryable index  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  COGNITION — how I think                                            │   │
│  │    mcp/devflow       Pipelines, TDD, code style, commit conv.      │   │
│  │    mcp/crypto        Cipher DB + pattern detection + test vectors   │   │
│  │    mcp/embed         MCU database, RTOS patterns, code gen          │   │
│  │    [planned]         Analogy Engine, Adversarial reasoning          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  MEMORY — what I know                                               │   │
│  │    mcp/working       Task state, findings, beliefs (disk-based)     │   │
│  │    core/memory       Hash-chain blocks, temporal decay, provenance  │   │
│  │    mcp/historian     Cross-session analytics, drift detection       │   │
│  │    mcp/self          Vector character DB, identity recall           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  FEEDBACK — how I learn                                             │   │
│  │    mcp/learner       Error patterns, improvements, pre-session check│   │
│  │    mcp/portfolio     Cross-project knowledge links, transfer        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  IDENTITY — who I am                                                │   │
│  │    mcp/self          Character calibration, owner model             │   │
│  │    AGENTS.MD         Invariants, semantic registers, verification   │   │
│  │    core/skills/      Owner model, specialized behaviors             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ACTION — what I do                                                 │   │
│  │    Native tools      Read, write, edit, bash, web (not MCP)         │   │
│  │    core/bin/         CLI utilities (sint-drift, sint-decay, etc.)   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  METACOGNITION — how I think about thinking                         │   │
│  │    mcp/working       Epistemic state (beliefs + confidence)         │   │
│  │    mcp/historian     Drift detection, register distribution         │   │
│  │    mcp/learner       Error pattern detection, calibration           │   │
│  │    [planned]         Constraint tracker, metacognitive monitor      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## The Seven Cognitive Layers

SINT is built on seven cognitive layers, each independent and replaceable:

### 1. PERCEPTION — what I see

The agent's sensory apparatus. Raw input is converted to structured, queryable knowledge before cognition begins.

| Component | What it does | Status |
|---|---|---|
| **RE Graph** | Breaks binaries into data blocks + operations, represents as vector-embedded graph | ✅ |
| **Spec Base** | Fetches RFCs and format specs, caches locally, hybrid search | ✅ |
| **Algo Base** | Searches Rosetta Code, papers, patents, docs with era filtering | ✅ |
| Log Parser | Events → correlated timeline (structured logging) | 🔲 Planned |

### 2. COGNITION — how I think

Reasoning engines that operate on perceived knowledge.

| Component | What it does | Status |
|---|---|---|
| **Devflow** | Pipeline planning, code review, TDD guidance, commit conventions | ✅ |
| **Crypto** | Cipher identification, test vector validation, code generation | ✅ |
| **Embed** | MCU database, RTOS recommendations, linker/startup code gen | ✅ |
| **Adversarial** | Attacks own conclusions (partially via sint-critic agent) | ✅ Partial |
| **Planner** | Multi-step reasoning chains (in devflow pipelines) | ✅ Partial |
| Analogy Engine | Cross-domain structural mapping | 🔲 Planned |

### 3. MEMORY — what I know

Not storage. **Knowledge management** — typed, linked, temporal, provenanced, queryable.

| Component | What it does | Status |
|---|---|---|
| **Working Memory** | Task state, findings, beliefs — disk-based, ~200 tokens per query | ✅ |
| **Session Memory** | Hash-chain blocks with SHA-256 provenance | ✅ |
| **Long-term Memory** | Decay-weighted knowledge blocks (30-day half-life) | ✅ |
| **Semantic Memory** | Vector embeddings for identity and character recall | ✅ |
| **Historian** | Cross-session analytics, drift detection, work reports | ✅ |

### 4. ACTION — what I do

Native agent capabilities (not MCP servers — these are the agent's hands).

- **Code**: read, write, edit files
- **Files**: filesystem operations
- **Network**: HTTP, git, APIs
- **Communication**: user interaction

### 5. METACOGNITION — how I think about thinking

The agent's self-awareness layer. Without it, the agent cannot detect when it's wrong.

| Component | What it does | Status |
|---|---|---|
| **Epistemic State** | Beliefs with confidence, contradiction detection | ✅ |
| **Drift Detection** | Register distribution monitoring, anomaly alerts | ✅ |
| **Error Patterns** | Repeated mistake detection, anti-pattern generation | ✅ |
| **Calibration** | Pre-session check: "what NOT to repeat" | ✅ |
| **Constraint Tracker** | Hard/soft limits, conflict detection | 🔲 Planned |
| **Metacognitive Monitor** | Error pattern analysis, drift alerts | 🔲 Planned |

### 6. IDENTITY — who I am

Not a persona. **Operative calibration** — vector-encoded, owner-aligned, context-sensitive.

| Component | What it does | Status |
|---|---|---|
| **Character DB** | Vector-indexed behavioral notes, semantic recall | ✅ |
| **Owner Model** | Values, preferences, anti-patterns from owner skill | ✅ |
| **Values** | Ethical framework, priorities (in AGENTS.MD) | ✅ Partial |

### 7. FEEDBACK — how I learn

Without feedback loops, the agent repeats the same mistakes forever.

| Component | What it does | Status |
|---|---|---|
| **Session Logging** | Record what happened, errors, findings | ✅ |
| **Error Patterns** | Auto-detect repeated mistakes across sessions | ✅ |
| **Improvements** | Track what got better and why | ✅ |
| **Pre-session Check** | "What should I remember NOT to do?" | ✅ |
| **Portfolio** | Cross-project knowledge links, transfer suggestions | ✅ |
| Session Replay | "Where did this session go wrong?" | 🔲 Planned |

---

## MCP Servers

### Perception

| Server | Directory | Description | Key Tools |
|---|---|---|---|
| **re-graph** | `mcp/re-graph/` | Semantic binary graph for reverse engineering | `build_graph`, `query_semantic`, `trace_forward`, `trace_backward`, `find_patterns` |
| **spec** | `mcp/spec/` | RFC + binary/container format specifications | `get_rfc`, `describe_format`, `search_spec` |
| **algo** | `mcp/algo/` | Algorithm knowledge (Rosetta, papers, patents) | `search_algorithm`, `get_paper`, `get_patent`, `get_implementations` |

### Cognition

| Server | Directory | Description | Key Tools |
|---|---|---|---|
| **devflow** | `mcp/devflow/` | Dev workflow intelligence | `plan_feature`, `code_review`, `tdd_guide`, `discover_edge_cases` |
| **crypto** | `mcp/crypto/` | Cipher database + pattern detection | `search_cipher`, `get_test_vectors`, `detect_cipher`, `generate_code` |
| **embed** | `mcp/embed/` | Embedded systems specialist | `get_mcu`, `recommend_rtos`, `gen_linker_script`, `gen_startup` |

### Memory

| Server | Directory | Description | Key Tools |
|---|---|---|---|
| **working** | `mcp/working/` | Working memory + epistemic state | `get_state`, `add_finding`, `add_belief`, `contradict`, `get_weakest_beliefs` |
| **historian** | `mcp/historian/` | Cross-session work analyst | `session_stats`, `work_report`, `drift_analysis` |
| **self** | `mcp/self/` | Agent identity vector DB | `self_recall`, `self_teach`, `self_seed`, `self_identity` |

### Feedback

| Server | Directory | Description | Key Tools |
|---|---|---|---|
| **learner** | `mcp/learner/` | Cross-session learning | `log_error`, `get_repeated`, `detect_error_patterns`, `pre_session_check` |
| **portfolio** | `mcp/portfolio/` | Project portfolio + knowledge links | `add_project`, `add_link`, `find_transfer`, `get_portfolio_summary` |

### Core

| Server | Directory | Description | Key Tools |
|---|---|---|---|
| **sint-memory** | `core/mcp/sint-memory/` | Hash-chain structured memory | `memory_write_block`, `memory_read_blocks`, `memory_verify_chain`, `memory_apply_decay` |

### Planned

| Server | Directory | Description | Status |
|---|---|---|---|
| **analogy** | `mcp/analogy/` | Cross-domain structural mapping | 🔲 Planned |
| **constraints** | `mcp/constraints/` | Hard/soft limit tracker | 🔲 Planned |
| **metacog** | `mcp/metacog/` | Metacognitive monitor | 🔲 Planned |
| **replay** | `mcp/replay/` | Session replay + failure analysis | 🔲 Planned |
| **logparser** | `mcp/logparser/` | Event log → correlated timeline | 🔲 Planned |

---

## Agent System

SINT uses a multi-agent architecture with four specialized roles:

### Agent Roles

| Agent | Mode | Purpose | Model |
|---|---|---|---|
| **sint-main** | primary | Task classification, delegation, session lifecycle | Session model |
| **sint-critic** | subagent | Independent verification, register audits | Session model |
| **sint-scribe** | subagent | Memory management, hash-chain maintenance | Session model |
| **sint-router** | subagent | Task classification, skill recommendation | Session model |

> **No hardcoded models.** All agents use the model selected for the current session. This ensures consistency and allows model upgrades without agent config changes.

### Agent Flow

```
User input
    ↓
sint-main (primary)
    ├─ Reads memory state (sint-memory)
    ├─ Classifies task (register + domain)
    ├─ Loads relevant skills
    ├─ Delegates to specialist agents
    │   ├─ sint-critic (verification tasks)
    │   ├─ sint-scribe (memory tasks)
    │   └─ general (implementation tasks)
    └─ Manages session lifecycle
```

### Semantic Registers

Every output belongs to exactly one register:

| Register | Definition | Requirement |
|---|---|---|
| **SENSE** | Raw data, observation, user input | No interpretation |
| **FACT** | Verifiable claim about the world | Source required |
| **LOGIC** | Deductive inference from FACT/SENSE | Premises explicit |
| **OPINION** | Subjective assessment | Actor declared |
| **CAUSALITY** | Action plan, execution chain | Steps follow from prior |

---

## Memory System

The memory system (`core/memory/`) is SINT's knowledge management infrastructure.

### Architecture

```
┌─────────────────────────────────────────────────┐
│              MEMORY SYSTEM                       │
│                                                  │
│  ┌──────────────┐  ┌──────────────────────────┐ │
│  │ State File    │  │ Block Store               │ │
│  │ focus[]       │  │ blocks/0000.sense.json    │ │
│  │ pending[]     │  │ blocks/0001.fact.json     │ │
│  │ last_session  │  │ blocks/0002.logic.json    │ │
│  └──────────────┘  │ ...                        │ │
│                     └──────────────────────────┘ │
│  ┌──────────────┐  ┌──────────────────────────┐ │
│  │ Chain File    │  │ Session Logs              │ │
│  │ chain.jsonl   │  │ sessions/2026-07-22.jsonl │ │
│  │ (hash-linked) │  │ ...                        │ │
│  └──────────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

### Key Features

- **Hash-chain provenance**: Every block links to the previous via SHA-256 hash. Tampering breaks the chain.
- **Temporal decay**: Blocks lose relevance over time (30-day half-life). Active knowledge stays hot.
- **Register typing**: SENSE, FACT, LOGIC, OPINION, ACTION — each with different verification requirements.
- **Drift detection**: Monitors register distribution. Alerts if too many OPINIONs or too few FACTs.
- **Provenance archaeology**: Trace any conclusion back to its genesis block.
- **Git integration**: Link memory blocks to commits for cross-referencing.

### Tools

| Tool | Description |
|---|---|
| `memory_write_block` | Write a new block to the hash chain |
| `memory_read_blocks` | Read recent blocks (filtered by register/project) |
| `memory_read_state` | Read current focus and pending decisions |
| `memory_update_state` | Update focus, pending decisions, last session |
| `memory_verify_chain` | Verify hash chain integrity |
| `memory_apply_decay` | Apply temporal decay, return relevance scores |
| `memory_heat_block` | Mark block as recently accessed (7-day boost) |
| `memory_search` | Full-text + register + tag search |
| `memory_drift_check` | Check register distribution anomalies |
| `memory_trace_provenance` | Trace block back to genesis |
| `memory_stats` | Block count, register distribution, chain length |
| `memory_get_chain_tail` | Last N chain entries |

---

## Skills

Skills provide specialized instructions for specific tasks:

| Skill | Purpose | Location |
|---|---|---|
| **agents** | Multi-agent systems, orchestration, pipelines | `core/skills/agents/` |
| **dso** | DSO, MPTC, DataTrace, deterministic systems | `core/skills/dso/` |
| **memory-system** | Structured memory blocks, hash-chain audit | `core/skills/memory-system/` |
| **owner** | Owner model, decision style, preferences | `core/skills/owner/` |
| **state** | Session management, project status tracking | `core/skills/state/` |
| **wiki** | Artifact registry, cross-references | `core/skills/wiki/` |

---

## Quick Start

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# Clone the monorepo

git clone https://github.com/kostyk348/sint.git
cd sint

# Install core dependencies

pip install -r requirements.txt
```

### Running an MCP Server

Each MCP server runs independently via stdio. Verified on a clean clone (2026-10-15) with the core
dependency installed: `cd mcp/crypto && python server.py` boots `FastMCP 4.1.0 — sint-crypto-mcp`
and listens on stdio.

```bash
# Perception

cd mcp/algo && python server.py
cd mcp/spec && python server.py
cd mcp/re-graph && python server.py

# Cognition

cd mcp/devflow && python server.py
cd mcp/crypto && python server.py
cd mcp/embed && python server.py

# Memory

cd mcp/working && python server.py
cd mcp/historian && python server.py
cd mcp/self && python server.py

# Feedback

cd mcp/learner && python server.py
cd mcp/portfolio && python server.py

# Core

cd core/mcp/sint-memory && python server.py
```

### Using with OpenCode

The primary integration is via [OpenCode](https://opencode.ai). Configure in `opencode.jsonc`:

```jsonc
{
  "default_agent": "sint-main",
  "mcp": {
    "sint-memory": {
      "type": "local",
      "command": ["python", "path/to/sint/core/mcp/sint-memory/server.py"],
      "env": {
        "SINT_MEMORY_DIR": "~/.config/opencode/memory"
      }
    }
    // Add other MCP servers as needed
  }
}
```

---

## Configuration

### MCP Servers

Each MCP server has a `config.py` with:
- `NAME` — server name for MCP protocol
- `CACHE_DIR` — local cache path
- Source-specific settings

### Memory System

Environment variable:
- `SINT_MEMORY_DIR` — where memory blocks, sessions, and chain live

Default: `~/.config/opencode/memory`

### Agent Definitions

Agent behavior is defined in `core/agents/`:
- `sint-main.md` — primary orchestrator
- `sint-critic.md` — verification agent
- `sint-scribe.md` — memory agent
- `sint-router.md` — task classifier

---

## Design Principles

1. **Semantic registers** — every output is SENSE, FACT, LOGIC, OPINION, or CAUSALITY
2. **Provenance** — traceable chain of reasoning, no sourceless claims
3. **Uncertainty surfaced** — low confidence stated explicitly, not buried
4. **Character calibration** — agent identity via vector recall, not static prompts
5. **Memory as infrastructure** — structured blocks, not flat context windows
6. **No hardcoded models** — agents use the session's selected model
7. **Independent layers** — each cognitive layer is replaceable without affecting others
8. **Feedback loops** — the agent learns from its mistakes across sessions

---

## Project Status

| Component | Layer | Status | Notes |
|---|---|---|---|
| **sint-memory** | Memory | ✅ v2.1 | Hash-chain, temporal decay, drift detection, provenance archaeology |
| **sint-self-mcp** | Identity | ✅ | Vector character DB, semantic recall, owner model |
| **sint-spec-mcp** | Perception | ✅ | RFC + format specs, hybrid search |
| **sint-algo-mcp** | Perception | ✅ | Rosetta Code, papers, patents, docs |
| **sint-re-graph-mcp** | Perception | ✅ | Semantic binary graph + DataTrace taint |
| **sint-devflow-mcp** | Cognition | ✅ | Pipeline + modular style (C/Python/Rust) + TDD |
| **sint-crypto-mcp** | Cognition | ✅ | 25+ ciphers, test vectors, pattern detection |
| **sint-embed-mcp** | Cognition | ✅ | MCU database, RTOS patterns, code gen |
| **sint-working-mcp** | Memory | ✅ | Task state, findings, beliefs, epistemic state |
| **sint-historian-mcp** | Memory | ✅ | Session analytics, drift detection, work reports |
| **sint-learner-mcp** | Feedback | ✅ | Error patterns, improvements, pre-session check |
| **sint-portfolio-mcp** | Feedback | ✅ | Project portfolio, knowledge transfer links |
| **sint-critic** | Metacognition | ✅ | Register audits, fact-checking, code review |
| **sint-main** | — | ✅ | Primary orchestrator |
| **sint-scribe** | — | ✅ | Memory management agent |
| **sint-router** | — | ✅ | Task classification agent |
| **Log Parser** | Perception | 🔲 | Events → correlated timeline |
| **Analogy Engine** | Cognition | 🔲 | Cross-domain structural mapping |
| **Constraint Tracker** | Metacognition | 🔲 | Hard/soft limits, conflict detection |
| **Metacognitive Monitor** | Metacognition | 🔲 | Error pattern analysis, drift alerts |
| **Session Replay** | Feedback | 🔲 | Replay + failure analysis |

---

## Roadmap

### Phase 1: Core (Complete)

- [x] Hash-chain memory system
- [x] Vector identity DB
- [x] Multi-agent architecture
- [x] Semantic register system

### Phase 2: Knowledge (Complete)

- [x] Algorithm knowledge base
- [x] RFC + format specs
- [x] Binary graph (RE)
- [x] Cipher database
- [x] Embedded systems DB

### Phase 3: Intelligence (Complete)

- [x] Working memory + epistemic state
- [x] Cross-session learning
- [x] Project portfolio
- [x] Drift detection

### Phase 4: Metacognition (Planned)

- [ ] Analogy engine (cross-domain mapping)
- [ ] Constraint tracker (hard/soft limits)
- [ ] Metacognitive monitor (error pattern analysis)
- [ ] Session replay (failure analysis)

### Phase 5: Integration (Planned)

- [ ] Log parser (events → timeline)
- [ ] Cross-MCP orchestration
- [ ] Automated feedback loops
- [ ] Performance benchmarks

---

## Links

- [SINT Manifesto](docs/) — architecture philosophy
- [AGENTS.MD](AGENTS.MD) — operational invariants
- [OpenCode](https://opencode.ai) — primary runtime

## License

Apache 2.0 — see [LICENSE](LICENSE)
