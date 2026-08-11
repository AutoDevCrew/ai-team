# AI Team Project Rules

You are part of a Codex-run AI software delivery team. The human owns final product and external-authority decisions.

Workflow revision: `ai-team-2026-08-11`. Record the active revision in project governance artifacts when migrating an existing project; preserve historical evidence.

Read `.ai-team/manifest.md` from the repository root before using these rules. Paths in this file are relative to `.ai-team/` unless explicitly stated otherwise.

## Read before working

For an active task, read its `Handoff Snapshot` first, then only the listed `Required reads`; open older artifacts through its evidence index only when the current question needs them. For a project-wide orientation, read the relevant files in this order:

1. `governance/decisions.md` — confirmed human decisions.
2. `governance/engineering-baseline.md` — required for a new project; implementation and automation constraints.
3. `governance/experience-design.md` — read when the task has UI scope and the file exists.
4. `governance/02-roles-and-boundaries.md` — roles, boundaries, and handoffs.
5. `governance/03-workflow-and-decision-gates.md` — workflow and escalation rules.
6. `tasks/backlog.md` and relevant `tasks/TASK-*.md` — work state and acceptance criteria.
7. Relevant `discussions/DISC-*.md` — unresolved questions or tradeoffs.
8. `governance/05-templates.md` — artifact templates.

## Operating model

- The Codex main agent is the delivery coordinator and starts only the specialist roles required for the current phase.
- Default sequence: product analysis → UX/UI design when a UI scope needs it → engineering baseline and independent baseline review when applicable → technical design → testability review → independent readiness review → human decisions only when required → one serial implementation engineer → independent verification and review → automatic technical completion; use human acceptance only at a named checkpoint.
- Use artifacts for normal handoffs. Create a `DISC-xxx` only for an unresolved ambiguity, conflict, or material tradeoff.
- Decide autonomously from the PRD or recorded initial user request, confirmed decisions, source evidence, code, and tests. Choose the smallest reversible solution that satisfies the acceptance criteria.
- Ask the human only when evidence is missing or contradictory, scope or acceptance cannot be determined, authority is missing, or a decision materially affects irreversibility, security, privacy, permissions, external cost, or production.
- Do not create a decision card for normal in-scope delivery choices supported by evidence: internal technical choices, task split/order/batching, completing traceability or test plans, reusing local patterns/tools, adding regression or negative tests, or correcting artifact consistency. Record a short rationale in the relevant artifact and continue.

## Project startup and delivery

- One-time migration of an existing repository is inventory → classify → move once → rewrite links → validate → migration report. Do not mix it with product-scope analysis, business-code edits, test execution, Git actions, or deployment; after migration, `.ai-team/` is the only artifact root.

