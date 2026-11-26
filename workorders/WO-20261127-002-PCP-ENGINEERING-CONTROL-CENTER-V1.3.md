# WO-20261127-002｜PCP Engineering Control Center V1.3
# Practical Engineering Execution — 实际工程执行与自主交付

## 1. Identity / 工单身份

~~~yaml
repository: Su9moon/PCP-Engineering-Runtime
workorder_id: WO-20261127-002
title: Practical Engineering Execution and Autonomous Delivery
executor: Codex
priority: P0
product_version: V1.3
source_issue: null
architecture_gate:
  required: false
  reason: routine_implementation
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
execution_environment:
  expected:
    os: Ubuntu 24.04 on WSL2
    shell: bash
    shell_version: UNKNOWN
    runner_type: Local Codex CLI on cbnet
  sources:
    - type: validated_runtime_evidence
      ref: Su9moon/PCP-Engineering-Runtime@4ec2ef2b45985c1fcc710ece05bd4f0d12280452:PROJECT_STATUS.md
    - type: validated_runtime_evidence
      ref: Su9moon/PCP-Engineering-Runtime@4ec2ef2b45985c1fcc710ece05bd4f0d12280452:reports/PCP-ENGINEERING-CONTROL-CENTER-V1.2-D01-20261127.md
  resolution:
    runtime_confirmation_required: true
    critical_fields:
      - os
    mismatch_policy: fail_closed
~~~

Architecture classification: 在已批准 ADR 的架构与权威边界内，扩展已实现的项目级 Dashboard 和适配器；复用 INTEGRATE 决策，不新设通用机制或新的架构 Gate。如实际发现必须修改跨域权威契约，单独定位该差距，不自行重定义契约。

## 2. Objective / 目标

把 V1.2 的一次性 D01 合成验证闭环升级成可重复使用的真实工程控制中心。用户从原 Dashboard 提出需求、与 AI 对话、编辑规划、授权下达；Ruflo 在授权范围内自主组织真实代码开发、测试、独立 Review、QA、必要返工、证据回写和交付，关闭浏览器后仍能继续，不依赖用户逐项转交工单。

优先使本机单 Worker 完成实际开发；随后按现有可用资源扩展并行及外部 Worker。不得把多节点或环境缺口扩大为本机交付阻断。

固定产品要求：本机与可信私有 LAN 均免登录；用户可操作对话、规划、授权、派发和查看结果；英文技术内容可保留，必须有完整中文对应信息；C0–C3 仅建议，Suggestion / Manual / Autonomous 模式及人工覆盖保留。

## 3. Governing references / 权威基线与输入

PCP canonical refs（沿用此前已核实的 22bae955686f03c5f440cdcd66e13a69f1289f90；执行时核对现行权威版本）：

- Su9moon/personal-ai-control-plane:AGENTS.md
- Su9moon/personal-ai-control-plane:governance/PCP_ENGINEERING_AGILITY_PRINCIPLE.md
- Su9moon/personal-ai-control-plane:.agents/skills/pcp-session-bootstrap/SKILL.md
- Su9moon/personal-ai-control-plane:.agents/skills/pcp-experience-reuse/SKILL.md
- Su9moon/personal-ai-control-plane:.agents/skills/pcp-workorder-handoff/SKILL.md
- Su9moon/personal-ai-control-plane:processes/experience-reuse-gate.md
- Su9moon/personal-ai-control-plane:governance/adr/ADR-2026-11-22-001_pcp-engineering-runtime.md
- Su9moon/personal-ai-control-plane:governance/PCP_EXECUTION_PROFILE_RESOLUTION_BASELINE.md
- Su9moon/personal-ai-control-plane:governance/PCP_EXECUTION_ENVIRONMENT_RESOLUTION_BASELINE.md
- Su9moon/personal-ai-control-plane:governance/baselines/PCP_WEBGPT_ROLE_ORGANIZATION_V0.2_FIXED.md
- Su9moon/personal-ai-control-plane:governance/baselines/PCP_RELEASE_RUNTIME_INDEPENDENCE_BASELINE_V0.1_FIXED.md

Runtime repo refs（V1.2 已推送交付基线 4ec2ef2b45985c1fcc710ece05bd4f0d12280452）：

