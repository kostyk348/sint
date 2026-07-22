"""sint-embed-mcp configuration."""
from pathlib import Path

NAME = "sint-embed-mcp"
VERSION = "0.1.0"

BASE_DIR = Path(__file__).parent
CACHE_DIR = BASE_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# MCU database
MCU_DB_DIR = BASE_DIR / "mcu_db"
RTOS_DIR = BASE_DIR / "rtos"
GEN_DIR = BASE_DIR / "gen"

SUPPORTED_ARCHS = ["arm", "xtensa", "x86", "riscv"]
SUPPORTED_RTOS = ["itron", "toppers", "t-kernel", "freertos", "dso-tron"]
