# PCP Execution Server Architecture Baseline V0.3

> 整理日期：2026-09-21
> 状态：Architecture Baseline V0.3 / ES-03 V0.2 Runtime Boundary Aligned
> 目的：固定 PCP Execution Server 的语义权威、职责边界、状态模型，以及可替换 runtime/provider 与 Executor 的接入边界。
> 修订依据：`tasks/TASK-005-es-baseline-runtime-boundary-alignment.md`；`pcp-execution-server` 中 ES-02、ES-03 V0.2、ES-04、Attempt Authority ADR 与 WO-20260921-001/002 Gap Analysis。
> 权威说明：本文件仍是上游 canonical architecture baseline；Execution Server 证据用于验证和对齐边界，不反向成为上游架构事实源。
> 当前结论：PCP 固定 execution semantics 与 canonical authority；queue、scheduler、dispatch、heartbeat、timeout、retry 和 durable workflow mechanics 可由可替换 runtime/provider 承担，但 binding 必须证明 PCP invariants 得到保留。

---

# 1. 背景

当前已经验证和讨论过 `Codex with ChatGPT` 的工作方式。

其原始思路主要是：

```text
本地 Codex
   ↓
调用 ChatGPT
   ↓
ChatGPT 规划 / 分析
   ↓
Codex 本地执行
   ↓
ChatGPT 再复核
```

这个模式对于“正在本地运行的 Codex，希望增加一个云端规划者和第二审查者”是成立的。

但对于 PCP 的长期目标，它存在明显方向差异：

- 控制权主要由本地 Codex 发起；
- Web ChatGPT 不能自然成为长期总控；
- 对话、执行、状态和恢复仍然围绕 Codex Session 组织；
- Codex 被赋予了过多流程主导权；
- 它没有真正抽象出独立于 Codex 的任务、权限、执行器和状态机。

而 PCP 的目标不是：

> 给 Codex 找一个更聪明的协作者。

而是：

> 让任务、状态、策略、权限和执行过程独立存在，Codex 只是其中一个可以被调度的 Executor。

因此，当前方向正式调整为：

```text
Codex with ChatGPT
        ↓
不作为 PCP 主架构
        ↓
保留其中有价值的本地连接能力
        ↓
Codex 成为 PCP Execution Server 下的一个 Executor
```

---

# 2. 核心结论

## 2.1 PCP Execution Server 的定位

`PCP Execution Server` 是 PCP 下的通用执行语义与 canonical runtime authority 模块。它可以通过可替换的 Runtime Binding / Provider 使用成熟编排能力，不要求 PCP 自建全部 runtime mechanics。

它不是：

- Codex 专属服务；
- 远程 Shell；
- ChatGPT 到本地电脑的穿透工具；
- 单纯的工单数据库；
- 单纯的 Agent 框架；
- WPOS 的业务工单系统。

它的职责是：

```text
将 PCP 中已经明确的任务
        ↓
转化为可执行的 ExecutionRequest
        ↓
经过 Policy / Approval
        ↓
授权并关联一条实际执行路径
        ↓
由 Runtime Binding / Provider 承载运行机制
        ↓
验证 runtime facts 并维护 canonical state
        ↓
收集 Result / Evidence
        ↓
进入 Review / Approval
        ↓
回写 PCP / Git
```

因此，它本质上属于：

```text
PCP Control Plane
        ↓
Execution Semantics / Canonical Runtime Authority
```

## 2.2 Work Intent 与 Execution Contract 分离

正式固定：

```text
Engineering Operations / Other Work Plane
        │
        │ Workorder / Intent
        ▼
Mapping / Adapter
        │
        ▼
PCP Execution Server
        │
        │ Northbound Execution Contract
        ▼
ExecutionRequest
```

Execution Server 不拥有 Engineering Operations Workorder 的定义权。Workorder
及其上层意图由调用方或所属 Work Plane 负责；Mapping / Adapter 将已明确的
意图映射为 Execution Server 可处理的请求。

## 2.3 ExecutionRequest 是 execution projection

正式固定：

```text
Workorder
= Authoritative Work Intent

ExecutionRequest
= Machine-executable execution projection / snapshot
```

ExecutionRequest 可以携带执行所需的 objective snapshot、acceptance
reference/snapshot、constraints 与 source references，但这些字段不得成为
新的上层工程事实源。

## 2.4 Work Item → Dispatch → Execution Instance

正式固定 PCP 执行链路中的三层语义：

```text
Work Item
   ↓
Dispatch
   ↓
ExecutionRequest
   ↓
Execution Instance
```

三层分别拥有不同事实：

- **Work Item owns intent**：拥有 WHY / WHAT、目标、Acceptance intent 与可持续演进的任务语义；
- **Dispatch freezes intent**：显式选择 Work Item 的一个确定版本 / snapshot，将其映射并冻结为本次机器可执行的 `ExecutionRequest`；
- **Execution Instance owns runtime facts**：拥有 WHO / WHERE / WHEN / STATUS / RESULT 等某一次真实运行事实。

因此：

1. Work Item 可以继续修改，但已 Dispatch 的 ExecutionRequest 不得被上游后续修改静默改变；
2. Work Item 发生影响执行语义的修改后，如需生效，必须显式重新 Dispatch，并产生新的 ExecutionRequest / Execution；
3. ExecutionRequest 是 Dispatch 的产物，不是 Work Item 本身，也不是 Execution Instance 本身；
4. 同一个 Work Item 可以被 Dispatch 多次，也可以产生多次 Execution；历史 Execution 的结果不得反向覆盖 Work Item 的长期意图事实；
5. Runtime Retry / Recovery / Revision 在同一个 frozen ExecutionRequest 下需要新的实际执行路径时，必须创建新的 Attempt；已终止 Attempt 不得重新进入 RUNNING，也不得破坏上述三层事实所有权。

