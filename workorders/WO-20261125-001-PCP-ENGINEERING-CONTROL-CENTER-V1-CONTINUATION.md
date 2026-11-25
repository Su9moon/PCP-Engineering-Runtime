# WO-20261125-001 --- PCP Engineering Control Center V1 Continuation

``` yaml
workorder_id: WO-20261125-001
title: PCP Engineering Control Center V1 Continuation
priority: P1
status: READY_FOR_EXECUTION
repository: Su9moon/PCP-Engineering-Runtime
execution_host: cbnet
environment: WSL2 Ubuntu 24.04
product_version: V1
gpt_ruflo_direct_integration: DEFERRED_TO_NEXT_VERSION
```

## 1. Objective

Continue and complete the existing PCP Engineering Runtime Dashboard V1
in the current project repository and application stack. This is a
continuation, not a rebuild. Inspect the actual local implementation and
Git state first, then complete the remaining V1 panel functions using
existing code, adapters, contracts, design and validated work.

The panel should let the user manage engineering work from one place:
submit tasks through the existing canonical path where available; view
task status, actual activity, issues and history; inspect Agent, Worker,
Event and Run state; inspect delivery files, Git commits, diffs, tests,
logs and evidence; review delivery and make supported human decisions;
and see truthful connection health/freshness.

This is a human-facing engineering workbench, not a Ruflo administration
clone, Autoloop clone, terminal-log viewer, new scheduler or new task
database.

## 2. Version boundary --- fixed

### 2.1 Current V1: Dashboard panel only

V1 includes: - the local web Dashboard and its seven main sections; -
thin local backend/read adapters over existing source-owned
interfaces; - task submission and human actions only where existing
canonical APIs and authorization contracts genuinely support them; -
truthful status, activity, evidence, review and connection views; - the
existing local cbnet deployment and browser access.

The panel may display Ruflo, Autoloop, EO and ES information through
their existing local interfaces. It must not create a second source of
truth or take over those systems' responsibilities.

### 2.2 Next version: GPT ↔ Ruflo direct management

This is a next-version requirement only. Do not implement it in this
workorder.

Future requirement: ChatGPT/GPT may submit instructions to, receive
progress from and interact with the authorized Ruflo Supervisor through
a secure PCP Runtime Gateway / MCP interface using authenticated HTTPS,
bounded permissions and auditable requests/results. GPT must not receive
raw local stdio access or unrestricted Ruflo/Autoloop permissions. The
future GPT entry must reuse the same authorized Runtime contracts as the
Dashboard rather than create a parallel control path.

For V1, do not build or configure a GPT-to-Ruflo MCP gateway, tunnel,
ChatGPT connector, remote control endpoint, GPT-specific authentication
or browser-to-local-stdio bridge. The Dashboard may show
`GPT ↔ Ruflo: deferred to next version` as a roadmap/connection status,
not as an active or failed connection.

### 2.3 Explicitly outside this V1 workorder

-   Do not implement GPT-to-Ruflo direct management.
-   Do not continue or modify `wo-20261124-003-dlv1` as part of this
    panel task. Preserve its existing state and evidence; do not cancel,
    rewrite or redispatch it.
-   Do not implement the Adaptive Orchestration runtime/connector work
    from `WO-20261124-003-RUFLO-ADAPTIVE-ORCHESTRATION.md` as a side
    task. Existing actual orchestration information may be displayed; do
    not create missing runtime capabilities to make UI controls appear
    active.
-   Do not rebuild or revalidate the completed first Ruflo/Autoloop POC.
-   Do not modify CB Blue/Green, CB TaskStore, EO/ES schemas or
    implementations, Ruflo upstream/Fork, or Autoloop upstream/Fork.
-   No production deployment, production credentials or customer data.

## 3. Governing PCP baseline and session bootstrap

Canonical PCP repository: `Su9moon/personal-ai-control-plane`

Pinned canonical commit: `22bae955686f03c5f440cdcd66e13a69f1289f90`

