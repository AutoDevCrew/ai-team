# Workflow and Decision Gates

## Source evidence

Register online inputs in `docs/sources.md` when a phase starts.

- A PRD defines business intent and rules when provided. Without one, the initial user request is the primary source but not a frozen specification: the product analyst records it and creates the existing acceptance specification as a lightweight product brief before technical design. Optional Figma is visual evidence. Optional Demo is behavioral evidence, not the scope authority.
- Before Demo browsing, the product analyst lists the current-phase pages/flows/routes and excluded legacy functionality from the PRD or no-PRD intake draft. Inspect only that scope in read-only mode; do not submit forms, create/delete data, change settings, or trigger state changes.
- Record source URL, version/time, authority, inspected pages, observed behavior, exclusions, and evidence gaps. Do not infer unavailable behavior.
- For unfamiliar or large repositories, use `$repomix-explorer` as scoped local read-only evidence. Do not upload private source, retain raw packs, or default to full-repository packing.

## No-PRD intake

The product analyst records the verbatim request in `docs/sources.md`, then uses the existing acceptance specification and requirement traceability matrix to define target user/goal, scope and exclusions, user stories, normal/error/boundary behavior, and observable acceptance criteria. Classify every proposed rule as evidence-backed, a conventional low-risk MVP assumption with rationale, or awaiting a human decision. The independent verifier must confirm source classification, traceability, and testability before the intake can freeze. Escalate only a material product rule that available evidence cannot determine; do not escalate ordinary reversible MVP detail.

## Delivery path

```text
sources → product analysis → UX/UI design (when needed) → engineering baseline and independent baseline review (when applicable) → technical design → security impact review (if triggered)
→ testability review and test plan → independent task-design review
→ serial implementation → independent verification and review → verified-complete → next eligible task
                                                        └→ named human acceptance checkpoint only
```

The coordinator advances only when a phase's exit conditions are met. AI autonomously resolves choices supported by a PRD or recorded initial user request, decisions, source evidence, code, tests, and project rules.

## Handoff snapshots and test execution

Normal role handoffs use the active task card's compact, source-linked **Handoff Snapshot**, not a full chat transcript. It records current state and technical outcome; source and decision references; frozen inputs/contracts; the current change-set fingerprint; Test Execution Manifest revision; required reads; on-demand Evidence index; open findings; next action and exit condition; and invalidation conditions. Each role reads that snapshot and its required-read set first. A material change to sources, decisions, contracts, code, tests, commands, fixtures, environment, findings, or next action refreshes the affected snapshot or manifest before handoff.

The independent verifier freezes a **Test Execution Manifest** before implementation. It divides the owner and affected/regression checks used while iterating from one approved full suite after the final revision and independent risk/mutation checks. The implementation engineer runs focused checks while iterating and one approved full suite after its final revision; the verifier runs one fresh full suite and applicable risk tests; the code/security reviewer runs diff-directed risk/mutation checks and repeats the full suite only when evidence is invalid. Capture a deterministic P0/P1, record partial-execution evidence (manifest revision, executed groups/results, unexecuted groups, and stop reason), stop unrelated broad execution, return to focused rework, then obtain final valid evidence.

For a stateful runtime, worker, asynchronous job, transaction, authorization boundary, or external side effect, the technical design includes `entry → authorization/precondition → scheduling or claim → state transition → side effect → recovery/compensation → observable result`, mapping each critical stage to a requirement, acceptance criterion, module, and test. A mock-only critical stage fails task design. Before recording `task-design-ready`, run `scripts/validate_task_handoff.py <task-card> --strict`; the verifier independently confirms each manifest group is executable or has an N/A rationale and each triggered runtime-chain stage has its mapping and entry-path test. Strict validation detects blank/placeholder fields only, not evidence truth.

## Human decision triggers

Create one decision card only if the evidence cannot determine the outcome, sources conflict, scope or acceptance is missing, authority is unavailable, or a choice has unresolved irreversible, security, privacy, permission, external-cost, or production impact. Present one dependency-ordered decision at a time; record a confirmed choice in `docs/decisions.md` before continuing dependent work.

Do not escalate normal evidence-backed, in-scope delivery choices: technical structure or test strategy, task split/order/batching, completing traceability/test/risk details already determined by sources, reusing local patterns/tools, adding regression or negative tests, or correcting artifact consistency. Record a short rationale in the relevant artifact and continue without a decision card.

