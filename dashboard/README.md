# PCP Engineering Control Center V1

Dashboard V1 follows the supplied seven-page [design](../design/pcp-engineering-control-center-demo.html). The original HTML is retained byte-for-byte with SHA-256 2325e82b6d39daa6039a108595751cb1ed7ee8c6b251a5baf4ee15ba73107232.

## Sources

| View | Source and limits |
| --- | --- |
| Overview and Engineering Tasks | EO worktree Job and Workorder YAML for this project. An ES execution is associated only when its request metadata matches the EO Job and Workorder. |
| Runs / Events and Worker Nodes | The configured Autoloop owner GET /v1/state and existing SQLite read projections. Event IDs come from persisted run-event links or the live response when available. Archived heartbeats do not establish online status. Archived connector receipts are attached only when both IDs match within the same Hub. |
| Agent Team | Local Ruflo stdio mcp_status and agent_list. The Supervisor planning receipt has separate model-call evidence. The measured planning response exposed gpt-6.2-sol without a response reasoning-effort field. |
| Delivery Review | EO Result, Evidence and Review YAML. Untracked or modified records are marked as local drafts. Local Git objects supply commit metadata and changed paths. An EO draft decision, Worker completion and ES acceptance remain separate. |
| Connections | Each component has a probe/observation time and capability state. The browser has no source-owner credentials. |

The dashboard's only enabled actions are read and navigation actions. EO create and review, ES dispatch, Autoloop control, and Ruflo replanning show the missing owned write or authorization interface. GPT ↔ Ruflo direct management is deferred to the next version.

## Local deployment

Run dashboard/serve.py with Python 3.12 and PyYAML on the existing cbnet WSL distribution. The installed user service is pcp-dashboard-v1.service. Its configuration and dedicated Dashboard credential are outside Git, under ~/.local/state/pcp-control-center/WO-20261125-001. The config has listeners, tls and sources entries. The installed state uses the existing EO directory, ES database, Autoloop configurations and projections, and Ruflo stdio configuration.

The server listens on HTTPS port 8787 at 127.0.0.1 and 192.168.5.4. The respective application allowlists are loopback and 192.168.5.0/24. A separate local admin login is required. The certificate is dashboard-v1.crt. The login password is stored as dashboard.password with 0600 permissions. Confirm certificate trust on the client before supplying the password.

- Start on the active WSL distribution with systemctl --user start pcp-dashboard-v1.service.
- Check the listener with systemctl --user status pcp-dashboard-v1.service and ss -ltn 'sport = :8787'.
- Stop with systemctl --user stop pcp-dashboard-v1.service, or use disable --now to stop and remove automatic startup on WSL user-session initialization.

The Windows-side local endpoint is https://127.0.0.1:8787/. The LAN endpoint is https://192.168.5.4:8787/. A dedicated hidden Windows WSL process keeps the user session alive while this deployment is running. After a Windows restart, start an Ubuntu-24.04 WSL user session and keep it active for the user service.

Local Windows and WSL HTTPS are verified using the deployed certificate. MEC browser access remains open. The Windows Hyper-V firewall has a blocking default and the non-elevated session received Access denied for the proposed WSL-only inbound rule. The rule should be scoped to private TCP 8787 at 192.168.5.4 from the approved MEC client or 192.168.5.0/24. Verify the connection from MEC and configure certificate trust there through the existing administrator process.

## Focused checks

Run python3 -B -m unittest discover -s dashboard -v from the repository root. The nine tests cover EO scope and drafts, ES correlation, Autoloop live/offline identity mapping, source credential transport, allowed client networks and the absence of HTTP write methods. The browser acceptance checks use the running HTTPS service and cover seven views, actual records, dialogs, filters, write-control explanations and responsive layout.
