---
name: cross-domain-discovery
description: Scan direct analogs, adjacent domains, and structurally analogous fields before PCP creates a new core abstraction, reusable infrastructure, or general-purpose mechanism. Use when Architecture Governance Gate classifies work as Architecture / Generic Capability. Do not use for routine bugs, ordinary work orders, or already-approved implementation details.
---

# Cross-Domain Discovery

References:
- `governance/baselines/PCP-01_系统定位与核心边界_V0.2_FIXED.md`
- `processes/architecture-governance-gate.md`

## Job to be done

Before designing a new general-purpose PCP mechanism, determine whether the need is real, whether the problem has already been solved elsewhere, and what irreducible PCP-specific remainder actually remains.

The goal is not to collect many links. The goal is to reduce the design space and decide:

`REUSE / INTEGRATE / BORROW / BUILD / DEFER`

This Skill is a discovery and architecture-governance method. It is not a PCP runtime component.

## Governing principle

> Problem First, Domain Second.

Do not begin by assuming the answer must be a new PCP component.

`PCP owns semantics` does not mean `PCP models everything in advance`.

## Trigger

Use this Skill when the Architecture Governance Gate requires it, including when:

- a new PCP Core concept is proposed;
- a reusable `Engine`, `Manager`, `Store`, `Router`, or similar abstraction is proposed;
- the same problem has appeared repeatedly and is about to be formalized;
- the mechanism would be reused by multiple projects;
- the proposal creates long-lived infrastructure;
- the team says or implies “we may need to build our own generic solution”;
- the topic is a long-lived mechanism around Memory, Agent, Learning, Governance, State, Evidence, runtime, persistence, policy, or integration.

Do not trigger by default for:

- a clear bug;
- a small feature with an established pattern;
- a routine work order;
- implementation inside an already-approved architecture.

## Workflow

### Step 0 — Confirm real-use evidence

Record why this capability needs durable treatment now.

Valid evidence includes repeated real tasks, real failures or maintenance burden, POC gaps, production behavior, validated integration constraints, or a user-approved architecture problem grounded in current work.

If there is no real-use evidence, default to `DEFER` or a narrowly scoped POC. Do not formalize a complete mechanism merely because it may be useful later.

### Step 1 — Rewrite the problem structurally

Convert the domain-specific request into a domain-neutral problem statement.

### Step 2 — Direct Analog

Search the same product or technology class and capture only solutions that materially address the structural problem.

### Step 3 — Adjacent Domain

Search mature neighboring disciplines that have handled similar constraints for years, such as durable execution, distributed systems, SRE, CI/CD, event sourcing, provenance, or knowledge management when relevant.

### Step 4 — Structural Analog

Ask which fields face the same problem structure even though the surface domain differs. This step is mandatory when the Gate is required.

### Step 5 — Inspect real evidence

Prefer, in order:

1. source code / official technical docs;
2. primary papers;
3. real benchmark or production evidence;
4. credible implementation reports;
5. secondary commentary only as discovery leads.

Do not treat a polished demo or README claim as proof of production maturity.

### Step 6 — Compare against PCP boundaries

For each serious candidate, answer:

- What problem does it actually solve?
- What assumptions does it make?
- Which layer should own it?
- Can PCP reuse it directly?
- Can PCP integrate it as an external provider?
- Is only the design pattern useful?
- Would adopting it expand PCP Core unnecessarily?
- What remains PCP-specific after reuse/integration/borrowing?

Provider/runtime-specific complexity must terminate at the Adapter / Integration Boundary.

### Step 7 — Decide

Choose one:

- **REUSE** — use the existing implementation;
- **INTEGRATE** — connect to it through an interface/provider/adapter;
- **BORROW** — reuse the mechanism or design principle only;
- **BUILD** — build only after evidence and the external scan prove a real PCP-specific remainder;
- **DEFER** — do not build now.

`BUILD` is not the default.

### Step 8 — Minimum formalization

After identifying the remainder, recommend the smallest durable form required now:

`reference / rule / workorder field / contract / canonical object / persistent schema / runtime component`

Do not promote a concept to an object, schema, or runtime component when a lighter form is sufficient.

### Step 9 — Produce the compact result

Use this minimum result:

    Real-use Evidence:
    verified | insufficient

    Structural Problem:
    ...

    Cross-Domain Scan: COMPLETE

    Direct Analog:
    - ...

    Adjacent Domain:
    - ...

    Structural Analog:
    - ...

    Decision:
    REUSE | INTEGRATE | BORROW | BUILD | DEFER

    PCP-specific remainder:
    ...

    Minimum formalization:
    ...

    Core-boundary impact:
    none | additive | requires ADR

    Evidence / uncertainty:
    ...

## Architecture Gate rule

If the scan is required, architecture design must not proceed until the scan has a decision, a PCP-specific remainder, and a minimum-formalization recommendation.

A workorder or architecture record uses the gate record defined in `processes/architecture-governance-gate.md`.

If waived, state why.

## Non-goals

This Skill does not create a Discovery Engine, knowledge graph, research runtime, autonomous crawler, generic Agent Framework, or new database.

External discoveries calibrate PCP; they do not automatically expand PCP.
