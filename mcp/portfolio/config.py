"""sint-portfolio-mcp configuration."""
from pathlib import Path

NAME = "sint-portfolio-mcp"
VERSION = "0.1.0"

BASE_DIR = Path(__file__).parent
CACHE_DIR = BASE_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# Portfolio data
PORTFOLIO_DIR = Path.home() / ".config" / "opencode" / "portfolio"
PORTFOLIO_DIR.mkdir(parents=True, exist_ok=True)

PROJECTS_FILE = PORTFOLIO_DIR / "projects.json"
LINKS_FILE = PORTFOLIO_DIR / "links.json"
NOTES_FILE = PORTFOLIO_DIR / "notes.json"
