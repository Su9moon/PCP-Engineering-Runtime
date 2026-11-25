# WO-20261126-002 — PCP Engineering Control Center V1.2
# 对话式工程规划、任务编排与执行闭环

## Identity

~~~yaml
repository: Su9moon/PCP-Engineering-Runtime
workorder_id: WO-20261126-002
title: PCP Engineering Control Center V1.2 — Conversational Planning & Execution Orchestration
executor: Codex CLI on cbnet
source_issue: null
priority: P1
status: READY_FOR_EXECUTION
product_version: V1.2
execution_host: cbnet
environment: WSL2 Ubuntu 24.04
runtime_owner: Ruflo Supervisor
execution_engine: Existing Autoloop Hub
worker_executor: Existing Codex CLI Workers
delivery_surface: Existing PCP Engineering Control Center Dashboard
~~~

## 1. 目标与交付定义

在已经部署的 PCP Engineering Control Center V1.1 上继续开发 V1.2。把 V1.1 的自然语言需求收集、需求档案、工程文档和跨会话保存，延伸为真实可用的工程规划与执行闭环：

**需求对话 → 需求确认 → Ruflo 工程规划 → 任务拆分与依赖 → 人工编排 → 正式任务确认 → 真实派发 → 执行监督 → 独立 Review / QA → 返工 → 交付证据与最终结果。**

最终用户不需要手工编写工程工单、拆分 Worker 任务、查看终端日志或自行追踪每个 Run。用户通过现有 Dashboard 完成需求表达、方案调整、授权和结果查看；Ruflo 负责工程规划和执行组织；Autoloop 负责现有 Hub / Event / Run / Worker 生命周期；Codex Worker 负责实际执行。

这是现有 Dashboard 的连续升级，不是重建项目，不是另建 Ruflo 管理台，也不是新增一套任务或调度系统。

### 1.1 本版本必须实现

1. V1.1 需求档案能够直接进入 Ruflo Supervisor 的工程规划流程。
2. Ruflo 能给出可检查、可编辑的实施计划和任务依赖关系。
3. 用户可以接受建议、修改建议或完全手动编排。
4. 用户明确确认后，才能创建/使用正式工程任务并启动获准的执行。
5. 复用现有 Ruflo → Autoloop → Codex Worker 执行链。
6. Dashboard 能显示真实任务、Agent、Worker、Event、Run、提交、测试、Review 和交付证据。
7. 支持执行中查看、重新规划、调整剩余任务、接管和返工；仅开放现有运行接口真正支持的操作。
8. 交付结果回到原任务和文档上下文，形成可追溯的闭环。

### 1.2 不属于本版本的连接方式

- 不把当前 ChatGPT 网页会话直接连接到 cbnet 本地 Ruflo。
- 不新建 MCP Server、MCP Gateway、Tunnel、ChatGPT Connector、远程控制端点或浏览器到本地 stdio 的桥接。
- 不改变已确定的本机执行拓扑。
- 本版本使用 Dashboard / cbnet 现有本地执行入口和已经配置的 Ruflo MCP；GPT 网页仍不拥有 Ruflo 的本地执行权限。
- 不通过 CB Bridge / Tunnel Client 派发本工单。

本版本的“对话到执行”是现有 Dashboard 对话与本机 Ruflo 执行链的衔接，不等于新建 ChatGPT 网页到 Ruflo 的远程控制通道。

## 2. 权威基线与输入

### 2.1 PCP 主仓

Canonical repository: Su9moon/personal-ai-control-plane  
Canonical commit: 22bae955686f03c5f440cdcd66e13a69f1289f90

执行前读取以下精确文件：

- Su9moon/personal-ai-control-plane@22bae955686f03c5f440cdcd66e13a69f1289f90:AGENTS.md
- Su9moon/personal-ai-control-plane@22bae955686f03c5f440cdcd66e13a69f1289f90:governance/PCP_ENGINEERING_AGILITY_PRINCIPLE.md
- Su9moon/personal-ai-control-plane@22bae955686f03c5f440cdcd66e13a69f1289f90:.agents/skills/pcp-session-bootstrap/SKILL.md
- Su9moon/personal-ai-control-plane@22bae955686f03c5f440cdcd66e13a69f1289f90:.agents/skills/pcp-experience-reuse/SKILL.md
- Su9moon/personal-ai-control-plane@22bae955686f03c5f440cdcd66e13a69f1289f90:.agents/skills/pcp-workorder-handoff/SKILL.md
- Su9moon/personal-ai-control-plane@22bae955686f03c5f440cdcd66e13a69f1289f90:processes/experience-reuse-gate.md
- Su9moon/personal-ai-control-plane@22bae955686f03c5f440cdcd66e13a69f1289f90:processes/architecture-governance-gate.md
- Su9moon/personal-ai-control-plane@22bae955686f03c5f440cdcd66e13a69f1289f90:governance/adr/ADR-2026-11-22-001_pcp-engineering-runtime.md
- Su9moon/personal-ai-control-plane@22bae955686f03c5f440cdcd66e13a69f1289f90:governance/PCP_EXECUTION_PROFILE_RESOLUTION_BASELINE.md
- Su9moon/personal-ai-control-plane@22bae955686f03c5f440cdcd66e13a69f1289f90:governance/PCP_EXECUTION_ENVIRONMENT_RESOLUTION_BASELINE.md
- Su9moon/personal-ai-control-plane@22bae955686f03c5f440cdcd66e13a69f1289f90:governance/baselines/PCP_WEBGPT_ROLE_ORGANIZATION_V0.2_FIXED.md