这条边界适用于 GitHub Issue、Engineering Operations Workorder、WPOS Case、ChatGPT Task 以及未来其他 Work Item 来源。

## 2.5 Northbound Contract、Runtime Binding 与 Executor Adapter 分离

正式固定：

```text
Caller
   ↓
Northbound Execution Contract
   ↓
PCP Execution Server
   ↓
Runtime Binding / Runtime Participant
   ↓
Executor Adapter Contract
   ↓
Concrete Executor
```

所有调用方共享 Northbound Execution Contract；Runtime Binding / Provider 承载
可替换 coordination mechanics；具体 Executor 不共享一个 concrete invocation
contract。Codex Adapter、Diagnostic Adapter、Shell Adapter 及未来 Adapter
可以分别拥有自己的 adapter contract。任何 binding 或 Adapter 都不能反向定义
ExecutionRequest、canonical state 或 current Attempt authority。

## 2.6 Review workflow 与 Acceptance authority 分离

Execution Server 可以拥有 `REVIEW_READY`、`APPROVED`、`REVISION_REQUESTED`、
`NEEDS_INPUT` 等 review routing、revision loop 和 evidence transport 能力。
但 Acceptance Criteria 的定义权来自上层 Work Intent / Workorder；Execution
Server 负责 Review Flow，不成为业务或工程目标事实源。

## 2.7 Runtime coordination 是可替换的机制边界

顶层概念固定为：

```text
Current Attempt Authority
Authority Evidence
Runtime Participant Identity / Correlation
Liveness / Loss Evidence
Stale-writer Rejection
```

`Worker Session`、`Claim`、concrete `Lease`、renew loop、heartbeat cadence、
monotonic fencing token、provider task token 和固定 Worker Pull operation 都可以是
某个 binding/profile 的实现方式，但不构成唯一 canonical runtime model。

无论选择哪种 mechanics：

- Execution Server 都是 canonical Execution / Attempt state 的唯一写入权威；
- 同一 Execution 同一时刻至多一个 active Attempt，同一 Attempt 同一时刻至多一个 current authority；
- runtime liveness 不等于 current authority；
- provider/runtime facts 只能作为输入，不能自行决定 LOST、Retry、Review、Approval 或 DONE；
- stale、revoked、expired 或 superseded authority 不得修改 canonical state；
- 新的真实执行路径必须先获得新的 Attempt 和 Invocation identity；
- Runtime Grant、cancellation outcome、late/orphan evidence、Result/Evidence/Review 边界保持由 PCP 语义约束。

---

# 3. PCP、WPOS 与 Execution Server 的关系

## 3.1 PCP

PCP 继续作为总控制面，负责：

- Project
- Goal
- Task
- Policy
- Decision
- Capability
- Knowledge
- Relation
- Approval
- Audit
- Global State

PCP 不负责亲自执行具体动作。

---

## 3.2 WPOS

WPOS 是通信公司业务 Work Plane。

WPOS 管理的是业务生命周期，例如：

```text
客户
商机
售前
报价
合同
项目
交付
售后
工单
回款
决策
```

WPOS 内的“工单”属于业务对象。

例如：

```text
医院 82663 偶发嘟声
```

可能是一个持续数天的售后 Case。

这个 Case 可以产生多个 Execution：

```text
Execution 1：分析 CDR
Execution 2：分析 FS Log
Execution 3：分析 TG Log
Execution 4：分析 PCAP
Execution 5：修改诊断脚本
Execution 6：生成最终结论
```

因此：

```text
WPOS Case != PCP Execution Ticket
```

而应该是：

```text
WPOS Case
   ↓
一个或多个 ExecutionRequest
```

---

## 3.3 Execution Server

Execution Server 是横向共享能力。

它既可以被 WPOS 使用，也可以被：

- ChatGPT Web
- 医院 AI 诊断平台
- PCP-CSB
- 其他 Work Plane
- CLI
- 未来其他 Agent / Runtime

直接调用。

因此：

```text
PCP Execution Server
```

不能依赖 WPOS 才能工作。

---

# 4. 最终逻辑架构

```text
                     ChatGPT Web
                     WPOS
                     CLI
                     其他入口
                         │
                         ▼
                ┌─────────────────┐
                │       PCP       │
                │                 │
                │ Project / Task  │
                │ Policy          │
                │ Decision        │
                │ Approval        │
                │ Audit           │
                │ Knowledge       │
                └────────┬────────┘
                         │
                         ▼
              ┌───────────────────────────┐
              │   PCP Execution Server    │
              │                           │
              │ ExecutionRequest          │
              │ Execution / Attempt       │
              │ Canonical State Authority │
              │ Current Attempt Authority │
              │ Policy / Runtime Grant    │
              │ Result / Evidence         │
              │ Review                    │
              │ Correlation / Audit       │
              └────────────┬──────────────┘
                           │ authorized path / normalized facts
                           ▼
              ┌───────────────────────────┐
              │ Runtime Binding / Provider│
              │                           │
              │ queue / scheduling        │
              │ dispatch / routing        │
              │ heartbeat / timeout       │
              │ retry / durable workflow  │
              │ provider-specific tokens  │
              └────────────┬──────────────┘
                           │
                           ▼
                Runtime Participant
                           │
                           ▼
                   Executor Adapter
               ┌───────────┼───────────┐
               ▼           ▼           ▼
          Codex Executor  Diagnostic  Future Executor
               │           Executor
               ▼
          Isolated Workspace / Artifact
               │
               ▼
              Git
```

