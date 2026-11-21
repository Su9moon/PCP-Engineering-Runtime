# PCP Skill Governance

- Status: `FIXED`
- Version: `V0.3`
- Fixed date: `2026-09-18`
- Scope: all PCP domains, GPT / Codex / Agent execution paths

## Purpose

Define what may become a PCP Skill and keep Skills thin, reusable, and executable.

A Skill is a repeatable execution behavior. It is not a knowledge container, architecture baseline, runtime state machine, or one-off task description.

## Skill Admission Rule

Create or formalize a Skill only when all conditions are true:

1. It is a repeatable behavior, not merely knowledge or a definition.
2. GPT / Codex / Agent will actually execute it.
3. It has appeared repeatedly in real work or has been explicitly approved as a reusable behavior.
4. It can be expressed as a short deterministic procedure or constraint set.
5. It should work without relying on chat memory to be performed correctly.

If any condition is missing, do not package it as a Skill.

## Correct Carrier

- Definition / architecture / long-lived truth -> `Baseline / Protocol`
- One-time action -> `Workorder`
- Periodic governance or review -> `Process / Automation`
- Runtime state / lease / retry / heartbeat / policy enforcement -> `Runtime / Code / Policy`
- Repeatable agent execution behavior -> `Skill`

## Canonical Skill Location

Repository-level PCP Skills use the native Agent Skills layout:

`/.agents/skills/<skill-name>/SKILL.md`

The PCP Git repository is the canonical source. Do not maintain a second canonical copy under `/skills/` or a custom Skill registry that duplicates native discovery metadata.

## Thin Skill Rule

A PCP Skill should contain only what the executor needs at execution time:

- trigger;
- required input;
- minimal rules or steps;
- output or stop condition;
- exact references to detailed governance/process/baseline when needed.

Do not copy full baselines, architecture definitions, long explanations, or large process documents into a Skill.

Detailed truth remains in Git documents and is referenced by exact path.

## Shared PCP Skills Fixed in V0.3

- `.agents/skills/pcp-workorder-handoff/SKILL.md`
- `.agents/skills/pcp-session-bootstrap/SKILL.md`
- `.agents/skills/pcp-experience-reuse/SKILL.md`
- `.agents/skills/pcp-domain-bootstrap/SKILL.md`

These are cross-cutting PCP capabilities and are not owned by Engineering Operations or any other single work domain.

`pcp-domain-bootstrap` standardizes the repeatable governance behavior for creating/formalizing PCP domain repositories: canonical authority remains upstream, downstream repositories receive commit-pinned authorized snapshots, and repository ownership boundaries are fixed before domain-specific implementation begins.

## New Skill Rule

When a repeated behavior appears suitable for formalization:

1. identify it as a Skill candidate;
2. remind the user that it may be worth fixing as a Skill;
3. do not create or promote it automatically;
4. create/fix it only after explicit user confirmation;
5. commit it to Git with its exact canonical path.

Existing Skills are not automatically rewritten by this document. Any semantic refactor of existing Skills is a separate reviewed change.