Read these exact references from that commit: - `AGENTS.md` -
`governance/PCP_ENGINEERING_AGILITY_PRINCIPLE.md` -
`.agents/skills/pcp-session-bootstrap/SKILL.md` -
`.agents/skills/pcp-experience-reuse/SKILL.md` -
`.agents/skills/pcp-workorder-handoff/SKILL.md` -
`processes/experience-reuse-gate.md` -
`processes/architecture-governance-gate.md` -
`governance/adr/ADR-2026-11-22-001_pcp-engineering-runtime.md` -
`governance/PCP_EXECUTION_PROFILE_RESOLUTION_BASELINE.md` -
`governance/PCP_EXECUTION_ENVIRONMENT_RESOLUTION_BASELINE.md` -
`governance/baselines/PCP_PROJECT_WORKSPACE_IDENTITY_BASELINE_V0.2_FIXED.md`

The PCP Session Bootstrap and Experience Reuse procedures have been
applied for this workorder. The executor must read the local project
entry rules/current project status and resolve current local
Git/environment facts before editing. Reuse the existing `INTEGRATE`
decision below; do not repeat the completed cross-domain scan or create
another Architecture Gate.

## 4. Project-local inputs and continuity

Repository: `Su9moon/PCP-Engineering-Runtime`

Primary existing V1 workorder:
`workorders/WO-20261123-001-PCP-ENGINEERING-CONTROL-CENTER.md`

Design reference: `design/pcp-engineering-control-center-demo.html`

Before implementation, inspect the actual local versions of: -
`AGENTS.md`, `README.md`, `PROJECT_STATUS.md`; - the primary V1
workorder and design reference above, if present locally; - current
application entry points, routes, local adapters and directly related
tests.

The prior V1 workorder is the product/acceptance reference. This
continuation narrows the version boundary by explicitly deferring GPT ↔
Ruflo direct management. If the prior workorder is absent from the local
checkout, this document still carries the current V1 scope; do not fetch
or substitute an old remote `main` snapshot over local work.

At the beginning, record the actual repository root, branch, full HEAD,
`git status --short` (including untracked files), existing worktrees,
current Dashboard stack/start method, actual service/listener state and
current adapter availability. Historical HEAD/remote SHA hints are not
current facts. Preserve all local commits, uncommitted changes and
untracked files.

## 5. Architecture and experience reuse

``` yaml
architecture_gate:
  required: true
  status: complete
  real_use_evidence: verified
  decision: INTEGRATE
  governing_decision: "Su9moon/personal-ai-control-plane@22bae955686f03c5f440cdcd66e13a69f1289f90:governance/adr/ADR-2026-11-22-001_pcp-engineering-runtime.md"
  pcp_specific_remainder: "A human-facing Dashboard V1 and thin local read/action adapters over existing EO, ES, Ruflo, Autoloop and GitHub contracts."
  minimum_formalization: "Continue the existing Dashboard and local adapter boundary. No second task ledger, execution store, scheduler, Worker Pool, message bus or Agent Runtime."
```

Experience reuse: `REUSE / EXTEND`, scope `PROJECT_LOCAL`.

Reuse the existing PCP Engineering Runtime ADR, the original V1
workorder/design, EO Job/Workorder/Result/Evidence/Review contracts, ES
ExecutionRequest/Execution/Attempt/Invocation and authorization
contracts, local Ruflo MCP and Autoloop Hub/Worker APIs, Git/GitHub
evidence links, and the existing Intelligent Engineer UX decisions for
task overview, actual activity, timeline, evidence, review and history.

Do not create a new Skill, Gate, database, RAG/vector store, generic
dashboard framework, policy engine, scheduler or runtime abstraction.

## 6. Responsibilities and execution entry

The user submits this workorder directly to the local Codex CLI session
on cbnet WSL2. Use the existing local project workspace. Do not dispatch
through CB Bridge or wait for a Tunnel Client.

