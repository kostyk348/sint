---
name: agents
description: Use when working with agent, multi-agent, pipeline, orchestration, tool use, memory, context. Multi-agent systems: pipelines, orchestration, verification, semantic integrity
---

> Multi-agent systems: pipelines, orchestration, verification, semantic integrity.

## WHEN ACTIVE
Building or analyzing agent systems, multi-LLM pipelines, orchestration logic, inter-agent protocols, semantic verification, audit trails.

## CORE PRINCIPLES

**No agent verifies itself.**
Self-verification is not verification. Every non-trivial output needs an independent checker — different model, different prompt framing, or deterministic validator.

**Semantic typing, always.**
Every message between agents carries a type: is it raw data, a verified fact, an inference, an opinion, or an execution plan? Untyped messages are bugs waiting to happen.

**Provenance is infrastructure, not an afterthought.**
Build audit trails from day one. Hash-chain or equivalent. Tamper-evident. Without provenance, debugging a multi-agent failure is archaeology.

**Trust is dynamic.**
An agent's reliability changes over time. Track it. An agent that consistently fails verification should lose privileges, not be silently tolerated.

## ARCHITECTURE PATTERNS

**Linear pipeline**
A → B → C. Simple, debuggable. Each stage has one job.
Use when: task is sequential, stages are independent.

**Quorum**
N agents independently process the same input, majority vote decides.
Use when: classification, high-stakes decisions, reducing single-model bias.
N=3, majority=2 for 1 fault tolerance. N=5 for 2 faults.

**Speaker + Critic**
One agent generates, another critiques. Different models preferred.
Use when: content generation where quality matters.

**Router + Specialists**
Router classifies task, dispatches to specialist agent.
Use when: diverse task types, each needing different expertise.

## WORKFLOW

```
1. DEFINE AGENT ROLES
   What does each agent produce? What register? (SENSE/FACT/LOGIC/OPINION/CAUSALITY)
   What are its inputs? What are its failure modes?

2. DEFINE VERIFICATION STRATEGY
   Who checks what? Is it quorum, independent verifier, or deterministic check?
   What happens on verification failure? (retry, escalate, log and continue)

3. DEFINE MESSAGE SCHEMA
   What fields does every inter-agent message have?
   Minimum: {type, content, source, confidence, actor, timestamp}

4. BUILD AUDIT TRAIL
   Every message logged. Hash-chain preferred.
   Include: actor, register, confidence, prev_hash.

5. DEFINE FAILURE MODES
   What does the system do when an agent times out?
   When verification fails repeatedly?
   When trust score drops below threshold?

6. TEST WITH ADVERSARIAL INPUTS
   What happens when one agent returns garbage?
   What happens when drift accumulates over many steps?
```

## ANTI-PATTERNS

- Single agent doing generation + verification
- Untyped messages between agents ("just pass the string")
- No audit trail — impossible to debug failures post-hoc
- All agents using the same model — correlated failures
- Trust score that never decreases — meaningless
- No recovery protocol — one failure kills the whole pipeline
- Infinite retry without backoff or escalation

## SINT-UA REGISTER REFERENCE
When implementing semantic typing, use or adapt these registers:
- `SENSE` — raw input, no interpretation
- `FACT` — verifiable claim, source required
- `LOGIC` — inference from FACT/SENSE, premises explicit
- `OPINION` — subjective, actor declared
- `CAUSALITY` — execution plan, step sequence
