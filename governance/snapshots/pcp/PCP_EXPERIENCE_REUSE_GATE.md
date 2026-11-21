# Experience Reuse Gate

## Purpose

Make existing PCP experience influence future execution before new conclusions, work orders, or generic mechanisms are produced. This is a lightweight retrieval and classification rule, not a runtime subsystem.

## Scope

The gate applies to existing PCP projects. It does not:

- create or change tagging or schema conventions;
- build databases, RAG, vector search, or retrieval services;
- modify FIXED baselines;
- package Skills by itself.

## Trigger A - Session Bootstrap

Run once when a new Codex/execution conversation starts for an existing PCP project.

Minimum behavior:

1. Read repository `AGENTS.md`.
2. Read current project status / README and the current Git baseline.
3. Search relevant approved governance.
4. Search relevant validated and candidate experience.
5. Consult Inbox sources only when the first three searches do not resolve the task context.
6. Load only task-relevant fragments, never the whole experience repository.

Stop as soon as the needed context is loaded. Do not scan every asset or reproduce whole source files in the conversation.

## Trigger B - Decision Reuse Gate

Run before:

- drafting a PCP or PCP-project implementation work order;
- proposing a reusable engineering pattern;
- introducing or changing governance or process;
- proposing a new generic PCP mechanism.

Procedure:

1. Identify the decision type and the task-relevant scope.
2. Search approved governance first, then `assets/validated/`, then `assets/candidates/`; consult `assets/inbox/sources/` only when needed.
3. Load only the fragments required to decide.
4. Classify the finding.

### Classification

- `REUSE` - existing approved guidance or asset already covers the decision; use it as approved guidance.
- `EXTEND` - the existing guidance or asset is correct but needs a small, scoped extension; the extension remains a separately reviewed change.
- `NEW_CANDIDATE` - no suitable existing asset exists and the finding may transfer beyond the current project; record it as a candidate only after review.
- `PROJECT_LOCAL` - the finding is useful only in the current project; keep it local and do not promote it.

Governance and validated assets may be reused as approved guidance. Candidate and Inbox assets are evidence, not automatically authoritative.

If the decision involves a new PCP Core concept, reusable Engine/Manager/Store/Router, multi-project infrastructure, or other generic mechanism, the existing `.agents/skills/cross-domain-discovery/SKILL.md` gate remains additionally required.

## Stop Rules

- Do not promote Inbox or Candidate assets during this gate.
- Do not package Skills from this gate.
- Do not load the full experience repository or rewrite existing asset metadata.
