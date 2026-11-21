# ADR-2026-11-22-001｜PCP Engineering Runtime 独立项目与集成方向

- 状态：**APPROVED FOR PROJECT BOOTSTRAP / POC**
- 日期：2026-11-22
- 决策范围：建立 PCP 下游独立工程项目；批准目标分层和 POC 方向，不代表生产架构已验收。
- 目标仓库：`Su9moon/PCP-Engineering-Runtime`
- 关联工单：`workorders/WO-20261122-PCP-ENGINEERING-RUNTIME-BOOTSTRAP-01.md`

## 1. 背景与真实需求

PCP 当前 EO、ES、CB 已有固定职责和持续实现，但复杂工程任务仍需要跨项目规划、多执行节点、独立审核、产品级验证和自动返工。继续在 EO、ES、CB 内重复建设 Agent 编排、Worker 调度、远程节点通信和生命周期机制，会造成职责重叠和重复维护。

用户已明确选择以开源产品为基础，成本主要投入模型 Token，并确认采用三种不同执行通道：

1. 看板等简单业务任务：由 CB 直接对接受控外部 API，输出结构化报告供应用嵌入。
2. 简单开发任务：由 Autoloop 调度单个执行节点完成。
3. 复杂工程任务：由中央智能体主机组织多个 Autoloop 外部执行节点，统一监督、独立审核、产品 QA、返工和交付。

## 2. 架构治理结论

```yaml
architecture_gate:
  required: true
  status: complete
  real_use_evidence: verified
  decision: INTEGRATE
  pcp_specific_remainder: "PCP Workorder 到 ExecutionRequest 的映射、ES 授权保持、中央 Supervisor 控制、独立 Review/Product QA、结果与 Evidence 回写；不重复实现上游运行机制"
  minimum_formalization: "建立独立集成仓，复用 Ruflo 与 Agent Autoloop，通过薄 Adapter 接入 EO/ES/CB；先完成纵向 POC，不建设第二套任务账本、调度器或 Worker Pool"
```

### 2.1 Direct analogs

- Ruflo：多 Agent 组织、Supervisor、工具接入、Codex 集成和 Worktree 能力。
- Agent Autoloop：Hub/Worker、远程节点接入、执行生命周期、事件和结果回收。
- OpenAI Symphony：任务板驱动、Codex 工作区与持续执行编排的设计参考。

### 2.2 Adjacent-domain analogs

- PCP ES 已固定的 Runtime Binding / Provider 与 Executor Adapter 分离。
- GitHub Actions Shared Runner 已有的跨仓库执行 Provider 验证。
- Git / GitHub 的分支、Worktree、PR、Review 和 CI 机制。

### 2.3 Structural analogs

采用控制面与执行面分离的分布式系统结构：中央控制器持有授权与调度意图，远程 Worker 执行有界工作，执行事实回到唯一权威账本；Worker 存活、任务完成回执和最终验收是不同事实。

### 2.4 Decision

**INTEGRATE**。复用成熟上游运行机制；PCP 只实现保持自身 Work Intent、Execution Authority、Evidence 和 Review 语义所需的薄适配。

## 3. 项目边界与事实权威

| 系统 | 权威职责 | 不得重复承担 |
|---|---|---|
| PCP 主仓 | 全局治理、项目关系、授权原则、架构决策和经验晋级 | 具体 Worker 运行状态 |
| EO | Engineering Job、Workorder、Result、Evidence、Job-level Review | 实时队列、Worker 心跳和进程状态 |
| ES | ExecutionRequest、Execution、Attempt、Invocation、当前执行权威、状态、Retry/Recovery 决策 | 具体 Provider 的内部运行账本 |
| Ruflo | 复杂任务的理解、规划、Agent 组织、监督、独立 Review 和 Product QA | PCP canonical Execution/Attempt 状态、生产授权 |
| Autoloop | Hub/Worker 调度机制、远程节点接入、执行进程、运行事件和结果回收 | PCP Attempt 授权、工程验收结论 |
| CB | 轻量业务 API/MCP 连接、受控外部服务调用、应用结果交付；保留现有 Bridge 能力 | 第二套通用 Agent Orchestrator / Worker Pool |
| Project Git | 正式源码、Worktree、PR、测试、版本和工程产物 | 工程任务与执行权威 |

所有 Ruflo / Autoloop 运行事实均为 Provider 输入。只有 ES 可以更新 canonical Execution / Attempt 状态；Autoloop 内部重试不得绕过 ES 创建新 Attempt 的授权。EO 的 Acceptance Criteria 仍是 Review 的目标事实源。

## 4. 目标执行通道

### L0 — 业务 API 直连

`Application → CB API Adapter → Allowlisted External API → Structured Result → Application UI`