- Su9moon/PCP-Engineering-Runtime:AGENTS.md
- Su9moon/PCP-Engineering-Runtime:README.md
- Su9moon/PCP-Engineering-Runtime:PROJECT_STATUS.md
- Su9moon/PCP-Engineering-Runtime:docs/architecture/POC_TARGET_ARCHITECTURE.md
- Su9moon/PCP-Engineering-Runtime:docs/integration/DEPENDENCY_MAP.md
- Su9moon/PCP-Engineering-Runtime:docs/engineering/EXPERIENCE_REUSE.md
- Su9moon/PCP-Engineering-Runtime:workorders/WO-20261126-002-PCP-ENGINEERING-CONTROL-CENTER-V1.2.md
- Su9moon/PCP-Engineering-Runtime:reports/PCP-ENGINEERING-CONTROL-CENTER-V1.2-D01-20261127.md
- Su9moon/PCP-Engineering-Runtime:dashboard/README.md
- Su9moon/PCP-Engineering-Runtime:dashboard/formal.py
- Su9moon/PCP-Engineering-Runtime:dashboard/operator_grant.py
- Su9moon/PCP-Engineering-Runtime:dashboard/sealed_modules.py
- Su9moon/PCP-Engineering-Runtime:dashboard/serve.py
- Su9moon/PCP-Engineering-Runtime:dashboard/planning.py
- Su9moon/PCP-Engineering-Runtime:dashboard/intake.py
- Su9moon/PCP-Engineering-Runtime:dashboard/plan.js

EO/ES/Autoloop/Ruflo 具体源代码和契约沿用 dependency map 的精确引用，先核对本机实际使用版本。禁止根据摘要猜测接口。

Experience reuse: REUSE / EXTEND, PROJECT_LOCAL。继承已批准 INTEGRATE 架构、V1.2/D01 实证和项目经验记录；复用既有检索结论（项目记录尚无直接匹配的 Validated Ruflo/Autoloop 资产，Candidate/Inbox 只作证据）。无需重复跨域研究或全量测试。

## 4. Starting point / 真实起点

- 当前远端交付分支 dashboard/wo-20261125-001，D01 交付 HEAD 4ec2ef2b45985c1fcc710ece05bd4f0d12280452，报告记载部署代码 c51a98de770114d6f8db8eecb803736a9a24e2c5。读取本地实际工作区与服务，保留后续合法提交、原 main 和全部未提交内容；远端旧 main 不得覆盖已部署代码。
- D01 已证明中文真实对话、模型规划、Manual 编排、EO 创建和读回、ES 唯一授权、Event 30 / Run 29、独立 Reviewer / QA、ES APPROVED/DONE 及 Dashboard 报告读回。Run 28 保留 unknown，不重派。
- D01 Worker 仅文本输出，没有工具事件、代码修改、测试或 Git 交付。当前 formal.py 存在 REQ-D01、synthetic-text-only、no_file_or_tool_use 等专用实现；报告明确 D01 规则及单次正式动作权限已关闭。本轮解决真实通用执行，不再做一句话的合成任务。
- LAN 普通草稿免登录可读写，模型及正式动作返回 403。服务端授权当前只识别 service owner 和回环连接，并不识别独立个人身份。
- Hub 47355 和 ruflo-local 是此前恢复的临时用户级 systemd 单元。报告确认宿主机重启后需要恢复。当前实际在线状态必须以现场为准。
- 既有测试：25 Python + 22 浏览器断言，以及 D01 定向 5 Python、3 授权、5 隔离验证和 Node 检查。复用未受影响结果；针对变更做必要验证。
- D01 证明本机运行，不证明跨主机执行、EO 完整 Result/Evidence/Review 权威回写或长期无人值守。以实际新增证据关闭这些缺口，不修改历史记录。

## 5. Implementation / 实际实施

### P0-A — Durable runtime / 服务持久化