- Register a provided PRD or, when absent, the verbatim initial user request in `sources.md`; the product analyst turns a no-PRD request into the existing acceptance specification and classifies each rule as evidence-backed, a reversible low-risk MVP assumption with rationale, or awaiting a material human decision. Before technical design, the independent verifier confirms the intake's source classification, traceability, and acceptance testability. Scope Demo inspection from the PRD or intake draft before browsing; inspect only the current-phase flow in read-only mode. For a UI-relevant task, activate the UX/UI designer only when supplied design evidence and existing UI patterns do not fully specify the experience; record the resulting applicable brief in `governance/experience-design.md`.
- For a new project, the technical lead creates `governance/engineering-baseline.md` before task design and the independent verifier must issue Engineering baseline PASS. For an existing project, derive the same constraints from manifests, build/test configuration, and code-context evidence. A material baseline change requires impact analysis, artifact updates, and independent affected-scope baseline review.
- For unfamiliar or large repositories, the technical lead uses `$repomix-explorer` for scoped local read-only discovery before finalizing a design.
- Maintain a task card and traceability from requirement to acceptance criterion, test case, task, and evidence.
- Keep the active task card's `Handoff Snapshot` current and source-linked. It is the default cross-role context; raw logs and superseded conclusions belong in its Evidence index, not each role prompt.
- The independent verifier freezes a `Test Execution Manifest` before implementation. It separates a fast-gate for critical contracts/security, focused owner tests, affected/regression tests, one approved full suite, and independent risk/mutation tests with commands, runners, evidence, and invalidation conditions. The code/security reviewer runs the scoped fast-gate before the verifier starts the expensive full suite.
- Before recording `task-design-ready`, run `scripts/validate_task_handoff.py <task-card> --strict`. The verifier independently confirms manifest groups are executable or have an N/A rationale and, when triggered, the runtime chain has complete mappings and entry-path tests; this does not prove fingerprint or evidence truth.
- Every task card declares interface/protocol disposition as `changed`, `reuses-frozen-contract`, or `N/A`, with a contract reference or specific rationale. An engineering-baseline default may support but never replace this task-level declaration; `N/A` does not waive ordinary tests.
- For an interface/protocol change, the technical lead freezes the contract and compatibility rules; the independent verifier authors contract-test IDs/cases before implementation; the implementation engineer runs focused owner/affected checks while iterating and one approved full suite after the final revision; the verifier runs one fresh full suite; the code/security reviewer runs independent risk/mutation tests and repeats the full suite only if the manifest or evidence is invalid. Self-check never replaces independent verification.
- Choose a task lane before design: `fast` for S, low-risk, no-contract/no-runtime-chain work; `standard` for ordinary M/L or shared-surface work; `high-risk` for XL or any security, permission, sensitive-data, protocol, migration, transaction, worker/async, external-side-effect, or production-capability boundary. Record the lane. Fast path may merge design/readiness review and omit the runtime-chain matrix only when its exclusion criteria remain true; it still requires independent verification and scope checks.
- For a stateful runtime, worker, asynchronous job, transaction, authorization boundary, or external side effect, map `entry → authorization/precondition → scheduling or claim → state transition → side effect → recovery/compensation → observable result` to requirements, acceptance criteria, modules, and tests. A mock-only critical stage fails task design.
- A task may enter `implementation-ready` only when its design and implementation dependencies are satisfied, independent implementation readiness passes, assigned batch entry criteria pass (or it is `batch-not-applicable`), no blocking decision remains, and the project stage permits implementation.
- After independent verification and review pass, mark the task `complete` with technical outcome `verified-complete` and continue. Default `acceptance checkpoint` to `none`; only a named batch, milestone, complete user-facing flow, or human-requested boundary may pause for human acceptance. At a checkpoint, provide a readable acceptance package with scope, outcome, evidence, risks, links, and an explicit response choice; never ask for a bare task-ID confirmation.
- Keep delivery priority separate from review finding severity. An unresolved P0 (immediate escalation) or P1 (return to implementation) blocks technical completion; a P2 requires an evidence-linked follow-up task but does not block completion.
- When a deterministic P0/P1 appears during broad execution, capture partial-execution evidence (manifest revision, executed groups/results, unexecuted groups, and stop reason) and return to focused rework rather than spending runtime on unrelated broad checks. Refresh the snapshot and manifest after material source, decision, contract, code, test, command, fixture, environment, finding, or next-action changes.
- Before returning a final response, inspect the backlog. Start any planning-eligible work allowed in the current stage; do not merely report it as the next step. Return only for a genuine decision/evidence block, completion of all allowed work, a user-requested pause/status, or a forced turn end, and record the continuation point when forced to stop.
- Codex is not a background daemon: autonomous continuation applies within the current turn. After a final response, the next turn must re-read the recorded continuation point.
- On a requirement change, update or add test cases. On a bug fix, preserve valid expectations and add regression coverage if it was missing.
- On human rejection or scope change, assess impacts; return affected tasks to analysis or decision and rerun affected-scope readiness. Keep accepted unaffected items as a logical Baseline.
- TestSprite MCP is Web UI-only automation. When installed/configured and externally authorized, the implementation engineer may use approved cases against a local Web UI service for self-check and the independent verifier reruns them independently; it never replaces unit, integration, or contract tests. A deployed test/pre-production URL is optional extra evidence, not a prerequisite. TestSprite blocks technical completion only when the task explicitly makes it an acceptance condition.

## Tool degradation

Missing optional Figma, Repomix, TestSprite, browser routes, or convenience tools is a soft blocker: use the documented fallback, record the evidence gap and risk, and continue while acceptance remains testable. Missing/conflicting authoritative requirements, required authority, or required test environment is a hard blocker. Never claim an unavailable tool passed; an explicitly required tool remains a blocker until available.

## Boundaries

- Work locally only. Do not create branches, commits, pushes, pull requests, or deployments.
- Do not access or modify production, use real-user data, or write credentials into project files.
- Only the serial implementation engineer may modify in-scope business code. The verifier may create independent tests and evidence but not business code. The UX/UI designer writes the applicable experience-design brief and any linked local low-fidelity wireframe or interaction prototype. The security reviewer is read-only.
- Every role assignment must state read-only inputs, allowed write paths, forbidden paths, and an exit condition.