不启动 Ruflo、Autoloop 或 Codex。API 目标、凭据、响应 Schema 和调用权限由 CB 受控配置；不允许任意 URL 代理。

### L1 — 单节点工程执行

`EO Workorder → ES Authorization → Autoloop Hub → One Worker → Executor → Evidence → Review`

简单开发任务直接使用一个 Worker，不强制启动多 Agent。

### L2 — 中央主机多节点工程执行

`EO Workorder → ES Authorization → Ruflo Supervisor → Autoloop Hub → Multiple Workers → Central Review/Product QA → EO Result/Evidence`

Ruflo 负责规划和监督；Autoloop 负责执行节点生命周期；ES 负责唯一执行授权和状态权威。

## 5. 必须保持的系统不变量

1. 一个 PCP Execution 的当前 Attempt 和执行权威由 ES 唯一确定。
2. 同一 Execution 同一时刻至多一个 active Attempt；失去、撤销或被替代的执行权威不能更新 canonical state。
3. Autoloop 的内部 Retry 不得静默变成新的 PCP Attempt；需要新的真实执行路径时，先由 ES 创建并授权新的 Attempt / Invocation。
4. Worker 的心跳、进程存活、完成回执均不等于 EO Review 或最终验收。
5. 每个并行写入任务使用隔离的 Worktree / 分支；Reviewer 使用独立上下文和只读输入；Product QA 使用受控测试环境。
6. Ruflo 不拥有 PCP 生产部署授权；生产变更沿用现有授权边界。
7. CB 的轻量 API 通道独立于 Ruflo/Autoloop，不为简单查询启动 Agent。
8. Ruflo、Autoloop 保持可替换；上游升级通过固定版本/Commit 和必要的兼容验证管理。

## 6. 新仓所有权

新仓 `pcp-engineering-runtime` 负责：

- Ruflo Supervisor 与 PCP 工程上下文之间的集成；
- Autoloop Hub/Worker Provider Adapter 原型及其执行关联；
- EO/ES 的薄映射和结果 / Evidence 回写适配；
- 独立 Review、Product QA、返工协调；
- 部署配置、集成测试、运行文档和 POC 证据。

新仓不负责：

- 重写 EO/ES 的 canonical object、schema、state machine 或授权机制；
- 新建第二套 Job/Workorder/Execution/Attempt 账本；
- 自建通用 Scheduler、Worker Pool、远程消息总线或 Agent Memory Platform；
- 复制 Ruflo / Autoloop 全部源码并长期维护一个私有大分叉；
- 修改 CB Blue/Green 现有运行实例；
- 直接执行未授权的生产操作。

Ruflo 与 Autoloop 保持独立上游/Fork 仓库；新仓以固定 commit、配置和薄适配引用它们。只有明确的 PCP 特定缺口才在对应 Fork 中做最小修改。

## 7. 首个验证里程碑

首个 POC 必须完成一条真实纵向链路：

1. 一份真实 EO Workorder；
2. ES 创建并授权一个 Execution / Attempt / Invocation；
3. Ruflo 接收授权范围并规划任务；
4. Autoloop Hub 将任务派发给至少一个真实外部 Codex Worker；
5. Worker 在独立 Worktree 中修改代码、执行测试并提交产物；
6. 结果及运行证据返回中央主机；
7. Ruflo Reviewer 独立检查原始 Workorder、Diff 和测试证据；
8. QA 通过真实产品入口验证目标行为；
9. QA 失败时，由 EO/ES 产生合法整改 Workorder / 新 Attempt，Autoloop 不得自行越权重试；
10. 通过后回写 EO Result / Evidence / Review。

POC 阶段先验证单节点，再扩展双节点并行；不把 Mock、Agent 名称注册、合成测试或单元测试当作真实远程执行证据。

## 8. 当前已知依赖事实

- Autoloop Fork 已通过当前 GitHub 连接确认：`Su9moon/agent-autoloop-pcp`，上游 `KKKKhazix/agent-autoloop`，MIT。
- 本决策写入时，当前连接可见的 Su9moon 仓库列表尚未找到 Ruflo Fork。不得把 `ruvnet/ruflo` 上游地址误标为用户 Fork；创建 Ruflo 依赖配置前应确认 Fork 的准确 URL。
- 新仓采用私有仓库，除非用户后续明确改变可见性。
- 第三方 MIT 代码如被复制或再分发，保留相应版权与许可证声明；不以 MIT 许可推定可使用上游商标。

## 9. 状态声明

本 ADR 批准建立项目、职责边界和 POC 方向。它**不宣称 Ruflo + Autoloop + EO/ES 已经联通，也不批准生产迁移或自动生产部署**。生产架构是否采用，以真实 POC 证据和用户后续决策为准。


