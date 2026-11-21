# PCP Execution Profile Resolution Baseline

- Status: `FIXED`
- Version: `V0.1.1`
- Fixed date: `2026-09-22`
- Source workorder: `https://github.com/Su9moon/personal-ai-control-plane/issues/17`
- Amendment source workorder: `https://github.com/Su9moon/personal-ai-control-plane/issues/20`
- Parent baseline merge: `2bb44d44a4c5f56729efee195d560a8b1ba5db03`
- Scope: PCP workorder execution-profile semantics, resolution, and audit evidence

## 1. Purpose

This baseline fixes how PCP interprets and resolves an `execution_profile`.

An execution profile is a recommended default, not a provider binding or an
unconditional runtime constraint. PCP owns the provider-neutral semantics,
resolution rules, and audit requirements. The Runtime owns only the mechanics
needed to select and start an available executor.

## 2. Canonical Workorder Profile

New PCP workorders that dispatch Codex or another governed executor MUST carry:

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

The current baseline fixes the resolution flags shown above. A workorder may
change the recommended model and reasoning effort, but it MUST NOT silently
turn the recommendation into a strict provider binding.

## 3. Fixed Semantics

- `recommended` is the workorder's preferred default.
- `actual` is the selection the Runtime ultimately executes when the Runtime
  exposes it. An explicit unavailability marker is evidence about
  observability, not an inferred actual value.
- `recommended != actual` is not itself a failure.
- `human_override_allowed: true` permits an explicit human selection to replace
  the workorder recommendation.
- `runtime_fallback_allowed: true` permits an unavailable higher-priority choice
  to fall back to an available capability.
- `strict_execution: false` means an exact model/effort match is not a start
  condition.
- `audit.required: true` means every execution MUST produce the complete
  evidence structure defined below. Completeness of the structure does not
  require the Runtime to expose every non-safety-critical telemetry value.

The profile describes execution intent. It does not score models, discover the
best model, schedule work, or bind PCP to a provider-specific model identifier.

## 4. Resolution Priority

Resolve the execution selection in this order:

```text
Human Explicit Selection
        >
Runtime Available Capability
        >
Workorder Recommendation
        >
Platform Default
```

Interpretation:

1. Honor an explicit human selection when the Runtime can execute it.
2. The Runtime capability boundary determines which requested or recommended
   choices are executable; it does not silently redefine PCP semantics.
3. When there is no explicit human selection, use the workorder recommendation
   if it is available.
4. Use the platform default only when no higher-priority usable selection is
   available.
5. When an explicit or recommended choice is unavailable, fallback is allowed,
   but the actual selection and reason MUST be recorded.

The priority is a resolution rule, not a request to implement a scheduler.

## 5. Resolution Types

Exactly one resolution type MUST be recorded:

- `default`: the actual selection uses the workorder recommendation, or a
  documented platform default when no recommendation exists on a historical
  workorder.
- `human_override`: an available explicit human selection determines the actual
  execution instead of the workorder recommendation.
- `runtime_fallback`: an explicit or recommended selection is unavailable and
  the Runtime uses another available capability.
- `runtime_unobservable`: the Runtime does not expose one or more actual
  model/effort values or enough selection provenance to truthfully classify the
  resolution as `default`, `human_override`, or `runtime_fallback`.

When a human selection is unavailable and the Runtime falls back, the type is
`runtime_fallback`; the reason MUST identify the unavailable human selection.
Use `runtime_fallback` only when the fallback is observed. Do not infer a
fallback from a difference, absence, or platform assumption.

`runtime_unobservable` is a partial-observability state, not an execution
failure or a claim about which resolution path occurred. Its reason MUST name
the fields or provenance the Runtime did not expose.

## 6. Canonical Execution Evidence

Every governed execution MUST produce this complete structure:

```yaml
execution_evidence:
  workorder_profile:
    recommended_model:
    recommended_reasoning_effort:

  selected_execution:
    actual_model:
    actual_reasoning_effort:

  resolution:
    type:
      - default
      - human_override
      - runtime_fallback
      - runtime_unobservable
    reason:

  requested_by:
  resolved_by:
  actor:
```

The list under `resolution.type` documents the allowed enum. An evidence
instance MUST contain one scalar enum value, not the list.

Field meaning:

- `workorder_profile.*`: recommendation read from the governing workorder.
- `selected_execution.*`: Runtime's actual model and effort labels when
  exposed; otherwise the exact sentinel `NOT_EXPOSED_BY_RUNTIME`.
- `resolution.type`: one allowed resolution type.
- `resolution.reason`: why that type and actual selection were used; required
  even for `default`.
- `requested_by`: identity or authority that issued the work or explicit
  selection.
- `resolved_by`: Runtime or execution surface that resolved the choice.
- `actor`: executor that performed the work.

Do not infer or fabricate unavailable evidence. For a historical workorder that
predates this baseline, use `null` for a missing recommendation and explain the
platform-default or explicit-selection path in `resolution.reason`. This rule
does not authorize migration of historical workorders.

For current execution telemetry, do not use `null`, copy a recommendation into
`actual`, or substitute a platform assumption. Use
`NOT_EXPOSED_BY_RUNTIME` for each field the Runtime does not expose. If
`resolved_by` itself is not exposed, use the same sentinel there. Preserve any
fields that are truthfully exposed, so partial evidence remains partial rather
than being reduced to all-or-nothing evidence.

Execution evidence belongs in the workorder result, handoff result, PR body, or
another Git-tracked execution record required by the governing workflow. It is
not a new runtime database or scheduling service.

## 7. Runtime Observability Rule

