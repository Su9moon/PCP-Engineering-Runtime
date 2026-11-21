# PCP Workorder Template

> Canonical template for new PCP workorders. Delete instructional placeholders
> when creating a real workorder; do not copy unresolved alternatives into an
> executable task.

## Identity

```yaml
repository: Su9moon/<repository>
workorder_id: <ID>
title: <title>
executor: Codex
source_issue: <exact URL or null>
```

## Governing References

- `Su9moon/<repository>:<exact/path>`
- `Su9moon/personal-ai-control-plane:governance/PCP_EXECUTION_PROFILE_RESOLUTION_BASELINE.md`
- `Su9moon/personal-ai-control-plane:governance/PCP_EXECUTION_ENVIRONMENT_RESOLUTION_BASELINE.md`

Do not use broad repository references when an exact path governs the task.

## Architecture Gate

Use one complete form from `processes/architecture-governance-gate.md`.

```yaml
architecture_gate:
  required: false
  reason: routine_implementation
```

For Architecture / Generic Capability work, replace it with a completed or
explicitly waived required-gate record before dispatch.

## Execution Profile

```yaml
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
```

The recommendation is not a strict provider binding. Resolution and evidence
follow `governance/PCP_EXECUTION_PROFILE_RESOLUTION_BASELINE.md`.

## Execution Environment

```yaml
execution_environment:
  expected:
    os: <value | UNKNOWN>
    shell: <value | UNKNOWN>
    shell_version: <value | UNKNOWN>
    runner_type: <value | UNKNOWN>

  sources:
    - type: <workorder | workflow | deployment_config | validated_runtime_evidence | repository_evidence>
      ref: <exact reference>

  resolution:
    runtime_confirmation_required: true
    critical_fields:
      - <field required for safe/correct execution>
    mismatch_policy: <fail_closed | explicit_fallback_allowed | informational>
```

Resolve expected environment from exact evidence; do not guess. Expected values
are not current actual Runtime facts. Runtime/preflight confirmation and result
evidence follow `governance/PCP_EXECUTION_ENVIRONMENT_RESOLUTION_BASELINE.md`.

## Connectivity Contract

Include this section for release build, production deployment/initialization, runtime packaging, or tasks whose behavior changes with connectivity. Omit it for ordinary engineering work when connectivity is irrelevant.

```yaml
connectivity_contract:
  llm_connectivity:
    mode: required | optional | none
    behavior_when_unavailable: <behavior>

  governance_connectivity:
    runtime: required | not_required
    update: required | package_supported | none

  external_services: []
```

Follow `governance/baselines/PCP_RELEASE_RUNTIME_INDEPENDENCE_BASELINE_V0.1_FIXED.md`. Do not collapse LLM/service connectivity and Governance-plane connectivity into one online/offline flag.

## Objective

<One independently acceptable outcome.>

## Scope

- <authorized change>

## Non-goals

- <explicit exclusion>

## Inputs

- <exact source or artifact>

## Actions

1. <bounded action>

## Validation

1. <observable acceptance check>

## Deliverables

- <artifact or report>

## Stop Conditions

- <success boundary, review boundary, or blocker>

## Execution Evidence

The executor fills this instance with the observed actual selection;
`resolution.type` is one scalar allowed value. Missing Runtime telemetry uses
the exact sentinel `NOT_EXPOSED_BY_RUNTIME`, continues automatically, and is
reported as an audit warning without artificial Human Confirmation.
This telemetry-only rule does not override any independent governance, scope,
authority, safety, destructive-operation, protected-data, or identity stop.

```yaml
execution_evidence:
  workorder_profile:
    recommended_model: <value or null for a historical workorder>
    recommended_reasoning_effort: <value or null for a historical workorder>

  selected_execution:
    actual_model: <runtime-reported value | NOT_EXPOSED_BY_RUNTIME>
    actual_reasoning_effort: <runtime-reported value | NOT_EXPOSED_BY_RUNTIME>

  resolution:
    type: <default | human_override | runtime_fallback | runtime_unobservable>
    reason: <required explanation>

  requested_by: <identity or authority>
  resolved_by: <runtime or execution surface | NOT_EXPOSED_BY_RUNTIME>
  actor: <executor>
```


## Environment Evidence

Record current Runtime/preflight facts without copying expected values into
actual fields. Use `NOT_EXPOSED_BY_RUNTIME` only for current fields the Runtime
does not expose.

```yaml
environment_evidence:
  actual:
    os: <observed value | NOT_EXPOSED_BY_RUNTIME>
    shell: <observed value | NOT_EXPOSED_BY_RUNTIME>
    shell_version: <observed value | NOT_EXPOSED_BY_RUNTIME>
    runner_type: <observed value | NOT_EXPOSED_BY_RUNTIME>
    runner_name: <observed value | NOT_EXPOSED_BY_RUNTIME>

  resolution:
    status: <matched | mismatch | fallback | partial_observability | unresolved>
    matches_expected: <true | false | UNKNOWN>
    mismatch_fields: []
    policy_applied: <fail_closed | explicit_fallback_allowed | informational>
    reason: <required explanation>

  observed_by: <runtime/preflight surface>
```
