# WO-20261126-001 — PCP Engineering Control Center V1.1 Conversational Intake

## Identity

- repository: Su9moon/PCP-Engineering-Runtime
- workorder_id: WO-20261126-001
- title: PCP Engineering Control Center V1.1 Conversational Intake
- executor: Codex
- source_issue: null
- priority: P1
- product_version: V1.1
- execution_host: cbnet
- environment: WSL2 Ubuntu 24.04

## Governing References

Canonical PCP source: Su9moon/personal-ai-control-plane@22bae955686f03c5f440cdcd66e13a69f1289f90

- Su9moon/personal-ai-control-plane:AGENTS.md
- Su9moon/personal-ai-control-plane:governance/PCP_ENGINEERING_AGILITY_PRINCIPLE.md
- Su9moon/personal-ai-control-plane:.agents/skills/pcp-session-bootstrap/SKILL.md
- Su9moon/personal-ai-control-plane:.agents/skills/pcp-experience-reuse/SKILL.md
- Su9moon/personal-ai-control-plane:.agents/skills/pcp-workorder-handoff/SKILL.md
- Su9moon/personal-ai-control-plane:processes/experience-reuse-gate.md
- Su9moon/personal-ai-control-plane:processes/architecture-governance-gate.md
- Su9moon/personal-ai-control-plane:governance/adr/ADR-2026-11-22-001_pcp-engineering-runtime.md
- Su9moon/personal-ai-control-plane:governance/PCP_EXECUTION_PROFILE_RESOLUTION_BASELINE.md
- Su9moon/personal-ai-control-plane:governance/PCP_EXECUTION_ENVIRONMENT_RESOLUTION_BASELINE.md
- Su9moon/personal-ai-control-plane:governance/templates/PCP_WORKORDER_TEMPLATE.md

Runtime repository references:

- Su9moon/PCP-Engineering-Runtime:AGENTS.md
- Su9moon/PCP-Engineering-Runtime:README.md
- Su9moon/PCP-Engineering-Runtime:PROJECT_STATUS.md
- Su9moon/PCP-Engineering-Runtime:docs/architecture/POC_TARGET_ARCHITECTURE.md
- Su9moon/PCP-Engineering-Runtime:docs/integration/DEPENDENCY_MAP.md
- Su9moon/PCP-Engineering-Runtime:docs/engineering/EXPERIENCE_REUSE.md
- Su9moon/PCP-Engineering-Runtime:workorders/WO-20261123-001-PCP-ENGINEERING-CONTROL-CENTER.md
- Su9moon/PCP-Engineering-Runtime:workorders/WO-20261125-001-PCP-ENGINEERING-CONTROL-CENTER-V1-CONTINUATION.md
- Su9moon/PCP-Engineering-Runtime:docs/product/CONVERSATIONAL_ENGINEERING_INTAKE_V1.1.md
- Su9moon/PCP-Engineering-Runtime:design/pcp-engineering-control-center-conversational-intake-demo.html

The two V1 workorders remain in force except where this addendum explicitly extends the task-entry experience. Continue the existing local Dashboard implementation; this is not a rebuild.

The new design references are on branch handoff/dashboard-v1-demo-20261125. Read those exact files as design inputs. Do not switch, merge, reset, or overwrite the user's actual local implementation branch merely to consume this handoff branch.

## Architecture Gate

    architecture_gate:
      required: true
      status: complete
      real_use_evidence: verified
      decision: INTEGRATE
      governing_decision: "Su9moon/personal-ai-control-plane@22bae955686f03c5f440cdcd66e13a69f1289f90:governance/adr/ADR-2026-11-22-001_pcp-engineering-runtime.md"
      pcp_specific_remainder: "Conversational engineering requirement clarification, provenance-aware live requirement dossier, reviewed document package, and mapping to the existing EO Job/Workorder authority."
      minimum_formalization: "Extend the existing Dashboard with a conversational intake UI and thin LLM/document/EO adapters where supported. Reuse EO and existing project context. No parallel task ledger, execution authority, scheduler, Worker Pool, Agent Memory platform or generic orchestration runtime."

