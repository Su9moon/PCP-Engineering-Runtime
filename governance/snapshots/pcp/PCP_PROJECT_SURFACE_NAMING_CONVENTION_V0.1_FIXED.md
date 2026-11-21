# PCP Project Surface Naming Convention

- Status: **FIXED**
- Version: **V0.1**
- Fixed date: **2026-09-20**
- Scope: PCP project-surface naming and routing
- Parent baseline: `PCP_PROJECT_WORKSPACE_IDENTITY_BASELINE_V0.1_FIXED.md`

## 1. Purpose

ChatGPT Desktop may surface Web GPT Projects and Local Codex Projects in the same navigation area.

To avoid confusing reasoning context with local execution context, PCP uses an explicit display-name convention for Local Codex Projects.

This convention affects UI naming only. It does not create a new Domain identity or canonical source.

## 2. Naming Rule

### Web GPT Project

Use the normal human-readable Domain / project name:

```text
<Project Name>
```

Examples:

```text
PCP Execution Server
PCP Engineering Operations
PCP Human Bridge
WPOS Business
```

### Local Codex Project

Prefix the corresponding local Codex project display name with:

```text
Lo_
```

Format:

```text
Lo_<Project Name>
```

Examples:

```text
Lo_PCP Execution Server
Lo_PCP Engineering Operations
Lo_PCP Human Bridge
Lo_WPOS Business
Lo_Codex Tools
```

## 3. Meaning of `Lo_`

`Lo_` means:

```text
Local Codex Project / Local Execution Context
```

It is only a human-visible disambiguation prefix.

It MUST NOT change:

- `domain_id`;
- Git repository name;
- Remote repository identity;
- persistent worktree path;
- managed worktree identity;
- branch naming;
- PCP canonical semantics.

For example:

```text
domain_id:
pcp-execution-server

remote repository:
pcp-execution-server

persistent workspace:
F:\0 codex\worktrees\persistent\pcp-execution-server

Web GPT Project:
PCP Execution Server

Local Codex Project:
Lo_PCP Execution Server
```

All of these surfaces still refer to the same Domain identity.

## 4. Work Routing

Default routing:

```text
Web GPT Project
= reasoning / planning / architecture / review / workorder preparation

Git Baseline / Issue
= canonical definition and executable task contract

Lo_ Local Codex Project
= repository execution / file changes / tests / diff / commit / PR
```

Once a Domain, Git baseline, and Issue / workorder are defined, execution should normally continue in the corresponding `Lo_` Local Codex Project.

The Local Codex Project should use that Domain's persistent worktree as its stable project root.

## 5. Historical Conversations

Existing historical Web / Work / Codex conversations do not need to be migrated merely to match the new naming convention.

Completed historical conversations may remain in their original location.

If an old conversation contains an important rule or decision that was never promoted to Git, the correct action is to validate and promote that information into the appropriate canonical Git document, not to rely on chat relocation as knowledge migration.

## 6. Progressive Provisioning

The `Lo_` convention is a naming and discovery aid, not a hard bootstrap gate.

A Domain remains valid even when a Local Codex Project or Web GPT Project has not yet been created.

When both surfaces exist, the naming convention should be used to make their roles immediately distinguishable.

## 7. Final Rule

```text
<Project Name>
= Web GPT reasoning / planning / review context

Lo_<Project Name>
= Local Codex execution context
```

Git remains the canonical source of formal state. Neither project surface becomes a parallel fact source.
