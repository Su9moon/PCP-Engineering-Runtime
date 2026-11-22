# Project Status

- Domain ID: `pcp-engineering-runtime`
- Repository: `Su9moon/PCP-Engineering-Runtime`
- Default branch: `main`
- Status: `RUFLO_LOCAL_DEPLOYMENT_COMPLETE_WITH_CODEX_AUTH_BLOCKER_PROVIDER_VERIFIED`
- Target host: `cbnet` / Ubuntu 24.04 / WSL2

## Ruflo

- Installed and executed: Ruflo `3.80.0` via pinned npm package `ruflo@3.80.0`.
- Node.js: `v24.22.3` through user-level NVM.
- npm: `11.19.1`.
- `ruflo doctor`: completed; 22 checks passed and 14 warnings reported. Warnings are non-blocking and include absent Claude Code CLI, agent-browser, API keys, optional memory database/daemon, and no MCP config inside Ruflo itself.
- Runtime mode: local stdio MCP on demand. No HTTP listener, TCP port, daemon, systemd service, Federation, swarm, worker, or autonomous fanout started.

## Ruflo account/provider boundary

- `ruflo auth --help` and `ruflo auth status` confirm Ruflo's auth command is Cognitum identity/profile management, not ChatGPT/Codex OAuth.
- `ruflo providers list` shows OpenAI `Not configured`; `providers test -p openai` reports no API key. No provider key was added.
- Existing CC Switch provider `happy小任务主流` remains the active Windows-side route. CC Switch remains the account/provider switcher; Ruflo remains the local orchestration/provider capability layer.

## Codex MCP

- WSL Codex CLI: `0.171.0`; `codex login status` remains `Not logged in` for `/home/cbnet/.codex`.
- Exactly one global MCP entry named `ruflo` is configured.
- Command: `/home/cbnet/.nvm/versions/node/v24.22.3/bin/npx -y ruflo@3.80.0 mcp start`.
- Startup timeout: 120 seconds; tool timeout: 120 seconds.
- Direct MCP protocol smoke passed: server initialized as `ruflo` `3.80.0`; 393 tool names were discovered; `mcp_status` returned `running=true`, `transport=stdio`, `port=null`, `host=null`.
- `guidance_brain` read-only recommendation call also passed.
- A Codex-hosted smoke reached the API endpoint but failed before MCP/tool discovery with HTTP `401 Unauthorized: Missing bearer or basic authentication in header` on WebSocket and HTTPS fallback.

## PCP boundaries

- EO Workorder / Result / Evidence and ES Execution / Attempt / Invocation remain authoritative.
- Autoloop integration is not started.
- EO/ES adapters are not started.
- CB Green, CB MCP, CB TaskStore, processes, and ports were not modified.
- Windows Codex Desktop and `/home/cbnet/.codex-plus-b` were not modified. Existing CC Switch route `happy小任务主流` was inspected only.

## Remaining limitation

The Codex interactive `codex exec` smoke could not complete tool discovery because the WSL ChatGPT auth state is absent. It returned HTTP `401 Unauthorized: Missing bearer or basic authentication in header` for the Responses WebSocket and HTTPS fallback. `codex login status` reports `Not logged in`. Ruflo direct stdio MCP discovery and `mcp_status` remain successful. Minimum unblock: complete an official Codex login for `/home/cbnet/.codex` or use a supported CC Switch-managed WSL auth target; do not copy credentials or edit auth files manually.