Experience reuse: REUSE / EXTEND, scope PROJECT_LOCAL. Reuse the approved PCP Engineering Runtime ADR, existing V1 workorders, current Dashboard stack, EO schemas, ES authority boundaries and the new V1.1 design references. Do not repeat the completed cross-domain discovery or create another Architecture Gate.

## Objective

Extend the existing PCP Engineering Control Center V1 so that New Engineering Task opens a conversational requirement-intake workspace instead of a conventional task form/modal.

The user describes an outcome or problem in natural language. The assistant progressively clarifies the request, maintains a live requirement dossier, drafts the appropriate engineering document package, and prepares an EO Job/Workorder. The user reviews and explicitly confirms the package before canonical work-item creation.

The interface must not require users to understand engineering schemas, Agent roles, Worker settings or workorder syntax before starting.

## Version Boundary

This work adds conversational requirement intake to the existing Dashboard. It does not implement GPT ↔ Ruflo direct management, which remains deferred under the existing V1 continuation workorder.

The intake assistant may call a configured LLM API for dialogue and document drafting. It must not receive Ruflo, Autoloop or ES execution-control tools. This is not a parallel GPT-to-Ruflo control path.

## Scope

### 1. Entry and conversation

- Replace the existing new-task form/modal entry with a dedicated conversational intake workspace.
- Preserve the existing seven Dashboard sections and navigation.
- Start from free text. Do not require a multi-field form before the first message.
- Ask one high-value follow-up question at a time, selected adaptively from the current requirement gaps.
- Offer optional quick-reply suggestions, but always support free-text answers.
- Let the user correct earlier answers, change scope, add constraints or redirect the discussion.
- Do not repeat information already confirmed in the current dossier or available authoritative project context.
- Do not implement a fixed questionnaire disguised as chat.

### 2. Live requirement dossier

Display an editable side panel updated as the conversation progresses. Include applicable fields:

- goal / problem;
- target project and repository;
- users / operating context;
- scope and exclusions;
- constraints and dependencies;
- expected deliverables;
- acceptance criteria;
- risks and assumptions;
- unresolved questions;
- advisory execution recommendation.

Every material item must have a visible provenance state:

- USER_CONFIRMED
- AI_SUGGESTED
- AI_INFERRED
- UNRESOLVED

The user can correct or reject AI-generated suggestions and inferences. Never silently promote an AI inference to a user-confirmed requirement.

### 3. Project context reuse

- Reuse the existing project selector/registry if present.
- Read only the selected project's relevant baseline, workorder, README/status and directly related evidence.
- Use exact repository/path references in generated documents.
- Approved governance and validated experience may guide the assistant. Candidate/Inbox material is evidence, not authoritative instruction.
- Do not broadly scan all PCP experience or all repositories for every turn.
- If no project is selected, let the conversation clarify whether this is a new project or work on an existing one; do not invent a project identity.

### 4. Document package

Generate drafts according to task complexity. Do not force seven separate files for a small task.

Potential documents:

1. Requirement brief.
2. Product / interaction design.
3. Technical design, when justified.
4. Implementation plan and task breakdown.
5. Advisory execution arrangement (complexity, suggested Agent/Worker roles, model profile).
6. Acceptance plan.
7. EO Job + Workorder draft mapped to the existing EO schemas.

The assistant may produce an initial package while some details remain unknown. Mark unresolved items and assumptions explicitly rather than blocking the entire draft.

Allow the user to preview documents, edit requirements, regenerate affected documents and review the complete package before confirmation.

### 5. Explicit confirmation and canonical EO creation

- Draft generation is not approval.
- Only an explicit user action may confirm the final package.
- After confirmation, create/use EO Job + Workorder only through an existing authorized canonical EO interface.
- If the EO write interface is unavailable, provide an exportable EO Workorder draft and state the exact missing interface. Do not create a local substitute task record.
- Creating an EO Workorder does not create an ES Execution, authorize an Attempt, dispatch Ruflo/Autoloop or start a Worker.
- ES authorization and execution remain separate subsequent actions under the existing authority model.

