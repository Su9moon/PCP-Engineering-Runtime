# WO-20261122-001 Vertical POC — Execution Update (2026-11-23)

## Scope and execution position

This update continues the existing `WO-20261122-001-VERTICAL-POC`; it does not create a replacement POC. Ruflo remains deployed on cbnet / WSL2 Ubuntu-24.04. The user's execution-location clarification is applied: code work may run on any authorized node, while the Ruflo control plane stays on cbnet. No separate worker host was available/verified in this turn.

## Verified execution evidence

- WSL Codex `0.171.0` ran with the existing CC Switch happy profile (`CODEX_HOME=/home/cbnet/.codex-plus-b`); a model-only `codex exec` returned `CODEX_HARNESS_OK` and completed. This proves model access through that existing route, not a remote Autoloop Worker.
- With an ephemeral CLI config override, Codex discovered Ruflo MCP server `ruflo` and tool `mcp_status`. Its real call returned `{"running":true,"pid":128963,"transport":"stdio","port":null,"host":null}`. No persistent Codex/CC Switch configuration was changed.
- The first sandboxed tool-call attempt was denied by this environment's `approval policy is never`; the successful verification was performed in the already-permitted full-access invocation. No policy settings or credentials were altered.
- The existing POC fixture's `apply_discount_cents` was implemented using integer arithmetic, basis-point discounts, half-up rounding, and strict type/range checks. Test suite: 8 tests passed, including rounding and invalid-input cases.
- Fixture edits were made directly in the existing checkout. No Autoloop run, ES authority, Attempt, Invocation, or independent Review is claimed for this local Codex execution.

## Remaining acceptance gaps and exact unblock conditions

1. **Real Autoloop Codex Worker:** `~/.agent-autoloop` is absent, no Autoloop process is running, and no independently authorized Worker host was verified. Unblock by authorizing/provisioning a Worker host with Node 24+, Codex CLI and model access, and installing/configuring the pinned Autoloop commit there; then capture its actual run/event identity.
2. **Secure Hub connectivity:** no Hub is running and no HTTPS endpoint reachable from a Worker was provided/verified. Only the existing local CC Switch endpoint at `127.0.0.1:15721` was reachable. Unblock by providing a secured HTTPS Hub route/certificate and network reachability; do not expose plain HTTP publicly.
3. **ES canonical authority and correlation:** no current ES service/authority was exercised, so no Execution/Attempt/Invocation exists for this run. Unblock by making the pinned ES kernel/store available and authorizing one frozen ExecutionRequest before dispatch; correlate the resulting Invocation to exactly one authorized Attempt.
4. **Independent Review and EO return:** no separate read-only Reviewer, Product QA acceptance record, or EO Result/Evidence/Review was produced. These must reference actual Worker and ES identities after the real run.
5. **Ruflo supervision:** MCP discovery and `mcp_status` are verified, but a supervised execution/Review/QA chain was not run.

No API key, new scheduler, daemon, public listener, or provider configuration was added. CB Green, TaskStore, Windows Codex, and the existing CC Switch account/provider configuration were not modified. No credentials were printed or copied.

## Files and validation

- Changed implementation: `examples/poc-fixture/src/poc_fixture/pricing.py`
- Changed tests: `examples/poc-fixture/tests/test_pricing.py`
- Validation: `python3 -m unittest discover -s examples/poc-fixture/tests -v` — 8 passed.

Status: **local Codex/model + Ruflo MCP + fixture slice verified; end-to-end vertical POC remains incomplete** pending the explicit prerequisites above.