## Human acceptance checkpoints

An independent verification or review `PASS` is not a request for human approval. After the technical completion gate passes, mark the task `complete` with technical outcome `verified-complete` and continue by default.

Set `acceptance checkpoint: none` for an ordinary task. Name a blocking checkpoint only for a batch, milestone, complete user-facing flow, or human-requested review boundary. The checkpoint may cover several completed tasks; do not pause after every task. Before requesting a checkpoint, prepare an acceptance package with scope, product outcome, in-scope/out-of-scope changes, concise UI or contract evidence, test/review results, residual risks, local artifact links, and one explicit accept/reject/conditional-response choice. Never request acceptance using only a task ID.

## Implementation readiness gate

Every `PASS` or `FAIL` is scope-bound and must name the reviewed artifact/task IDs. Do not interpret a governance/foundation `PASS` as implementation approval for any business task.

- **Engineering baseline PASS:** independent review has frozen the project-level platform, stack, automation, commands, boundaries, and environment; required before greenfield task design and after a material baseline change.
- **Governance foundation PASS:** delivery controls and shared conventions are usable; it does not freeze or authorize a business task.
- **Task design PASS:** one task's requirements, design, test plan, and applicable risk treatment are frozen; it does not authorize code changes by itself.
- **Task implementation-ready:** that task has an independent positive readiness verdict, resolved dependencies/blockers, and a ready environment.
- **Project stage open:** the declared project phase permits business-code work.

The independent verifier first concludes whether a task is `task-design-ready`: its requirements, technical design, applicable experience-design brief, test plan, and applicable security treatment are frozen. For a UI task, the UX/UI designer is activated only when scoped Figma/Demo evidence and existing UI patterns do not fully specify the experience; its brief is reviewed within this existing task-design gate, not a new project-level gate. Record design blockers separately from implementation blockers. Serial implementation requires both a later task implementation-ready verdict and a project stage open for implementation.

For a material engineering-baseline change, record its version/reason and assess affected requirements, designs, tasks, tests, security treatment, environments, and batch entry criteria. Update affected artifacts and obtain an independent affected-scope Engineering baseline PASS before affected work resumes. Compatible local changes with no such impact may continue autonomously; escalate only when normal decision criteria apply.

- Every relevant PRD item or no-PRD intake requirement is `covered`, `out of scope` with reason, or `awaiting decision` in the traceability matrix.
- Every in-scope requirement has observable acceptance criteria, baseline impact, design/task mapping, and at least one test.
- Every design change maps back to a requirement.
- For UI work, every screen, interaction, component state, responsive rule, and applicable accessibility treatment maps to scoped source evidence or the frozen experience-design brief, an acceptance criterion, and a test.
- Each test has a stable ID and maps `REQ → AC → TEST → TASK → evidence`.
- The test plan covers normal, error/boundary, permission, and applicable regression behavior with prerequisites, data, environment, method, expectation, and evidence.
- Every task card declares interface/protocol disposition as `changed`, `reuses-frozen-contract`, or `N/A`, with a frozen/inherited contract reference or a specific N/A rationale. A project engineering-baseline default is supporting evidence, not a replacement for this task-level declaration; `N/A` does not waive ordinary tests. For `changed`, the technical lead freezes the contract and applicable compatibility rules; the independent verifier authors contract-test cases for applicable generation/serialization, valid/invalid inputs, outputs/errors, permissions, compatibility/default/unknown-field behavior, and retry/idempotency/concurrency/transaction behavior.
- Test accounts, fixtures/data, local dependencies, reset method, and commands are ready.
- Applicable security, privacy, accessibility, performance, reliability, observability, and recovery treatment is mapped or marked not applicable with reason.

Missing evidence, source conflict, untestable acceptance, unresolved assumption, unauthorized action, or unplanned baseline regression fails the relevant review. A frozen upstream contract is sufficient for downstream task design; pending upstream implementation and a closed project stage are implementation blockers, not design blockers. After a task-design PASS, AI must continue to the next planning-eligible task without waiting for a user prompt. A later task-scoped implementation review, no blocking decision, project-stage opening, and the batch condition defined below are all required before AI may move that task to `implementation-ready`.

