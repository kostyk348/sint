"""sint-crypto-mcp — крипто-специалист (fastmcp, stdio).

Cipher knowledge base, pattern detection, test vector validation,
code generation, side-channel analysis hints.

Tools:
  list_ciphers(family, tag)    — catalogue all known ciphers
  get_cipher(name)             — detailed info on one cipher
  get_test_vectors(cipher)     — RFC/NIST Known Answer Tests
  validate_vector(cipher, key, pt, ct) — check encrypt roundtrip
  detect_crypto(data, format)  — scan binary for crypto patterns
  analyze_entropy(data)        — entropy analysis of data block
  generate_impl(cipher, lang)  — generate clean-room C/Python/Rust
  side_channel_notes(cipher)   — timing/SCA analysis for this cipher
  compare_ciphers(names)       — side-by-side cipher comparison

Run: python server.py (stdio)
"""
from __future__ import annotations

import json
from pathlib import Path

from fastmcp import FastMCP

from config import NAME, VERSION, CIPHERS_DIR, SUPPORTED_LANGS
from ciphers.database import (
    get_cipher, list_ciphers, get_families, CipherInfo, CIPHERS,
)
from test_vectors.vectors import get_vectors, list_ciphers_with_vectors, VECTORS
from patterns.detect import detect_crypto_patterns, analyze_entropy

mcp = FastMCP(NAME)


# ═══════════════════════════════════════════════════════════════════
# CIPHER CATALOGUE
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def list_ciphers(family: str = "", tag: str = "") -> str:
    """List all known ciphers in the database.

    Args:
        family: filter by 'block' | 'stream' | 'hash' | 'aead' | 'lwc'
        tag: filter by tag (e.g. 'japanese', 'lightweight', 'broken')
    Returns: JSON array of cipher summaries.
    """
    results = list_ciphers(family=family, tag=tag)
    return json.dumps({
        "total": len(results),
        "ciphers": results,
        "families": get_families(),
    }, ensure_ascii=False, indent=1)


@mcp.tool()
def get_cipher_info(name: str) -> str:
    """Get detailed information about a specific cipher.

    Args:
        name: cipher name (e.g. 'CLEFIA', 'Camellia', 'AES')
    Returns: JSON with full cipher specification.
    """
    ci = get_cipher(name)
    if not ci:
        return json.dumps({"error": f"cipher '{name}' not found",
                           "suggestions": list(c.name for c in CIPHERS.values())})
    return json.dumps({
        "name": ci.name,
        "family": ci.family,
        "key_sizes": ci.key_sizes,
        "block_size": ci.block_size,
        "rounds": ci.rounds,
        "has_sbox": ci.sbox_pattern is not None,
        "refs": ci.refs,
        "tags": ci.tags,
        "has_test_vectors": ci.name.lower() in VECTORS,
    }, ensure_ascii=False, indent=1)


# ═══════════════════════════════════════════════════════════════════
# TEST VECTORS
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def get_test_vectors(cipher: str) -> str:
    """Get Known Answer Test vectors for a cipher.

    Args:
        cipher: cipher name
    Returns: JSON array of test vectors (key, pt, ct, ref).
    """
    vecs = get_vectors(cipher)
    if not vecs:
        return json.dumps({"error": f"no test vectors for '{cipher}'",
                           "available": list_ciphers_with_vectors()})
    return json.dumps({
        "cipher": cipher,
        "count": len(vecs),
        "vectors": vecs,
    }, ensure_ascii=False, indent=1)


