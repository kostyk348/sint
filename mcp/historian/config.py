"""sint-historian-mcp configuration."""
from pathlib import Path

NAME = "sint-historian-mcp"
VERSION = "0.1.0"

BASE_DIR = Path(__file__).parent
CACHE_DIR = BASE_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# Session log analysis
ANALYZERS_DIR = BASE_DIR / "analyzers"
REPORTERS_DIR = BASE_DIR / "reporters"

# Memory system integration
MEMORY_BLOCKS_LIMIT = 100  # max blocks to fetch per query
PATTERN_MIN_OCCURRENCES = 2  # min times a pattern must occur to report
