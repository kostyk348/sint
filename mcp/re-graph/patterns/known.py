"""Known pattern signatures for binary analysis.

Each pattern is a set of byte sequences, structural properties,
or behavioral markers that identify a specific algorithm or protocol.
"""
from __future__ import annotations

import math
from typing import Dict, List, Tuple


# ── AES S-box (first 32 bytes) ────────────────────────────────────
AES_SBOX_32 = bytes([
    0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5,
    0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
    0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0,
    0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
])

# ── AES inverse S-box (first 32 bytes) ────────────────────────────
AES_INV_SBOX_32 = bytes([
    0x52, 0x09, 0x6A, 0xD5, 0x30, 0x36, 0xA5, 0x38,
    0xBF, 0x40, 0xA3, 0x9E, 0x81, 0xF3, 0xD7, 0xFB,
    0x7C, 0xE3, 0x39, 0x82, 0x9B, 0x2F, 0xFF, 0x87,
    0x34, 0x8E, 0x43, 0x44, 0xC4, 0xDE, 0xE9, 0xCB,
])

# ── CLEFIA S-boxes (from RFC 6114) ────────────────────────────────
CLEFIA_SBOX0_16 = bytes([
    0x57, 0x49, 0xD1, 0xC6, 0x2F, 0x33, 0x24, 0x0C,
    0x71, 0xB6, 0x9A, 0x8E, 0x85, 0x21, 0xBC, 0x98,
])

# ── CRC-32 polynomial (reversed, in little-endian tables) ──────────
# Common CRC-32 lookup table first 4 entries
CRC32_TABLE_4 = bytes([
    0x00, 0x00, 0x00, 0x00,  # entry 0
    0x96, 0x30, 0x07, 0x77,  # entry 1
    0x2C, 0x61, 0x0E, 0xEE,  # entry 2
    0xBA, 0x51, 0x09, 0x99,  # entry 3
])

# ── Base64 alphabet (ASCII) ───────────────────────────────────────
BASE64_ALPHABET = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

# ── MD5 initialization values ──────────────────────────────────────
MD5_INIT = bytes([
    0x01, 0x23, 0x45, 0x67,  # A
    0x89, 0xAB, 0xCD, 0xEF,  # B
    0xFE, 0xDC, 0xBA, 0x98,  # C
    0x76, 0x54, 0x32, 0x10,  # D
])

# ── SHA-256 initial hash values (first 8 bytes of H0) ─────────────
SHA256_H0 = bytes([
    0x67, 0xE6, 0x09, 0x6A,  # H0[0] = 0x6A09E667
    0x8A, 0xCA, 0xE1, 0xBB,  # H0[1] = 0xBB67AE85
])

# ── RC4 key scheduling permutation (first 256 bytes when key is empty)
# Actually: we check for the characteristic pattern of rapid
# sequential byte access to a 256-byte array

# ── DES S-boxes (first 32 bytes of S1) ────────────────────────────
DES_S1_16 = bytes([
    0x0E, 0x04, 0x0D, 0x01, 0x02, 0x0F, 0x0B, 0x08,
    0x03, 0x0A, 0x06, 0x0C, 0x05, 0x09, 0x00, 0x07,
])

# ── RSA modulus patterns ──────────────────────────────────────────
# RSA keys typically start with 0x00 0x01 or 0x00 0x02 (PKCS#1)
RSA_PKCS1_PREFIX = bytes([0x00, 0x01])
RSA_PKCS1_ENCRYPT_PREFIX = bytes([0x00, 0x02])


def _entropy(data: bytes) -> float:
    """Calculate Shannon entropy of byte data."""
    if not data:
        return 0.0
    freq = [0] * 256
    for b in data:
        freq[b] += 1
    n = len(data)
    ent = 0.0
    for f in freq:
        if f > 0:
            p = f / n
            ent -= p * math.log2(p)
    return ent


def _byte_freq_analysis(data: bytes) -> dict:
    """Analyze byte frequency distribution."""
    freq = [0] * 256
    for b in data:
        freq[b] += 1
    n = len(data)
    if n == 0:
        return {}
    # Top 5 most frequent bytes
    indexed = [(freq[i], i) for i in range(256) if freq[i] > 0]
    indexed.sort(reverse=True)
    return {
        "unique_bytes": sum(1 for f in freq if f > 0),
        "top_5": [(hex(b), round(f / n, 4)) for f, b in indexed[:5]],
        "entropy": round(_entropy(data), 4),
    }