GPT prepares requirements/workorders only in V1; GPT does not connect
to, manage or dispatch Ruflo.

Preserve the existing project execution ownership: - **Local Codex
session:** receives the workorder, performs local repository/environment
bootstrap, and hands the implementation request to the existing local
Ruflo Supervisor when the local Ruflo MCP is available. - **Ruflo
Supervisor:** owns engineering planning, task decomposition, Agent
organization, dispatch decisions, supervision, independent Review, QA,
rework and final engineering acceptance. - **Autoloop:** owns its
existing Hub/Event/Run/Worker lifecycle and result collection. - **Codex
CLI Worker:** executes bounded implementation/test tasks as an Autoloop
Worker; it is not the engineering planner or final acceptance
authority. - **Dashboard:** human-facing panel and thin local adapter,
not another scheduler or canonical task store.

Do not require a ChatGPT-to-Ruflo MCP connection for any V1
implementation or operation.

If local Ruflo MCP is unavailable, report the exact local connection
error. Do not try to repair it through GPT, a new tunnel, CB Bridge or a
new gateway. Continue only bounded, already-authorized Dashboard UI work
that can safely be executed directly in the local Codex workspace; do
not claim Ruflo orchestration, independent Ruflo Review or Ruflo
acceptance when those did not occur.

## 7. Dashboard V1 product scope

Complete the seven main navigation sections using the existing
repository stack and supplied design reference. Chinese is the default
UI language; desktop-first and responsive behavior are required.

### 7.1 Overview

Show engineering task summary;
pending/running/completed/failed/needs-review/blocked counts where
source records support them; recent actual activity;
Ruflo/Autoloop/EO/ES/GitHub health; and data source/last-observed
freshness. Never invent progress percentages, heartbeats, online states
or counts.

### 7.2 Engineering Tasks

Show task list, useful filters, title, project/repository, workorder
reference, current status and last actual activity; task detail
navigation; and task creation through the canonical EO Job + Workorder
path when the existing authorized write interface is available. If not
exposed, show the actual blocker. Do not store task records in a new
Dashboard database or local JSON ledger.

### 7.3 Runs / Events

Show actual Autoloop Event and Run IDs; task/workorder correlation where
available; Worker and Codex Thread references where exposed; status,
start/end time, exit code and failure/block reason; actual logs/result
references. Distinguish provider Run completion from PCP
Execution/Attempt and final review. `Run done` is not delivery
acceptance.

### 7.4 Agent Team

Show actual Ruflo Agent registrations/runtime facts, Supervisor
identity/status, Agent IDs and roles only when returned by the runtime,
current assignment/last activity where exposed. Distinguish MCP
connectivity, Agent registration and actual model execution. Do not
invent Agent roles or model telemetry.

### 7.5 Worker Nodes

Show actual Autoloop Worker identity, host/executor where exposed,
connection/last-seen status, active Run and recent history. State
whether execution is local-only or remote. Do not show remote Worker
capability as verified when only a same-host Worker has been tested.

### 7.6 Delivery Review

Show actual deliverable files/paths, source repository/branch/commit,
Git diff/commit links, test results/logs, SHA256 or source-provided
digest, Reviewer/QA result, and canonical EO Review/human decision
separately from provider QA. Support approve/request rework/needs-input
only when the existing canonical API and authorization path are
available; otherwise show the exact unavailable capability and keep the
action disabled.

### 7.7 Connections / Configuration

Show actual state and last observation for Ruflo local MCP,
Supervisor/model execution, Autoloop Hub, Workers, EO, ES, GitHub, local
Dashboard service and HTTPS endpoint. Distinguish `not configured`,
`not connected`, `not verified`, `blocked`, `failed`, `not exposed` and
`deferred`. Show
`GPT ↔ Ruflo direct management: deferred to next version`; do not
expose/configure a GPT gateway in V1.

## 8. Thin local adapters and canonical data ownership

