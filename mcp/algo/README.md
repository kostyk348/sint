# sint-algo-mcp

Unified algorithm knowledge MCP server for the [SINT](https://github.com/kostyk348/sint-ua-v2.1) agent ecosystem.

Searches algorithms, ideas, papers, patents, and documentation across multiple sources with a local hybrid cache.

## Sources

| Source | Content | Method |
|---|---|---|
| **Rosetta Code** | Algorithm implementations in 40+ languages | Scrape + local cache |
| **GitHub** | Trending repos, code patterns | GitHub API |
| **Papers** | arXiv + Semantic Scholar | Academic API |
| **Patents** | PatentsView + Google Patents | Patent API |
| **Docs** | Library/middleware documentation | Web scrape + LLM distill |
| **Docs-Tools** | Android, PS Vita, Ghidra, Linux kernel | Specialized scrapers |

## Tools

| Tool | Description |
|---|---|
| `search_algorithm(query, source, era_min, era_max)` | Unified search across all sources |
| `get_implementations(name, lang)` | Code implementations for a Rosetta Code task |
| `get_paper(query, era_min, era_max)` | Academic papers with era filter |
| `get_patent(query)` | Patent search for commercial/historical ideas |
| `describe_middleware(query)` | Distilled docs for libraries and tools |
| `ingest(source, limit, query)` | Grow the local cache at runtime |
| `add_note(name, note, refs)` | Persist agent/user notes across sessions |
| `stats()` | Cache statistics per source |

### Era Filter

Use `era_min`/`era_max` to surface forgotten ideas:

```
search_algorithm("hash table", era_min=1950, era_max=1990)
```

Returns pre-hash-table-optimization era implementations — Knuth-era techniques.

## Architecture

```
Query → Index (SQLite FTS5) → Source modules → Response
                ↓
         fastembed vectors (BAAI/bge-small-en-v1.5)
                ↓
         Hybrid search: keyword + semantic
```

## Setup

```bash
pip install fastmcp httpx sqlite-utils fastembed numpy
```

## Run

```bash
python server.py          # stdio mode
fastmcp run server.py     # via fastmcp CLI
```

## Configuration

Edit `config.py`:
- `CACHE_DIR` — local cache path
- `SOURCES` — enabled sources list
- `ERA_MIN`/`ERA_MAX` — default paper search range

## First Run

```python
# Seed the index with Rosetta Code algorithms
ingest(source="rosetta", limit=100)

# Search
search_algorithm("quick sort")
search_algorithm("ray casting", source="papers")
```

## Integration

This MCP server is designed for the [SINT](https://github.com/kostyk348/sint-ua-v2.1) agent but works standalone with any MCP-compatible client.

## License

MIT