@mcp.tool()
def validate_implementation(cipher: str, key_hex: str,
                            pt_hex: str, ct_hex: str) -> str:
    """Validate a cipher implementation against known test vectors.

    Given your implementation's output, checks if it matches
    any known test vector for this cipher.

    Args:
        cipher: cipher name
        key_hex: key in hex
        pt_hex: plaintext in hex
        ct_hex: ciphertext (your output) in hex
    Returns: match/no-match with suggestions.
    """
    vecs = get_vectors(cipher)
    if not vecs:
        return json.dumps({"error": f"no test vectors for '{cipher}'"})

    for v in vecs:
        if v["key"] == key_hex and v["pt"] == pt_hex:
            if v["ct"] == ct_hex:
                return json.dumps({
                    "status": "PASS",
                    "vector": v["ref"],
                    "note": "Output matches test vector ✅",
                }, indent=1)
            else:
                return json.dumps({
                    "status": "FAIL",
                    "vector": v["ref"],
                    "expected": v["ct"],
                    "got": ct_hex,
                    "note": "Output does not match ❌",
                }, indent=1)

    return json.dumps({
        "status": "UNKNOWN_VECTOR",
        "note": "No matching test vector found for this (key, pt) pair",
        "available_vectors": [
            {"key": v["key"], "ref": v["ref"]} for v in vecs
        ],
    }, indent=1)


# ═══════════════════════════════════════════════════════════════════
# PATTERN DETECTION
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def detect_crypto(data_hex: str, data_name: str = "") -> str:
    """Scan hex data for known crypto patterns.

    Detects: S-boxes, round constants, IVs, entropy classification.

    Args:
        data_hex: data as hex string
        data_name: optional label for the data
    Returns: JSON with detected patterns and entropy analysis.
    """
    try:
        data = bytes.fromhex(data_hex)
    except ValueError:
        return json.dumps({"error": "invalid hex string"})

    result = detect_crypto_patterns(data)
    if data_name:
        result["name"] = data_name
    return json.dumps(result, ensure_ascii=False, indent=1)


@mcp.tool()
def analyze_data_entropy(data_hex: str, data_name: str = "") -> str:
    """Analyze entropy of a binary data block.

    High entropy (>7.5) = likely encrypted/compressed.
    Low entropy (<3.0) = structured data/constants.

    Args:
        data_hex: data as hex string
        data_name: optional label
    Returns: entropy score + classification.
    """
    try:
        data = bytes.fromhex(data_hex)
    except ValueError:
        return json.dumps({"error": "invalid hex string"})

    result = analyze_entropy(data, name=data_name)
    return json.dumps(result, ensure_ascii=False, indent=1)


# ═══════════════════════════════════════════════════════════════════
# CODE GENERATION
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def generate_implementation(cipher: str, language: str = "c") -> str:
    """Generate a clean-room C/Python/Rust skeleton for a cipher.

    Produces header, key schedule, encrypt/decrypt stubs with
    correct constants based on the cipher spec.

    Args:
        cipher: cipher name
        language: 'c' | 'python' | 'rust'
    Returns: generated source code.
    """
    ci = get_cipher(cipher)
    if not ci:
        return json.dumps({"error": f"cipher '{cipher}' not found"})

    if language not in SUPPORTED_LANGS:
        return json.dumps({"error": f"unsupported language '{language}'",
                           "supported": SUPPORTED_LANGS})

    if language == "c":
        code = _gen_c(ci)
    elif language == "python":
        code = _gen_python(ci)
    elif language == "rust":
        code = _gen_rust(ci)
    else:
        return json.dumps({"error": f"unsupported language: {language}"})

    return json.dumps({
        "cipher": ci.name,
        "language": language,
        "code": code,
        "lines": len(code.splitlines()),
        "note": "⚠️  Skeleton only — implement core logic before using in production",
    }, ensure_ascii=False, indent=1)