Use existing contracts and actual local interfaces discovered during
implementation; do not hardcode stale historical ports.

-   **Autoloop:** reuse the configured Hub API, including available read
    endpoints such as `GET /v1/state`, `GET /v1/stream`,
    `GET /v1/runs/:id/why`, or existing MCP `status` / `why` tools.
-   **Ruflo:** use the configured local stdio MCP entry point from the
    Dashboard backend only. Browser code must never connect directly to
    stdio or receive Ruflo credentials.
-   **EO:** reuse canonical Job/Workorder/Result/Evidence/Review records
    and interfaces.
-   **ES:** reuse the existing ExecutionKernel and contracts. Do not
    create another execution database or state machine. If an operation
    is not exposed, show that precise limitation.
-   **GitHub:** link to source Workorder, branch, commit, PR and
    evidence where available.

Authority: - EO owns Job, Workorder, Result, Evidence and Job-level
Review intent/state. - ES owns ExecutionRequest, Execution, Attempt,
Invocation, execution authority and canonical execution transitions. -
Ruflo owns planning, Agent organization, supervision, independent Review
and Product QA. - Autoloop owns provider Hub/Worker lifecycle, Event/Run
state and provider result collection. - Codex is an executor, not
task-state authority. - Dashboard aggregates/presents source-owned data;
it does not become a parallel authority.

One Autoloop Hub Run maps to the corresponding ES Invocation under one
ES Attempt where canonical ES integration is active. Provider retries
must not create new PCP Attempts. Do not infer an active EO/ES
integration merely because schemas exist.

A small in-memory read cache is acceptable for responsiveness only if it
has explicit freshness semantics and is not a durable task/execution
store.

## 9. Human orchestration controls in V1

V1 may display actual orchestration information and expose controls
already supported by existing APIs, but it must not create a new
adaptive orchestration runtime.

If current Ruflo/Autoloop interfaces expose the relevant fields, the
task form/detail may show: - advisory complexity C0--C3; -
suggestion/manual/autonomous mode as selected task configuration; -
Agent roles/assignments; - Worker count and serial/parallel strategy; -
Review/QA participation; - timeout/resource settings; - human override
and approval status.

C0--C3 is advisory only, not a permission level or feature lock.
Complexity, operational risk and authorization are separate.
Human-selected settings take precedence when supported by the existing
runtime contract. Do not invent a local AI complexity assessor or
duplicate Ruflo planning logic in the Dashboard. Do not claim a setting
was applied unless actual dispatch/result evidence confirms it. If a
control is unsupported, show it as unavailable/not exposed with a
concise reason; do not build the missing runtime capability in this
panel-only workorder.

## 10. Actions and truthful capability handling

Wire only actions supported by existing authorized interfaces: -
create/use EO Job + Workorder through the canonical path; - dispatch
only after existing ES authorization succeeds; - pause/cancel/retry only
through the owning runtime's actual operation; -
approve/rework/needs-input only through canonical EO/ES review
transition; - request Ruflo re-plan only through an existing local
authorized Ruflo interface.

Every action must show its real result or exact blocker. If the full
write path is unavailable, deliver the functional Dashboard with real
read adapters and clearly disabled/unavailable actions. Do not replace
missing APIs with mocks, local fake state or a second task ledger. Do
not stop unrelated panel implementation because one optional action is
unavailable.

## 11. Deployment and access

Preserve the existing V1 target: - cbnet, Windows 11 / WSL2 Ubuntu
24.04; - browser access from the MEC LAN; - HTTPS; - port `8787`, unless
actual existing project configuration proves a different
already-approved port; - single administrator.

Use the existing repository stack and service/deployment pattern. Do not
reinstall WSL, Node.js, Codex, Ruflo or Autoloop. Keep Ruflo stdio,
Autoloop and EO/ES owner credentials on the host/backend only. Never put
them in browser JavaScript, HTML bundles, localStorage or client-visible
configuration.