1. 在 cbnet 本地调用现有 Ruflo Supervisor，交付本工单目标及上述基线。先恢复可执行路径，再推进其余工作。Codex 只做必要 bootstrap 和真实工程操作，不代替 Ruflo 的持续监督和最终工程验收。
2. 复用原 Dashboard 8787、Hub 47355、Worker 配置及同一权威数据目录。将临时 Hub/Worker 单元转为正常持久的用户级 systemd 服务，使用现有经过验证的启动命令、工作目录、私有配置和凭据引用。不要同时启动第二个指向同一 store 的 Hub/Worker，不重复安装。
3. 优先沿用现有 WSL 用户服务和 Windows 启动机制；实现适合当前环境的开机恢复，确保服务依赖、正常退出、失败重启及运行状态读回。宿主机未真实重启时不得宣称 Windows 重启验收；在允许的范围内实测服务重启与 WSL 会话恢复。不得未经授权重启整个宿主机或停掉其他业务。
4. Supervisor 的续推进不能依赖浏览器连接或初始 Codex 对话保持打开。优先复用现有 Ruflo/Autoloop 运行与恢复能力，必要时仅在现有适配器中补齐针对当前 EO/ES 记录的恢复/续作入口。不得新造通用 scheduler、第二套队列或任务数据库。恢复时按权威状态继续，不能重复创建 Event、Attempt 或重派已完成任务。
5. Dashboard 连接/Worker 页展示实际服务状态、观察时间和阻断原因；仅使用真实可用的服务操作。未支持的动作不伪造。

### P0-B — LAN operation / 局域网完整操作

1. 保留本机与已配置可信私有子网的 HTTPS 免登录入口（当前报告为 192.168.5.6:8787；地址按现场实际配置）。在局域网可执行对话、规划、人工编排、明确确认、正式授权下达、查看运行与报告。
2. 扩展 operator_grant.py 与 serve.py 的现有服务端授权：只有实际匹配的已配置可信 LAN 连接、TLS 同源、服务端允许的操作和项目范围才可使用相应能力；使用真实连接来源，不信任任意转发头、Origin 单独声明或任意浏览器提供的授权字段。保留防跨站请求、项目/路径白名单、范围校验、凭据服务端保存。免登录意味着不声称知道个人身份；记录真实可观察的 service-owner authority 和操作来源。不要新增登录、身份平台、公开互联网入口或客户端密钥。
3. 正式操作必须绑定用户确认的需求/计划版本及具体项目、操作权限、预算/资源限制（已有能力支持时）。同一已授权范围内的自主子任务及正常返工不要求用户重复确认。拒绝超范围、任意命令、任意仓库路径和生产操作。不能以“可信 LAN”替代 EO/ES 授权。
4. 在原服务配置和原子网边界内启用真实操作；独立 MEC 实测若需要用户设备，提供准确访问地址和最短人工验证步骤，标明未实测，不阻断本机其余工作。

### P0-C — Reusable formal execution / 通用工程任务下达

1. 在现有 formal.py、planning.py、serve.py、intake.py、相关前端及已存在的 Runtime Adapter 内，将 D01 专用绑定改成通用、项目范围受控的工程任务路径。保留 D01 原记录及其只读回显，不恢复其派发权限。
2. 使用现有项目注册/仓库映射；先启用 PCP-Engineering-Runtime 自身作为首个真实写入目标。按已批准计划选择工作区、源提交、任务依赖、执行模式和 Worker。后续注册其他项目沿用同一受控机制，而非为每份草稿改代码或手工编辑服务私有配置。
3. 以现有 EO Schema/Template 创建正式 Job / Workorder，正确分配唯一身份并保存计划版本引用；以 EO Git 读回验证正式对象。使用现有 EO 权威存储和 Git 工作方式，不另建账本；授权范围允许时保留正式提交引用。
4. 使用现有 ES ExecutionKernel 和现有 store 生成并授权 Request / Execution / Attempt / Invocation。真实 Provider Run 关联按已有合同写入 runtime reference；禁止 D01 固定 ID、伪造状态、重复派发、跨计划复用授权及过期授权写回。
5. 使用现有 Autoloop 真实路由和 Worker 规则，允许经授权的代码写入、测试和 Git 提交，不再把所有任务限定为 synthetic-text-only。任务文本不允许决定任意命令、路径、凭据；执行参数由服务端从项目登记、确认版本和权限推导。每个并行 writer 隔离 Git worktree；禁止写入 Dashboard 当前运行源码、原 main 的未提交内容、运行数据库或凭据。
6. 从现有正式任务页支持新建/继续/再次下达其他已授权任务，不需要手工改 D01 开关。不创建通用无约束 shell、公开 API、Gateway 或新的身份系统。
7. 独立 Reviewer 依据原始 Workorder、确认计划、Diff、Commit 与测试；Product QA 从实际产品入口验证。通过后按真实 EO/ES 机制完成 Result/Evidence/Review 回写并读取最终状态。EO 写回未成功时如实保留可恢复状态，不把 ES DONE 冒充所有 EO 交付记录已完成。
8. 现有 sealed_modules.py 的有效完整性约束可复用，但不得把 D01 固定文件、固定签名或一次性人工复核升级为每次正常工程执行必须人工重新配置的流程。必要更新与正常版本发布一起完成。

