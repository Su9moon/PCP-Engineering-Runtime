# PCP Architecture Governance Gate

**Status:** Canonical Process
**Scope:** PCP architecture and reusable-mechanism governance
**Governing principle:** governance/baselines/PCP-01_系统定位与核心边界_V0.2_FIXED.md

## Purpose

This process operationalizes PCP-01. It does not create a new architectural principle or a new runtime component.

Its purpose is to prevent a recurring failure mode:

    a capability sounds useful
    -> PCP models it completely
    -> objects / schema / runtime are formalized
    -> only later does real use reveal that the model was too heavy
       or mature infrastructure already owned the mechanics

The required order is:

    classify
    -> inspect real-use evidence
    -> inspect existing capability
    -> cross-domain discovery when required
    -> identify the PCP-specific remainder
    -> choose the minimum formalization
    -> only then design or implement

## 1. Classification
## 用户授权的反人为设障约束（2026-10-18）

此 Architecture Governance Gate 的目的在于避免无根据地建设复杂机制，**不是让 Agent 自行增加开发审批层级**。执行时必须遵循 `governance/PCP_ENGINEERING_AGILITY_PRINCIPLE.md`：

- 正常 bugfix、已定边界内的功能开发、版本升级、实例复用，不因为过去某版固定分支、源码子集、身份或旧工作流而自动新增“审批/冻结/复核”关卡。
- 旧方案/代码出现硬编码限制但已与当前目标冲突时，应以真实依赖及危险性判断是否需要保留；无技术必要就修正，不让遗留的 E0a/MVP 机制定义当前业务目标。
- 不新增通用 Gate、调度、状态或流程来执行此要求；完成必要的真实技术验证即可。
- 对跨越用户授权的部署、破坏性修改、凭据及生产数据操作，保留现行授权边界；不以“不要设障”为由越权。



Every proposed task that may change architecture or create a reusable mechanism must be classified before design or implementation.

### Routine

Examples:

- clear bug fix;
- small feature using an already-approved pattern;
- implementation inside an already-approved architecture;
- documentation correction that does not change a durable rule.

Routine work does not require Cross-Domain Discovery.

### Architecture / Generic Capability

The Gate is required when the proposal would:

- create or modify a PCP Core abstraction;
- create a reusable Engine / Manager / Store / Router or equivalent;
- create long-lived or multi-project infrastructure;
- formalize a repeatedly observed mechanism;
- define durable State / Evidence / Memory / Agent / Governance semantics;
- introduce a generic runtime, orchestration, persistence, policy, or integration mechanism;
- materially change ownership, authority, replaceability, or cross-domain contracts.

When classification is uncertain, classify as Architecture / Generic Capability until the Gate determines otherwise.

## 2. Real-use Evidence

Before formalizing a generic mechanism, ask:

> Has the need appeared in real work strongly enough to justify durable PCP semantics now?

Valid evidence may include:

- repeated real tasks;
- a real failure or maintenance burden;
- an existing POC that exposed a concrete gap;
- production or operational behavior;
- a validated integration constraint;
- a user-approved architecture problem grounded in current work.

Real-use evidence is not the same as "this may be useful later".

If real-use evidence is absent:

    default = DEFER
    or
    continue with a narrowly scoped POC

Do not create a complete object model merely to prepare for a hypothetical future need.

## 3. Existing Capability

Before PCP builds mechanics, identify whether mature systems already own them.

Examples include:

- Git / GitHub for versioning, review, history and CI;
- durable runtimes for queue, retry, recovery, persistence and scheduling;
- provider-native SDK/API/runtime behavior;
- standard schemas and validators;
- artifact stores, observability systems and databases.

The question is not "can PCP implement this?"

The question is:

> What mechanics can remain owned by an existing mature system while PCP keeps only the required semantics, governance, contracts and relationships?

## 4. Cross-Domain Discovery

When required, apply:

    .agents/skills/cross-domain-discovery/SKILL.md

The decision must be one of:

- REUSE
- INTEGRATE
- BORROW
- BUILD
- DEFER

BUILD is valid only after the scan and evidence identify a real PCP-specific remainder.

## 5. PCP-specific Remainder

Record the irreducible part PCP must own.

Typical PCP-owned concerns may include:

- canonical semantics;
- governance and policy;
- authority boundaries;
- relationships and references;
- stable contracts;
- provider-neutral capability requirements;
- integration boundaries.

Mechanics already supplied by mature infrastructure are not automatically part of the remainder.

Provider/runtime-specific complexity must terminate at the appropriate Adapter / Integration Boundary.

## 6. Minimum Formalization

After the remainder is known, choose the smallest durable formalization required now.

Possible levels, from light to heavy:

    reference / note
    -> rule / checklist
    -> workorder field
    -> contract
    -> canonical object
    -> persistent schema
    -> runtime component

Do not skip directly to a canonical object, schema, or runtime component when a reference, contract, or thin adapter is enough.

Principle:

> Own only the stable semantics that real use has justified.

"PCP owns semantics" does not mean "PCP models everything in advance".

## 7. Gate Record

Architecture / Generic Capability work must carry a gate record in the governing workorder/task.

Minimum form:

    architecture_gate:
      required: true
      status: complete
      real_use_evidence: verified
      decision: INTEGRATE
      pcp_specific_remainder: "..."
      minimum_formalization: "..."

Allowed status when required: true:

- complete
- waived

A waiver must include a reason and is an explicit governance decision, not an implicit skip.

Routine work may use:

    architecture_gate:
      required: false
      reason: routine_implementation

## 8. Stop Rule

If architecture_gate.required = true and the status is neither complete nor an explicitly justified waived, architecture or implementation work must stop.

The next action is to complete the Gate, not to continue designing the mechanism.

## 9. Domain Inheritance

Independent PCP domain repositories must inherit this process through their entry rules.

A domain repository must not create a second canonical copy of PCP-01.

Domain bootstrap must ensure that:

- the domain AGENTS.md routes applicable work through this Gate;
- the exact canonical process path is referenced;
- if a downstream snapshot is required for autonomous execution, it is marked non-canonical and pinned to an exact upstream commit;
- domain-specific governance may narrow the rule but may not silently remove it.

## 10. Workorder Handoff and Session Bootstrap

The expected routing order is:

    Session Bootstrap
    -> read exact Workorder
    -> classify task / inspect architecture_gate
    -> complete Architecture Governance Gate when required
    -> execute authorized work

The executor must not infer that a missing gate means not required.

## 11. Mechanical Validation

Machine validation is a backstop, not a new governance runtime.

For governance-sensitive paths, a lightweight repository check may require an explicit workorder reference and validate the gate record.

Preferred implementation:

    GitHub Actions
    +
    small validation script

Do not build a custom Governance Engine for this purpose.

## 12. Validation Target

The first live validation target after this process is adopted is the next new ES architecture/general-capability task.

Success means the task reaches design only after:

    real-use evidence
    -> existing capability review
    -> discovery / POC when needed
    -> PCP-specific remainder
    -> minimum formalization

EO remains at V0.1 until ES has produced enough real runtime evidence for a later EO alignment review.