Runtime Binding / Provider 是可替换 mechanics 层。它必须先满足 PCP
authorization，并把 provider/runtime event 归一化为 fact 交由 Execution Server
验证；任何 provider identity、status、timeout 或 success 都不能直接替代 PCP
canonical identity、authority、state 或 Review decision。

---

# 5. 主链路正式定义

未来主链路固定为：

```text
Work Plane / PCP
        ↓
Work Item / Work Intent
        ↓
Dispatch / Mapping / Adapter
        ↓
Northbound Execution Contract
        ↓
ExecutionRequest (frozen execution projection)
        ↓
PCP Execution Server
        ↓
Execution Instance / Attempt authorization
        ↓
Policy / Approval / Effective Runtime Grant
        ↓
Runtime Binding / Provider
        ↓
Runtime Participant
        ↓
Executor Adapter
        ↓
Concrete Executor
        ↓
Normalized runtime facts + durable Result / Evidence
        ↓
Execution Server validation
        ↓
Review / Approval
        ↓
PCP / Git
```

其中：

```text
Codex
```

只是：

```text
Executor = codex
```

Runtime Binding / Provider 负责可替换的运行机制；Execution Server 继续拥有
canonical state interpretation、current authority、retry/recovery authorization、
LOST、cancellation outcome 与 Review boundary。

---

# 6. 为什么不能让 Codex 继续作为流程发起者

原始 Codex with ChatGPT 的逻辑是：

```text
Codex
  ↓
请求 ChatGPT 帮助规划
  ↓
Codex 执行
  ↓
ChatGPT Review
```

这个模式的问题是：

- Executor 掌握流程发起权；
- Executor 绑定业务上下文；
- Executor 决定何时请求 Review；
- 状态依赖 Codex Thread；
- 任务脱离 Codex 后不容易独立存在；
- 很难统一接入其他 Executor；
- 很难统一做 Policy / Approval / Audit。

PCP 模式必须反过来：

```text
PCP / Work Plane
 ↓
Policy / Approval
 ↓
Execution Server canonical authority
 ↓
Runtime Binding / Provider
 ↓
Executor
```

Executor 不决定：

- 为什么做；
- 什么时候做；
- 能不能做；
- 做完以后谁验收；
- 是否允许部署；
- 是否允许写生产环境；
- 是否允许继续自动修订；
- 是否需要人工确认。

这些都必须在 Executor 外部。

---

# 7. ExecutionRequest projection 的概念

聊天内容本身不能直接等价于可执行任务。

应该经过：

```text
Conversation
   ↓
Requirement Draft
   ↓
Work Item / Workorder
   ↓
READY
   ↓
Dispatch
   ↓
ExecutionRequest
   ↓
Execution Instance
```

ExecutionRequest 是机器可执行的 execution projection / snapshot，而不是
Workorder 或上层工程事实的替代物。

它可以携带：

```text
objective snapshot
acceptance reference/snapshot
constraints
source references
```

Workorder 仍然是 authoritative Work Intent；ExecutionRequest 中的字段只
服务于本次执行、调度、审计与恢复。

示例：

```yaml
execution_id: EXE-20260916-001
project_id: hospital-billing

source:
  type: pcp_task
  source_id: TASK-1028

executor_type: codex

objective:
  修复重复计费问题

context_refs:
  - requirement: REQ-182
  - issue: BUG-37

acceptance:
  - 不再产生重复计费
  - 原有测试全部通过
  - 新增回归测试

constraints:
  writable_paths:
    - src/billing/**
    - tests/**

  forbidden:
    - production_db
    - git_push
    - deployment

risk: medium

review_policy:
  max_revision_rounds: 3
  human_on_failure: true
```

---

# 8. Execution Server 负责什么

Execution Server 负责稳定的 PCP execution semantics 和 canonical runtime
authority。它不要求通过 PCP 自建 queue、scheduler、Lease service、heartbeat
loop、retry engine 或 durable workflow engine 来实现这些语义。

## 8.1 Execution / Attempt 状态机

Execution state 与合法迁移以固定的 ES-02 Contract 为准。顶层状态类别为：

```text
Admission / Gate:
ACCEPTED
WAITING_APPROVAL
READY
QUEUED

Active / Suspension:
RUNNING
NEEDS_INPUT
BLOCKED
RECOVERABLE

Review:
REVIEW_READY
REVISION_REQUESTED

Terminal:
DONE
FAILED
CANCELLED
DENIED
REJECTED
SUPERSEDED
```

Attempt lifecycle 为：

```text
CREATED
   ↓
CLAIMED
   ├── RUNNING
   ├── CANCELLED
   └── LOST

RUNNING
   ├── COMPLETED
   ├── FAILED
   ├── CANCELLED
   └── LOST
```

固定规则：

- Execution current state 只能由 Execution Server 通过合法 transition 修改；
- authority acquisition / dispatch 与 actual runtime start 分离；
- `CLAIMED` 不等于 Execution `RUNNING`；
- Attempt `COMPLETED` 不等于 Execution `DONE`；
- Attempt `FAILED` / `LOST` 不自动等于 Execution `FAILED`；
- Retry / Recovery / Revision 启动新的实际执行路径时必须创建新的 Attempt；
- terminal Execution 和 terminal Attempt 均不得 reopen；
- Result 必须 durable 且满足 Result Contract 后才能进入 Review，Review acceptance 才能决定 DONE。

---

## 8.2 Runtime Participant Identity / Capability / Correlation

