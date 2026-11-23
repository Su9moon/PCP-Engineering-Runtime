# WO-20261122-001 Vertical POC — Execution Update (2026-11-23)

## Scope and execution position

Continues the existing `workorders/WO-20261122-001-VERTICAL-POC.md`; no substitute POC was created. Ruflo control plane remains on cbnet / WSL2 Ubuntu-24.04. Execution location is flexible, but the verified Autoloop Worker ran on the same cbnet WSL host as the Hub. This proves a real local Autoloop/Codex path, not remote Worker acceptance.

## Verified execution evidence

- Reused Node.js `v24.22.3`, Ruflo `3.80.0`, Codex CLI `0.171.0`, and existing CC Switch profile `happy小任务主流` through `CODEX_HOME=/home/cbnet/.codex-plus-b`. A real model-only `codex exec` completed (`CODEX_HARNESS_OK`); no credentials were displayed or copied.
- With ephemeral Codex MCP configuration, Codex discovered Ruflo server `ruflo` and tool `mcp_status`; its real call returned `running=true`, `transport=stdio`, `port=null`, `host=null`. Persistent Codex and CC Switch configuration were unchanged.
- Ruflo policy `status` and `verify --full` succeeded. At final check, the decision ledger was valid with length 5 and both log/mirror anchors true. No anchor-establishment flow was used.
- Ruflo MCP CLI `mcp_status` succeeded (`running=true`, stdio, no network port). `agent_list` returned zero agents. `analyze_diff` and `analyze_diff-risk` executed and reported low risk. These heuristic tools are not a Ruflo-supervised Worker, semantic review, or Product QA.
- Isolated Autoloop installation at `/home/cbnet/.agent-autoloop-poc-20261123` uses pinned commit `f27466d5f0ec9fc6f2f48a1fa68c748581906bdc`. Hub log and socket inspection confirm it listens only on `127.0.0.1:3350`; Worker reported cbnet started. Autoloop Run 2 used Codex thread `01a206a0-2d1e-7ce1-a2a0-ce3cda1af76a`, branch `poc/wo-20261122-001-codex-worker`, commit `b8ac0f81e47b2a3c3e09e0889d799564005da431`. Hub and Worker were on the same host; HTTPS/remote connectivity was not exercised.
- ES request `EXR-WO-20261122-001-POC-01` / Execution `EXE-c4ef6d50232848378940693ed6e1ec0c` has a failed premature-reference Attempt `ATT-e07aec29715445ae9f24b7746ce4691c` and a separately authorized completed Attempt `ATT-035dee80849a4ab2b2cfd2f720e8ee11` / Invocation `AINV-d4131db257294835aa086ec1bbe4ec5f`. ES history records approved review and Execution `DONE`. The completed Attempt's runtime_ref is nevertheless the placeholder `provider-awaiting-actual-autoloop-run; attempt ATT-...`, not the actual Autoloop Run 2 identity. ES-to-Autoloop correlation acceptance is therefore NOT met. The terminal historical ES record was not edited.
- The exact Autoloop worker commit received independent read-only Codex review, approved for the bounded fixture change. Current main-checkout fixture tests pass: 8 tests. Ruflo semantic review and separate Product QA remain incomplete.
- Main contains a distinct equivalent implementation commit `1cc92ba5dab02f5f5d86706bca73c54fe8fffdcf`; it is not the Autoloop Worker commit. Main and Worker worktrees each have separate uncommitted fixture edits; these were preserved, not discarded or history-rewritten.
- EO Result/Evidence/Review drafts exist but are uncommitted. They only support bounded fixture acceptance and do not establish accurate provider correlation, Ruflo supervision, remote execution, or final EO acceptance.

## Remaining acceptance gaps and exact unblock conditions

1. **ES ↔ Autoloop correlation:** do not alter the completed historical Attempt. Any redispatch needs a new ES request/Execution plus explicit authorization; the adapter must bind the actual Autoloop Run ID at the supported runtime-start transition and preserve one run / one Invocation / one Attempt.
2. **Remote Worker:** an independently authorized Worker host and a secured, reachable HTTPS Hub route with certificate/trust and outbound connectivity are required. Current Hub is loopback-only at `127.0.0.1:3350`; no public plain-HTTP listener was opened.
3. **Ruflo supervision and Product QA:** `agent_list` is empty. A governed Ruflo supervisor/reviewer flow and distinct Product QA result remain required; heuristic diff analysis is not approval.
4. **EO final return:** validate and finalize the existing EO drafts against the unchanged schemas after accurate ES, Worker, review, and QA evidence exists.

No API key, new scheduler, public listener, or account/provider configuration was added. CB Green, TaskStore, Windows Codex, and existing CC Switch configuration were not modified. No credentials were printed or copied. The isolated POC Hub and local state are retained; they are not configured as a production service.

## Validation

- `python3 -m unittest discover -s examples/poc-fixture/tests -v` — 8 passed.
- Ruflo policy `status` and `verify --full` — valid ledger, anchors valid.
- Ruflo MCP `mcp_status` — succeeded; `agent_list` — empty; `analyze_diff` and `analyze_diff-risk` — succeeded, low risk.

Status: **fixture execution slice verified through a real same-host Autoloop/Codex Worker; end-to-end Vertical POC remains OPEN** because the completed ES Attempt has an inaccurate runtime reference, and remote HTTPS Worker, Ruflo supervision, and distinct Product QA are unverified.
