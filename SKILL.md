---
name: ai-team
description: Launch or refine a Codex-run local software delivery team from a PRD with optional Figma and/or Demo inputs. Use when setting up reusable AI-team project rules, role handoffs, Markdown task tracking, scoped Demo inspection, structured multi-agent discussions, and human decision gates without building a separate orchestration system.
---

# AI Team

Run a Codex-native software delivery workflow. Use Codex as the coordinator and specialist subagents as temporary roles; do not build or install another multi-agent framework.

Workflow revision: `ai-team-2026-08-11`. Projects may record this revision in `AGENTS.md` and active task snapshots. A later revision requires a project-document sync before affected work resumes; historical evidence is never rewritten.

## Start or refine a project

1. Inspect the target workspace for root `AGENTS.md` and `.ai-team/manifest.md`.
2. Read existing project instructions before creating files. Preserve user material and merge missing rules instead of overwriting it.
3. Resolve the artifact layout before creating files. `.ai-team/manifest.md` is the only supported layout manifest and defines `governance-root`, `task-root`, `discussion-root`, `evidence-root`, and `script-root`. If the manifest is missing or incomplete, initialize or repair the namespaced template from `assets/project-template/`:
   - root `AGENTS.md` as a thin Codex entry point;
   - `.ai-team/manifest.md` and `.ai-team/project-rules.md`;
   - `.ai-team/governance/` for roles, workflow, decisions, and templates;
   - `.ai-team/tasks/` for the backlog and task cards;
   - `.ai-team/discussions/`, `.ai-team/evidence/`, and `.ai-team/scripts/` as needed;
   - `.ai-team/sources.md` when a project phase starts;
   - copy `scripts/validate_task_handoff.py` into the manifest's `script-root` when task cards are created or migrated.
4. Use `references/role-protocol.md` when creating or revising role, handoff, and discussion rules. The asset template is the project-local, editable source of truth after initialization; do not edit the bundled asset to record project decisions.
5. Keep the manifest's governance root small. Merge overlapping rules into the role protocol or workflow; do not create a new document for each role or one-off concept.
6. Migrate an existing project to the current acceptance model or namespaced layout only when the user explicitly requests it. This is a one-time physical migration, not a compatibility mode. Preserve historical task, test, and acceptance evidence; replace universal per-task human acceptance with named checkpoints; mark independently verified, previously awaiting-human-acceptance technical tasks `complete` when no named checkpoint applies; do not modify business code during this migration.

Path aliases in the remainder of this skill mean the manifest's `governance-root`, `source-register`, `task-root`, `discussion-root`, `evidence-root`, and `script-root`. They always resolve under `.ai-team/`. Never maintain two canonical copies of the same artifact.

### One-time project migration

Only when the user requests migration, perform this one-time sequence:

1. Inventory the existing instructions, governance, source/specification, tasks, discussions, evidence, and AI-team helper scripts; record the inventory before moving anything.
2. Classify each delivery artifact into `.ai-team/governance/`, `.ai-team/sources.md` or `.ai-team/specs/`, `.ai-team/tasks/`, `.ai-team/discussions/`, `.ai-team/evidence/`, or `.ai-team/scripts/`. Do not move business source, project tooling, generated output, runtime data, or deployment material into the AI-team artifact tree.
3. Create or repair `.ai-team/manifest.md` and `.ai-team/project-rules.md`; move artifacts once, preserving task IDs, evidence IDs, decisions, and historical content. Never create mirrored copies.
4. Rewrite relative Markdown links, required-read paths, script paths, and active-task references; update the root `AGENTS.md` to a thin entry point.
5. Copy the validator into `.ai-team/scripts/`, run structural validation and a link/path audit, then inspect the backlog and active task snapshot for stale paths.
6. Record a migration report and stop. Do not combine layout migration with product-scope analysis, business-code edits, test execution, Git actions, or deployment. After migration, root-level `docs/`, `tasks/`, `discussions/`, and `scripts/` are not valid AI-team artifact locations.

## Run the delivery workflow

