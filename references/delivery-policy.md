# Delivery Policy

Workflow revision: `ai-team-2026-08-12-r13`.

This is the single global authority for AI-team delivery lanes, states, gates, handoffs, validation, severity, acceptance, and re-entry. Copy it to `.ai-team/governance/workflow.md` during project initialization. The project-local copy is the runtime authority for that project.

Resolve all paths from `.ai-team/manifest.md`. Machine-readable active enums, compact field groups, stage authorization, and table contracts come from `governance/workflow-schema.json`; exact Markdown syntax comes from `governance/templates.md`.

## Delivery path

```text
source intake → product analysis → UX/UI design when needed
→ engineering baseline/review when needed → technical design/security review
→ testability and task-design review → implementation readiness
→ one serial implementation engineer → independent verification plus triggered code/security review
→ state complete + technical outcome verified-complete → next eligible task
→ named human acceptance checkpoint only when declared
```

The product analyst owns intended behavior. The UX/UI designer owns unspecified experience details when active. The technical lead owns implementation constraints and contracts. The independent verifier owns testability and quality verdicts. Detailed role boundaries are defined only in `governance/roles.md`.

## Sources and intake

- Initialize the canonical source-register schema and register a PRD or the verbatim initial request before creating promoted task state. A PRD is preferred, not mandatory. Figma and Demo are optional evidence.
- The current product-requirement source must be `provided` or `no-prd intake`. Move superseded sources to history and replace the current entry; a superseded entry cannot authorize promoted work.
- For a no-PRD request, create a lightweight acceptance specification. Classify each rule as evidence-backed, a reversible low-risk assumption with rationale, or awaiting a material human decision. An independent verifier freezes it only when scope, traceability, and testability are complete.
- Before Standard/High-risk task promotion, freeze one project acceptance specification with an explicit REQ catalog and one project traceability matrix. Every catalogued requirement appears exactly once as covered, out of scope, or awaiting decision; covered rows map AC, TASK, and TEST IDs. A standalone Fast non-behavior task may use its card-local source/traceability instead when both project specification files are intentionally absent; if either project file exists, validate both normally.
- Before browsing a Demo, list current-phase flows/pages/routes and excluded legacy behavior. Authorized login, navigation, pagination, and non-mutating search/filter actions are allowed. Do not create or change business data, settings, permissions, or external state unless the user separately authorizes a reversible test action. Record pages, time, observations, exclusions, actions, cleanup, and access gaps.
- Activate UX/UI only when a UI task remains underspecified after product analysis and existing Figma, Demo, and design-system evidence are considered. Do not redesign supplied evidence.

## Execution lanes

Record one lane before task design.

- `fast`: first require a positive whitelist match—pure documentation, comments, copy/text, style/token constants, or local test additions with no business-behavior change. Then confirm no contract/schema/generated-code, authentication/authorization, sensitive-data, dependency, external-service, transaction, worker/async, runtime-chain, material UX, or baseline trigger. If the task is not clearly whitelisted, use `standard`.
- `standard`: ordinary M/L work or shared UI, data, module, compatibility, or regression impact.
- `high-risk`: XL work or any security, permission, sensitive-data, protocol, migration, transaction, worker/async, external side effect, or production-capability boundary.

Fast path uses the compact `Fast merged design/readiness` plus `Fast execution and verification` sections and may claim `implementation-ready` directly when its verifier verdict and project stage pass. It omits Standard planning and all untriggered annexes but never removes traceability, acceptance evidence, independent verification, or scope checks. Reclassify whenever the change surface grows.

## State and outcome model

| Concept | Allowed values | Meaning |
| --- | --- | --- |
| Task state | `analysis`, `awaiting-human-decision`, `task-design-ready`, `implementation-ready`, `implementing`, `awaiting-verification`, `complete`, `cancelled/superseded` | Workflow position |
| Additive blocker | `design-blocked`, `implementation-blocked` | Reason work cannot advance; retains the last valid state |
| Technical outcome | `not-complete`, `verified-complete` | Evidence-backed completion result |
| Acceptance checkpoint | named ID plus `blocking` or `non-blocking` mode and `pending`, `accepted`, `rejected`, or `conditional` status; otherwise `none` / `not-required` | Human product review boundary |

`complete` is the task state. `verified-complete` is the technical outcome that justifies it; they are not competing states. A named checkpoint may group completed tasks and does not change their technical outcome.

```text
analysis → task-design-ready → implementation-ready → implementing → awaiting-verification → complete
    │              │                    │                    │
    ├─ awaiting-human-decision          ├─ implementation-blocked
    └─ design-blocked                   └─ return to implementing on P1
```

