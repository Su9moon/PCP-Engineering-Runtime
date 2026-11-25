# Project Status

- Domain ID: `pcp-engineering-runtime`
- Repository: `Su9moon/PCP-Engineering-Runtime`
- Default branch: `main`
- Status: `VERTICAL_POC_LOCAL_WORKER_VERIFIED_REMOTE_AND_GOVERNANCE_ACCEPTANCE_OPEN`
- Ruflo control-plane target: `cbnet` / Ubuntu 24.04 / WSL2
- Execution location: flexible across authorized nodes; do not infer all workers must be on cbnet.

## Dashboard V1.1 conversational intake

- WO-20261126-001 is deployed on the existing pcp-dashboard-v1.service over https://127.0.0.1:8787/ and https://192.168.5.4:8787/. Both endpoints returned HTTP 200 without a login from cbnet WSL. Edge on cbnet verified task-entry navigation. An independent MEC-device test remains open.
- The task action opens a free-text intake with an editable, provenance-labelled dossier and resumable drafts. The service uses atomic JSON files under ~/.local/state/pcp-control-center/WO-20261125-001/intake-drafts. The directory and files use 0700 and 0600 permissions.
- The actual browser sample recovered two user turns, confirmed fields, 12 exact Git source references and document revisions after refresh, a clean browser session and a real service restart. The PCP pin is 22bae955686f03c5f440cdcd66e13a69f1289f90. The autoloop/workorder query returned zero matching validated and candidate assets and three matching Inbox references, marked non-authoritative.
- Three reviewable packages were generated and preserved. The browser exported the latest EO Workorder YAML as DRAFT with unallocated EO IDs. Document confirmation was recorded locally. Existing EO/ES/Autoloop source counts remained 1 workorder, 1 execution and 33 historical runs.
- Intake has no configured server-side LLM endpoint, model or credential binding. Live adaptive replies and LLM drafting are unavailable. The local EO checkout provides canonical templates and Git records. An authorized EO Job/Workorder creation interface remains unavailable. The dashboard supports manual conversation, template generation, confirmation and export.
- Backend validation passed 19 Python tests and JS syntax checks. Eighteen browser assertions passed with a real service restart. HTTPS integration checked same-origin intake writes, draft path confinement and rejection of unsupported writes.
- Actual host evidence recorded Ubuntu 24.04, Bash 5.2.21, Python 3.12.3, and the existing worktree and user service. Local Codex CLI 0.171.0 was invoked directly. Its configured model route returned HTTP 401 Missing bearer, so model review and actual model/effort were NOT_EXPOSED_BY_RUNTIME. Local tests and deployment were verified by the cbnet tools without CB or Tunnel.
- Workorder and design inputs were retrieved byte-for-byte at b05d96d2e74b90ff77844aff2b4fe157b6e1f651. Original local main and its pending changes were preserved. The V1.1 work continues the deployed dashboard branch.

## Dashboard V1 continuation

- Workorder WO-20261125-001 is implemented in an isolated worktree based on the existing local main. The original main working tree and the remote main ref were preserved.
- The delivered original design exactly matches SHA-256 2325e82b6d39daa6039a108595751cb1ed7ee8c6b251a5baf4ee15ba73107232. The seven Chinese-language views use its navigation and visual styling.
- Verified data includes 1 EO Workorder, 1 local draft EO Result, 1 existing ES Execution and 33 historical Autoloop Runs across two Hub projections. Both Hub live probes were offline. EO/ES/provider write controls remain unavailable with explicit reasons.
- Local Ruflo 3.80.0 supplied the implementation directive via the original Supervisor. The runtime reported gpt-6.2-sol. Response reasoning effort is NOT_EXPOSED_BY_RUNTIME. The Dashboard MCP probe was connected and its agent_list returned zero registrations for that stdio session.
- Personal Dashboard HTTPS uses https://127.0.0.1:8787/ and https://192.168.5.4:8787/. Both entries open without login. The Windows Hyper-V rule is active for TCP 8787 from 192.168.5.0/24. Both listeners returned HTTP 200 without credentials from WSL. An independent MEC-device test is still open.
- Next version backlog is GPT ↔ Ruflo direct management over a secure and authorized Runtime Gateway. There is no Gateway, Tunnel or ChatGPT connector in this delivery.
- Deployment and validation details are in [dashboard/README.md](dashboard/README.md).

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
