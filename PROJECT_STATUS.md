# Project Status

- Domain ID: `pcp-engineering-runtime`
- Repository: `Su9moon/PCP-Engineering-Runtime`
- Default branch: `main`
- Status: `VERTICAL_POC_LOCAL_SLICE_VERIFIED_REMOTE_ACCEPTANCE_OPEN`
- Ruflo control-plane target: `cbnet` / Ubuntu 24.04 / WSL2
- Execution location: flexible across authorized nodes; do not infer all workers must be on cbnet.

## Ruflo deployment

- Ruflo `3.80.0` is installed and run through Node.js `v24.22.3` / npm `11.19.1`.
- Deployment is local stdio MCP on demand; no HTTP/TCP service, daemon, systemd unit, Federation, or autonomous fanout was started.
- Existing Ruflo deployment report: `reports/LOCAL-RUFLO-DEPLOYMENT-20261122.md`.

## Codex / CC Switch

- WSL Codex CLI `0.171.0` successfully completed a real model-only `codex exec` using the existing CC Switch `happy小任务主流` profile via `CODEX_HOME=/home/cbnet/.codex-plus-b`; no secret material was displayed or copied.
- Codex ephemeral MCP config override discovered Ruflo `mcp_status` and invoked it successfully. Result: `running=true`, `transport=stdio`, `port=null`, `host=null` (process PID was observed in command output). The persistent Codex and CC Switch configurations were unchanged.
- This provider-backed model path is distinct from official ChatGPT OAuth login under `/home/cbnet/.codex`; do not infer OAuth login from it.

## Existing Vertical POC progress

- Continued `workorders/WO-20261122-001-VERTICAL-POC.md`; no replacement POC created.
- Added fixture discount behavior with integer-cent arithmetic, basis-point rates, half-up rounding, and input validation. Eight fixture unit tests pass.
- This was a local Codex execution, not an Autoloop Worker run. No ES-authorized Execution/Attempt/Invocation, Ruflo-supervised task, independent Review, or EO Result/Evidence/Review is claimed.
- Detailed evidence and blockers: `reports/VERTICAL-POC-EXECUTION-20261123.md`.

## Open acceptance prerequisites

- No `~/.agent-autoloop` initialization/configuration or running Autoloop Hub was present.
- No separate authorized Worker host was verified.
- No secure HTTPS Hub route was provided/reachable; only local CC Switch endpoint `127.0.0.1:15721` was reachable.
- No live ES authority/store was exercised to issue an authorized ExecutionRequest and Invocation.
- Independent read-only Review and EO evidence return remain open.

Unblock the end-to-end chain by providing/authorizing a Worker host with Node 24+, Codex model access and pinned Autoloop setup; a secured HTTPS Hub route; and the live/pinned ES authority store to authorize one frozen request. Then capture real Autoloop, ES, Review and EO identities. Do not add API keys, schedulers, or public plain-HTTP listeners as a workaround.

## Preserved boundaries

CB Green, TaskStore, Windows Codex, and existing CC Switch account/provider configuration were not modified. Ruflo, Autoloop, PCP, EO, and ES upstream source were not modified.