## 10. 2026-11-22 建仓与源码核验补充

### 10.1 Repository identity

- 用户已创建目标仓库：`https://github.com/Su9moon/PCP-Engineering-Runtime`。
- GitHub 当前核验：`main` 分支，`Public`，仓库初始为空；用户拥有 Admin / Push 权限。
- **保留用户创建时的 Public 设置**，不擅自切换为 Private。
- 新仓是 PCP 下游 Domain 的代码与集成事实源；本 ADR 仍由 PCP main 持有跨域架构权威。

### 10.2 Autoloop remote Worker capability — source verified

已核对 Fork `Su9moon/agent-autoloop-pcp@f27466d5f0ec9fc6f2f48a1fa68c748581906bdc`：

- `host/config.ts` 明确区分 Hub 主机与仅执行 Worker 的机器；Worker 机器只需要 Hub URL 与自己的 Worker key。
- `host/up.ts` 可独立启动 Hub 或 Worker；Worker 通过 `hubClient(config.url, key)` 主动连接 Hub。
- `protocol/client.ts` 的 Worker `work()` 通过 HTTP `GET /v1/work` 长轮询领取任务。
- 因此 Worker 可以主动向 Hub 建立出站连接，不要求 Worker 主机开放入站端口。Hub 若监听非回环地址，源码提示应置于 HTTPS 反向代理之后。
- `kernel/decide.ts` 目前有最多 10 次自动失败重试与指数退避。此为 Autoloop Provider 内部运行事实；集成时必须将其关联到同一个 ES Attempt / Invocation，不得把它静默转成新的 PCP Attempt。只有 ES 授权新 Attempt 后，才可开始新的 PCP 执行路径。
- 当前 Fork `package.json` 为 `private: true`、`node >=24`、MIT，未声明 package version；集成应按 Git commit 固定源码，不假设 npm latest 即为该 Fork。

这证明 Autoloop 源码具备远程 Hub/Worker 协议路径，**不等于已完成真实跨主机联通或多节点验收**。

### 10.3 Ruflo and Symphony source identity

- Ruflo 上游核验：`ruvnet/ruflo@87f612cef121b50c2e31e2d3f88e46d88963a377`，README 标注版本 3.80.0、MIT；根 `package.json` 当前包名为 `claude-flow`，而 README 使用 `ruflo` 命令，部署前必须核实实际可安装包名与启动路径。
- 用户已表示 Ruflo Fork 已存在；但本次连接可见的 Su9moon 仓库清单和按名称检索未能识别其确切 `owner/repo`。**不得将 `ruvnet/ruflo` 标成用户 Fork**。Codex 应先在用户本机 GitHub 登录上下文中定位；若仍不可见，可将上述固定上游 commit 作为只读 POC 依赖，不得向上游写入。
- 用户已有 `Su9moon/symphony-cb`，Fork 自 `openai/symphony`，当前 HEAD `be10a1b79df723d6d7612b5651c8522704dafb2e`，Apache-2.0。其 `SPEC.md` 标记为 Draft v1，Elixir README 将实现标为 evaluation-only prototype；保留为工作流/隔离执行的结构参考，不纳入当前运行依赖。

### 10.4 L0 business API boundary clarification

L0 表达用户确认的目标分工：简单业务任务由 CB 直接调用受控外部 API，返回结构化结果给业务应用；该通道不启动 Ruflo/Autoloop。此决策**不声称当前 `codex-bridge` 仓库已经具备通用外部业务 API Adapter**。本次 Engineering Runtime POC 不修改 CB，也不扩展 CB 的现有 Worker/Task 架构；L0 的具体 Adapter 另按 CB 当前 Baseline 与授权推进。


### 10.5 Domain and project-surface identity

- Stable domain identity: `pcp-engineering-runtime`.
- Canonical Remote Git: `Su9moon/PCP-Engineering-Runtime`, branch `main`, Public.
- Apply current `PCP_PROJECT_WORKSPACE_IDENTITY_BASELINE_V0.2_FIXED.md`; V0.1 is the historical predecessor.
- Apply `PCP_PROJECT_SURFACE_NAMING_CONVENTION_V0.1_FIXED.md` when a Local Codex Project is provisioned. Recommended display name: `Lo_PCP Engineering Runtime`.
- Local Git metadata and Persistent Worktree are progressively provisioned, not hard bootstrap gates. No local path is asserted by this ADR; discover the user's actual workspace at execution time. Do not substitute the baseline's default path for a user-configured path.
- A Web GPT Project is optional and is not required to make the Git domain valid. Production Runtime Workspace / Installed Release do not exist yet and are not part of this POC.
