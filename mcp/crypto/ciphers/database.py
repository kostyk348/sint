"""Cipher knowledge database — specs, params, patterns for known ciphers."""
from __future__ import annotations
from typing import Optional

# ── Cipher record ─────────────────────────────────────────────────────
class CipherInfo:
    """Metadata + detection pattern for one cipher."""
    def __init__(self, name: str, family: str, key_sizes: list[int],
                 block_size: int = 0, rounds: int = 0,
                 sbox_pattern: Optional[bytes] = None,
                 constants: Optional[list[bytes]] = None,
                 refs: Optional[list[str]] = None,
                 tags: Optional[list[str]] = None):
        self.name = name
        self.family = family       # block | stream | hash | aead | lwc
        self.key_sizes = key_sizes
        self.block_size = block_size
        self.rounds = rounds
        self.sbox_pattern = sbox_pattern   # known S-box bytes for detection
        self.constants = constants or []
        self.refs = refs or []
        self.tags = tags or []


# ── CIPHER DATABASE ───────────────────────────────────────────────────
CIPHERS: dict[str, CipherInfo] = {}

def register(c: CipherInfo):
    CIPHERS[c.name.lower()] = c

# --- Block ciphers ---
register(CipherInfo("AES", "block", [128, 192, 256], 128, 10,
    sbox_pattern=bytes([
        0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,
        0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
    ]),
    refs=["FIPS 197"],
    tags=["nist", "usa", "rijndael"]))

register(CipherInfo("Camellia", "block", [128, 192, 256], 128, 24,
    sbox_pattern=bytes([
        0x70,0x82,0x2c,0xec,0xb3,0x27,0xc0,0xe5,
        0xe4,0x85,0x57,0x35,0xea,0x0c,0xae,0x41,
    ]),
    refs=["RFC 3713", "ISO/IEC 18033-3"],
    tags=["japanese", "ntt", "mitsubishi", "lightweight"]))

register(CipherInfo("CLEFIA", "block", [128, 192, 256], 128, 18,
    sbox_pattern=bytes([
        0x57,0x49,0xd1,0xc6,0x2f,0x33,0x74,0xfb,
        0x95,0x6d,0x82,0xea,0x0e,0xb0,0xa8,0x1c,
    ]),
    refs=["RFC 6114", "ISO/IEC 29192-2"],
    tags=["japanese", "sony", "lightweight"]))

register(CipherInfo("MISTY1", "block", [128], 64, 8,
    refs=["RFC 2994", "ISO/IEC 18033-3"],
    tags=["japanese", "mitsubishi", "lightweight"]))

register(CipherInfo("KASUMI", "block", [128], 64, 8,
    refs=["3GPP TS 35.202"],
    tags=["3gpp", "gsm", "lte", "japanese"]))

register(CipherInfo("SEED", "block", [128], 128, 16,
    refs=["RFC 4269", "ISO/IEC 18033-3"],
    tags=["korean", "kisa"]))

register(CipherInfo("ARIA", "block", [128, 192, 256], 128, 12,
    refs=["RFC 5794", "KS X 1213"],
    tags=["korean", "kisa"]))

register(CipherInfo("FEAL", "block", [64], 64, 4,
    refs=["FEAL-8/NTT"],
    tags=["japanese", "broken", "historical", "ntt"]))

register(CipherInfo("DES", "block", [56], 64, 16,
    sbox_pattern=bytes([
        0xe0,0xf0,0x10,0x20,0x30,0x40,0x50,0x60,
    ]),
    refs=["FIPS 46-3"],
    tags=["nist", "usa", "historical", "broken"]))

register(CipherInfo("3DES", "block", [112, 168], 64, 16,
    refs=["SP 800-67"],
    tags=["nist", "usa"]))

register(CipherInfo("SM4", "block", [128], 128, 32,
    refs=["GB/T 32907-2016"],
    tags=["chinese", "national"]))

register(CipherInfo("Twofish", "block", [128, 192, 256], 128, 16,
    tags=["usa", "aes-finalist"]))

register(CipherInfo("Serpent", "block", [128, 192, 256], 128, 32,
    tags=["usa", "aes-finalist"]))

# --- Stream ciphers ---
register(CipherInfo("RC4", "stream", [8, 128], 0, 0,
    refs=["RFC 7465"],
    tags=["broken", "historical"]))

register(CipherInfo("ChaCha20", "stream", [256], 64, 20,
    refs=["RFC 8439"],
    tags=["bernstein", "djb", "modern"]))

register(CipherInfo("Salsa20", "stream", [256], 64, 20,
    refs=["eSTREAM"],
    tags=["bernstein", "djb", "eSTREAM"]))

# --- Hash functions ---
register(CipherInfo("MD5", "hash", [0], 64, 64,
    constants=[bytes([
        0x67,0x45,0x23,0x01,0xef,0xcd,0xab,0x89,
    ])],
    refs=["RFC 1321"],
    tags=["broken", "historical"]))

register(CipherInfo("SHA-1", "hash", [0], 64, 80,
    constants=[bytes([
        0x01,0x23,0x45,0x67,0x89,0xab,0xcd,0xef,
    ])],
    refs=["FIPS 180-4"],
    tags=["nist", "deprecated"]))

register(CipherInfo("SHA-256", "hash", [0], 64, 64,
    refs=["FIPS 180-4"],
    tags=["nist", "modern"]))

register(CipherInfo("SHA-3", "hash", [0], 200, 24,
    refs=["FIPS 202"],
    tags=["nist", "modern", "keccak"]))

# --- Lightweight / Japanese ---
register(CipherInfo("Hierocrypt-3", "block", [128, 192, 256], 128, 16,
    refs=["ISO/IEC 18033-3"],
    tags=["japanese", "toshiba"]))

register(CipherInfo("KCipher-2", "stream", [128], 0, 0,
    refs=["ISO/IEC 18033-4"],
    tags=["japanese", "kddi"]))

register(CipherInfo("Enocoro", "stream", [80, 128], 0, 0,
    tags=["japanese", "hitachi", "lightweight"]))

register(CipherInfo("Multi-S01", "block", [64], 64, 12,
    tags=["japanese", "cryptorec"]))


# ── Lookup helpers ────────────────────────────────────────────────────

def get_cipher(name: str) -> Optional[CipherInfo]:
    """Lookup cipher by name (case-insensitive, partial match)."""
    key = name.lower()
    if key in CIPHERS:
        return CIPHERS[key]
    # Partial match
    for cname, ci in CIPHERS.items():
        if key in cname or cname in key:
            return ci
    return None

def list_ciphers(family: str = "", tag: str = "") -> list[dict]:
    """List all ciphers, optionally filtered."""
    results = []
    for ci in CIPHERS.values():
        if family and ci.family != family:
            continue
        if tag and tag not in ci.tags:
            continue
        results.append({
            "name": ci.name,
            "family": ci.family,
            "key_sizes": ci.key_sizes,
            "block_size": ci.block_size,
            "rounds": ci.rounds,
            "tags": ci.tags,
            "refs": ci.refs,
        })
    return sorted(results, key=lambda x: x["name"])

def get_families() -> dict:
    """Get cipher count by family."""
    counts = {}
    for ci in CIPHERS.values():
        counts[ci.family] = counts.get(ci.family, 0) + 1
    return counts
