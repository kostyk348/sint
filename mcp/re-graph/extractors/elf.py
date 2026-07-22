"""ELF binary extractor using lief.

Extracts: sections, symbols, imports, exports, entry point,
structure info — and maps them onto the semantic graph.
"""
from __future__ import annotations

import hashlib
from typing import Dict, List, Optional

try:
    import lief
    HAS_LIEF = True
except ImportError:
    HAS_LIEF = False


def extract_elf(path: str) -> dict:
    """Parse ELF binary and extract structural information."""
    if not HAS_LIEF:
        return {"error": "lief not installed", "install": "pip install lief"}

    binary = lief.parse(path)
    if binary is None:
        return {"error": f"failed to parse: {path}"}

    result = {
        "path": path,
        "format": "ELF",
        "type": str(binary.header.file_type).split(".")[-1],
        "machine": str(binary.header.machine_type).split(".")[-1],
        "endian": "little" if binary.header.identity_data == lief.ELF.ELF_DATA.LSB else "big",
        "entry_point": hex(binary.header.entrypoint),
        "bits": 64 if binary.header.identity_class == lief.ELF.ELF_CLASS.CLASS64 else 32,
        "sections": [],
        "symbols": [],
        "imports": [],
        "exports": [],
        "strings_sample": [],
        "hash": "",
    }

    # File hash
    with open(path, "rb") as f:
        result["hash"] = hashlib.sha256(f.read()[:8192]).hexdigest()[:16]

    # Sections
    for sec in binary.sections:
        name = sec.name or ""
        result["sections"].append({
            "name": name,
            "offset": hex(sec.offset),
            "size": sec.size,
            "virtual_addr": hex(sec.virtual_address),
            "type": str(sec.type).split(".")[-1],
            "entropy": round(sec.content.get().entropy() if hasattr(sec, 'content') and sec.content else 0.0, 3),
        })

    # Symbols
    for sym in binary.dynamic_symbols:
        if sym.name:
            result["symbols"].append({
                "name": sym.name,
                "address": hex(sym.value),
                "size": sym.size,
                "type": str(sym.type).split(".")[-1],
                "binding": str(sym.binding).split(".")[-1],
            })
    # Limit to first 200
    result["symbols"] = result["symbols"][:200]

    # Imports
    for imp in binary.imported_functions:
        result["imports"].append({
            "name": imp.name if imp.name else hex(imp.address),
            "library": imp.library_name if hasattr(imp, "library_name") else "",
            "address": hex(imp.address),
        })

    # Exports
    for exp in binary.exported_functions:
        result["exports"].append({
            "name": exp.name if exp.name else hex(exp.address),
            "address": hex(exp.address),
        })

    # Sample strings from .rodata / .data
    for sec in binary.sections:
        if sec.name in (".rodata", ".data", ".rdata"):
            try:
                content = sec.content
                if content:
                    raw = bytes(content)
                    # Extract printable strings (min 8 chars)
                    strings = []
                    current = []
                    for b in raw:
                        if 32 <= b < 127:
                            current.append(chr(b))
                        else:
                            if len(current) >= 8:
                                strings.append("".join(current))
                            current = []
                    result["strings_sample"].extend(strings[:20])
            except Exception:
                pass

    result["strings_sample"] = result["strings_sample"][:30]
    return result


def map_elf_to_graph(graph, elf_info: dict):
    """Map ELF structural information onto a BinaryGraph.

    Creates:
    - Data nodes for sections (with size, entropy, type)
    - Operation nodes for functions (imports, exports, symbols)
    - Edges for call relationships (import → entry point)
    """
    binary_name = elf_info.get("path", "unknown").split("/")[-1].split("\\")[-1]

    # Add section data nodes
    for sec in elf_info.get("sections", []):
        name = sec["name"]
        if not name:
            continue
        graph.add_data_block(
            name=f"section:{name}",
            size=sec.get("size", 0),
            source="elf",
            dtype="section",
            vaddr=sec.get("virtual_addr", ""),
            section_type=sec.get("type", ""),
            entropy=sec.get("entropy", 0),
        )

    # Add function operation nodes
    for imp in elf_info.get("imports", []):
        graph.add_operation(
            name=f"import:{imp['name']}",
            op_type="import",
            addr=imp.get("address", ""),
            library=imp.get("library", ""),
        )

    for exp in elf_info.get("exports", []):
        graph.add_operation(
            name=f"export:{exp['name']}",
            op_type="export",
            addr=exp.get("address", ""),
        )

    # Add entry point
    entry = elf_info.get("entry_point", "")
    if entry and entry != "0x0":
        graph.add_operation(
            name=f"entry:{entry}",
            op_type="entry_point",
            addr=entry,
        )

    # Add significant symbols
    for sym in elf_info.get("symbols", []):
        if sym.get("size", 0) > 0 and sym.get("type") == "FUNC":
            graph.add_operation(
                name=f"sym:{sym['name']}",
                op_type="function",
                addr=sym.get("address", ""),
                size=sym.get("size", 0),
                binding=sym.get("binding", ""),
            )

    # Add string data
    for s in elf_info.get("strings_sample", []):
        graph.add_data_block(
            name=f"str:{s[:40]}",
            size=len(s),
            source="elf",
            dtype="string",
            content=s[:200],
        )
