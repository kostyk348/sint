"""sint-working-mcp configuration."""
from pathlib import Path

NAME = "sint-working-mcp"
VERSION = "0.1.0"

BASE_DIR = Path(__file__).parent
CACHE_DIR = BASE_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# Working memory files (per-session, on disk)
WORKING_DIR = Path.home() / ".config" / "opencode" / "working"
WORKING_DIR.mkdir(parents=True, exist_ok=True)

TASK_FILE = WORKING_DIR / "task.json"
FINDINGS_FILE = WORKING_DIR / "findings.json"
BELIEFS_FILE = WORKING_DIR / "beliefs.json"
OPEN_FILE = WORKING_DIR / "open.json"
SESSION_LOG = WORKING_DIR / "session_log.json"

# Compression threshold: compress conversation every N messages
COMPRESS_EVERY = 15

# Confidence thresholds
CONFIDENCE_HIGH = 0.85
CONFIDENCE_MEDIUM = 0.60
CONFIDENCE_LOW = 0.35
