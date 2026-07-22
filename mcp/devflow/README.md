# sint-devflow-mcp

Development workflow intelligence MCP server for the [SINT](https://github.com/kostyk348/sint-ua-v2.1) agent ecosystem.

Not a linter. A **knowledge base + planner** that helps the agent write code like a senior developer: iterative, tested, documented.

## Features

- **Pipeline Planning** — break features into verified steps with TDD guidance
- **Modular Style System** — language-specific coding rules (C99/Python/Rust + plugin architecture)
- **Code Review** — anti-pattern detection, naming conventions, TODO scanning
- **Commit Conventions** — Conventional Commits message generation
- **Edge Case Discovery** — systematic edge case brainstorming by domain
- **TDD Guide** — Red→Green→Refactor workflow templates

## Tools

### Pipeline Planning

| Tool | Description |
|---|---|
| `plan_feature(title, tasks)` | Break feature into verified pipeline steps |
| `get_next_action(pipeline_id)` | Get next actionable step with criteria |
| `update_step(pipeline_id, step_id, status)` | Mark step done/failed/blocked |

### Coding Style

| Tool | Description |
|---|---|
| `get_style_rules(language)` | Get coding style rules for a language |
| `code_review(code, language)` | Review code for violations + quality score |
| `list_languages()` | List registered style plugins |

### Commit Conventions

| Tool | Description |
|---|---|
| `commit_conventions()` | Get Conventional Commits rules |
| `make_commit_message(type, scope, desc)` | Generate commit message |

### Edge Cases & TDD

| Tool | Description |
|---|---|
| `discover_edge_cases(description)` | Systematic edge case discovery |
| `tdd_guide(task)` | TDD workflow for a specific task |

## Style Plugin System

Add a new language by creating a single file in `style/`:

```python
# style/javascript.py
from style.base import LanguageStyle

class JavaScriptStyle(LanguageStyle):
    name = "javascript"
    
    def get_config(self):
        return {
            "indent": 2,
            "line_length": 100,
            "naming": {"function": "camelCase", "class": "PascalCase"},
            "anti_patterns": [...]
        }
    
    def review_code(self, code):
        # Return {"score": float, "findings": [...]}
        ...
```

Zero changes to `server.py` — auto-discovered at runtime.

### Built-in Languages

| Language | Anti-patterns | Naming Rules |
|---|---|---|
| C99 | Buffer overflows, unbounded `strcpy`, missing null checks | snake_case, UPPER_CASE macros |
| Python | Mutable defaults, bare `except`, global state | snake_case, PascalCase classes |
| Rust | Unwrap chains, clone abuse, ignoring `Result` | snake_case, PascalCase types |

## Architecture

```
User task → plan_feature() → Pipeline (steps with verification)
                                    ↓
                            get_next_action() → agent executes
                                    ↓
                            update_step() → next step
```

## Setup

```bash
pip install fastmcp
```

## Run

```bash
python server.py    # stdio mode
```

## Example Session

```
1. plan_feature("ECHONET parser", ["define frames", "implement parser", "add tests"])
   → Pipeline with 3 steps, each with verification criteria + edge cases

2. get_next_action(pipe_id)
   → Step 1: "define frames" — test-first recommended, edge cases: empty payload, oversized

3. update_step(pipe_id, "s01", "done")
   → Step 2 unlocked: "implement parser"

4. make_commit_message("feat", "parser", "add ECHONET Lite frame definitions")
   → "feat(parser): add ECHONET Lite frame definitions"
```

## License

MIT
