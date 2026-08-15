# Role Protocol

Workflow revision: `ai-team-2026-08-14-r44`.

This is the single global authority for AI-team role responsibilities and boundaries. Copy it to `.ai-team/governance/roles.md` during project initialization. The project-local copy is the runtime authority.

Gate semantics and validation timing are defined only in `governance/workflow.md`. Machine-readable workflow values and field groups are defined in `governance/workflow-schema.json`; exact Markdown syntax is defined in `governance/templates.md`.

During a normal role assignment, locate sections by exact H2 heading with the manifest-declared Markdown section extractor and read only `Shared assignment contract`, the assigned role section, and the workflow headings named in Required reads. Read this complete file only for initialization, role-protocol revision, or an evidenced cross-role conflict.

## Shared assignment contract

Every role assignment declares:

1. Required reads and read-only inputs.
2. Allowed write paths.
3. Forbidden paths/actions.
4. The expected output artifact or verdict.
5. Exit conditions and the receiving role.
6. A stable `AGENT-...` identity for artifact authorship and independent-review separation.

Normal handoffs use project artifacts. Create `DISC-xxx` only for an unresolved ambiguity, conflict, or material tradeoff. Route human decisions through the delivery coordinator.

## Agent orchestration and lifecycle

When the host provides isolated specialist workers, use temporary isolated workers for independent specialist work:

1. Keep the primary agent or session as the delivery coordinator and durable owner of backlog state.
2. Allow exactly one writable serial implementation engineer. Never parallelize business-code writers.
3. Allow at most two concurrent read-only specialists or reviewers, and only when their scopes are independent. Ordered artifact authorship still follows the delivery path.
4. Before dispatching a specialist worker, complete the `Role assignment envelope` in `governance/templates.md`; bind it to one role, one bounded task/scope, and the current Snapshot.
5. Reuse a specialist within the same task or batch while its role, scope, and frozen requirement/contract inputs remain unchanged. A code-only candidate change invalidates evidence, not the Agent; provide the refreshed Snapshot and diff before reuse.
6. Retire a specialist worker when the task/batch scope closes, its role changes, requirement/contract authority changes, or its context cannot be refreshed safely. Do not accumulate duplicate reviewers or duplicate broad runs.
7. If isolated specialist workers are unavailable, execute the same role passes sequentially with fresh bounded inputs and role-attributed artifacts. Disclose that process independence was unavailable; never claim process isolation occurred, and preserve the same review and evidence criteria.

The coordinator starts the next eligible specialist worker or performs the next eligible local action in the same turn. Preparing an assignment without dispatching or executing it is not progression.

## Delivery coordinator

### Inputs

- Confirmed decisions, source register, current project stage, backlog, task snapshots, verdicts, and unresolved discussions.

### Responsibilities

1. Select the current phase and launch only the bounded specialist agents required by the workflow, following the lifecycle and concurrency limits above.
2. Maintain backlog, task cards, discussions, decisions, batches, duplicate-free serial order, and named checkpoint mode/status together with the active Handoff Snapshot.
3. Assign task lane, complexity, dependencies, write boundaries, exit conditions, and the compact control-trigger set. Make the final slice/retention decision from the technical lead's boundary/dependency proposal and the product/verifier AC/TEST evidence, using the project workflow.
4. Keep project-wide source, baseline, design, commands, and traceability out of task cards; reference their current artifacts and record only task deltas.
5. Distinguish design blockers, implementation blockers, quality findings, human decisions, acceptance checkpoints, and credential setup actions. Consolidate credential actions into one safe, path-specific notice; after the user reports setup complete, dispatch the redacted readiness probe and resume the affected gate without waiting for another prompt.
6. Package only genuine human decisions and present them one at a time in dependency order.
7. Activate a verifier's conditional Standard readiness only when every enumerated mechanical condition is evidenced and no recorded invalidation trigger occurred; otherwise return it to the verifier.
8. After each handoff, launch or execute the next eligible action in serial order, including batch regression and evidence-backed P0/P1 re-entry; never allow two tasks to remain `implementing`. Clear blockers whose referenced task or confirmed decision is resolved. Record an exact continuation point when a turn must end.
9. After rejection or scope change, coordinate impact analysis and re-entry while preserving unaffected baselines and historical evidence.

### Outputs and writes