class PatternDetector:
    """Detect known algorithm/protocol patterns in binary data."""

    def __init__(self):
        self.patterns = [
            ("AES_SBOX", AES_SBOX_32, "AES encryption (S-box lookup table)", 0.95),
            ("AES_INV_SBOX", AES_INV_SBOX_32, "AES decryption (inverse S-box)", 0.95),
            ("CLEFIA_SBOX0", CLEFIA_SBOX0_16, "CLEFIA cipher (S-box 0)", 0.90),
            ("CRC32_TABLE", CRC32_TABLE_4, "CRC-32 checksum (lookup table)", 0.85),
            ("MD5_INIT", MD5_INIT, "MD5 hash (initialization vector)", 0.90),
            ("SHA256_H0", SHA256_H0, "SHA-256 hash (initial H0)", 0.85),
            ("DES_S1", DES_S1_16, "DES cipher (S-box 1)", 0.88),
        ]

    def scan_bytes(self, data: bytes, offset: int = 0) -> List[dict]:
        """Scan byte data for known patterns."""
        found = []
        for name, signature, description, confidence in self.patterns:
            pos = data.find(signature)
            if pos >= 0:
                found.append({
                    "pattern": name,
                    "description": description,
                    "confidence": confidence,
                    "offset": hex(offset + pos),
                    "signature_length": len(signature),
                })
        return found

    def analyze_buffer(self, data: bytes) -> dict:
        """Full analysis of a buffer: patterns + statistics."""
        patterns = self.scan_bytes(data)
        stats = _byte_freq_analysis(data)

        return {
            "size": len(data),
            "entropy": stats.get("entropy", 0),
            "unique_bytes": stats.get("unique_bytes", 0),
            "top_frequent_bytes": stats.get("top_5", []),
            "patterns_detected": patterns,
            "likely_crypto": stats.get("entropy", 0) > 7.5 and len(data) >= 16,
            "likely_text": stats.get("unique_bytes", 0) < 128 and stats.get("entropy", 0) < 5.0,
            "likely_structured": self._check_structured(data),
        }

    def _check_structured(self, data: bytes) -> bool:
        """Check if data looks structured (repeated patterns, alignment)."""
        if len(data) < 16:
            return False
        # Check for repeated 4-byte or 16-byte patterns
        for step in [4, 8, 16]:
            if len(data) >= step * 4:
                chunks = [data[i:i+step] for i in range(0, min(len(data), step * 4), step)]
                if len(set(chunks)) < len(chunks) * 0.7:
                    return True
        return False

    def detect_all(self, data: bytes, offset: int = 0) -> dict:
        """Run all detection: patterns + analysis + recommendations."""
        analysis = self.analyze_buffer(data)
        recommendations = []

        for p in analysis["patterns_detected"]:
            if "AES" in p["pattern"]:
                recommendations.append("This is likely AES encryption. Check for key schedule and round function.")
            elif "CLEFIA" in p["pattern"]:
                recommendations.append("This is CLEFIA, a lightweight Japanese cipher (Sony).")
            elif "CRC" in p["pattern"]:
                recommendations.append("CRC-32 checksum detected. Used for data integrity.")
            elif "MD5" in p["pattern"]:
                recommendations.append("MD5 hash detected. Note: MD5 is cryptographically broken.")
            elif "SHA" in p["pattern"]:
                recommendations.append("SHA-256 hash detected.")
            elif "DES" in p["pattern"]:
                recommendations.append("DES cipher detected. Note: DES is broken, 3DES or AES recommended.")

        if analysis["likely_crypto"] and not analysis["patterns_detected"]:
            recommendations.append("High entropy data detected. Could be encrypted, compressed, or random.")

        analysis["recommendations"] = recommendations
        return analysis


# Singleton
_detector = None

def get_detector() -> PatternDetector:
    global _detector
    if _detector is None:
        _detector = PatternDetector()
    return _detector
