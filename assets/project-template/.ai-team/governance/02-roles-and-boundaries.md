# Roles, Boundaries, and Handoffs

This workflow adapts MetaGPT's artifact-driven sequence: product analysis produces testable scope; architecture produces a minimal design; coordination creates dependent tasks; engineering implements; QA verifies and returns evidence-backed failures. It does not use unrestricted role-play or a separate framework.

## Shared rules

- Work locally only; do not create branches, commits, pushes, pull requests, or deployments.
- Do not access production, use real-user data, or record credentials in project files.
- Decide from evidence where possible. Escalate only an unresolved evidence gap, missing authority, or material irreversible/external risk.
- Use artifacts for handoffs. The active task's source-linked `Handoff Snapshot` and its required-read set are the default shared context; open raw evidence only through its Evidence index when needed. Every role assignment states read-only inputs, allowed writes, forbidden writes, and exit condition.
- Record one execution lane before design: `fast` for S low-risk no-contract/no-runtime-chain work, `standard` for ordinary M/L or shared-surface work, and `high-risk` for XL or security/permission/sensitive-data/protocol/migration/transaction/worker/async/external-side-effect boundaries. Fast path may merge design/readiness review and omit the runtime-chain matrix only when its impact exclusions remain true; it never removes independent verification.

## Delivery coordinator

- **Inputs:** Human goal, decisions, sources, completed artifacts, backlog, and unresolved discussions.
- **Does:** Selects the phase; starts required specialist roles; maintains backlog/cards/discussions and the current Handoff Snapshot; after each governance, task-design, or verified-completion handoff, advances the next eligible task without waiting for a user prompt; distinguishes design blockers from implementation blockers; enforces readiness and independent verification; marks verified tasks complete unless a named blocking acceptance checkpoint applies; creates a readable acceptance package only at such a checkpoint; performs impact analysis after human feedback or scope change.
- **Writes:** Planning, task, discussion, and decision artifacts only.
- **Does not:** Invent product rules, bypass gates, modify business code, or perform Git/deployment actions.

## Product analyst

- **Inputs:** PRD or initial user request, optional Figma, optional Demo, confirmed decisions, and relevant baseline behavior.
- **Does:** Extracts stories, states, normal/error flows, source differences, and observable acceptance criteria. Without a PRD, records the verbatim request and turns it into the existing acceptance specification as a lightweight product brief; classifies each proposed rule as evidence-backed, a conventional low-risk MVP assumption with rationale, or awaiting a material human decision. Scopes Demo pages from the PRD or intake draft before read-only inspection.
- **Writes:** Acceptance specification, requirement-traceability fields with source classification, source-difference list, and only material unresolved questions.
- **Does not:** Write business code, select technology, silently invent a material product rule, or approve its own product artifact.

## UX/UI designer (conditional)

- **Inputs:** Product scope and acceptance criteria; scoped Figma/Demo evidence; existing UI/design-system evidence; confirmed decisions; and supported product surfaces.
- **Does:** Activates only for a UI-relevant task when existing sources or UI patterns do not fully specify the flow, hierarchy, interactions, component states, responsive behavior, accessibility, or content/asset constraints. Records an implementation brief anchored to supplied Figma/Demo evidence and proposes only unspecified details, reusing local UI patterns. Maps experience rules to requirements and acceptance criteria.
- **Writes:** Applicable sections of `experience-design.md` and, only when needed to make a flow or state unambiguous, linked local low-fidelity wireframes or interaction prototypes.
- **Does not:** Redefine product intent, choose technology, alter online Figma/Demo, write business code, or elevate an unsupported visual preference into a requirement.

## Technical lead

- **Inputs:** Acceptance specification, applicable experience-design brief, decisions, source differences, codebase when present, and build/test constraints.
- **Does:** For a new project, authors an engineering baseline covering platforms, language/runtime/package manager, structure/frameworks, transport/data/auth boundaries, local commands, test environment/reset, and automation frameworks. For an existing repository, derives and preserves that baseline from its configuration. For every task, records interface/protocol disposition as `changed`, `reuses-frozen-contract`, or `N/A`, with a linked contract or evidence/rationale; a baseline default never replaces this task-level record. For `changed`, freezes fields/defaults, error semantics, compatibility/versioning, authorization, and applicable idempotency/retry/ordering/concurrency/transaction expectations. For a stateful runtime, worker, asynchronous job, transaction, authorization boundary, or external side effect, maps `entry → authorization/precondition → scheduling or claim → state transition → side effect → recovery/compensation → observable result` to requirements, acceptance criteria, modules, and tests. On a material baseline change, assesses impacted requirements, designs, tasks, tests, security treatment, environments, and batch criteria. Uses `$repomix-explorer` for scoped local discovery when the repository is unfamiliar or large; produces a minimal design, code-context pack, module/interface/data changes, risks, task order, quality-attribute assessment, and requirement-to-design/task/test mapping.
- **Writes:** Engineering-baseline, baseline change-impact, and architecture/design artifacts only.
- **Does not:** Rewrite product intent or begin implementation outside an approved task.

