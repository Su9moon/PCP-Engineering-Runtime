# Project Status

- Domain ID: `pcp-engineering-runtime`
- Repository: `Su9moon/PCP-Engineering-Runtime`
- Default branch: `main`
- Status: `VERTICAL_POC_LOCAL_WORKER_VERIFIED_REMOTE_AND_GOVERNANCE_ACCEPTANCE_OPEN`
- Ruflo control-plane target: `cbnet` / Ubuntu 24.04 / WSL2
- Execution location: flexible across authorized nodes; do not infer all workers must be on cbnet.

## Dashboard V1.2 D01 execution continuation

- WO-20261126-002 resumes from `aa10e159383cd2f5a9fbdb82e5a0ac25d0ca2105`. The existing 8787 service now has the reviewed code at `c51a98de770114d6f8db8eecb803736a9a24e2c5`. Localhost and private LAN access remain anonymous. The LAN address is now `192.168.5.6`, with the same private subnet and existing 8787 firewall scope. A separate MEC device has not been tested.
- A server-owned grant enables real local TLS same-origin dialogue and Ruflo planning. The browser recorded two actual `gpt-6.2-sol` route 200 responses and stored confirmed Chinese requirements R1 and Manual plan P2. Complexity remains advisory. The grant is based on the service account and does not identify individual same-host users.
- The one authorized non-production action created `JOB-20261127-001` and `WO-20261127-001` in the existing EO Git repository at `6785b6d08d1a0a0a05fb11291158e0a90f59e4d0`. The existing ES kernel created one Request, Execution, Attempt and Invocation. The recovered `ruflo-local` Worker completed Autoloop Event 30 / Run 29 once, with exit code 0 and zero retries. The historical Run 28 is unknown with zero retries and unchanged original evidence.
- Dashboard read back and exported “D01 合成验证通过。” Worker context recorded `gpt-6.2-sol` and `high`. Distinct Ruflo Reviewer and Product QA signed PASS, the original Supervisor accepted D01, and ES recorded APPROVED with canonical state DONE.
- Independent checks passed 5 focused Python tests for P1, 3 grant checks and the five-case EO/ES fixture for P3, Node syntax checks, two real model calls and one end-to-end Worker run. The earlier 25 Python / 22 browser results were reused. The D01 test rule is paused after its only run.

[D01 continuation and execution evidence](reports/PCP-ENGINEERING-CONTROL-CENTER-V1.2-D01-20261127.md)

## Dashboard V1.2 engineering planning

- WO-20261126-002 continues the V1.1 deployment on `dashboard/wo-20261125-001`. The existing service is active at `https://127.0.0.1:8787/` and `https://192.168.5.4:8787/`. Loopback and LAN returned HTTPS 200 without a login. LAN model requests returned 403. An independent MEC-device check remains open.
- The original Ruflo 3.80.0 Supervisor planned the work and scoped the model connection. The final deployed browser call used `gpt-6.2-sol`, returned route 200 in 19,657 ms, and stored revision 7 with six earlier revisions intact. Receipt `resp_0e723ef45085db6f016b077245bb5487d0a3dd342e6321c222`. The request used effort `high`. Runtime response effort remains unexposed.
- The existing intake stores confirmed requirement snapshots and versioned proposals, with Suggestion, Manual and Autonomous planning choices, dependency edits, risk and separate authorization scope. A plan confirmation records a local decision. Live dispatch remains disabled.
- Code `647a8bc6cb74339943cd74f95f73ad25a750c506` passed 25 focused Python tests and 22 browser assertions. Independent Ruflo Reviewer and Product QA accepted the sealed evidence within the planning scope. The Supervisor accepted P2 and kept P1 in REWORK for an independent diff and test reproduction and server-side operator authorization. The live planner is now paused. Loopback planning POST returns 503 and LAN planning POST returns 403. Both listeners still read the seven revisions and offer anonymous draft editing.
- Live execution P3 remains blocked. The primary Hub on port 47355 is offline, WO-003 Run 28 remains claimed, and there is no authorized EO creation or corresponding ES Attempt path. This work reused the fixture-era run and review evidence, created no new Autoloop Event or Run, and preserved the original local main and existing pending changes.

[Detailed V1.2 report](reports/PCP-ENGINEERING-CONTROL-CENTER-V1.2-20261126.md)

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
