# PCP Execution Environment Resolution Baseline

- Status: `FIXED`
- Version: `V0.1`
- Fixed date: `2026-09-22`
- Source workorder: `https://github.com/Su9moon/personal-ai-control-plane/issues/22`
- Parent canonical commit: `1108cda47c1a8d25b33e6ebba3969f1d9c9ff7da`
- Related baseline: `governance/PCP_EXECUTION_PROFILE_RESOLUTION_BASELINE.md V0.1.1`
- Scope: provider-neutral execution-environment semantics, resolution, compatibility policy, and evidence

## 1. Purpose

This baseline fixes how PCP represents and resolves the execution environment of
a governed Workorder.

`execution_profile` and `execution_environment` are separate concerns:

- `execution_profile` defines recommended execution/model configuration and
  truthful execution-selection evidence;
- `execution_environment` defines the OS, shell, runner/runtime constraints a
  task is expected to use and the environment actually observed for the current
  execution.

PCP owns the semantics, precedence, compatibility policy, and evidence contract.
It does not own runner discovery, scheduling, provisioning, or provider-specific
environment mechanics.

## 2. Expected Is Not Actual

The canonical distinction is:

```text
expected environment
!=
actual observed environment
```

Configuration, Workorder requirements, and validated historical evidence may
establish `expected`.

Only current Runtime/preflight observation may establish `actual` for the
current execution.

Do not convert historical POC evidence, workflow configuration, a Dockerfile,
a shebang, a filename extension, or a platform assumption into current actual
Runtime evidence.

## 3. Expected Environment Resolution

Resolve expected environment at Workorder creation or handoff in this order:

```text
Human / Workorder explicit requirement
        >
Exact target workflow / CI / deployment configuration
        >
Validated runtime / POC evidence
        >
Repository-local supporting evidence
        >
UNKNOWN
```

Repository-local supporting evidence may include a Dockerfile, container
configuration, shebang, script extension, or implementation documentation.

Supporting evidence is a clue. It MUST NOT override an explicit Workorder or
target-workflow declaration.

Examples:

```text
.ps1 -> PowerShell clue
.sh  -> shell clue
```

A clue is not current actual environment evidence.

If a field cannot be established from authorized creation-time evidence, record
that expected field as `UNKNOWN`. Do not guess.

## 4. Canonical Workorder Contract

Every new governed Workorder MUST carry an `execution_environment` block.

Minimum shape:

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

The structure is intentionally small. It is not a machine inventory schema.

`critical_fields` is task-specific. A field belongs there only when task
correctness, compatibility, authorization, or safety depends on it.

## 5. Actual Environment Evidence

Before environment-sensitive execution, observe the current environment using a
lightweight Runtime/preflight mechanism appropriate to the execution surface.

The baseline does not prescribe the discovery command or implementation.

Canonical result shape:

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

Preserve every truthfully observed field. Do not reduce partial evidence to
all-or-nothing evidence.

## 6. UNKNOWN and NOT_EXPOSED_BY_RUNTIME

These values have different meanings:

- `UNKNOWN` — creation-time evidence cannot establish an expected value.
- `NOT_EXPOSED_BY_RUNTIME` — the current Runtime/preflight does not expose an
  actual value.

They are not interchangeable.

Neither value authorizes copying an expected value into actual evidence.

This follows the truthfulness principle already fixed by Execution Profile
Resolution V0.1.1: expectation, observed fact, and unavailable telemetry are
different facts.

## 7. Critical and Non-Critical Fields

Environment observability is not identical to model-selection telemetry.

Missing non-critical metadata may continue with an audit warning.

Typical examples:

- runner display name;
- non-essential host metadata.

When safe/correct execution depends on a field, inability to confirm that field
MUST NOT be silently ignored.

Typical critical fields may include:

- OS;
- shell;
- shell version;
- architecture or language/runtime version when the Workorder explicitly
  depends on it.

If a critical field is required and remains `NOT_EXPOSED_BY_RUNTIME`, the
environment preflight is unresolved and environment-sensitive execution MUST
stop rather than guess.

This is an execution-compatibility stop. It is not a new governance Gate.

## 8. Mismatch Policy

The allowed policy values are:

### `fail_closed`

A mismatch in a declared critical field stops environment-sensitive execution.

### `explicit_fallback_allowed`

Execution may continue only when the Workorder already defines or references
the acceptable fallback/compatibility path.

The executor MUST NOT invent a fallback.

### `informational`

A mismatch may be recorded and execution may continue only for fields explicitly
non-critical to correctness, authorization, and safety.

`informational` MUST NOT be used to bypass a critical compatibility
requirement.

## 9. Runtime Confirmation

`runtime_confirmation_required` MUST be explicit.

When it is `true`, actual environment evidence must be captured before the
first environment-sensitive action.

When it is `false`, the Workorder must have no critical environment field whose
correctness depends on current Runtime confirmation. This does not authorize
fabrication of actual values.

## 10. Conservative Automation Principle

For infrastructure or harness code running in automation contexts, prefer
low-dependency capabilities that avoid unnecessary reliance on ambient machine
state such as:

- user profiles;
- implicit module autoload;
- interactive shell state;
- user-local PATH assumptions;
- other unreviewed host configuration.

This principle does not ban standard shell commands and does not mandate a
provider-specific implementation.

The Workorder environment should inform implementation choices without causing
PCP Core to own shell/runtime mechanics.

## 11. Relationship to Execution Profile Resolution

The two contracts remain parallel:

```text
Workorder
├── execution_profile
│   ├── recommended
│   ├── resolution
│   └── execution evidence
│
└── execution_environment
    ├── expected
    ├── sources
    ├── resolution policy
    └── environment evidence
```

Do not merge model-selection semantics and execution-environment semantics into
one object.

## 12. Backward Compatibility

- Existing Workorders are not bulk-migrated.
- Workorders created after this baseline MUST carry `execution_environment`.
- A future execution of a historical Workorder may resolve expected environment
  from its exact target configuration/evidence and produce current
  `environment_evidence` without rewriting historical task content.
- Existing Execution Profile V0.1.1 evidence remains valid and unchanged.

## 13. Validation Matrix

| Case | Required result |
| --- | --- |
| Explicit Workorder environment conflicts with lower-priority evidence | Workorder requirement wins for expected |
| Workorder silent; exact workflow declares runner/shell | Workflow establishes expected fields |
| Only `.ps1` / `.sh` clue exists | May support expected inference only at repository-evidence priority; never becomes actual |
| Current preflight matches all critical expected fields | Proceed; record `matched` |
| Critical field mismatches under `fail_closed` | STOP environment-sensitive execution |
| Workorder defines an acceptable fallback | Continue only through that explicit fallback; record `fallback` |
| Non-critical metadata is unobservable | Record sentinel/warning and continue |
| Critical required field is unobservable | Record `unresolved`; STOP rather than guess |
| No new Gate/runtime component is introduced | PASS |

## 14. Non-Goals and Boundary

This baseline does not create or implement:

- an Environment Gate;
- runner discovery service;
- runner inventory database;
- scheduler or Runtime dispatcher;
- shell detection daemon;
- provider-specific runner abstraction;
- automatic environment provisioning;
- container orchestration;
- full machine capability inventory;
- Domain-specific deployment logic.

Provider/runtime-specific mechanics terminate outside PCP Core.

Changing these semantics, precedence rules, policy enum, or evidence contract
requires a reviewed baseline amendment.