Execution Server 必须验证：

```text
authenticated principal / provider identity
runtime participant identity
applicable capability
Policy / Approval
Effective Runtime Grant
PCP-to-provider correlation
```

capability advertisement 只是 eligibility input，不授予权限。provider/runtime
identity 只是 correlation handle，不替代 `request_id`、`execution_id`、
`attempt_id` 或 `invocation_id`。

每个 binding 必须在 runtime fact 可能影响 canonical state 之前持久保存关联，
并支持发现 surviving / old runtime，接受 Server 的 stop、quarantine、ignore
或等效 reconciliation decision。

固定的 centralized Worker Registry、online 状态、load inventory 和
heartbeat record 不是 canonical implementation requirement。

---

## 8.3 Current Attempt Authority

必须保持：

```text
one Execution → at most one active Attempt
one Attempt   → at most one current execution authority
```

Execution Server 在授权实际执行路径前验证 Attempt eligibility、identity、
capability、Policy 和 Effective Runtime Grant，并拥有 current authority 的建立、
撤销、过期和终止决定。

binding 必须提供足以区分 current 与 stale authority 的 Authority Evidence，
并覆盖 start、progress/control、complete、fail、release 和 cancel
acknowledgement 等所有可能修改 canonical runtime facts 的路径。

concrete Claim/Lease object、`lease_id`、renew loop、`expires_at`、server-time
response、monotonic fencing token 或 provider-specific token 都不是唯一实现。
无论采用何种实现，stale、revoked、expired 或 superseded authority 的 mutation
都必须被拒绝。

---

## 8.4 Liveness / Loss / Cancellation Evidence

runtime liveness 与 current Attempt authority 必须分离：

```text
online / polling / heartbeat / provider running
!=
current authority
```

heartbeat、timeout、disconnect、provider failure 和 cancellation delivery 可以
由 runtime/provider 提供；它们只产生待验证的 facts。Execution Server 依据
current authority、runtime evidence、canonical state 和 Policy 决定 LOST、
authority revocation、cancellation terminal transition 以及后续 Execution state。

Cancellation / supersession 必须先记录 control intent，再取得实际停止或有效
隔离证据，最后由 Execution Server 接受 terminal transition。cancel/complete
race 以 Server append-only event order 为权威。

---

## 8.5 Retry / Recovery

Retry / Recovery / Revision 需要新的实际执行路径时：

```text
terminated old Attempt
  ↓
Execution Server + Policy authorize
  ↓
new attempt_id
  ↓
new invocation_id
  ↓
binding/provider may dispatch
```

provider automatic retry 必须被禁用、限制为 observation-only，或被 binding
gate 在新的 PCP Attempt authorization 之后；不得产生未表示的实际执行路径。

queue、re-dispatch、retry、durable replay 和 recovery engine 可以保持 external。
恢复可以使用 immutable ExecutionRequest、经过验证的 workspace/checkpoint、
Git 和 durable evidence，但 native runtime/session continuation 不得复活旧 Attempt。

---

# 9. Git 的正式定位

Git 继续作为 PCP 的长期事实源之一。

## Git 应保存

```text
需求
规则
配置
代码
Ticket / Task 定义
ExecutionRequest 快照
diff
测试结果
Review
最终结论
Evidence 索引
历史版本
```

---

## Git 不应该负责

```text
runtime participant 是否在线
heartbeat / timeout
实时 dispatch / claim / lease representation
任务抢占
即时 cancel delivery
当前运行 phase
provider retry / replay
短周期状态变化
```

因此正式采用：

```text
Git
= Durable State / Source of Truth

Execution Server
= Canonical Execution / Attempt Authority and State Interpretation

Runtime Binding / Provider
= Replaceable Volatile Coordination Mechanics
```

provider 的 durable workflow history 可以作为 runtime evidence 与 correlation
source，但不能替代 PCP canonical state、identity、authority 或 Review history。

---

# 10. Runtime concern 分类与非规范示例

V0.3 对先前 baseline 中的 concrete runtime items 作以下分类：

| Item | Classification | V0.3 baseline decision |
|---|---|---|
| Worker Registry | `binding requirement` | binding 必须提供 authenticated participant identity、capability input 与 durable correlation；centralized registry service、online/load view 不是 mandatory architecture。 |
| Scheduler | `provider mechanic` | queue ranking、fairness、load balancing 和 dispatch selection 可由 runtime/provider 负责。 |
| Claim / Lease implementation | `provider mechanic` | PCP 固定 exclusive current authority、Claim/Start separation 和 stale rejection；concrete Claim/Lease object 不是唯一实现。 |
| heartbeat loop | `provider mechanic` | heartbeat 可提供 liveness/loss/control evidence，不直接证明 authority 或决定 LOST。 |
| lease renewal | `provider mechanic` | renew cadence、expiry representation 和 control loop 属于具体 binding/profile。 |
| fencing implementation | `provider mechanic` | PCP 固定 stale-writer rejection；concrete monotonic token 不是唯一实现，binding 仍须证明所有 mutation path 的 guard。 |
| retry engine | `provider mechanic` | provider 可承载 retry/re-dispatch mechanics；每条新的实际执行路径必须先获得 PCP 新 Attempt/Invocation authorization。 |
| recovery engine | `provider mechanic` | durable replay/recovery mechanics 可外置；Server 保留 Recovery authorization、canonical transition 与 old-runtime reconciliation decision。 |
| Local Worker topology | `non-normative example` | 常驻本地进程、outbound polling 或 tunnel 都只是可选 deployment pattern。 |
| FastAPI / SQLite examples | `non-normative example` | 只保留为早期 bootstrap illustration，不是技术选择、schema/API 或 provider 决定。 |