### 2.2 Runtime 仓库与 V1.1 输入

Repository: Su9moon/PCP-Engineering-Runtime

读取当前本地工作区中的：

- AGENTS.md
- README.md
- PROJECT_STATUS.md
- docs/architecture/POC_TARGET_ARCHITECTURE.md
- docs/integration/DEPENDENCY_MAP.md
- docs/engineering/EXPERIENCE_REUSE.md
- 当前 Dashboard 的真实代码、路由、后端适配器、测试和部署配置
- 当前实际存在的 V1 / V1.1 工单与报告

V1.1 设计输入位于远端交接分支 handoff/dashboard-v1-demo-20261125，分支当时对应 HEAD 为 b05d96d2e74b90ff77844aff2b4fe157b6e1f651。使用 Git 只读查看以下文件，不要为了读取设计文件切换、合并或覆盖用户当前本地分支：

- design/pcp-engineering-control-center-conversational-intake-demo.html
- docs/product/CONVERSATIONAL_ENGINEERING_INTAKE_V1.1.md
- workorders/WO-20261126-001-PCP-ENGINEERING-CONTROL-CENTER-CONVERSATIONAL-INTAKE-V1.1.md

V1.1 的设计、工单和已部署实现不是同一个事实。以 cbnet 本地实际代码、运行状态和用户已部署版本为实施基线；远端 main 不得替代本地实现。

### 2.3 已有自适应编排需求与 POC 证据

复用此前的 Ruflo 自适应编排设计 WO-20261124-003-RUFLO-ADAPTIVE-ORCHESTRATION：

- C0–C3 复杂度建议；
- Suggestion / Manual / Autonomous 三种编排模式；
- 人工可覆盖 Agent、Worker、并行策略、测试、Review / QA 等受支持配置；
- Ruflo 动态重新规划；
- 运行中人工介入；
- Ruflo → Autoloop → Codex 的现有执行路径；
- 真实模型、Event、Run、Worker、测试和 Review 证据。

该历史工单的相关产品需求已合并进本 V1.2 交付目标。不要将它作为平行工单再次独立派发，不要重复建设相同功能；如果本地已有实现或证据，直接复用并补齐差距。不得修改、取消或删除历史工单及其原始证据。

此前首轮 Ruflo / Autoloop POC 已有真实运行记录。用户报告包括 20 次 Supervisor 调用、20 个 Autoloop Run、T1/T2/T3 独立验收及返工验证，模型记录为 gpt-6.2-sol / high。执行者必须从本地原始报告、工单和 Git 记录核对实际 SHA、Event / Run ID 与证据路径。不得重跑首轮 POC，不得把用户报告的摘要冒充原始运行证据。

## 3. 架构 Gate 与经验复用

~~~yaml
architecture_gate:
  required: true
  status: complete
  real_use_evidence: verified
  decision: INTEGRATE
  governing_decision: "Su9moon/personal-ai-control-plane@22bae955686f03c5f440cdcd66e13a69f1289f90:governance/adr/ADR-2026-11-22-001_pcp-engineering-runtime.md"
  pcp_specific_remainder: "把 V1.1 的需求档案与文档交付接入现有 Ruflo 工程规划、人工编排、Autoloop 执行监督及交付证据展示。"
  minimum_formalization: "在现有 Dashboard 与本地 Runtime Adapter 中扩展；复用 Ruflo、Autoloop、EO/ES 现有接口和已验证 POC；不新建 Gateway、Scheduler、Worker Pool、队列、消息总线、任务数据库或 Agent Runtime。"
~~~

Architecture Gate 已由 PCP ADR 批准。本工单是该已批准架构内的项目级实现，不重复跨域扫描，不创建新的 Architecture Gate，不新增 PCP Core 抽象。

Experience reuse classification: REUSE / EXTEND  
Implementation scope: PROJECT_LOCAL

复用：
- PCP Engineering Runtime ADR 和当前 AGENTS 边界；
- V1.1 对话、需求档案、项目经验来源、文档版本及跨会话保存；
- 已部署 Dashboard 的七个主导航区及现有服务；
- Ruflo Supervisor、Agent、Tool Calling 与已验证的编排能力；
- Autoloop 现有 Hub、Event、Run、Worker 和结果回收；
- 现有 EO / ES 权威记录和授权边界（以实际已接通的接口为准）；
- 已完成的 Ruflo / Autoloop POC 和测试证据；
- PCP 五角色 FIXED 基线。

不得把 Candidate / Inbox 经验升级成正式要求；不得创建新的 Skill、Gate、数据库、RAG、向量库、调度器、Worker Pool 或通用编排框架。

## 4. 固定架构与职责边界

本版本保持现有执行拓扑：

~~~text
用户
  ↓