1. Register the provided inputs in `<source-register>` using the source template. A PRD is preferred but not required: an initial user request is a valid product source when no PRD exists. Figma and Demo are optional.
2. When a Demo link is provided, have the product analyst derive a current-phase inspection scope from the PRD or, for a no-PRD intake, the current acceptance-specification draft before using the built-in browser: target flows or pages, entry routes or states, and explicitly excluded prior-phase functionality. Follow the available browser-control skill. Inspect only that scope in read-only mode; do not submit forms, create/delete data, change settings, or trigger other state-changing actions. Record inspected pages, observed behavior, excluded legacy content, and evidence time in `<source-register>`. If authorized browser access is unavailable, record the evidence gap and use the hard/soft blocker policy below rather than inferring Demo behavior.
3. Do not crawl the whole Demo or treat an uninspected prior-phase page as a requirement. If the PRD or no-PRD intake draft cannot identify the current-phase pages or flow, ask one decision-card question to establish that scope before browsing beyond minimal route discovery. If access requires credentials or a test account, request that authorization as one decision item before continuing.
4. Start the product analyst to produce a source-traceable, testable scope. For a no-PRD intake, have the independent verifier review source classification, traceability, and acceptance testability before technical baseline or design finalization. For a UI-relevant scope, determine whether the scoped Figma, Demo, and existing design system fully specify the user flow, states, responsive behavior, and accessibility constraints. When they do, record the source linkage in the acceptance specification and continue without the UX/UI designer. When they do not, start the UX/UI designer after product analysis and before technical-design finalization. The designer produces a scoped experience-design brief anchored to any supplied source and proposes only the unspecified details; it must not redesign supplied nodes/routes. Product analysis remains the authority for product rules. The technical lead may inspect the code baseline in parallel, but must not finalize design until it receives the required product and experience artifacts. For an unfamiliar or large repository, invoke `$repomix-explorer` before finalizing the design and use its findings to create a scoped code-context pack. Do not use it for a known single-file or single-symbol lookup; use direct local search instead. Create a `DISC-xxx` record only for ambiguity, conflict, or a real tradeoff.
5. Have the technical lead establish the engineering baseline when the project has no usable code baseline. Have the independent verifier review it before task design, then have the technical lead produce the minimal design and task proposal. For a sensitive change, run the security impact review before design finalization. Then have the product analyst, UX/UI designer when active, technical lead, and independent verifier hold a structured testability review: product owns intended behavior, UX/UI owns interaction detail, and technical ownership remains unchanged, while the verifier produces the pre-implementation test plan, stable test-case IDs, and any eligible automation-test plan; challenge untestable criteria, missing data/environment, and regression gaps.
6. Have the independent verifier run the task-design review in `references/role-protocol.md`; neither the product nor technical artifact author may approve its own work.
7. Resolve every design-review blocker through correction or a decision card. Apply the sequential confirmation protocol only when a decision is genuinely required; otherwise record a task-design verdict and continue autonomously to the next planning-eligible task.
8. After technical design and review, maintain one Markdown backlog and one task card per work item; link the code-context pack, acceptance specification, experience-design brief when applicable, security impact review when applicable, and test plan. Put a compact, source-linked `Handoff Snapshot` at the top of every active task card, with a required-read set, on-demand evidence links, current change-set fingerprint, frozen inputs, test-manifest ID, open findings, next action, exit condition, and invalidation conditions. A task with frozen design inputs enters `task-design-ready`; record unresolved implementation dependencies separately. Keep cards with unresolved decisions in the project's awaiting-human-decision state. A selected task may move to the project's implementation-ready state only when its design and implementation dependencies are satisfied, its own task-level implementation readiness passes, its assigned batch entry criteria pass (or it is explicitly `batch-not-applicable`), no blocking decision remains, and the project stage permits implementation.
9. Run independent verification and review after implementation. Execute the approved test plan, add evidence-backed risk tests when needed, and return reproducible findings to the implementation role; do not let the implementation role approve itself. Use the frozen test execution manifest to separate focused development checks from final evidence runs.
10. After independent verification and review pass, mark a task `complete` as a verified local technical outcome and continue to the next eligible task. Request human acceptance only at a named acceptance checkpoint; present the acceptance package defined below rather than a bare task ID. If the human rejects or changes scope, identify affected requirements, acceptance criteria, tests, modules, and downstream tasks; keep unaffected accepted items as a logical baseline, move affected cards back to analysis or awaiting-decision in the Markdown backlog, and require an affected-scope readiness review before implementation resumes. Do not perform version-control or deployment actions.

Within the user-authorized stage, continue from each completed handoff to the next planning-eligible task or remediation item. Do not stop merely because a task card or review artifact was created, a foundation review passed, an implementation dependency is pending, or business-code work is prohibited by the current stage. When implementation is stage-blocked, keep advancing task design, test planning, security treatment, and independent design review using frozen upstream contracts. Stop only at a genuine human decision, missing external authority/evidence needed for the current planning work, completion of all allowed work, or a user request to pause. “Continue autonomously” means continue within the current Codex turn until a valid turn-ending condition; Codex is not a background daemon. After Codex returns a final response, a new chat turn is required to continue, and the project artifacts preserve the exact continuation point.

## Execution lanes

Choose a lane before task design and record it on the task card:

- **Fast path:** first look for a positive whitelist: pure documentation, comments, copy/text, style/token constants, or local test additions that do not change business behavior. Then confirm no API/RPC/event/schema/generated-code change; authentication, authorization, sensitive-data, payment, upload, secret, dependency, external-service, transaction, worker, asynchronous, runtime-chain, material UX, or baseline trigger. Combine task-design and implementation-readiness review into one independent checklist, allow a reasoned fast-gate `N/A`, skip the runtime-chain matrix, and use focused owner/affected tests plus only the regression evidence required by impact analysis. Independent verification and scope boundaries still apply. If the task is not clearly on the whitelist, use Standard path.
- **Standard path:** ordinary `M/L` work or shared-module, UI, data, compatibility, or regression impact. Use the normal design, testability, readiness, implementation, and independent verification gates.
- **High-risk path:** `XL` work or any security, permission, sensitive-data, external side effect, transaction, worker/async, protocol, migration, or production-capability boundary. Use the complete workflow, runtime-chain matrix when triggered, security review, reviewer-first fast-gate, affected regression, and independent full-suite evidence.