def _gen_c(ci: CipherInfo) -> str:
    n = ci.name.lower().replace("-", "_")
    N = ci.name.upper().replace("-", "_")
    bs = ci.block_size // 8 if ci.block_size else 16
    lines = [
        f"/* {ci.name} — clean-room C implementation skeleton */",
        f"/* Family: {ci.family}, Key sizes: {ci.key_sizes} bits */",
        f"/* Refs: {', '.join(ci.refs) if ci.refs else 'N/A'} */",
        "",
        f"#ifndef {N}_H",
        f"#define {N}_H",
        "",
        f"#include <stdint.h>",
        f"#include <stddef.h>",
        "",
        f"#define {N}_BLOCK_SIZE {bs}",
        f"#define {N}_KEY_MIN     {min(ci.key_sizes)//8}",
        f"#define {N}_KEY_MAX     {max(ci.key_sizes)//8}",
        "",
        f"typedef struct {{",
        f"    uint8_t ek[4 * {ci.rounds + 4 if ci.rounds else 32}]; /* round keys */",
        f"    int     rounds;",
        f"}} {n}_ctx;",
        "",
        f"int {n}_set_key({n}_ctx *ctx, const uint8_t *key, size_t key_len);",
        f"void {n}_encrypt_block(const {n}_ctx *ctx,",
        f"                        const uint8_t in[{N}_BLOCK_SIZE],",
        f"                        uint8_t out[{N}_BLOCK_SIZE]);",
        f"void {n}_decrypt_block(const {n}_ctx *ctx,",
        f"                        const uint8_t in[{N}_BLOCK_SIZE],",
        f"                        uint8_t out[{N}_BLOCK_SIZE]);",
        "",
        f"#endif /* {N}_H */",
        "",
        f"/* === Implementation === */",
        f"/* Key schedule: {ci.rounds} rounds, keys {ci.key_sizes} bits */",
        f"/* TODO: implement {ci.name} core logic */",
        f"/* Reference: {', '.join(ci.refs) if ci.refs else 'specification'} */",
    ]
    return "\n".join(lines)


def _gen_python(ci: CipherInfo) -> str:
    n = ci.name.lower().replace("-", "_")
    lines = [
        f"\"\"\"{ci.name} — clean-room Python implementation skeleton.\"\"\"",
        f"\"\"\"Family: {ci.family}, Key sizes: {ci.key_sizes} bits\"\"\"",
        "",
        f"BLOCK_SIZE = {ci.block_size // 8 if ci.block_size else 16}",
        f"KEY_SIZES  = {ci.key_sizes}",
        f"ROUNDS     = {ci.rounds}",
        "",
        f"def key_schedule(key: bytes):",
        f'    """Expand key into round keys."""',
        f"    raise NotImplementedError",
        "",
        f"def encrypt_block(pt: bytes, rk) -> bytes:",
        f'    """Encrypt one block."""',
        f"    raise NotImplementedError",
        "",
        f"def decrypt_block(ct: bytes, rk) -> bytes:",
        f'    """Decrypt one block."""',
        f"    raise NotImplementedError",
        "",
        f"# Test vectors available: {ci.name.lower() in VECTORS}",
    ]
    return "\n".join(lines)


