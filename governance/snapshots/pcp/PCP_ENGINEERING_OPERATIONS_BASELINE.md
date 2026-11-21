# PCP Engineering Operations BASELINE

**文档状态：FIXED / Architecture Baseline**  
**版本：V0.1**  
**固定日期：2026-09-17**  
**所属体系：Personal AI Control Plane（PCP）**  
**文件名：`PCP_Engineering_Operations_BASELINE.md`**

> 本文用于固定 Engineering Operations（EngOps）的定位、边界、核心对象、与 PCP / Execution Server / Project Repo / Business Domain 的关系，以及当前多智能体工程协同模式。
>
> 本文不重定义已经固定的 PCP Execution Server。涉及 Execution Server 的定义，以既有 `PCP_Execution_Server_架构基线_2026-09-16.md` 为上游约束。
>
> 旧聊天仅作为设计过程输入，不作为事实源。本文经用户明确要求生成后，作为新的固定 MD 基线。

---

## 1. 本次收口的目的

此前两个讨论分别从两个方向解决同一问题：

1. **AI JOBs 边界划分**
   - 解决“开发、环境、基础设施、自动化工程工作放在哪里管理”；
   - 最终名称收敛为 **Engineering Operations（EngOps）**；
   - 核心是工程 Job、长期工程状态、中间过程、复核、证据和可复用工程资产。

2. **多智能体协同模式**
   - 解决“ChatGPT / GPT、Codex、Git、Human、Execution Server 如何共同推进多个工程任务”；
   - 核心是 Commander / Control / Runtime / Executor / Review 的职责分离。

两者不是两套系统。

正式关系固定为：

> **Engineering Operations 是工程工作控制域；多智能体协同是 Engineering Operations 的主要运行方式之一；Execution Server 是独立的通用执行运行时。**

---

## 2. 一句话定义

> **Engineering Operations 是 PCP 下游的工程作业控制域，用于管理跨项目的软件开发、环境、基础设施与自动化工程工作的 Job、中间状态、编排意图、复核、证据和可复用工程资产；它不直接承担实时执行运行时，也不保存业务事实或项目正式源码。**

简称：

```text
Engineering Operations
= Engineering Work Control Domain
```

可简称：

```text
EngOps
```

原讨论中的 `AI JOBs` 仅作为早期工作名称，不再作为正式模块名。

---

## 3. 总体架构

```text
                           Human
                             │
                批准 / 否决 / 干预 / 最终决策
                             │
                             ▼
                    ChatGPT / GPT Commander
                 目标理解 / 拆分 / Review / 重规划
                             │
                             ▼
                    ┌──────────────────┐
                    │       PCP        │
                    │ Project / Goal   │
                    │ Policy / State   │
                    │ Approval / Audit │
                    └────────┬─────────┘
                             │
               ┌─────────────┴─────────────┐
               │                           │
               ▼                           ▼
   ┌──────────────────────┐     ┌────────────────────────┐
   │ Engineering          │     │ PCP Execution Server   │
   │ Operations           │     │                        │
   │                      │     │ ExecutionRequest       │
   │ Engineering Job      │     │ Runtime State          │
   │ Engineering State    │     │ Worker / Claim / Lease │
   │ Review / Evidence    │     │ Retry / Recovery       │
   │ Skill References     │     │ Result Package         │
   │ Infra Orchestration  │     │ Executor Adapter       │
   └──────────┬───────────┘     └────────────┬───────────┘
              │                              │
              │ Job → 1:N ExecutionRequest  │
              └──────────────────────────────┘
                                             │
                          ┌──────────────────┼──────────────────┐
                          ▼                  ▼                  ▼
                    Codex Executor        Script/API       Future Executor
                          │
                          ▼
                    Project Workspace
                          │
                          ▼
                    Project Git Repo
```

核心边界：

```text
PCP                  = 为什么做 / 做什么 / Policy / Approval / 全局状态
Engineering Operations = 工程工作如何被组织、追踪、复核和沉淀
Execution Server     = 一个 Execution 如何被机器可靠执行
Executor             = 具体执行动作
Project Repo         = 项目正式代码和项目正式工程资产
Git                  = 已批准工程事实、版本与长期审计
Human                = 最终 Authority
```

