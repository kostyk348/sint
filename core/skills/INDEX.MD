# SKILLS INDEX
> Part of AGENTS.MD framework. Read this file first, then load only the relevant skill(s).
> Version 1.0 — model-agnostic, platform-agnostic.

---

## HOW TO USE THIS INDEX

### Automatic selection (preferred)
Before starting any task, scan the user's request and match it against the trigger keywords below.
Load the skill file(s) that match. If multiple skills match, load all relevant ones — they are designed to compose.
If no skill matches clearly, proceed with AGENTS.MD core only and note the gap.

### Manual override
User can explicitly request a skill: `/skill <name>` or "use reverse skill".
In this case, load that skill regardless of auto-detection.

### Selection algorithm
```
1. Extract nouns and verbs from the task.
2. Match against TRIGGERS column below.
3. If confidence > 0.6 → load skill automatically.
4. If confidence 0.3–0.6 → load skill, note uncertainty.
5. If confidence < 0.3 → skip, use core AGENTS.MD only.
6. Never load more than 4 skills simultaneously (token budget).
7. If >4 match, prefer the most specific over the most general.
```

### Token budget awareness
Each skill is ~300–500 tokens. Loading 4 skills = ~2000 tokens overhead.
For simple tasks, 1 skill is enough. For complex multi-domain tasks, load up to 4.
When in doubt: load fewer, do better.

---

## SKILL REGISTRY

### SYSTEMS & LOW-LEVEL

| Skill | File | Triggers | Use when |
|---|---|---|---|
| **systems** | systems.md | kernel, RTOS, OS, driver, syscall, interrupt, scheduler, IPC, memory map | Working on OS-level code, drivers, real-time systems |
| **kernel** | kernel.md | kernel module, kthread, IRQ, DMA, mmap, /proc, /sys, eBPF, kprobe | Linux/Windows kernel internals, modules, tracing |
| **embedded** | embedded.md | MCU, firmware, bare metal, UART, SPI, I2C, GPIO, flash, bootloader | Microcontrollers, firmware, hardware interfaces |
| **asm** | asm.md | assembly, disassembly, registers, opcodes, calling convention, stack frame, x86, ARM, MIPS | Reading/writing assembly, ABI analysis |
| **memory** | memory.md | allocator, heap, stack, leak, buffer, arena, mmap, malloc, free, UAF, OOB | Memory management, allocators, corruption analysis |
| **perf** | perf.md | latency, throughput, jitter, benchmark, profiling, cache, branch, pipeline, perf stat | Performance analysis, optimization, benchmarking |

### REVERSE & SECURITY

| Skill | File | Triggers | Use when |
|---|---|---|---|
| **reverse** | reverse.md | reverse engineering, decompile, disassemble, binary, Ghidra, IDA, radare, stripped | Analyzing unknown binaries, game formats, protocols |
| **binary** | binary.md | ELF, PE, COFF, section, segment, symbol, reloc, dynamic linking, loader | Binary format analysis, linker internals |
| **ebpf** | ebpf.md | eBPF, bpftrace, kprobe, uprobe, tracepoint, XDP, tc, libbpf, BCC | eBPF programs, kernel tracing, network filtering |
| **fuzzing** | fuzzing.md | fuzzer, AFL, libFuzzer, corpus, coverage, sanitizer, ASAN, crash triage | Fuzzing targets, crash analysis, sanitizer usage |
| **exploit** | exploit.md | exploit, ROP, shellcode, vulnerability, CVE, mitigation, ASLR, NX, canary | Vulnerability research, exploit development |

### CODE & DEVELOPMENT

| Skill | File | Triggers | Use when |
|---|---|---|---|
| **code** | code.md | write code, implement, function, class, module, library, algorithm | General coding tasks across any language |
| **debug** | debug.md | bug, crash, error, segfault, exception, trace, reproduce, bisect | Debugging any kind of failure |
| **refactor** | refactor.md | refactor, clean up, restructure, simplify, technical debt, coupling | Improving existing code structure |
| **test** | test.md | test, unit test, integration, coverage, mock, fixture, TDD | Writing or fixing tests |
| **api** | api.md | API, REST, HTTP, endpoint, request, response, auth, rate limit, schema | Designing or consuming APIs |
| **git** | git.md | git, commit, branch, merge, rebase, conflict, history, bisect | Git operations, history analysis |

### DATA & MATH

| Skill | File | Triggers | Use when |
|---|---|---|---|
| **data** | data.md | dataset, CSV, JSON, parse, transform, pipeline, ETL, pandas, numpy | Data processing, transformation, analysis |
| **math** | math.md | equation, formula, proof, algebra, calculus, linear algebra, numerical | Mathematical reasoning, derivations |
| **ml** | ml.md | model, training, loss, gradient, neural network, inference, fine-tune | Machine learning, model analysis |
| **control** | control.md | PID, LQR, controller, plant, stability, transfer function, genetic programming, GP | Control systems, controller synthesis |
| **stats** | stats.md | statistics, distribution, hypothesis, p-value, regression, variance, correlation | Statistical analysis, experiment design |

### AGENTS & AI

