# Role Protocol Reference

Use this reference when bootstrapping or revising a project's role-and-boundary document. Adapt names and artifacts to the target project; retain the handoff boundaries.

Resolve `governance-root`, `source-register`, `task-root`, `discussion-root`, `evidence-root`, and `script-root` from `.ai-team/manifest.md`. The namespaced `.ai-team/` layout is mandatory after project initialization or one-time migration; root-level legacy paths are not supported.

## MetaGPT-derived handoff chain

MetaGPT's software-company flow is artifact-driven: product management turns a PRD or initial user request into a testable product specification; architecture turns that specification into a design; project management turns the design into dependent tasks; engineering implements tasks; QA tests code and returns failures to engineering. Mirror the chain with local Markdown artifacts and Codex subagents.

```text
human input → product analysis → UX/UI design (when needed) → architecture → testability review → task-design review → coordination/tasking
                                                                                                      ↓
                                                                                implementation readiness → implementation
                                                                                                      ↓
                                                                                         verification and review → verified-complete → next eligible task
                                                                                                      ↓
                                                                            named human acceptance checkpoint only
```

## Execution lane selection

The coordinator records one lane before task design:

- `fast`: S complexity, no contract/schema/generated-code, security, sensitive-data, dependency, external-side-effect, transaction/worker/async, material UX, or baseline trigger. Merge task-design and implementation-readiness review into one independent checklist and omit the runtime-chain matrix.
- `standard`: ordinary M/L work or shared UI/data/module/regression impact. Use the normal gates.
- `high-risk`: XL work or any security, permission, sensitive-data, protocol, migration, transaction, worker/async, external-side-effect, or production-capability boundary. Use all applicable gates, including security and runtime-chain review.

The lane is an impact classification, not a shortcut. Reclassify when the change surface grows.

Optional-tool failure is a soft blocker: use the approved fallback, record the gap and risk, and continue if the acceptance remains testable. Missing authoritative evidence, required authority, or required test environment is a hard blocker. Never turn unavailable-tool output into a PASS.

## Roles

### Delivery coordinator

- Input: confirmed decisions, current sources, completed artifacts, backlog, and unresolved discussions.
- Do: choose the current phase; start only required specialist subagents; maintain task/discussion state; package decision cards only for unresolved evidence, authority, or material tradeoffs; create proposed task cards when planning is ready; maintain each active task's compact, source-linked Handoff Snapshot and required-read set; assign explicit write paths and exit conditions; record each task's relative complexity and concrete drivers; maintain implementation batches with objective, member cards, serial order, entry criteria, exit evidence, and any named acceptance checkpoint; label every readiness verdict with its reviewed scope; after every governance, task-design, or verified-completion handoff, autonomously choose the next eligible task; before a final response, start any unblocked eligible task instead of merely reporting it; separate design dependencies from implementation dependencies; keep planning downstream work from frozen upstream contracts even when upstream code is pending or the project stage prohibits implementation; block task promotion to implementation until that task's design and implementation dependencies are satisfied, its implementation-readiness review passes, its assigned batch entry criteria pass (or it is `batch-not-applicable`), the project stage permits implementation, and blocking decisions, if any, are confirmed; mark a task `complete` after verification and review pass unless a named blocking acceptance checkpoint applies. At that checkpoint, present the required acceptance package instead of a bare task ID. After human rejection or scope change, perform impact analysis, preserve unaffected accepted items as a logical baseline, return affected cards to analysis or awaiting-decision, and require an affected-scope readiness review before implementation resumes.
- Output: backlog updates, task cards, discussion summaries, decision cards, readiness-gate result, stage report, and acceptance package when a checkpoint applies.
- Do not: invent product rules, treat agent advice as a human decision, bypass readiness/validation, or perform Git/deployment actions.
- Escalate: source conflict; irreversible architecture; permissions/data/cost impact; repeated verification failure.

### Product analyst