## Gate authority

The following checklists are normative. Supporting prose explains evidence and exceptions; when wording differs, the checklist controls.

### Engineering baseline PASS

Required for a greenfield project and after a material baseline change:

1. Platforms, language/runtime/package manager, frameworks, module boundaries, transport/data/auth/configuration boundaries, local commands, test frameworks, environment/data/reset, and external constraints are recorded.
2. The technical lead authored the baseline.
3. An independent verifier confirmed source alignment, coverage, executable commands, and testability.

An existing repository derives these constraints from manifests, configuration, code, and tests. Preserve its established stack unless a task requires change.

### Task-design-ready

1. Every in-scope requirement is covered, out of scope with reason, or awaiting a decision.
2. Observable acceptance criteria map `REQ → AC → TEST → TASK → evidence`.
3. The compact card references project-level source/baseline/design evidence and records one control-trigger set. `none` requires a concrete rationale; triggered experience, Web UI, interface, security, runtime-chain, TestSprite, or baseline-change treatment uses only its applicable annex/reference.
4. An interface trigger requires a frozen contract reference and contract-test IDs; absence of the trigger means no interface/protocol change is in task scope.
5. Required test accounts, fixtures, dependencies, reset method, commands, and evidence expectations are defined.
6. Security and runtime-chain treatment is complete when triggered.
7. Artifact-author and independent-reviewer identities are recorded; product, UX, and technical authors do not approve the delivery artifacts they authored. The verifier may own the compact task Test Manifest while assessing those source artifacts.

Pending upstream implementation or a closed project stage is an implementation blocker, not a design failure, when the upstream contract is frozen.

### Implementation-ready

1. Design dependencies are frozen.
2. Implementation dependencies and environment are ready.
3. The task has a current independent implementation-readiness PASS, issued directly or activated from an uninvalidated conditional PASS after only its enumerated mechanical conditions became true.
4. Assigned batch entry criteria pass, or the card records `batch-not-applicable`.
5. No human decision or P0/P1 blocks the task.
6. The manifest-declared project stage is `implementation-authorized` for the task scope. A user's local build/change/fix request authorizes the coordinator to set that stage unless the user explicitly limits work to analysis; never invent another human implementation gate.

#### Standard combined readiness

- Use one verifier planning assignment to produce the compact Test Manifest, task-design verdict, and either a direct implementation-readiness verdict or a conditional PASS.
- Limit a conditional PASS to enumerated mechanical conditions: named dependency completion, environment/command evidence, batch entry, blocker clearance, or opening an explicitly recorded stage restriction. Preserve the verifier verdict and separately record activation status, mechanical conditions, evidence, and invalidation triggers.
- While activation status is `pending`, keep the task `task-design-ready` with an implementation blocker.
- Let the coordinator set activation status to `activated` without another verifier assignment only when those exact conditions become true. Record activation evidence, then set `implementation-ready`; never rewrite the verifier's original verdict.
- Require a fresh verifier review for any unlisted discrepancy or change to source, requirement, design, contract, test manifest, risk treatment, or relevant environment assumption.
- Exclude High-risk tasks; they always receive a separate current implementation-readiness review after task design.

### Technical completion

1. The change remains within approved scope or has a confirmed decision.
2. Implementation self-check records build/generation/lint/type-check, required tests, omissions, and residual risks.
3. Required owner, affected/regression, contract, final-suite, and independent risk evidence is valid.
4. The independent verifier records a fresh verification-phase PASS bound to the current Snapshot ID, Test Manifest revision, fingerprinted candidate, and verification time. A PASS field begins with explicit status `PASS`; `NOT PASS` or other prose containing the word does not pass.
5. Fast and ordinary Standard work may use one independent verifier for diff review and test verification. High-risk work and interface, security, runtime-chain, or material baseline triggers require a separate current code-security-phase evidence record. No unresolved P0/P1 remains.
6. The implementation engineer differs from the independent verifier; any separately required code/security reviewer differs from both. Product/technical artifact authors do not approve their own work.
7. Required fingerprint policy and strict validation pass.
8. Set task state `complete` and technical outcome `verified-complete`, then continue unless a named checkpoint blocks the covered scope.

## Task planning and batches