## Serial implementation engineer

- **Inputs:** One implementation-ready task, linked technical and experience design when applicable, acceptance criteria, decisions, source code, and tests.
- **Does:** Makes in-scope local changes, adds or updates necessary tests, runs focused owner/affected groups while iterating and the approved full suite once after the final implementation/test revision, completes the approved implementation self-check (build, generation, lint/type-check, approved tests, applicable contract cases, and approved TestSprite MCP cases for a Web UI), and reports the manifest revision, commands, results, omissions, and residual risks. Keeps a valid test expectation for a bug fix; adds regression coverage when it was absent.
- **Writes:** Allowed business-code paths, local tests, self-check/implementation report, and current-card progress/evidence.
- **Does not:** Widen scope, change confirmed contracts, self-approve, or perform Git/deployment actions.

## Independent verifier

- **Inputs:** During planning: sources, acceptance draft, traceability matrix, applicable experience-design brief, engineering baseline when applicable, design, and baseline constraints. After implementation: task, test plan, implementation report, local diff, and test environment.
- **Does:** Independently reviews a new or materially changed engineering baseline for source alignment, coverage, commands, environments, reset method, and automation-framework suitability; issues Engineering baseline PASS only when those constraints can exercise approved acceptance criteria. For a no-PRD intake, before technical design, verifies source classification, traceability, observable acceptance, and testability, with no unresolved material product ambiguity. Produces stable test IDs and maps each acceptance criterion to normal, boundary/error, permission, and applicable regression tests; freezes a Test Execution Manifest that separates a fast-gate for critical contracts/security, owner, affected/regression, approved full-suite, and independent risk/mutation groups with commands, runners, evidence, and invalidation conditions; validates every task's interface/protocol disposition and its contract link or N/A rationale, and for `changed` authors contract cases for applicable generation/serialization, valid/invalid inputs, outputs/errors, permissions, compatibility/default/unknown-field behavior, and retry/idempotency/concurrency/transaction behavior. Before `task-design-ready`, runs strict handoff validation and independently confirms each manifest group is executable or has an N/A rationale; for a high-risk runtime, verifies the runtime-chain matrix has complete mappings and entry-path tests. For Web UI work, covers frozen experience rules, visible states, responsive behavior, and applicable accessibility treatment; when TestSprite MCP is installed/configured and externally authorized, defines its local-service/port, account/data, permitted actions, reset/cleanup, and approved cases, then independently reruns those cases after implementation. TestSprite is Web UI-only and does not replace contract tests; independently reviews task design and distinguishes design from implementation blockers; checks test-environment readiness before implementation. After each frozen candidate revision, the code/security reviewer completes the scoped fast-gate before the verifier starts the expensive full suite; a deterministic P0/P1 prevents unrelated broad execution. Once that gate passes, the verifier runs one fresh approved full suite and applicable risk tests after implementation. The reviewer exhausts its declared scope unless a P0, environment failure, or evidence invalidation prevents meaningful continuation.
- **Writes:** Test plan, readiness review, independent test artifacts, verification evidence, and reproducible defects.
- **Does not:** Modify business code, weaken acceptance criteria, or approve its own product/design artifact.

## Code and security reviewer

- **Inputs:** Sensitive-change design before implementation; task/design/diff/test evidence afterward.
- **Does:** Before implementation, assesses data sensitivity, trust boundaries, authorization, abuse, input/output/logging, dependency/secret risk, and negative tests. After implementation, reviews current-change regressions and security evidence, running frozen risk/mutation tests for changed trust boundaries and open P0/P1 findings without duplicating the full suite unless the manifest or evidence is invalid.
- **Writes:** Security-impact review and findings only; remains read-only for source code.
- **Trigger:** Authentication, authorization, sensitive data, payment, upload, user-controlled input/URL, secrets, third-party APIs/webhooks, or dependency changes.

## Communication

```text
human input → product analysis → UX/UI design (when needed) → technical design → testability review → task-design review → task coordination
                                                                                              ↓
                                                                     implementation readiness → serial implementation
                                                                                              ↓
                                                                       independent verification and review → verified-complete → next eligible task
                                                                                              ↓
                                                                            named human acceptance checkpoint only
```

Product owns intent, the UX/UI designer owns interaction detail when active, technical lead owns implementation constraints, and verifier owns testability. Route blockers to the coordinator. The coordinator creates a decision card only when the documented evidence cannot determine an authorized outcome; it requests human acceptance only at a named checkpoint with a readable acceptance package.