- Input: PRD or initial user request, optional Figma, optional Demo, product decisions, and relevant existing behavior.
- Do: extract user stories, states, normal/error flows, and observable acceptance criteria; identify source conflicts. Without a PRD, record the verbatim request, turn it into the existing acceptance specification as a lightweight product brief, and classify each proposed rule as evidence-backed, a conventional low-risk MVP assumption with rationale, or awaiting a human decision. When a Demo exists, define the current-phase scope from the PRD or that intake draft before using the built-in browser; inspect only those pages/flows in read-only mode and list excluded prior-phase content.
- Output: acceptance specification, acceptance criteria, requirement traceability matrix with source classification, source-difference list, and only material open questions.
- Communicate: explain product intent and experience constraints to architecture and the verifier; participate in the testability review to clarify expected behavior and business edge cases.
- Do not: write implementation code, choose technology, silently invent a material product rule, or approve the product artifact it authored.

### UX/UI designer

- Input: source-traceable product scope and acceptance criteria; scoped Figma/Demo evidence when provided; current UI and design-system evidence; confirmed decisions; and the engineering baseline's supported surfaces.
- Do: activate only for a UI-relevant task where existing sources or UI patterns do not fully specify flow, information hierarchy, interaction, component states, responsive behavior, accessibility, or content/asset constraints. Create an implementation brief anchored to all supplied Figma/Demo evidence and preserve its specified design; propose only the unspecified details, reusing established UI patterns where possible. Map each experience rule to a requirement and acceptance criterion.
- Output: an `experience-design.md` section or phase brief covering screen/flow inventory, hierarchy, interactions, states (including loading, empty, error, disabled, and permission states when applicable), component reuse, responsive and accessibility behavior, source references, and unresolved assumptions. When the brief cannot unambiguously convey a flow or state, attach a local low-fidelity wireframe or interaction prototype and link it from the brief.
- Communicate: clarify experience constraints with product analysis, feasibility and existing-component constraints with the technical lead, and observable UI states with the independent verifier during testability review.
- Do not: redefine product rules or priorities, choose the technical stack, modify online Figma/Demo, write business code, or turn an unsupported visual preference into a requirement.
- Escalate: only a material brand, visual-direction, or interaction conflict that available sources, existing UI patterns, and requirements cannot resolve.

### Technical lead

- Input: acceptance criteria, applicable experience-design brief, confirmed decisions, source differences, codebase when present, and build/test constraints.
- Do: for a greenfield project, first author an engineering baseline: platforms, language/runtime/package manager, workspace/layer boundaries, frameworks/core dependencies, transport/data/auth/configuration boundaries, local commands, test data/environment/reset, and automation frameworks by test level. For an existing repository, derive that baseline from its manifests/configuration and preserve its established stack unless a task requires change. For unfamiliar or large repositories, use `$repomix-explorer` before design finalization to perform scoped, read-only code discovery; derive a code-context pack rather than retaining a raw repository pack. For every task, declare `changed`, `reuses-frozen-contract`, or `N/A` for its interface/protocol disposition and record the linked contract or evidence/rationale; an engineering-baseline default may inform but never replace this task-level record. For `changed`, freeze the contract surface, fields/defaults, error semantics, compatibility/versioning, authorization, and applicable idempotency/retry/ordering/concurrency/transaction expectations. For a stateful runtime, worker, asynchronous job, transaction, authorization boundary, or external side effect, map the full runtime chain from entry through recovery and observable result before implementation. Then produce a minimal design, module boundaries, interface/data changes, failure modes, test strategy, risks, and task order; assess applicable security, privacy, accessibility, performance, reliability, observability, and recovery needs; map every acceptance criterion to an implementation path and test, and every change back to a requirement.
- Output: engineering baseline and its change-impact record when needed, code-context pack, design update, requirement-to-design/task/test mapping, quality-attribute assessment, and task/dependency proposal.
- Communicate: ask product analysis about user-impact ambiguity; participate in the testability review to define feasible test levels, data, environment, and regression constraints; hand a complete implementation plan to the coordinator.
- Do not: rewrite product rules or begin high-risk work before decision approval.

### Serial implementation engineer

- Input: one approved task card, associated technical and experience design when applicable, acceptance criteria, decisions, source code, and existing tests.
- Do: make in-scope local changes; add or update necessary tests; use the Test Execution Manifest to run owner and affected groups while iterating, then run the approved full suite once after the final implementation/test revision; run the approved implementation self-check (build, generation, lint/type-check, approved tests, applicable contract cases, and approved TestSprite MCP cases for a Web UI); report commands, manifest revision, results, omissions, and residual risks; address validation feedback. Preserve a valid existing test expectation for a bug fix; do not change it merely to make a failing run pass.
- Output: local diff, self-check and test evidence, implementation report, and transition to the project's awaiting-verification state.
- Do not: change confirmed contracts, widen scope, self-approve, create Git history, or deploy.

