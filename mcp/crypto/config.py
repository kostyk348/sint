"""sint-crypto-mcp configuration."""
from pathlib import Path

NAME = "sint-crypto-mcp"
VERSION = "0.1.0"

BASE_DIR = Path(__file__).parent
CACHE_DIR = BASE_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# Cipher database
CIPHERS_DIR = BASE_DIR / "ciphers"
TEST_VECTORS_DIR = BASE_DIR / "test_vectors"
PATTERNS_DIR = BASE_DIR / "patterns"

# Supported cipher families
CIPHER_FAMILIES = [
    "block", "stream", "hash", "aead", "signature",
    "kem", "pkc", "lwc", "lightweight",
]

# Default language for code generation
DEFAULT_LANG = "c"
SUPPORTED_LANGS = ["c", "python", "rust"]