- Maintain one Markdown backlog and one unique card per task. Task IDs are monotonic and never reused.
- Record complexity S/M/L/XL with concrete drivers. Complexity is a risk/planning signal, not a time promise. Split XL work when independently testable slices exist.
- A batch records objective, members, duplicate-free serial order, entry criteria, exit evidence, and any named acceptance checkpoint with mode and status. It never bulk-promotes tasks; each card needs its own readiness and verification.
- Do not start a later member before every earlier member in that batch's serial order is complete. More than one task may not be `implementing` at once.
- Run focused owner/affected verification for each ordinary task and one approved full regression at batch exit. High-risk work may retain a per-task full suite. A batch regression failure re-enters only affected completed tasks.
- A completed batch with a pending blocking checkpoint stops later batches and produces a human-readable checkpoint package. A non-blocking checkpoint does not pause otherwise eligible work.
- Rejected or conditional acceptance preserves accepted scope and autonomously re-enters only affected requirements/tasks; conditional status remains blocking until its recorded conditions become verified or the human changes the checkpoint outcome.
- Separate design dependencies from implementation dependencies. Continue downstream design from frozen upstream contracts.

## Handoffs and validation

- The active compact Handoff Snapshot plus its project-level references are the default cross-role context. Field groups come from the Schema and exact Markdown syntax from `governance/templates.md`; do not reproduce their lists here or elsewhere.
- The compact task card is the canonical task delta, state, manifest reference, gate summary, and completion record. Project-wide facts remain in their project artifacts; supporting evidence may not override the card.
- Bound ordinary assignments to the snapshot's exact project references; `Shared assignment contract` plus the assigned role section from `governance/roles.md`; the specifically named workflow section or gate checklist; and only the artifact template section being changed.
- Use `<script-root>/extract_markdown_section.py <markdown-file> "<H2 heading>"` for bounded reads when available. It ignores headings inside fenced examples; do not use brittle line-number ranges.
- Read complete authority files only during initialization, workflow revision, or when an evidenced cross-section conflict cannot be resolved from the cited sections. The coordinator names the required headings in every assignment.
- Keep raw logs and superseded snapshots/manifests/verdicts in `.ai-team/evidence/`; link only current evidence from the compact card.
- Refresh the snapshot or compact Test Manifest reference after material source, decision, contract, code, test, command, fixture, environment, finding, or next-action changes.
- Record the review phase in every Review evidence record. Design/readiness records remain historical inputs at completion and retain their original Snapshot binding while still matching the current frozen Manifest; a Manifest or design-input change invalidates them. Verification and code-security records must bind the current completion Snapshot and Manifest. Never substitute one phase's PASS for another.
- At a boundary, run `<script-root>/check_project_consistency.py <project-root> --task TASK-... --gate <task-design|implementation-ready|verified-complete> --next-action`. It combines task, project, fingerprint, backlog, and continuation checks. Use `validate_task_handoff.py --strict` only for focused card debugging.
- For code, protocol, generated-output, dependency, runtime, Standard, or High-risk work, use `Fingerprint policy: required`. A pure Fast-path documentation/style/metadata task may use a reasoned `N/A`.
- Gate validation locates the nearest ancestor manifest, rejects duplicate authoritative sections or fenced/comment-only fields, cross-checks Snapshot/Manifest revisions, validates state/outcome, reviewer separation, dispositions, test environment, scoped gate semantics, and linked local evidence, confirms the project authority layout, and automatically verifies required project-relative SHA-256 ledger entries. Before implementation, the inventory may include planned new files while the ledger freezes existing inputs. At `verified-complete`, regenerate from the actual files: the declared inventory must equal the ledger path set. Validation does not run project commands or prove test-result truth.

## Test execution

- The independent verifier freezes one compact task Test Manifest reference before implementation. Project-default commands remain in the engineering baseline; the card records task-specific implementer checks, independent checks, batch regression, risk/contract checks, and environment differences.
- The implementation engineer runs focused owner/affected checks while iterating. The independent verifier runs fresh task acceptance and affected-regression checks against the current candidate.
- Ordinary Standard work runs the approved full regression once at batch exit, not once per task. High-risk work may require it for each candidate. A batch regression failure re-enters affected tasks with the failing evidence.
- For Fast and ordinary Standard work without a separate-review trigger, the verifier combines independent diff review and test verification in one assignment. When a separate review is triggered, its scoped fast-gate precedes expensive independent regression.
- `Fresh` means independently running frozen commands against the current candidate; it does not mean creating a new Agent process. Reuse the same verifier within the frozen task/batch scope after it reads the refreshed Snapshot and diff.
- On deterministic P0/P1, capture the manifest revision, executed groups/results, unexecuted groups, and stop reason; stop unrelated broad execution and return to focused rework.
- Changes to implementation, tests, commands, fixtures, contracts, or relevant environment invalidate affected evidence. Reuse unaffected evidence only with a recorded impact proof.
- If two consecutive candidates produce new P1 findings, perform task-scoped technical re-entry before another broad run. Classify findings as implementation remediation, correctable design gap, or material scope/contract decision; continue the first two autonomously and escalate only the third.

