# PCP-01｜系统定位与核心边界

**文档状态：FIXED**  
**版本：V0.2**  
**固定日期：2026-08-18**  
**所属项目：Personal AI Control Plane（PCP）**  
**继承基线：PCP-01 / V0.1 / FIXED（2026-08-10）**  
**本次变更来源：ADR-2026-08-18-001｜Cross-Domain Discovery Gate**  
**变更规则：后续如需修改本文件中的顶层原则，必须通过新的 ADR / Change Request，经用户确认后升级版本；不得由 Codex、WorkBuddy 或其他 Agent 自行修改。**

---

## 1. PCP 的正式定位

**Personal AI Control Plane（PCP）是用户自主管理的长期数字信息、状态、关系与行动控制面。**

PCP 的目标不是再造一个普通任务管理器、知识库、文件管理器或 AI 助手，而是在不同系统之间建立一个由用户长期掌控的统一事实层和控制层。

PCP 可以覆盖：

- 工作与商业项目；
- AI 工程与开发能力建设；
- 学习与知识沉淀；
- 内容与个人品牌；
- 游戏与兴趣项目；
- 家庭；
- 育儿；
- 健康；
- 个人财务；
- 日常生活；
- 未来新增的其他长期领域。

这些内容进入同一个 PCP，但通过 **Area、权限、敏感度、关系和生命周期** 进行组织与隔离。

### 1.1 PCP 不是什么

PCP 不是：

- 单纯的项目管理系统；
- 单纯的 TODO 系统；
- 单纯的知识库；
- 单纯的 RAG 系统；
- 单纯的 AI Memory；
- Git 的替代品；
- OneDrive 的替代品；
- ChatGPT / Codex / WorkBuddy 的替代品；
- 要求所有资料迁移进去的新文件系统。

PCP 的职责是：

> **知道“有什么、是什么、在哪里、当前什么状态、与什么有关、谁产生或确认、下一步如何行动”。**

---

## 2. 用户是最终决策权威

PCP 的最高权威不是 ChatGPT、Codex、WorkBuddy，也不是任何未来 AI Agent。

**用户是最终决策 Authority。**

正式权威链如下：

```text
用户
│
│ 最终批准 / 否决
▼
ChatGPT
│
│ 设计 / 分析 / 方案 / 复核
▼
用户批准后的设计
│
▼
Git Approved Baseline / ADR / Task
│
▼
Codex
工程实施 / 测试 / 版本提交
```

因此：

- ChatGPT 可以提出架构方案，但不能单独改变已批准架构；
- Codex 可以提出工程风险和 Change Request，但不能自行改顶层设计；
- WorkBuddy 可以执行自动化和国内生态接口动作，但不能成为最终事实裁决者；
- 某次新的 AI 对话与既有 Baseline 冲突时，以 **Git 中最新、经用户批准的 Baseline / ADR** 为准。

---

## 3. PCP 的五层结构

PCP 固定采用以下五层认知模型：

```text
┌──────────────────────────────────────────────┐
│ 1. 用户决策层                                │
│    User — 最终决策、批准、否决               │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│ 2. AI 交互层                                 │
│    ChatGPT / 其他 AI                         │
│    设计、分析、判断、复核                    │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│ 3. Personal AI Control Plane                 │
│    状态、关系、规则、索引、策略              │
└───────────────┬──────────────┬───────────────┘
                │              │
        ┌───────▼──────┐ ┌────▼────────┐ ┌────▼────────┐
        │ PostgreSQL   │ │ File Store  │ │ Git         │
        │ 结构化事实源 │ │ 文件事实源  │ │ 工程版本源  │
        └──────────────┘ └─────────────┘ └────┬────────┘
                                              │
                                              ▼
┌──────────────────────────────────────────────┐
│ 5. 执行 / 集成层                             │
│    Codex / WorkBuddy / 企业微信 / Agent      │
└──────────────────────────────────────────────┘
```

其中：

- AI 层可以替换；
- 执行 Agent 可以替换；
- 文件存储 Provider 可以替换；
- 核心数据和控制权必须长期属于用户。

---

## 4. 三类核心事实源

PCP 不要求所有内容都塞进同一个数据库。

不同类型的数据分别由最适合的系统承担权威事实源。

---

## 4.1 PostgreSQL：结构化运行事实源

PostgreSQL 回答：

> **“现在是什么状态？”**

主要保存：

