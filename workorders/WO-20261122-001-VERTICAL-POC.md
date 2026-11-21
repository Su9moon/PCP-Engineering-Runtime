# WO-20261122-001 — Ruflo + Autoloop + EO/ES Vertical POC

## Identity

~~~yaml
repository: Su9moon/PCP-Engineering-Runtime
workorder_id: WO-20261122-001
title: Ruflo Supervisor and Autoloop remote Codex Worker vertical POC
executor: Codex
source_issue: null
status: READY_FOR_EXECUTION
priority: P0
authorized_by: user
authorized_date: 2026-11-22
source_work_item:
  repository: Su9moon/pcp-engineering-operations
  job: jobs/JOB-20261122-001/job.yaml
  workorder: workorders/WO-20261122-001/workorder.yaml
  source_commit: 0ca2043e6149d9106f2e6caba5627a6511e1074c
~~~

## Governing References

- Su9moon/personal-ai-control-plane@a66978ce1d5170fd1d0407678c78bdbb0c36d136: governance/adr/ADR-2026-11-22-001_pcp-engineering-runtime.md
- Su9moon/personal-ai-control-plane@a66978ce1d5170fd1d0407678c78bdbb0c36d136: processes/architecture-governance-gate.md
- Su9moon/personal-ai-control-plane@a66978ce1d5170fd1d0407678c78bdbb0c36d136: processes/experience-reuse-gate.md
- Su9moon/personal-ai-control-plane@a66978ce1d5170fd1d0407678c78bdbb0c36d136: governance/PCP_EXECUTION_PROFILE_RESOLUTION_BASELINE.md
- Su9moon/personal-ai-control-plane@a66978ce1d5170fd1d0407678c78bdbb0c36d136: governance/PCP_EXECUTION_ENVIRONMENT_RESOLUTION_BASELINE.md
- Su9moon/personal-ai-control-plane@a66978ce1d5170fd1d0407678c78bdbb0c36d136: governance/baselines/PCP_PROJECT_WORKSPACE_IDENTITY_BASELINE_V0.2_FIXED.md
- Su9moon/personal-ai-control-plane@a66978ce1d5170fd1d0407678c78bdbb0c36d136: governance/baselines/PCP_PROJECT_SURFACE_NAMING_CONVENTION_V0.1_FIXED.md
- Su9moon/PCP-Engineering-Runtime: AGENTS.md, PROJECT_STATUS.md, docs/architecture/POC_TARGET_ARCHITECTURE.md, docs/integration/DEPENDENCY_MAP.md, docs/engineering/EXPERIENCE_REUSE.md
- Su9moon/pcp-engineering-operations@c22189ba1144cdcf5cebf9b10a7db8e7c4f2e94d: AGENTS.md; schemas/job.schema.yaml; schemas/workorder.schema.yaml; schemas/result.schema.yaml; schemas/evidence.schema.yaml; schemas/review.schema.yaml; matching templates/
- Su9moon/pcp-execution-server@85783a75bd5ef7bc44110c6f9184b55748b4bfc4: AGENTS.md; README.md; governance/contracts/NORTHBOUND_EXECUTION_CONTRACT_V0.1.md; governance/contracts/EXECUTION_STATE_MACHINE_V0.1.md; governance/contracts/WORKER_PROTOCOL_V0.2.md; governance/contracts/EXECUTOR_ADAPTER_CONTRACT_V0.1.md; src/execution_server/kernel.py; src/execution_server/store.py; docs/RUNTIME_BINDING_GITHUB_ORG_SHARED_RUNNER_VALIDATION_V0.1.md
- Su9moon/agent-autoloop-pcp@f27466d5f0ec9fc6f2f48a1fa68c748581906bdc: AGENTS.md; package.json; host/config.ts; host/up.ts; protocol/client.ts; worker/worker.ts; kernel/decide.ts; docs/protocol.md; docs/state-machines.md
- ruvnet/ruflo@87f612cef121b50c2e31e2d3f88e46d88963a377: README.md; package.json (upstream read-only until user's Fork URL is resolved)
- Su9moon/symphony-cb@be10a1b79df723d6d7612b5651c8522704dafb2e: SPEC.md and elixir/README.md (reference only)

## Architecture Gate

~~~yaml
architecture_gate:
  required: true
  status: complete
  real_use_evidence: verified
  decision: INTEGRATE
  pcp_specific_remainder: "EO Workorder to ES ExecutionRequest mapping; ES authority preservation; Ruflo Supervisor integration; Autoloop provider correlation; independent Review/Product QA; EO Result/Evidence/Review return."
  minimum_formalization: "One thin integration adapter and MCP boundary; reuse Ruflo and Autoloop; use existing EO/ES contracts and state; no second task ledger or scheduler."
~~~

## Experience Reuse

~~~yaml
experience_reuse: REUSE
reused:
  - PCP fixed architecture and execution profile/environment governance
  - EO Job / Workorder / Result / Evidence / Review schemas
  - ES V0.3 Runtime Binding / Provider boundary and ExecutionKernel
  - Autoloop remote Hub / Worker protocol and provider event lifecycle
  - Ruflo Supervisor / Agent organization capability
  - Symphony spec as reference only
  - PCP experience observations on capability equivalence, baseline fidelity, dependency continuity and compact handoff
~~~

## Objective

Build a real, reviewable vertical POC in this repository. Prove one EO Workorder, one ES-authorized Execution / Attempt / Invocation, one actual Codex Worker launched through Autoloop, Ruflo supervision, independent read-only Review, Product QA and evidence return. This is not a production deployment.

## Scope

1. Preflight GitHub identity, Node.js, Python, Codex CLI availability/authentication, Ruflo package/command and Hub-to-Worker network path. Apply Workspace Identity V0.2; if a Local Codex Project is created, name it Lo_PCP Engineering Runtime. Discover the actual local workspace path instead of assuming a default. Do not print credentials.
2. Resolve the user's Ruflo Fork URL using local authenticated GitHub CLI/API. If not discoverable, continue with the pinned upstream commit read-only. Do not write to upstream.
3. Read the exact EO / ES / Autoloop / Ruflo references above. Confirm actual kernel methods and EO schemas; do not infer APIs from summaries.
4. Implement the smallest PCP Runtime Adapter in this repository. It may expose MCP tools to Ruflo and call the existing ES Python ExecutionKernel plus Autoloop Hub HTTP API. No second Job / Workorder / Execution / Attempt store.
5. Derive the Autoloop source event ID from ES execution_id + attempt_id. Record the Autoloop run ID as an ES runtime reference when the Worker actually starts.
6. Configure Autoloop Hub and one Worker from the pinned Fork. Worker connects outbound to Hub over HTTPS. A same-host Worker is setup evidence only, not remote acceptance.
7. Use examples/poc-fixture as the task target. The real Codex task is to add apply_discount_cents to the pricing module using integer cents only, discount basis points 0–10000, deterministic half-up rounding, strict integer validation and unit tests.
8. Run Codex through the actual Autoloop Worker in a unique local Git worktree on the Worker host. Record Worker identity/host, Autoloop event/run IDs, Codex session evidence if exposed, worktree, branch, commit, logs and tests.
9. Ruflo acts as central Supervisor. A separate Reviewer context must be read-only and inspect the original Workorder, diff, commit and test evidence. Do not reuse the authoring session.
10. Run Product QA independently against the fixture's real entry point, including half-up rounding and invalid-input cases.
11. Feed provider results to ES using the current authority and existing kernel methods. Record result/evidence and ES Review. Do not mark Execution DONE before approved Review.
12. Create EO Result, Evidence and Review records using existing schemas/templates and the active EO Job / Workorder. Do not change EO schemas, models or governance.
13. Verify Autoloop internal retries remain within the same ES Attempt / Invocation. Any new PCP Attempt requires new ES authorization.
14. Add only required integration tests and a concise runbook. Commit and push the POC on a normal feature branch if authentication permits; do not merge or deploy.

## Non-goals

- No production deployment, migration, production credentials or customer data.
- No modifications to PCP governance, EO/ES schemas or source, CB, Autoloop or Ruflo source.
- No second task database, generic Scheduler, Worker Pool, message bus, Agent Memory or workflow engine.
- No arbitrary command/path/repository execution from event content.
- No Mock as proof of real Codex or remote Worker execution.
- No full multi-node rollout in this milestone. Prove one remote Worker first; a second Worker is a follow-up after the single-Worker chain passes.
- No auto-merge or production publish.

## Validation and acceptance

1. EO Job and Workorder conform to current EO schemas.
2. ES accepts one frozen ExecutionRequest and creates one Execution, one Attempt, one Invocation and current authority.
3. A real Autoloop Worker runs Codex on a separate host and connects outbound to Hub over HTTPS. Same-host-only execution is reported as local and leaves remote acceptance open.
4. Worker modifies only the fixture in a unique worktree and produces a commit or patch artifact.
5. Autoloop run ID, ES Invocation and Attempt are correlated; provider retries do not create another PCP Attempt.
6. Independent Ruflo Review uses a separate read-only context.
7. Product QA passes with rounding and invalid-input coverage.
8. ES accepts the result under current authority and records Review; Execution becomes DONE only after approved Review.
9. EO Result / Evidence / Review reference the actual commit, tests, Worker run, ES identities and Review.
10. No secrets, production data or unauthorized source changes are committed.
11. Execution Profile and Environment evidence are truthful; unavailable non-critical telemetry uses PCP sentinel values without an artificial stop.

## Stop conditions

- If an ES operation is missing, do not modify ES; report the exact contract/code gap and complete the supported portion.
- If the Ruflo Fork URL is not discoverable locally, use pinned upstream read-only and record the unresolved identity; do not block Autoloop setup.
- If Node.js 24+ is unavailable, report the exact requirement; do not silently use an unsupported version.
- If Codex CLI is unavailable/unauthenticated on Worker, do not claim real execution.
- If no secure Hub HTTPS route exists, finish local setup, do not expose public plain HTTP, and report the exact remote prerequisite.
- If ES authority is absent, revoked or mismatched, do not dispatch or publish under stale authority.
- Production actions, credentials and customer data are outside this workorder.

## Execution Profile

~~~yaml
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
~~~

## Execution Environment

~~~yaml
execution_environment:
  expected:
    os: UNKNOWN
    shell: UNKNOWN
    shell_version: UNKNOWN
    runner_type: Codex CLI on a user-managed Linux / WSL Worker host (confirm at runtime)
  sources:
    - type: repository_evidence
      ref: Su9moon/agent-autoloop-pcp@f27466d5f0ec9fc6f2f48a1fa68c748581906bdc:package.json
    - type: repository_evidence
      ref: Su9moon/pcp-execution-server@85783a75bd5ef7bc44110c6f9184b55748b4bfc4:src/execution_server/kernel.py
    - type: repository_evidence
      ref: Su9moon/pcp-engineering-operations@c22189ba1144cdcf5cebf9b10a7db8e7c4f2e94d:schemas/workorder.schema.yaml
  resolution:
    runtime_confirmation_required: true
    critical_fields:
      - Node.js 24+ on Hub and Worker
      - Python version compatible with current ES kernel
      - Codex CLI installed and authenticated on Worker
      - secure HTTPS reachability from Worker to Hub
      - GitHub read/write capability for the POC feature branch
    mismatch_policy: explicit_fallback_allowed
~~~

## Connectivity Contract

~~~yaml
connectivity_contract:
  llm_connectivity:
    mode: required
    behavior_when_unavailable: "Do not start new Agent runs; preserve ES and Autoloop state and report the unavailable dependency."
  governance_connectivity:
    runtime: not_required
    update: package_supported
  external_services:
    - capability: GitHub repository read / feature-branch push
      requirement: required
      behavior_when_unavailable: "Complete local evidence and report the missing GitHub operation; do not claim a published branch."
    - capability: Autoloop Hub HTTPS endpoint
      requirement: required
      behavior_when_unavailable: "Continue local setup; do not expose an insecure public endpoint; remote acceptance remains open."
    - capability: Codex / model service
      requirement: required
      behavior_when_unavailable: "Do not claim a real Codex Worker execution."
~~~

## Execution Evidence

~~~yaml
execution_evidence:
  workorder_profile:
    recommended_model: TERRA
    recommended_reasoning_effort: High
  selected_execution:
    actual_model: NOT_EXPOSED_BY_RUNTIME
    actual_reasoning_effort: NOT_EXPOSED_BY_RUNTIME
  resolution:
    type: runtime_unobservable
    reason: "Replace with observed selection; retain sentinel if the runtime does not expose model/effort provenance."
  requested_by: user
  resolved_by: NOT_EXPOSED_BY_RUNTIME
  actor: Codex
~~~

## Environment Evidence

~~~yaml
environment_evidence:
  actual:
    os: NOT_EXPOSED_BY_RUNTIME
    shell: NOT_EXPOSED_BY_RUNTIME
    shell_version: NOT_EXPOSED_BY_RUNTIME
    runner_type: NOT_EXPOSED_BY_RUNTIME
    runner_name: NOT_EXPOSED_BY_RUNTIME
  resolution:
    status: unresolved
    matches_expected: UNKNOWN
    mismatch_fields: []
    policy_applied: explicit_fallback_allowed
    reason: "Replace with current preflight observations before the first environment-sensitive action."
  observed_by: Codex preflight
~~~