PCP Engineering Control Center V1.1 / V1.2
  ├─ 对话、需求档案、工程文档
  ├─ 计划展示、人工编排、确认和监督
  └─ 现有本地 Runtime Adapter
          ↓
     cbnet 本地 Codex / 已配置的 Ruflo MCP
          ↓
     Ruflo Supervisor
       ├─ 需求理解与工程规划
       ├─ 任务拆分与依赖安排
       ├─ Agent 组织与派发决策
       ├─ 执行监督、Review、QA、返工
       └─ 最终工程结果
          ↓
     现有 Autoloop Hub
       ├─ Event / Run
       ├─ Worker 生命周期
       └─ 执行结果回收
          ↓
     现有 Codex CLI Workers
       ├─ 隔离工作区中的代码修改
       ├─ 测试与证据
       └─ Commit / Patch / 交付文件
          ↓
     Ruflo Review / QA / 返工 / 验收
          ↓
     Dashboard 任务详情与交付证据
~~~

职责：

| 组件 | 本版本职责 | 不得承担 |
|---|---|---|
| Dashboard | 对话入口、需求档案、计划编辑、人工授权、状态与证据展示 | 第二套 Scheduler 或任务事实源 |
| 本地 Codex | 接收本工单、执行本地 Bootstrap、调用现有 Ruflo MCP | 代替 Ruflo 规划、调度、Review 和最终验收 |
| Ruflo Supervisor | 任务理解、复杂度建议、计划拆分、Agent 组织、派发、监督、Review、QA、返工和最终工程验收 | 越权扩大用户授权、伪造 Worker 或运行事实 |
| Autoloop | 现有 Hub / Event / Run / Worker 生命周期及结果回收 | PCP 的用户授权、正式验收或第二套任务账本 |
| Codex Worker | 按授权范围执行具体工程任务、测试和提交证据 | 工程总控或最终验收权威 |
| EO / ES | 继续保持各自已经接通的正式任务、执行授权和状态权威 | 被 Dashboard 或 Ruflo 的本地状态替代 |

若现有 Runtime 已通过 EO / ES 接通正式任务或执行授权，必须继续使用并保留其权威边界。不得绕过已经生效的授权，不得仅凭 EO / ES Schema 存在就声称接口已经接通。不得为了本工单修改 EO / ES Schema 或重建其状态机。实际接口不支持的动作必须明确显示为 unavailable / not exposed，并说明具体原因。

## 5. V1.1 连续性与产品边界

### 5.1 必须保留的 V1.1 能力

- 自然语言对话入口；
- 一次只问一个最有价值的澄清问题；
- 可编辑需求档案；
- USER_CONFIRMED / AI_SUGGESTED / AI_INFERRED / UNRESOLVED 来源状态；
- 选定项目的基线和 PCP 经验检索及精确来源引用；
- 对话、档案、来源、未解决问题和文档版本的持久保存；
- 跨浏览器会话、页面刷新和 Dashboard 服务重启后恢复；
- 版本化工程文档预览、修订、导出；
- 用户确认前不创建正式 EO Job / Workorder；
- 不在需求对话阶段自动创建执行或派发 Worker。

### 5.2 V1.2 入口与工作流

V1.2 在原有需求对话工作区增加工程规划与执行阶段，不新增第二个 Dashboard 或独立 Ruflo 管理台。

用户确认需求文档后，提供“生成工程计划”入口。Ruflo 根据确认后的需求档案和项目基线生成计划。用户可以回到对话修订需求，也可以直接编辑计划。只有确认最终计划和执行授权后才进入派发。

七个既有主导航区继续保留。相关能力融入现有 Engineering Tasks、Task Detail、Agent Team、Runs / Events、Worker Nodes、Delivery Review 和 Connections / Configuration 页面，不为同一能力新建重复页面。

## 6. Ruflo 工程规划与任务拆分

### 6.1 规划输入

Ruflo Supervisor 应收到：
- 已确认的需求档案；
- 用户批准的范围和排除项；
- 项目仓库、当前基线、有效工单和必要的历史决策；
- 已检索经验的精确来源与成熟度；
- 交付物和验收标准；
- 已知环境、依赖和实际运行能力。

不得只把一段聊天摘要作为唯一规划输入；必须保留正式需求档案和精确来源。

### 6.2 规划输出

Ruflo 生成可检查的计划，至少包含适用字段：

- 总体目标和技术方案；
- 任务清单及每项任务的目标；
- 任务之间的依赖关系和可并行关系；
- 每项任务的输入、输出和验收条件；
- 涉及的仓库、路径、模块和工作区范围；
- 建议 Agent / Worker 职责与数量；
- 串行或并行建议；
- 测试、独立 Review 和 Product QA 方案；
- 预计风险、未决问题和关键假设；
- 复杂度建议、模型建议和实际可用能力；
- 交付证据要求。

拆分应以实际依赖、并行价值、责任边界和验收需要为依据。简单连续工作可以保留为一个任务，不得为了展示多 Agent 而机械拆分。

### 6.3 复杂度与风险

复杂度使用 C0 / C1 / C2 / C3，作为建议标签：