跨所有实现保持的 `semantic requirement` 包括：

- frozen ExecutionRequest 与 Execution/Attempt identity；
- canonical state authority 与 current Attempt authority；
- stale-writer rejection 与 late/orphan evidence isolation；
- Retry/Recovery/Revision authorization 和 LOST decision；
- Effective Runtime Grant 与 independent Policy/Approval；
- cancellation outcome authority；
- Result/Evidence durability、Review separation 与 terminal immutability；
- Executor Adapter boundary 和 executor replaceability。

任何 Runtime Binding / Provider 必须逐项证明适用的 `binding requirement`。本节
不选择 provider，不定义 binding API、wire operation、storage schema 或 deployment
topology。

---

# 11. 不建议把大文件塞进 Execution Server

Execution Server 只保存状态和引用。

以下内容不应该大量进入数据库：

```text
源代码
大型 diff
PCAP
日志包
测试 artifact
文档
压缩包
模型输出全集
```

这些可以放：

```text
Git
本地 Artifact Storage
对象存储
文件系统
```

Execution Server 只保存：

```text
URI
path
hash
size
type
metadata
```

---

# 12. Runtime Participant 与 Local Worker 示例

Runtime Participant 是把一条已获授权的实际执行路径连接到 Executor Adapter 的
逻辑参与者。它可以是本地常驻进程、provider Worker、托管 Activity、远程 agent
或其他 binding-specific runtime。

`Local Worker` 仅是一个 `non-normative example`：

```text
Runtime Binding / Provider
        ↓
Local Runtime Participant
        ↓
prepare isolated workspace
        ↓
Executor Adapter
        ↓
Concrete Executor
        ↓
normalized facts / artifacts
```

在某些网络环境中，Local Worker 可以主动出站连接，从而适应 NAT、无公网 IP、
动态地址或无端口映射的机器。该拓扑不构成 canonical requirement，也不排除
provider-native pull、push、queue、direct assignment 或其他 dispatch model。

无论 topology 如何，Runtime Participant：

- 不拥有 canonical Execution / Attempt state；
- 不得自授权 Retry、Recovery、Review、Approval 或 DONE；
- 不得扩大 Effective Runtime Grant；
- authority loss 后必须停止旧 runtime，或将其隔离到不能继续产生未授权 side effect；
- 只能向 binding/Server 报告可验证 facts 和 outcome。

---

# 13. 通信模式

通信与 dispatch model 由 Runtime Binding / Provider 选择，例如：

```text
provider queue
Worker pull
server push
direct assignment
poll / long-poll
WebSocket / SSE
provider-native RPC
```

V0.3 不固定 outbound-only Worker、`claim_next` operation、heartbeat cadence、
transport、wire envelope 或 control channel。每个 binding/profile 必须记录其
dispatch model、identity correlation、authority acquisition、validity/revocation、
stale guard、start evidence、idempotency、retry gate、loss evidence、
reconciliation、cancellation、Runtime Grant 和 isolation 映射。

安全边界保持不变：

```text
不得把公网直接打开本地 Shell 作为控制面
不得绕过 Runtime Grant 直接控制本地文件系统
不得自动获得 full_access
```

---

# 14. Codex Executor 的定位

Codex Executor 是 PCP Execution Server 下的一个执行器。

它负责：

```text
收到经授权的 Invocation Input Package
↓
准备 Codex Session
↓
进入指定 Workspace
↓
修改
↓
测试
↓
生成 Result Package
```

它不负责：

```text
决定任务是否应该执行
决定风险等级
决定权限
决定是否可以部署
决定是否 push
决定是否通过验收
决定业务目标
```

---

# 15. Git Worktree 与 Attempt-scoped Isolation

PCP 固定的 semantic requirement 是：

> 每条实际执行路径使用 Attempt-scoped isolation，或可证明等效的 containment。

对于 Git code-change Execution，独立 Git worktree 是推荐的
`non-normative example`：

```text
repo/
.worktrees/
  ATT-001/
  ATT-002/
```

它可以提供多任务隔离、稳定 diff、恢复与审计。对于不适用 Git/worktree 的
Executor，binding 可以使用 sandbox、container、remote workspace 或其他等效
隔离方式。

authority loss / revocation 后，binding 必须停止旧 runtime，或将其隔离到不能
继续产生未授权 side effect。workspace identity 本身不证明 current authority。

---

# 16. Codex Thread / Session

一次 Codex execution path 必须保持以下 identity 分离：

```yaml
execution_id: EXE-001
attempt_id: ATT-002
invocation_id: AINV-002
native_runtime_ref: codex-thread-or-process-ref
```

Review 要求 revision 时：

```text
REVISION_REQUESTED
       ↓
Execution Server authorizes new Attempt
       ↓
new invocation_id
       ↓
Adapter may resume the same native Codex thread when Policy allows
```

必须明确：

> Codex Thread 是 native runtime reference，不是 PCP Attempt，也不是事实源。

即使复用同一个 native thread，新的实际执行尝试仍需新的 `attempt_id` 和
`invocation_id`。Thread 丢失时，任务仍然必须可以通过 immutable
ExecutionRequest、Git、经过验证的 workspace/checkpoint 与 durable evidence
重建。

---

# 17. Revision Loop

Review 不通过且 frozen objective / acceptance / constraints 未变化时，可以进入
`REVISION_REQUESTED`。每轮实际修订必须由 Execution Server + Policy
授权新的 Attempt 和 Invocation；不得把已终止 Attempt 重新变为 RUNNING。

