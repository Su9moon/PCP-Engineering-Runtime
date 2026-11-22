# Local Ruflo Deployment Report

Date: 2026-11-23 (Asia/Shanghai)
Repository: `Su9moon/PCP-Engineering-Runtime`
Workorder: `WO-20261122-001-RUFLO-LOCAL-DEPLOYMENT.md`

## Host and versions

- User: `cbnet`
- Distribution: Ubuntu 24.04 LTS
- Kernel: WSL2
- Node: `v24.22.3`
- npm: `11.19.1`
- Ruflo: `v3.80.0`
- Codex CLI binary: `0.171.0`
- Resolved npx: `/home/cbnet/.nvm/versions/node/v24.22.3/bin/npx`

## Installation

Ruflo was invoked with the pinned command:

```text
/home/cbnet/.nvm/versions/node/v24.22.3/bin/npx -y ruflo@3.80.0
```

`ruflo doctor` completed with 22 passed checks and 14 warnings. Warnings were preserved rather than hidden. No `--fix` command was run.

Node 24 was installed with user-level NVM. The default Node alias is `24.22.3`; no system Ubuntu package or Windows Node installation was replaced.

## Codex MCP registration

Sanitized registration:

```toml
[mcp_servers.ruflo]
command = "/home/cbnet/.nvm/versions/node/v24.22.3/bin/npx"
args = ["-y", "ruflo@3.80.0", "mcp", "start"]
enabled = true
startup_timeout_sec = 120
tool_timeout_sec = 120
```

`codex mcp list --json` showed exactly one enabled `ruflo` stdio server and no unrelated MCP entry was present or changed.

## Direct MCP smoke evidence

A fresh local stdio MCP process initialized successfully:

```json
{"serverInfo":{"name":"ruflo","version":"3.80.0"},"protocolVersion":"2024-11-05"}
```

The server advertised 393 actual tool names. Key requested tools were present: `mcp_status` and `guidance_brain`.

The real read-only `mcp_status` call returned:

```json
{
  "running": true,
  "pid": 118817,
  "transport": "stdio",
  "port": null,
  "host": null
}
```

A read-only `guidance_brain` recommendation call for preserving EO/ES authority and leaving CB unchanged also returned successfully. No task, agent, swarm, or workorder was created.

## Ruflo account and provider capability verification

The pinned local CLI was queried without changing configuration:

```text
ruflo auth --help
ruflo auth status
ruflo providers --help
ruflo providers list
ruflo providers test -p openai
```

Observed behavior:

- `ruflo auth` is Ruflo/Cognitum identity management (`login`, `logout`, `status`, named profiles); it is not the OpenAI ChatGPT/Codex OAuth store.
- `ruflo providers` manages AI provider/API-key configuration and model selection.
- `providers list` reports OpenAI as `Not configured`; `providers test -p openai` reports `Not configured (no API key found)`. No key was entered or created.
- Therefore PCP keeps Codex/ChatGPT account switching in CC Switch and uses Ruflo for provider/agent orchestration only.

The existing CC Switch provider `happy小任务主流` remains the active Windows-side Codex route. Its isolated terminal launcher still points at `.codex-plus-b`; no credentials were copied into WSL and no auth file was fabricated.

## Preservation evidence

- No Ruflo HTTP/TCP listener, systemd service, daemon, Federation, or unattended worker was started.
- CB Green / CB MCP / CB TaskStore were not started, stopped, restarted, migrated, repaired, or modified.
- Windows Codex Desktop, CC Switch provider definitions, and `~/.codex-plus-b` were not modified. CC Switch was only inspected for its existing `happy小任务主流` route and target-directory behavior.
- The WSL `/home/cbnet/.codex/config.toml` hash remained `8bfd5d31cf92f2b21d434d0f1db01794261ce399f14f2e6128e0e15ca43504f6` during this verification; it still contains only the Ruflo stdio MCP entry.
- No provider API key, token, auth JSON, cookie, or secret was added to this repository.

## Current acceptance state

- Ruflo direct stdio discovery and direct read-only `mcp_status` smoke remain successful: 393 tools; server `3.80.0`; `running=true`, `transport=stdio`, `port=null`, `host=null`.
- `codex mcp list --json` still shows exactly one enabled MCP server, `ruflo`, with the pinned local stdio command.
- A Codex-hosted smoke was attempted after CC Switch inspection. It could not reach the model backend because the WSL `CODEX_HOME=/home/cbnet/.codex` has no `auth.json`; the CLI returned HTTP `401 Unauthorized: Missing bearer or basic authentication in header` for `wss://api.openai.com/v1/responses` and HTTPS fallback.
- `codex login status` remains `Not logged in`. The minimum unblock is a successful official Codex login that writes the WSL Codex auth state (or a supported CC Switch-managed WSL auth target); do not copy Windows credentials or hand-edit auth files.

This report records the provider decision and the remaining Codex-hosted acceptance limitation without exposing credentials.
