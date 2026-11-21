# PCP Project & Workspace Identity Baseline

- Status: **FIXED**
- Version: **V0.1**
- Fixed date: **2026-09-20**
- Scope: PCP cross-domain governance
- Canonical repository: `personal-ai-control-plane`

## 1. Purpose

本 Baseline 定义 PCP 及其下游 Domain 在以下对象之间的统一身份、状态与职责边界：

- Domain
- Remote Git Repository
- Local Git
- Persistent Worktree
- Managed Worktree
- Local Codex Project
- Web GPT Project

目标不是要求所有 Domain 同时创建所有工作环境，而是保证：

1. 所有工具围绕同一个 Domain Identity 工作；
2. 不同工具不会各自产生平行事实源；
3. 本地工程状态、共享正式状态、执行上下文和推理上下文可以明确区分；
4. 新 Domain 可以渐进式建立 Local / Codex / Web 工作环境，而不依赖人工记忆其关系。

---

## 2. Scope

本 Baseline 属于 PCP 顶层跨域治理。

适用于当前及后续 PCP / WPOS 工程 Domain，包括但不限于：

- `personal-ai-control-plane`
- `pcp-execution-server`
- `pcp-engineering-operations`
- `pcp-human-bridge`
- `wpos-domain-business`
- `codex-tools`

本 Baseline 不属于任何单一子域。

子域可以拥有自己的 Workspace、Execution 或 Repository 规则，但不得改变本 Baseline 定义的身份与权威关系。

---

## 3. Core Model

统一模型：

```text
                    Domain Identity
                          │
                          ▼
                   Remote Git Repo
                Shared Canonical State
                          │
                       fetch/pull
                          ▼
                      Local Git
                Local Recorded State
                          │
             ┌────────────┴────────────┐
             │                         │
             ▼                         ▼
   Persistent Worktree          Managed Worktree
    Stable Workspace           Execution Workspace
             │
             ▼
     Local Codex Project
      Execution Context


Web GPT Project
= Reasoning / Planning / Review Context
```

所有对象围绕同一个 Domain Identity 工作。

它们不是多个独立事实源。

---

## 4. Domain Identity

Domain 是最高层逻辑身份。

每个正式 Domain 应具有稳定的：

```text
domain_id
```

通常与其 canonical Git Repository 对应。

Domain Identity 用于关联：

- Remote Git
- Local Git
- Persistent Workspace
- Codex Project
- Web GPT Project
- Execution Workspace

Domain Identity 本身不依赖某一个客户端、电脑或 AI 产品存在。

---

## 5. Remote Git

Remote Git Repository 是当前 PCP 工程体系的共享事实载体。

默认情况下：

```text
Remote Git Canonical Branch
=
Shared Canonical State
```

例如正式 `main` 分支中的：

- Baseline
- Governance
- Architecture
- Contract
- Schema
- AGENTS
- Canonical Skill
- 正式代码
- 正式提交的 Workorder / Evidence
- Version History

构成其他 Agent、机器和入口共同读取的正式状态。

### 5.1 Canonical Promotion

信息从讨论状态升级为正式事实，应经过类似过程：

```text
Discussion
    ↓
Candidate Change
    ↓
Local Commit
    ↓
Push / Merge
    ↓
Remote Canonical
```

聊天中确认的内容，在正式生成对应文件并进入 Remote Git canonical branch 前，不自动成为共享事实。

---

## 6. Local Git

Local Git 表示本机工程记录状态。

它不是新的共享事实源。

状态区分：

```text
Working Tree
= Candidate Change

Local Commit
= Local Recorded State

Remote Canonical Commit
= Shared Canonical State
```

因此，本地已经 commit，不等于其他 Web GPT、Worker 或其他机器已经可以将其视为当前正式状态。

---

## 7. Local Workspace Layout

PCP 本地工程根遵循：

```text
F:\0 codex
```

标准结构：

```text
F:\0 codex\
│
├─ git-meta\
│  └─ <repo>.git
│
├─ worktrees\
│  ├─ persistent\
│  │  └─ <repo>\
│  │
│  └─ managed\
│     └─ <execution-worktree>\
│
└─ no-project-tasks\
```

### 7.1 git-meta

```text
F:\0 codex\git-meta\<repo>.git
```

职责：

- 保存本机 Git repository metadata；
- 为 persistent / managed worktree 提供共同 repository identity；
- 不作为日常编辑工作目录。

### 7.2 Persistent Worktree

```text
F:\0 codex\worktrees\persistent\<repo>
```

定义：

```text
Stable Local Workspace
```

职责：

- Domain 的长期本地工作空间；
- Human 的稳定工程入口；
- Local Codex Project 的默认项目根；
- 保存长期存在的 checkout。

推荐关系：

```text
1 active Git Repo
≈
1 Primary Persistent Worktree
≈
1 Primary Local Codex Project
```

该关系是推荐路径，不是对所有 Repository 的强制要求。

### 7.3 Managed Worktree

```text
F:\0 codex\worktrees\managed\<execution>
```

定义：

```text
Per-execution Workspace
```

用于：

- 单次任务；
- 隔离修改；
- Codex 临时执行；
- Execution Server 后续调度。

Managed Worktree：

- 不拥有新的 Domain Identity；
- 不成为长期项目入口；
- 不成为 canonical truth；
- 可以根据执行生命周期创建或销毁。

---

## 8. Local Codex Project

Local Codex Project 定义为：

```text
Execution Context
```

主要负责：

- 读取 Repository；
- 读取 `AGENTS.md`；
- 使用 Skills；
- 修改代码或文档；
- 执行测试；
- 产生 Diff；
- 产生 Result / Evidence；
- Commit / Push。

