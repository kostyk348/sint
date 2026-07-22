"""Generic binary extractor — works with any file type.

Extracts: entropy profile, byte frequency, magic bytes,
structural markers, string table, and known patterns.
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import List

from patterns.known import get_detector, _entropy, _byte_freq_analysis


# Common magic bytes
MAGICS = {
    b"\x7fELF": "ELF",
    b"MZ": "PE/EXE",
    b"PK\x03\x04": "ZIP/JAR/APK",
    b"\x89PNG": "PNG",
    b"\xff\xd8\xff": "JPEG",
    b"GIF8": "GIF",
    b"\x1f\x8b": "GZIP",
    b"BZ": "BZIP2",
    b"\xfd7zXZ": "XZ",
    b"Rar!": "RAR",
    b"\xca\xfe\xba\xbe": "Mach-O/Fat",
    b"\xfe\xed\xfa\xce": "Mach-O 32",
    b"\xfe\xed\xfa\xcf": "Mach-O 64",
    b"NDS": "Nintendo DS",
    b"\x28\xcd\x3d\x45": "PS Vita PBP",
    b"~\x20\x43\x4f\x4d\x50\x41\x54": "DSO manifest",
}


def extract_generic(path: str, sample_size: int = 65536) -> dict:
    """Generic binary analysis — no dependencies beyond stdlib."""
    p = Path(path)
    if not p.exists():
        return {"error": f"file not found: {path}"}

    raw = p.read_bytes()
    total_size = len(raw)

    result = {
        "path": str(p),
        "format": "unknown",
        "size": total_size,
        "hash": hashlib.sha256(raw[:8192]).hexdigest()[:16],
        "sections": [],
        "symbols": [],
        "imports": [],
        "exports": [],
        "strings_sample": [],
    }

    # Detect format
    for magic, fmt in MAGICS.items():
        if raw.startswith(magic):
            result["format"] = fmt
            break

    # Entropy profile (per 1KB block)
    block_size = 1024
    entropy_profile = []
    for i in range(0, min(total_size, sample_size), block_size):
        block = raw[i:i+block_size]
        ent = _entropy(block)
        entropy_profile.append({
            "offset": hex(i),
            "entropy": round(ent, 3),
        })

    result["entropy_profile"] = entropy_profile
    result["overall_entropy"] = round(
        sum(e["entropy"] for e in entropy_profile) / max(len(entropy_profile), 1), 3
    )

    # Byte frequency analysis on first sample
    sample = raw[:sample_size]
    freq_analysis = _byte_freq_analysis(sample)
    result["byte_analysis"] = freq_analysis

    # Pattern detection
    detector = get_detector()
    patterns = detector.detect_all(sample)
    result["patterns"] = patterns.get("patterns_detected", [])
    result["recommendations"] = patterns.get("recommendations", [])
    result["likely_crypto"] = patterns.get("likely_crypto", False)

    # Extract printable strings
    strings = []
    current = []
    for b in raw:
        if 32 <= b < 127:
            current.append(chr(b))
        else:
            if len(current) >= 6:
                s = "".join(current)
                strings.append(s)
            current = []
    result["strings_sample"] = strings[:50]
    result["total_strings"] = len(strings)

    return result


def map_generic_to_graph(graph, gen_info: dict):
    """Map generic binary analysis onto a BinaryGraph."""
    binary_name = Path(gen_info.get("path", "unknown")).stem

    # Add format node
    graph.add_data_block(
        name=f"file:{binary_name}",
        size=gen_info.get("size", 0),
        source="generic",
        dtype="file",
        format=gen_info.get("format", "unknown"),
        entropy=gen_info.get("overall_entropy", 0),
    )

    # Add entropy blocks as data nodes
    for ep in gen_info.get("entropy_profile", []):
        ent = ep["entropy"]
        if ent > 7.0:
            graph.add_data_block(
                name=f"entropy_block:{ep['offset']}",
                size=1024,
                source="generic",
                dtype="high_entropy",
                offset=ep["offset"],
                entropy=ent,
            )

    # Add detected patterns as operation nodes
    for p in gen_info.get("patterns", []):
        graph.add_operation(
            name=f"pattern:{p['pattern']}",
            op_type="known_pattern",
            pattern=p["pattern"],
            description=p.get("description", ""),
            confidence=p.get("confidence", 0),
            offset=p.get("offset", ""),
        )

    # Add strings as data nodes
    for s in gen_info.get("strings_sample", [])[:20]:
        graph.add_data_block(
            name=f"str:{s[:40]}",
            size=len(s),
            source="generic",
            dtype="string",
            content=s[:200],
        )
