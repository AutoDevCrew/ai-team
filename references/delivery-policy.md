# Delivery Policy

This is the single global authority for AI-team delivery lanes, states, gates, handoffs, validation, severity, acceptance, and re-entry. Copy it to `.ai-team/governance/workflow.md` during project initialization or migration. The project-local copy is the runtime authority for that project.

Resolve all paths from `.ai-team/manifest.md`. Exact artifact field names and Markdown syntax come only from `governance/templates.md`.

## Delivery path

```text
source intake → product analysis → UX/UI design when needed
→ engineering baseline/review when needed → technical design/security review
→ testability and task-design review → implementation readiness
→ one serial implementation engineer → independent verification and code/security review
→ state complete + technical outcome verified-complete → next eligible task
→ named human acceptance checkpoint only when declared
```

The product analyst owns intended behavior. The UX/UI designer owns unspecified experience details when active. The technical lead owns implementation constraints and contracts. The independent verifier owns testability and quality verdicts. Detailed role boundaries are defined only in `governance/roles.md`.

## Sources and intake

- Register a PRD or the verbatim initial request in the source register. A PRD is preferred, not mandatory. Figma and Demo are optional evidence.
- For a no-PRD request, create a lightweight acceptance specification. Classify each rule as evidence-backed, a reversible low-risk assumption with rationale, or awaiting a material human decision. An independent verifier freezes it only when scope, traceability, and testability are complete.
- Before browsing a Demo, list current-phase flows/pages/routes and excluded legacy behavior. Inspect only that scope in read-only mode; do not submit forms or mutate data/settings. Record pages, time, observations, exclusions, and access gaps.
- Activate UX/UI only when a UI task remains underspecified after product analysis and existing Figma, Demo, and design-system evidence are considered. Do not redesign supplied evidence.

## Execution lanes

Record one lane before task design.

- `fast`: first require a positive whitelist match—pure documentation, comments, copy/text, style/token constants, or local test additions with no business-behavior change. Then confirm no contract/schema/generated-code, authentication/authorization, sensitive-data, dependency, external-service, transaction, worker/async, runtime-chain, material UX, or baseline trigger. If the task is not clearly whitelisted, use `standard`.
- `standard`: ordinary M/L work or shared UI, data, module, compatibility, or regression impact.
- `high-risk`: XL work or any security, permission, sensitive-data, protocol, migration, transaction, worker/async, external side effect, or production-capability boundary.

Fast path may merge task-design and implementation-readiness review, use a reasoned fast-gate `N/A`, and omit the runtime-chain matrix. It never removes independent verification or scope checks. Reclassify whenever the change surface grows.

## State and outcome model

| Concept | Allowed values | Meaning |
| --- | --- | --- |
| Task state | `analysis`, `awaiting-human-decision`, `task-design-ready`, `implementation-ready`, `implementing`, `awaiting-verification`, `complete`, `cancelled/superseded` | Workflow position |
| Additive blocker | `design-blocked`, `implementation-blocked` | Reason work cannot advance; retains the last valid state |
| Technical outcome | `not-complete`, `verified-complete` | Evidence-backed completion result |
| Acceptance checkpoint | `none`, named checkpoint ID, `awaiting-human-acceptance` for the checkpoint scope | Human product review boundary |

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
3. Technical, data, interface/protocol, UI, quality, and regression impacts are mapped or have a reasoned N/A.
4. Interface/protocol disposition is `changed`, `reuses-frozen-contract`, or reasoned `N/A`; changed contracts and contract-test cases are frozen.
5. Required test accounts, fixtures, dependencies, reset method, commands, and evidence expectations are defined.
6. Security and runtime-chain treatment is complete when triggered.
7. The independent verifier records a scoped PASS; product, UX, and technical authors do not approve the delivery artifacts they authored. The verifier may own the independent test plan and Test Execution Manifest while assessing those source artifacts.

Pending upstream implementation or a closed project stage is an implementation blocker, not a design failure, when the upstream contract is frozen.

### Implementation-ready

1. Design dependencies are frozen.
2. Implementation dependencies and environment are ready.
3. The task has a current independent implementation-readiness PASS, issued directly or activated from an uninvalidated conditional PASS after only its enumerated mechanical conditions became true.
4. Assigned batch entry criteria pass, or the card records `batch-not-applicable`.
5. No human decision or P0/P1 blocks the task.
6. The project stage permits business-code implementation.

#### Standard combined readiness

- Use one verifier planning assignment to produce the test plan and Test Execution Manifest, task-design verdict, and either a direct implementation-readiness verdict or a conditional PASS.
- Limit a conditional PASS to enumerated mechanical conditions: named dependency completion, environment/command evidence, batch entry, blocker clearance, or project-stage opening. Record required evidence and invalidation triggers.
- Do not promote on a conditional PASS. Keep the task `task-design-ready` with an implementation blocker until activation.
- Let the coordinator activate it without another verifier assignment only when those exact conditions become true. Record activation evidence before setting `implementation-ready`.
- Require a fresh verifier review for any unlisted discrepancy or change to source, requirement, design, contract, test manifest, risk treatment, or relevant environment assumption.
- Exclude High-risk tasks; they always receive a separate current implementation-readiness review after task design.