---

## 4. Engineering Operations 的职责

Engineering Operations 管理的是**工程工作的生命周期**，而不是业务生命周期，也不是机器进程生命周期。

### 4.1 Engineering Job

Engineering Job 是 EngOps 的核心对象。

它描述：

```text
要解决什么工程问题
目标项目是什么
目标 Repo / Workspace 是什么
允许修改什么
依赖什么上下文
需要哪些能力 / Skill
验收标准是什么
当前工程状态是什么
产生了哪些 Execution
结果和证据在哪里
Review 结论是什么
是否需要返工 / 人工决策
```

一个 Engineering Job 可以跨多次执行存在。

---

### 4.2 Engineering State

EngOps 保存长期有意义的工程状态，例如：

```text
Job 是否已定义
是否满足进入执行的条件
是否正在等待 Execution
是否有阻塞
是否已产生候选结果
是否正在 Review
是否需要返工
是否已经验收结束
```

EngOps 不负责维护毫秒级、秒级或短周期 Runtime State。

---

### 4.3 Engineering Orchestration

EngOps 管理**工程编排意图**，包括：

```text
先做什么
后做什么
哪些 Job 可以并行
哪些 Job 有依赖
哪个项目 / Repo 是目标
需要什么环境
需要什么 Skill
需要什么 Review
是否属于基础设施任务
```

它可以形成多个 ExecutionRequest。

但：

> EngOps 不负责 Worker claim、lease、实时 retry、进程存活和实时调度实现。

这些属于 Execution Server。

---

### 4.4 Review

EngOps 保存 Job 级 Review 结论和复核链。

Review 的输入至少可以包括：

```text
Acceptance Criteria
Diff
Tests
Result Package
Evidence
风险
未完成项
```

Executor 不能自行宣布 Job 为 `DONE`。

Job 的最终完成必须经过外部 Review / Approval。

---

### 4.5 Evidence

EngOps 保存：

```text
Evidence 索引
测试结果引用
Diff 引用
日志引用
截图 / 报告引用
PR / Commit 引用
Execution Result 引用
Review 结论
```

大文件本体不要求进入 EngOps 仓库。

---

### 4.6 可复用工程资产

EngOps 可以沉淀跨项目复用的工程资产，例如：

```text
Job 模板
ExecutionRequest 模板
Review Checklist
测试规范
环境准备规范
基础设施编排模板
工程 Skill 引用
Executor 使用规范
恢复 / 回滚方法
工程 Evidence 规范
```

但必须满足：

> **可复用工程资产属于 EngOps；项目正式实现属于 Project Repo。**

---

## 5. 基础设施编排的正式归属

基础设施相关工程工作属于 Engineering Operations。

例如：

```text
Docker 环境准备
测试环境初始化
服务启动 / 停止方案
开发机环境配置
CI/CD 工程任务
构建环境
VPS / 本地 Worker 准备
工程工具安装
开发依赖更新
自动化脚本编排
```

它们首先表现为 Engineering Job。

但实际执行仍通过：

```text
Engineering Job
      ↓
ExecutionRequest
      ↓
Execution Server
      ↓
Executor
      ↓
Docker / Shell / Script / API / Codex / CI
```

因此：

> **基础设施编排的“工程意图、状态、Review、Evidence”归 EngOps；具体运行时执行归 Execution Server / Executor。**

---

## 6. Engineering Operations 不负责什么

EngOps 明确不是：

```text
业务数据库
WPOS Business Domain
客户 / 商机 / 合同 / 回款系统
业务售后 Case 数据库
项目源码总仓库
项目正式生产配置总仓库
Execution Server
Worker Registry
实时消息总线
实时进程监控系统
Codex Session 存储
模型长期记忆
```

以下内容不得因为“方便”而被复制进 EngOps：

```text
整个项目源码
项目完整业务资料
客户业务事实
Business Domain 正式实例数据
生产数据库
大量 PCAP / Log / Artifact 本体
其他 Repo 的长期镜像副本
```

