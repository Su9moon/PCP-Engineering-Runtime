# WO-20261122-001｜Ruflo 本机部署与 Codex MCP 接入

## Identity

```yaml
repository: Su9moon/PCP-Engineering-Runtime
workorder_id: PCP-ER-RUFLO-LOCAL-DEPLOYMENT-01
title: Deploy Ruflo locally on cbnet WSL and connect it to Codex
executor: Codex CLI on WSL Ubuntu-24.04
status: READY_FOR_EXECUTION
priority: P0
authorized_by: user
authorized_date: 2026-11-22
```

## Governing references

Canonical PCP repository: `Su9moon/personal-ai-control-plane`

Pinned PCP source commit: `22bae955686f03c5f440cdcd66e13a69f1289f90`

Read:

- `AGENTS.md`
- `governance/PCP_ENGINEERING_AGILITY_PRINCIPLE.md`
- `governance/baselines/PCP-01_系统定位与核心边界_V0.2_FIXED.md`
- `processes/architecture-governance-gate.md`
- `.agents/skills/pcp-session-bootstrap/SKILL.md`
- `.agents/skills/pcp-experience-reuse/SKILL.md`
- `processes/experience-reuse-gate.md`
- `.agents/skills/cross-domain-discovery/SKILL.md`
- `governance/baselines/PCP_Engineering_Operations_BASELINE.md`
- `governance/baselines/PCP_Execution_Server_BASELINE.md`
- `governance/baselines/PCP_PROJECT_WORKSPACE_IDENTITY_BASELINE_V0.2_FIXED.md`
- `governance/baselines/PCP_PROJECT_WORKSPACE_REGISTRY_GOVERNANCE_V0.1_FIXED.md`
- `governance/adr/ADR-2026-11-22-001_pcp-engineering-runtime.md`

Ruflo upstream:

- Repository: https://github.com/ruvnet/ruflo
- Release: `v3.80.0`
- Source commit: `87f612cef121b50c2e31e2d3f88e46d88963a377`
- License: MIT
- Release notes: https://github.com/ruvnet/ruflo/releases/tag/v3.80.0
- Codex MCP setup: Ruflo README documents a local stdio MCP command for Codex: `npx -y ruflo@latest mcp start`. This workorder pins the version to `3.80.0` instead of floating `latest`.

Autoloop future compatibility:

- PCP fork: `Su9moon/agent-autoloop-pcp`
- Observed HEAD: `f27466d5f0ec9fc6f2f48a1fa68c748581906bdc`
- Its `package.json` declares Node.js `>=24`. Use Node 24 on this shared local execution host if an upgrade is required; do not deploy Autoloop in this workorder.

## Architecture gate

```yaml
architecture_gate:
  required: true
  status: complete
  real_use_evidence: verified
  decision: INTEGRATE
  pcp_specific_remainder: "Ruflo local Supervisor integration while preserving EO Workorder/Result/Evidence and ES Execution/Attempt authority; later Autoloop Provider mapping"
  minimum_formalization: "Install and run upstream Ruflo locally; use its documented Codex stdio MCP entry; no new scheduler, TaskStore, Worker Pool, HTTP service or PCP state machine"
```

The decision is already approved in PCP ADR-2026-11-22-001. This workorder implements the first local deployment step; it does not reopen architecture selection.

## Experience reuse

Classification: `REUSE` + `INTEGRATE`.

Reuse:

- Existing PCP EO / ES authority split and ES Runtime Binding / Provider boundary.
- Existing CB WSL Blue/Green deployment and TaskStore; preserve them unchanged.
- Existing PCP Engineering Agility principle: do not add unnecessary gates, runtimes, schedulers or duplicate stores.
- Existing worktree / Git / PR mechanisms for actual code execution.

Experience status:

- No Ruflo-specific item was found in PCP Validated assets.
- The existing cross-project runtime assessment is research/proposed, not an accepted baseline; the newer user-approved PCP ADR defines the current Ruflo direction.
- Relevant Inbox observations reinforce baseline recall and end-to-end dependency continuity. They do not authorize a new generic recovery mechanism.

## Objective

Deploy Ruflo on the user's **new local WSL execution host** and make its MCP tools callable from the Linux WSL Codex CLI.

Success means:

1. Ruflo CLI `3.80.0` runs locally.
2. Ruflo's stdio MCP server starts successfully under the local Codex CLI.
3. Codex can call Ruflo's read-only health/status tool and receive a real response.
4. The setup uses the existing WSL Codex ChatGPT login; no separate provider API key is introduced.
5. Existing CB Green and its MCP / TaskStore / processes / ports remain unchanged.

This is a local runtime installation and smoke test. The stdio MCP process is started on demand by Codex; this stage proves local Ruflo tool availability, **not yet unattended background scheduling, Autoloop integration or a production execution rollout**.

## Target host — use this environment only

Last confirmed facts:

```yaml
windows_host: Windows 11
wsl_distribution: Ubuntu-24.04
wsl_version: WSL2
linux_user: cbnet
linux_home: /home/cbnet
systemd: running
codex_cli_last_confirmed: 0.162.1
codex_auth_last_confirmed: ChatGPT login works
last_confirmation_date: 2026-11-17
```

Important:

- Node.js / npm versions were not verified in the prior setup. Inspect the actual environment before changing anything.
- This is the new `cbnet` environment, not the older `jjyy` WSL installation.
- The existing CB Green is on this host. It was previously recorded as prepared but not fully activated; do not infer its current liveness and do not try to activate or repair it here.
- The WSL virtual disk is stored under `D:\\0 codex\\wsl\\Ubuntu-24.04\\ext4.vhdx`. Do not move, resize, compact, or otherwise alter the WSL disk.

## Deployment design

### Use MCP-only integration first

Use the official Ruflo Codex MCP path directly:

```bash
npx -y ruflo@3.80.0 mcp start
```

Register it in the WSL Codex CLI as a **stdio MCP server** named `ruflo`.

Do **not** run `ruflo init --codex` in this first deployment. That initializer also installs a user-scope Ruflo plugin and lifecycle hooks. Ruflo upstream ADR-491 specifically flags Codex CLI `0.162.1` as a problematic hook build; the MCP-only path is sufficient to bring up the runtime and avoids enabling hooks before compatibility review.

Do not install or trust `ruflo-core`, `ruflo-mods`, or other Codex plugins in this task. Plugin / hook integration can be considered after the MCP runtime is proven and the Codex hook compatibility is separately established.

### Runtime mode

- Codex launches the Ruflo MCP process on demand for each Codex session.
- The process uses local stdio; it must not bind a TCP port.
- Do not install a systemd service, start a background Ruflo daemon, or expose a network MCP endpoint.
- Do not enable unattended swarm automation or Autopilot workers.
- Do not initialize Ruflo Federation.
- Do not start an agent swarm or create test tasks in Ruflo during this deployment smoke.

### Authority boundaries

- Ruflo may coordinate agents and maintain provider-local coordination / memory evidence.
- Ruflo does not become the canonical PCP Workorder, Execution, Attempt, Result or Evidence store.
- ES remains the only authority for Execution / Attempt / Invocation and retry / recovery decisions.
- EO remains the durable engineering intent / result / evidence / review source.
- Autoloop is not installed or started in this workorder.
- CB is not modified.

## Actions

### A. Confirm the actual WSL environment

Run read-only checks:

```bash
whoami
printf 'HOME=%s\\n' "$HOME"
lsb_release -a
uname -a
systemctl is-system-running
node --version 2>/dev/null || true
npm --version 2>/dev/null || true
command -v node || true
command -v npm || true
command -v npx || true
codex --version
codex login status
```

Confirm:

