"""Crypto pattern detection in binary data.

Scans raw bytes for known S-boxes, constants, and crypto-related
signatures. Used by RE workflows to identify what cipher a binary uses.
"""
from __future__ import annotations
from typing import Optional
from ciphers.database import CIPHERS

# ── Detection helpers ─────────────────────────────────────────────────

def search_sbox(data: bytes) -> list[dict]:
    """Search for known S-box patterns in binary data."""
    results = []
    for name, ci in CIPHERS.items():
        if not ci.sbox_pattern:
            continue
        pos = data.find(ci.sbox_pattern)
        if pos >= 0:
            results.append({
                "cipher": ci.name,
                "type": "sbox",
                "position": pos,
                "confidence": 0.95,
                "note": f"Found {ci.name} S-box at offset 0x{pos:x}",
            })
        # Also search for partial matches (first 4 bytes)
        partial = ci.sbox_pattern[:4]
        for i in range(len(data) - 4):
            if data[i:i+4] == partial:
                # Check if it's not the full match already counted
                if pos != i:
                    results.append({
                        "cipher": ci.name,
                        "type": "sbox_partial",
                        "position": i,
                        "confidence": 0.6,
                        "note": f"Possible {ci.name} S-box fragment at 0x{i:x}",
                    })
                break
    return results


def search_constants(data: bytes) -> list[dict]:
    """Search for known cipher constants (IVs, round constants)."""
    results = []
    for name, ci in CIPHERS.items():
        for const in ci.constants:
            pos = data.find(const)
            if pos >= 0:
                results.append({
                    "cipher": ci.name,
                    "type": "constant",
                    "position": pos,
                    "confidence": 0.9,
                    "note": f"Found {ci.name} constant at 0x{pos:x}",
                })
    return results


def analyze_entropy(data: bytes, name: str = "") -> dict:
    """Analyze entropy profile of data blocks."""
    if not data:
        return {"error": "empty data"}

    from math import log2
    from collections import Counter

    total = len(data)
    if total == 0:
        return {"entropy": 0.0}

    freq = Counter(data)
    entropy = -sum((c/total) * log2(c/total) for c in freq.values())

    result = {
        "name": name,
        "size": total,
        "entropy": round(entropy, 4),
        "entropy_per_byte": round(entropy / 8, 4),
    }

    # Classify
    if entropy > 7.5:
        result["classification"] = "ENCRYPTED / COMPRESSED"
        result["confidence"] = 0.85
    elif entropy > 6.5:
        result["classification"] = "LIKELY_ENCRYPTED"
        result["confidence"] = 0.7
    elif entropy < 3.0:
        result["classification"] = "STRUCTURED / CONSTANTS"
        result["confidence"] = 0.9
    else:
        result["classification"] = "AMBIGUOUS"
        result["confidence"] = 0.4

    return result


def detect_crypto_patterns(data: bytes) -> dict:
    """Full crypto pattern scan of binary data."""
    return {
        "sboxes": search_sbox(data),
        "constants": search_constants(data),
        "entropy": analyze_entropy(data),
        "total_sections": len(data) // 256 + 1,
    }