revision rounds 必须有限，并由 Policy 决定。一个非规范示例是：

```text
max_revision_rounds = 3
```

每一轮必须记录：

```text
revision_round
review_reason
requested_changes
attempt_id
invocation_id
executor_result
```

超过 Policy 上限时进入 `NEEDS_INPUT` 或其他 ES-02 允许的决定路径。若
Review 要求实际改变 objective、acceptance 或 constraints，则必须 new Dispatch /
new ExecutionRequest，不得伪装为同一 Execution 下的 revision。

---

# 18. Result Package

Codex 不能只返回一句：

> 已完成。

必须返回结构化 Result。

示例：

```yaml
execution_id: EXE-001
status: REVIEW_READY

changes:
  files_modified: 4
  files_added: 2
  files_deleted: 0

git:
  base_commit: 7ac82f
  diff_ref: artifact://EXE-001/diff.patch

tests:
  total: 126
  passed: 126
  failed: 0

acceptance:
  AC-01: PASS
  AC-02: PASS
  AC-03: PASS

risks:
  - 未在真实生产数据库验证

needs_human_input: false

summary:
  已完成重复计费修复，并新增相关回归测试。
```

同时保留：

```text
git diff
test stdout
test stderr
Codex final response
artifact
相关 evidence
```

---

# 19. Review 的正式定义

Review 不是 Codex 自己说：

> 我测试过了，没问题。

而是独立审查：

```text
Acceptance Criteria
        VS
Code Diff
        VS
Tests
        VS
Evidence
```

Review 结果：

```text
APPROVED
REVISION_REQUESTED
NEEDS_INPUT
REJECTED
```

Review workflow 的路由、revision loop 与 evidence transport 属于 Execution
Server；Acceptance Criteria 的定义权仍来自上层 Work Intent / Workorder。
Execution Server 负责 Review Flow，但不成为业务或工程目标事实源。

---

# 20. Policy Gate

Policy 必须位于 Codex 外部。

示例：

```yaml
execution_policy:
  filesystem: workspace_write
  network: limited

  allow_commands:
    - pytest
    - npm test
    - npm run lint

  deny:
    - git push
    - ssh
    - deploy
    - production database
    - docker rm

  require_approval:
    - migration
    - delete
    - external_message
    - deployment
```

原则：

> Executor 不能自己升级权限。

不能出现：

```text
Codex：
我觉得需要 full_access
→ 自动获得 full_access
```

必须经过 PCP Policy / Approval。

---

# 21. ChatGPT 与 Execution Server 的关系

ChatGPT 不直接调用：

```text
codex_run()
```

而应该调用：

```text
execution_submit()
execution_get()
execution_review()
execution_cancel()
```

即：

```text
ChatGPT
   ↓
PCP
   ↓
Execution Server
   ↓
Runtime Binding / Provider
   ↓
Executor
```

而不是：

```text
ChatGPT
   ↓
Codex
```

---

# 22. 最小 MCP / Plugin 接口

ChatGPT 侧建议保持非常小。

第一版：

```text
execution_submit
execution_get
execution_review
execution_cancel
```

未来可以增加：

```text
execution_list
execution_retry
execution_artifacts
worker_status
```

其中 `execution_retry` 只表示向 Execution Server 请求一次受 Policy 约束的
新 Attempt authorization，不得直接触发 provider-hidden retry。

但不应该直接开放：

```text
shell_exec
filesystem_write_anywhere
full_access
deploy
git_push
production_db
```

---

# 23. Codex with ChatGPT 的重新定位

现有 Codex with ChatGPT 不再作为：

```text
PCP Execution Framework
```

而重新定义为：

```text
Local Runtime Access Adapter
+
部分 Codex Executor 原型能力
```

---

# 24. Codex with ChatGPT 可复用部分

## 24.1 本地 ↔ 云端轻量连接

它已经验证了：

```text
Cloud AI
   ↕
Local Workspace
```

的轻量访问方式。

这个能力有价值。

---

## 24.2 项目身份隔离

现有设计中不同工作区绑定不同项目身份。

这个思想应保留。

---

## 24.3 只读访问

ChatGPT 可以读取：

```text
代码
日志
diff
项目状态
```

而不直接拥有本地任意写权限。

这是正确的安全边界。

---

## 24.4 断线重连

现有连接的断线恢复、常驻连接思路可以复用。

---

## 24.5 本地 Runtime Access

未来隧道主要用于访问 Git 无法覆盖的内容，例如：

```text
未 commit 的本地工作区
实时日志
Codex Session / Thread
测试 stdout
本机进程状态
本地临时 Artifact
本机专属环境
无法进入 Git 的敏感配置
```

---

# 25. Codex with ChatGPT 不继续沿用的部分

以下逻辑不再作为主架构：

```text
Codex 主动发起
↓
ChatGPT 规划
↓
Codex 执行
↓
ChatGPT Review
```

原因：

- 控制方向错误；
- Executor 主导流程；
- 不方便多 Executor；
- 不适合 PCP Policy；
- 不适合 WPOS；
- 状态不独立；
- 不适合作为长期 Work Control Plane。

---

# 26. 隧道的重新定位

原 C2C 隧道从：

```text
核心协作链路
```

降级为：

```text
Optional Local Runtime Access Adapter
```

默认架构只要求 Execution Server 能通过选定的 Runtime Binding / Provider
关联并控制实际执行路径。是否使用 Git、provider queue、Local Worker、tunnel
或其他 connectivity pattern，由具体 binding/profile 决定。

