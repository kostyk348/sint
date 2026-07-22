"""Semantic Binary Graph — core graph operations.

Nodes represent data blocks and operations.
Edges represent data flow, calls, and taint propagation.
Embeddings enable semantic search over graph structure.
"""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx
import numpy as np

from config import (
    GRAPH_DB, NODE_DATA, NODE_OPERATION,
    EDGE_DATA_FLOW, EDGE_CALL, EDGE_TRANSFORM, EDGE_Taint, EDGE_DATA_ACCESS,
    TAINT_NAMES, T_UNTRUSTED,
)
from embed import embed, cosine, embed_batch


class BinaryGraph:
    """In-memory NetworkX graph + SQLite persistence for a single binary."""

    def __init__(self, binary_name: str, db_path: Path | None = None):
        self.name = binary_name
        self.db = db_path or GRAPH_DB
        self.G = nx.DiGraph()
        self._conn: sqlite3.Connection | None = None
        self._ensure_schema()

    # ── SQLite persistence ──────────────────────────────────────────

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db))
            self._conn.execute("PRAGMA journal_mode=WAL")
        return self._conn

    def _ensure_schema(self):
        conn = self._get_conn()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS graphs (
                name TEXT PRIMARY KEY,
                created TEXT,
                updated TEXT,
                node_count INTEGER,
                edge_count INTEGER,
                meta TEXT
            );
            CREATE TABLE IF NOT EXISTS nodes (
                graph TEXT,
                node_id TEXT,
                node_type TEXT,
                label TEXT,
                data TEXT,
                embedding BLOB,
                PRIMARY KEY (graph, node_id)
            );
            CREATE TABLE IF NOT EXISTS edges (
                graph TEXT,
                source TEXT,
                target TEXT,
                edge_type TEXT,
                data TEXT,
                PRIMARY KEY (graph, source, target, edge_type)
            );
            CREATE TABLE IF NOT EXISTS patterns (
                graph TEXT,
                node_id TEXT,
                pattern_name TEXT,
                confidence REAL,
                details TEXT,
                PRIMARY KEY (graph, node_id, pattern_name)
            );
        """)
        conn.commit()

    # ── Node operations ─────────────────────────────────────────────

    def add_node(self, node_id: str, node_type: str, label: str,
                 data: dict | None = None, embedding: list | None = None) -> str:
        """Add a node to the graph. Returns node_id."""
        data = data or {}
        desc = self._make_description(node_id, node_type, label, data)

        if embedding is None:
            embedding = embed(desc)

        self.G.add_node(node_id, type=node_type, label=label,
                        data=data, embedding=embedding, description=desc)
        return node_id

    def add_data_block(self, name: str, size: int = 0,
                       source: str = "", dtype: str = "buffer",
                       entropy: float = 0.0, **kwargs) -> str:
        """Add a data block node (buffer, struct, string, constant)."""
        nid = f"data:{name}"
        data = {
            "size": size, "source": source, "dtype": dtype,
            "entropy": round(entropy, 3), **kwargs,
        }
        return self.add_node(nid, NODE_DATA, name, data)

    def add_operation(self, name: str, op_type: str = "function",
                      addr: int = 0, size: int = 0,
                      complexity: str = "", **kwargs) -> str:
        """Add an operation node (function, basic block, loop)."""
        nid = f"op:{name}"
        data = {
            "op_type": op_type, "addr": hex(addr) if addr else "",
            "size": size, "complexity": complexity, **kwargs,
        }
        return self.add_node(nid, NODE_OPERATION, name, data)

    # ── Edge operations ─────────────────────────────────────────────

    def add_edge(self, source: str, target: str, edge_type: str,
                 data: dict | None = None):
        """Add an edge between two nodes."""
        data = data or {}
        self.G.add_edge(source, target, edge_type=edge_type, data=data)

    def add_data_flow(self, data_node: str, op_node: str, **kwargs):
        self.add_edge(data_node, op_node, EDGE_DATA_FLOW, kwargs)

    def add_call(self, caller: str, callee: str, **kwargs):
        self.add_edge(caller, callee, EDGE_CALL, kwargs)

    def add_transform(self, op_node: str, data_node: str, **kwargs):
        self.add_edge(op_node, data_node, EDGE_TRANSFORM, kwargs)

    def add_taint_flow(self, source: str, target: str, taint_label: int = 0,
                       **kwargs):
        """Add a taint-flow edge (from DataTrace)."""
        data = {"taint_label": taint_label,
                "taint_origin": TAINT_NAMES.get(taint_label, "unknown"),
                **kwargs}
        self.add_edge(source, target, EDGE_Taint, data)

    # ── Semantic queries ────────────────────────────────────────────

    def find_similar(self, query: str, k: int = 5,
                     node_type: str = "") -> List[dict]:
        """Find nodes semantically similar to query text."""
        q_emb = embed(query)
        results = []
        for nid, ndata in self.G.nodes(data=True):
            if node_type and ndata.get("type") != node_type:
                continue
            emb = ndata.get("embedding")
            if emb is None:
                continue
            sc = cosine(q_emb, emb)
            results.append({
                "node_id": nid,
                "type": ndata.get("type", ""),
                "label": ndata.get("label", ""),
                "score": round(sc, 4),
                "data": ndata.get("data", {}),
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:k]

    def find_pattern(self, pattern_hint: str, k: int = 5) -> List[dict]:
        """Find nodes matching a known pattern by semantic similarity."""
        # Build a richer query with pattern context
        query = f"known pattern: {pattern_hint} (S-box lookup, round function, key schedule, polynomial, permutation)"
        return self.find_similar(query, k=k, node_type=NODE_OPERATION)

    # ── Transform tracing ───────────────────────────────────────────

    def trace_forward(self, start: str, max_depth: int = 10) -> dict:
        """Trace data flow forward from a node."""
        if start not in self.G:
            return {"error": f"node '{start}' not found"}
        return self._trace(start, direction="forward", max_depth=max_depth)

    def trace_backward(self, start: str, max_depth: int = 10) -> dict:
        """Trace data flow backward to origins."""
        if start not in self.G:
            return {"error": f"node '{start}' not found"}
        return self._trace(start, direction="backward", max_depth=max_depth)

    def _trace(self, start: str, direction: str = "forward",
               max_depth: int = 10) -> dict:
        """BFS trace through the graph."""
        visited = set()
        queue = [(start, 0)]
        chain = []

        while queue:
            node, depth = queue.pop(0)
            if node in visited or depth > max_depth:
                continue
            visited.add(node)

            ndata = self.G.nodes.get(node, {})
            chain.append({
                "node_id": node,
                "type": ndata.get("type", ""),
                "label": ndata.get("label", ""),
                "depth": depth,
                "data": ndata.get("data", {}),
            })

            if direction == "forward":
                for _, tgt, edata in self.G.out_edges(node, data=True):
                    if tgt not in visited:
                        queue.append((tgt, depth + 1))
            else:
                for src, _, edata in self.G.in_edges(node, data=True):
                    if src not in visited:
                        queue.append((src, depth + 1))

        return {"start": start, "direction": direction,
                "chain": chain, "total_nodes": len(chain)}

    # ── Delta analysis ──────────────────────────────────────────────

    def get_delta(self, before_id: str, after_id: str) -> dict:
        """Compare two data nodes: what changed."""
        before = self.G.nodes.get(before_id, {})
        after = self.G.nodes.get(after_id, {})
        if not before or not after:
            return {"error": "one or both nodes not found"}

        bd = before.get("data", {})
        ad = after.get("data", {})

        delta = {
            "before": {"id": before_id, "label": before.get("label"), **bd},
            "after": {"id": after_id, "label": after.get("label"), **ad},
            "changes": {},
        }

        # Compare size
        bs = bd.get("size", 0)
        as_ = ad.get("size", 0)
        if bs != as_:
            delta["changes"]["size"] = {"from": bs, "to": as_,
                                        "delta": as_ - bs}

        # Compare entropy
        be = bd.get("entropy", 0.0)
        ae = ad.get("entropy", 0.0)
        if abs(be - ae) > 0.05:
            delta["changes"]["entropy"] = {"from": be, "to": ae,
                                           "delta": round(ae - be, 3)}

        # Compare taint
        bt = bd.get("taint_label", 0)
        at = ad.get("taint_label", 0)
        if bt != at:
            delta["changes"]["taint"] = {
                "from": TAINT_NAMES.get(bt, "clean"),
                "to": TAINT_NAMES.get(at, "clean"),
            }

        delta["has_changes"] = bool(delta["changes"])
        return delta

    # ── Subgraph export ─────────────────────────────────────────────

    def get_subgraph(self, center: str, radius: int = 2) -> dict:
        """Get nodes within radius hops of center."""
        if center not in self.G:
            return {"error": f"node '{center}' not found"}

        nodes = set()
        queue = [(center, 0)]
        while queue:
            n, d = queue.pop(0)
            if n in nodes or d > radius:
                continue
            nodes.add(n)
            for _, tgt in self.G.out_edges(n):
                queue.append((tgt, d + 1))
            for src, _ in self.G.in_edges(n):
                queue.append((src, d + 1))

        sub = {"nodes": [], "edges": []}
        for n in nodes:
            nd = self.G.nodes[n]
            sub["nodes"].append({
                "id": n, "type": nd.get("type", ""),
                "label": nd.get("label", ""),
                "data": nd.get("data", {}),
            })
        for s, t, ed in self.G.subgraph(nodes).edges(data=True):
            sub["edges"].append({
                "source": s, "target": t,
                "edge_type": ed.get("edge_type", ""),
                "data": ed.get("data", {}),
            })
        return sub

    # ── Summary generation ──────────────────────────────────────────

    def summarize(self) -> dict:
        """Generate a linguistic summary of the graph."""
        nodes_data = [n for n, d in self.G.nodes(data=True)
                      if d.get("type") == NODE_DATA]
        nodes_op = [n for n, d in self.G.nodes(data=True)
                    if d.get("type") == NODE_OPERATION]

        taint_edges = [(s, t, d) for s, t, d in self.G.edges(data=True)
                       if d.get("edge_type") == EDGE_Taint]

        # Find high-entropy data (potential crypto)
        crypto_candidates = []
        for n in nodes_data:
            nd = self.G.nodes[n]
            ent = nd.get("data", {}).get("entropy", 0)
            if ent > 7.0:
                crypto_candidates.append({
                    "node": n,
                    "entropy": ent,
                    "label": nd.get("label", ""),
                })

        # Find taint sinks (untrusted data reaching output)
        taint_sinks = []
        for src, tgt, ed in taint_edges:
            taint_label = ed.get("data", {}).get("taint_label", 0)
            if taint_label & T_UNTRUSTED:
                tgt_nd = self.G.nodes.get(tgt, {})
                taint_sinks.append({
                    "source_node": src,
                    "sink_node": tgt,
                    "taint_origin": TAINT_NAMES.get(taint_label, "unknown"),
                    "sink_label": tgt_nd.get("label", ""),
                })

        return {
            "graph": self.name,
            "total_nodes": self.G.number_of_nodes(),
            "total_edges": self.G.number_of_edges(),
            "data_blocks": len(nodes_data),
            "operations": len(nodes_op),
            "taint_flows": len(taint_edges),
            "taint_sinks": taint_sinks,
            "high_entropy_data": crypto_candidates,
            "connected_components": nx.number_weakly_connected_components(self.G),
        }

    # ── Persistence ─────────────────────────────────────────────────

    def save(self, meta: dict | None = None):
        """Save graph to SQLite."""
        conn = self._get_conn()
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Upsert graph metadata
        conn.execute("""
            INSERT OR REPLACE INTO graphs (name, created, updated, node_count, edge_count, meta)
            VALUES (?, COALESCE((SELECT created FROM graphs WHERE name=?), ?), ?, ?, ?, ?)
        """, (self.name, self.name, now, now,
              self.G.number_of_nodes(), self.G.number_of_edges(),
              json.dumps(meta or {}, ensure_ascii=False)))

        # Save nodes
        conn.execute("DELETE FROM nodes WHERE graph=?", (self.name,))
        for nid, ndata in self.G.nodes(data=True):
            emb = ndata.get("embedding")
            emb_blob = np.asarray(emb, dtype=np.float32).tobytes() if emb else None
            conn.execute(
                "INSERT INTO nodes (graph, node_id, node_type, label, data, embedding) VALUES (?,?,?,?,?,?)",
                (self.name, nid, ndata.get("type", ""), ndata.get("label", ""),
                 json.dumps(ndata.get("data", {}), ensure_ascii=False), emb_blob)
            )

        # Save edges
        conn.execute("DELETE FROM edges WHERE graph=?", (self.name,))
        for src, tgt, edata in self.G.edges(data=True):
            conn.execute(
                "INSERT INTO edges (graph, source, target, edge_type, data) VALUES (?,?,?,?,?)",
                (self.name, src, tgt, edata.get("edge_type", ""),
                 json.dumps(edata.get("data", {}), ensure_ascii=False))
            )

        # Save patterns
        conn.execute("DELETE FROM patterns WHERE graph=?", (self.name,))
        for nid, ndata in self.G.nodes(data=True):
            for pname, pconf in ndata.get("patterns", {}).items():
                conn.execute(
                    "INSERT INTO patterns (graph, node_id, pattern_name, confidence, details) VALUES (?,?,?,?,?)",
                    (self.name, nid, pname, pconf.get("confidence", 0),
                     json.dumps(pconf, ensure_ascii=False))
                )

        conn.commit()

    @classmethod
    def load(cls, binary_name: str, db_path: Path | None = None) -> "BinaryGraph":
        """Load graph from SQLite."""
        g = cls(binary_name, db_path)
        conn = g._get_conn()

        # Load nodes
        for row in conn.execute(
            "SELECT node_id, node_type, label, data, embedding FROM nodes WHERE graph=?",
            (binary_name,)
        ):
            nid, ntype, label, data_json, emb_blob = row
            data = json.loads(data_json) if data_json else {}
            emb = np.frombuffer(emb_blob, dtype=np.float32).tolist() if emb_blob else None
            g.G.add_node(nid, type=ntype, label=label, data=data,
                         embedding=emb, description=label)

        # Load edges
        for row in conn.execute(
            "SELECT source, target, edge_type, data FROM edges WHERE graph=?",
            (binary_name,)
        ):
            src, tgt, etype, data_json = row
            data = json.loads(data_json) if data_json else {}
            g.G.add_edge(src, tgt, edge_type=etype, data=data)

        return g

    # ── Helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _make_description(node_id: str, node_type: str, label: str,
                          data: dict) -> str:
        """Create a natural-language description for embedding."""
        parts = [f"{node_type}: {label}"]
        if data.get("dtype"):
            parts.append(f"type={data['dtype']}")
        if data.get("size"):
            parts.append(f"size={data['size']} bytes")
        if data.get("entropy"):
            parts.append(f"entropy={data['entropy']}")
        if data.get("op_type"):
            parts.append(f"operation={data['op_type']}")
        if data.get("source"):
            parts.append(f"source={data['source']}")
        if data.get("taint_label"):
            parts.append(f"taint={TAINT_NAMES.get(data['taint_label'], '?')}")
        if data.get("pattern"):
            parts.append(f"matches {data['pattern']}")
        return " | ".join(parts)

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