---

## 7. 与 Business Domain / WPOS 的边界

Business Domain 管：

```text
客户
商机
报价
合同
项目
交付
售后
业务工单
回款
业务事实
```

Engineering Operations 管：

```text
为了完成这些业务目标而产生的工程工作
```

例如：

```text
WPOS 售后 Case
“82663 偶发嘟声”
```

这是业务对象。

它可能产生：

```text
ENG-JOB-001  改进日志分析脚本
ENG-JOB-002  增加 DTMF 回归测试工具
ENG-JOB-003  建立诊断环境自动初始化
```

这些才属于 Engineering Operations。

原则：

```text
Business Case != Engineering Job
Engineering Job != ExecutionRequest
```

---

## 8. 与 Project Repo 的边界

每个正式项目继续拥有自己的 Git Repo / Workspace。

例如：

```text
project-a/
project-b/
pcp-csb/
hospital-billing/
voice-business/
```

Project Repo 保存：

```text
正式源码
正式配置
项目 Tests
Migration
Release
项目级文档
项目 Commit / PR
```

Engineering Operations 不复制项目源码。

EngOps 只保存：

```text
Job
目标 Repo 引用
目标 Branch / Worktree 引用
Execution 引用
Review
Evidence 索引
可复用工程资产
跨项目工程状态
```

正式关系：

```text
Engineering Job
      │
      ├── target_repo
      ├── target_project
      └── target_workspace / branch / worktree
                    │
                    ▼
                Project Repo
```

---

## 9. Engineering Job 与 ExecutionRequest 的关系

正式固定：

```text
Engineering Job 1 : N ExecutionRequest
```

Job 是长期工程工作对象。

ExecutionRequest 是一次机器可执行合同。

例如：

```text
ENG-JOB-017
“给 KF 增加 RAG 回归测试”
```

可能产生：

```text
EXE-001  调研现有测试结构
EXE-002  编写测试
EXE-003  修复第一轮失败
EXE-004  执行完整回归
EXE-005  根据 Review 修改
```

Job 不因为一次 Execution 失败而消失。

Execution 不因为 Job 仍存在而无限保持运行状态。

---

## 10. Job 与 Execution 的状态边界

不建立两套互相重复的实时状态机。

### Engineering Operations 关心

```text
Job 是否可执行
Job 是否存在阻塞
Job 是否已有候选结果
Job 是否等待 Review
Job 是否需要返工
Job 是否已经验收
```

### Execution Server 关心

沿用既有 Execution Server 基线：

```text
DRAFT
READY
QUEUED
RUNNING
REVIEW_READY
REVISION_REQUESTED
NEEDS_INPUT
BLOCKED
FAILED
CANCELLED
RECOVERABLE
DONE
```

其中：

```text
claim
lease
renew
heartbeat
timeout
retry
recovery
cancel
```

属于 Runtime。

### 关于 heartbeat 的边界解释

多智能体协同不要求 Agent 持续发送“业务进度同步”。

但 Execution Runtime 可以保留：

```text
lease
deadline
timeout
必要 heartbeat
```

用于：

```text
判断 Worker / Executor 是否存活
续租
检测卡死
故障恢复
```

因此：

> **“不要求持续同步”不等于“Execution Server 禁止 heartbeat”。Heartbeat 是 Runtime 生存性机制，不是业务协同协议。**

---

## 11. ChatGPT / GPT Commander 的职责

ChatGPT / GPT 在这一模式中作为 Commander / Planner / Reviewer。

负责：

```text
理解目标
拆分 Engineering Job
发现依赖
调整优先级
准备执行上下文
生成 / 检查 ExecutionRequest
分析 Result / Evidence
执行独立 Review
要求返工
重新规划
向 Human 汇报工程状态
```

不直接承担：

```text
本地代码修改
长期 Runtime State
Worker claim
具体 Shell 执行
自行越权部署
自行判定最终批准
```

---

## 12. Human 的职责

Human 是最终 Authority。

Human 负责：

```text
批准架构
批准高风险动作
处理需要业务判断的断点
接受 / 否决关键 Review
决定是否部署
决定是否进入生产环境
处理超出自动修订范围的问题
```

