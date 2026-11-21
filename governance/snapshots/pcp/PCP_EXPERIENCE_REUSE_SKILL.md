---
name: pcp-experience-reuse
description: Reuse existing PCP experience before creating a new workorder, reusable pattern, governance/process rule, or generic mechanism.
---

# PCP Experience Reuse

References:
- `governance/PCP_SKILL_GOVERNANCE.md`
- `processes/experience-reuse-gate.md` — Decision Reuse Gate

## Rules
The current user-directed cross-project engineering principle is `governance/PCP_ENGINEERING_AGILITY_PRINCIPLE.md`. When reusing prior experience, never promote an obsolete MVP implementation restriction (fixed branch, file-count/source subset, identity, or extra approval gate) into a requirement for routine development or upgrades without current user authorization or demonstrated technical necessity. This Skill adds **no new gate**.



1. Apply the Decision Reuse Gate before creating a new workorder, reusable pattern, governance/process rule, or generic PCP mechanism.
2. Use the retrieval order defined in `processes/experience-reuse-gate.md`; load only task-relevant fragments.
3. Classify the result as `REUSE`, `EXTEND`, `NEW_CANDIDATE`, or `PROJECT_LOCAL`.
4. Candidate and Inbox material are evidence, not authoritative guidance.
5. Do not promote assets or package a new Skill during this gate.
6. If the proposal creates a new PCP Core concept or reusable generic mechanism, also apply `.agents/skills/cross-domain-discovery/SKILL.md`.
