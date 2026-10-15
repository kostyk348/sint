# BEAUTY.md — что осталось за владельцем

Аудит (`repo_polish_audit.py`, прогон 14.10.2026) по этому репозиторию:

```
sint   ★3  2026-07-31 → нет тем
```

У воркера нет задачи ставить GitHub-метаданные, теги и релизы. Ниже — только то, чего не сделать
из репозитория. Запускать после публикации локального коммита из этой ветки.

## 1. Метаданные (описание, темы)

Описание есть, темы пустые:

```
desc: "SINT Agent Ecosystem — monorepo for all MCP servers, core memory system, and architecture docs"
topics: []
```

Готовая команда:

```bash
gh repo edit kostyk348/sint \
  --description "SINT — Structured Intelligence Network Topology: agent architecture as a cognitive system (perception / cognition / memory / feedback / identity / metacognition) — MCP servers, hash-chain memory, agents, skills, architecture docs. Apache-2.0." \
  --add-topic mcp \
  --add-topic mcp-servers \
  --add-topic ai-agents \
  --add-topic agent-architecture \
  --add-topic monorepo \
  --add-topic python \
  --add-topic memory
```

## 2. Тег/релиз — пока не предлагать

Правило портфеля: тег и релиз ставятся только там, где есть зелёный CI, иначе зелёный бейдж врёт.
В `sint` прогонять **нечего**:

```
sint/tests/ -> только .gitkeep (0 тестов)
.github/workflows -> отсутствует
CI на GitHub: прогонов нет (gh run list -R kostyk348/sint -> пусто)
```

Поэтому: сначала тесты, потом CI, потом тег. Ставить CI, который ничего не запускает, —
это пустышка, её в портфеле не держим.

Что реально можно проверить уже сейчас (и что стоит завернуть в тесты):

```bash
pip install -r requirements.txt          # fastmcp, httpx, fastembed, numpy, networkx, lief
cd mcp/crypto && python server.py        # проверено 15.10.2026 с установленным fastmcp:
                                         # FastMCP 4.1.0, Server: sint-crypto-mcp, слушает stdio
```

Так выглядит рабочая проверка для серверов на fastmcp: поднять процесс на stdio и вызвать
`initialize` + пару tools. Пока такого набора нет, honest CI для этого репозитория невозможен.

## 3. Отдельно — расхождения в README (не правил, это содержательные утверждения)

* `README.md:7` — «This monorepo contains the entire SINT ecosystem: 11 MCP servers …»,
  при этом каталогов серверов в `mcp/` шестнадцать (`algo`, `analogy`, `constraints`, `crypto`,
  `devflow`, `embed`, `historian`, `learner`, `logparser`, `metacog`, `portfolio`, `re-graph`,
  `replay`, `self`, `spec`, `working`) плюс `core/mcp/sint-memory`. Часть — плейсхолдеры с README
  без кода (появились в `5c1388c`), поэтому «11» и «16» расходятся не случайно: стоит явно
  разделить «работающие серверы» и «спецификации». Цифру выберет владелец.