只有需要访问实时本地状态时，隧道才可能成为某个 profile 的可选机制。

---

# 27. 为什么不继续围绕隧道设计

因为 PCP 真正要解决的是：

```text
任务是否存在
状态是否存在
权限是否明确
谁执行
执行到哪里
结果是什么
谁验收
失败怎么恢复
```

这些问题与“有没有公网穿透”不是同一个问题。

隧道只是：

```text
Connectivity
```

而不是：

```text
Control Plane
```

---

# 28. Git-only 模式是否可行

Git-only 可以作为 `non-normative bootstrap example` 验证最小闭环，例如用
repository state 传递 READY、Result 与 Review artifacts。

它不改变以下边界：

- Git polling 不是 canonical Scheduler；
- repository lock 不自动等于 current Attempt authority；
- commit/push success 不自动等于 Result accepted 或 Execution DONE；
- Retry、LOST、cancellation 和 stale mutation 仍须由 Execution Server 语义决定。

因此 Git-only 不是 V0.3 规定的生产 runtime/provider，也不授权新的 Git layout
或 binding design。

---

# 29. 为什么仍需要 Runtime Coordination

实际执行仍需要处理：

```text
dispatch / routing
liveness / timeout
cancellation delivery
progress observation
retry / replay
durable runtime continuity
```

这些 volatile mechanics 不适合由 Git 单独承载，但也不要求 PCP 自建一个固定
“轻服务”。正式边界是：

```text
Git
= durable artifacts and history

Execution Server
= canonical semantics, authority and state interpretation

Runtime Binding / Provider
= replaceable coordination mechanics
```

成熟 runtime/provider 应优先复用；只有 PCP-specific semantic remainder 才保留
在 Execution Server。任何 provider 选择与生产适配需要单独授权和验证。

---

# 30. MVP 示例（非规范）

早期最小闭环可以抽象为：

```text
Caller / Work Plane
   ↓
ExecutionRequest
   ↓
Execution Server authorization
   ↓
Runtime Binding / Provider
   ↓
Executor Adapter
   ↓
Concrete Executor
   ↓
durable Result / Evidence
   ↓
Execution Server validation
   ↓
Review / Approval
```

具体使用 Git polling、Local Worker、provider queue、FastAPI、SQLite 或其他
技术都只是候选实现，不属于本 baseline 的 canonical decision。本节不授权
Runtime Binding、Provider Selection、Codex Adapter、ES-05 或部署实现。

---

# 31. MVP 明确不做

第一阶段不做：

```text
自动 git push
自动 merge
自动部署
生产数据库修改
SSH 生产设备
多 Agent 协商
复杂 DAG
自动权限提升
无限自动修订
大规模 Worker 集群
复杂消息队列
Kubernetes
```

---

# 32. MVP 验证目标

第一阶段只需要证明三件事：

## 32.1 远端派工

人在外面：

```text
ChatGPT Web
→ PCP
→ Execution
```

能生成稳定、明确、可执行任务。

---

## 32.2 无人值守执行

经过授权的 runtime participant / Executor path 能：

```text
接收或被分配已授权工作
执行
测试
在 Policy 允许时由新 Attempt 恢复
输出结果
```

而不需要远程桌面操作。自动领取、provider polling、push dispatch 和 recovery
engine 都是可替换 mechanics，不构成 mandatory PCP implementation。

---

## 32.3 独立复核

结果能回到 Web：

```text
Result
+
Diff
+
Tests
+
Evidence
```

由 ChatGPT 或其他 Reviewer 独立验收。

---

# 33. 后续扩展

一旦 Codex Executor 跑通，Execution Server 可以接入：

```text
Diagnostic Executor
Browser Executor
Data Analyzer
Document Executor
CSB Agent
Remote Site Agent
Human Task
```

最终可能出现：

```text
PCP Task
  ↓
Execution Server
  ├── Codex Executor
  ├── Diagnostic Executor
  ├── Browser Executor
  ├── Human
  └── Future Agent
```

---

# 34. 与医院 AI 诊断平台的关系

例如：

```text
检查 82663 异常通话
```

Execution Server 可以分配：

```text
executor_type = diagnostic
```

执行：

```text
CDR
FS Log
TG Log
PCAP
↓
Evidence
↓
Diagnosis
↓
Review
```

而：

```text
修改诊断脚本
```

则：

```text
executor_type = codex
```

因此同一个 PCP Task 可以产生多个不同 Executor 的 Execution。

---

# 35. 与 WPOS 的典型关系

例如：

```text
WPOS
└── 售后 Case：82663 偶发嘟声
```

产生：

```text
EXE-001 分析 CDR
EXE-002 分析 FS
EXE-003 分析 TG
EXE-004 分析 PCAP
EXE-005 修改分析脚本
EXE-006 输出报告
```

Execution Server 负责执行。

WPOS 继续负责业务生命周期。

---

# 36. 当前最终边界

## PCP / Work Plane

负责：

```text
为什么做
做什么
优先级
业务目标
政策
审批
全局状态
事实引用
```

PCP 或其他 Work Plane 持有 Work Item / Work Intent / Workorder 的定义权。
Dispatch 显式选择并冻结一个确定版本，生成 ExecutionRequest；Execution
Instance 只拥有某一次运行事实。Execution Server 不反向定义上层工程意图，
也不允许上游后续修改静默改变已经 Dispatch 的 Execution。

## Execution Server

负责：

```text
Northbound Execution Contract
ExecutionRequest admission / idempotency
Execution / Attempt identity
canonical state and append-only event interpretation
current Attempt authority
Policy / Approval validation
Effective Runtime Grant
stale-writer rejection
LOST and Retry / Recovery authorization
cancellation outcome authority
runtime / provider / executor correlation
Result / Evidence validation and late/orphan handling
Review Flow and terminal decisions
```

