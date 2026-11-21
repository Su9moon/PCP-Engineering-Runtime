---
name: pcp-domain-bootstrap
description: Standard PCP domain bootstrap. Use when creating or formalizing a new PCP domain repository that inherits cross-domain governance from the PCP main repository.
---

# PCP Domain Bootstrap

References:
- `governance/PCP_SKILL_GOVERNANCE.md`
- `processes/architecture-governance-gate.md`

## Trigger

Use when a PCP capability or work domain is being split into, initialized as, or formalized as an independent repository.

## Required Inputs

- canonical PCP repository;
- domain name and target repository;
- exact upstream canonical baseline/governance path(s);
- approved domain responsibility and boundary;
- bootstrap workorder or explicit authorization.

## Procedure

1. **Check before create**
   - Verify whether the target domain repository already exists.
   - If it exists, inspect it first; do not rebuild or overwrite it blindly.

2. **Fix authority first**
   - Decide which definitions remain authoritative in the PCP main repository.
   - Decide which definitions are owned by the new domain.
   - Do not create two canonical copies of the same governance fact.

3. **Canonical first**
   - Cross-domain architecture, governance, or baseline truth must be committed to the canonical PCP repository before downstream bootstrap.
   - Record the exact upstream repository, path, version, and commit SHA.

4. **Pin the source**
   - Downstream bootstrap must reference a fixed upstream commit, not only a moving branch such as `main`.

5. **Create authorized snapshot**
   - Copy only authorized upstream baseline/governance input required for autonomous domain execution into `governance/snapshots/`.
   - Add provenance including upstream repository, exact path, source commit, version, and capture date.
   - Mark every snapshot explicitly as non-canonical downstream input.

6. **Fix the domain boundary and governance inheritance**
   - Domain `README.md` and `AGENTS.md` must state what the repository owns and does not own.
   - Domain `AGENTS.md` must route applicable Architecture / Generic Capability work through `processes/architecture-governance-gate.md`.
   - If the domain must operate without reading the upstream repository, provide an authorized non-canonical snapshot/reference of the gate process pinned to an exact upstream commit.
   - Required but incomplete architecture gates are a STOP condition.
   - A downstream repository may define its own contracts, models, runtime, implementation, tests, and local governance only within its approved boundary.

7. **Protect snapshot semantics**
   - Never edit a downstream snapshot to redefine upstream architecture.
   - Upstream changes must occur in the canonical repository first, then be explicitly re-snapshotted downstream.
   - Domain-specific rules may narrow execution but may not silently remove PCP-wide architecture gates.

8. **Stop at bootstrap scope**
   - Do not automatically continue into domain-specific schema, API, runtime, implementation, or feature design unless separately authorized.

## Snapshot Provenance Minimum

A snapshot must identify at least:

- upstream repository;
- upstream path;
- exact upstream commit;
- baseline/governance version;
- capture date;
- statement that upstream remains authoritative.

## Output

Return:

- canonical upstream commit/ref used;
- target domain repository;
- created/updated repository tree;
- snapshot path and provenance;
- inherited architecture-gate path/state;
- any deviation, conflict, or unresolved ownership question.

## Stop Conditions

Stop and report instead of guessing when:

- the target repository already exists with conflicting content;
- upstream authority is ambiguous;
- the required canonical baseline is missing;
- a requested snapshot cannot be tied to an exact upstream commit;
- architecture_gate is required but not complete or explicitly waived;
- the work would create a second canonical source for the same governance fact.

## Production Runtime Boundary

This Skill governs independent **engineering Domain repositories**. Its upstream governance snapshot mechanism is not a production product Release.

When a Domain also ships a deployable/runtime product:

- build/governance may consume upstream PCP canonical;
- the product must be packaged as an Approved Release with provenance/digests;
- production Runtime consumes the Installed Release;
- production Runtime must not require live access to the upstream PCP repository unless its Connectivity Contract explicitly says so;
- third-party Runtime deployment must not require the developer's PCP/Git credentials.

Use `governance/baselines/PCP_RELEASE_RUNTIME_INDEPENDENCE_BASELINE_V0.1_FIXED.md` for this boundary.