- Area；
- Project；
- Person；
- Item；
- Event；
- Decision；
- Knowledge 元数据；
- Artifact 元数据；
- Source；
- Relation；
- 状态；
- 优先级；
- L1 / L2 / L3 层级；
- 生命周期；
- sensitivity；
- provenance；
- Actor / Agent 信息；
- 时间线；
- 文件定位信息；
- 自动化运行需要的结构化信息。

示例：

```text
Project: BWE V3
Layer: L1
Area: 游戏
Status: active
Priority: P2

Recent Event:
Git baseline verified

Next:
进入当前批准阶段
```

对于生活场景：

```text
Person: 孩子A
Area: 育儿

Event:
家长会

Sensitivity:
S2

Provenance:
user_confirmed
```

### PostgreSQL 不负责

- 保存大型 PDF / Office / 图片文件本体；
- 保存 Git commit 历史；
- 把聊天全文作为唯一事实；
- 替代 OneDrive / NAS / S3 等文件存储。

---

## 4.2 文件事实源：当前首选 OneDrive，但 Provider 可替换

当前阶段：

**OneDrive 是主要文件事实源。**

保存：

- PDF；
- Word；
- Excel；
- PowerPoint；
- 图片；
- 合同；
- 商务资料；
- 项目资料；
- 家庭资料；
- 育儿资料；
- 健康资料；
- 其他长期文件本体。

但 PCP 顶层模型不得把 OneDrive 写死成不可替换组件。

正式抽象为：

```text
Artifact
│
└── Storage Location
    ├── provider = onedrive
    ├── provider = local
    ├── provider = nas
    ├── provider = s3
    └── provider = future
```

因此数据库建议记录：

```text
storage_provider
locator / path
artifact_type
owner / related_entity
sensitivity
provenance
```

而不是让大量业务模型直接依赖：

```text
onedrive_path
```

### 原则

> **SQL 知道文件“是什么、属于谁、在哪里”。**  
> **文件存储系统保存文件“本身”。**

当前实际使用 OneDrive，不影响以后增加 NAS、S3 或其他 Provider。

---

## 4.3 Git：工程设计、代码与版本事实源

Git 回答：

> **“工程设计和实现是怎么演进的？”**

Git 保存：

- Approved Architecture；
- Baseline；
- ADR；
- Change Request；
- Task / 工单；
- Handoff；
- 源代码；
- Schema / Migration；
- Tests；
- PROJECT_STATUS；
- 实施报告；
- Release；
- Commit 历史；
- 回滚点。

例如：

```text
Baseline V0.1
↓
PCP-R1 Approved
↓
Codex implementation
↓
Tests
↓
PCP-R1 RESULT
↓
GPT Review
↓
下一轮批准
```

### Git 不负责

Git 不作为：

- 实时业务数据库；
- PostgreSQL 的替代；
- OneDrive 的替代；
- AI 与 Agent 的实时消息总线；
- 运行中的个人数据存储。

例如：

```text
“PCP-R1 当时批准的设计是什么？”
→ Git 权威
```

而：

```text
“BWE 当前 priority 是多少？”
→ PostgreSQL 权威
```

### Git 的正式角色

> **Git = 已批准工程状态 + 工程账本 + 版本历史。**

---

## 5. ChatGPT、Codex、WorkBuddy 的固定边界

---

## 5.1 ChatGPT

定位：

**Design / Reasoning / Review Interface**

负责：

- 问题定义；
- 顶层架构设计；
- 方案比较；
- 工单设计；
- 数据模型设计；
- 风险分析；
- Codex 结果复核；
- 下一轮设计。

ChatGPT 不是：

- 永久数据库；
- 文件事实源；
- 自动获得最终决策权的 Authority；
- 唯一历史记录。

关键设计一旦获用户批准，应固化到 Git。

---

## 5.2 Codex

定位：

**Engineering Executor**

负责：

- 按批准工单实施；
- 编码；
- 测试；
- Migration；
- Docker / Deployment；
- Git commit；
- PROJECT_STATUS；
- 实施结果回传；
- 技术风险和 Change Request。

Codex 不负责：

- 自行修改顶层架构；
- 自行扩大 Scope；
- 自行决定战略优先级；
- 自行进入下一轮。

---

## 5.3 WorkBuddy

定位：

**China Integration / Automation Agent**

主要价值：

- 企业微信；
- 微信相关生态；
- 腾讯生态；
- 国内 SaaS；
- 本地文件操作；
- 自动化任务；
- 国内 Connector / MCP / API 集成。

已确认：