Never select Fast path merely to avoid a gate. A task moves to Standard or High-risk when its impact analysis reveals a trigger, and a later material change re-evaluates the lane.

## Compact gate checklists

These checklists are the normative operational gate. The detailed sections explain exceptions and evidence requirements; if wording differs, the checklist controls the gate and the detailed section supplies the rationale.

**Implementation-ready** — all must be checked:

1. Design dependencies are frozen.
2. Implementation dependencies and environment are ready.
3. Task-scoped implementation-readiness is independently `PASS`.
4. Assigned batch entry criteria pass, or the card says `batch-not-applicable`.
5. No blocking decision or P0/P1 remains.
6. The project stage permits implementation.

**Technical completion** — all must be checked:

1. Change stays within approved scope.
2. Implementation self-check is recorded, including omissions and risks.
3. Required owner, affected, contract, and approved final tests are executed or evidenced as omitted.
4. Independent verifier has a fresh scoped `PASS`.
5. Code/security reviewer has no unresolved P0/P1.
6. The task's fingerprint policy is satisfied and strict fingerprint verification passes when required.
7. The task records `verified-complete` before the coordinator advances.

### State flow at a glance

```text
analysis → task-design-ready → implementation-ready → implementing
    │              │                    │                    │
    ├─ decision ───┘                    ├─ implementation-blocked
    └─ design-blocked                   └─ awaiting-verification
                                                     ↓
                                          verified-complete → next eligible task
                                                     ↓
                                  named human checkpoint (only when declared)
```

`blocked` is additive, not a replacement for the last valid stage. Human rejection or scope change returns only affected work to `analysis` or `awaiting-human-decision`; accepted unaffected work remains a logical baseline.

## Enforce project boundaries

- Treat `<governance-root>/decisions.md` as the only source of confirmed human decisions.
- Assign every decision card a monotonically increasing `DEC-<NNN>` ID. Reuse that same ID when recording its confirmed outcome in `<governance-root>/decisions.md`; do not create a parallel `D-<NNN>` namespace.
- Keep online inputs as source references; record extracted rules in local artifacts so they survive a session.
- Do not create branches, commits, pushes, pull requests, or deployments unless the user explicitly changes the project policy.
- Use only authorized test accounts and non-production environments.
- Escalate unresolved product ambiguity, unavailable authority for irreversible/security/privacy/permission/cost/production impact, or unresolved validation failures through a concise decision card.

## Autonomous decisions and human escalation

Decide autonomously from the PRD or recorded initial user request, confirmed decisions, scoped Demo/Figma evidence, codebase, tests, and project rules. Choose the smallest reversible solution that satisfies the traceable acceptance criteria; do not request approval merely because a normal implementation or technical choice has alternatives.

Request one human decision only when the available evidence cannot determine the outcome, sources conflict, scope or acceptance criteria are missing, an action exceeds granted authority, or a choice is irreversible or materially affects security, privacy, permissions, external cost, or production. State the evidence gap and the blocked work. If the evidence is sufficient, record the rationale in local artifacts and continue.

### Do not escalate: autonomous examples

When supported by sufficient evidence and within approved local scope, decide without a decision card and record a short rationale in the relevant design, task, or evidence artifact:

- Choose internal structure, API shape, algorithm, naming, module boundary, or test strategy consistent with approved requirements and the codebase.
- Resolve design/readiness gaps by completing traceability, acceptance detail, test planning, risk treatment, task metadata, or technical precision already determined by sources.
- Split, merge, order, estimate, or batch tasks; classify design versus implementation dependencies.
- Reuse an existing code pattern, local tool, build command, fixture, or generated-code workflow that satisfies the approved contract.
- Add local regression, boundary, permission, negative, fixture, or compatibility tests needed to preserve approved acceptance criteria.
- Make backward-compatible, in-scope local adjustments that do not change a confirmed contract, product behavior, permission model, data policy, external service, or project boundary.
- Correct documentation consistency, links, terminology, and task state when an authoritative artifact determines the result.

This list is illustrative, not an override of the escalation conditions above. Do not create a decision card for these normal delivery choices.

## Human decisions and acceptance checkpoints

Keep three actions distinct:

- A **human decision** resolves a genuine evidence, authority, or material-tradeoff gap and follows the sequential confirmation protocol.
- An **independent quality verdict** records test, review, or readiness evidence. A `PASS` is not a human decision and must automatically advance the allowed work.
- A **human acceptance checkpoint** is an explicitly named batch, milestone, end-to-end product flow, or user-requested review boundary. It is not a default task state. Set `acceptance checkpoint: none` for an ordinary internal task.

After a task has independent verification and review `PASS`, mark it `complete` with technical outcome `verified-complete` and continue. Use `awaiting-human-acceptance` only when the task belongs to a named blocking checkpoint. A checkpoint may group completed tasks; do not make the human ratify each member card.