### Technical completion

1. The change remains within approved scope or has a confirmed decision.
2. Implementation self-check records build/generation/lint/type-check, required tests, omissions, and residual risks.
3. Required owner, affected/regression, contract, final-suite, and independent risk evidence is valid.
4. The independent verifier records a fresh scoped PASS.
5. Code/security review has no unresolved P0/P1.
6. Required fingerprint policy and strict validation pass.
7. Set task state `complete` and technical outcome `verified-complete`, then continue unless a named checkpoint blocks the covered scope.

## Task planning and batches

- Maintain one Markdown backlog and one unique card per task. Task IDs are monotonic and never reused.
- Record complexity S/M/L/XL with concrete drivers. Complexity is a risk/planning signal, not a time promise. Split XL work when independently testable slices exist.
- A batch records objective, members, serial order, entry criteria, exit evidence, and any named acceptance checkpoint. It never bulk-promotes tasks; each card needs its own readiness and verification.
- Separate design dependencies from implementation dependencies. Continue downstream design from frozen upstream contracts.

## Handoffs and validation

- The active task's Handoff Snapshot and Required reads are the default cross-role context. Exact fields come only from `governance/templates.md`; do not reproduce the field list here or elsewhere.
- Bound ordinary assignments to the minimum authoritative context: the snapshot and Required reads; `Shared assignment contract` plus the assigned role section from `governance/roles.md`; the specifically named workflow section or gate checklist; and only the artifact template section being created or changed. Do not reread complete workflow, role, or template catalogs for a normal handoff.
- Use `<script-root>/extract_markdown_section.py <markdown-file> "<H2 heading>"` for bounded reads when available. It ignores headings inside fenced examples; do not use brittle line-number ranges.
- Read complete authority files only during initialization, migration, workflow revision, or when an evidenced cross-section conflict cannot be resolved from the cited sections. The coordinator names the required headings in every assignment.
- Keep raw logs and superseded snapshots/manifests/verdicts behind the Evidence index.
- Refresh the snapshot or Test Execution Manifest after material source, decision, contract, code, test, command, fixture, environment, finding, or next-action changes.
- Run `<script-root>/validate_task_handoff.py <task-card> --strict` before `task-design-ready`, after material design re-entry, before `verified-complete`, and before crossing a High-risk channel.
- For code, protocol, generated-output, dependency, runtime, Standard, or High-risk work, use `Fingerprint policy: required`. A pure Fast-path documentation/style/metadata task may use a reasoned `N/A`.
- Strict validation locates the nearest ancestor manifest, confirms the card is under its declared Task root, verifies the manifest-declared project rules, workflow, roles, templates, and delivery helpers exist, validates key field semantics and conditional Standard readiness guardrails, and automatically verifies required project-relative SHA-256 ledger entries. It does not run project commands or prove test-result truth.

## Test execution

- The independent verifier freezes a Test Execution Manifest before implementation. Exact fields and ledger syntax come only from `governance/templates.md`.
- The implementation engineer runs focused owner/affected groups while iterating and one approved full suite after the final implementation/test revision.
- For each frozen candidate, code/security review runs the scoped fast-gate and risk/mutation checks before the verifier's expensive full suite.
- Only after the scoped review has no deterministic P0/P1 does the verifier run one fresh approved full suite and applicable independent risk tests. `Fresh` means independently rerunning the already frozen manifest commands against the current candidate; it does not mean redesigning the test plan unless the manifest was invalidated. Reviewers do not duplicate that full suite unless evidence is invalid.
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

## Autonomous progression and turn boundary

- After every governance, design, readiness, remediation, or verified-completion handoff, start the next eligible action without waiting for a human prompt.
- A closed implementation stage or pending upstream code does not stop allowed design, test, security, or review work when contracts are frozen.
- Before returning, inspect the backlog. Stop only for a genuine human decision, missing required external evidence/authority, completion of all allowed work, a user pause/status request, or forced turn end.
- Codex is not a background daemon. When a turn must end with work open, record the exact continuation point in the active task artifact.

## Tool use and degradation

- Use scoped `$repomix-explorer` for unfamiliar or large repositories. Keep raw packs temporary and local; exclude secrets/generated/unrelated data. For known symbols, use targeted local search.
- Missing optional Figma, Repomix, TestSprite, browser routes, or convenience tools is a soft blocker: use source/code evidence or provider-neutral tests and record limitations. Missing authoritative requirements, required authority, or required test environment is a hard blocker.
- TestSprite MCP is optional Web UI-only automation for an authorized local service. Draft provider-neutral cases before implementation; implementation may run approved cases as self-check and the verifier reruns them independently. It never replaces unit, integration, or contract tests and blocks completion only when explicitly required.
- Never claim unavailable-tool evidence as PASS. Do not install/configure external tools, expose credentials, target production, or deploy without separate authority.
