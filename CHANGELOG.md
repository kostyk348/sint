# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

No tagged releases yet — the entries below are reconstructed from `git log`
(first commit `17de015`, 2026-07-22) and grouped by kind of change.

## [Unreleased]

### Added

- **Monorepo migration** (`17de015`): the SINT ecosystem moved from 10 separate repositories into one
  tree — MCP servers across the perception / cognition / memory / feedback layers, core memory system,
  agent definitions (`core/agents`), skills (`core/skills`), architecture docs, and the `core/bin` CLI
  utilities (`sint`, `sint-drift`, `sint-decay`, `sint-embeddings`, `sint-archaeology`, `sint-git`,
  `sint-tmux`) with `core/Makefile` and slash commands (`core/commands`).
- **`mcp/working`** — working memory plus epistemic state (beliefs with confidence) (`064e7ef`).
- **`mcp/learner`** — error-pattern detection and pre-session calibration (`5c1388c`).
- **`mcp/portfolio`** — cross-project knowledge links and transfer suggestions (`5c1388c`).
- **README of the monorepo** — seven cognitive layers, MCP server map, memory system, agent system,
  skills, design principles, status and roadmap; plus a manifesto update (`5c1388c`).
- **Server placeholders with specs** for planned components: `analogy`, `constraints`, `logparser`,
  `metacog`, `replay` (`5c1388c`).
- `LICENSE` and `.gitignore` (`17de015`).

### Changed

- Documentation reworked for the full ecosystem: root `README.md` and `docs/README.md` (`5c1388c`).
- License switched to **Apache 2.0** (patent clause, attribution, royalty-friendly) (`66b5cba`).
- README badges added (license, Python version, MCP) — follow-up to `66b5cba`.

### Notes

- `tests/` is empty (only `.gitkeep`); there is no CI workflow, because there is nothing honest to run
  yet. First tests, then CI — see `BEAUTY.md`.
