# sint-re-graph-mcp

Semantic Binary Graph — reverse engineering intelligence layer for the sint agent.

Breaks binaries into **data blocks** and **operations**, represents them as a
**vector-embedded graph**. The agent queries the graph semantically instead of
reading thousands of lines of disassembly.

## Architecture

```
binary → extractors → NetworkX graph → fastembed vectors → SQLite
                         ↕
              DataTrace taint flow (dynamic)
```

## Tools

| Tool | Description |
|---|---|
| `build_graph(path)` | Analyze binary, build semantic graph |
| `import_datatrace(graph, jsonl)` | Add DataTrace taint flow |
| `query_semantic(query)` | Find nodes by semantic similarity |
| `trace_forward(node)` | Trace data flow forward |
| `trace_backward(node)` | Trace data to origins |
| `find_patterns(graph)` | Detect known crypto/protocol patterns |
| `get_delta(before, after)` | Compare two data states |
| `summarize(graph)` | Linguistic summary |
| `get_subgraph(center, radius)` | Neighborhood extraction |
| `export_graph(graph, format)` | Export for visualization |
| `list_graphs()` | List cached graphs |
| `save_graph(graph)` / `load_graph(name)` | Persistence |

## Setup

```bash
pip install fastmcp networkx fastembed numpy lief
```

## Run

```bash
python server.py  # stdio mode
```

## DataTrace Integration

Import taint flow from DataTrace JSONL:

```python
import_datatrace("my_binary", "/path/to/events.jsonl")
```

Adds edges for: network → buffer → memcpy → sendto chains.
Shows which untrusted data reaches sinks.

## Design Principles

- **Semantic compression**: agent sees 50 graph nodes, not 2000 asm lines
- **Dynamic + Static**: DataTrace gives runtime flow, extractors give code structure
- **Embeddings**: every node has a 384-dim vector for semantic search
- **Persistence**: graphs survive across sessions via SQLite

## Dependencies

- `fastmcp` — MCP server framework
- `networkx` — graph operations
- `fastembed` — local embeddings (BAAI/bge-small-en-v1.5)
- `numpy` — vector math
- `lief` — ELF/PE/Mach-O parsing (optional, fallback to generic)

## License

MIT