| 等级 | 典型任务 | 默认建议 |
|---|---|---|
| C0 | 问答、只读检查、有限分析 | Ruflo 直接处理，通常不需要 Worker |
| C1 | 目标明确、范围有限的工程修改 | 一个合适的 Agent / Worker，定向测试 |
| C2 | 多步骤、跨模块或有明显依赖的工程任务 | 必要时多个 Agent / Worker，显式依赖、Review 和 QA |
| C3 | 范围广、需求不确定或多阶段工程任务 | 深度规划、分阶段交付，按需要并行及独立 Review / QA |

C0–C3 仅为建议，不是权限等级、固定执行通道或功能开关。不得因为复杂度标签限制人工配置。

必须分别表达：
- complexity_band：工程复杂度；
- risk_profile：数据敏感性、生产影响、安全影响、可逆性及外部副作用；
- authorization_scope：用户实际授予的执行权限。

不得由复杂度推导风险或授权。低复杂度任务可以高风险；高复杂度任务可以低风险。

## 7. 三种编排模式与人工控制

默认模式为 suggestion。模式按任务选择，不设置全局强制模式。

### 7.1 Suggestion — AI 建议模式

Ruflo 提出复杂度、任务拆分、依赖、Agent / Worker、并行策略、测试、Review 和 QA 建议。用户可以接受、编辑任意受支持配置或完全替换计划。最终执行使用用户确认后的配置，而不是未经确认的原始建议。

### 7.2 Manual — 人工编排模式

用户直接配置任务拆分、依赖、Agent / Worker、并行策略、模型、测试和 Review。Ruflo 可以分析冲突和提出建议，但不得静默覆盖人工配置。

### 7.3 Autonomous — 授权范围内自主编排模式

用户先明确任务范围和允许的操作边界。在该范围内，Ruflo 可以：
- 组织 Agent 和 Worker；
- 调整剩余任务顺序和并行度；
- 根据真实执行证据重新规划；
- 发起 Review、QA 和范围内返工；
- 调整受支持的资源配置；
- 给出最终工程验收结论。

任何超出已授权范围、涉及受保护操作或扩大目标范围的行为，必须暂停该项并请求用户授权。不得把 Autonomous 解释为无限制 Shell、生产或外部操作权限。

### 7.4 人工可编辑配置

在实际接口支持的范围内，任务创建和详情应支持查看/修改：

- 编排模式；
- 复杂度建议及人工覆盖；
- 任务拆分和依赖顺序；
- Agent 角色、职责和数量；
- 可用 Worker 选择和数量；
- 串行 / 并行策略；
- Worktree / 分支隔离；
- 测试范围和深度；
- 独立 Reviewer 与 QA 参与；
- 返工策略和实际支持的重试参数；
- 超时、资源或 Token 预算（仅限 Runtime 实际暴露的字段）；
- 模型与 reasoning effort；
- 仓库、路径和工具访问范围；
- 允许操作及人工授权边界。

不支持的配置要显示真实原因，不能用本地假状态制造“已生效”的假象。

### 7.5 覆盖与变更记录

每次被接受的人工覆盖或重大计划变化，记录：
- 关联任务 / Workorder；
- 操作者；
- 时间；
- 修改前的值；
- 修改后的值；
- 原因（如有）；
- 立即生效还是下一次 Run 生效。

使用现有 Workorder、文档版本或与其关联的计划产物保存。不得新建独立的编排状态数据库。

## 8. 正式任务、用户确认与派发

### 8.1 确认顺序

1. 用户确认需求档案和工程文档。
2. Ruflo 生成工程计划。
3. 用户审阅并编辑任务、依赖、执行配置和验收要求。
4. 用户明确确认最终计划。
5. 使用现有授权的 EO Job / Workorder 接口创建或更新正式工程任务。
6. 用户明确确认本次执行范围和允许操作。
7. 通过现有 Ruflo / Autoloop 执行接口派发。
8. 保存真实 Event / Run / Worker / 结果引用。

确认工程计划不等于授权生产操作。创建 EO Workorder 不自动等于创建执行或授权 Worker。

### 8.2 派发要求

- 复用已经存在的 Ruflo Supervisor 和 Autoloop Hub / Worker 接口。
- 不重建 Ruflo → Autoloop Connector，不重复首轮三任务 POC。
- 不通过 CB Bridge / Tunnel Client。
- 不增加新的 MCP Server、Gateway、Tunnel、远程控制端点或 ChatGPT Connector。
- 不从浏览器代码直接访问本地 stdio；凭据和 Runtime 连接保持在本机后端。
- 每个实际 Worker 写入任务使用独立隔离工作区；并行 Worker 不得共用可写 Worktree。
- 派发必须使用用户最终确认的配置；不得以最初 AI 建议替代人工覆盖。
- 任何实际不支持的派发参数不得伪称已经应用。
- 不得把 Autoloop provider 内部重试冒充为新的 PCP 执行授权；如现有 ES 执行授权链已启用，必须继续遵守 ES 的 Attempt / Invocation 权威。

### 8.3 生产与外部操作边界

本工单只授权开发环境和受控非生产测试任务。不得自动合并、发布或部署生产；不得使用生产凭据、客户数据或执行不可逆外部操作。

## 9. 执行监督与动态重新规划