## Contract, runtime, and security treatment

- For a changed interface/protocol, freeze surface, fields/defaults, errors, compatibility/versioning, authorization, and applicable idempotency/retry/ordering/concurrency/transaction behavior. The verifier authors stable contract-test IDs before implementation.
- For a state machine, worker, async job, transaction, authorization boundary, or external side effect, map `entry → authorization/precondition → scheduling/claim → state transition → side effect → recovery/compensation → observable result` to requirements, acceptance criteria, modules, and entry-path tests. Mock-only coverage of a critical stage fails design.
- Shift security left for authentication, authorization, sensitive data, payment, upload, user-controlled input/URLs, secrets, dependencies, third-party APIs, or webhooks. Map trust boundaries, abuse cases, mitigations, and negative tests before design finalization; repeat diff-directed review after implementation.

## Finding severity

Finding severity is distinct from backlog priority.

- `P0`: credible security/data exposure, irreversible loss/corruption, or inability to deliver safely. Block and escalate immediately.
- `P1`: acceptance criterion, required regression, or security control not met. Return to implementation; do not request human acceptance.
- `P2`: non-blocking improvement. Create an evidence-linked follow-up task; do not silently discard it or block completion.

Record severity, reproduction evidence, affected REQ/AC/TEST, disposition, and follow-up link. Unresolved P0/P1 blocks completion.

## Human decisions and acceptance

- Decide autonomously from sufficient sources, confirmed decisions, scoped Demo/Figma evidence, code, tests, and reversible local conventions.
- Create one decision card only for unresolved evidence conflict, missing scope/acceptance, unavailable authority, or material irreversible, security, privacy, permission, external-cost, or production impact. Present and record one dependency-ordered decision at a time.
- Do not escalate normal internal structure, naming, task split/order/batching, test strategy, local pattern reuse, traceability completion, regression tests, or document consistency when evidence determines the answer.
- Verification PASS is a quality verdict, not a human decision. Human acceptance is required only at a named batch, milestone, end-to-end flow, or user-requested checkpoint.
- A checkpoint package states scope, product outcome, in/out-of-scope changes, evidence, limitations/risks, artifact links, and one accept/reject/conditional choice. Never request acceptance with only a task ID.

## Change and feedback re-entry

- Distinguish defects from requirement changes. A defect preserves valid expectations and adds missing regression coverage; a changed requirement updates affected cases and retains superseded history.
- On rejection or scope change, update the existing cards and backlog, preserve historical evidence, and analyze affected requirements, acceptance criteria, tests, modules, interfaces/data, baseline constraints, and dependents.
- Preserve unaffected accepted items as a logical baseline. Return affected work to analysis or awaiting decision and require affected-scope readiness before implementation resumes.
- A material engineering-baseline change requires impact analysis, artifact updates, and an independent affected-scope Engineering baseline PASS.
- A task may become `cancelled/superseded` only with a dated feedback/change record that identifies the cancelling or replacement evidence, affected REQ/TASK scope, and concrete next action. Cancellation is not a shortcut around verification.

## Autonomous progression and turn boundary

- After every governance, design, readiness, remediation, or verified-completion handoff, start the next eligible action without waiting for a human prompt.
- After a clean project consistency check, run it with `--next-action`; when it prints an eligible local action, dispatch or execute that action instead of returning a next-step report.
- A closed implementation stage or pending upstream code does not stop allowed design, test, security, or review work when contracts are frozen.
- Before returning, inspect the backlog. Stop only for a genuine human decision, missing required external evidence/authority, completion of all allowed work, a user pause/status request, or forced turn end.
- Codex is not a background daemon. When a turn must end with work open, record the exact continuation point in the active task artifact.

## Tool use and degradation

- Use scoped `$repomix-explorer` for unfamiliar or large repositories. Keep raw packs temporary and local; exclude secrets/generated/unrelated data. For known symbols, use targeted local search.
- An unavailable optional Figma, Repomix, TestSprite, browser route, or convenience tool is not by itself a blocker. Continue with targeted source/code evidence or provider-neutral tests and record the limitation. Treat it as a hard evidence gap only when that source or capability is explicitly required for acceptance or is the sole authority for a material rule.
- TestSprite MCP is optional Web UI-only automation for an authorized local service. Draft provider-neutral cases before implementation; implementation may run approved cases as self-check and the verifier reruns them independently. It never replaces unit, integration, or contract tests and blocks completion only when explicitly required.
- Never claim unavailable-tool evidence as PASS. Do not install/configure external tools, expose credentials, target production, or deploy without separate authority.
