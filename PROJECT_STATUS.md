# Project Status

- Domain ID: pcp-engineering-runtime
- Repository: Su9moon/PCP-Engineering-Runtime
- Visibility: Public (user-created; preserve)
- Default branch: main
- Status: BOOTSTRAP_COMPLETE / VERTICAL_POC_READY
- Runtime implementation: not started
- Production deployment: not authorized

## Governance
PCP main source used for the bootstrap snapshots: 1cd4f0094cc8a7b7170876c471353da20c22fcad. PCP main remains canonical. Project ADR: governance/adr/ADR-2026-11-22-001_pcp-engineering-runtime.md.

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

## Open for POC
1. Resolve the exact Ruflo Fork URL locally; non-blocking for Autoloop setup.
2. Confirm Node.js 24+ on Hub and Workers.
3. Confirm Codex CLI availability/authentication on the Worker.
4. Confirm HTTPS reachability from a separate Worker host to Hub.
5. Verify EO/ES mapping against exact contracts/schemas.

Active handoff: workorders/WO-20261122-001-VERTICAL-POC.md. No live Ruflo/Autoloop integration, multi-host run or production capability is claimed.
