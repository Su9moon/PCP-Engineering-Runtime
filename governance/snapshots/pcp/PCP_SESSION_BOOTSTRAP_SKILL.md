---
name: pcp-session-bootstrap
description: Deterministic entry into an existing PCP project. Use once when a new GPT, Codex, Agent, or execution conversation starts work on an existing project.
---

# PCP Session Bootstrap

References:
- `governance/PCP_SKILL_GOVERNANCE.md`
- `governance/PCP_EXECUTION_PROFILE_RESOLUTION_BASELINE.md`
- `governance/PCP_EXECUTION_ENVIRONMENT_RESOLUTION_BASELINE.md`
- `processes/experience-reuse-gate.md` — Session Bootstrap
- `processes/architecture-governance-gate.md`
- `governance/PCP_ENGINEERING_AGILITY_PRINCIPLE.md` — user-directed ban on arbitrary engineering/upgrade constraints

## Rules

**Execution precedence:** After reading root `AGENTS.md`, apply the current user-directed engineering agility principle. Do not silently upgrade historical MVP implementation constraints (fixed branch, file count/subset, extra identity/approvals) into new task blockers; reuse the existing instance/mechanism and retain only demonstrated safety/authorization constraints. This adds no new review step.


1. Start from an explicit repository plus exact workorder/entry path; do not reconstruct the task from chat memory.
2. Read repository-root `AGENTS.md`, then the exact entry/workorder path and the exact references it names.
3. Apply the Session Bootstrap section of `processes/experience-reuse-gate.md`; load only task-relevant context.
4. Inspect the workorder `architecture_gate` before architecture or implementation work begins.
5. If `architecture_gate.required = true`, proceed only when status is `complete` or explicitly justified `waived`.
6. If `architecture_gate` is missing on work that may change architecture or create a reusable/general mechanism, stop and classify the task using `processes/architecture-governance-gate.md`.
7. Read the workorder `execution_profile` and resolve the actual model/effort using `governance/PCP_EXECUTION_PROFILE_RESOLUTION_BASELINE.md`.
8. Treat the workorder profile as a recommendation: allow explicit human override and Runtime fallback, but never replace or degrade silently.
9. Record complete execution evidence. For non-safety-critical Runtime fields that are not exposed, use `NOT_EXPOSED_BY_RUNTIME`, classify the evidence as `runtime_unobservable`, continue automatically, and report the warning at completion.
10. Missing execution telemetry alone is not a STOP condition and does not require Human Confirmation. Real authority, scope, safety, destructive-operation, protected-data, or canonical-identity failures remain fail-closed.
11. Read `execution_environment`; resolve expected values only from its authorized sources and canonical precedence. Do not convert historical/configuration evidence into current actual Runtime facts.
12. Before environment-sensitive execution, perform the required Runtime/preflight confirmation. Missing non-critical environment metadata may continue with an audit warning; a required critical compatibility field that is mismatched or unobservable follows the Workorder mismatch policy and MUST NOT be guessed.
13. Do not scan the whole repository or experience store to guess missing facts.
14. If the entry path or a required governing reference is missing/conflicting, stop and report.

## Governance preflight

Expected order:

    read repository AGENTS.md
    -> read exact workorder
    -> inspect architecture_gate
    -> if required and incomplete: STOP and complete Gate
    -> read exact governing references
    -> resolve recommended vs actual execution
    -> record execution evidence
    -> resolve expected execution environment
    -> confirm current environment when required
    -> record environment evidence
    -> execute authorized work

The executor must never infer that a missing gate means `not required`.

## Ready State

Proceed only after repository, current task, governing references, scope, stop conditions, applicable governance gates, execution-profile handling, and execution-environment handling are unambiguous. Execution-profile telemetry may remain explicitly unobservable under its baseline. Environment fields required for safe/correct execution may not remain unresolved past the relevant preflight.

For a historical workorder without the canonical nested profile, do not migrate it automatically. Use an explicit human selection or platform default and record missing recommendation fields as `null` with the reason. For a historical workorder without `execution_environment`, resolve expected environment from exact target configuration/evidence for the current run and produce current environment evidence without rewriting the historical workorder.