Do not expose unauthenticated/plain HTTP Autoloop Hub publicly. Do not
broaden Dashboard to public Internet access. Do not introduce a new
identity provider or multi-user account system.

Provide actual URL, startup method, stop/disable method and access
boundary. Normal viewing/task inspection must not require terminal
operation.

## 12. Execution profile

``` yaml
execution_profile:
  recommended:
    model: SOL
    reasoning_effort: High
  resolution:
    human_override_allowed: true
    runtime_fallback_allowed: true
    strict_execution: false
  audit:
    required: true
```

Resolve using
`Su9moon/personal-ai-control-plane@22bae955686f03c5f440cdcd66e13a69f1289f90:governance/PCP_EXECUTION_PROFILE_RESOLUTION_BASELINE.md`.
Human explicit selection takes precedence. Runtime fallback is allowed
only when observed and recorded; never silently substitute/degrade.
Record actual model/effort when exposed. If not exposed, use
`NOT_EXPOSED_BY_RUNTIME` and `runtime_unobservable`; missing non-safety
telemetry alone is not a stop condition.

## 13. Execution environment

``` yaml
execution_environment:
  expected:
    os: Linux
    shell: bash
    shell_version: UNKNOWN
    runner_type: Codex CLI on cbnet WSL2 Ubuntu 24.04
  sources:
    - type: workorder
      ref: "Su9moon/PCP-Engineering-Runtime:workorders/WO-20261125-001-PCP-ENGINEERING-CONTROL-CENTER-V1-CONTINUATION.md"
    - type: repository_evidence
      ref: "Su9moon/PCP-Engineering-Runtime:AGENTS.md"
    - type: repository_evidence
      ref: "Su9moon/PCP-Engineering-Runtime:PROJECT_STATUS.md"
    - type: repository_evidence
      ref: "Su9moon/personal-ai-control-plane@22bae955686f03c5f440cdcd66e13a69f1289f90:governance/PCP_EXECUTION_ENVIRONMENT_RESOLUTION_BASELINE.md"
  resolution:
    runtime_confirmation_required: true
    critical_fields:
      - actual local repository path, branch, HEAD and working-tree state
      - actual WSL OS and shell
      - actual Node.js version if required by the existing Dashboard stack
      - actual Dashboard service endpoint and port
      - actual local Ruflo/Autoloop adapter endpoints if used
    mismatch_policy: explicit_fallback_allowed
```

Resolve expected and actual environment separately. Do not treat
expected values as current facts. Do not upgrade runtimes merely to
match an old assumption if the existing application stack works.

## 14. Implementation approach

1.  Read local project `AGENTS.md`, `PROJECT_STATUS.md`, `README.md`,
    the current Dashboard V1 workorder and design reference.
2.  Record actual local Git/worktree and Dashboard runtime state.
3.  Inspect the existing Dashboard. Build a concise gap list against
    Sections 7--11; do not rewrite completed, working pages or repeat
    unaffected tests.
4.  Have the local Ruflo Supervisor own engineering planning and task
    decomposition when its local MCP is available. It may use existing
    Autoloop Workers for bounded implementation, independent Review and
    QA.
5.  Implement the missing V1 UI and thin local adapters in the existing
    stack.
6.  Run only tests affected by the changes plus focused Dashboard
    integration tests.
7.  Start/update the existing local Dashboard service and verify browser
    access over the actual approved HTTPS/LAN endpoint.
8.  Update `PROJECT_STATUS.md` with the actual V1 state and explicit
    next-version GPT ↔ Ruflo requirement.

Do not stop after returning a plan or gap report. Continue
implementation through V1 acceptance. Unknown/non-critical status must
be shown honestly and must not become a global blocker. Stop only for a
real authority, destructive-operation, protected-data, critical identity
or unavoidable technical compatibility issue.

## 15. Focused validation