**企业微信自动化出口已经过实际测试，可作为后续正式通道。**

WorkBuddy 不是：

- PCP 核心数据库；
- 最终事实源；
- 所有敏感数据的默认读取者；
- 不可替换平台。

原则：

> **WB 可以“看”和“做”，但不成为唯一的“存”。**

---

## 6. Vendor Independence：厂商解耦

PCP 必须允许未来替换：

```text
ChatGPT → 其他模型 / AI
Codex → 其他 Coding Agent
WorkBuddy → 其他国内 Agent
OneDrive → NAS / S3 / 其他文件平台
```

替换任何一个外围系统时：

- PostgreSQL 中的核心状态仍存在；
- Git 中的架构和版本仍存在；
- 文件资产仍可迁移；
- PCP 的核心关系模型不需要重构。

---

## 7. Exit / Portability：可退出和可迁移

“数据属于用户”必须落实为技术能力。

PCP 长期必须支持：

- PostgreSQL Backup / Restore；
- JSON / YAML / CSV 等开放格式导出；
- Git 仓库完整 clone / archive；
- 文件系统独立于 PCP 可直接读取；
- Storage Provider 可迁移；
- 不依赖某个 AI 平台才能理解数据。

原则：

> **即使 PCP 软件停止维护，用户仍能恢复、读取、迁移自己的核心数据。**

---

## 8. 总进度管家的定位

总进度管家不是 PCP 本体。

它是运行在 PCP 上面的：

**Portfolio / Decision 子系统。**

它主要回答：

- 当前最重要的事情是什么；
- L1 / L2 / L3 各有哪些活跃事项；
- 哪些事情存在阻塞；
- 下一步行动是什么；
- 资源应该放在哪里；
- 哪些事项应该暂停、归档或重新激活。

不是所有进入 PCP 的信息都进入总进度管家。

例如：

```text
孩子第一次骑自行车
```

可以是值得保存的 Event，

但不必进入：

```text
今日 P0 / P1 / P2 总盘
```

---

## 9. 工作、生活与育儿统一进入 PCP

PCP 不拆分“工作系统”和“生活系统”。

长期领域使用 Area 表达，例如：

```text
Area
├── 通信
├── AI工程
├── 内容
├── 游戏
├── 家庭
├── 育儿
├── 健康
├── 财务
└── 生活
```

而具体有结束结果的事情再成为 Project。

例如：

```text
Area: 育儿

Person:
孩子A

Project:
幼儿园选择

Event:
体检
家长会

Item:
预约疫苗

Artifact:
体检报告.pdf

Decision:
是否报名某兴趣班
```

因此：

> **育儿是长期 Area，不是一个永远做不完的 Project。**

---

## 10. 一个完整运行示例

用户说：

> “孩子下周四家长会，帮我记一下。”

未来可形成：

```text
User
↓
ChatGPT / 企业微信
↓
PCP API
↓
PostgreSQL

Person = 孩子A
Area = 育儿
Event = 家长会
Date = ...
Sensitivity = S2
Provenance = user_confirmed
```

如果还有学校通知：

```text
Artifact
↓
Storage Location
provider = onedrive
locator = ...
```

数据库建立：

```text
Event
家长会
↓
Relation
↓
Artifact
学校通知
```

之后：

```text
PCP
↓
WorkBuddy
↓
企业微信
↓
提醒
```

即使 WorkBuddy 停止使用：

- Event 仍在 SQL；
- 文件仍在 OneDrive；
- 关系仍在 PCP；
- 历史架构仍在 Git。

---

## 11. Cross-Domain Discovery Gate｜跨域解空间扫描门

### 11.1 原则

PCP 在新增核心抽象、通用机制或长期基础设施之前，不应仅依据当前项目内部推演形成方案。

应先把具体问题从当前业务语境中抽象为结构性问题，再检查现有产品、开源项目、论文和其他领域中是否已经存在成熟解法。

正式采用：

> **Problem First, Domain Second：先按问题结构搜索，再按行业标签搜索。**

外部解空间扫描至少覆盖三个层级：

1. **Direct Analog（直接同类）**：与当前问题属于同一产品或技术类别的现有方案；
2. **Adjacent Domain（相邻领域）**：长期处理类似问题的成熟计算机、工程或业务领域；
3. **Structural Analog（结构同构领域）**：表面场景不同，但问题结构、约束、反馈和风险模型高度相似的领域。

### 11.2 触发条件

Cross-Domain Discovery Gate 不是普通任务的前置流程。