Runtime observability failure is not execution failure.

When all execution-profile metadata is exposed, record it normally. When one or
more non-safety-critical execution-profile fields are not exposed:

1. record each unavailable field as `NOT_EXPOSED_BY_RUNTIME`;
2. set `resolution.type: runtime_unobservable` when the resolution path cannot
   be classified truthfully;
3. state the missing fields or provenance in `resolution.reason`;
4. continue the authorized execution automatically;
5. surface the partial-observability warning in the final Result Package or
   audit summary.

Missing execution telemetry alone MUST NOT request Human Confirmation and MUST
NOT stop an otherwise authorized execution.

This non-blocking rule is limited to observability. It does not provide
authority, broaden scope, or prove a fallback/default/override that was not
observed.

### Complete Runtime evidence

```yaml
selected_execution:
  actual_model: SOL
  actual_reasoning_effort: High
resolution:
  type: default
  reason: Workorder recommendation was exposed as the selected execution.
```

### Partial Runtime evidence

```yaml
selected_execution:
  actual_model: SOL
  actual_reasoning_effort: NOT_EXPOSED_BY_RUNTIME
resolution:
  type: runtime_unobservable
  reason: Runtime exposed the model but not reasoning effort or selection provenance.
```

### Model and reasoning not exposed

```yaml
selected_execution:
  actual_model: NOT_EXPOSED_BY_RUNTIME
  actual_reasoning_effort: NOT_EXPOSED_BY_RUNTIME
resolution:
  type: runtime_unobservable
  reason: Runtime did not expose model, reasoning effort, or selection provenance.
```

## 8. Hard STOP Boundaries

Real governance, authority, scope, and safety failures remain fail-closed.
Examples include:

- a required Human Run Gate is absent;
- canonical implementation identity cannot be tied to the reviewed commit;
- Policy SHA or Scope SHA mismatches;
- unauthorized scope expansion or destructive operation;
- protected database or protected path access without authority;
- an explicit governance or safety boundary violation.

These conditions are not telemetry gaps. Do not relabel them as
`runtime_unobservable` or continue automatically.

### Genuine hard-stop example

```yaml
execution_status: STOPPED
stop_reason: SCOPE_SHA_MISMATCH
execution_evidence:
  workorder_profile:
    recommended_model: TERRA
    recommended_reasoning_effort: High
  selected_execution:
    actual_model: NOT_EXPOSED_BY_RUNTIME
    actual_reasoning_effort: NOT_EXPOSED_BY_RUNTIME
  resolution:
    type: runtime_unobservable
    reason: Runtime execution-profile telemetry was not exposed.
  requested_by: human_authority
  resolved_by: NOT_EXPOSED_BY_RUNTIME
  actor: Codex
```

The telemetry remains truthfully recorded, but it neither causes nor overrides
the independent `SCOPE_SHA_MISMATCH` hard stop.

## 9. Prohibitions

- No silent replacement of a requested or recommended model/effort.
- No unrecorded degradation or fallback.
- No copying a recommendation into `actual` when Runtime telemetry is absent.
- No Human Confirmation request or STOP caused only by missing non-critical
  execution telemetry.
- No claim that `recommended != actual` failed solely because the values differ.
- No provider-specific identifiers in this canonical contract.
- No model capability scoring or automatic best-model selection.
- No Runtime scheduling, dispatch, or Codex-internal implementation in PCP.

If `audit.required: true`, the executor MUST produce the evidence structure,
using explicit unavailability markers where needed. Failure to expose Runtime
telemetry is an audit warning; failure to record either the observed value or
its explicit unavailability is an evidence-contract violation. Neither changes
the actual outcome of the executed work.

## 10. Validation Matrix

| Case | Input condition | Required actual selection | Required resolution | Result |
| --- | --- | --- | --- | --- |
| Recommended available | No human override; recommendation available | Recommended model/effort | `default` with reason | PASS |
| Human explicit selection | Human selects an available model/effort | Human selection | `human_override` with requester and reason | PASS |
| Recommended unavailable | No human override; recommendation unavailable; fallback available | Available fallback | `runtime_fallback` with reason | PASS |
| Partial Runtime evidence | Some actual values exposed; effort or provenance not exposed | Exposed values plus sentinel for missing fields | `runtime_unobservable`; continue and warn | PASS |
| Model/reasoning not exposed | Runtime exposes neither actual value nor selection provenance | Explicit sentinels | `runtime_unobservable`; continue and warn | PASS |
| Silent replacement | Actual differs without evidence and reason | Unrecorded | none or incomplete | FAIL |
| Genuine governance failure | Required gate/SHA/scope/authority boundary fails | Independent hard stop | `STOPPED`; telemetry state does not override | FAIL CLOSED |

## 11. Compatibility and Migration

- Workorders created after this baseline MUST use the canonical nested profile.
- Existing workorders are not migrated merely to adopt this baseline.
- A future execution of a historical workorder still produces execution
  evidence; missing historical recommendation fields remain `null`.
- Older flat `model` / `reasoning_effort` workorder fields remain historical
  evidence and MUST NOT be rewritten in bulk.
- Existing V0.1 `default`, `human_override`, and `runtime_fallback` evidence
  remains valid and is not migrated.
- `runtime_unobservable` and `NOT_EXPOSED_BY_RUNTIME` are additive V0.1.1
  values for new result/audit output; they do not alter an existing execution
  outcome.

## 12. Change Boundary

Changing these semantics, the resolution priority, or the evidence contract
requires a reviewed new baseline version. Runtime and provider implementations
may vary as long as they preserve this contract and terminate provider-specific
logic outside PCP Core.
