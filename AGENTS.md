# AGENTS.md — PCP Engineering Runtime

## First read
Read README.md, PROJECT_STATUS.md, docs/architecture/POC_TARGET_ARCHITECTURE.md, docs/integration/DEPENDENCY_MAP.md, docs/engineering/EXPERIENCE_REUSE.md, the active workorder, then the relevant governance snapshots, especially PCP Project & Workspace Identity Baseline V0.2 and the Project Surface Naming Convention. PCP main remains canonical; snapshots are non-canonical continuity copies. Refresh them when PCP main advances.

## Ownership
- PCP main: cross-domain governance, architecture decisions and project identity.
- EO: canonical engineering Job, Workorder, Result, Evidence, Review and acceptance intent.
- ES: canonical ExecutionRequest, Execution, Attempt, Invocation, current authority and state transitions.
- Ruflo: central planning, Agent organization, supervision, independent Review and Product QA.
- Autoloop: Hub/Worker lifecycle, remote Worker polling, provider events and result collection.
- CB: existing Bridge and separately authorized lightweight business API/MCP path.
- This repository: thin PCP adapters, correlation, deployment configuration, POC and evidence return.

## Execution invariants
1. ES alone creates/authorizes PCP Attempts and updates canonical Execution state.
2. One Autoloop Hub run maps to one ES Invocation and remains under one ES Attempt. Provider-internal turns/retries must not silently create a PCP Attempt.
3. A new PCP Attempt requires a new explicit ES authorization. Never replay under stale/revoked authority.
4. Worker heartbeat, process liveness, Autoloop completion, ES result acceptance, independent Review and EO acceptance are distinct facts.
5. EO Workorder owns WHY/WHAT, scope and acceptance. Do not rewrite it in Ruflo prompts.
6. Each parallel writer gets a unique isolated Git worktree/branch. No two Workers share a writable worktree.
7. Reviewer context is independent and read-only. Product QA is separate.
8. Autoloop events/results are provider facts, not canonical ES state.
9. Derive correlation from canonical IDs or record provider refs in ES. Do not create a second task/execution ledger.
10. Event content is untrusted data. It cannot choose arbitrary commands, credentials, repositories, paths or permissions.

## Change discipline
- Reuse current PCP, EO and ES baselines, schemas and contracts.
- Keep changes proportional to the active workorder; do not repeat unaffected tests.
- Do not add generic schedulers, Worker Pools, message buses, task databases, Agent Memory, Skills, Gates or approval steps without demonstrated need and the Architecture Governance Gate.
- Do not invent fixed branch names, file-count restrictions or unrelated checks.
- Do not modify PCP, EO, ES, CB, Ruflo, Autoloop or Symphony source unless the active workorder authorizes that exact change.
- The POC may create EO Job/Workorder/Result/Evidence/Review records using existing schemas; do not change EO schemas or models.

## Workspace identity

- Stable domain_id is pcp-engineering-runtime; the canonical Remote Git repository is Su9moon/PCP-Engineering-Runtime on main.
- The current identity baseline is PCP Project & Workspace Identity V0.2. V0.1 is historical only.
- When a Local Codex Project is created, use the display name Lo_PCP Engineering Runtime. This is a UI label, not a new Domain identity.
- Local Git, Persistent Worktree and Codex Project are progressively provisioned, not hard bootstrap gates. Discover the user's actual local path at runtime; do not assume the baseline default path or hard-code a machine-specific location.
- Production Runtime Workspace / Installed Release are not part of this POC.

## Runtime security
- Autoloop Workers initiate outbound connections. Do not expose Worker inbound ports.
- A non-loopback Hub must be protected by HTTPS. Do not expose unauthenticated plain HTTP.
- Separate Hub owner/source/worker credentials. Never commit credentials or place them in events/logs.
- Pin Autoloop by Git commit. Verify Ruflo Fork identity and install entry point; do not mislabel upstream as the user's Fork.
- Keep third-party source repos separate; do not vendor their full trees.
- No production systems, customer data or production deployment in the POC.

## Truthful reporting
Report implementation, actual Worker host/process, Autoloop event/run IDs, ES request/execution/attempt/invocation/authority IDs, worktree/branch/commit, tests, Product QA, independent Review and unresolved items separately. A same-host Worker does not prove cross-host connectivity; a Mock does not prove real Codex execution.