以下情况原则上必须触发：

- 新增 PCP Core 概念；
- 准备新增通用 `Engine / Manager / Store / Router` 等抽象；
- 同一类问题已经重复出现并准备长期固化；
- 准备建设多项目复用的长期基础设施；
- 明显出现“可能需要自己造一个通用轮子”的判断；
- 涉及 Memory / Agent / Learning / Governance / State / Evidence 等长期通用机制。

以下情况默认不触发：

- 修复明确 Bug；
- 已知模式的小功能；
- 普通工单；
- 已批准设计范围内的常规实现。

### 11.3 外部方案决策口径

扫描结束后，不以“找到了多少项目”为结果，而必须形成以下之一：

- **REUSE**：直接使用已有实现；
- **INTEGRATE**：通过接口接入已有系统；
- **BORROW**：不引入系统本体，仅借用成熟机制、设计模式或治理方法；
- **BUILD**：确认现有方案不能满足 PCP 的真实剩余问题后自行建设；
- **DEFER**：当前价值、成熟度或需求不足，延后建设。

扫描最终必须回答：

> **真正剩下的、必须由 PCP 自己解决的问题是什么？**

### 11.4 PCP Core 边界保护

跨域发现用于校正和补强 PCP，不自动扩大 PCP Core。

不得因为发现一个优秀外部项目或机制，就默认把其：

- Agent Runtime；
- Learning Engine；
- Memory Engine；
- Research Engine；
- Workflow Runtime；
- 其他完整基础设施

复制进 PCP。

优先顺序为：

```text
Reuse
↓
Integrate
↓
Borrow
↓
Build only the PCP-specific remainder
↓
Defer when not justified
```

### 11.5 最小记录要求

需要触发本 Gate 的重要架构决策，应至少记录：

```text
Cross-Domain Scan: required / waived / complete

Direct Analog: reviewed / not reviewed
Adjacent Domain: reviewed / not reviewed
Structural Analog: reviewed / not reviewed

Decision: REUSE / INTEGRATE / BORROW / BUILD / DEFER
PCP-specific remainder: ...
```

该记录是治理检查项，不要求新增数据库、Discovery Engine、Knowledge Graph、Research Router 或其他运行时模块。

---

## 12. PCP-01 最终固定原则

本设计块正式固定如下：

1. **PCP 是统一的个人长期数字控制面。**
2. **工作、学习、生活、家庭、育儿等进入同一个 PCP。**
3. **用户是最终决策 Authority。**
4. **ChatGPT 是设计、分析和复核工具。**
5. **Git 中用户批准的 Baseline / ADR 是当前工程设计权威。**
6. **Codex 是工程执行者。**
7. **WorkBuddy 是国内接口与自动化执行层。**
8. **PostgreSQL 是结构化运行事实源。**
9. **文件本体由独立 Storage Provider 保存，当前主 Provider 为 OneDrive。**
10. **Git 是架构、工单、代码、实施结果和版本历史事实源。**
11. **Git 不是实时业务数据库，也不是实时消息总线。**
12. **任何 AI / Agent 都不能成为唯一长期事实源。**
13. **系统必须支持厂商替换。**
14. **系统必须支持数据导出、恢复和退出。**
15. **总进度管家是 PCP 上层 Portfolio 子系统，不是 PCP 本体。**
16. **关键状态不得只存在于聊天记录。**
17. **在创造通用机制之前，先把问题从当前业务语境中抽象出来，扫描 Direct Analog、Adjacent Domain 与 Structural Analog。**
18. **外部方案统一按 REUSE / INTEGRATE / BORROW / BUILD / DEFER 判断，只有真正属于 PCP 的剩余问题才自行建设。**
19. **外部发现用于校正和补强 PCP，不因发现新机制而自动扩大 PCP Core。**
20. **Cross-Domain Discovery Gate 是重要架构决策的治理检查项，不是新的 PCP 运行时模块。**

---

## 13. FIXED 声明

本文件自 **2026-08-18** 起标记为：

**PCP-01 / V0.2 / FIXED**

本版本在保留 PCP-01 / V0.1 原有核心边界的基础上，新增 Cross-Domain Discovery Gate。后续 R1 以及所有子系统设计均必须遵循本文件。

如需修改：

```text
发现问题
↓
提出 ADR / Change Request
↓
ChatGPT 分析
↓
用户确认
↓
产生新版本
↓
Git 固化
```

未经以上流程，不修改本设计块。