Before requesting a checkpoint, create an acceptance package that states the checkpoint and task scope, product-facing outcome, in-scope and out-of-scope changes, concise source/contract or UI evidence, test and review results, known limitations and residual risks, linked local artifacts, and one explicit accept/reject/conditional-response choice. Do not ask the human to approve tests, task cards, or an already evidence-determined technical choice. Never request acceptance using only a task ID.

## No-PRD intake and requirements freeze

When the user provides an informal request instead of a PRD, the delivery coordinator starts the product analyst rather than treating the request as a frozen specification.

1. Record the verbatim request and its authority in `<source-register>` as the initial product source.
2. The product analyst writes the existing acceptance specification as a lightweight product brief: target user and goal; in-scope and out-of-scope behavior; user stories, normal/error/boundary states, and observable acceptance criteria; applicable quality constraints; and source differences from code, Demo, or Figma.
3. In the acceptance specification and requirement traceability matrix, classify every proposed rule as `evidence-backed`, `conventional low-risk MVP assumption` with rationale, or `awaiting human decision`. A low-risk assumption may be used only when it is reversible and does not materially change product behavior, permissions, data handling, cost, security, or a confirmed boundary.
4. Start the UX/UI designer when the UI behavior, states, responsive behavior, accessibility, or content constraints remain unspecified after product analysis; the designer may define only those interaction details, not product rules.
5. The product analyst must not silently invent a material product rule. Create one dependency-ordered decision card only when available evidence cannot determine a rule that materially changes scope or observable behavior. Group related alternatives into that one question; do not escalate ordinary MVP detail already supported by the sources.
6. The product analyst drafts the requirements but cannot approve them. Freeze the no-PRD intake only after the independent verifier finds every in-scope requirement source-classified, acceptance-testable, traceable to a test, and free of unresolved material product ambiguity. Then continue to technical design.

## Engineering baseline for new projects

Before task design for a greenfield project, the technical lead creates `<governance-root>/engineering-baseline.md`. For an existing repository, derive the same baseline from manifests, build/test configuration, and code-context evidence; do not replace an established stack without a task-level reason.

The baseline freezes the implementation constraints required by the serial engineer and verifier:

- product surfaces and supported platforms; language, runtime, package manager, and supported versions;
- repository/workspace layout, module and layer boundaries, primary frameworks, and approved core dependencies;
- transport/API contract style, data storage, caching, file handling, authentication/authorization boundary, and configuration/secrets boundary;
- local bootstrap, build, lint/type-check, generation, and test commands; test accounts/data, fixtures, reset/cleanup method, and local dependencies;
- automation stack by test level: unit, integration/contract, component where applicable, end-to-end, accessibility/performance/security checks where applicable, plus the evidence each suite produces;
- external-service, licensing, cost, and production exclusions.

The technical lead authors the baseline; it is frozen only after an independent verifier records an `Engineering baseline PASS`, confirming coverage, source alignment, commands, environments, reset method, and automation frameworks can exercise the approved acceptance criteria. The author must not approve its own baseline.

Do not ask the human to choose ordinary languages or frameworks when the evidence supports a reasonable choice. Escalate only material platform, compatibility, licensing, cost, compliance, security, or external-service tradeoffs.

For a baseline change, including a new core dependency, material version/runtime upgrade, framework replacement, transport/storage change, test-framework change, or local-command/environment change: record the reason and version; analyze affected requirements, designs, tasks, tests, security treatment, environments, and batch entry criteria; update those artifacts; then obtain an independent affected-scope engineering-baseline review before resuming affected task design or implementation. A local compatible change that does not affect those constraints may be recorded and continued autonomously; do not create a decision card unless an escalation condition applies.

## Sequential confirmation protocol

When one or more unresolved confirmations exist:

1. Identify their dependency order and present **only the first** decision card.
2. State the decision ID, one question, options, recommendation, impact, and what remains blocked.
3. Stop. Do not start a dependent task, present the next decision, or advance the workflow phase.
4. Accept a decision only when the human explicitly selects an option or explicitly approves the single stated recommendation. Do not treat an ambiguous acknowledgement as approval when options remain.
5. Record the confirmed choice in `<governance-root>/decisions.md`, update affected discussion/task state, then assess the next unresolved confirmation.
6. Present the next decision only after the previous one is recorded. If no confirmation remains, continue the workflow.

Keep unrelated read-only analysis within the current phase only when it cannot alter, bypass, or pre-empt the pending decision.

## Scope-bound readiness

Treat every verdict as scoped to the artifact and work it reviewed. Record the scope next to every `PASS` or `FAIL`; never use a project-level or foundation verdict as an implied approval for unrelated task implementation.