对于需要持续工程工作的 Domain，推荐：

```text
Codex Project Root
=
Persistent Worktree Root
```

Codex Project 本身不是事实源。

以下内容不能替代 Git：

- Codex Chat；
- Codex 当前线程上下文；
- Codex Runtime State；
- Managed Worktree 中未提交修改。

---

## 9. Web GPT Project

Web GPT Project 定义为：

```text
Reasoning / Planning / Review Context
```

主要负责：

- 长期讨论；
- 架构推理；
- 方案比较；
- 决策过程；
- Workorder 准备；
- Review；
- 上下文连续性。

Web GPT Project 不拥有 canonical state。

### 9.1 Web Project Boundary

Web GPT Project 应按照持续讨论与决策边界建立，而不机械要求：

```text
1 Git Repo
=
1 Web GPT Project
```

对于当前长期活跃、边界明确的 Domain，可以采用近似一一对应。

后续新建 Repository 是否需要单独 Web Project，应根据实际持续讨论需求决定。

---

## 10. Web GPT Memory

Web GPT Project Memory 与聊天记录仅用于：

```text
Conversation Continuity
```

可以帮助：

- 恢复历史讨论；
- 理解设计原因；
- 减少重复背景说明。

不得单独作为以下问题的权威答案：

- 当前 Baseline 是什么；
- 当前 Schema 是什么；
- 当前接口是什么；
- 当前正式代码是什么；
- 当前 Git 状态是什么；
- 当前 Issue / Workorder 正式状态是什么。

遇到此类问题，应回到对应 Remote Git canonical source。

---

## 11. Authority Levels

### Level 1 — Shared Canonical State

```text
Remote Git
Canonical Branch
```

所有 Agent / Machine / Web GPT 应共同认可的正式状态。

### Level 2 — Local Recorded State

```text
Local Git Commit
Not Yet Published
```

已经记录，但尚未成为共享正式状态。

### Level 3 — Working State

```text
Persistent Worktree
Managed Worktree
Staging Area
Uncommitted Diff
```

正在工作的候选变化。

### Level 4 — Reasoning / Execution Context

```text
Web GPT Chat
Web GPT Project Memory
Codex Chat
Codex Runtime State
```

用于推理、规划和执行，不能独立升级为正式事实。

---

## 12. Progressive Provisioning

建立新 Domain 时，不要求一次性创建所有工作环境。

基础要求是：

```text
Domain Identity
+
Remote Git Repository
+
Canonical Rules
```

其他能力按需要渐进建立。

### Local Workspace

当首次需要长期本地工程工作时建立。

### Codex Project

当首次需要持续 Codex 工程上下文时建立。

### Web GPT Project

当该 Domain 开始产生持续、独立的讨论与 Review 上下文时建立。

因此以下状态是允许的：

```text
Git:        READY
Local:      NOT_INITIALIZED
Codex:      NOT_INITIALIZED
Web GPT:    NOT_REQUIRED
```

这不是错误状态。

---

## 13. Registry

PCP 可以维护轻量 Project / Workspace Registry，用于避免依赖人工记忆。

Registry 的职责是：

```text
Discovery / Mapping / Reminder
```

而不是：

```text
Hard Bootstrap Gate
```

建议记录最小信息：

```yaml
domain_id:

remote_git:
  repository:
  canonical_branch:

local:
  git_metadata:
  persistent_workspace:
  status:

codex:
  project:
  status:

web_gpt:
  project:
  status:
```

状态可以包括：

```text
ready
not_initialized
not_required
deprecated
```

Registry 记录项目工作表面是否存在，不拥有各 Domain 的业务事实。

---

## 14. Execution Relationship

未来 PCP EO / ES 进入正式执行链路后，应通过 Domain Identity 解析工作空间。

逻辑关系：

```text
domain_id
    ↓
Remote Repository Identity
    ↓
Local Repository Identity
    ↓
Persistent Workspace
    ↓
ExecutionRequest
    ↓
Managed Worktree
    ↓
Executor
```

临时本地路径、Codex-specific runtime details 等不得提升为 PCP canonical semantics。

---

## 15. Current Recommended Mapping

当前活跃 Domain：

```text
personal-ai-control-plane
pcp-execution-server
pcp-engineering-operations
pcp-human-bridge
wpos-domain-business
codex-tools
```

对于前五个长期活跃 Domain：

```text
Remote Git       → Required
Persistent       → Recommended
Codex Project    → Recommended
Web GPT Project  → Recommended
```

`codex-tools`：

```text
Remote Git       → Required
Persistent       → Recommended
Codex Project    → Recommended
Web GPT Project  → Optional / Based on ongoing reasoning needs
```

---

## 16. Operating Principle

开始处理一个已有工程 Domain 前，优先确认：

```text
Which Domain?
      ↓
Which Remote Git?
      ↓
What is current canonical state?
      ↓
Is local workspace needed?
      ↓
Is Codex execution needed?
      ↓
Is persistent Web reasoning context needed?
```

工具和 Workspace 应服务于 Domain，而不是反过来定义 Domain。

---

## 17. Final Model

最终固定：

```text
Remote Git
= Shared Canonical State

Local Git
= Local Recorded State

Persistent Worktree
= Stable Local Workspace

Managed Worktree
= Per-execution Working State

Local Codex Project
= Execution Context

Web GPT Project
= Reasoning / Planning / Review Context
```

所有工作表面围绕同一 Domain Identity 工作。

PCP 不允许 Web GPT、Codex、本地 Workspace 或临时运行态形成新的平行事实源。
