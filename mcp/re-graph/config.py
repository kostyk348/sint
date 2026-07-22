"""sint-re-graph-mcp configuration."""
from pathlib import Path

NAME = "sint-re-graph-mcp"
VERSION = "0.1.0"

BASE_DIR = Path(__file__).parent
CACHE_DIR = BASE_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# Graph storage
GRAPH_DB = CACHE_DIR / "graphs.db"

# Embedding model (same as sint-self-mcp)
EMBED_MODEL = "BAAI/bge-small-en-v1.5"

# Pattern signature files
PATTERNS_DIR = BASE_DIR / "patterns"

# Node types
NODE_DATA = "data"       # buffer, struct, string, constant, variable
NODE_OPERATION = "operation"  # function, basic_block, loop, branch

# Edge types
EDGE_DATA_FLOW = "data_flow"      # data A → used by operation B
EDGE_CALL = "call"                 # function A calls function B
EDGE_TRANSFORM = "transform"       # operation A produces data B
EDGE_Taint = "taint_flow"          # from DataTrace: tainted data flows
EDGE_DATA_ACCESS = "data_access"   # operation reads/writes data

# Taint labels (matches DataTrace)
T_NETWORK = 0x01
T_FILE    = 0x02
T_ARGV    = 0x04
T_CONST   = 0x08
T_HEAP    = 0x10
T_STACK   = 0x20
T_UNTRUSTED = T_NETWORK | T_FILE | T_ARGV

TAINT_NAMES = {
    T_NETWORK: "network",
    T_FILE: "file",
    T_ARGV: "argv",
    T_CONST: "const",
    T_HEAP: "heap",
    T_STACK: "stack",
}
