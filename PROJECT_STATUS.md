# Project Status

- Domain ID: pcp-engineering-runtime
- Repository: Su9moon/PCP-Engineering-Runtime
- Visibility: Public (user-created; preserve)
- Default branch: main
- Status: BOOTSTRAP_COMPLETE / RUFLO_LOCAL_DEPLOYMENT_READY
- Ruflo local runtime: deployment workorder prepared; execution not yet confirmed
- Autoloop / EO-ES runtime integration: not started
- Production deployment: not authorized

## Governance
PCP main source used for the bootstrap snapshots: a66978ce1d5170fd1d0407678c78bdbb0c36d136. PCP main remains canonical. Canonical project ADR: Su9moon/personal-ai-control-plane:governance/adr/ADR-2026-11-22-001_pcp-engineering-runtime.md. Local continuity snapshot: governance/snapshots/pcp/ADR-2026-11-22-001_pcp-engineering-runtime.md.

## Pinned inputs
- EO: Su9moon/pcp-engineering-operations@c22189ba1144cdcf5cebf9b10a7db8e7c4f2e94d
- ES: Su9moon/pcp-execution-server@85783a75bd5ef7bc44110c6f9184b55748b4bfc4
- CB: Su9moon/codex-bridge@9b626b492729f02f53d119657d4d0dad67f4f37a
- Autoloop Fork: Su9moon/agent-autoloop-pcp@f27466d5f0ec9fc6f2f48a1fa68c748581906bdc
- Ruflo upstream: ruvnet/ruflo@87f612cef121b50c2e31e2d3f88e46d88963a377
- Symphony reference: Su9moon/symphony-cb@be10a1b79df723d6d7612b5651c8522704dafb2e

## Verified facts
- Autoloop has separate Hub/Worker configuration; Worker-only hosts need Hub URL and Worker key and initiate HTTP long-poll to the Hub.
- A non-loopback Hub should be behind HTTPS. This source inspection does not prove a live cross-host route.
- Autoloop has up to 10 internal failure retries with exponential backoff; these must remain within the same provider run / ES Attempt unless ES authorizes a new Attempt.
- ES currently exposes an embedded Python ExecutionKernel, not a general HTTP/MCP service. Reuse the kernel through a thin adapter; do not create a second ES store.
- EO has Job/Workorder/Result/Evidence/Review schemas and templates.
- Ruflo README reports 3.80.0; root package metadata says claude-flow while README uses ruflo. Verify the actual package/command.
- User reports a Ruflo Fork exists, but connected GitHub listing/search did not identify its exact URL. Resolve via local gh auth; if still unavailable, use pinned upstream read-only.
- Symphony SPEC is Draft v1 and its Elixir README calls the implementation evaluation-only.

## EO canonical work item

- Job: Su9moon/pcp-engineering-operations@0ca2043e6149d9106f2e6caba5627a6511e1074c:jobs/JOB-20261122-001/job.yaml
- Workorder: Su9moon/pcp-engineering-operations@0ca2043e6149d9106f2e6caba5627a6511e1074c:workorders/WO-20261122-001/workorder.yaml
- EO Job/Workorder creation is complete; both are READY.

## Repository bootstrap

- Initial README commit: c9ab4560965138575d08e24d0ec3f8fa8c02cacd
- Architecture/docs/fixture commit: 8636ac80739ffa32cccb61a182963433779bc6a5
- PCP governance snapshot/provenance commit: 7187fb0016223225835019f7c865a98565c81db2
- 22 exact PCP governance/skill/baseline snapshots are present under governance/snapshots/pcp/.

## Workspace identity

- Current identity baseline: PCP Project & Workspace Identity V0.2.
- Local Codex Project display name, when provisioned: Lo_PCP Engineering Runtime.
- Local Git / Persistent Worktree / Codex UI state: not asserted by this bootstrap; discover the actual user workspace at execution time. No local path is hard-coded.
- Production Runtime Workspace / Installed Release: not required for this engineering POC.

## Immediate next action: Ruflo local deployment

- Active handoff: `workorders/WO-20261122-001-RUFLO-LOCAL-DEPLOYMENT.md`.
- Target: new Windows 11 / WSL2 Ubuntu-24.04 host, Linux user `cbnet`.
- Deployment mode: pinned Ruflo `3.80.0` stdio MCP launched on demand by WSL Codex; no daemon, hooks, plugin activation, Federation, or Autoloop yet.
- The ChatGPT-to-WSL Codex Bridge tunnel is currently unavailable (`Tunnel-client has not been seen for 300 seconds`), so no local installation has been executed from this chat.
- Ruflo Fork must be resolved by authenticated local `gh` lookup. If still unavailable, use the pinned upstream read-only as the deployment workorder specifies.

## Next after local deployment passes

- Resume `workorders/WO-20261122-001-VERTICAL-POC.md` for the EO/ES + Autoloop + Ruflo vertical POC.
- No live Ruflo/Autoloop integration, multi-host run or production capability is claimed.