- **Engineering baseline PASS:** an independent verifier has reviewed and frozen the project-level platforms, stack, automation, commands, boundaries, and environment constraints. It is required before task-design review for a greenfield project and after a material baseline change; it does not authorize business implementation.
- **Governance foundation PASS:** traceability, roles, review process, shared test conventions, or other delivery controls are usable. It does not freeze product/design details or authorize any business task.
- **Task design PASS:** one task's requirement, technical design, applicable experience-design brief, test plan, and relevant risk treatment are frozen. It does not authorize implementation by itself.
- **Task implementation-ready:** the independent verifier gives that task a positive readiness verdict, its dependencies and blocking decisions are resolved, and its environment is ready.
- **Project stage open:** the project's declared stage allows business-code work. A task may start serial implementation only when both this condition and task implementation-ready are true.

Separate dependency types. A **design dependency** blocks task design only when its product rule, interface contract, or other required input is not frozen. An **implementation dependency** blocks code changes only; it must not block downstream design, test planning, security treatment, or task-design review when the upstream contract is frozen. Record the dependency type and revalidate downstream assumptions when upstream implementation completes.

## Autonomous planning progression

After a governance/foundation review or any task-design verdict, the coordinator must choose the next planning-eligible task without waiting for a user prompt. Use the serial backlog order unless an independent design dependency makes another task the only eligible choice.

For each planning-eligible task: complete its product/technical refinement, test plan, security treatment when triggered, and independent task-design review; record `task-design-ready`, design blockers, and implementation blockers separately; then continue to the next task. Do not label a task `FAIL` merely because an upstream implementation or the project stage is pending. Use `needs-design-remediation`, `awaiting-human-decision`, or `implementation-blocked` with a precise reason.

## Continuation audit before final response

Before returning a final response, inspect the backlog and current project stage. If a planning-eligible task or in-scope remediation exists and no genuine human decision or required external evidence/authority blocks it, start that work in the same run. Do not merely report it as the next step.

Return a final response only when a genuine human decision is required, required external evidence/authority is unavailable, all work allowed in the current stage is complete, the user requested a pause or status-only response, or the execution environment requires the turn to end. If a forced turn end leaves work open, state the exact continuation point in the relevant project artifact rather than asking the human what to do next.

## Complexity and implementation batches

Assign each task a relative `complexity` of `S`, `M`, `L`, or `XL` and record its concrete drivers: changed contracts/modules, data or migration impact, authorization/sensitive-data risk, external dependencies, test-environment work, baseline regression surface, and unresolved uncertainty. Complexity is a planning and review signal, not a duration, cost, staffing, or story-point commitment. Split an `XL` task when independently testable slices exist.

Maintain implementation batches in the backlog when more than one task is planned. Each batch records an ID, objective, member task IDs, intended serial implementation order, implementation entry criteria, and exit evidence. Use batches to bound implementation risk and give the human an understandable delivery cadence.

- A batch does not bulk-promote tasks: every task still needs its own implementation-readiness verdict.
- A frozen upstream contract permits downstream task design across batch boundaries. Pending upstream implementation is recorded as an implementation dependency, not a planning stop.
- If the human explicitly authorizes only named batches for implementation, stop code changes at that batch boundary but continue all allowed design preparation for later batches.
- If no batch-specific implementation boundary exists, automatically plan and prepare the next batch after the current batch's allowed work completes; do not wait for a user prompt. A batch exit requires its member verification and review, not universal human approval; stop for acceptance only when the backlog names that batch as a blocking checkpoint.

## Implementation readiness gate

Before a task can enter the project's implementation-ready state, require an independent, task-scoped implementation-readiness verdict. Record the reviewed task IDs, artifact scope, verdict, design blockers, implementation blockers, and residual risks. A task-design PASS is a required input, but not a substitute, for implementation readiness.

- Maintain a requirement traceability matrix: every in-scope PRD item or no-PRD intake requirement has a stable ID, source location and classification, scope status, observable acceptance criteria, source/Demo evidence or conflict, baseline impact, implementation task, and test.
- Require the technical design to map every acceptance criterion to a module/interface/data change (or explicit no-change), task, and test; every proposed change must trace back to a requirement.
- Require every task card to declare an interface/protocol disposition: `changed`, `reuses-frozen-contract`, or `N/A`. For `changed`, link the frozen contract and contract-test scope; for `reuses-frozen-contract`, link the inherited contract; for `N/A`, explain why no API/RPC/event/schema/generated-code or other interface/protocol surface changes. An engineering-baseline default may be cited but never replaces the task-level declaration. `N/A` removes only contract testing; it never removes ordinary unit, integration, UI, or regression-test obligations.
- For UI work, require every screen, interaction, component state, responsive rule, and accessibility treatment to trace to scoped Figma/Demo evidence or an applicable frozen experience-design brief, then to an acceptance criterion and test.
- Treat unverified assumptions, source conflicts, missing scope, irreversible changes, permissions, data handling, external cost, and unplanned baseline regressions as blockers or human decisions—never silent assumptions.
- Require the reviewer to check source coverage independently. Classify every relevant PRD item or no-PRD intake requirement as covered, out of scope (with reason), or awaiting a decision. A matrix with unclassified items fails the gate.
- Require a pre-implementation test plan that assigns a stable test-case ID and maps every acceptance criterion to normal, error/boundary, permission, and applicable regression scenarios, with test data/preconditions, environment, method, expected result, evidence expectation, and automation eligibility.
- Treat test cases as traceable assets: map requirement → acceptance criterion → test case → task → execution evidence. A bug that violates an unchanged acceptance criterion must not weaken its test expectation; add a regression test when coverage was missing. A requirement change must create or update its affected test cases and mark superseded tests as such while preserving their historical evidence.
- Verify that required test accounts, test data/fixtures, dependent local services, reset method, and test commands are available before implementation. Missing test-environment readiness fails the gate.
- Assess relevant quality attributes—security, privacy, accessibility, performance, reliability, observability, and recovery. Map each applicable attribute to an acceptance criterion, design treatment, and test; record a reason when an attribute is not applicable.
- Record the review conclusion and remaining risks in local artifacts. Ask the human to confirm the first outstanding blocking decision only when one exists. No implementation starts while a blocking decision remains unresolved; otherwise implementation may proceed.
- Check that the task's recorded batch entry criteria are satisfied before implementation. Batch completion evidence does not waive task-level verification or review. A named acceptance checkpoint may add a separate human boundary but does not change the technical verdict of its member tasks.

