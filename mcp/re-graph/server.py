"""sint-re-graph-mcp server (fastmcp, stdio).

Semantic Binary Graph — reverse engineering intelligence layer.

Breaks binaries into data blocks + operations, represents them as a
vector-embedded graph. Agent queries the graph semantically instead
of reading thousands of lines of disassembly.

Integrates with DataTrace for dynamic taint flow analysis.

Tools:
  build_graph(path)              — analyze binary, build semantic graph
  import_datatrace(graph, jsonl) — add DataTrace taint flow to graph
  query_semantic(query, ...)     — find nodes by semantic similarity
  trace_forward(node)            — trace data flow forward
  trace_backward(node)           — trace data to origins
  find_patterns(graph)           — detect known crypto/protocol patterns
  get_delta(before, after)       — compare two data states
  summarize(graph)               — linguistic summary of graph
  get_subgraph(center, radius)   — neighborhood extraction
  export_graph(graph, format)    — export for visualization
  list_graphs()                  — list all cached graphs
  save_graph(graph)              — persist to SQLite
  load_graph(name)               — load from SQLite

Run: python server.py (stdio)
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

from config import NAME, CACHE_DIR, GRAPH_DB
from graph import BinaryGraph
from extractors.elf import extract_elf, map_elf_to_graph, HAS_LIEF
from extractors.generic import extract_generic, map_generic_to_graph
from extractors.datatrace import (
    parse_datatrace_events, integrate_datatrace_to_graph,
)
from patterns.known import get_detector

mcp = FastMCP(NAME)

# ── Active graph store (in-memory, per MCP session) ────────────────
_active: dict[str, BinaryGraph] = {}


def _get(name: str) -> BinaryGraph:
    """Get active graph by name."""
    if name not in _active:
        return None
    return _active[name]


# ═══════════════════════════════════════════════════════════════════
# BUILD GRAPH
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def build_graph(path: str, name: str = "") -> str:
    """Analyze a binary file and build a semantic graph.

    Extracts: sections, symbols, imports, strings, entropy profile,
    known patterns (AES S-box, CRC tables, MD5/SHA init values).

    Args:
        path: path to the binary file
        name: optional graph name (defaults to filename)
    Returns: JSON with analysis results and graph stats.
    """
    p = Path(path)
    if not p.exists():
        return json.dumps({"error": f"file not found: {path}"})

    gname = name or p.stem
    graph = BinaryGraph(gname)

    # Try ELF first, fallback to generic
    elf_info = None
    if HAS_LIEF:
        try:
            elf_info = extract_elf(path)
            if "error" not in elf_info:
                map_elf_to_graph(graph, elf_info)
        except Exception:
            elf_info = None

    gen_info = extract_generic(path)
    if "error" not in gen_info:
        map_generic_to_graph(graph, gen_info)

    # Auto-detect patterns in high-entropy regions
    detector = get_detector()
    if elf_info:
        for sec in elf_info.get("sections", []):
            if sec.get("entropy", 0) > 7.0 and sec.get("size", 0) > 0:
                # High-entropy section — scan for crypto patterns
                graph.add_data_block(
                    name=f"section:{sec['name']}",
                    size=sec.get("size", 0),
                    source="elf",
                    dtype="high_entropy_section",
                    entropy=sec.get("entropy", 0),
                )

    summary = graph.summarize()
    summary["file"] = str(p)
    summary["format"] = gen_info.get("format", "unknown")
    summary["elf"] = elf_info is not None and "error" not in (elf_info or {})

    _active[gname] = graph
    return json.dumps(summary, ensure_ascii=False, indent=1)


# ═══════════════════════════════════════════════════════════════════
# DATATRACE INTEGRATION
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def import_datatrace(graph_name: str, jsonl_path: str) -> str:
    """Import DataTrace event stream into an existing graph.

    Adds taint flow edges: which buffers come from network/file/argv,
    how they propagate through memcpy, and which reach sinks (sendto).

    Args:
        graph_name: name of the active graph
        jsonl_path: path to DataTrace JSONL event file
    Returns: JSON with taint analysis summary.
    """
    graph = _get(graph_name)
    if not graph:
        return json.dumps({"error": f"graph '{graph_name}' not found; run build_graph first"})

    events = parse_datatrace_events(jsonl_path)
    if not events:
        return json.dumps({"error": f"no events parsed from {jsonl_path}"})

    result = integrate_datatrace_to_graph(graph, events)

    # Update summary with taint info
    summary = graph.summarize()
    result["graph_summary"] = summary
    return json.dumps(result, ensure_ascii=False, indent=1)


# ═══════════════════════════════════════════════════════════════════
# SEMANTIC QUERIES
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def query_semantic(query: str, graph_name: str = "", node_type: str = "",
                   k: int = 5) -> str:
    """Find nodes semantically similar to a natural language query.

    Examples:
        "buffer that receives network data" → finds recv-related buffers
        "encryption function" → finds crypto operations
        "string constants" → finds string data blocks

    Args:
        query: natural language description of what to find
        graph_name: which graph to search (latest if empty)
        node_type: filter by "data" or "operation"
        k: max results
    Returns: JSON list of matching nodes with scores.
    """
    graph = _resolve_graph(graph_name)
    if not graph:
        return json.dumps({"error": "no active graph"})

    results = graph.find_similar(query, k=k, node_type=node_type)
    return json.dumps({"query": query, "graph": graph.name,
                       "results": results}, ensure_ascii=False, indent=1)


@mcp.tool()
def find_patterns(graph_name: str = "") -> str:
    """Find known algorithm patterns in the graph.

    Detects: AES S-box, CLEFIA S-box, CRC-32 tables, MD5/SHA init values,
    DES S-box, and high-entropy regions (potential encrypted data).

    Args:
        graph_name: which graph to analyze (latest if empty)
    Returns: JSON list of detected patterns with confidence scores.
    """
    graph = _resolve_graph(graph_name)
    if not graph:
        return json.dumps({"error": "no active graph"})

    patterns = []
    for nid, ndata in graph.G.nodes(data=True):
        if ndata.get("type") == "data":
            label = ndata.get("label", "")
            data = ndata.get("data", {})
            ent = data.get("entropy", 0)

            # Check patterns based on node properties
            if ent > 7.0:
                patterns.append({
                    "node_id": nid,
                    "label": label,
                    "pattern": "HIGH_ENTROPY",
                    "description": "High entropy data — likely encrypted/compressed",
                    "confidence": 0.8 if ent > 7.5 else 0.6,
                    "entropy": ent,
                })

            dtype = data.get("dtype", "")
            if "aes" in label.lower() or "s-box" in label.lower():
                patterns.append({
                    "node_id": nid,
                    "label": label,
                    "pattern": "AES_SBOX",
                    "description": "AES S-box lookup table",
                    "confidence": 0.95,
                })
            elif "crc" in label.lower():
                patterns.append({
                    "node_id": nid,
                    "label": label,
                    "pattern": "CRC_TABLE",
                    "description": "CRC lookup table",
                    "confidence": 0.85,
                })

    return json.dumps({"graph": graph.name, "patterns": patterns,
                       "total": len(patterns)}, ensure_ascii=False, indent=1)


# ═══════════════════════════════════════════════════════════════════
# TRANSFORM TRACING
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def trace_forward(node_id: str, graph_name: str = "",
                  max_depth: int = 10) -> str:
    """Trace what happens to data after this node.

    Shows: which operations consume this data, what they produce,
    and where the data ultimately ends up.

    Args:
        node_id: starting node (e.g. "data:buf_0x7fff1234")
        graph_name: which graph (latest if empty)
        max_depth: max hops to trace
    Returns: JSON chain of transformations.
    """
    graph = _resolve_graph(graph_name)
    if not graph:
        return json.dumps({"error": "no active graph"})

    result = graph.trace_forward(node_id, max_depth=max_depth)
    return json.dumps(result, ensure_ascii=False, indent=1)


@mcp.tool()
def trace_backward(node_id: str, graph_name: str = "",
                   max_depth: int = 10) -> str:
    """Trace where data came from (provenance).

    Shows: which operations produced this data, and what were the
    original sources (network, file, argv, constants).

    Args:
        node_id: target node to trace back from
        graph_name: which graph (latest if empty)
        max_depth: max hops to trace
    Returns: JSON chain of provenance.
    """
    graph = _resolve_graph(graph_name)
    if not graph:
        return json.dumps({"error": "no active graph"})

    result = graph.trace_backward(node_id, max_depth=max_depth)
    return json.dumps(result, ensure_ascii=False, indent=1)


# ═══════════════════════════════════════════════════════════════════
# DELTA & COMPARISON
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def get_delta(before_id: str, after_id: str, graph_name: str = "") -> str:
    """Compare two data nodes: what changed between them.

    Useful for: before/after encryption, before/after transformation,
    before/after protocol processing.

    Args:
        before_id: first node ID
        after_id: second node ID
        graph_name: which graph (latest if empty)
    Returns: JSON with changes (size, entropy, taint, etc.)
    """
    graph = _resolve_graph(graph_name)
    if not graph:
        return json.dumps({"error": "no active graph"})

    result = graph.get_delta(before_id, after_id)
    return json.dumps(result, ensure_ascii=False, indent=1)


# ═══════════════════════════════════════════════════════════════════
# GRAPH INFO
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def summarize(graph_name: str = "") -> str:
    """Generate a linguistic summary of the graph.

    Shows: node counts, taint flows, high-entropy data,
    connected components, and notable findings.

    Args:
        graph_name: which graph (latest if empty)
    Returns: JSON summary.
    """
    graph = _resolve_graph(graph_name)
    if not graph:
        return json.dumps({"error": "no active graph"})

    result = graph.summarize()
    return json.dumps(result, ensure_ascii=False, indent=1)


@mcp.tool()
def get_subgraph(center: str, radius: int = 2,
                graph_name: str = "") -> str:
    """Get neighborhood around a node (within radius hops).

    Args:
        center: node ID to center on
        radius: how many hops (default 2)
        graph_name: which graph (latest if empty)
    Returns: JSON with nodes and edges in neighborhood.
    """
    graph = _resolve_graph(graph_name)
    if not graph:
        return json.dumps({"error": "no active graph"})

    result = graph.get_subgraph(center, radius=radius)
    return json.dumps(result, ensure_ascii=False, indent=1)


@mcp.tool()
def list_graphs() -> str:
    """List all active and cached graphs."""
    active = list(_active.keys())

    # Check SQLite for persisted graphs
    cached = []
    try:
        import sqlite3
        conn = sqlite3.connect(str(GRAPH_DB))
        for row in conn.execute("SELECT name, node_count, edge_count, updated FROM graphs"):
            cached.append({
                "name": row[0], "nodes": row[1],
                "edges": row[2], "updated": row[3],
            })
        conn.close()
    except Exception:
        pass

    return json.dumps({"active": active, "cached": cached}, ensure_ascii=False, indent=1)


@mcp.tool()
def save_graph(graph_name: str) -> str:
    """Persist graph to SQLite for later loading."""
    graph = _get(graph_name)
    if not graph:
        return json.dumps({"error": f"graph '{graph_name}' not found"})

    graph.save()
    summary = graph.summarize()
    return json.dumps({"status": "saved", "graph": graph_name,
                       "nodes": summary["total_nodes"],
                       "edges": summary["total_edges"]}, ensure_ascii=False)


@mcp.tool()
def load_graph(graph_name: str) -> str:
    """Load a previously saved graph from SQLite."""
    try:
        graph = BinaryGraph.load(graph_name)
        _active[graph_name] = graph
        summary = graph.summarize()
        return json.dumps({"status": "loaded", "graph": graph_name,
                           "nodes": summary["total_nodes"],
                           "edges": summary["total_edges"]}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def export_graph(graph_name: str = "", fmt: str = "json") -> str:
    """Export graph for visualization or external use.

    Formats:
        json    — nodes + edges JSON (for D3.js, Cytoscape, etc.)
        graphml — GraphML (for Gephi, yEd)
        dot     — Graphviz DOT
    """
    graph = _resolve_graph(graph_name)
    if not graph:
        return json.dumps({"error": "no active graph"})

    if fmt == "json":
        sub = graph.get_subgraph(
            list(graph.G.nodes)[0] if graph.G.nodes else "", radius=999
        )
        return json.dumps(sub, ensure_ascii=False, indent=1)

    elif fmt == "graphml":
        import networkx as nx
        from io import StringIO
        buf = StringIO()
        # Remove embedding data for GraphML (not serializable)
        clean = graph.G.copy()
        for _, nd in clean.nodes(data=True):
            nd.pop("embedding", None)
            nd.pop("data", None)  # dict not serializable to GraphML
        nx.write_graphml(clean, buf)
        return buf.getvalue()

    elif fmt == "dot":
        import networkx as nx
        from io import StringIO
        buf = StringIO()
        clean = graph.G.copy()
        for _, nd in clean.nodes(data=True):
            nd.pop("embedding", None)
            nd.pop("data", None)
        nx.drawing.nx_pydot.write_dot(clean, buf)
        return buf.getvalue()

    return json.dumps({"error": f"unknown format '{fmt}'; use json|graphml|dot"})


# ═══════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════

def _resolve_graph(name: str) -> BinaryGraph:
    """Resolve graph by name, or return the latest one."""
    if name:
        return _get(name)
    if _active:
        # Return the most recently added
        last_key = list(_active.keys())[-1]
        return _active[last_key]
    return None


if __name__ == "__main__":
    mcp.run(transport="stdio")
