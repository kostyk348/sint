---
name: dso
description: Use when working with DSO, MPTC, DataTrace, SINT, jitter, arena allocator, tick-aware, ensemble stability, non-minimum-phase, trust score, hash-chain, semantic register, taint tracking. Project-specific patterns from DSO, MPTC, DataTrace, SINT-UA, DSO Control
---

> Project-specific patterns from DSO, MPTC, DataTrace, SINT-UA, DSO Control.
> This skill contains verified and candidate patterns from real project experience.
> Update this file when something works — see AGENTS.MD §11.

## WHEN ACTIVE
Any task touching: deterministic scheduling, custom allocators, eBPF taint tracking,
multi-agent semantic systems, genetic programming for control, SINT register model.
Trigger keywords: DSO, MPTC, DataTrace, SINT, jitter, arena allocator, tick-aware,
ensemble stability, non-minimum-phase, trust score, hash-chain, semantic register.

---

## PROJECT MAP

### DSO — Deterministic Streaming OS
Research kernel/RTOS concept. Core goal: minimize scheduling jitter for streaming workloads.
Key insight: jitter reduction at the cost of mean throughput is an acceptable tradeoff
for real-time streaming. Worst-case matters more than average-case.

### MPTC — Memory Allocator
LD_PRELOAD allocator targeting tick-aware workloads. Iterated v1→v8000+.
Core idea: allocations classified by semantic type and lifecycle stage,
not just size. Arena/pool selection based on object lifetime prediction.

### DataTrace
eBPF-based taint tracking for legacy binary format reverse engineering.
64-bit shadow memory bitmasks per address. L-function for taint recombination.
Goal: automated understanding of data flow through stripped binaries.

### SINT-UA v2
Multi-agent semantic protocol. Register-typed messages (SENSE/FACT/LOGIC/OPINION/CAUSALITY).
Hash-chain audit log. Quorum voting. Trust scores. Recovery protocol.
Core invariant: no agent verifies its own output.

### DSO Control
Genetic programming for control system synthesis. Compares GP, PID, LQR
across multiple plant types including non-minimum-phase. Ensemble-based fitness.

### DSA — Data-oriented Streaming Audio
Open-source FMOD replacement at /home/lain/dsa/. Arena allocator per object type,
SoA (Struct of Arrays) channel layout, tick-based mixer, hash-chain audit.
ALSA output backend. C ABI + C++ ABI exported for LD_PRELOAD compat.
Verified on Slay the Spire 2.

---

## ARCHITECTURE PRINCIPLES (from project experience)

**Separation of concerns is load-bearing.**
In MPTC: allocation path, lifecycle tracking, and entropy scoring must be separate.
Mixing them caused bootstrap deadlocks (v1-v3) and overhead without benefit (v5+).
In SINT: generation, classification, verification must be separate agents/models.
Self-verification silently inherits bias.

**Measure before adding complexity.**
Entropy-aware wave selection in MPTC added overhead without measurable benefit
on real workloads. Lifecycle float arithmetic: same result. Complexity must earn its place
through benchmarks, not theoretical appeal.

**Tick-awareness is the key allocator insight.**
Standard allocators are tick-agnostic. MPTC's advantage came specifically from
aligning allocation/deallocation patterns with application tick boundaries.
This is the one thing that produced real numbers.

**Ensemble over nominal for robustness.**
DSO Control finding: optimizing for nominal plant performance produces controllers
fragile to parameter variation. Ensemble fitness (test across plant distribution)
produces controllers that stabilize more members at the cost of worse mean on nominal.
For safety-critical: ensemble approach is correct even if mean looks worse.

**Hash-chain is cheap and pays off.**
SINT audit log: adding prev_hash to each packet costs ~microseconds.
Benefit: complete tamper-evident provenance for post-hoc debugging.
Should be default in any multi-step agent pipeline, not an afterthought.

---

## VERIFIED PATTERNS

### tick-aligned arena allocation
- **Context**: MPTC v4, tick-aware workload benchmarks
- **Approach**: Separate arena per tick phase. Bulk-free at tick boundary instead of individual frees.
- **Result**: 10-18× improvement over glibc on tick-aware workloads (measured)
- **Verified**: Benchmark suite, multiple runs
- **Caveat**: Benefit disappears on non-tick-aware workloads. Overhead on random allocation patterns.
- **Date**: 2025