目标不是让 Human 盯住每个 Codex Session。

目标是：

> **Human 在工作台查看状态、结果、风险和断点，只在需要决策的位置介入。**

---

## 13. Codex 的定位

Codex 固定为 Executor 之一。

```text
Executor = codex
```

它负责：

```text
进入指定 Workspace
读取任务上下文
修改代码 / 配置
运行测试
生成 Diff
生成 Result Package
输出风险和 blocker
```

它不负责：

```text
决定 Job 是否应该存在
决定 Job 优先级
自行改变 Scope
自行升级权限
自行决定部署
自行宣布最终验收通过
成为长期事实源
```

---

## 14. Codex CLI 与 Desktop

本基线**不固定**：

```text
Codex CLI
vs
Codex Desktop
vs
SDK / app-server
```

作为唯一执行接入形式。

原因：

```text
此前尚未形成正式确认
Execution Contract 应独立于某个 Codex 客户端
Codex 只是 Executor
```

因此当前只固定接口原则：

```text
Execution Server / Worker
        ↓
Codex Executor Adapter
        ↓
具体 Codex 运行形态
```

具体选择留到 Executor Adapter 实施阶段确认。

---

## 15. Skill 的定位

Skill 属于可复用 Capability / Engineering Asset。

Skill 描述：

```text
怎么做
采用什么流程
使用什么工具
输出什么格式
检查什么风险
如何形成 Evidence
```

Skill 可以帮助 Job / Executor 按规范更新状态。

但：

> **Skill 不是 Engineering State 的事实源。**

权威状态仍属于：

```text
Engineering Job
+
Execution Runtime
```

因此不采用：

```text
Skill 文件自己持有唯一任务状态
```

而采用：

```text
Job 引用 Skill
Execution 使用 Skill
State 独立保存
```

---

## 16. Model 的边界

模型属于执行策略的一部分，但此前尚未固定完整的逐 Job 模型路由规范。

本基线只固定：

1. Model 不成为 Job / State / Skill 的事实源；
2. Model 可替换；
3. 实际执行所使用的模型必须可审计；
4. 模型选择不能破坏 Execution Contract。

尚未固定：

```text
是否每个 Engineering Job 必须显式指定具体模型
是保存 default_model 还是 model_profile
是否由 Router 自动决策
Planner / Executor / Reviewer 是否必须不同模型
```

这些进入后续 `Model Policy / Execution Policy` 专项定义。

---

## 17. 多智能体协同的正式模式

目标模式：

```text
                 Human
                   │
                   ▼
          GPT / ChatGPT Commander
                   │
          ┌────────┴────────┐
          │                 │
      ENG-JOB-A         ENG-JOB-B
          │                 │
          ▼                 ▼
       EXE-A1             EXE-B1
          │                 │
     Worker / Codex     Worker / Codex
          │                 │
          ▼                 ▼
      Project A Repo     Project B Repo
          │                 │
          └────────┬────────┘
                   ▼
             Result / Evidence
                   │
                   ▼
              GPT Review
                   │
          ┌────────┼────────┐
          ▼        ▼        ▼
       APPROVE   REVISE   NEEDS_INPUT
                   │
                   ▼
                 Human
             必要节点介入
```

多 Agent 的意义不是让 Agent 彼此自由讨论。

第一阶段重点是：

```text
多个独立 Engineering Job
多个独立 Execution
多个隔离 Workspace / Worktree
统一状态
统一结果
统一 Review
统一工作台汇报
```

---

## 18. Git 的正式定位

继续继承 PCP / Execution Server 既有原则：

```text
Git = Durable Engineering State / Versioned Source of Truth
```

Git 保存：

```text
Approved Baseline
ADR
Engineering Job 定义
ExecutionRequest 快照
Review
Evidence 索引
工程规范
Skill
模板
最终结果
历史版本
```

Git 不承担：

```text
Worker 在线状态
实时 heartbeat
实时 claim / lease
进程状态
实时 retry
实时 cancel
短周期 Runtime State
```

---