At minimum: 1. All seven navigation sections render and navigate
correctly. 2. Task list/detail uses actual source data; no fake seed
tasks are presented as canonical tasks. 3. Autoloop Event/Run mapping
preserves exact IDs and distinguishes provider completion from canonical
execution and review. 4. Ruflo MCP connectivity, Supervisor registration
and real model execution are represented separately. 5. EO and ES facts
are not conflated with provider Event/Run records. 6. Last-observed
time/freshness and unavailable states are accurate. 7. Credentials
remain backend-only. 8. Each visible action is genuinely wired to an
existing authorized API or disabled with a precise reason. 9. No second
task/execution database or scheduler is introduced. 10. Dashboard starts
using the existing service pattern and is accessible over the actual
local HTTPS/LAN endpoint. 11. Focused tests cover source mapping, status
mapping, authorization boundary, UI navigation and relevant actions. 12.
Reuse unaffected test evidence; no unrelated full-project audit or
repeat of the first Ruflo/Autoloop POC.

## 16. Deliverables

-   Completed Dashboard V1 implementation in the existing repository.
-   Screenshots of the seven sections.
-   Real data-source mapping and current integration states.
-   Actual URL/port, service startup and stop instructions.
-   List of wired actions and unavailable actions with exact reasons.
-   Focused test results.
-   Updated `PROJECT_STATUS.md`.
-   Git commit SHA(s) and exact changed-file summary.
-   Remaining V1 gaps and concrete unblock conditions.
-   Explicit next-version backlog entry: GPT ↔ Ruflo direct management
    through a secure, authorized Runtime Gateway.

## 17. Git and workspace protection

Before editing, inspect actual local repository root, branch, full HEAD,
`git status --short`, untracked files and worktrees. Preserve all local
commits and uncommitted/untracked changes. Use the current project
workspace and existing branch conventions; use an isolated worktree only
where parallel writes or actual workspace safety require it.

Never reset, clean, rebase, force-sync, overwrite local work with old
remote `main`, discard user changes, mix unrelated changes into this
task's commit, force-push or deploy to production.

## 18. Acceptance

V1 is complete when: - the existing Dashboard is completed rather than
rebuilt; - all seven sections are usable; - real source data and
freshness are shown truthfully; - task submission/review actions are
wired where existing authorized APIs support them, and unavailable
actions are accurately represented; - Ruflo/Autoloop/EO/ES
responsibilities remain distinct; - no duplicate scheduler, Worker Pool,
queue, task database or execution store is introduced; - the local cbnet
HTTPS Dashboard is usable from MEC LAN without terminal operation for
normal viewing; - focused validation passes; - project status and Git
evidence are delivered; - GPT ↔ Ruflo direct management is explicitly
deferred to the next version and no V1 GPT gateway/tunnel is built.

## 19. Dispatch instruction

Submit this workorder directly to the local cbnet Codex CLI session:

`workorders/WO-20261125-001-PCP-ENGINEERING-CONTROL-CENTER-V1-CONTINUATION.md`

> 继续执行 PCP Engineering Runtime Dashboard V1，不重建项目。先读取本地
> AGENTS、PROJECT_STATUS、README、当前 Dashboard 代码和原 V1
> workorder，核实当前 HEAD/Git 状态，然后直接补齐尚未完成的面板功能。
>
> 本版本只做 Dashboard panel。GPT ↔ Ruflo
> 直接管理明确延期到下一版本；不要配置 GPT MCP Gateway、Tunnel 或
> ChatGPT 连接器。不要把当前 GPT 会话接入 Ruflo。
>
> 使用本地 cbnet Codex 作为工单入口；按现有本地 Ruflo/Autoloop
> 工程分工推进，不通过 CB Bridge/Tunnel。Ruflo 可用时由原 Supervisor
> 规划、组织 Worker、Review、QA 和验收；Codex 不得声称未发生的 Ruflo
> 自主执行。
>
> 保留现有代码、工作区和 Git 历史。不要执行或修改
> `wo-20261124-003-dlv1`，不要重做首轮
> POC。直接完成面板，不要只返回计划或审计报告。