## Efficient handoffs and bounded validation

Normal handoffs share current, traceable facts through artifacts; do not try to share full chat transcripts or prior role reasoning. Historical evidence remains durable but is not the default read path.

- The coordinator maintains the active task card's `Handoff Snapshot`. Each assignment reads the snapshot and only its `Required reads`; open `On-demand evidence` only to answer a concrete question. Every summarized fact must cite a source, decision, test, evidence ID, or code-context location.
- The snapshot is invalid when its recorded source/decision revision, current code fingerprint, frozen contract, test-manifest revision, open-finding set, or next action changes. Refresh the snapshot before assigning another role. Do not reuse a stale snapshot as proof.
- Keep the coordinator and the one serial implementation engineer in their existing role thread for a batch when the environment supports it. For each candidate revision, keep at most one active serial implementation engineer, one independent verifier, and one code/security reviewer; retire or explicitly mark stale any restarted duplicate before assigning a fresh review. Verifiers and reviewers may retain their own evidence index, but must independently inspect the current diff and must not inherit implementation reasoning as evidence.
- Keep raw logs and historical PASS/FAIL records behind the task card's `Evidence index`. Do not copy them into every handoff. Run `<script-root>/validate_task_handoff.py <task-card> --strict` when the project copies that script and creates or materially revises an active task card, before recording `task-design-ready`, after material design re-entry, before `verified-complete`, and before crossing a High-risk channel. For code, protocol, generated-output, dependency, runtime, or High-risk changes, set `Fingerprint policy: required`; strict validation then requires a SHA-256 ledger and automatically verifies it. A pure Fast-path documentation/style/metadata task may set a reasoned `Fingerprint policy: N/A`, but never for Standard or High-risk work. The validator locates the nearest ancestor `.ai-team/manifest.md`, checks that the card is inside its declared Task root, and resolves ledger paths from the project root; task-root subdirectories are supported. `--verify-fingerprint` remains available as an explicit read-only command. Structural validation checks key field semantics and the ledger checks listed files; neither executes project commands or proves test evidence truth.

Before implementation, the verifier freezes a `Test Execution Manifest` that names its revision, commands, test groups, evidence expectation, runner, and invalidation conditions. At minimum distinguish a fast-gate group for critical contracts/security, owner tests, affected/regression tests, approved full-suite tests, and independent risk or security tests.

- For each frozen candidate revision, the code/security reviewer runs the complete scoped fast-gate and risk/mutation checks first. Do not start the expensive independent full-suite execution while that scoped gate has a deterministic P0/P1 or invalid evidence. The reviewer exhausts its declared scope before returning a verdict, unless a P0, environment failure, or evidence invalidation makes further checks meaningless.
- The implementation engineer runs owner and affected groups while iterating. After its final implementation/test revision, it runs the approved full suite once and records the result against the manifest revision.
- Only after the scoped review has no deterministic P0/P1 does the independent verifier run one fresh approved full-suite execution. The code/security reviewer does not duplicate that full suite merely to duplicate the verifier unless the manifest or evidence is invalid.
- When a deterministic P0/P1 is reproduced, stop unrelated broad test execution after preserving the failure evidence. Record partial-execution evidence: the manifest revision, executed test groups and results, and every unexecuted group with its stop reason. Return to focused test-first rework. After all blocking findings are closed, run the final approved suite and the required independent evidence again.
- A change to implementation, tests, commands, fixtures, contracts, or relevant environment invalidates prior affected evidence. It requires one new final run at the resulting frozen revision, not a full-suite run after every intermediate edit.

Reuse unaffected baseline evidence only when an impact check proves that the changed files, contracts, runtime paths, and test environment cannot affect that evidence; record the reused evidence IDs and rationale in the manifest. Otherwise rerun the affected group. Never use evidence from a changed relevant surface as proof.

### Repeated-finding circuit breaker