def _gen_rust(ci: CipherInfo) -> str:
    n = ci.name.lower().replace("-", "_")
    N = ci.name.replace("-", "")
    bs = ci.block_size // 8 if ci.block_size else 16
    lines = [
        f"//! {ci.name} — clean-room Rust implementation skeleton.",
        f"//! Family: {ci.family}, Key sizes: {ci.key_sizes} bits",
        "",
        f"pub const BLOCK_SIZE: usize = {bs};",
        f"pub const KEY_SIZES: &[usize] = &{ci.key_sizes};",
        f"pub const ROUNDS: usize = {ci.rounds};",
        "",
        f"pub struct {N} {{",
        f"    round_keys: [[u8; 16]; {ci.rounds + 1 if ci.rounds else 32}],",
        f"}}",
        "",
        f"impl {N} {{",
        f"    pub fn new(key: &[u8]) -> Result<Self, &'static str> {{",
        f"        // TODO: implement key schedule",
        f"        Err(\"not implemented\")",
        f"    }}",
        "",
        f"    pub fn encrypt_block(&self, block: &[u8; BLOCK_SIZE]) -> [u8; BLOCK_SIZE] {{",
        f"        // TODO: implement encryption",
        f"        *block",
        f"    }}",
        "",
        f"    pub fn decrypt_block(&self, block: &[u8; BLOCK_SIZE]) -> [u8; BLOCK_SIZE] {{",
        f"        // TODO: implement decryption",
        f"        *block",
        f"    }}",
        f"}}",
    ]
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# ANALYSIS
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def side_channel_notes(cipher: str) -> str:
    """Get side-channel analysis notes for a cipher.

    Args:
        cipher: cipher name
    Returns: JSON with SCA considerations.
    """
    ci = get_cipher(cipher)
    if not ci:
        return json.dumps({"error": f"cipher '{cipher}' not found"})

    notes = {
        "cipher": ci.name,
        "key_sizes": ci.key_sizes,
        "block_size": ci.block_size,
        "rounds": ci.rounds,
    }

    # Generic SCA concerns based on cipher structure
    concerns = []

    if ci.family == "block":
        concerns.append({
            "concern": "S-box lookups",
            "risk": "table-based S-box can leak key via cache timing",
            "mitigation": "use constant-time replacements or bit-slicing",
            "severity": "high",
        })
        concerns.append({
            "concern": "Key schedule branching",
            "risk": "branch on key bits leaks key via timing",
            "mitigation": "ensure data-independent execution time",
            "severity": "medium",
        })
    if ci.rounds < 10:
        concerns.append({
            "concern": "Low round count",
            "risk": "reduced security margin against differential/linear",
            "mitigation": "ensure sufficient rounds for key size",
            "severity": "info",
        })
    if "broken" in ci.tags:
        concerns.append({
            "concern": "Known cryptanalytic break",
            "risk": "cipher is considered broken",
            "mitigation": "do NOT use in production; historical only",
            "severity": "critical",
        })

    notes["concerns"] = concerns
    notes["total_concerns"] = len(concerns)

    return json.dumps(notes, ensure_ascii=False, indent=1)


@mcp.tool()
def compare_ciphers(cipher_names: str) -> str:
    """Side-by-side comparison of multiple ciphers.

    Args:
        cipher_names: comma-separated cipher names (e.g. 'AES,Camellia,CLEFIA')
    Returns: JSON comparison table.
    """
    names = [n.strip() for n in cipher_names.split(",")]
    results = []
    for name in names:
        ci = get_cipher(name)
        if ci:
            results.append({
                "name": ci.name,
                "family": ci.family,
                "key_sizes": ci.key_sizes,
                "block_size": ci.block_size,
                "rounds": ci.rounds,
                "tags": ci.tags,
                "refs": ci.refs,
            })
        else:
            results.append({"name": name, "error": "not found"})

    return json.dumps({
        "comparison": results,
        "count": len(results),
    }, ensure_ascii=False, indent=1)


@mcp.tool()
def crypto_help() -> str:
    """Get help on how to use sint-crypto-mcp tools.

    Returns: usage guide with examples.
    """
    return json.dumps({
        "description": "sint-crypto-mcp — Cipher knowledge base and analysis",
        "tools": {
            "list_ciphers": "list_ciphers(family='japanese') — all Japanese ciphers",
            "get_cipher_info": "get_cipher_info('CLEFIA') — detailed CLEFIA specs",
            "get_test_vectors": "get_test_vectors('Camellia') — RFC 3713 vectors",
            "validate_implementation": "validate_implementation('AES', key_hex, pt_hex, ct_hex)",
            "detect_crypto": "detect_crypto('deadbeef...', 'section.bin') — scan binary blob",
            "analyze_data_entropy": "analyze_data_entropy('...') — entropy only",
            "generate_implementation": "generate_implementation('FEAL', 'c') — C skeleton",
            "side_channel_notes": "side_channel_notes('AES') — SCA analysis",
            "compare_ciphers": "compare_ciphers('AES,Camellia,CLEFIA') — side-by-side",
        },
        "examples": [
            "Find Japanese ciphers: list_ciphers(tag='japanese')",
            "Scan binary for crypto: detect_crypto(data_hex)",
            "Validate impl: validate_implementation('CLEFIA', key, pt, ct)",
            "Generate code: generate_implementation('FEAL', 'python')",
        ],
    }, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    mcp.run(transport="stdio")