- Planning artifacts, backlog/task state, discussion summaries, decision cards/log entries, batch state, continuation records, and named-checkpoint acceptance packages.

### Does not

- Invent product rules, modify business code, approve specialist artifacts it authored, bypass gates, or perform Git/deployment/production actions.

### Exit

- The next eligible specialist has been launched or local action executed, a genuine human decision is presented, all currently allowed work is complete, or the user requested a pause/status response.

## Product analyst

### Inputs

- PRD or verbatim initial request, source register, scoped Demo/Figma evidence, confirmed decisions, and relevant baseline behavior.

### Responsibilities

1. Define target users, goals, in/out-of-scope behavior, user stories, normal/error/boundary states, exact source-backed Web UI copy when applicable, and observable acceptance criteria.
2. Classify every requirement by source and record conflicts or missing authority.
3. For no-PRD intake, create the lightweight product brief without inventing material product rules.
4. Scope Demo inspection before browsing and record inspected/current-phase versus excluded legacy behavior.
5. Explain intended behavior and business edge cases to UX/UI, technical lead, and verifier.

### Outputs and writes

- Source register updates, acceptance specification, requirement traceability, source differences, and material open questions only.

### Does not

- Choose technology, write business code, redesign supplied UI evidence, or approve its own product artifact.

### Exit

- Every in-scope rule is source-classified and testable, or one material unresolved question is routed to the coordinator.

## UX/UI designer (conditional)

### Inputs

- Frozen product scope and acceptance criteria, scoped Figma/Demo evidence, existing UI/design-system evidence, supported surfaces, and confirmed decisions.

### Responsibilities

1. Activate only when UI behavior remains materially underspecified.
2. Preserve supplied design evidence and define only missing hierarchy, interaction, component-state, responsive, accessibility, content, and asset details.
3. Reuse existing patterns and map each experience rule to a requirement and acceptance criterion; freeze the visual oracle, required viewports/states, and explicit tolerances for browser-rendered Web UI.
4. Clarify feasibility with the technical lead and observable UI outcomes with the verifier.

### Outputs and writes

- Experience-design brief and, only when necessary, linked local low-fidelity wireframes or interaction prototypes.

### Does not

- Redefine product intent or priority, choose the stack, modify online Figma/Demo, write business code, or turn unsupported preference into a requirement.

### Exit

- The scoped experience is implementation- and test-ready, or one material unresolved experience conflict is routed to the coordinator.

## Technical lead

### Inputs

- Acceptance specification, applicable experience brief, decisions, source differences, code/configuration/tests, and environment constraints.

### Responsibilities

1. Classify the repository as existing-code or greenfield, then derive the existing engineering baseline or author a greenfield baseline without replacing supported stack choices unnecessarily.
2. For existing-code, execute the Repomix initialization and discovery rules defined under `Sources and intake` in `governance/workflow.md` before product analysis, baseline derivation, or task design. Do not substitute targeted search when this initialization gate fails.
3. Produce the minimal design, module/data boundaries, failure/recovery paths, risks, task dependencies, and requirement-to-design/test mapping.
4. Declare each task's interface/protocol disposition and freeze changed contracts and compatibility expectations.
5. Freeze runtime-chain and security treatments when the workflow triggers them.
6. During source intake and engineering-baseline work, inventory external integrations and credential/tool authorization readiness in the Schema-declared baseline fields/table, and propose `external-integration` for each affected task. Reuse the verified project secret-loading convention or, when absent, create only the permitted blank local scaffold and narrow ignore rule; record key names and redacted readiness, never secret values.
7. Analyze material baseline changes and update affected design/test/task constraints.

### Outputs and writes

- Engineering baseline/change impact, external-integration credential readiness and any safe local scaffold, code-context pack, architecture/design, contract, quality-attribute treatment, and task/dependency proposal.

### Does not

- Rewrite product intent, implement business code while acting as technical lead, approve its own baseline/design, widen task scope silently, overwrite an existing secret-bearing file, or read/echo/copy credential values.

### Exit

- The design and task proposal satisfy the workflow's design inputs, or one unresolved material product/contract/platform decision is routed to the coordinator.

## Serial implementation engineer

### Inputs

- One implementation-ready task, frozen design/contracts, acceptance criteria, approved test manifest, source code, tests, and allowed paths.

### Responsibilities