### 6. LLM provider integration

- Inspect the existing Dashboard/server configuration for a usable LLM API provider before adding anything.
- Reuse an existing configured provider when available; do not route intake through Ruflo agent_execute or Autoloop.
- Keep API credentials server-side only. Never expose keys in browser JavaScript, HTML bundles, localStorage or client-visible configuration.
- Do not hard-code a provider, model, endpoint or API key; do not silently fall back to another provider/model.
- If no provider is configured, finish the UI and manual draft experience, show the precise missing configuration, and report that live AI dialogue/document generation is not yet connected. Do not use scripted/mock replies as evidence of a live model.
- Do not add a provider marketplace or generic model-routing framework.

### 7. Draft persistence and export

- Inspect the existing project/file capabilities and reuse them if suitable.
- Do not create a new database, task ledger, Agent Memory service or general-purpose persistence layer for this feature.
- If there is no existing safe draft-persistence path, keep the active draft in the current session and provide an exportable Markdown/document package. Clearly indicate that the session draft is not yet persisted across sessions.
- After approval, associate final documents with the selected project using an existing authorized file/Git workflow. Do not auto-commit or push.

### 8. Existing Dashboard continuity

- Preserve the seven existing sections and all working V1 behavior.
- Existing task list/detail continues to read canonical EO/ES/provider records.
- Do not redesign unrelated Agent, Worker, Run, Review or Connection pages.
- Keep all status and capability claims truthful.

## Non-goals

- GPT ↔ Ruflo direct management, GPT MCP Gateway, tunnel or ChatGPT connector.
- Direct Ruflo/Autoloop/ES controls from the intake assistant.
- Automatic ES authorization, execution dispatch, retry, merge or deployment.
- A second task database, execution store, scheduler, Worker Pool, message bus or Agent Memory system.
- A fixed questionnaire or a large upfront engineering form.
- Provider marketplace, multi-model router or new identity system.
- Production deployment or production/customer data.
- Rebuilding the existing Dashboard or repeating the first Ruflo/Autoloop POC.

## Connectivity Contract

    connectivity_contract:
      llm_connectivity:
        mode: required
        behavior_when_unavailable: "Keep manual drafting available; show the exact missing provider/configuration; disable live AI responses and LLM document generation; do not use mock responses or silently fall back."
      governance_connectivity:
        runtime: not_required
        update: none
      external_services:
        - "Existing configured LLM API provider, if present; provider identity must be observed rather than guessed."
        - "Existing authorized EO write interface, only if exposed."

LLM connectivity and PCP governance connectivity are separate. A missing LLM provider must not disable unrelated Dashboard sections or manual draft editing.

## Implementation Approach

1. Read the actual local repository AGENTS.md, PROJECT_STATUS.md, README.md, both existing V1 workorders, current design demo and this addendum.
2. Inspect and report the actual local repository root, branch, full HEAD, working-tree status including untracked files, worktrees, Dashboard stack/start method, service/listener and existing LLM/EO adapter configuration. Do not assume remote main represents the local implementation.
3. Preserve all local commits, uncommitted changes, untracked files and existing POC evidence.
4. Compare the existing Dashboard with the new design reference and implement only the missing conversational intake experience.
5. Reuse the existing frontend/backend stack and adapter boundaries. Keep the implementation proportional; do not introduce new infrastructure when an existing interface is sufficient.
6. Implement the dossier, provenance states, document preview/revision and explicit confirmation flow.
7. Connect to an existing configured LLM provider only if actually present. If none is configured, complete all safe UI/manual-draft work and report the exact configuration required for live AI.
8. Use the existing EO write path only if it is genuinely available and authorized; otherwise export the canonical EO Workorder draft.
9. Run focused tests for changed conversation/dossier/document/EO-boundary behavior and affected navigation. Reuse unaffected V1 test evidence; do not repeat unrelated tests.
10. Update PROJECT_STATUS.md with actual implementation, provider and EO integration state, tests and remaining gaps.
11. Do not stop after returning a plan or gap list. Complete the authorized implementation that can proceed without the unresolved external configuration.

