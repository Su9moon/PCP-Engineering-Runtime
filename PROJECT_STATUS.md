# Project Status

- Domain ID: `pcp-engineering-runtime`
- Repository: `Su9moon/PCP-Engineering-Runtime`
- Default branch: `main`
- Status: `VERTICAL_POC_LOCAL_WORKER_VERIFIED_REMOTE_AND_GOVERNANCE_ACCEPTANCE_OPEN`
- Ruflo control-plane target: `cbnet` / Ubuntu 24.04 / WSL2
- Execution location: flexible across authorized nodes; do not infer all workers must be on cbnet.

## Ruflo deployment and MCP

- Reused Ruflo `3.80.0`, Node.js `v24.22.3`, and Codex CLI `0.171.0`; no installation repeated.
- Existing CC Switch `happy小任务主流` profile was used via `/home/cbnet/.codex-plus-b` for a real model-only Codex call. No secrets were copied or displayed; persistent Codex/CC Switch configuration was unchanged.
- Codex ephemeral MCP config discovered Ruflo `mcp_status` and made a real call; result: `running=true`, stdio, `port=null`, `host=null`.
- Ruflo `policy status` and `policy verify --full` passed; final verification reported valid ledger length 5 and valid log/mirror anchors. No anchor establishment was attempted.
- Ruflo MCP `mcp_status` succeeded; `agent_list` returned zero agents. `analyze_diff` and `analyze_diff-risk` reported low risk, but do not constitute supervision, semantic approval, or QA.
- Deployment report: `reports/LOCAL-RUFLO-DEPLOYMENT-20261122.md`.

## Existing Vertical POC progress

- Continued `workorders/WO-20261122-001-VERTICAL-POC.md`; no replacement POC or scheduler created.
- Existing isolated pinned Autoloop installation ran Codex Worker Run 2 in a dedicated worktree, producing `b8ac0f81e47b2a3c3e09e0889d799564005da431` (thread `01a206a0-2d1e-7ce1-a2a0-ce3cda1af76a`). Hub and Worker both ran on cbnet WSL; remote execution is not claimed.
- Exact fixture commit received independent read-only Codex review; 8 tests pass in the current main checkout. A separate equivalent implementation commit also exists on main; uncommitted edits in main and Worker worktrees are preserved.
- ES execution is historically DONE and review approved, but the completed Attempt runtime_ref is a placeholder, not the actual Autoloop run ID. ES-provider correlation acceptance is unmet; historical ES state was not altered. EO YAML records are uncommitted drafts only.
- Detailed execution evidence and blockers: `reports/VERTICAL-POC-EXECUTION-20261123.md`.

## Open acceptance prerequisites

1. For correct ES/provider correlation, any redispatch requires a **new** request/Execution and explicit authorization; do not reuse or rewrite the completed historical Attempt. Bind actual Autoloop Run ID at the supported start transition.
2. Remote acceptance requires an independently authorized Worker host and secured, reachable HTTPS Hub route/certificate/trust. Current Hub binds only `127.0.0.1:3350`.
3. Ruflo supervised review and separate Product QA remain uncompleted; heuristic diff analysis is not approval.
4. Validate/finalize EO Result/Evidence/Review with accurate ES, Worker, review, and QA evidence.

No API key, public HTTP service, new scheduler, or provider/account changes were added. CB Green, TaskStore, Windows Codex, and CC Switch configuration remain preserved. Ruflo upstream, Autoloop, ES, and EO source/schema were not modified.
