"""sint-learner-mcp configuration."""
from pathlib import Path

NAME = "sint-learner-mcp"
VERSION = "0.1.0"

BASE_DIR = Path(__file__).parent
CACHE_DIR = BASE_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# Learner data (persists across sessions)
LEARNER_DIR = Path.home() / ".config" / "opencode" / "learner"
LEARNER_DIR.mkdir(parents=True, exist_ok=True)

ERRORS_FILE = LEARNER_DIR / "errors.json"
PATTERNS_FILE = LEARNER_DIR / "patterns.json"
SESSIONS_FILE = LEARNER_DIR / "sessions.json"
IMPROVEMENTS_FILE = LEARNER_DIR / "improvements.json"

# Thresholds
PATTERN_MIN_OCCURRENCES = 2  # N occurrences to flag as pattern
STALE_ERROR_DAYS = 30  # errors older than this need re-verification