- user is `cbnet`;
- home is `/home/cbnet`;
- distro is Ubuntu 24.04;
- Codex is the Linux WSL CLI, not Windows Codex Desktop;
- current ChatGPT login is still valid.

Do not read or print auth tokens, API keys, cookies, or credential files.

### B. Bring the local Node runtime to the compatible version

Ruflo requires Node.js 20+; the PCP Autoloop fork planned for the same execution host requires Node.js 24+.

- If Node.js 24 or later and npm 9+ are already available, reuse them.
- If Node.js is below 24, install Node.js 24 using a **user-level NVM installation** for `cbnet`; do not replace Ubuntu system packages or alter Windows Node installations.
- Ensure `node`, `npm`, and `npx` resolve consistently in the shell that launches Codex.
- Record the resolved `npx` executable path; use that exact path in the Codex MCP entry if needed.
- Do not install Rust / Docker / databases / extra services unless the actual Ruflo install reports a concrete required dependency.

### C. Update only the WSL Codex CLI if needed

The last confirmed WSL Codex CLI version was `0.162.1`. OpenAI's official changelog lists `0.171.0` on 2026-11-20.

- If the current WSL Codex CLI is already `0.171.0` or newer, keep it.
- If it is still `0.162.1` or otherwise older than `0.171.0`, update only the WSL Linux CLI to `0.171.0`.
- If it is npm-managed, use:

```bash
npm install -g @openai/codex@0.171.0
```

- If installed through another supported method, use that installation method's normal updater.
- Preserve `/home/cbnet/.codex/auth.json`, `/home/cbnet/.codex/config.toml`, all existing MCP entries, and the separate `~/.codex-plus-b` profile.
- Do not modify Windows Codex Desktop, Windows authentication, CC Switch, or any other machine.
- Re-run `codex --version` and `codex login status` after the update.

### D. Verify and run Ruflo

Use the pinned package:

```bash
npx -y ruflo@3.80.0 --version
npx -y ruflo@3.80.0 doctor
```

Requirements:

- Confirm reported version is `3.80.0`.
- Use `doctor` without `--fix`; do not run automatic repair.
- Do not use `@latest` in the final Codex MCP command.
- If the package download or startup fails, capture the exact error and fix only the concrete dependency/network issue. Do not redesign the runtime.

### E. Register the Ruflo stdio MCP server in WSL Codex

First inspect the existing server list:

```bash
codex mcp list --json
```

Then:

1. Preserve every existing MCP entry, especially the existing CB / Green entry.
2. If a server named `ruflo` already exists and already uses the pinned command, keep it.
3. If `ruflo` is absent, add exactly one entry using the resolved absolute `npx` path:

```bash
codex mcp add ruflo -- <ABSOLUTE_NPX_PATH> -y ruflo@3.80.0 mcp start
```

4. If a `ruflo` entry exists but points to a floating or different version, update only that `ruflo` entry to the pinned command. Do not remove or recreate unrelated MCP servers.
5. In `/home/cbnet/.codex/config.toml`, set the Ruflo section's startup and tool timeouts to 120 seconds if those fields are absent:

```toml
[mcp_servers.ruflo]
command = "<resolved absolute npx path>"
args = ["-y", "ruflo@3.80.0", "mcp", "start"]
enabled = true
startup_timeout_sec = 120
tool_timeout_sec = 120
```

Preserve all other Codex configuration sections and values. Do not copy secrets into the MCP environment.

### F. Verify a real MCP session

- Restart the WSL Codex CLI session so it reloads the MCP configuration.
- Confirm `codex mcp list` shows exactly one enabled `ruflo` entry and all existing MCP entries remain present.
- In a fresh Codex session, verify that Ruflo tools are discoverable.
- Call the read-only `mcp_status` tool and capture its actual response.
- If `guidance_brain` is present, make one read-only recommendation call against the PCP runtime objective; do not create a swarm, agent, task, or workorder in Ruflo during this installation smoke.
- Record the actual tool names returned by the server; do not hardcode a marketing tool count.
- If Codex cannot start the MCP process, inspect the exact stderr / process exit and correct the smallest cause.

