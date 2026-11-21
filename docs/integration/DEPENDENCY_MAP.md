# Dependency Map and Pinned Source Evidence

All source refs are commit-pinned. Do not use floating latest versions.

## PCP and existing domains

| Repository | Commit | Role |
|---|---|---|
| Su9moon/personal-ai-control-plane | a66978ce1d5170fd1d0407678c78bdbb0c36d136 | Canonical governance / ADR |
| Su9moon/pcp-engineering-operations | c22189ba1144cdcf5cebf9b10a7db8e7c4f2e94d | EO Job / Workorder / Result / Evidence / Review |
| Su9moon/pcp-execution-server | 85783a75bd5ef7bc44110c6f9184b55748b4bfc4 | ES Execution / Attempt / Invocation authority |
| Su9moon/codex-bridge | 9b626b492729f02f53d119657d4d0dad67f4f37a | Existing CB Bridge; unchanged in this POC |

EO inputs: AGENTS.md; schemas/job.schema.yaml; schemas/workorder.schema.yaml; schemas/result.schema.yaml; schemas/evidence.schema.yaml; schemas/review.schema.yaml; templates/job.template.yaml; templates/workorder.template.yaml; templates/result.template.yaml; templates/evidence.template.yaml; templates/review.template.yaml.

ES inputs: AGENTS.md; README.md; governance/snapshots/PCP_Execution_Server_BASELINE_V0.3.snapshot.md; governance/contracts/NORTHBOUND_EXECUTION_CONTRACT_V0.1.md; governance/contracts/EXECUTION_STATE_MACHINE_V0.1.md; governance/contracts/WORKER_PROTOCOL_V0.2.md; governance/contracts/EXECUTOR_ADAPTER_CONTRACT_V0.1.md; src/execution_server/kernel.py; src/execution_server/store.py; src/adapters/codex/adapter.py; docs/RUNTIME_BINDING_GITHUB_ORG_SHARED_RUNNER_VALIDATION_V0.1.md.

The current ES implementation is an embedded Python kernel, not a general network service. Use its existing contract and code; do not create another canonical execution store.

## EO POC Work Item

- Job: Su9moon/pcp-engineering-operations@0ca2043e6149d9106f2e6caba5627a6511e1074c:jobs/JOB-20261122-001/job.yaml
- Workorder: Su9moon/pcp-engineering-operations@0ca2043e6149d9106f2e6caba5627a6511e1074c:workorders/WO-20261122-001/workorder.yaml
- Both records are READY and use the existing EO V0.1 schemas.

## Agent Autoloop

- Fork: Su9moon/agent-autoloop-pcp
- Upstream parent: KKKKhazix/agent-autoloop
- HEAD: f27466d5f0ec9fc6f2f48a1fa68c748581906bdc
- License: MIT; package is private, requires Node.js >=24 and has no declared semver version.
- Install from the pinned Git source, not an assumed npm latest package.

Inspected source: host/config.ts (Hub/Worker config split); host/up.ts (separate Hub and Worker startup); protocol/client.ts (Worker long-poll); worker/worker.ts (Worker process and result); kernel/decide.ts (MAX_ATTEMPTS=10 and exponential backoff); docs/protocol.md; docs/state-machines.md; host/server.ts; host/http.ts.

Remote Worker source support is verified, live cross-host networking is not. Hub non-loopback exposure must use HTTPS.

## Ruflo

- Upstream: ruvnet/ruflo
- HEAD: 87f612cef121b50c2e31e2d3f88e46d88963a377
- README reports 3.80.0 / MIT. Root package metadata names the package claude-flow while README examples use ruflo; verify actual install and command.
- User reports a Ruflo Fork exists, but the connected GitHub listing/search did not identify its exact owner/repo. Resolve with local gh auth. If unavailable, use this pinned upstream commit read-only; never write to upstream or label it as the user's Fork.

## Symphony reference only

- User Fork: Su9moon/symphony-cb, parent openai/symphony
- HEAD: be10a1b79df723d6d7612b5651c8522704dafb2e
- License: Apache-2.0
- SPEC.md is Draft v1; Elixir README says evaluation-only prototype.
- Reference for issue/workspace orchestration only, not a selected runtime dependency.

## CB lane

L0 is the user's intended lightweight business-API path. This POC does not modify CB or claim that the current codex-bridge repository already exposes a generic external business-API adapter.
