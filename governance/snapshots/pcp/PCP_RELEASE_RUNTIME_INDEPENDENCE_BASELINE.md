# PCP Release / Runtime Independence Baseline

- Status: **FIXED**
- Version: **V0.1**
- Fixed date: **2026-09-22**
- Scope: PCP cross-domain architecture/governance
- Source ADR: `governance/adr/ADR-2026-09-22-002_runtime-independence-from-governance-plane.md`

## 1. Purpose

本 Baseline 固定 PCP 及下游 Domain 在以下阶段之间的权威与依赖边界：

```text
Govern / Build
    ↓
Release
    ↓
Deploy / Initialize
    ↓
Run
```

目标：

1. 生产 Runtime 不依赖工程治理环境才能成立；
2. Runtime 使用已批准 Installed Release，而不是实时读取上游 repo；
3. Release 可追溯到 Git canonical；
4. Runtime 外部连接要求显式声明；
5. 支持第三方/独立部署；
6. 不引入通用 Release 平台。

## 2. Authority Model

### 2.1 Governance / Build Authority

Git canonical 与已批准工程治理回答：

> “这个产品/能力应该被构建成什么？”

包括：

- Baseline；
- Architecture；
- Schema；
- Skill；
- Tool；
- Operator Policy；
- Implementation；
- Tests；
- Workorder；
- Release definition。

### 2.2 Release Authority

Approved Release 回答：

> “这一版被批准部署的产品到底包含什么？”

Release 是从已批准 Build/Governance 输入产生的不可变部署单元。

每个 Release 必须具备唯一 Release Identity。

### 2.3 Runtime Authority

Installed Release 回答：

> “当前这个生产环境按哪一版规则和能力运行？”

Runtime 默认依赖：

- Installed Release；
- 当前生产配置；
- 当前生产数据；
- 声明的 Runtime 外部能力。

Runtime 默认不依赖：

- 原始 PCP repo；
- 原始 Domain repo；
- 开发者 persistent worktree；
- GitHub Issue/PR；
- Architecture Gate；
- 工程 Codex Project。

## 3. Build / Release / Run Separation

固定：

```text
Engineering Canonical
      ↓ build
Release Artifact
      ↓ deploy
Installed Release
      ↓ run
Production Runtime
```

规则：

- Runtime 不在运行时重新构建自身治理；
- Runtime 不从聊天恢复 Release；
- Runtime 不以“上游 main 当前内容”覆盖已安装 Release；
- 上游发生变更不会自动改变正在运行的生产环境；
- 变更必须形成新 Release，再明确部署。

## 4. Release Identity

最小 Release Identity：

```yaml
release:
  release_id:
  domain_id:
  product_id:
  version:
  built_from:
    repository:
    commit:
  created_at:
```

Release ID 必须足以区分不同批准发布版本。

## 5. Artifact Provenance and Integrity

Release Manifest 至少记录：

```yaml
artifacts:
  - role:
    source:
    target:
    sha256:
```

要求：

- Release Artifact 可追溯到 source repo/path/commit；
- 部署后可以验证 target digest；
- Production local edits 不自动成为新 Release；
- 需要改变受管控 Artifact 时，应回到 Engineering/Governance 形成新 Release。

无需引入签名基础设施才能满足 V0.1；SHA256 + exact source provenance 即可。

## 6. Connectivity Contract

每个可部署/可运行单元必须声明 Connectivity Contract。

### 6.1 AI / LLM connectivity

```yaml
llm_connectivity:
  mode: required | optional | none
  behavior_when_unavailable:
```

`required` 表示无 LLM 时该 AI Runtime 不可正常执行。

PCP V0.1 不要求本地 LLM fallback。

### 6.2 Governance connectivity

```yaml
governance_connectivity:
  runtime: required | not_required
  update: required | package_supported | none
```

生产产品推荐：

```yaml
governance_connectivity:
  runtime: not_required
  update: package_supported
```

含义：

- 日常 Runtime 不连接 Governance Plane 也能工作；
- 升级既可通过连接 Governance Plane，也可导入已批准 Release Package。

### 6.3 External service connectivity

产品/API/Connector 依赖按需要声明：

```yaml
external_services:
  - capability:
    requirement: required | optional
    behavior_when_unavailable:
```

Provider-specific 细节保留在产品/Adapter 层。

## 7. Connectivity Failure Semantics

连接不可用时必须区分：