## 19. Engineering Operations 与 Execution Server 的关系

两者都是 PCP 下游能力，但职责不同。

```text
PCP
 ├── Engineering Operations
 └── Execution Server
```

不是：

```text
Engineering Operations
└── Execution Server 的子模块
```

也不是：

```text
Execution Server
└── Engineering Operations 的子模块
```

它们通过契约连接：

```text
Engineering Job
      ↓
ExecutionRequest
      ↓
Execution Server
      ↓
Result / Evidence
      ↓
Engineering Job Review / State Update
```

---

## 20. “Execution Server 前期试用实例”的最终解释

此前“Engineering Operations 是 Execution Server 前期试用实例”的说法容易造成模块边界混乱。

正式修正为：

> **Engineering Operations 不是 Execution Server 的实例；Engineering Operations 是 Execution Server 的第一个真实工程业务域和验证场。**

也就是说：

第一阶段可以先用：

```text
GPT
+
Git
+
Engineering Job
+
Codex
+
人工 Review
```

验证：

```text
Job Schema
状态边界
Execution Contract
Evidence
Review
Skill 引用
失败处理
多任务协作
```

成熟后，把通用运行机制交给 Execution Server：

```text
Worker
claim / lease
runtime state
cancel
retry
recovery
Result Package
Executor Adapter
```

Engineering Operations 继续存在，不被 Execution Server 吞并。

---

## 21. 第一阶段 V0.1：Git-first 验证

V0.1 不要求先把完整 Execution Server 做完。

先验证：

```text
ChatGPT / GPT
      ↓
Engineering Job
      ↓
Git
      ↓
人工或轻量触发
      ↓
Codex Executor
      ↓
Project Repo / Worktree
      ↓
Tests / Diff / Result / Evidence
      ↓
GPT Review
      ↓
APPROVE / REVISE / NEEDS_INPUT
```

目的：

1. 验证工程 Job 是否足够稳定；
2. 验证多个项目是否可以统一管理；
3. 验证中间状态是否可以跨对话 / 跨 Agent 恢复；
4. 验证 Codex 是否能稳定按 Job 工作；
5. 验证 Review / Evidence 是否足以让 Human 不盯 Session；
6. 为 Execution Server 提供真实接口需求。

---

## 22. V0.1 明确不做

继承 Execution Server MVP 边界，并针对 EngOps 补充：

```text
不自动部署生产
不自动修改生产数据库
不自动 SSH 生产设备
不自动 merge
不允许 Executor 自动升级权限
不做无限 Revision Loop
不做复杂 DAG
不做 Agent 自由协商网络
不做大规模 Worker 集群
不先建设 Kubernetes
不把所有项目源码集中复制到 EngOps
不把业务事实迁移到 EngOps
不让 Codex Session 成为状态事实源
不让 Skill 文件成为状态事实源
```

---

## 23. 已处理的重复与冲突

### 23.1 AI JOBs vs Engineering Operations

结果：

```text
正式名称 = Engineering Operations
AI JOBs = 废弃的早期名称
```

原因：

`AI JOBs` 容易被理解成“AI 的任务列表”，无法覆盖：

```text
开发
环境
基础设施
工程编排
Review
Evidence
跨项目工程资产
```

---

### 23.2 Engineering Operations vs Execution Server

结果：

```text
EngOps = 工程工作控制
Execution Server = 执行运行时
```

一个 Job 可以产生多个 Execution。

---

### 23.3 Job State vs Runtime State

结果：

```text
EngOps 保存长期工程状态
Execution Server 保存实时执行状态
```

不重复建设两套 claim / running / heartbeat 状态系统。

---

### 23.4 “不需要心跳” vs Execution Server heartbeat

结果：

```text
不需要 Agent 持续业务同步
≠
Runtime 不允许 heartbeat
```

heartbeat 仅用于运行时存活、lease 和恢复。

---

### 23.5 Skill 管状态

结果：

```text
Skill 可定义状态更新方法
但 Skill 不持有权威状态
```

---

### 23.6 Project Repo vs Engineering Operations Repo

结果：