任务详情页必须展示真实的：
- 总计划和当前计划版本；
- 子任务状态、依赖和执行顺序；
- Ruflo Agent / Supervisor 实际身份与活动；
- Worker 身份、主机和执行器（Runtime 暴露时）；
- Autoloop Event / Run ID、状态、开始/结束时间；
- 真实日志、结果、Commit、Diff、测试和证据引用；
- 最后观察时间及数据新鲜度；
- 当前阻断、失败原因和未完成事项。

不得虚构进度百分比、心跳、在线状态、模型调用或完成数量。必须区分 Agent 注册、Supervisor 可调用、真实模型执行、Worker 存活、Run done、Review 通过和最终交付。

Ruflo 可以在新证据改变范围、依赖或验证需求时重新评估：
- Suggestion / Manual 模式下，重大计划变化先给用户确认；
- Autonomous 模式下，只能在已批准范围内调整，并记录原因；
- 已完成任务及证据必须保留，只重新安排剩余任务；
- 不得无技术理由重启整个任务。

运行中的人工操作仅限当前 Ruflo / Autoloop API 真正支持的能力：
- 查看计划和 Agent / Worker 分配；
- 请求重新规划；
- 调整剩余任务优先级和执行顺序；
- 对剩余工作调整 Agent / Worker 或并行度；
- 通过实际所属 Runtime 操作暂停、恢复或取消；
- 修改剩余工作的 Review / QA 范围；
- 请求独立 Review 或范围内返工；
- 接管任务或返回 Manual 模式。

如果当前 Run 无法动态修改，应明确提示“当前 Run 不支持；可对下一次 Run / 重新规划生效”，不得伪造操作成功。

## 10. Review、QA、返工和最终交付

### 10.1 独立 Review

Reviewer 必须使用独立于实施者的上下文，读取原始需求、当前确认计划、代码 Diff、Commit、测试和交付证据。实施者不得自审自批。

Review 只检查已批准范围和验收标准。可选优化单独列出，不得变成强制返工或扩大本次需求。

### 10.2 Product QA

QA 必须从真实产品入口或适用测试入口验证目标行为，不能只根据单元测试或 Worker 自述给出通过结论。

### 10.3 返工

- 范围内缺陷由 Ruflo 组织返工；
- 保留原有完成项、Commit 和证据；
- 只返工受影响部分；
- 新的执行授权必须遵守当前已接通的权威机制；
- 超出原范围的改动单独提出，不得混入强制返工。

### 10.4 交付

交付视图至少展示：
- 最终交付摘要；
- 完成 / 未完成 / 阻断任务；
- 代码仓库、分支、Commit、Diff；
- 实际测试及结果；
- Review 和 QA 结论；
- Autoloop Event / Run、Worker 和模型证据（仅限真实暴露字段）；
- 文档和交付文件；
- 剩余风险、未决问题和后续建议。

最终结果必须回到原工程任务和需求上下文，形成完整追溯。Worker done 或 Autoloop Run done 不等于最终验收通过。

## 11. 数据、版本与持久化

- 复用 V1.1 已部署的需求会话持久化、文档版本和项目上下文机制。
- 工程计划作为版本化产物关联到对应需求会话及 EO Job / Workorder。
- 正式工程任务继续由现有 EO 权威记录；执行状态继续由现有执行 Runtime 权威记录。
- Dashboard 可以缓存读取数据，但缓存必须有明确新鲜度，不能成为持久任务账本。
- 不创建第二套 Job / Workorder / Execution / Attempt / Run 数据库。
- 计划修订必须保留历史版本；不得覆盖已经确认的计划或文档。
- 项目之间的需求、档案、证据和执行计划必须隔离。
- 不在浏览器 localStorage 或前端代码保存 Token、API Key、Cookie 或其他凭据。

## 12. 模型与角色约束

### 12.1 模型

复用此前已验证的模型配置作为推荐值：
- Ruflo Supervisor / Agents：gpt-6.2-sol / high；
- Autoloop Codex Worker：gpt-6.2-sol / high。

PCP 工单中的 provider-neutral 推荐为 SOL / High。不得按 C0–C3 自动降低模型或 reasoning effort，不做按复杂度自动路由，不修改 CC Switch 或普通 Codex 全局 Provider 配置。

配置标签不等于真实执行证据。实际模型和 reasoning effort 仅在 Runtime 暴露时记录；不暴露时使用 PCP 规定的 NOT_EXPOSED_BY_RUNTIME / runtime_unobservable，不得猜测。

### 12.2 PCP 角色组织

遵守 PCP 五角色 WebGPT 组织 V0.2 FIXED：
- Supervisor；
- Chief Engineer；
- Execution Coordinator；
- Reviewer；
- Operations。

PCP Controller 是控制面板，不是第六个 Agent。N 个 Codex Worker 与五个 WebGPT 角色不是同一数量体系。

该固定组织基线不要求每个工程任务都启动全部五个角色。Ruflo 内部 Agent 和 Autoloop Worker 的数量、名称、状态必须以实际 Runtime 返回为准，不得把 WebGPT 角色、Ruflo Agent 和 Codex Worker 混为一谈。

## 13. 部署与访问