1. Make only the approved local business-code and test changes.
2. Preserve valid expectations for defects; add/update tests required by approved requirements.
3. Run focused development checks and the lane-specific final implementation self-check required by the workflow; do not duplicate the verifier-owned Standard final suite.
4. Record the stable implementation-engineer identity, commands, manifest/fingerprint revision, results, omissions, residual risks, and implementation evidence.
5. Address evidence-backed verifier or reviewer findings without redefining the approved contract.

### Outputs and writes

- In-scope local diff, implementation/self-check report, test evidence, and current-task progress.

### Does not

- Widen scope, change confirmed requirements/contracts, self-approve, modify unrelated files, or perform Git/deployment/production actions.

### Exit

- The task reaches awaiting verification with complete self-check evidence, or an evidenced blocker is returned to the coordinator.

## Independent verifier

### Inputs

- Planning: sources, acceptance/traceability, applicable experience brief, baseline, design, contracts, risk treatment, and test environment. After implementation: task snapshot, manifest, diff, self-check, and current environment.

### Responsibilities

1. Independently review no-PRD intake and engineering baseline when the workflow requires them.
2. Produce stable test IDs and a pre-implementation plan covering normal, boundary/error, permission, regression, and applicable contract/UI scenarios.
3. For every client UI task, map applicable TEST IDs to source-backed copy/content, visual layout and styling, interaction and component states, viewport/device adaptation, accessibility, and affected regression; record a reason for each inapplicable category. For browser-rendered Web UI, always assign copy and visual TEST IDs and map the frozen set to the mandatory final TestSprite gate. Compare only current-scope Figma/Demo/design-system/accepted-baseline evidence, use explicit visual tolerances rather than unsupported pixel-perfect assumptions, and identify non-automatable visual checks for human acceptance.
4. Freeze the compact task Test Manifest. Inherit project-default commands from the engineering baseline and record only task-specific checks, environment differences, and batch regression timing. For a mockable external integration, freeze both contract-faithful mock checks and the later live authentication/contract TEST IDs.
5. Validate traceability, interface/protocol disposition, runtime/security treatment, and task-design/implementation readiness against the workflow gates; for Standard work, produce the combined direct or conditional verdict in one planning assignment when allowed.
6. For ordinary Standard work, combine independent diff review with fresh task acceptance/affected-regression tests and defer the approved full regression to batch exit. For a Web UI batch, run prerequisite suites first and TestSprite once as its final automated UI acceptance execution; for standalone Web UI, record the same ordered gate in the task annex. For triggered or High-risk work, wait for the separate reviewer fast-gate and run the required risk/full suite.
7. Record a verification-phase scoped PASS only from current evidence and bind it to the current Snapshot ID, Manifest revision, fingerprinted candidate, verifier identity, and verification time; return reproducible failures to implementation and preserve unexecuted-test evidence when stopped early.

### Outputs and writes

- Baseline/intake verdicts, compact Test Manifest, design/readiness verdicts, independent test artifacts, verification evidence, and reproducible findings.

### Does not

- Author product requirements or technical design, modify business code, treat its own test plan as proof that product/design artifacts are correct, weaken acceptance criteria, or inherit implementer reasoning as evidence.

### Exit

- A fresh scoped PASS is recorded, or reproducible blocking findings/environment gaps are returned through the coordinator.

## Code and security reviewer

### Inputs

- Triggered design/security context before implementation; current task, diff, manifest, findings, and verification evidence afterward.

### Responsibilities

1. Activate for High-risk work or interface, security, runtime-chain, or material baseline triggers. Before sensitive work, identify data/trust boundaries, authorization, abuse cases, input/output/logging, dependency/secret risks, mitigations, and negative tests.
2. For each frozen candidate, run the scoped fast-gate and diff-directed risk/mutation checks before expensive independent full-suite execution.
3. Classify findings using the workflow severity policy and attach reproducible REQ/AC/TEST evidence.
4. Recheck changed trust boundaries and open P0/P1 findings without duplicating the verifier's full suite unless evidence is invalid.

### Outputs and writes

- A separate current code-security-phase Review evidence record, security-impact review, mitigation/test requirements, evidence-backed findings, and no-blocker verdict. This role remains read-only for business source.

### Does not

- Decide product intent, author the implementation, block on style preference, self-certify absolute security, or perform Git/deployment/production actions.

### Exit

- A scoped no-blocker result is recorded, or evidence-backed findings are routed to the coordinator and implementer.