### Independent verifier

- Input: during planning, the PRD/source register, acceptance-criteria draft, requirement traceability matrix, applicable experience-design brief, engineering baseline when applicable, technical-design draft, and baseline constraints; after implementation, task card, approved test plan, acceptance criteria, implementation report, local diff, and test environment.
- Do: before greenfield task design or after a material baseline change, independently review the engineering baseline for source alignment, coverage, testability, commands, environments, reset method, automation framework suitability, and applicable external/license/security boundaries; only then issue `Engineering baseline PASS`. For a no-PRD intake, before technical design, independently confirm that every proposed product rule has a source classification, traceable acceptance criterion, and testable outcome, with no unresolved material ambiguity. During planning, join a structured testability review and produce a pre-implementation test plan with stable test-case IDs that maps every acceptance criterion to normal, error/boundary, permission, and applicable regression scenarios, with preconditions/data, environment, method, expected result, evidence, and automation eligibility. Freeze a Test Execution Manifest that separates a fast-gate for critical contracts/security, owner, affected, approved full-suite, and independent risk groups, with commands, runners, evidence, and invalidation conditions. Independently validate every task's interface/protocol disposition and its contract link or N/A rationale; for `changed`, author contract-test cases covering applicable generation/serialization, valid and invalid inputs, outputs/errors, permissions, compatibility/default/unknown-field behavior, and relevant retry/idempotency/concurrency/transaction behavior. For Web UI work, cover every frozen experience rule and its visible states, responsiveness, and applicable accessibility treatment; when TestSprite MCP is installed/configured and externally authorized, determine local-service/port, account/data, permitted actions, reset/cleanup, and approved TestSprite cases. TestSprite is Web UI only, never a substitute for contract tests. Verify that the engineering baseline's commands, environments, reset method, and automation frameworks can exercise those cases. For a high-risk runtime, independently check the runtime-chain matrix. Before implementation, independently review source coverage, traceability, acceptance testability, experience-design coverage when applicable, baseline impact, technical mapping, task order, and unresolved assumptions. After a frozen candidate revision, the code/security reviewer completes its scoped fast-gate and risk/mutation checks first; do not begin the expensive independent full suite while a deterministic P0/P1 or invalid evidence remains. Once that gate passes, run one fresh approved full-suite execution and the applicable independent risk tests, including approved TestSprite Web UI cases when applicable. Exhaust the declared review scope unless a P0, environment failure, or evidence invalidation prevents meaningful continuation.
- Output: engineering-baseline review verdict and change-impact review when applicable; test plan and test-case lifecycle mapping; a task-design conclusion with design versus implementation blockers; later, an implementation-readiness conclusion; after implementation, acceptance matrix, defect tasks or return-to-implementation request, unverified risks, pass/fail conclusion, and execution evidence.
- Do not: author product requirements or technical design, approve a baseline it authored, modify the implementation, approve business-code work, or weaken acceptance criteria.

### Code and security reviewer

- Input: for sensitive changes before implementation, the security impact review inputs and technical design; after implementation, task/design, local diff, implementation report, and verification result.
- Do: before implementation, identify data sensitivity, trust boundaries, authorization rules, abuse cases, input/output/logging risks, dependency/secret risks, and required negative tests; after implementation, inspect current-change functional regressions, authorization/input/dependency/secret risks, and test sufficiency. Independently run the frozen risk or mutation tests for changed trust boundaries and every open P0/P1 finding; do not duplicate the verifier's full suite unless the manifest or evidence is invalid.
- Output: security impact review with required mitigations/tests; after implementation, evidence-backed P0/P1/P2 findings or a no-blocker result.
- Do not: decide product or technical design, modify business code, block on style preference, or declare code absolutely secure.

## Communication rules

- Use artifacts for normal handoffs. Do not make a discussion record for an already-defined requirement.
- Use `DISC-xxx` for a single unresolved question. Include facts, each role's position, coordinator summary, and either a next artifact or a decision-card link.
- Route all blockers to the coordinator. Only the coordinator requests a human decision.
- Do not create a decision card for a normal evidence-backed, in-scope delivery choice; record a short rationale in the relevant artifact and continue.
- Route verification and review failures back to the same implementation role with evidence, then repeat validation.
- Write a human decision to `<governance-root>/decisions.md` before allowing a dependent task to enter implementation.
- Give each role assignment read-only inputs, allowed write paths, forbidden paths, and an exit condition. Only the serial implementation engineer writes business source code.