## Complexity and implementation batches

Every task records relative complexity (`S/M/L/XL`) and concrete drivers: changed contracts/modules, data or migration impact, authorization/sensitive-data risk, external dependencies, test-environment work, baseline regression surface, and uncertainty. Complexity is not a time or cost promise; split `XL` work when independently testable slices exist.

The backlog may group tasks into implementation batches. Each batch records its objective, member tasks, serial order, entry criteria, exit evidence, any named acceptance checkpoint, and any explicit implementation boundary. A batch never bulk-promotes its member cards. A card may enter `implementation-ready` only when its design and implementation dependencies are satisfied, its task-scoped implementation readiness passes, its assigned batch entry criteria pass (or the card is explicitly `batch-not-applicable`), no blocking decision remains, and the project stage is open. Pending upstream implementation or a closed batch does not stop planning later tasks whose design inputs are frozen. If no explicit human batch boundary exists, the coordinator automatically prepares the next batch after allowed work completes. A batch exit does not require universal human task acceptance; it pauses only at its named blocking checkpoint.

## Continuation audit before final response

Before returning a final response, the coordinator inspects the backlog and current stage. If planning-eligible work or in-scope remediation remains without a genuine decision or required external evidence/authority block, it must start that work in the same run rather than merely naming it as next. A final response is permitted only for a genuine decision/evidence block, completion of all allowed work, a user-requested pause or status-only response, or a forced turn end; record the exact continuation point in the project artifacts when forced to stop.

## TestSprite MCP for Web UI (optional)

TestSprite MCP is Web UI-only automation, not a backend/API/protocol testing provider and not the source of truth. The verifier determines whether a Web UI change has a running local service and local port, project path, dedicated account/data, permitted actions, cleanup/reset method, and authority to use TestSprite as an external service. When eligible, create and review TestSprite cases from approved acceptance criteria before implementation.

The implementation engineer may run the approved cases against the local Web UI service as self-check evidence. After implementation, the verifier independently reruns those cases and records structured results or failures. TestSprite never replaces required unit, integration, or contract tests. A deployed test/pre-production URL may provide additional evidence after a human deploys; it is not a prerequisite for local MCP execution. TestSprite blocks technical completion only when the task explicitly states that result as an acceptance condition. Do not configure TestSprite, credentials, deployment, or production testing without human authority.

## Technical completion gate

Keep **delivery priority** separate from **finding severity**. An unresolved P0 or P1 is a blocking finding: P0 is a credible security/data exposure, irreversible loss/corruption, or unsafe-local-delivery failure and requires immediate human escalation; P1 means an acceptance criterion, required regression, or security control is not met and returns the task to implementation. A P2 is a non-blocking improvement or low-risk issue; create an evidence-linked follow-up task without blocking technical completion.

Before moving a task to `awaiting-verification`, the implementation engineer records the approved self-check: build, generation, lint/type-check, approved tests, applicable contract cases, results, omissions, and residual risks. Before marking a task `complete`, require: implementation within approved scope; self-check completed or omissions evidenced; approved tests executed or omissions evidenced; required regression and applicable contract tests run; independent verifier pass/fail conclusion; and no unresolved blocking code/security finding. Record each finding's severity, reproducible evidence, affected requirement/acceptance criterion/test, disposition, and follow-up task. Record technical outcome `verified-complete`; the coordinator then advances the next eligible task. A named blocking acceptance checkpoint is a separate human boundary, not a universal task state.

## Human rejection, bugs, and scope change

Record human feedback in the original task and any applicable acceptance package. Do not rewrite historical acceptance criteria or evidence.

- **Bug in approved scope:** Preserve the requirement and valid test expectation. Identify affected artifacts, add regression coverage when missing, return affected work to `analysis` or `awaiting-human-decision`, and rerun affected-scope readiness before reimplementation.
- **New or changed scope:** Create new requirement/task/test artifacts. Do not silently expand an accepted task. Reanalyze affected downstream work.
- **Cancelled or replaced scope:** Mark the original task `cancelled/superseded` and link the reason, decision, and replacement task.

Mark accepted unaffected requirements, acceptance criteria, and tests as a logical **Baseline**. A Baseline is not a code snapshot and must be regression-tested if a later change affects it.
