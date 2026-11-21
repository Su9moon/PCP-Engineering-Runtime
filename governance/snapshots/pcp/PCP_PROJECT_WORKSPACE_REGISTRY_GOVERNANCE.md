# PCP Project / Workspace Registry Governance

- Status: **FIXED**
- Version: **V0.1**
- Fixed date: **2026-09-20**
- Scope: PCP cross-domain project/workspace registry
- Parent baseline: `PCP_PROJECT_WORKSPACE_IDENTITY_BASELINE_V0.1_FIXED.md`

## 1. Purpose

The PCP Project / Workspace Registry exists to reduce reliance on human memory when mapping a Domain to its Git, local workspace, Codex, Web GPT, and execution surfaces.

The Registry is a discovery / mapping / reminder mechanism.

It is not a new source of business truth, and it must not turn volatile machine state into cross-machine canonical semantics.

## 2. Authority Split

Registry information is divided into two classes.

### 2.1 Stable Domain Mapping

Stable mapping may be governed in Git.

Examples:

- `domain_id`;
- canonical repository identity;
- canonical branch;
- expected persistent-workspace convention;
- Local Codex project naming convention;
- Web GPT project naming/recommendation;
- whether a project surface is recommended / optional / not required;
- schema and allowed status vocabulary.

These are durable governance facts.

### 2.2 Local Runtime / Machine State

Volatile machine-local state must remain local runtime evidence.

Examples:

- absolute local path on one machine;
- current local HEAD;
- staged / unstaged / untracked files;
- worktree currently active / paused;
- whether a Desktop UI object currently exists;
- current Codex Desktop selection;
- current process / lock / execution occupancy;
- temporary migration or cleanup state.

These values may be recorded in a locally generated Registry instance, result bundle, or evidence file, but they are not promoted to cross-machine canonical truth merely because they appear in a Registry.

## 3. Canonical Rule

The canonical object is the **Registry schema / governance contract**, not a machine snapshot.

Therefore:

```text
Git
= Registry schema / stable Domain mapping / governance rules

Local generated Registry
= current machine observation
```

A local Registry snapshot may be checked into Git only when explicitly required as evidence or a reviewed configuration artifact. If checked in, it must clearly identify its machine / observation scope and must not be interpreted as universally current.

## 4. Verification Provenance

A status such as `ready` is incomplete unless its verification basis is known.

Where the Registry schema supports it, record a verification method.

Recommended values:

```text
git_verified
filesystem_verified
runtime_verified
user_confirmed
provider_verified
inferred
unverified
```

### git_verified

Verified from Git repository state or remote canonical source.

### filesystem_verified

Verified from the actual local filesystem / worktree.

### runtime_verified

Verified by the relevant executor / runtime through a supported interface.

### user_confirmed

The user explicitly confirmed an external/UI state that the executor cannot verify through a supported interface.

Examples:

- Local Codex Project exists and points to the intended persistent root;
- Web GPT Project exists;
- a Desktop-only project surface has been created or renamed.

### provider_verified

Verified through an official provider API / connector.

### inferred

Derived indirectly and not independently confirmed.

Must not normally be used to promote a state to `ready`.

### unverified

No reliable verification exists.

## 5. Ready-State Rule

A component may be marked `ready` only when there is an appropriate verification source for that component.

Examples:

```yaml
local:
  status: ready
  verification_method: filesystem_verified

codex:
  status: ready
  verification_method: user_confirmed

web_gpt:
  status: ready
  verification_method: user_confirmed
```

If the current schema does not yet contain `verification_method`, the status may still be updated after valid verification, but the verification source must be recorded in the corresponding result / follow-up evidence.

Do not keep a state at `manual_ui_check` after the user has explicitly confirmed the relevant UI state.

Do not mark a UI state `ready` merely because a filesystem path or Git repository exists.

## 6. Allowed Status Vocabulary

Recommended stable status vocabulary:

```text
ready
not_initialized
not_required
manual_ui_check
blocked
deprecated
retired
```

Machine-specific workflows may use additional transient states, but those states should not become cross-domain semantics unless repeated real use justifies formalization.

## 7. Worktree State

Persistent and managed worktree status are separate concerns.

A Domain may be locally ready while also having a protected managed execution state.

Example:

```yaml
local:
  status: ready

protected_work_state:
  status: paused
  managed_worktree: <machine-local path>
```

The existence of a protected managed worktree does not automatically make the Domain local workspace invalid.

Managed-worktree lifecycle semantics should not be expanded into a new generic runtime model until repeated real use justifies it.

## 8. UI Verification Boundary

Codex / Agent execution must not manipulate or inspect opaque Desktop / Web UI state through unsupported means.

When a required UI state cannot be verified through a supported interface:

```text
manual_ui_check
```

is correct.

Once the user explicitly confirms the UI state:

```text
status: ready
verification_method: user_confirmed
```

is correct.

The lack of machine-verifiable UI access is not, by itself, a blocker to a user-confirmed project surface.

## 9. Progressive Provisioning

Registry state must preserve the existing PCP progressive-provisioning model.

Valid examples include:

```text
Git: READY
Local: NOT_INITIALIZED
Codex: NOT_INITIALIZED
Web GPT: NOT_REQUIRED
```

A missing optional surface is not an error.

## 10. Non-Goals

This governance does not introduce:

- a registry service;
- a database;
- a daemon;
- a synchronization runtime;
- a Desktop automation layer;
- a custom discovery engine;
- a new scheduler or orchestrator.

If repeated real use later proves such mechanics necessary, they must pass the Architecture Governance Gate before implementation.

## 11. Final Rule

```text
Stable mapping / schema
→ governed in Git

Current machine state
→ locally observed / generated

Ready state
→ requires appropriate verification provenance

Unsupported UI state
→ user confirmation is valid evidence

Registry
→ discovery / mapping / reminder, never a parallel source of truth
```