Execution Server 是上述 semantics 的权威。它不因为 queue、scheduler、
heartbeat、timeout、retry 或 durable workflow 有用，就必须拥有这些 mechanics
的 concrete implementation。

## Runtime Binding / Provider

可以负责：

```text
queueing / scheduling
dispatch / worker routing
heartbeat / timeout
retry / re-dispatch mechanics
durable workflow mechanics
provider-specific identity / token
runtime observation and control delivery
```

前提是 binding 在实际执行开始前服从 PCP authorization，持久保存 identity
correlation，将 provider event 归一化为 fact，并证明 authority、stale guard、
idempotency、Runtime Grant、cancellation、isolation 和 Result/Evidence
obligations。provider 不直接写 canonical state。

## Executor Adapter / Executor

负责：

```text
把已授权 Invocation Input 转换为 concrete executor invocation
执行具体动作
观察、停止、收集并标准化 executor outcome
```

Adapter / Executor 不拥有 current Attempt authority，不自授权 retry，不扩大
Runtime Grant，不把 executor success 当作 Review acceptance。Executor 保持
可替换；Codex 是具体 Executor，而不是 shared contract 的事实源。

## Git

负责：

```text
长期事实
版本
历史
代码
结果
证据索引
```

## Local Runtime Adapter / C2C Tunnel

负责：

```text
可选实时本地访问
未同步内容
本地运行态
```

它属于 connectivity / binding mechanism，不是 Control Plane 或 mandatory
runtime topology。

---

# 37. 当前固定结论

正式固定以下结论：

1. `Codex with ChatGPT` 不作为 PCP 的主架构。
2. 它最有价值的是本地到云端的轻量连接与只读访问能力。
3. C2C 隧道降级为 optional `Local Runtime Access Adapter`。
4. PCP Execution Server 是通用 execution semantics 与 canonical runtime authority 模块。
5. Codex 是 Execution Server 下可替换的一个 Executor。
6. Git 继续作为长期事实源之一。
7. Execution Server 拥有 Execution / Attempt canonical state interpretation；volatile coordination mechanics 可由可替换 runtime/provider 承担。
8. Worker Pull、server push、provider queue、direct assignment 与 outbound Local Worker 都是 binding/profile 选择，不构成统一 mandatory topology。
9. PCP 掌握 Policy / Approval / Runtime Grant，不允许 Runtime Participant、binding、provider 或 Executor 自行升级权限。
10. 正式 Execution 默认使用 Attempt-scoped isolation 或可证明等效的 containment。
11. native Executor session/thread 可以被引用或恢复，但不得复活旧 PCP Attempt，也不作为 canonical fact source。
12. Review 必须基于 Acceptance + Result + Evidence；executor/provider success 不等于 DONE。
13. 自动 retry/re-dispatch 必须被 gate 在新 PCP Attempt authorization 之后，不能产生隐藏的实际执行路径。
14. current authority 的撤销、过期、LOST、Retry/Recovery authorization 和 cancellation outcome 由 Execution Server 决定。
15. stale、revoked、expired 或 superseded authority 不得修改 canonical state；late content 只能作为 immutable non-canonical evidence。
16. 所有调用方共享 Northbound Execution Contract；具体 Executor 通过各自 Adapter Contract 接入，不把任何单一 Executor 的调用细节提升为通用 Contract。
17. 正式固定 `Work Item → Dispatch → ExecutionRequest → Execution Instance`：Work Item 拥有意图事实；Dispatch 冻结确定版本；ExecutionRequest 是本次 Dispatch 的机器可执行投影；Execution Instance 拥有某一次运行事实。
18. Runtime Binding / Provider 必须保持 PCP identity、authority、state、Result/Evidence/Review 与 Audit 边界，不得成为新的 canonical source。
19. Worker Registry、Scheduler、Claim/Lease、heartbeat、renewal、fencing、retry/recovery engine、Local Worker 和 FastAPI/SQLite 按 §10 分类，不再作为一组 mandatory PCP implementation。
20. 本 baseline 不选择 provider，不定义 Runtime Binding API/schema，不授权 ES-05、Codex Adapter、EO alignment 或 deployment。

---

# 38. 后续工作授权边界

ExecutionRequest、Execution State Machine、Worker Protocol V0.2 与 Executor
Adapter Contract 已分别由 ES-01 至 ES-04 固定。V0.3 alignment 不重新定义这些
Contract，也不授权任何 downstream implementation。

未来进入以下工作前，必须有单独的 governing Task / Workorder、适用的
Architecture Gate 和明确 Scope：

```text
Runtime Binding design / implementation
Provider evaluation or selection
binding API / schema / storage
Codex Adapter / ES-05
EO alignment
production deployment
```

后续 binding 必须对 ES-03 V0.2 的全部适用 `binding requirement` 提供 proof，
并保留本 baseline 的 semantic invariants。若实现无法保留 invariant，应停止并
回到 governance review，不得在 adapter 或 provider integration 中静默修改
canonical semantics。

---

# 39. 一句话定义

> **PCP Execution Server 是 PCP 将已明确的任务、政策和审批转换为受 canonical Execution / Attempt authority 约束的实际执行，并统一验证状态、结果、证据、复核与审计的语义控制模块；queue、scheduler、dispatch、heartbeat、timeout、retry 和 durable workflow 可由可替换 runtime/provider 承担，Codex 只是其中一个可替换 Executor。**