### G. Confirm no collateral changes

Read-only compare before/after:

- Existing CB Green process / service state, MCP endpoint and port configuration.
- Existing CB TaskStore path and data file metadata.
- Existing Codex MCP entries other than `ruflo`.
- Windows Codex Desktop / CC Switch configuration must remain untouched.

Do not start, stop, restart, migrate, or repair CB Green. Do not read or expose its tokens.

### H. Record the deployment result

Create:

- `PROJECT_STATUS.md` — concise actual status of Ruflo, Codex MCP, Autoloop (not deployed), EO/ES adapters (not started), and CB (unchanged).
- `reports/LOCAL-RUFLO-DEPLOYMENT-20261122.md` — exact versions, resolved executable paths, commands, doctor summary, MCP tool smoke evidence, and before/after CB preservation evidence.

Do not include:

- tokens, API keys, auth JSON, cookies, environment dumps, or private customer data;
- full Codex configuration containing unrelated secrets;
- private machine-specific data not needed to reproduce the deployment.

Commit the two sanitized project reports to this repository using the repository's normal workflow. Do not commit local `~/.codex` configuration, npm caches, runtime databases, or secrets.

## Validation / acceptance

All of the following must be true:

1. Target environment is the new `cbnet` WSL Ubuntu-24.04, not the old `jjyy` host.
2. Ruflo CLI reports version `3.80.0`.
3. Ruflo `doctor` completes; warnings are reported accurately, not hidden.
4. Codex CLI is `0.171.0` or newer and its existing ChatGPT login still works.
5. Exactly one Ruflo stdio MCP entry is configured in WSL Codex.
6. A fresh Codex session discovers Ruflo tools and receives a real successful `mcp_status` response.
7. No Ruflo HTTP listener, TCP port, systemd service, daemon, Federation, unattended worker or autonomous fanout is started.
8. No new CB Server, CB MCP endpoint, CB TaskStore, Scheduler or Worker Pool is created.
9. Existing CB Green and all non-Ruflo Codex MCP entries remain unchanged.
10. Windows Codex Desktop, CC Switch and `~/.codex-plus-b` remain unchanged.
11. No provider API key is added.
12. Sanitized deployment evidence is committed in this repository.

## Non-goals

- No Autoloop installation or Hub / Worker connection yet.
- No EO / ES adapter implementation or schema change.
- No CB code, service, port, TaskStore or token changes.
- No Ruflo plugin / hooks installation or trust activation.
- No Ruflo Federation.
- No production repository write, push, merge, release or deployment.
- No new PCP canonical state machine, Scheduler, TaskStore, Worker Pool, message bus or governance service.
- No full Ruflo benchmark or broad upstream code audit.

## Stop conditions

Stop only the affected step and continue all independent local setup work if:

- Node / npm installation is blocked by a concrete network or permission error.
- Ruflo `3.80.0` cannot be fetched from npm.
- Codex MCP command syntax differs from the documented interface.
- Codex `mcp_status` fails after the server starts.

Do not interpret an unknown CB runtime state as permission to repair or replace it. Preserve it and report the exact observation.

## Final handoff

Return:

- WSL host identity and actual Node / npm / Codex versions.
- Ruflo version and doctor result.
- Exact Ruflo MCP command and sanitized Codex registration result.
- `mcp_status` result and discovered tool names.
- Confirmation that existing CB Green / TaskStore / MCP and Windows Codex configuration were not modified.
- Commit SHA for `PROJECT_STATUS.md` and deployment report.
- Any precise remaining blocker and the exact next executable step.

Once this workorder passes, the next workorder can connect the local Ruflo Supervisor to the Autoloop Hub / external Workers. Do not begin that integration here.
