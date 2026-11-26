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

Run dashboard/serve.py with Python 3.12 and PyYAML on the existing cbnet WSL distribution. The installed user service is pcp-dashboard-v1.service. Its configuration is outside Git, under ~/.local/state/pcp-control-center/WO-20261125-001. The config has port, tls, sources and optional lan entries. It uses the existing EO directory, ES database, Autoloop configurations and projections, and Ruflo stdio configuration.

The dashboard opens without a login over HTTPS. cbnet serves 127.0.0.1:8787 and 192.168.5.4:8787. The LAN listener accepts clients from 192.168.5.0/24. The Windows Hyper-V rule PCP-Dashboard-V1-8787 permits TCP 8787 on the Private profile for that subnet. The certificate is dashboard-v1.crt.

- Start on the active WSL distribution with systemctl --user start pcp-dashboard-v1.service.
- Check the listener with systemctl --user status pcp-dashboard-v1.service and ss -ltn 'sport = :8787'.
- Stop with systemctl --user stop pcp-dashboard-v1.service, or use disable --now to stop and remove automatic startup on WSL user-session initialization.

The Windows-side local endpoint is https://127.0.0.1:8787/. The LAN endpoint is https://192.168.5.4:8787/. A dedicated hidden Windows WSL process keeps the user session alive while this deployment is running. After a Windows restart, start an Ubuntu-24.04 WSL user session and keep it active for the user service.

## Focused checks

Run python3 -B -m unittest discover -s dashboard -v from the repository root. The eleven tests cover EO scope and drafts, ES correlation, Autoloop live/offline identity mapping, source credential transport, listener and client network scope, direct page access and the absence of HTTP write methods. The browser acceptance checks use the running HTTPS service and cover seven views, actual records, dialogs, filters, write-control explanations and responsive layout.

## V1.1 conversational intake

Open **工程任务 → 新建工程任务** or /#intake. The workspace saves free-text turns and requirement fields in a resumable local draft. Select the Runtime project to load its committed context and the pinned PCP baseline, then use task-specific keywords to retrieve experience in maturity order. Candidate and Inbox material stays visible as non-authoritative evidence in the brief. It is excluded from the EO input references.

The active service uses a private intake-drafts directory beside dashboard.json. Set intake.directory and intake.pcp_repo in the service configuration to enable this feature in another existing installation. The store uses 0700 directory permissions, 0600 draft files, atomic replacement, and draft-version checks for concurrent tabs. Every generated package keeps its source references, revision, and confirmation timestamp.

Generate a package to preview and download the combined requirement brief and the EO Job and Workorder YAML drafts. Confirming a revision records a local document decision. Current deployment has no authorized EO write interface and no configured Intake LLM endpoint, model, or authentication. Manual capture, source retrieval, revision and export work through the same local and LAN HTTPS service.

Run python3 -B -m unittest discover -s dashboard -v for the targeted backend tests. Browser evidence covers task entry, manual conversation, source provenance, export, stale revision handling and reopening the saved draft across refresh, a fresh Edge context and a real service restart.

## V1.2 engineering planning

In the existing Intake workspace, confirm the current requirements document before generating or editing an engineering plan. The local HTTPS listener can ask the configured existing Ruflo Supervisor for a proposal. The server sends the confirmed dossier, document revision and exact source references. It validates the returned JSON before storing a suggested plan in the same intake draft. LAN clients can read and edit drafts and cannot invoke the model. The plan panel records the actual Supervisor, response model, receipt ID and requested effort. Response effort is reported as unexposed.

The plan versions maintain task dependencies, manual order, proposed Worker configuration, risk and proposed authorization. Suggestion, Manual and Autonomous mode are local planning choices. Confirming a plan records a document decision. The current deployment lacks an authorized EO creation path and an effective ES authorization/dispatch link. The dashboard presents existing run and review data as source-owned evidence and shows that an unbound plan has no corresponding Run or Worker.

The enabled private intake.planner configuration refers to the existing local Ruflo adapter, Supervisor working directory and observed loopback route. The same service still serves 127.0.0.1:8787 and 192.168.5.4:8787. To stop or restart it, use systemctl --user stop pcp-dashboard-v1.service or systemctl --user restart pcp-dashboard-v1.service. Browser viewing uses the same TLS certificate and LAN boundary.

The private planner contract pins the existing Node executable and Ruflo launcher, tool and core. The adapter passes read-back-verified sealed copies of those three modules into the Node process and checks the compiled-source receipt before calling the Supervisor. A failed contract or missing same-request model receipt blocks plan generation. The service can still read saved plans and accept local draft edits.

The V1.2 handoff pauses normal model requests by omitting `intake.planner` from the private service configuration. Local model requests return 503 and LAN model requests return 403. The saved drafts and history remain available. The release decision requires independent execution of the review checks and evidence of operator authorization for model generation.

## V1.2 D01 execution continuation

The existing private `dashboard.json` can grant model actions to the local service operator. The service checks the ownership and permissions of the file it opened. A state-changing privileged request requires the real loopback listener, a loopback peer and an exact HTTPS Origin. The configured LAN continues to support anonymous browsing and draft editing.

A formal grant binds the non-production operation to one intake draft. EO writes use the configured branch, immutable template and schema commit, and Git object storage. ES uses the existing ExecutionKernel checkout and SQLite store. The request pins the committed Workorder and the Hub event is keyed by the kernel-issued Invocation. The plan and execution panels show distinct records for formal authorization, the provider receipt and the ES result.

The recovered Autoloop Hub uses its existing database and loopback port. The Worker retains its registered identity and uses a separate recovery directory to avoid automatically resuming the archived Run 28.
