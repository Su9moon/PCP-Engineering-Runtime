---
name: pcp-workorder-handoff
description: Standard PCP task handoff. Use when a task is being pushed from discussion/planning to GPT, Codex, Agent, or another executor.
---

# PCP Workorder Handoff

References:
- `governance/PCP_SKILL_GOVERNANCE.md`
- `governance/PCP_EXECUTION_PROFILE_RESOLUTION_BASELINE.md`
- `governance/PCP_EXECUTION_ENVIRONMENT_RESOLUTION_BASELINE.md`
- `processes/architecture-governance-gate.md`
- `governance/PCP_ENGINEERING_AGILITY_PRINCIPLE.md` — avoid AI-invented fixed branches, file subsets, identities and approvals

## Rules

When drafting or dispatching work, **do not add unsupported approval gates, immutable branch names, source-file-count restrictions, extra version identities, or additional workflows** merely because a prior MVP or workorder used them. Preserve the user's current request, required technical safety, production authorization and evidence; avoid making the workorder heavier than the task. This rule does not itself create a new gate.


1. Definitions, architecture, boundaries, and long-lived rules belong in Git Baseline/Protocol documents, not in the workorder.
2. A workorder contains only this task's scope, inputs, actions, outputs/evidence, stop conditions, required governance-gate state, and executor profile.
3. Every governing reference must identify `repo + exact path`.
4. Never scan a repository broadly to guess the source of truth.
5. If an exact reference is missing, inaccessible, conflicting, or ambiguous, stop and report instead of selecting a substitute.
6. A governed executor workorder MUST carry the canonical recommended execution profile before dispatch.
7. The recommendation is not a strict provider binding. Resolve it using the canonical priority and always return execution evidence.
8. Every new governed Workorder MUST also carry `execution_environment`; resolve expected environment from exact evidence and never treat expected values as current actual Runtime facts.

## Execution profile

For governed execution, every new workorder MUST contain:

    execution_profile:
      recommended:
        model: TERRA
        reasoning_effort: High
      resolution:
        human_override_allowed: true
        runtime_fallback_allowed: true
        strict_execution: false
      audit:
        required: true

Allowed model values:

- `LUNA`
- `TERRA`
- `SOL`

Allowed reasoning-effort values:

- `Low`
- `Medium`
- `High`
- `Max`

Selection guidance:

- `LUNA / Low-Medium`: mechanical, repetitive, low-risk work with little ambiguity.
- `TERRA / Medium-High`: normal implementation, testing, migration, or scoped debugging with clear boundaries.
- `SOL / High-Max`: architecture, cross-module reasoning, difficult diagnosis, high-risk trade-offs, or critical baseline/review work.

The model/effort recommendation is part of the Git workorder. Do not rely on chat to carry it. An explicit human selection made after dispatch remains higher priority and is recorded as resolution evidence.

Resolve the actual execution in this order:

    Human Explicit Selection
    > Runtime Available Capability
    > Workorder Recommendation
    > Platform Default

If the requested or recommended model/effort is unavailable, Runtime fallback is allowed. Never replace or degrade silently.

## Execution evidence

Every result MUST include the complete evidence structure from `governance/PCP_EXECUTION_PROFILE_RESOLUTION_BASELINE.md`, including:

- recommended and actual model/effort;
- one resolution type: `default`, `human_override`, `runtime_fallback`, or `runtime_unobservable`;
- a reason, including for `default`;
- `requested_by`, `resolved_by`, and `actor`.

When Runtime does not expose actual model, reasoning effort, or selection provenance, use `NOT_EXPOSED_BY_RUNTIME` for each unavailable field, select `runtime_unobservable`, continue automatically, and surface the warning in the result. Missing telemetry alone MUST NOT require Human Confirmation or stop execution.

`recommended != actual` is not itself a failure. A claimed fallback without evidence or a silent replacement is a failure of the governance contract. A truthfully recorded Runtime observability gap is not.

## Execution environment

Every new governed Workorder MUST contain the minimum environment contract from
`governance/PCP_EXECUTION_ENVIRONMENT_RESOLUTION_BASELINE.md`:

    execution_environment:
      expected:
        os: <value | UNKNOWN>
        shell: <value | UNKNOWN>
        shell_version: <value | UNKNOWN>
        runner_type: <value | UNKNOWN>
      sources:
        - type: <source type>
          ref: <exact reference>
      resolution:
        runtime_confirmation_required: true
        critical_fields:
          - <task-critical field>
        mismatch_policy: <fail_closed | explicit_fallback_allowed | informational>

Resolve expected fields in canonical precedence order: explicit Workorder/human requirement, exact target workflow/configuration, validated Runtime/POC evidence, repository-local supporting evidence, then `UNKNOWN`.

Filename extensions, shebangs, Dockerfiles, and similar repository clues are supporting evidence, never current actual environment facts.

Before environment-sensitive execution, record current `environment_evidence` when confirmation is required. Missing non-critical Runtime metadata may continue with a warning. A required critical field that cannot be confirmed is an unresolved compatibility condition and MUST stop rather than be guessed. Environment fallback is allowed only when the Workorder already defines or references it.

## Architecture classification

Before dispatch, classify the task using `processes/architecture-governance-gate.md`.

Architecture / Generic Capability work must carry:

    architecture_gate:
      required: true
      status: complete
      real_use_evidence: verified
      decision: INTEGRATE
      pcp_specific_remainder: "..."
      minimum_formalization: "..."

`status: waived` is allowed only with an explicit reason.

Routine work must explicitly state why the Gate is not required:

    architecture_gate:
      required: false
      reason: routine_implementation

A missing `architecture_gate` is not equivalent to `required: false`.

## Stop rule

Do not dispatch Architecture / Generic Capability work when the required gate is incomplete.

The correct next action is to complete the Gate, not to let the executor infer or bypass it.

## Dispatch

Default handoff message:

`执行 <repo> 中 <workorder-path>，按其中引用的基线、治理 Gate、execution_profile 与 execution_environment 执行；分别按 Execution Profile / Execution Environment Resolution Baseline 记录实际 evidence。`