If two consecutive candidate revisions of the same task produce new P1 findings, do not launch another broad suite by default. The coordinator performs a task-scoped technical re-entry and classifies every finding as (1) in-scope implementation remediation, (2) a correctable task-design artifact gap, or (3) a material scope/contract decision. Continue the first two autonomously after updating the affected artifacts and tests. Escalate only the third. If independently testable slices exist, split the task before the next candidate revision; preserve historical evidence and do not advance a dependent task until the current task has a new frozen fingerprint and fresh independent PASS verdicts.

For a task touching a runtime state machine, background worker, asynchronous job, transaction, authorization boundary, or external side effect, the technical lead and verifier must freeze a runtime-chain matrix before implementation. Map `entry -> authorization/precondition -> scheduling or claim -> state transition -> side effect -> recovery/compensation -> observable result` to requirement, acceptance criterion, module, and test. A critical stage that has only a unit mock and no entry-path test fails task design. At task-design review, the independent verifier confirms each manifest group has an executable command/runner or an N/A rationale, and each triggered runtime-chain stage has its required mapping and entry-path test.

## Contract testing and implementation self-check

For a task whose interface/protocol disposition is `changed`, the technical lead freezes the contract surface and its applicable request/response or message fields, defaults/optionality, error semantics, compatibility/versioning constraints, authorization boundary, and idempotency, retry, ordering, concurrency, or transaction expectations.

The independent verifier validates every task's declared disposition and supporting evidence. For `changed`, it authors the approved contract-test cases and stable test IDs before implementation. Cover applicable serialization/deserialization or generation, valid and invalid inputs, success and error outputs, permissions, compatibility/default/unknown-field behavior, and the relevant retry, idempotency, concurrency, transaction, or regression cases. The implementation engineer may add or update in-scope unit, integration, and contract-test code, but may not redefine the approved contract or self-approve its result.

Before moving a task to `awaiting-verification`, the implementation engineer completes and records the required local self-check: build, generation, lint/type-check, approved test commands and contract cases, results, omitted checks, and residual risks. The independent verifier then reruns the approved evidence and may add independent risk tests; self-check evidence never substitutes for independent verification.

## Review finding severity

Keep **delivery priority** (the order in which planned tasks are worked) separate from **finding severity** (the quality consequence of a verifier or code/security-review finding). An unresolved P0 or P1 is a blocking finding.

- **P0:** credible security or data exposure, irreversible loss/corruption, or a failure that makes safe local delivery impossible. Block immediately and escalate to the human.
- **P1:** an acceptance criterion, required regression, or security control is not met. Return the task to implementation; do not request human acceptance.
- **P2:** a non-blocking improvement or low-risk issue. Create an evidence-linked follow-up task; do not silently discard it or block technical completion.

Record each finding's severity, reproducible evidence, affected requirement/acceptance criterion/test, disposition, and any linked follow-up task in the task card. See `references/role-protocol.md` for the role-level policy.

## Technical completion and acceptance checkpoints

Before marking a task `complete`, require all of the following:

- The implementation remains within the approved task scope, or the deviation is a confirmed decision.
- The approved test plan has been executed, and every omission has evidence and a recorded risk.
- The implementation self-check and, when applicable, the approved contract-test cases have passed or have an evidenced omission/recorded risk.
- The task records the impact on its test cases (unchanged, added, step updated, expectation updated, or superseded), and the affected tests plus required regressions have been run.
- The independent verifier has recorded a fresh scoped `PASS`, and the code/security reviewer has no unresolved blocking finding.
- Record technical outcome `verified-complete`, then automatically continue unless the task belongs to a named blocking acceptance checkpoint. Git and deployment actions remain outside this workflow.

At a named blocking checkpoint, set the checkpoint scope to `awaiting-human-acceptance` and attach the acceptance package. Human acceptance applies to the named scope, not implicitly to every task. A human may still review, reject, or change any completed work later; use the re-entry procedure below.

## Acceptance-feedback re-entry

When human feedback, including checkpoint rejection, rejects work or changes scope, the coordinator updates the original task card and the Markdown backlog; do not delete, recreate, or overwrite historical acceptance evidence.

- Perform an impact analysis over requirements, acceptance criteria, test cases, design/modules/interfaces/data, baseline regression constraints, and dependent tasks.
- Preserve every accepted and unaffected requirement/acceptance criterion/test as a **logical baseline**. It is not a code snapshot or a permanent exemption from regression testing: retest it when a later change affects it.
- Return every affected task to analysis, or awaiting a human decision when scope/priority/contract/risk is unresolved. Update its requirements, design, test plan, automation cases, security review when applicable, and dependencies.
- An independent verifier performs an affected-scope readiness review before a returned task may re-enter implementation. A narrow bug fix may reuse unaffected artifacts, but must still demonstrate that its acceptance criteria, tests, baseline impact, and environment remain ready.
- Keep scope changes separate from defects: a valid existing test expectation remains for a defect; a changed requirement creates or updates test cases and retains superseded-case history.

## Security shift left

