"""DataTrace event parser + taint integration for sint-re-graph-mcp.

Parses DataTrace JSONL event streams and maps them onto the semantic graph.
This gives us DYNAMIC taint flow on top of STATIC pattern analysis.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from config import (
    T_NETWORK, T_FILE, T_ARGV, T_CONST, T_HEAP, T_STACK,
    T_UNTRUSTED, TAINT_NAMES, EDGE_Taint, NODE_DATA, NODE_OPERATION,
)


@dataclass
class TaintEvent:
    """Parsed DataTrace event."""
    ts: int
    pid: int
    tid: int
    event_type: str  # malloc, free, memcpy, sendto, recvfrom, etc.
    addr: int
    addr2: int
    size: int
    sample: bytes = b""
    is_ret: bool = False

    @property
    def is_recv(self) -> bool:
        return self.event_type in ("recvfrom", "recv")

    @property
    def is_send(self) -> bool:
        return self.event_type in ("sendto", "send")

    @property
    def is_copy(self) -> bool:
        return self.event_type in ("memcpy", "memmove")

    @property
    def is_alloc(self) -> bool:
        return self.event_type in ("malloc", "calloc", "realloc") and not self.is_ret

    @property
    def is_free(self) -> bool:
        return self.event_type == "free"


def parse_datatrace_events(jsonl_path: str) -> List[TaintEvent]:
    """Parse a DataTrace JSONL event file."""
    events = []
    with open(jsonl_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or not line.startswith("{"):
                continue
            try:
                d = json.loads(line)
                # Map DataTrace type codes to names
                type_map = {
                    1: "malloc", 2: "free", 3: "calloc",
                    4: "memcpy", 5: "memmove",
                    6: "sendto", 7: "recvfrom",
                    8: "send", 9: "recv",
                }
                raw_type = d.get("type", 0)
                is_ret = bool(raw_type & 0x1000)
                event_type = type_map.get(raw_type & ~0x1000, f"unknown_{raw_type}")

                sample = b""
                if d.get("sample"):
                    sample = bytes(d["sample"])
                elif d.get("sample_b64"):
                    import base64
                    sample = base64.b64decode(d["sample_b64"])

                events.append(TaintEvent(
                    ts=d.get("ts", 0),
                    pid=d.get("pid", 0),
                    tid=d.get("tid", 0),
                    event_type=event_type,
                    addr=d.get("addr", 0),
                    addr2=d.get("addr2", 0),
                    size=d.get("size", 0),
                    sample=sample,
                    is_ret=is_ret,
                ))
            except (json.JSONDecodeError, KeyError):
                continue
    return events


class TaintTracker:
    """Track taint labels through DataTrace events.

    Mirrors DataTrace's taint model but operates on our graph:
    - recvfrom/recv marks buffer as T_NETWORK
    - file read marks buffer as T_FILE
    - memcpy propagates labels
    - sendto/send is a sink
    """

    def __init__(self):
        # addr → taint_label (bitmask)
        self.shadows: Dict[int, int] = {}
        self.events_processed = 0
        self.taint_flows: List[dict] = []  # recorded flows for graph edges

    def process_event(self, ev: TaintEvent) -> Optional[dict]:
        """Process a single event. Returns a flow record if interesting."""
        self.events_processed += 1

        if ev.is_recv and not ev.is_ret:
            # Network receive → mark buffer as T_NETWORK
            self.shadows[ev.addr] = T_NETWORK
            return {
                "type": "taint_source",
                "addr": ev.addr,
                "size": ev.size,
                "taint": T_NETWORK,
                "taint_name": "network",
                "event": ev.event_type,
            }

        elif ev.event_type in ("fread", "read", "fgets") and not ev.is_ret:
            # File read → mark as T_FILE
            self.shadows[ev.addr] = T_FILE
            return {
                "type": "taint_source",
                "addr": ev.addr,
                "size": ev.size,
                "taint": T_FILE,
                "taint_name": "file",
                "event": ev.event_type,
            }

        elif ev.event_type in ("main",) and ev.addr2:
            # argv → mark as T_ARGV
            self.shadows[ev.addr] = T_ARGV
            return {
                "type": "taint_source",
                "addr": ev.addr,
                "size": ev.size,
                "taint": T_ARGV,
                "taint_name": "argv",
                "event": ev.event_type,
            }

        elif ev.is_copy:
            # memcpy/memmove: propagate taint from src to dst
            src_label = self.shadows.get(ev.addr2, 0)
            dst_label = self.shadows.get(ev.addr, 0)
            new_label = src_label | dst_label  # L_union
            if src_label:
                self.shadows[ev.addr] = new_label
                self.taint_flows.append({
                    "type": "taint_propagation",
                    "src_addr": ev.addr2,
                    "dst_addr": ev.addr,
                    "size": ev.size,
                    "taint": src_label,
                    "taint_name": TAINT_NAMES.get(src_label, "mixed"),
                    "event": ev.event_type,
                })
                return self.taint_flows[-1]

        elif ev.is_send:
            # Send → check if tainted data reaches sink
            label = self.shadows.get(ev.addr, 0)
            if label & T_UNTRUSTED:
                flow = {
                    "type": "taint_sink",
                    "addr": ev.addr,
                    "size": ev.size,
                    "taint": label,
                    "taint_name": TAINT_NAMES.get(label, "untrusted"),
                    "event": ev.event_type,
                    "is_untrusted": True,
                }
                self.taint_flows.append(flow)
                return flow

        elif ev.is_alloc:
            # Mark new allocation as heap (default)
            if ev.addr not in self.shadows:
                self.shadows[ev.addr] = T_HEAP

        elif ev.is_free:
            # Remove from shadow memory
            self.shadows.pop(ev.addr, None)

        return None

    def process_all(self, events: List[TaintEvent]) -> List[dict]:
        """Process all events, return list of interesting flows."""
        flows = []
        for ev in events:
            result = self.process_event(ev)
            if result:
                flows.append(result)
        return flows

    def get_taint_summary(self) -> dict:
        """Summary of taint state."""
        by_origin = {}
        for addr, label in self.shadows.items():
            name = TAINT_NAMES.get(label, f"0x{label:x}")
            by_origin[name] = by_origin.get(name, 0) + 1

        return {
            "events_processed": self.events_processed,
            "tracked_addresses": len(self.shadows),
            "taint_flows_recorded": len(self.taint_flows),
            "distribution": by_origin,
            "untrusted_flows": sum(1 for f in self.taint_flows
                                   if f.get("is_untrusted")),
        }


def integrate_datatrace_to_graph(graph, events: List[TaintEvent]):
    """Map DataTrace events onto a BinaryGraph.

    Creates:
    - Data nodes for each unique buffer (by address range)
    - Operation nodes for each function/event type
    - Taint flow edges between them
    """
    tracker = TaintTracker()
    flows = tracker.process_all(events)

    # Group events by address → create data nodes
    buffers = {}  # addr → {min_addr, max_addr, total_size, events}
    for ev in events:
        if ev.addr not in buffers:
            buffers[ev.addr] = {
                "min_addr": ev.addr,
                "max_addr": ev.addr + ev.size,
                "total_size": ev.size,
                "event_count": 0,
                "types": set(),
                "taint": 0,
            }
        buf = buffers[ev.addr]
        buf["max_addr"] = max(buf["max_addr"], ev.addr + ev.size)
        buf["total_size"] = max(buf["total_size"], ev.addr + ev.size - buf["min_addr"])
        buf["event_count"] += 1
        buf["types"].add(ev.event_type)
        buf["taint"] = tracker.shadows.get(ev.addr, 0)

    # Add data nodes for significant buffers
    for addr, info in buffers.items():
        if info["event_count"] >= 2:  # only non-trivial buffers
            graph.add_data_block(
                name=f"buf_{hex(addr)}",
                size=info["total_size"],
                source="datatrace",
                dtype="taint_tracked",
                taint_label=info["taint"],
                event_count=info["event_count"],
                event_types=sorted(info["types"]),
            )

    # Add operation nodes for event types
    event_types_seen = set()
    for ev in events:
        event_types_seen.add(ev.event_type)
    for etype in event_types_seen:
        graph.add_operation(
            name=f"dt_{etype}",
            op_type="libc_hook",
            event_type=etype,
        )

    # Add taint flow edges
    for flow in flows:
        src_addr = flow.get("src_addr") or flow.get("addr")
        dst_addr = flow.get("dst_addr") or flow.get("addr")
        src_node = f"data:{hex(src_addr)}"
        dst_node = f"data:{hex(dst_addr)}"

        # Ensure nodes exist
        for nid, addr_val in [(src_node, src_addr), (dst_node, dst_addr)]:
            if nid not in graph.G:
                graph.add_data_block(
                    name=f"buf_{hex(addr_val)}",
                    size=flow.get("size", 0),
                    source="datatrace",
                    dtype="taint_tracked",
                    taint_label=tracker.shadows.get(addr_val, 0),
                )

        graph.add_taint_flow(
            src_node, dst_node,
            taint_label=flow.get("taint", 0),
            flow_type=flow.get("type", ""),
            event=flow.get("event", ""),
        )

    return {
        "buffers_tracked": len(buffers),
        "taint_flows": len(flows),
        "untrusted_flows": sum(1 for f in flows if f.get("is_untrusted")),
        "tracker_summary": tracker.get_taint_summary(),
    }