```text
Project Repo = 项目正式实现
EngOps Repo  = 跨项目工程 Job / Review / Evidence / 工程资产
```

不复制源码。

---

## 24. 当前仍未固定的事项

以下事项本次不擅自定案：

1. **Codex Executor 的具体接入方式**
   - CLI
   - Desktop
   - SDK
   - app-server
   - 其他 Adapter

2. **Model Policy 的详细 Schema**
   - Job 是否必须指定具体模型；
   - model_profile；
   - Planner / Executor / Reviewer 模型策略；
   - Router 自动选择规则。

3. **Engineering Job 的最终 YAML / JSON Schema**
   - 本文固定概念与边界；
   - 字段定义进入下一步实施规范。

4. **Engineering Operations 独立 Git Repo 的最终仓库名**
   - 模块名已固定为 `Engineering Operations`；
   - 仓库命名在创建仓库时单独确认。

---

## 25. 推荐的最小 Engineering Job 信息

本节仅固定必需信息类别，不固定最终字段格式：

```text
Job ID
Title / Objective
Source / Parent Task
Target Project
Target Repo
Scope
Context References
Acceptance Criteria
Constraints
Risk
Required Capability / Skill References
Execution References
Current Engineering State
Blockers
Evidence References
Review Result
Final Result Reference
```

模型字段留待 Model Policy 固定后加入正式 Schema。

---

## 26. 下一步实施顺序

本基线固定后，不再重复讨论模块顶层边界。

下一步直接进入：

```text
1. 建立 Engineering Operations Git Domain / Repo
2. 定义 Engineering Job Schema
3. 定义目录结构
4. 定义 Job State / Event 的持久化格式
5. 定义 Skill 引用规则
6. 定义 Engineering Job → ExecutionRequest 映射
7. 定义 Codex Executor Adapter 首版
8. 选择一个真实工程 Job 做端到端验证
9. 根据验证结果反推 Execution Server MVP
```

---

## 27. 最终固定结论

正式固定：

1. `AI JOBs` 正式收敛为 **Engineering Operations（EngOps）**。
2. EngOps 是 PCP 下游的**工程作业控制域**。
3. EngOps 管开发、环境、基础设施和自动化工程工作的 Job、中间状态、Review、Evidence 和可复用工程资产。
4. EngOps 不管理业务事实。
5. EngOps 不保存各项目正式源码副本。
6. Project Repo 继续管理项目正式实现。
7. Engineering Job 与 ExecutionRequest 分离，关系为 **1:N**。
8. EngOps 与 Execution Server 是职责平级的 PCP 下游模块，通过 Execution Contract 连接。
9. EngOps 不是 Execution Server 的实例，而是其第一个真实工程业务域 / 验证场。
10. Execution Server 的既有基线继续有效，不因本次合并被重新定义。
11. ChatGPT / GPT 负责 Commander / Planner / Reviewer。
12. Codex 是 Executor，不是流程控制者。
13. Human 是最终 Authority。
14. Skill 是 Capability / 工程方法资产，不是状态事实源。
15. Job State 与 Runtime State 分离。
16. 不要求 Agent 持续业务心跳；Execution Runtime 可保留 lease / timeout / 必要 heartbeat。
17. Git 保存长期工程事实与版本，轻 Runtime 保存实时执行状态。
18. 第一阶段采用 Git-first + GPT + Codex + Review 跑真实闭环，不先建设复杂平台。
19. Codex CLI / Desktop 的具体选择本次不固定。
20. 逐 Job 的 Model Policy 详细规则本次不固定。
21. 本文固定后，下一步进入 Engineering Operations Repo、Job Schema 和真实 Job 验证，不再重新讨论顶层边界。

---

## 28. 一句话最终版本

> **PCP Engineering Operations 是 PCP 中负责跨项目工程工作的长期控制域：它把开发、环境、基础设施和自动化需求固化为可追踪、可复核、可审计的 Engineering Job，并通过 ExecutionRequest 调用独立的 Execution Server 和可替换 Executor 执行；项目代码仍归各自 Project Repo，业务事实仍归业务域，Human 保持最终决策权。**