| Skill | File | Triggers | Use when |
|---|---|---|---|
| **agents** | agents.md | agent, multi-agent, pipeline, orchestration, tool use, memory, context | Building or analyzing agent systems |
| **protocols** | protocols.md | protocol, message format, serialization, schema, versioning, wire format | Designing communication protocols |
| **prompts** | prompts.md | prompt, system prompt, instruction, few-shot, chain-of-thought, template | Prompt engineering, instruction design |
| **eval** | eval.md | evaluation, benchmark, metric, score, comparison, ablation | Evaluating AI/agent system quality |

### RESEARCH & WRITING

| Skill | File | Triggers | Use when |
|---|---|---|---|
| **research** | research.md | research, paper, literature, survey, prior work, citation, hypothesis | Academic or technical research tasks |
| **writing** | writing.md | write, document, explain, article, post, readme, report | Technical writing, documentation |
| **docs** | docs.md | documentation, docstring, API doc, changelog, spec, RFC | Writing formal documentation |
| **review** | review.md | review, critique, feedback, assess, evaluate, code review | Reviewing code, papers, designs |

### SESSION & WORKFLOW

| Skill | File | Triggers | Use when |
|---|---|---|---|
| **wiki** | wiki.md | artifact, registry, script, benchmark, prototype, create, check if exists, WIKI | Registering or checking for existing artifacts before creating something new |
| **state** | state.md | session, focus, project status, pending decision, continuation, resume, log, STATE | Managing session state, tracking active projects, saving/restoring context (legacy) |
| **memory-system** | memory-system.md | memory, block, chain, hash, provenance, session log, state.json, structured memory | Structured memory with hash-chain provenance. Use for reading/writing memory blocks, session management, verifying chain integrity. Replaces flat STATE.MD. |
| **owner** | owner.md | konstantin, preference, decision style, anti-preference, owner, calibration | Aligning agent behavior with Konstantin's preferences and avoiding known mistakes |

### PROJECT-SPECIFIC

| Skill | File | Triggers | Use when |
|---|---|---|---|
| **dso** | dso.md | DSO, MPTC, DataTrace, SINT, jitter, tick-aware, arena, ensemble stability, non-minimum-phase, trust score, hash-chain, semantic register, taint tracking | Any task touching Konstantin's core projects. Load this first if any trigger matches — it contains verified patterns unavailable elsewhere. |

### PLATFORM-SPECIFIC

| Skill | File | Triggers | Use when |
|---|---|---|---|
| **linux** | linux.md | Linux, bash, shell, systemd, cgroup, namespace, proc, apt, pacman | Linux-specific tasks, sysadmin |
| **windows** | windows.md | Windows, PowerShell, registry, WinAPI, COM, DLL, PE, NTFS | Windows-specific tasks, WinAPI |
| **vita** | vita.md | PS Vita, vitasdk, vita2d, SceKernel, homebrew, VPK, SELF | PS Vita homebrew development |
| **android** | android.md | Android, ADB, APK, Termux, JNI, Binder, NDK | Android development or tooling |
| **web** | web.md | HTML, CSS, JavaScript, browser, DOM, fetch, CORS, WebSocket | Web frontend or browser-side tasks |

---

## COMPOSITION EXAMPLES

**"Debug a kernel panic in my RTOS driver"**
→ Load: `kernel` + `debug` + `systems`

**"Write a eBPF taint tracker for binary analysis"**
→ Load: `ebpf` + `reverse` + `binary`

**"Benchmark my genetic programming controller vs PID"**
→ Load: `control` + `perf` + `stats`

**"Write documentation for SINT-UA v2 protocol"**
→ Load: `protocols` + `docs` + `agents`

**"Port VitaTube to use a different API"**
→ Load: `vita` + `api` + `code`

**"Analyze crash in PS Vita homebrew memory allocator"**
→ Load: `vita` + `memory` + `debug`

---

**"Start new session — continue MPTC allocator"**
→ Load: `state` + `owner` + `dso` + `memory`

**"Create a benchmark script for MPTC"**
→ Load: `wiki` + `dso` + `perf`

**"Continue work on MPTC allocator"**
→ Load: `dso` + `memory` + `perf`

**"Add taint tracking to DataTrace"**
→ Load: `dso` + `ebpf` + `reverse`

**"Tune GP fitness for DSO Control"**
→ Load: `dso` + `control` + `stats`

**"Start session with structured memory"**
→ Use agent: `sint-scribe` → reads `memory-system` + `state` + `owner`

**"Verify this code change is correct"**
→ Use agent: `sint-critic` → checks register compliance + logical integrity

**"Classify this complex task"**
→ Use agent: `sint-router` → produces JSON classification + routing

---

## SKILL UPDATE REMINDER

When a session produces a verified pattern:
1. Identify which skill file owns it (or create new)
2. Write it under `## VERIFIED PATTERNS` per AGENTS.MD §11 format
3. If unverified but promising → `## CANDIDATE PATTERNS`
4. Update INDEX.MD triggers if new keywords emerged

The `dso.md` skill is the highest-priority file to keep updated —
it contains knowledge unavailable to the base model.

---

## GAPS & UNKNOWN TASKS

If no skill matches:
1. Proceed with AGENTS.MD core only.
2. At the end of your response, note: `[SKILL GAP: suggest adding skill for <domain>]`
3. This allows the skill library to grow organically from real usage.
