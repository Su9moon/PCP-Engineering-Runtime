# Conversational Engineering Intake — Design V1.1

- Date: 2026-11-26
- Status: **DESIGN DRAFT — user accepted the product direction; 2026-11-26 revision makes durable cross-session continuation and evidence-backed project experience reuse required implementation outcomes**
- Product: PCP Engineering Control Center
- Parent design: \`design/pcp-engineering-control-center-demo.html\`
- Companion prototype: \`design/pcp-engineering-control-center-conversational-intake-demo.html\`

## 1. Product decision

Replace the conventional **New Engineering Task** form/modal with a **Conversational Engineering Intake** workspace.

The user starts with an outcome, problem, or rough idea. The assistant progressively clarifies the requirement through adaptive multi-turn dialogue. The user does not need to know EO schemas, technical workorder formats, Agent roles, or execution settings.

The experience has five linked outputs:

1. Conversation — understand intent and clarify the most important missing information.
2. Requirement dossier — maintain a live, editable summary with provenance.
3. Engineering document package — generate draft documents from the dossier.
4. Canonical EO work item — create the EO Job/Workorder only after explicit user confirmation.
5. Continuity and project context — preserve the intake across sessions and reuse relevant project baselines and experience with visible source provenance.

**Conversation is the entry point; the dossier is the working summary; approved documents are the durable project artifacts; EO remains the canonical engineering-work authority.**

## 2. Interaction model

### 2.1 Adaptive dialogue

- Begin with a free-text prompt, not a required form.
- Ask one high-value clarification at a time.
- Choose the next question from the current requirement gaps and the user's latest answer; do not follow a rigid questionnaire.
- Offer optional quick replies when useful, while always allowing free-text answers.
- Let the user change direction, correct previous answers, or add constraints at any time.
- Reuse only relevant project context and exact governing references; do not dump the whole project history into the conversation.
- Do not repeatedly ask for information already established in the current dossier or authoritative project records.

### 2.2 Live requirement dossier

Display a side panel that updates as the conversation progresses. It should include, as applicable:

- Goal / problem to solve
- Target project and repository
- Users / operating context
- Scope and expected outcomes
- Constraints and dependencies
- Desired deliverables
- Acceptance criteria
- Risks and unresolved questions
- Suggested execution approach

Every material item must carry one of four provenance states:

| State | Meaning |
|---|---|
| User-confirmed | Explicitly stated or confirmed by the user |
| AI suggestion | A recommendation, not an approved requirement |
| AI inference | A provisional interpretation derived from evidence |
| Unresolved | Information not yet established |

The user can edit or reject AI suggestions and inferences. Never silently promote an AI inference into a user-confirmed fact.

### 2.3 Draft-first behavior

- The assistant may generate a useful first draft even when some details remain unknown.
- Unknowns must be labelled and carried into the document package; they are not automatic blockers.
- The assistant should explain material assumptions and distinguish them from confirmed facts.
- Users can revise the conversation or dossier and regenerate affected documents.

## 3. Document package

Generate only the documents justified by task complexity. Small tasks may combine sections into one concise brief; complex projects may produce separate files.

Potential package contents:

1. Requirement brief — problem, goal, users, scope, constraints and expected outcomes.
2. Product / interaction design — user journeys, UI behavior and functional requirements.
3. Technical design — architecture, interfaces, dependencies and data ownership, when needed.
4. Implementation plan — phases, work breakdown, dependencies and deliverables.
5. Execution recommendation — advisory complexity, suggested Agent/Worker arrangement and model profile; never an authorization.
6. Acceptance plan — observable acceptance criteria and focused validation.
7. EO Job + Workorder draft — mapped to the existing canonical EO schemas.

Documents are drafts until the user explicitly confirms them. The system must support review and correction before formal work-item creation.

## 4. Authority and integration boundaries

- The user is the final authority for requirements, assumptions, document approval and work activation.
- EO remains authoritative for Job, Workorder, Result, Evidence and Job-level Review.
- ES remains authoritative for ExecutionRequest, Execution, Attempt, Invocation and execution authorization.
- Creating an EO Workorder does **not** create an ES Execution or authorize a Worker.
- No Ruflo/Autoloop dispatch, retry, cancellation, or execution control is exposed by the intake conversation.
- The intake assistant may use an LLM for requirement clarification and document drafting, but it does not receive Ruflo, Autoloop or ES control tools.
- GPT ↔ Ruflo direct management remains deferred under the existing V1 continuation boundary. This design does not implement or imply that integration.

## 5. Project context and persistence

### 5.1 Project selection and context

- Use the existing project/repository selector and registry. Preserve the selected project's exact repository identity, local workspace reference and relevant branch/commit when available.
- For the selected project, load only its relevant `AGENTS.md`, README/status, current baseline, active workorder, applicable decisions and directly related implementation/evidence.
- Reuse exact repository/path/commit references in the dossier and generated documents. Never invent a project identity, branch, commit or source.
- If no project is selected, clarify whether this is a new project or work on an existing one before assigning a project identity.

### 5.2 Experience retrieval and maturity

- Reuse the PCP experience process at `Su9moon/personal-ai-control-plane:processes/experience-reuse-gate.md`.
- Retrieve in this order: approved governance/baselines and validated assets; then relevant candidates; consult Inbox sources only when the first searches do not resolve the task context.
- Approved governance and validated assets may guide the work as approved guidance. Candidate and Inbox assets are evidence only; never silently promote them into requirements or authoritative instructions.
- Search only for terms and concepts relevant to the current requirement, within the selected project and the applicable PCP experience paths. Do not scan all repositories or the full experience store on every turn.
- Show each material reused source with its exact repository/path and commit/ref when available, plus its maturity/authority status and why it is relevant. Distinguish project facts from reusable experience and AI interpretation.
- If a source cannot be accessed, state the exact unavailable source/capability. Do not claim that experience retrieval succeeded when it did not.

### 5.3 Durable intake sessions

- Treat each intake as a resumable draft, not an ephemeral chat.
- Persist the conversation transcript, selected project/repository identity, dossier fields and their provenance, unresolved questions, source references, generated document package and version history, approval state, and last-updated timestamp.
- Automatically save after each user/assistant turn and after dossier or document changes.
- Provide a visible list of recent/in-progress intake drafts. The user can reopen one and continue from its last saved state after page refresh, a new browser session, or Dashboard service restart.
- On resume, restore confirmed facts, provenance, relevant source references, unresolved questions and document versions. Do not repeat already answered questions unless the user changes the requirement or the source facts have changed.
- Keep separate projects' intake context isolated. Never silently carry one project's requirements or evidence into another project's session.

### 5.4 Persistence implementation boundary

- Inspect the existing Dashboard backend, database and project/file storage first; reuse the existing persistence capability when suitable.
- If no suitable persistence exists, implement only the smallest server-side, project-local draft store using the Dashboard's existing application-data boundary (for example, atomic JSON files in its private data directory). This is a bounded feature implementation, not a new general database, task ledger, Agent Memory platform or persistence service.
- Use generated session identifiers, server-side path confinement and the application's existing access/session boundary. Do not store API keys, credentials or secrets in transcripts or draft records.
- Do not use browser localStorage as the sole durable store, and do not write active conversation state into tracked source files.
- If a real technical or permission constraint prevents durable persistence, report the exact blocker and do not mark cross-session continuation complete. Continue independent UI, dialogue and export work where possible.

### 5.5 Approved documents

- Final approved documents should be exportable and associated with the selected project using an existing authorized file/Git workflow.
- Preserve prior document revisions when regenerating; do not silently overwrite an approved or previously reviewed version.
- Do not auto-commit or push without the existing authorized Git workflow.

## 6. Main workspace layout

- Primary area: conversation timeline, assistant messages, user replies, optional suggestion chips and free-text composer.
- Side area: live editable requirement dossier, provenance labels, unresolved questions, AI suggestions/inferences and the sources reused from project baselines/experience.
- Document area: generated package, per-document preview, revision/regeneration and approval state.
- Session area: recent/in-progress drafts with project identity, last-updated time and a clear resume action.
- Source references must be inspectable; show exact repository/path and ref/commit where available, not merely a generic "knowledge used" indicator.
- Primary entry: existing **New Engineering Task** action opens this conversation workspace.
- Keep the existing seven Dashboard sections and their source-of-truth boundaries intact.

## 7. LLM provider boundary

The design is provider-neutral. The eventual implementation must inspect existing local provider configuration and use an authorized server-side integration if available.

- Do not hard-code an API key or expose credentials to browser code.
- Do not silently choose a provider or substitute a model.
- If no provider is configured, keep the requirement draft editable and show the precise missing configuration; do not pretend an AI response or generated document came from a live model.
- LLM connectivity and PCP governance connectivity remain separate dimensions.

The concrete provider, endpoint, model and credential source remain an implementation decision; this design does not authorize adding credentials or selecting a paid service.

## 8. V1.1 design prototype boundary

The companion HTML is an interaction prototype only. It simulates dialogue, dossier updates and document preview in browser memory.

It does **not**:
- call a live LLM;
- retrieve live project baselines or PCP experience;
- persist or resume intake sessions across browser sessions/restarts;
- maintain durable document revision history;
- write EO Job/Workorder records;
- create ES executions or authorize workers;
- connect to Ruflo or Autoloop;
- deploy or change the cbnet Dashboard service.

The production implementation must not treat the prototype's scripted replies, in-memory state or simulated buttons as evidence that these capabilities are connected.

## 9. Architecture governance and experience reuse

The existing PCP decision remains authoritative:

\`\`\`yaml
architecture_gate:
  required: true
  status: complete
  real_use_evidence: verified
  decision: INTEGRATE
  governing_decision: "Su9moon/personal-ai-control-plane@22bae955686f03c5f440cdcd66e13a69f1289f90:governance/adr/ADR-2026-11-22-001_pcp-engineering-runtime.md"
  pcp_specific_remainder: "Conversational requirement clarification, provenance-aware requirement dossier, approved document package, and mapping to the existing EO Job/Workorder authority."
  minimum_formalization: "A Dashboard intake UI and thin LLM/document/EO adapters where supported; no parallel task ledger, execution authority, scheduler, or generic orchestration runtime."
\`\`\`

Experience reuse: **REUSE / EXTEND**, scope **PROJECT_LOCAL**. Reuse the existing PCP Engineering Runtime ADR, AGENTS.md, Dashboard V1 workorders, EO schemas, ES authority boundaries, and existing design demo. Do not create another Architecture Gate or repeat the completed cross-domain discovery.

## 10. Open implementation decisions

These are implementation facts to inspect in the actual local Dashboard workspace, not reasons to downgrade the accepted product behavior:

1. Which existing LLM API/provider configuration can power live dialogue and document drafting.
2. Which existing project/repository and PCP experience retrieval interfaces are already available to the Dashboard, and what exact read access they provide.
3. Which existing Dashboard database/application-data directory should persist resumable intake sessions; if none is suitable, use the bounded project-local server-side store described in Section 5.4.
4. The exact local Dashboard implementation branch, current runtime state and existing service boundary; the executor must inspect the user's actual local workspace before editing.

Do not guess a provider, source connection, storage path, branch or runtime fact. Report exact gaps while completing independent work.

## 11. Design acceptance

- The primary task-entry action opens a conversation workspace, not a conventional task form.
- The conversation supports free-text replies and optional suggestions.
- The assistant asks adaptive, focused follow-up questions rather than presenting a fixed questionnaire.
- The dossier visibly distinguishes user-confirmed, AI-suggested, AI-inferred and unresolved items.
- Users can correct the dossier and change direction.
- A document package can be generated while retaining explicit unresolved items.
- Documents can be previewed and revised before confirmation; regeneration preserves prior document revisions.
- An intake draft is automatically persisted and can be reopened after refresh, a new browser session and Dashboard service restart.
- Resume restores the transcript, selected project, dossier provenance, unresolved questions, source references and document revisions without losing confirmed facts.
- Relevant project baselines and experience are retrieved using the approved-governance/validated/candidate/Inbox maturity order; exact source paths and refs are visible.
- Candidate and Inbox material is never presented as authoritative guidance; inaccessible sources are reported honestly.
- Explicit user confirmation is required before EO Job/Workorder creation.
- No ES execution or Ruflo/Autoloop run is created by the intake flow.
- The prototype labels all simulated operations truthfully and does not claim backend integration.
- Existing dashboard sections and V1 authority boundaries are preserved.