### ensemble fitness for GP control
- **Context**: DSO Control, non-minimum-phase plant
- **Approach**: Fitness function evaluated across ensemble of plant parameter variations, not just nominal
- **Result**: DSO-tuned PID stabilized significantly more ensemble members than classically tuned PID. Cost: worse mean performance on stable members.
- **Verified**: Python benchmark, multiple plant types
- **Caveat**: Mean performance metric will look worse. This is expected and correct for the use case.
- **Date**: 2025-2026

### quorum classification reduces single-model bias
- **Context**: SINT-UA v2 architecture
- **Approach**: 3 independent critic calls, majority vote for register classification
- **Result**: Eliminates systematic misclassification from single-model bias. Mock-mode verified unanimously.
- **Verified**: Design-level verification + mock demo run
- **Caveat**: All critics same model = correlated failures. Real benefit requires different models per critic.
- **Date**: 2026

### C function for C++ ABI symbol export
- **Context**: DSA FMOD replacement, C++ ABI symbols needed for LD_PRELOAD
- **Approach**: Define `_ZN4FMOD*` symbols as plain C functions (C doesn't mangle names, so symbol name = exact function name)
- **Result**: 205 C++ ABI symbols exported from libfmod.so + libfmodstudio.so without a C++ compiler. All GodotFmod imports satisfied.
- **Verified**: Slay the Spire 2 loads with "FMOD Sound System: Successfully initialized"
- **Caveat**: Only works for methods where `this` can be passed as first arg. Virtual dispatch would need vtable setup.
- **Date**: 2026-07-06

---

## CANDIDATE PATTERNS

### semantic object type classification in allocator
- **Hypothesis**: Classifying allocations by semantic type (string, buffer, struct, temp) enables smarter lifetime prediction and reduces fragmentation
- **Tried**: Implemented in MPTC v5+, but overhead measurement was inconclusive
- **Needs**: Benchmark on realistic mixed-type workload with clear semantic categories. Compare fragmentation, not just throughput.

### eBPF shadow memory for taint tracking (DataTrace)
- **Hypothesis**: 64-bit bitmask per address in BPF hash map, L-function for propagation, enables automated data flow reconstruction in stripped binaries
- **Tried**: Design phase, not fully implemented
- **Needs**: Working eBPF program on real target binary. Measure false positive rate on known data flows.

### TF-IDF drift detection in agent pipeline
- **Hypothesis**: TF-IDF cosine similarity between task embedding and packet embedding detects semantic drift before it causes pipeline failure
- **Tried**: Implemented in SINT-UA v2 mock mode. Drift values increased predictably (0.48→0.66) across pipeline steps.
- **Needs**: Test with real LLM calls where actual drift occurs. Calibrate θ threshold on real failure cases.

### madvise differentiation by lifecycle stage
- **Hypothesis**: Calling madvise(MADV_FREE) on arenas entering idle lifecycle and madvise(MADV_WILLNEED) before active phase reduces RSS without hurting latency
- **Tried**: Implemented in MPTC, not benchmarked in isolation
- **Needs**: Isolated benchmark measuring RSS delta and latency impact separately.

---

## KNOWN DEAD ENDS

These approaches were tried and found to add overhead without measurable benefit.
Do not revisit without a specific new hypothesis for why conditions have changed.

| Approach | Project | Why it failed |
|---|---|---|
| Entropy-aware wave selection | MPTC v5+ | Added computation overhead, no measurable allocation quality improvement on real workloads |
| Lifecycle float arithmetic | MPTC | Floating point ops in hot allocation path, overhead > benefit |
| Single-agent self-verification | SINT v1 | Inherits model bias, integrity check was always PASS (hardcoded) |
| Bigram embeddings for drift | SINT v1 | Too coarse (64-dim hardcoded), no IDF weighting, poor semantic signal |
| E-STOP without recovery | SINT v1 | Fatal halt on drift, no way to resume. Recovery protocol needed. |

---

## CROSS-REFERENCES

- Low-level allocation details → `memory.md`
- eBPF implementation patterns → `ebpf.md`
- Control system theory → `control.md`
- Agent architecture patterns → `agents.md`
- Benchmarking methodology → `perf.md`, `stats.md`