### P0-D — First real work / 首个真实代码交付

不是再输出一段文本。使用 Dashboard 创建 PCP Engineering Runtime 自身的一个真实非生产开发需求：在既有 Connections / Worker / Run 视图补齐持久服务启动后的真实可用性及恢复状态展示，解决当前无法直观看出运行服务是否能继续接受任务的实际缺口。复用现有状态接口、数据来源和样式；只增加现场尚缺的功能，避免与 P0-A 重复开发。若该功能已由前序实现完整交付，Supervisor 选择同范围内另一个实际未完成的 Dashboard 运行可用性缺口，并在计划中解释依据。

- 由本地 bootstrap 完成让系统能够安全派发的最小改动后，将上述实际功能通过 Dashboard 的正式 EO/ES 路径交给真实 Worker，而非让初始 Codex 手工实现后冒充 Worker。
- Worker 在独立 worktree 实际改代码、执行必要测试、产生可审查 commit。捕获真实 tool/file change/test/commit 证据。独立 Reviewer、QA 使用真实目标和代码/产品证据。
- 通过现有授权部署流程将已通过复核的改动接入原非生产 8787 服务；禁止 Worker 直接覆盖正在执行的控制面或自行发布生产。由现有部署主体在任务安全边界内更新并保留回退路径。
- 通过 Dashboard 再下达一个独立、实际未完成的低风险工程任务（例如修复发现的中文显示/状态读取问题），复用相同通用机制，不更改源代码或私有配置来专门放行第二个任务。这是可重复性验证，不是重复合成 POC。

### P1 — Autonomous continuation / 连续推进与返工

- 在已授权的 Autonomous 计划内，使用真实执行结果触发 Ruflo 对剩余依赖、独立任务、Review/QA 及整改的安排。完成一项后继续下一项，不要求用户反复点击、不等待浏览器、不重新交接整份工单。
- 复用 V1.2 的计划版本和人工编排入口。用户可调整剩余任务、优先级、资源和模式；正在运行的任务仅使用 Provider 真正支持的操作，未支持时明确显示。
- 如真实 Review/QA 不通过，在原范围内自动组织最小整改；按 ES 现有机制产生必要的新授权 Attempt，保留历史。若本轮实际全部通过，不人为制造产品缺陷；可复用已验证的返工证据，补齐本次通用路径必要的定向失败分支验证并区分真实返工与测试夹具。
- 至少执行一个包含真实依赖的多任务计划，关闭浏览器后继续并在重新打开时看到状态。依据现有运行能力恢复 Supervisor 续作，验证不重复已完成任务。
- 只有超出范围、真实权限、明确资源限制或关键不可逆操作需要用户介入。局部阻断只影响相关任务及真实依赖，不停掉其他独立工作。

### P2 — Parallel & remote / 并行与外部节点

- 先完成本机可重复执行。若已有至少两个可用授权 Worker，使用真实独立任务验证并行、独立 worktree、依赖收敛和正确回链；不新建 Worker Pool。
- 外部 Worker 沿用 Autoloop 现有 outbound HTTPS 机制和独立凭据；复用已注册节点、实际可信可达路径和现有证书机制。没有独立授权主机、凭据或安全网络路径时，不扩大暴露范围、不虚构远端结果；记录具体缺口并保留 P0/P1 交付，后续接入时继续。
- 同一宿主机多个 Worker 只能证明本机并行，不能证明跨主机执行。

## 6. Connectivity / 连接契约

