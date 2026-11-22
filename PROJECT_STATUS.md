# Project Status

- Domain ID: `pcp-engineering-runtime`
- Repository: `Su9moon/PCP-Engineering-Runtime`
- Default branch: `main`
- Status: `RUFLO_LOCAL_DEPLOYMENT_COMPLETE`
- Target host: `cbnet` / Ubuntu 24.04 / WSL2

## Ruflo

- Installed and executed: Ruflo `3.80.0` via pinned npm package `ruflo@3.80.0`.
- Node.js: `v24.22.3` through user-level NVM.
- npm: `11.19.1`.
- `ruflo doctor`: completed; 22 checks passed and 14 warnings reported. Warnings are non-blocking and include absent Claude Code CLI, agent-browser, API keys, optional memory database/daemon, and no MCP config inside Ruflo itself.
- Runtime mode: local stdio MCP on demand. No HTTP listener, TCP port, daemon, systemd service, Federation, swarm, worker, or autonomous fanout started.

## Codex MCP

- WSL Codex CLI: `0.171.0`, ChatGPT login status must be revalidated after device-auth network completion.
- Exactly one global MCP entry named `ruflo` is configured.
- Command: `/home/cbnet/.nvm/versions/node/v24.22.3/bin/npx -y ruflo@3.80.0 mcp start`.
- Startup timeout: 120 seconds; tool timeout: 120 seconds.
- Direct MCP protocol smoke passed: server initialized as `ruflo` `3.80.0`; 393 tool names were discovered; `mcp_status` returned `running=true`, `transport=stdio`, `port=null`, `host=null`.
- `guidance_brain` read-only recommendation call also passed.

## PCP boundaries

- EO Workorder / Result / Evidence and ES Execution / Attempt / Invocation remain authoritative.
- Autoloop integration is not started.
- EO/ES adapters are not started.
- CB Green, CB MCP, CB TaskStore, processes, and ports were not modified.
- Windows Codex Desktop, CC Switch, and `~/.codex-plus-b` were not modified.

## Remaining limitation

The Codex interactive `codex exec` smoke could not complete tool discovery because the WSL ChatGPT device-auth token exchange returned a network error and `codex login status` currently reports `Not logged in`. The direct stdio MCP protocol smoke is successful and is recorded in the deployment report.
