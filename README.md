# PCP Engineering Runtime

**Domain ID:** `pcp-engineering-runtime`  
**Repository:** [Su9moon/PCP-Engineering-Runtime](https://github.com/Su9moon/PCP-Engineering-Runtime)  
**Status:** Bootstrap complete; first vertical POC ready for Codex execution.

PCP Engineering Runtime is the integration domain for complex, multi-node engineering execution. It reuses Ruflo for central supervision and Agent Autoloop for Hub/Worker execution, while preserving PCP's existing engineering intent and execution authority.

This repository owns the PCP-specific integration adapters, deployment configuration, execution correlation, independent review / product-QA handoff, and evidence return. It does not reimplement the upstream agent runtime or PCP's canonical task/execution ledgers.

## Execution lanes

| Lane | Use | Path |
|---|---|---|
| L0 — business API | Simple dashboard/business tasks | Application → authorized CB/API adapter → external API → structured result → application |
| L1 — single-node engineering | Small, bounded code changes | Workorder → ES authorization → Autoloop Hub → one Worker → Codex → evidence / review |
| L2 — supervised multi-node engineering | Complex cross-module or parallel engineering | Workorder → ES authorization → Ruflo Supervisor → Autoloop Hub → multiple isolated Workers → independent Review / Product QA → evidence |

L0 is a separate lightweight path. It must not start Ruflo or Autoloop. This POC does not modify CB or assume that a generic business-API adapter is already implemented there.

## Authority boundaries

| Component | Owns | Does not own |
|---|---|---|
| PCP main | Cross-domain governance, architecture decisions, project identity, approved experience | Live worker/run state |
| EO | Engineering Job, Workorder, Result, Evidence, Review intent and acceptance | Runtime process / worker state |
| ES | ExecutionRequest, Execution, Attempt, Invocation, current execution authority and state transitions | Provider-internal scheduling and process state |
| Ruflo | Complex-task planning, Agent organization, supervision, independent Review and Product QA | PCP canonical Execution / Attempt state or production authorization |
| Autoloop | Hub/Worker lifecycle, remote worker polling, provider run events and provider result collection | PCP canonical Attempt authorization or engineering acceptance |
| CB | Existing bridge plus separately authorized lightweight API/MCP integration | General-purpose multi-agent orchestration / Worker Pool |
| This repository | Thin adapters, correlation, integration configuration, POC and evidence | A second Job/Workorder/Execution/Attempt ledger |

**Core invariant:** one PCP Attempt is authorized by ES. One Autoloop Hub run is correlated to one ES Invocation. Autoloop's internal turns/retries remain provider-internal facts under that same Attempt; a new PCP Attempt requires a new ES authorization.

## Start here

1. [AGENTS.md](AGENTS.md) — project execution rules and boundaries.
2. [PROJECT_STATUS.md](PROJECT_STATUS.md) — current state, pinned inputs, and unresolved dependencies.
3. [Target POC architecture](docs/architecture/POC_TARGET_ARCHITECTURE.md).
4. [Dependency map](docs/integration/DEPENDENCY_MAP.md).
5. [Experience reuse](docs/engineering/EXPERIENCE_REUSE.md).
6. [Codex vertical POC workorder](workorders/WO-20261122-001-VERTICAL-POC.md).

## Governance

- PCP main remains the canonical source for global governance and this project's architecture decision.
- Files under `governance/snapshots/pcp/` are exact, commit-pinned, **non-canonical snapshots** for downstream execution continuity. They do not override PCP main.
- Before changing architecture or adding a generic capability, follow the snapshot of the PCP Architecture Governance Gate and refresh the upstream baseline if PCP main has advanced.
- Reuse existing EO / ES contracts and schemas. Do not create a parallel task store, scheduler, generic Worker Pool, message bus, or Agent Memory platform.

## Current delivery boundary

The repository bootstrap and POC specification are complete. Ruflo + Autoloop have **not** yet been integrated or validated in a live multi-host run. The next step is the real vertical POC described in the workorder.

The repository is Public because it was created with that visibility. No license file has been added; Public visibility alone does not grant a reuse license. Third-party dependencies remain separate repositories and are pinned by commit.