保留 V1 已有部署方式：
- 主机：cbnet，Windows 11 / WSL2 Ubuntu 24.04；
- Dashboard：现有本地服务；
- 用户访问：现有 MEC LAN HTTPS；
- 端口：优先沿用当前实际配置；历史目标端口为 8787，不得仅凭旧工单覆盖当前配置；
- 用户：现有单管理员边界。

不得重装 WSL、Codex、Ruflo、Autoloop 或已有运行环境。不得扩大到公共互联网，不新增身份系统，不暴露本地 stdio、Autoloop 未认证 HTTP 或 Runtime 凭据。

正常查看任务、进度和交付不应要求用户操作终端。提供实际访问 URL、服务启动方式和停止/禁用方式；不得根据历史配置猜测当前 URL 或端口。

## 14. 非目标

- 不重建 V1.1 Dashboard，不更换现有应用技术栈。
- 不重复 V1.1 已完成的对话、档案、持久化、文档版本和经验检索功能。
- 不重跑首轮 Ruflo / Autoloop 三任务 POC或已完成的 Tool Calling 验证。
- 不独立重新派发 WO-20261124-003 的重叠范围；本工单整合其产品目标。
- 不新增 ChatGPT 网页到 Ruflo 的 MCP Gateway、Tunnel、ChatGPT Connector、远程端点或 GPT 专用身份认证。
- 不通过 CB Bridge / Tunnel Client 连接 Ruflo。
- 不新增 Scheduler、队列、Worker Pool、Event Bus、Agent Memory、第二套任务数据库或执行状态机。
- 不修改 CB Blue/Green、CB TaskStore、EO / ES Schema 或上游实现、Ruflo / Autoloop Fork 源码。
- 不新增 PCP Core Baseline、Skill、Gate、通用模型路由或跨项目框架。
- 不自动合并、发布或部署生产；不使用生产数据和客户凭据。

## 15. 执行方式与实施步骤

本工单必须由 cbnet 本地 Codex CLI 执行，并由现有 Ruflo Supervisor 负责工程规划和任务编排。

### 15.1 首先核实真实本地状态

执行前：
1. 读取本地 AGENTS.md、README.md、PROJECT_STATUS.md 和本工单。
2. 确认实际仓库根目录、当前分支、完整 HEAD、git status --short、未跟踪文件和 Worktree。
3. 确认当前 Dashboard 服务、启动方式、监听地址、HTTPS 入口、当前前后端技术栈。
4. 确认现有 Ruflo MCP、Supervisor、Autoloop Hub / Worker 的真实状态。
5. 定位 V1.1 原始部署报告、测试证据、持久化数据边界和现有适配器。
6. 核对本地是否已有 WO-20261124-003 的实现和证据；只复用，不重复派发。

用户报告的 V1.1 连续性信息（必须在本地重新核实）：
- 已部署版本对应本地报告 Commit：f854fc325cebfa41a6b2fd50c5f496d59d0bb121；
- 用户报告的定向测试结果为 19 项 Python 检查和 18 项浏览器检查通过；
- GitHub 远端 main 的历史 HEAD 为 cfb20f24e34812e80ccd038feb49e05d0c9157bb，不能据此认定远端 main 包含本地部署版本。

以上是连续性线索，不是当前运行事实。必须在本地核对原始报告、测试路径和 Git 状态后再引用。

保留本地全部 Commit、未提交修改、未跟踪文件、现有 Worktree 和运行证据。严禁 reset、clean、rebase、强制同步、覆盖本地工作区或为读取设计分支而切换当前工作分支。不要强制使用固定分支名。

### 15.2 Ruflo 首次接手

本地 Codex 完成本地只读 Bootstrap 后，必须通过现有 Ruflo MCP：

1. 调用 mcp_status；
2. 检查当前 Supervisor、Agent 和工具能力；
3. 将本工单原文、V1.1 需求档案边界和已有 POC 证据交给 Ruflo Supervisor；
4. 由 Ruflo Supervisor 自己评估并制定本工单的实施计划；
5. 保存实际 Supervisor 响应和可观测的模型证据。

外层 Codex 不得代替 Ruflo 编写工程拆分和派发计划。Codex 仅处理必要的本地 Bootstrap、环境核对和最小连接操作；后续由 Ruflo 组织 Agent、调用 Autoloop、派发 Worker、Review、QA、返工和最终验收。

如果现有 Ruflo MCP 或 Supervisor 无法执行，记录具体工具名、调用参数范围、实际错误和最小解除条件。不得伪造 Ruflo 规划，也不得擅自新建 Gateway / Tunnel。继续完成不依赖该能力的安全 UI、文档和本地功能。

### 15.3 实际实现

1. 将 V1.1 需求档案接入 Ruflo 规划输入。
2. 在现有 Dashboard 中实现计划生成、任务列表、依赖关系和计划版本展示。
3. 实现 Suggestion / Manual / Autonomous 三种模式和人工可编辑配置。
4. 将用户最终确认的计划映射到现有正式任务记录或关联计划产物。
5. 接通现有 Ruflo / Autoloop 本地执行路径，不重建连接器。
6. 实现真实执行状态、Event / Run / Worker、日志、Commit、测试和证据展示。
7. 实现受支持的运行中人工控制、重新规划、Review、QA 和返工。
8. 完成交付结果与原任务、需求档案和文档版本的关联。
9. 更新 PROJECT_STATUS.md 和本版本报告。
10. 只运行受影响部分的定向测试；复用仍有效的 V1.1 和 POC 证据。

