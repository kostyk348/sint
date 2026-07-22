# sint-spec-mcp

RFC and binary/container format specification MCP server for the [SINT](https://github.com/kostyk348/sint-ua-v2.1) agent ecosystem.

Local-first spec knowledge base with hybrid search (keyword + semantic embeddings).

## Sources

| Source | Content | Coverage |
|---|---|---|
| **RFC** | Internet standards (IETF) | Transport, HTTP, DNS, TLS, etc. |
| **Formats** | Binary/container format specs | ELF, PE, PNG, ZIP, MP4, etc. |

## Tools

| Tool | Description |
|---|---|
| `search_spec(query, source)` | Search spec index by title/name |
| `get_rfc(num)` | Fetch full RFC text (cached locally) |
| `describe_format(name)` | Format overview + authoritative spec URL |
| `ingest(source, query, limit)` | Grow the local cache |
| `add_note(name, note, refs)` | Persist agent/user spec notes |
| `stats()` | Cache statistics per source |

## Usage

### Find an RFC

```python
search_spec("TLS handshake")
search_spec("HTTP cookies", source="rfc")
get_rfc(8446)  # TLS 1.3
```

### Understand a Binary Format

```python
describe_format("ELF")    # → spec URL + Wikipedia overview
describe_format("PNG")    # → chunk structure + extensions
describe_format("ZIP")    # → local headers + compression methods
```

### Research Before Implementation

```python
# Before writing a parser:
describe_format("MP4")
# → get atom structure, box types, embedded codec info

# Before implementing a protocol:
get_rfc(7231)
# → full HTTP/1.1 semantics
```

## Architecture

```
Query → Index (SQLite FTS5) → Source fetchers → Response
                ↓
         fastembed vectors
                ↓
         Hybrid: keyword + semantic
                ↓
         Local cache (never re-fetch)
```

## Setup

```bash
pip install fastmcp httpx sqlite-utils fastembed
```

## Run

```bash
python server.py    # stdio mode
```

## Cache Growth

The index starts empty. Seed it:

```python
ingest(source="rfc", query="transport", limit=20)
ingest(source="formats", query="executable", limit=10)
```

Subsequent searches hit the local cache — no network needed.

## Integration

Designed for the [SINT](https://github.com/kostyk348/sint-ua-v2.1) agent. Use before writing parsers, protocol implementations, or format converters.

## License

MIT