## Validation

1. The primary task-creation action opens the conversational workspace, not the old form/modal.
2. A user can start with free text and continue through multiple turns.
3. Follow-up questions adapt to the current requirement gaps; the UI does not force a fixed questionnaire.
4. Quick replies and free-text replies both work.
5. The requirement dossier updates and visibly distinguishes all four provenance states.
6. The user can correct a dossier item or change scope without losing confirmed facts.
7. Draft documents can be generated with unresolved items explicitly retained.
8. Documents can be previewed and revised before approval.
9. Explicit user confirmation is required before EO Job/Workorder creation.
10. No ES Execution/Attempt/Invocation, Ruflo dispatch or Autoloop Run is created by intake.
11. If LLM configuration is absent, the UI reports the exact gap and does not claim live AI behavior.
12. If EO write is unavailable, the system exports a Workorder draft and does not create a parallel task record.
13. No credential is exposed to browser code.
14. Existing seven Dashboard sections remain usable; run only focused regression checks for affected navigation and shared components.
15. The local Dashboard continues to use its existing service pattern and authorized cbnet HTTPS/LAN boundary.

## Deliverables

- Updated Dashboard V1.1 conversational intake implementation in the existing local workspace.
- Screenshots of the conversation workspace, live dossier and document preview/confirmation.
- Example generated requirement/document package.
- Actual LLM provider connection status and exact configuration gap, if any.
- Actual EO Workorder creation/export behavior and evidence.
- Confirmation that no ES execution or Ruflo/Autoloop dispatch occurred during intake.
- Focused test results.
- Updated PROJECT_STATUS.md.
- Exact changed-file summary and Git commit SHA(s).
- Remaining gaps with concrete unblock conditions.

## Stop Conditions

- Stop only for a real repository identity conflict, destructive-operation risk, protected-data/credential issue, or an unavoidable technical incompatibility.
- Missing LLM configuration stops only live AI invocation; continue UI and manual draft functionality.
- Missing EO write interface stops only canonical EO record creation; continue document generation/export.
- Missing persistence support does not justify adding a new database; provide session-scoped draft/export and report the limitation.
- Do not convert any of these local capability gaps into a global Dashboard blocker.

## Execution Profile

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

## Execution Environment

    execution_environment:
      expected:
        os: Linux
        shell: bash
        shell_version: UNKNOWN
        runner_type: Codex CLI on cbnet WSL2 Ubuntu 24.04
      sources:
        - type: workorder
          ref: "Su9moon/PCP-Engineering-Runtime:workorders/WO-20261126-001-PCP-ENGINEERING-CONTROL-CENTER-CONVERSATIONAL-INTAKE-V1.1.md"
        - type: repository_evidence
          ref: "Su9moon/PCP-Engineering-Runtime:AGENTS.md"
        - type: repository_evidence
          ref: "Su9moon/PCP-Engineering-Runtime:PROJECT_STATUS.md"
        - type: repository_evidence
          ref: "Su9moon/personal-ai-control-plane@22bae955686f03c5f440cdcd66e13a69f1289f90:governance/PCP_EXECUTION_ENVIRONMENT_RESOLUTION_BASELINE.md"
      resolution:
        runtime_confirmation_required: true
        critical_fields:
          - actual local repository path, branch, HEAD and Git status
          - actual WSL OS and shell
          - actual Dashboard stack/runtime and listener
          - actual LLM provider configuration, if live AI is to be enabled
        mismatch_policy: explicit_fallback_allowed

## Dispatch

Execute directly in the existing local cbnet Codex CLI project/workspace for Su9moon/PCP-Engineering-Runtime.

Read this exact workorder and its governing references. Preserve the actual local branch and working tree; do not assume this handoff branch is the implementation branch. Do not dispatch through CB Bridge or wait for a Tunnel Client. Do not modify CB Blue/Green, EO/ES schemas, Ruflo/Autoloop source, or production systems.

Continue the existing Dashboard V1 implementation and add the V1.1 conversational intake. Do not return only a plan or audit report.