不要停留在计划、审计或差距列表。对已授权且可执行的部分直接完成实现。遇到单项接口限制时，只阻断该项操作，继续完成其他独立工作。

## 16. 验收标准

### A. V1.1 连续性
1. V1.1 对话、档案、来源、持久化和文档版本仍可正常使用。
2. 已确认的需求档案可以进入规划流程，不要求用户重复输入。
3. 页面刷新、浏览器新会话和 Dashboard 服务重启后，需求与计划版本均可恢复。
4. 原七个导航区和已完成页面没有被重建或破坏。

### B. 规划与任务拆分
5. Ruflo Supervisor 实际接收本工单及需求档案，并返回可检查的实施计划。
6. 计划包含必要任务、依赖、输入、输出和验收条件。
7. 简单任务不会被机械拆分；复杂任务能够表达真实依赖和可并行关系。
8. C0–C3 建议、复杂度、风险和授权分别表达。
9. C0 可以人工选择多 Worker / 完整 QA；C3 可以人工选择单 Worker / 串行执行，不存在复杂度硬锁。

### C. 人工编排
10. Suggestion 模式可以接受或修改 Ruflo 建议，最终派发采用用户确认配置。
11. Manual 模式下人工配置保持权威，Ruflo 不得静默覆盖。
12. Autonomous 模式只在明确授权范围内自主调整，并保留计划变更证据。
13. 受支持的 Agent、Worker、并行度、测试、Review、模型和范围参数可编辑。
14. 不支持的配置或运行中操作显示真实限制，不使用模拟按钮。

### D. 真实派发与监督
15. 用户确认需求、计划和执行范围后，才开始实际派发。
16. 通过现有本地 Ruflo → Autoloop → Codex Worker 路径完成至少一个受控非生产任务。
17. Worker 实际执行结果与对应 Event / Run、任务和计划能够关联。
18. Worker 使用隔离工作区，交付 Commit / Patch、测试和真实日志证据。
19. 任务详情展示真实状态、最后活动、数据新鲜度和阻断原因。
20. 运行中重新规划、暂停、恢复、取消等操作仅在现有 Runtime 支持时生效；不支持时明确说明。

### E. Review / QA / 交付
21. 独立 Reviewer 与实施上下文分离，读取原始需求、确认计划、Diff 和测试证据。
22. Product QA 验证实际产品行为，不以 Worker 自述替代。
23. Review 失败时可以在原范围内组织返工，保留已完成工作和原始证据。
24. 最终交付包含 Commit、Diff、测试、Review、QA、交付文件和未完成项。
25. Worker done、Run done、Review pass 和最终用户验收是不同状态，不得混淆。

### F. 架构与安全
26. 没有新增 MCP Gateway、Tunnel、ChatGPT Connector 或第二套 Scheduler / Worker Pool / 任务数据库。
27. 没有修改 CB / EO / ES Schema、上游 Ruflo / Autoloop 或生产环境。
28. 没有凭据泄露到浏览器、日志、文档或 Git。
29. 所有实际模型、Agent、Worker、Event、Run 和授权信息均有真实来源；未暴露字段如实标记。
30. 仅执行受影响测试，复用有效历史证据，不重复首轮 POC 和无关测试。

## 17. 交付物

- V1.2 Dashboard 实际实现，保留原 V1.1 工作区和功能。
- 需求对话到工程计划的实际操作截图。
- 任务拆分、依赖关系和人工编排界面截图。
- Suggestion / Manual / Autonomous 三种模式的真实行为证据。
- 至少一个受控非生产任务的真实 Ruflo → Autoloop → Codex Worker 执行证据。
- Event / Run / Worker / Commit / 测试 / Review / QA 的关联记录。
- 人工覆盖、重新规划和返工的实际证据。
- 版本化计划与需求档案的恢复证据。
- 定向测试结果及复用的历史测试证据来源。
- 更新 PROJECT_STATUS.md。
- 新增报告 reports/PCP-ENGINEERING-CONTROL-CENTER-V1.2-20261126.md。
- 实际运行 Commit SHA、变更文件摘要、Dashboard 访问 URL 和服务操作说明。
- 未完成能力及其精确解除条件。

## 18. Stop Conditions

仅在以下具体情形停止受影响的操作：
- 当前本地仓库身份或活动工作区无法确认，且修改可能覆盖用户工作；
- 当前授权不足，或操作涉及未授权的生产、客户数据、凭据和不可逆外部影响；
- 必需的 Ruflo / Autoloop 接口确实不可用，无法执行相应真实操作；
- 当前运行时关键兼容条件无法确认，继续会造成明确技术风险；
- 现有接口的权威边界存在冲突，不能在不越权的情况下完成该项操作。

停止时必须说明：具体失败范围、实际证据、解除条件，以及仍可继续完成的工作。未知状态不得自动扩大为全局阻断；单项接口不可用不得阻断无关 UI、计划、文档或测试工作。