Run a security impact review before design finalization when a task touches authentication, authorization, sensitive data, payment, file upload, user-controlled input or URLs, secrets, third-party APIs, webhooks, or dependency changes.

- The code/security reviewer identifies data sensitivity, trust boundaries, authorization rules, abuse cases, input/output/logging risks, dependency/secret risks, and required negative tests.
- Map every applicable finding to the design, task, and test plan. Escalate unresolved high-impact risk through a decision card.
- Continue with the existing post-implementation diff review; the early review informs it but does not replace it.

## Role write boundaries

- The coordinator writes planning, task, discussion, and decision artifacts only.
- Product analysis, UX/UI designer, and technical lead write their assigned specification or design artifacts only.
- The serial implementation engineer is the only role authorized to modify business source code, and only within the task card's allowed paths.
- The verifier may add independent test artifacts and verification evidence, but must not modify business source code. The security reviewer is read-only.
- Include allowed write paths, forbidden paths, read-only inputs, and exit conditions in every role assignment. These are workflow controls, not filesystem sandboxing.

## Demo inspection protocol

- Figma is supplementary evidence, never a prerequisite. A PRD plus a scoped Demo is sufficient to start discovery. The product analyst scopes its authority; a UX/UI designer, when active, consumes only that scoped evidence.
- The PRD defines the current phase. Before browsing, express the scope as named flows/pages/routes and list known prior-phase exclusions.
- Treat the Demo as behavioral evidence for scoped pages only; the PRD remains the source of truth for intended scope.
- Preserve the scope and evidence in `<source-register>` so a later agent can distinguish current work from inherited functionality.

## Repository analysis with Repomix

Use `$repomix-explorer` as a read-only aid for initial repository discovery and task-level impact analysis when it is installed.

- Start with the target entry points, modules, file types, and test/configuration files; use include/ignore filters and compression for large repositories. Do not automatically pack an entire repository.
- Write Repomix output to a project-excluded temporary location. Do not commit it, add it to project documentation, upload it, or use remote/website packing for private local source code.
- Treat generated packs as potentially sensitive even when Repomix excludes known credential patterns. Explicitly exclude credentials, environment files, private keys, generated artifacts, and unrelated large data.
- Record only the derived evidence in the architecture artifact: target modules, entry points, relevant call paths, contracts/data, build and test commands, allowed and forbidden areas, baseline regression constraints, and open questions.
- If Repomix is unavailable or its scoped output is still too large, fall back to `rg --files`, targeted `rg` searches, manifests, entry points, and test configuration. Do not infer missing code behavior.

## Graceful degradation

Tool unavailability is not automatically a project blocker. Classify the gap before stopping:

- **Hard blocker:** missing or conflicting product/contract evidence, unavailable authority for a required action, or a required test environment/fixture. Stop the dependent work and record the exact gap.
- **Soft blocker:** optional Figma, Repomix, TestSprite, an optional browser route, or a non-required convenience tool. Use the documented fallback (PRD/code evidence, targeted local search, provider-neutral test cases, or manual read-only inspection), record the limitation and risk, and continue when the acceptance criteria remain testable.
- Never claim that an unavailable tool passed. If the acceptance condition explicitly requires that tool's evidence, it becomes a hard blocker until authorized and available.

The handoff must name the unavailable tool, fallback used, affected evidence, and the condition that would require re-entry. This prevents optional integrations from freezing the whole delivery path.

## Optional TestSprite MCP Web UI testing

Use TestSprite MCP only for Web UI automation, and only when it is installed/configured and the human has authorized its external-service access. It is an execution provider, not the project's source of truth; do not use it for backend, API, or protocol contract testing.

- During testability review, the independent verifier determines whether the change includes a Web UI and whether TestSprite is eligible: a running local Web UI service and local port, project path, dedicated test account/data, permitted actions, reset/cleanup method, and an approved external-service boundary. Record a provider-neutral test plan even if TestSprite is unavailable.
- Before implementation, draft and review TestSprite-eligible Web UI cases from the approved acceptance criteria. Preserve the local case IDs and mappings in project artifacts; do not wait for deployment to decide expected behavior.
- During implementation, the implementation engineer may run only the approved cases through configured TestSprite MCP against the local Web UI service as self-check evidence. After implementation, the independent verifier runs the approved cases independently and attaches structured results/failure evidence to the task. Neither role may treat TestSprite results as a substitute for the required local unit, integration, or contract tests.
- An authorized test or pre-production URL may be an additional target after a human deploys, but the agent must not deploy, configure credentials, install TestSprite, or target production without separate human authority.
- TestSprite execution is optional unless the task explicitly makes its result an acceptance condition. When required, it blocks technical completion; otherwise record unavailability or omission with evidence and risk.
- For a requirement change, update or add the affected automation cases before execution and retain superseded-case history. For a bug fix, preserve a valid existing expectation; add a regression case if the bug was uncovered.

## Improve this skill from real use

Classify feedback before changing anything:

- Update the **project documents only** when the rule is specific to one product, stack, organization, or permission model.
- Update this **global skill** only when the improvement is reusable across future projects and the user explicitly asks to update `$ai-team`.
