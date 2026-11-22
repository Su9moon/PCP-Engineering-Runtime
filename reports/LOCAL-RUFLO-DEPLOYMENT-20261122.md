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

The server advertised 393 actual tool names. The complete discovered names are captured in the execution transcript; key requested tools were present: `mcp_status` and `guidance_brain`.

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

## Preservation evidence

- No Ruflo HTTP/TCP listener, systemd service, daemon, Federation, or unattended worker was started.
- CB Green / CB MCP / CB TaskStore were not started, stopped, restarted, migrated, repaired, or modified.
- Windows Codex Desktop, CC Switch, and `~/.codex-plus-b` were not modified.
- No provider API key, token, auth JSON, cookie, or secret was added to this repository.

## Limitation

The WSL Codex CLI is `0.171.0`, but `codex login status` remains `Not logged in`. The official device-auth browser flow reaches the callback page, while the CLI polling request to `https://auth.openai.com/api/accounts/deviceauth/token` fails with `error sending request for url`; no auth.json was created or modified. The endpoint itself is reachable from WSL: direct and configured-proxy POST probes receive HTTP 400 for an intentionally incomplete request, proving DNS/TLS/HTTP connectivity. The remaining failure is specific to the CLI device-auth polling exchange (likely proxy/client request handling or the authorization transaction not being visible to the polling client), not Ruflo/MCP. Minimal unblock: run the official `codex login --device-auth` flow in the same WSL shell and permit its HTTPS POST polling to `/api/accounts/deviceauth/token` through the active network path, then verify `codex login status` before rerunning the Codex-hosted MCP smoke. Direct MCP protocol verification is successful; Codex-hosted tool discovery remains pending this login result.
