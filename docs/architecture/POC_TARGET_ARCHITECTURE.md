# Target Architecture — First Vertical POC

## Target composition

~~~text
EO Job + Workorder
       |
       v
ES ExecutionKernel: ExecutionRequest / Execution / Attempt / Invocation / authority
       ^
       | canonical updates
       |
Ruflo Supervisor <----> PCP Runtime Adapter / MCP tools
                              |
                              v
                        Autoloop Hub
                              |
                   outbound HTTPS long-poll
                              |
                              v
                   Remote Autoloop Worker
                              |
                              v
                    Codex in isolated Worktree
                              |
                    provider result / evidence
                              v
                     Adapter -> ES result
                              |
             +----------------+----------------+
             |                                 |
    Ruflo independent Reviewer          Product QA
             |                                 |
             +----------------+----------------+
                              v
                       ES Review decision
                              |
                              v
                    EO Result / Evidence / Review
~~~

Ruflo supervises complex work. Autoloop provides Hub/Worker execution. The PCP Runtime Adapter is a thin boundary adapter, not another scheduler.

## Execution lanes

- L0 business API: Application -> authorized CB/API adapter -> allowlisted external API -> structured result. No Ruflo, Autoloop or Codex. This is the user's intended lightweight path; this POC does not modify CB or claim a generic API adapter already exists.
- L1 simple engineering: EO Workorder -> ES authorization -> Autoloop Hub -> one Worker -> Codex -> evidence / Review.
- L2 complex engineering: EO Workorder -> ES authorization -> Ruflo Supervisor -> Adapter -> Autoloop Hub -> multiple isolated Workers -> independent Review / Product QA -> EO acceptance.

Prove one Worker first. Add a second Worker only after the single-Worker chain passes.

## Canonical correlation

- EO owns Workorder intent and acceptance.
- ES accepts a frozen ExecutionRequest and creates Execution / Attempt / Invocation / authority before provider dispatch.
- Derive Autoloop event ID from ES execution_id + attempt_id; do not add a second task database.
- One Autoloop Hub run maps to one ES Invocation. Record its run ID as the ES runtime reference when the Worker actually starts.
- Autoloop internal turns/retries stay inside that same run and ES Attempt. A new PCP Attempt requires new ES authorization.
- Worker heartbeat, process liveness, Autoloop completion, ES result acceptance, Review and EO acceptance are distinct facts.

## Verified Autoloop remote path

The pinned Fork has separate Hub and Worker configurations. A Worker-only host uses Hub URL + its Worker key and initiates HTTP long-poll to the Hub. Worker inbound ports are not required. The Hub needs a secure reachable endpoint; non-loopback listeners must be protected by HTTPS.

Autoloop rules are trusted configuration. Event text is untrusted task data and cannot select arbitrary command, credentials, repository, path or permissions.

## Worktree isolation

Each execution uses a unique Worker-local worktree based on the frozen target SHA, a unique branch, bounded workspace-write access and recorded commit/test evidence. Parallel Workers never share a writable worktree. If dynamic path selection is required, use a wrapper/adapter that validates repository and path against an allowlist. Do not accept arbitrary cwd or shell commands from events.

## Ruflo integration

The POC must verify the actual Ruflo install command and MCP entry point at the pinned version. A small MCP adapter owned here exposes only the operations needed to submit an authorized execution, dispatch/read Autoloop status, retrieve evidence and request Review. Do not expose raw ES mutation methods to arbitrary agents. Reviewer context is separate and read-only. Ruflo does not gain PCP execution or production authority.

## Current EO / ES facts

- EO V0.1 already defines Job, Workorder, Result, Evidence and Review schemas/templates. Reuse them without schema changes.
- ES V0.3 fixes Runtime Binding / Provider boundaries. Current code has an embedded Python ExecutionKernel with submit, authorize, start, result, failure and review operations; no general HTTP/MCP server is present.
- The POC may wrap the existing kernel locally from this repository. Do not duplicate its database/state machine or patch ES in this POC.
- If a required ES operation is absent, report the exact contract/code gap instead of inventing a transition.

## Security and POC boundary

Separate least-privilege Hub/Worker credentials; no secrets in events/logs/Git; HTTPS for remote Hub access; no stale ES authority; no production or customer data. The first POC proves one real EO Workorder, one ES-authorized execution, one actual Codex Worker, one isolated fixture change, independent Review, Product QA and EO evidence return. A same-host Worker is setup evidence only, not cross-host proof.
