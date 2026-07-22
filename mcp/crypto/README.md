# sint-crypto-mcp

Cipher knowledge base + pattern detection + test vector validation + code generation for 25+ ciphers.

MCP server for the [SINT](https://github.com/kostyk348/sint-ua-v2.1) agent ecosystem.

## Purpose

When reverse-engineering or implementing cryptography, you need: known test vectors, algorithm identification, clean reference code, and pattern detection in binaries.

This MCP provides all four.

## Features

- **25+ Cipher Database** — block ciphers, stream ciphers, hash functions
- **Pattern Detection** — identify cipher implementations in binaries
- **Test Vector Validation** — verify implementations against known-good vectors
- **Code Generation** — clean C99 reference implementations
- **Side-Channel Awareness** — constant-time patterns, timing attack vectors

## Tools

| Tool | Description |
|---|---|
| `search_cipher(query)` | Find cipher by name, family, or property |
| `get_cipher(name)` | Full cipher details (rounds, block size, key sizes) |
| `get_test_vectors(cipher, variant)` | NIST/RFC test vectors |
| `validate_implementation(cipher, code)` | Check code against test vectors |
| `detect_cipher(binary_hex)` | Identify cipher patterns in hex dump |
| `generate_code(cipher, lang)` | Clean reference implementation |
| `compare_ciphers(names)` | Side-by-side comparison |
| `list_ciphers(family)` | Browse cipher database |

## Cipher Database

### Block Ciphers

| Cipher | Family | Block | Key Sizes | Notes |
|---|---|---|---|---|
| AES | Rijndael | 128 | 128/192/256 | NIST standard |
| Camellia | — | 128 | 128/192/256 | Japanese (NTT/Mitsubishi) |
| CLEFIA | — | 128 | 128/192/256 | Sony, ISO/IEC 29192 |
| SM4 | — | 128 | 128 | Chinese national standard |
| ChaCha20 | Stream | — | 256 | Bernstein, TLS 1.3 |

### Hash Functions

| Hash | Output | Notes |
|---|---|---|
| SHA-256 | 256 | NIST SHA-2 family |
| BLAKE2b | 512 | Faster than SHA-3 |
| MD5 | 128 | Broken, but still seen in legacy |

### Pattern Detection

Identifies cipher implementations in binaries by:
- S-box lookups (AES 16-byte tables)
- Round constants (AES Rcon, Camellia FL/FLINV)
- Key schedule patterns
- Known test vector outputs

```python
detect_cipher("063a8e48e5d7b5b1c8a3c9b8a1e3f5d2")
# → {"candidates": ["AES-128 (partial match)", "Camellia-128"]]}
```

### Test Vectors

```python
get_test_vectors("AES", variant="128-ECB")
# → NIST SP 800-38A vectors for AES-128-ECB
```

## Setup

```bash
pip install fastmcp
```

## Run

```bash
python server.py    # stdio mode
```

## Integration

Use when:
- Reverse-engineering crypto in binaries
- Implementing cipher from spec
- Validating existing implementation
- Comparing cipher properties for design decisions

## License

MIT