- `RUNTIME_DEPENDENCY_UNAVAILABLE`
- `GOVERNANCE_PLANE_UNAVAILABLE`
- `OPTIONAL_CAPABILITY_UNAVAILABLE`

如果 `llm_connectivity = required`，LLM 不可用可以阻塞 AI 业务操作。

如果 `governance_connectivity.runtime = not_required`，GitHub / PCP / Domain repo 不可达不得阻塞正常 Runtime。

## 8. Production Initialization

Production Initialization 应消费：

- local approved Release Package；
- 或已被明确部署到目标环境的 Release Artifact。

初始化不应要求目标生产目录本身是 Git worktree。

初始化可：

- 验证 Release Manifest；
- 恢复受管控配置；
- 校验 hash；
- 检查生产数据兼容性；
- 生成 Runtime/Data Baseline；
- 记录 Installed Release。

初始化不得：

- 根据聊天重建 Release；
- 因上游 repo 不可达而否定一个完整本地 Release；
- 默认重置生产数据；
- 把 Governance workspace 变成 Production workspace。

## 9. Upgrade

Upgrade：

```text
Approved New Release
  ↓
Compatibility / Migration check
  ↓
Production deployment gate
  ↓
Install
  ↓
Verify
  ↓
Current Installed Release changes
```

上游 Git 变更本身不是生产升级。

## 10. Rollback

Rollback 应以已批准历史 Release 为单位。

V0.1 不规定自动 rollback manager。

最小要求：

- 能识别上一 Installed Release；
- 能获得其 Release Package/Artifact；
- 能识别数据 migration 是否可逆；
- 不把 checkout 任意旧 commit 等同于生产 rollback。

## 11. Production Runtime Workspace

Production Runtime Workspace 是新的正式 Workspace Surface：

```text
Production Runtime Workspace
= installed product/runtime + live production data
```

它：

- 不等于 persistent Git worktree；
- 不等于 managed worktree；
- 不等于 Local Codex engineering project；
- 可以使用 Codex / Agent 作为 Runtime Executor；
- 可以完全没有 Git metadata；
- 通过 Installed Release Identity 关联上游产品版本。

## 12. Third-party Runtime

第三方 Runtime 可以只获得：

- Release Package；
- deployment/init instructions；
- runtime dependencies；
- product-specific configuration；
- 自己的生产数据。

它不需要获得：

- 原始 PCP repo；
- Domain engineering repo；
- developer GitHub credentials；
- Issue/PR history；
- PCP engineering project layout。

## 13. Engineering Domain Snapshot Boundary

`pcp-domain-bootstrap` 中的 upstream governance snapshot 仍用于：

> 下游 Domain 的自主工程治理。

Production Release 用于：

> 产品/Runtime 的部署和运行。

二者不得混用。

## 14. Workorder Rule

普通工程 Workorder 不需要增加 Connectivity Contract。

以下 Workorder 必须明确引用/声明：

- release build；
- production deployment；
- production initialization；
- runtime packaging；
- runtime capability whose behavior changes with connectivity。

这避免把 Runtime dependency governance 扩散到所有普通工程任务。

## 15. Minimum Release Manifest

使用：

`governance/templates/PCP_RELEASE_MANIFEST_TEMPLATE.yaml`

Domain 可以扩展字段，但不得弱化：

- source provenance；
- artifact digest；
- connectivity contract；
- runtime authority；
- compatibility identity。

## 16. Non-goals

本 Baseline 不创建：

- release service；
- artifact registry；
- package manager；
- update daemon；
- deployment orchestrator；
- local LLM；
- generic runtime dependency manager。

## 17. Adoption Rule

新的可部署 Runtime 从本 Baseline 固定后开始遵循。

现有项目不要求立即批量重构；在下一次真实 Release / Deployment / Initialization 时对齐。

## 18. Fixed Principles

1. Git canonical 是 Build / Engineering Authority。
2. Approved Release 是 Deployment Authority。
3. Installed Release 是 Production Runtime Authority。
4. Production Runtime 默认不依赖 Governance Plane 实时可达。
5. LLM Connectivity 与 Governance Connectivity 是不同维度。
6. Offline local-LLM execution 不是 PCP 当前通用要求。
7. Runtime Workspace 不要求是 Git worktree。
8. 上游变化必须先变成新 Release，不能直接改变 Runtime。
9. Release 必须具备 provenance + digest。
10. 第三方部署不得要求访问开发者 PCP 工程环境。