~~~yaml
connectivity_contract:
  llm_connectivity:
    mode: required
    behavior_when_unavailable: 保留现有草稿及正式任务状态，不伪造模型回复或执行成功；独立可执行工作继续。
  governance_connectivity:
    runtime: not_required
    update: package_supported
  external_services:
    - existing authorized LLM route
    - existing EO Git storage
    - existing ES ExecutionKernel and store
    - existing Ruflo Supervisor
    - existing Autoloop Hub and Worker
~~~

沿用已配置模型及认证路径，推荐 SOL / High；实际 model/effort 按暴露证据记录。不得将 ChatGPT 网页登录凭据提取给服务端，不新增付费服务或擅改 CC Switch/全局 Codex 配置。

## 7. Acceptance / 验收

P0 必须：
- 原 8787 服务保留、免登录；可信 LAN 和本机相应功能可用，原配置边界外的请求被拒绝。独立 MEC 未实测必须单列。
- Hub/Worker 持久启动配置生效，验证可执行的服务重启恢复，历史 D01/Run 28 保留，无重复派发。
- 两次不同真实任务通过通用正式入口，至少一次有实际代码 Diff、测试、Git Commit，第二次无 D01 式专用开关。不得用两个文本输出任务替代。
- Dashboard 真实展示对应 EO IDs、ES Attempt/Invocation、Autoloop Event/Run、Worker、Commit、Review/QA、结果；正式 EO Result/Evidence/Review 的创建及读回要分别核实。
- 独立 QA 从真实产品入口验收；更新原服务后能继续使用。
- UI、对话、计划、工单和交付报告具有完整中文信息；英文原文和机器字段保留，不能只有英文。

P1 必须：
- 实际多任务计划从已授权开始连续推进；关闭浏览器后仍在运行，重开可查看。
- 范围内返工机制可使用，并遵守 ES 授权；区分真实缺陷返工和测试/复用证据。
- 人工覆盖及接管行为真实生效，无新增复杂度 Gate。

P2：按真实可用 Worker 和网络验收条件交付；如条件缺失，仅标该项阻断，不阻塞 P0/P1，不宣称已通过跨主机验收。

## 8. Deliverables / 交付物

- 原 Dashboard V1.3 实际代码及已部署版本；启动/恢复配置和简明运行说明。
- 首个真实开发任务及第二个实际任务的 EO/ES/Autoloop 证据、实际 Worker Diff/Commit/测试，独立 Review、QA 与 EO 结果记录。
- 连续推进、恢复及人工控制证据；局域网功能结果和真实外部节点状态。
- 更新 PROJECT_STATUS.md 和 dashboard/README.md：按新事实标明当前地址、能力及已解决的旧限制，历史证据保留。
- 中文交付报告、必要截图、部署代码 SHA、交付 HEAD，推送现有开发分支或按实际 Git 工作方式提交。不要提交凭据、私有配置、客户数据或未脱敏模型日志；不自动合并 main。
- 实际 execution_evidence 和 environment_evidence 按上述两项 PCP Baseline 完整记录。不可见的非关键字段使用 NOT_EXPOSED_BY_RUNTIME，不把推荐值冒充实际值。

## 9. Execution instructions / 执行纪律

本工单授权在现有 cbnet 开发环境和 Runtime 项目内实施上述工作及原非生产 8787 更新；不授权其他业务生产发布、凭据泄露、破坏性 Git 操作或扩大网络边界。直接调用现有本地 Ruflo/Codex，不经过 CB Bridge，不新增 Gateway/Tunnel。未确认依赖不得猜测接口。

按 P0→P1 推进，同时完成有条件的 P2；不将阶段变成额外人工审批。遇到具体故障直接修复，完成定向验证后继续，禁止只返回计划、审计报告或重复测试。已有 D01 的一次性结果不重新派发，不以旧 Run 28 为全局阻断。不改写 PCP 固定基线或 EO/ES canonical schema/state machine，不重造 scheduler/queue/Worker Pool/Agent Memory。现有接口不支持的跨域动作，指出具体契约差距并完成独立工作。

本工单不是另一轮合成 POC。完成标准是用户可以在原 Dashboard 真实下达可执行工程任务，看到 Ruflo 持续组织工作，最终拿到真实可审查的工程交付。
