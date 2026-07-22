# SINT — Agent Ecosystem

Monorepo for the SINT agent: MCP servers, core memory system, and architecture docs.

> **SINT** = **S**tructured **I**ntelligence **N**etwork **T**opology  
> Agents as systems, not chatbots with tools.

## Architecture

```
sint/
├── mcp/                    ← MCP servers (the "organs")
│   ├── algo/               Algorithm knowledge base
│   ├── crypto/             Cipher database + pattern detection
│   ├── devflow/            Dev workflow intelligence
│   ├── embed/              Embedded systems specialist
│   ├── historian/          Cross-session work analyst
│   ├── re-graph/           Semantic binary graph (reverse eng)
│   ├── self/               Agent identity vector DB
│   └── spec/               RFC + format specifications
├── core/                   ← Memory system + agent runtime
│   ├── memory/             Hash-chain structured memory
│   ├── agents/             Agent definitions (main, scribe, critic, router)
│   ├── skills/             Specialized skills
│   ├── mcp/sint-memory/    Memory MCP server
│   ├── bin/                CLI tools (sint-drift, sint-decay, etc.)
│   └── plugin/             OpenCode plugin (sint-hooks)
├── docs/                   ← Architecture docs
│   └── README.md           SINT Manifesto
└── tests/                  ← Cross-component tests
```

## MCP Servers

| Server | Purpose | Key Tools |
|---|---|---|
| **algo** | Algorithm knowledge (Rosetta, papers, patents) | `search_algorithm`, `get_paper`, `get_patent` |
| **crypto** | Cipher DB + test vectors + code gen | `search_cipher`, `get_test_vectors`, `detect_cipher` |
| **devflow** | Pipeline planning, style, TDD | `plan_feature`, `code_review`, `tdd_guide` |
| **embed** | MCU database, RTOS patterns | `get_mcu`, `recommend_rtos`, `gen_linker_script` |
| **historian** | Session analytics, drift detection | `session_stats`, `work_report`, `drift_analysis` |
| **re-graph** | Semantic binary graph | `build_graph`, `query_semantic`, `trace_forward` |
| **self** | Agent identity/character recall | `self_recall`, `self_teach`, `self_seed` |
| **spec** | RFC + format specifications | `get_rfc`, `describe_format`, `search_spec` |

## Quick Start

```bash
# Clone
git clone https://github.com/kostyk348/sint.git
cd sint

# Install dependencies
pip install -r requirements.txt

# Run any MCP server
cd mcp/algo && python server.py    # stdio mode
cd mcp/crypto && python server.py
```

## Core: Memory System

The memory system (`core/`) provides:

- **Hash-chain blocks** — typed memory (SENSE/FACT/LOGIC/OPINION/ACTION) with SHA-256 provenance
- **Temporal decay** — blocks lose relevance over time unless heated
- **Drift detection** — monitor register distribution anomalies
- **Provenance archaeology** — trace any conclusion back to its genesis
- **Git integration** — link memory blocks to commits

See [`core/`](core/) for the full memory system.

## Agent Roles

| Role | Purpose |
|---|---|
| **sint-main** | Primary orchestrator — task classification, delegation, session management |
| **sint-scribe** | Memory management — read/write blocks, maintain hash-chain |
| **sint-critic** | Independent verification — register audits, fact-checking |
| **sint-router** | Task classification — semantic register, domain, skill recommendation |

## Design Principles

1. **Semantic registers** — every output is SENSE, FACT, LOGIC, OPINION, or ACTION
2. **Provenance** — traceable chain of reasoning, no sourceless claims
3. **Uncertainty surfaced** — low confidence stated explicitly, not buried
4. **Character calibration** — agent identity via vector recall, not static prompts
5. **Memory as infrastructure** — structured blocks, not flat context windows

## Links

- [SINT Manifesto](docs/) — architecture philosophy
- [Original repos](https://github.com/kostyk348?tab=repositories&q=sint) — pre-monorepo history

## License

MIT