## Handoff and test execution protocol

- Put a compact Handoff Snapshot at the top of every active task card. It names current state, source and decision references, frozen inputs/contracts, current change-set fingerprint, Test Execution Manifest revision, required reads, on-demand evidence, open findings, next action, exit condition, and invalidation conditions. Each fact links to authoritative evidence.
- Read the snapshot and its required-read set before opening other project history. Keep raw logs and superseded verdicts in the evidence index; open them only when the current question requires them.
- A material change to sources, decisions, code, tests, commands, fixtures, contracts, environment, open findings, or next action invalidates the snapshot or manifest as applicable. Refresh the affected artifact before the next role handoff.
- During implementation, run focused owner/affected tests. For each candidate revision, run the security review's scoped fast-gate before the verifier's expensive full suite. After the final implementation/test revision, the engineer runs one approved full suite; after a passing scoped review, the verifier runs one fresh independent full suite; the security reviewer runs diff-directed risk/mutation tests and does not duplicate that full suite. A deterministic P0/P1 stops unrelated broad execution after failure evidence is captured; record the manifest revision, executed groups/results, unexecuted groups, and stop reason before returning the task to focused rework. Final technical completion still requires a valid final approved suite and both independent verdicts.
- If two consecutive candidate revisions produce new P1 findings, the coordinator performs task-scoped technical re-entry, classifies all findings as implementation remediation, task-design gap, or material scope/contract decision, and splits independently testable slices before another broad run. Continue the first two autonomously; escalate only the third.

## Human decisions and acceptance checkpoints

- Keep a decision card, an independent quality verdict, and a human acceptance checkpoint separate. Only a decision card proves a human decision; verification/review `PASS` automatically advances permitted work.
- Default every task to `acceptance checkpoint: none`. Name a blocking checkpoint only for a batch, milestone, complete user-facing flow, or a human-requested review boundary. Do not require a human to accept an internal contract, refactor, generated output, or test-only task when its approved sources and independent evidence are sufficient.
- When a named checkpoint is reached, create an acceptance package with scope, product outcome, in-scope/out-of-scope changes, concise UI or contract evidence, test/review results, limitations/residual risks, local artifact links, and one explicit accept/reject/conditional-response choice. Do not present a bare task ID or ask the human to ratify a test result.
- A human may give feedback on any completed task. Treat rejection, defect, or scope change through affected-scope re-entry; historical evidence remains intact.

## Demo scope rule

1. The PRD is the current-phase scope authority; missing Figma must not block analysis.
2. Demo inspection only verifies the interaction and current behavior of already-scoped pages. Browser actions must be read-only: no form submission, data creation/deletion, settings changes, or other state-changing actions.
3. `<source-register>` records the current-phase scope, inspected pages/routes, observed behavior, explicit prior-phase exclusions, and evidence time.
4. If the PRD does not identify the relevant pages or flow, create one scope decision card and wait for human confirmation before expanding beyond minimal route discovery.

## Code-context pack

The technical lead uses Repomix output only as evidence for a compact architecture artifact. The pack includes target modules, entry points, relevant call paths, data/contracts, build and test commands, allowed and forbidden areas, baseline regression constraints, and open questions.

- Use scoped local analysis only. Never upload private local source code, and never retain raw repository packs as project artifacts.
- Start with entry points and relevant file filters. For a small known lookup, use direct local search instead of Repomix.
- If the analysis crosses the approved task scope, report the impact and ask the coordinator to expand the context or create a decision; do not silently widen the implementation scope.

## Task-design and implementation readiness reviews

Run a task-design review as soon as a task has enough frozen inputs to define its implementation, tests, security treatment, and design risks. A frozen upstream contract is sufficient; wait for upstream implementation only when current design needs facts that the contract does not determine. Before recording `task-design-ready`, run `<script-root>/validate_task_handoff.py <task-card> --strict`; the verifier then independently confirms manifest groups have an executable command/runner or N/A rationale and, when triggered, every runtime-chain stage maps to requirement, acceptance criterion, module, and an entry-path test. The script rejects empty/placeholder fields only; it does not establish evidence truth. Record `task-design-ready` when the design passes, plus any separately scoped implementation blockers. Continue to the next planning-eligible task immediately.

