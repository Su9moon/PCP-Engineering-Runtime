# PCP Repository Rules

## 全项目最高优先级工程原则｜不得人为设障（用户 2026-10-18 明确要求）

**先读：** `governance/PCP_ENGINEERING_AGILITY_PRINCIPLE.md`。在 PCP 及下游项目的正常开发、升级、注册和验收中，AI/Agent **不得自行添加固定 Git 分支、固定文件数量/子集、额外版本身份、重复批准、无必要的 Gate/锁/流程**。历史阶段限制若已不符合现行用户目标，应修正旧实现而不是迫使现行目标适配旧限制。优先原地复用、最小改动、快速完成。**不得以本原则扩大生产、凭据、数据或破坏性操作权限**；只有经事实证明必要的技术/安全保护才保留。既有后文历史要求如与此原则冲突，以现行用户要求和本条为准；不要为本条再创建新的审批机制。


1. Git Markdown files are the current source of truth for capability assets.
2. `assets/inbox/sources/` is the shared landing zone for raw or lightly structured experience extractions from existing work conversations/projects.
3. Extraction work must preserve provenance and uncertainty. Do not convert every finding into a Skill.
4. Candidate promotion is a separate review step. Use `assets/candidates/` only after review.
5. `assets/validated/` is reserved for assets with repeated evidence or explicit review approval.
6. Do not introduce databases, vector stores, RAG, custom orchestration runtimes, or formal Skill generators during the V0 bootstrap unless separately approved.
7. Source extraction agents may create or update only the exact files named by their work order unless the work order explicitly expands scope.
8. Architecture/general-mechanism work follows `processes/architecture-governance-gate.md`. Before proposing a new PCP Core concept, reusable Engine/Manager/Store/Router, multi-project infrastructure, or other generic mechanism, classify the task, confirm real-use evidence, identify existing mature capability, and apply `.agents/skills/cross-domain-discovery/SKILL.md` when required. The valid decision is REUSE / INTEGRATE / BORROW / BUILD / DEFER. BUILD is allowed only for a proven PCP-specific remainder, and formalization must be the minimum justified by real use.
9. On a new execution conversation for an existing PCP project, apply `.agents/skills/pcp-session-bootstrap/SKILL.md` once. Session Bootstrap must inspect the workorder architecture gate before execution.
10. Before a new workorder, reusable-pattern, governance/process decision, or generic mechanism, apply `.agents/skills/pcp-experience-reuse/SKILL.md`.
11. Weekly capability review follows `processes/weekly-capability-review.md`.
12. PCP task handoff follows `.agents/skills/pcp-workorder-handoff/SKILL.md`: dispatch by exact `repo + workorder path`; the workorder references exact governing baseline/protocol paths and carries an explicit `architecture_gate`; do not scan to guess the source of truth.
13. New or modified Skills must comply with `governance/PCP_SKILL_GOVERNANCE.md`. Identify and surface suitable Skill candidates, but do not create or promote them without explicit user approval.
14. Creating or formalizing an independent PCP domain repository follows `.agents/skills/pcp-domain-bootstrap/SKILL.md`: establish upstream canonical authority first, pin the exact upstream commit, propagate only an authorized non-canonical snapshot downstream, fix the domain boundary before implementation, and inherit the Architecture Governance Gate.
15. Required but incomplete Architecture Governance Gate is a STOP condition. A missing gate must not be silently treated as `not required`.

16. Release / Runtime Independence follows `governance/baselines/PCP_RELEASE_RUNTIME_INDEPENDENCE_BASELINE_V0.1_FIXED.md`. Deployable/production runtimes consume an Installed Release and MUST NOT assume live PCP/Domain Git access unless their Connectivity Contract explicitly requires it. LLM/service connectivity and Governance connectivity are separate dimensions.

17. 对于 PCP WebGPT 多角色、Chrome/Relay、工程层级与雷达式工作台相关任务，**首先读取现行五角色基线** `governance/baselines/PCP_WEBGPT_ROLE_ORGANIZATION_V0.2_FIXED.md`；旧三对话基线 `governance/baselines/PCP_WEBGPT_MULTI_CONVERSATION_ROLE_COLLABORATION_BASELINE_V0.1_FIXED.md` 保留作历史对照，已由 V0.2 取代其角色组织与交接优先级。**五个固定 WebGPT 角色：Supervisor、Chief Engineer、Execution Coordinator、Reviewer、Operations；PCP Controller 是主控制面板而非第六个 Agent；N 个 Codex Worker 执行任务**。总工负责设计、协调员负责细分派工、Reviewer 独立且不扩需求、Operations 按需唤醒。五对话无人值守运行/MCP/恢复均未验收。不得私自改动组织边界或复制 EO/ES/CB 任务队列，不得把 Charterion/OpenTeam 当成已批准依赖。