## 19. Execution Profile

~~~yaml
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
~~~

遵循 PCP Execution Profile Resolution Baseline。人工明确选择优先；Runtime fallback 只能在真实发生且记录原因时使用。未暴露的模型或思考等级使用 NOT_EXPOSED_BY_RUNTIME / runtime_unobservable，不得猜测，也不得仅因非安全遥测缺失而停止执行。

## 20. Execution Environment

~~~yaml
execution_environment:
  expected:
    os: Linux
    shell: bash
    shell_version: UNKNOWN
    runner_type: Codex CLI on cbnet WSL2 Ubuntu 24.04
  sources:
    - type: workorder
      ref: Su9moon/PCP-Engineering-Runtime:workorders/WO-20261126-002-PCP-ENGINEERING-CONTROL-CENTER-V1.2.md
    - type: repository_evidence
      ref: Su9moon/PCP-Engineering-Runtime:AGENTS.md
    - type: repository_evidence
      ref: Su9moon/PCP-Engineering-Runtime:PROJECT_STATUS.md
    - type: repository_evidence
      ref: Su9moon/PCP-Engineering-Runtime:docs/architecture/POC_TARGET_ARCHITECTURE.md
    - type: repository_evidence
      ref: Su9moon/personal-ai-control-plane@22bae955686f03c5f440cdcd66e13a69f1289f90:governance/PCP_EXECUTION_ENVIRONMENT_RESOLUTION_BASELINE.md
  resolution:
    runtime_confirmation_required: true
    critical_fields:
      - actual repository path, branch, HEAD and working-tree state
      - actual WSL OS and shell
      - actual Dashboard service and HTTPS endpoint
      - actual Ruflo MCP and Supervisor availability
      - actual Autoloop Hub / Worker connectivity
    mismatch_policy: explicit_fallback_allowed
~~~

实际环境必须在本地确认；不得将期望环境当作当前事实。不得为了匹配历史版本号或旧端口而升级/替换当前正常运行的环境。

## 21. Connectivity Contract

~~~yaml
connectivity_contract:
  llm_connectivity:
    mode: required
    behavior_when_unavailable: "保留需求档案和人工编排；显示实际缺失的模型/Provider/连接；不得使用模拟回复或伪造 Ruflo 规划。"
  governance_connectivity:
    runtime: not_required
    update: none
  external_services:
    - capability: Existing local Ruflo stdio MCP
      requirement: required_for_live_Ruflo_planning
      behavior_when_unavailable: "报告实际调用错误；继续可独立完成的 UI、计划编辑、文档和测试；不得新建 Gateway/Tunnel。"
    - capability: Existing local Autoloop Hub / Worker APIs
      requirement: required_for_live_dispatch
      behavior_when_unavailable: "继续计划、人工编排和监控 UI；不得伪造 Run 或 Worker 状态。"
    - capability: Existing GitHub repository access
      requirement: required_for_commit_and_evidence
      behavior_when_unavailable: "保留本地实现和证据，明确报告未能推送；不得声称远端已更新。"
    - capability: Existing cbnet Dashboard HTTPS / MEC LAN
      requirement: required_for_browser_acceptance
      behavior_when_unavailable: "完成本地实现与测试，报告真实服务/网络阻断；不得扩大公网暴露。"
~~~

## 22. Dispatch Instruction

将以下内容直接发送到 cbnet 本地 Codex CLI：

> 请执行 Su9moon/PCP-Engineering-Runtime 中的：
>
> workorders/WO-20261126-002-PCP-ENGINEERING-CONTROL-CENTER-V1.2.md
>
> 这是 V1.1 的连续升级，不是重建。先读取本工单引用的 PCP 权威基线、当前本地 AGENTS / PROJECT_STATUS、V1.1 已部署实现和原始证据。核对本地 HEAD、分支、工作区和服务状态；不要用远端旧 main 覆盖本地部署版本。
>
> 首先通过现有 Ruflo MCP 调用 mcp_status，并让 Ruflo Supervisor 使用 SOL / High 推荐配置评估本工单、制定任务拆分和实施计划。保存真实 Supervisor 响应和模型证据。随后由 Ruflo 组织 Agent、调用现有 Autoloop、派发 Codex Worker、监督、Review、QA、返工和最终验收。外层 Codex 不得代替 Ruflo 做工程规划和派工。
>
> 复用 V1.1、首轮 Ruflo / Autoloop POC 和已有自适应编排成果。WO-20261124-003 的重叠需求已经合并到本工单，不要平行重复派发；如已有实现，复用并只补差距。
>
> 不新增 MCP Gateway、Tunnel、ChatGPT Connector 或远程控制端点；不使用 CB Bridge；不重建 Scheduler、Worker Pool、任务数据库或 Ruflo / Autoloop Connector。保持现有 cbnet 本地 Codex → Ruflo MCP → Ruflo Supervisor → Autoloop → Codex Worker 执行拓扑。
>
> 直接完成本工单范围内可执行的实现，不要只返回计划或审计报告。只验证实际受影响部分，复用未受影响的历史测试证据。交付代码、真实运行证据、Review / QA、报告和 Commit SHA。
