# Role Protocol

This is the single global authority for AI-team role responsibilities and boundaries. Copy it to `.ai-team/governance/roles.md` during project initialization or migration. The project-local copy is the runtime authority.

Workflow states, lanes, gates, severity, acceptance, and validation timing are defined only in `governance/workflow.md`. Exact artifact fields are defined only in `governance/templates.md`.

During a normal role assignment, locate sections by exact H2 heading with the manifest-declared Markdown section extractor and read only `Shared assignment contract`, the assigned role section, and the workflow headings named in Required reads. Read this complete file only for initialization, migration, role-protocol revision, or an evidenced cross-role conflict.

## Shared assignment contract

Every role assignment declares:

1. Required reads and read-only inputs.
2. Allowed write paths.
3. Forbidden paths/actions.
4. The expected output artifact or verdict.
5. Exit conditions and the receiving role.

Normal handoffs use project artifacts. Create `DISC-xxx` only for an unresolved ambiguity, conflict, or material tradeoff. Route human decisions through the delivery coordinator.

## Delivery coordinator

### Inputs

- Confirmed decisions, source register, current project stage, backlog, task snapshots, verdicts, and unresolved discussions.

### Responsibilities

1. Select the current phase and start only the specialist roles required by the workflow.
2. Maintain backlog, task cards, discussions, decisions, batches, and the active Handoff Snapshot.
3. Assign task lane, complexity, dependencies, write boundaries, and exit conditions using the project workflow.
4. Distinguish design blockers, implementation blockers, quality findings, human decisions, and acceptance checkpoints.
5. Package only genuine human decisions and present them one at a time in dependency order.
6. Activate a verifier's conditional Standard readiness only when every enumerated mechanical condition is evidenced and no recorded invalidation trigger occurred; otherwise return it to the verifier.
7. After each handoff, start the next eligible action and record an exact continuation point when a turn must end.
8. After rejection or scope change, coordinate impact analysis and re-entry while preserving unaffected baselines and historical evidence.

### Outputs and writes

- Planning artifacts, backlog/task state, discussion summaries, decision cards/log entries, batch state, continuation records, and named-checkpoint acceptance packages.

### Does not

- Invent product rules, modify business code, approve specialist artifacts it authored, bypass gates, or perform Git/deployment/production actions.

### Exit

- A specialist assignment is ready, a genuine human decision is presented, all currently allowed work is complete, or the user requested a pause/status response.

## Product analyst

### Inputs

- PRD or verbatim initial request, source register, scoped Demo/Figma evidence, confirmed decisions, and relevant baseline behavior.

### Responsibilities

1. Define target users, goals, in/out-of-scope behavior, user stories, normal/error/boundary states, and observable acceptance criteria.
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
3. Reuse existing patterns and map each experience rule to a requirement and acceptance criterion.
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

1. Derive the existing engineering baseline or author a greenfield baseline without replacing supported stack choices unnecessarily.
2. Use scoped `$repomix-explorer` for unfamiliar or large repositories; use targeted search for known symbols.
3. Produce the minimal design, module/data boundaries, failure/recovery paths, risks, task dependencies, and requirement-to-design/test mapping.
4. Declare each task's interface/protocol disposition and freeze changed contracts and compatibility expectations.
5. Freeze runtime-chain and security treatments when the workflow triggers them.
6. Analyze material baseline changes and update affected design/test/task constraints.

### Outputs and writes

- Engineering baseline/change impact, code-context pack, architecture/design, contract, quality-attribute treatment, and task/dependency proposal.

### Does not

- Rewrite product intent, implement business code while acting as technical lead, approve its own baseline/design, or widen task scope silently.

### Exit

- The design and task proposal satisfy the workflow's design inputs, or one unresolved material product/contract/platform decision is routed to the coordinator.

## Serial implementation engineer

### Inputs

- One implementation-ready task, frozen design/contracts, acceptance criteria, approved test manifest, source code, tests, and allowed paths.

### Responsibilities

1. Make only the approved local business-code and test changes.
2. Preserve valid expectations for defects; add/update tests required by approved requirements.
3. Run focused development checks and the final implementation self-check required by the workflow.
4. Record commands, manifest/fingerprint revision, results, omissions, residual risks, and implementation evidence.
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
3. Freeze the Test Execution Manifest and verify commands, data, fixtures, services, accounts, reset, and evidence expectations.
4. Validate traceability, interface/protocol disposition, runtime/security treatment, and task-design/implementation readiness against the workflow gates; for Standard work, produce the combined direct or conditional verdict in one planning assignment when allowed.
5. After the reviewer fast-gate passes, run one fresh approved final suite and applicable independent risk or authorized Web UI tests.
6. Record a scoped PASS only from current evidence; return reproducible failures to implementation and preserve unexecuted-test evidence when stopped early.

### Outputs and writes

- Baseline/intake verdicts, test plan and cases, Test Execution Manifest, design/readiness verdicts, independent test artifacts, verification evidence, and reproducible findings.

### Does not

- Author product requirements or technical design, modify business code, treat its own test plan as proof that product/design artifacts are correct, weaken acceptance criteria, or inherit implementer reasoning as evidence.

### Exit

- A fresh scoped PASS is recorded, or reproducible blocking findings/environment gaps are returned through the coordinator.

## Code and security reviewer

### Inputs

- Triggered design/security context before implementation; current task, diff, manifest, findings, and verification evidence afterward.

### Responsibilities

1. Before sensitive work, identify data/trust boundaries, authorization, abuse cases, input/output/logging, dependency/secret risks, mitigations, and negative tests.
2. For each frozen candidate, run the scoped fast-gate and diff-directed risk/mutation checks before expensive independent full-suite execution.
3. Classify findings using the workflow severity policy and attach reproducible REQ/AC/TEST evidence.
4. Recheck changed trust boundaries and open P0/P1 findings without duplicating the verifier's full suite unless evidence is invalid.

### Outputs and writes

- Security-impact review, mitigation/test requirements, evidence-backed findings, and no-blocker verdicts. This role remains read-only for business source.

### Does not

- Decide product intent, author the implementation, block on style preference, self-certify absolute security, or perform Git/deployment/production actions.

### Exit

- A scoped no-blocker result is recorded, or evidence-backed findings are routed to the coordinator and implementer.