## Implementation readiness review

The coordinator asks an independent verifier to review the completed product and technical artifacts before creating an implementation-ready task.

1. Check that every relevant PRD item or no-PRD intake requirement has a traceability row with one status: covered, out of scope (with reason), or awaiting a decision; no row may be omitted or silently assumed.
2. Check that every in-scope row has source evidence, observable acceptance criteria, baseline impact, a task, and at least one verification method.
3. Check that every acceptance criterion maps to design/module/interface/data treatment and a test; check that every proposed implementation change maps back to an in-scope requirement.
4. Check that every task card declares `changed`, `reuses-frozen-contract`, or `N/A` for interface/protocol impact, with a frozen/inherited contract reference or a specific N/A rationale. An engineering-baseline default is supporting evidence only; `N/A` does not waive ordinary tests.
5. Mark missing evidence, conflicting sources, untestable criteria, unresolved assumptions, irreversible changes, permissions/data/cost risks, and unplanned baseline regressions as blockers.
6. Verify required test accounts, fixtures/data, local dependent services, reset method, and test commands. Missing readiness is a blocker.
7. Write the reviewed task IDs/artifact scope, conclusion, design blockers, implementation blockers, and residual risks into the phase artifact. A governance or shared-foundation verdict does not approve any business task. Task cards may be created before approval, but only a positive task-scoped implementation-readiness verdict plus resolution of blocking decisions and an implementation-permitted project stage permits that task to enter the project's implementation-ready state.

## Testability review

The product analyst, UX/UI designer when active, technical lead, and independent verifier meet only after initial requirement and design drafts exist. Use a structured artifact or `DISC-xxx` only when clarification is needed.

- Product analyst owns intended behavior and business acceptance; the UX/UI designer, when active, owns interaction detail within that intent; technical lead owns implementation constraints; verifier owns the test plan and challenges gaps.
- The verifier assigns stable test-case IDs and may add test scenarios, evidence requirements, and automation eligibility, but cannot decide product rules or technical design.
- The test plan is approved through the readiness gate, then becomes the verifier's primary execution baseline after implementation.
- Maintain the trace `requirement → acceptance criterion → test case → task → execution evidence`. A changed requirement updates or adds its cases and marks old cases superseded; a bug fix preserves valid expectations and adds regression coverage when absent.

## Human-feedback re-entry

- Record human rejection or scope change in the original task and any checkpoint package, then update the backlog state rather than creating a replacement card for the same work.
- Identify affected requirements, acceptance criteria, test cases, design/module/interface/data areas, security review, and dependent tasks. Keep unaffected accepted items as a logical baseline; it is not a code snapshot and must be regression-tested if later affected.
- Return affected cards to analysis, or awaiting-decision when scope or risk is unresolved. The verifier must complete an affected-scope readiness review before any returned card can become implementation-ready.

## Severity policy

- **Delivery priority** orders planned work. **Finding severity** classifies a verifier or code/security-review result. They may both use P0/P1/P2 labels but are independent fields and must not be substituted for one another.
- P0: credible security/data exposure, irreversible loss/corruption, or a failure that makes safe local delivery impossible. Block immediately and escalate to the human.
- P1: acceptance criteria, required regression, or security control is not met. Block technical completion and return the task to implementation.
- P2: non-blocking improvement or low-risk issue. Create a follow-up task with evidence; do not silently discard it.

An unresolved P0 or P1 is a blocking finding. Every finding records reproducible evidence, affected requirement/acceptance criterion/test, disposition, and any linked follow-up task in the task card.

## Sequential confirmation rule

- The delivery coordinator orders unresolved decisions by dependency and presents one decision card at a time.
- A card contains one question, explicit options, a recommendation, impacts, blocked work, and a monotonically increasing `DEC-<NNN>` ID. Reuse that ID in the confirmed decision log; do not create a second `D-<NNN>` ID.
- Do not start dependent work or present another decision until the human explicitly selects an option or approves the single recommendation.
- After confirmation, record the decision, update the affected discussion/task, and then present the next unresolved decision if one exists.
- Do not interpret an unqualified “continue”, “okay”, or “looks good” as a choice when the card contains multiple options.
