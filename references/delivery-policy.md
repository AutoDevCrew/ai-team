# Delivery Policy

Workflow revision: `ai-team-2026-08-14-r44`.

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
- Classify a repository with business or test source as `existing-code`; otherwise classify it as `greenfield` and record a reasoned Repomix N/A.
- Before product analysis, engineering-baseline work, or task design for existing code, the technical lead initializes discovery with an installed `repomix` or transient `npx --yes repomix@latest`—never a global install.
- Resolve `<runner> --version`, then run `<runner> --compress --style xml --output <temporary-path> --ignore ".ai-team/**,node_modules/**,vendor/**,dist/**,build/**,coverage/**,.venv/**,**/.env*,**/*secret*,**/*credential*" <repository-root>`. Keep the raw pack temporary and local.
- Record the version, runner, exact command, scope, exclusions, and file/token metrics in the source register. If Repomix cannot run, stop initialization and request only the minimum Node/npx or Repomix setup; targeted search is not a substitute. After initialization, regenerate a temporary pack for broad architecture or cross-file discovery when relevant code changes, and use targeted local search for known symbols or exact paths.
- The current product-requirement source must be `provided` or `no-prd intake`. Move superseded sources to history and replace the current entry; a superseded entry cannot authorize promoted work.
- For a no-PRD request, create a lightweight acceptance specification. Classify each rule as evidence-backed, a reversible low-risk assumption with rationale, or awaiting a material human decision. An independent verifier freezes it only when scope, traceability, and testability are complete.
- Before Standard/High-risk task promotion, freeze one project acceptance specification with an explicit REQ catalog and one project traceability matrix. List every evaluated REQ once as covered, out of scope with source/decision rationale, or awaiting decision; only covered rows map AC, TASK, and TEST IDs.
- A standalone Fast non-behavior task may use card-local source/traceability when both project specification files are intentionally absent. If either project file exists, validate both normally.
- Before browsing a Demo, list current-phase flows/pages/routes and excluded legacy behavior. Authorized login, navigation, pagination, and non-mutating search/filter actions are allowed. Do not create or change business data, settings, permissions, or external state unless the user separately authorizes a reversible test action. Record pages, time, observations, exclusions, actions, cleanup, and access gaps.
- Activate UX/UI only when a UI task remains underspecified after product analysis and existing Figma, Demo, and design-system evidence are considered. Do not redesign supplied evidence.

## Execution lanes

Record one lane before task design.

- `fast`: require every declared change path to match the Schema's positive path whitelist for documentation, tests, copy, style, token, or localization assets, with no business-behavior change. Production-code paths use `standard` even for a small comment or copy edit. Confirm no contract/schema/generated-code, authentication/authorization, sensitive-data, dependency, external-service, transaction, worker/async, runtime-chain, material UX, or baseline trigger. If the task is not clearly whitelisted, use `standard`.
- `standard`: ordinary M/L work or shared UI, data, module, compatibility, or regression impact.
- `high-risk`: XL work or any security, permission, sensitive-data, protocol, migration, transaction, worker/async, external side effect, or production-capability boundary.

Fast path uses the lane-contract sections declared in the Schema and may claim `implementation-ready` directly when its verifier verdict and project stage pass. It lists every changed path. Pure Fast documentation/style/metadata work may use a reasoned fingerprint N/A; Fast test-code work uses the required fingerprint policy. It omits Standard planning and all untriggered annexes but never removes traceability, acceptance evidence, independent verification, or scope checks. Reclassify whenever the change surface grows.

## State and outcome model

| Concept | Allowed values | Meaning |
| --- | --- | --- |
| Task state | `analysis`, `awaiting-human-decision`, `task-design-ready`, `implementation-ready`, `implementing`, `awaiting-verification`, `complete`, `cancelled/superseded` | Workflow position |
| Additive blocker | `design-blocked`, `implementation-blocked` | Reason work cannot advance; retains the last valid state |
| Technical outcome | `not-complete`, `verified-complete` | Evidence-backed completion result |
| Acceptance checkpoint | named ID plus `blocking` or `non-blocking` mode and `pending`, `accepted`, `rejected`, or `conditional` status; otherwise `none` / `not-required` | Human product review boundary |

`complete` is the task state. `verified-complete` is the technical outcome that justifies it; they are not competing states. A named checkpoint may group completed tasks and does not change their technical outcome.

In the backlog, `Owner role` means the role responsible for the next executable task action, not the coordinator's durable ownership of backlog state. `Next gate` means the gate expected after that action or decision resolves. Allowed state/owner/gate combinations come only from the Schema's `state_contracts`.

```text
analysis → task-design-ready → implementation-ready → implementing → awaiting-verification → complete
    │              │                    │                    │
    ├─ awaiting-human-decision          ├─ implementation-blocked
    └─ design-blocked                   └─ return to implementing on P1
```

## Gate authority

Across this policy, each gate checklist controls its gate. Supporting prose explains evidence and exceptions; when a checklist delegates to another section, apply that section only to the scope named by the checklist.

## Engineering baseline PASS

Required for a greenfield project and after a material baseline change:

1. Platforms, language/runtime/package manager, frameworks, module boundaries, transport/data/auth/configuration boundaries, local commands, test frameworks, environment/data/reset, external constraints, and the Schema-declared external-integration credential-readiness fields/table are complete or explicitly inapplicable; an existing-code repository also has a valid Repomix initialization record in the source register.
2. The technical lead authored the baseline.
3. An independent verifier confirmed source alignment, coverage, executable commands, and testability.

An existing repository derives these constraints from manifests, configuration, code, and tests. Preserve its established stack unless a task requires change.

## Task-design-ready

1. Every evaluated requirement is covered, out of scope with source/decision rationale, or awaiting a decision; only covered requirements need AC/TASK/TEST delivery mappings.
2. Observable acceptance criteria map `REQ → AC → TEST → TASK → evidence`.
3. The compact card references project-level source/baseline/design evidence and records one control-trigger set. It satisfies the independently verifiable slice test under Task planning and batches; any retained L/XL task records `split-decision: retained — <stop-splitting rationale>` in its design/readiness verdict. `none` requires a concrete rationale; triggered experience, Web UI, external integration, interface, security, runtime-chain, TestSprite, or baseline-change treatment uses only its applicable annex/reference.
4. An interface trigger requires a frozen contract reference and contract-test IDs; use it only for a public or cross-process, service, team, or compatibility-promised boundary. A private signature inside a new module is technical design, not an interface trigger. Absence of the trigger means no interface/protocol change is in task scope.
5. Required test accounts, fixtures, dependencies, reset method, commands, and evidence expectations are defined.
6. Security and runtime-chain treatment is complete when triggered.
7. Artifact-author and independent-reviewer identities are recorded; product, UX, and technical authors do not approve the delivery artifacts they authored. The verifier may own the compact task Test Manifest while assessing those source artifacts.

Pending upstream implementation or a closed project stage is an implementation blocker, not a design failure, when the upstream contract is frozen.

## Implementation-ready

1. Design dependencies are frozen.
2. Implementation dependencies and environment are ready.
3. The task has a current independent PASS in its lane-declared readiness phase: `fast-design-readiness` for Fast or `implementation-readiness` for Standard/High-risk. A Standard conditional PASS may be activated only after its enumerated mechanical conditions become true without an invalidating change.
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

## Technical completion

1. The change remains within approved scope or has a confirmed decision.
2. Implementation self-check records build/generation/lint/type-check, required tests, omissions, and residual risks.
3. Required owner, affected/regression, contract, final-suite, and independent risk evidence is valid.
4. The independent verifier records a fresh verification-phase PASS bound to the current Snapshot ID, Test Manifest revision, fingerprinted candidate, and verification time. A PASS field begins with explicit status `PASS`; `NOT PASS` or other prose containing the word does not pass.
5. Fast and ordinary Standard work may use one independent verifier for diff review and test verification. High-risk work and interface, security, runtime-chain, or material baseline triggers require a separate current code-security-phase evidence record. No unresolved P0/P1 remains.
6. The implementation engineer differs from the independent verifier; any separately required code/security reviewer differs from both.
7. Required fingerprint policy and strict validation pass.
8. Set task state `complete` and technical outcome `verified-complete`, then continue unless a named checkpoint blocks the covered scope.

## Task planning and batches

- Maintain one Markdown backlog and one unique card per task. Task IDs are monotonic and never reused.
- Record complexity S/M/L/XL with concrete drivers; complexity is a review signal, not a command to split. A slice is independently verifiable only when it has one primary observable outcome, mapped AC/TEST and one focused verification group, failures can be attributed and remediated within its declared owner surface, and it does not require changing another unfinished task's owner surface.
- Before task-design PASS, split work only when it contains multiple independently verifiable outcomes or independently remediable risk boundaries, or when a likely failure would otherwise invalidate unrelated evidence. Stop splitting when a child cannot pass or fail independently, a contract/transaction/shared-boundary change must remain atomic, or child cards would repeat substantially the same files and checks. Prefer S/M only when it reduces failure or retest scope.
- Compare both sides: split cost includes each extra card, Snapshot, gate, reviewer handoff, fingerprint, and context rebuild; retention cost includes lane escalation, broader failure/re-entry scope, and per-candidate risk or full-suite work. Choose the lower total failure/retest cost, reuse frozen project/batch references and default commands, and record only task deltas.
- Plan serial batch slices around stable ownership surfaces. Keep tightly coupled changes to a shared boundary in its owner task before verification. If later work must change a verified shared boundary, create a narrow boundary-extension task and re-enter only its direct dependents; do not combine it with unrelated business behavior.
- A batch records objective, members, duplicate-free serial order, entry criteria, exit evidence, and any named acceptance checkpoint with mode and status. Before completion, `Exit evidence` records the planned regression command; a batch containing Web UI scope records prerequisite suites followed by a final TestSprite run. After all members complete it records `PASS` plus current evidence/time or `FAIL` plus affected-scope evidence. It never bulk-promotes tasks; each card needs its own readiness and verification.
- Do not start a later member before every earlier member in that batch's serial order is complete. More than one task may not be `implementing` at once.
- A batch is not finished and no checkpoint is presented until `Exit evidence` records the current regression result required by Test execution.
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
- Within one reviewer role, review phase, and Snapshot/Manifest binding, aggregate related checks, commands, and findings into one Review evidence record. Use separate records only when the reviewer role, phase, candidate/freshness binding, or independence requirement differs.
- Record one Schema-declared review phase in every Review evidence record: `intake`, `baseline`, `task-design`, `implementation-readiness`, `fast-design-readiness`, `verification`, or `code-security`. Design/readiness records remain historical inputs at completion and retain their original Snapshot binding while still matching the current frozen Manifest; a Manifest or design-input change invalidates them. Verification and code-security records must bind the current completion Snapshot and Manifest. Never substitute one phase's PASS for another.
- At a boundary, run `<script-root>/check_project_consistency.py <project-root> --task TASK-... --gate <task-design|implementation-ready|verified-complete> --next-action`. It combines task, project, fingerprint, backlog, and continuation checks. On FAIL it emits `NEXT fix-consistency` for the first source-located error; repair it locally and rerun. Use `validate_task_handoff.py --strict` only for focused card debugging.
- For test code, production code, protocol, generated-output, dependency, runtime, Standard, or High-risk work, use `Fingerprint policy: required`. A pure Fast-path documentation/style/metadata task may use a reasoned `N/A`.
- Gate validation locates the nearest ancestor manifest; rejects duplicate authoritative sections and fenced/comment-only fields; and checks revision, state/outcome, reviewer separation, dispositions, test environment, gate semantics, linked evidence, and authority layout.
- A required candidate ledger becomes mandatory only at `awaiting-verification` and `verified-complete`. Before then, use `N/A — candidate files do not exist yet` when no candidate exists, or record an optional existing-input ledger without planned paths.
- After the candidate path set settles, generate inventory and ledger with `<script-root>/render_fingerprint_ledger.py <project-root> <project-relative-path>...`. At `verified-complete`, the declared inventory must equal the generated ledger path set.
- Validation does not run project commands or prove test-result truth.

## Test execution

- The independent verifier freezes one compact task Test Manifest reference before implementation. Project-default commands remain in the engineering baseline; the card records task-specific implementer checks, independent checks, batch regression, risk/contract checks, and environment differences.
- The implementation engineer runs focused owner/affected checks while iterating. The independent verifier runs fresh task acceptance and affected-regression checks against the current candidate.
- Ordinary Standard work runs the approved full regression once at batch exit, not once per task. High-risk work may require it for each candidate. A batch regression failure re-enters only affected completed tasks with the failing evidence.
- For a Web UI batch, run all non-TestSprite prerequisite suites first and TestSprite once as the last automated UI acceptance execution.
- The batch cannot finish or enter human acceptance until exit evidence records the Schema-declared final TestSprite PASS bound to every frozen Web UI TEST ID, current candidate, report, visual evidence, and execution time. A standalone `batch-not-applicable` Web UI task records the same gate in its annex.
- Any later source, oracle, code, test, configuration, data, or relevant environment change invalidates that PASS and requires another final TestSprite run.
- For Fast and ordinary Standard work without a separate-review trigger, the verifier combines independent diff review and test verification in one assignment. When a separate review is triggered, its scoped fast-gate precedes expensive independent regression.
- `Fresh` means independently running frozen commands against the current candidate; it does not mean creating a new Agent process. Reuse the same verifier within the frozen task/batch scope after it reads the refreshed Snapshot and diff.
- On deterministic P0/P1, capture the manifest revision, executed groups/results, unexecuted groups, and stop reason; stop unrelated broad execution and return to focused rework.
- Changes to implementation, tests, commands, fixtures, contracts, or relevant environment invalidate affected evidence. Reuse unaffected evidence only with a recorded impact proof.
- If two consecutive candidates produce new P1 findings, perform task-scoped technical re-entry before another broad run. Classify findings as implementation remediation, correctable design gap, or material scope/contract decision; continue the first two autonomously and escalate only the third.

## Contract, runtime, and security treatment

- For a changed interface/protocol, freeze surface, fields/defaults, errors, compatibility/versioning, authorization, and applicable idempotency/retry/ordering/concurrency/transaction behavior. The verifier authors stable contract-test IDs before implementation.
- For a state machine, worker, async job, transaction, authorization boundary, or external side effect, map `entry → authorization/precondition → scheduling/claim → state transition → side effect → recovery/compensation → observable result` to requirements, acceptance criteria, modules, and entry-path tests. Mock-only coverage of a critical stage fails design.
- Shift security left for authentication, authorization, sensitive data, payment, upload, user-controlled input/URLs, secrets, dependencies, third-party APIs, or webhooks. Map trust boundaries, abuse cases, mitigations, and negative tests before design finalization; repeat diff-directed review after implementation.
- For every security or interface trigger, record in `Risk and contract checks` either `differentiator: TEST-...` for each frozen implementation-form constraint that rejects an otherwise equivalent implementation, or `manual-review-only: <concrete rationale>`. A differentiator is structural, contract, or observable; a manual-only constraint is not mechanically proven by a gate PASS.

## Finding severity

Finding severity is distinct from backlog priority.

- `P0`: credible security/data exposure, irreversible loss/corruption, or inability to deliver safely. Block and escalate immediately.
- `P1`: acceptance criterion, required regression, or security control not met. Return to implementation; do not request human acceptance.
- `P2`: non-blocking improvement. Create an evidence-linked follow-up task; do not silently discard it or block completion.

- Record each finding in the main Findings field as a `FIND-...` or `EVID-...` ID followed immediately by P0/P1/P2 severity, reproduction evidence, affected REQ/AC/TEST, disposition, and follow-up link. This field is the authoritative inventory.
- Record no findings as `none` or `none — <concrete reason>`; use the same no-value syntax for blockers and material-decision fields. Severity words in free or negative prose do not declare a finding.
- An ID-adjacent severity in the open-follow-up field is a blocking safety signal. A follow-up ID absent from a main field that reports no findings is a cross-field inconsistency.
- Keep an unresolved P0/P1 FIND ID in the backlog blocker until remediation or disposition removes it. Do not invent a DEC ID unless a separate material human decision is required. Unresolved P0/P1 blocks completion.

## Human decisions and acceptance

- Decide autonomously from sufficient sources, confirmed decisions, scoped Demo/Figma evidence, code, tests, and reversible local conventions.
- Create one decision card only for unresolved evidence conflict, missing scope/acceptance, unavailable authority, or material irreversible, security, privacy, permission, external-cost, or production impact. Present and record one dependency-ordered decision at a time.
- A DEC blocker clears only when the matching decision-log entry explicitly records `Status: confirmed`; an ID mention or open, pending, rejected, or obsolete status never grants authority.
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

- An initialized empty backlog continues through source intake, product analysis, and first-task creation. A completed batch continues through batch regression before any checkpoint. Clear a blocker once every referenced task is complete and every referenced decision is present in the confirmed decision log.
- After every governance, design, readiness, remediation, or verified-completion handoff, start the next eligible action without waiting for a human prompt.
- Treat deterministic consistency errors as local remediation: correct the affected artifact/state, preserve prior evidence, rerun the check, and continue. Escalate only when the correction needs a genuinely material human decision or unavailable authority/evidence.
- Run the project consistency check with `--next-action`; repair its source-located `fix-consistency` action on FAIL, or dispatch/execute its eligible local action on PASS instead of returning a next-step report.
- A closed implementation stage or pending upstream code does not stop allowed design, test, security, or review work when contracts are frozen.
- Before returning, inspect the backlog. Stop only for a genuine human decision, missing required external evidence/authority, completion of all allowed work, a user pause/status request, or forced turn end.
- Do not assume the agent host continues after returning a response. When a turn must end with work open, record the exact continuation point in the active task artifact.

## Tool use and degradation

- An unavailable optional Figma, browser route, or convenience tool is not by itself a blocker. Continue with targeted source/code evidence or provider-neutral tests and record the limitation. Repomix is not optional for existing-code initialization. Treat another unavailable capability as a hard evidence gap only when it is explicitly required for acceptance or is the sole authority for a material rule.
- For `external-integration`, also read `Credential and integration treatment`. For `web-ui` or `testsprite`, also read `Web UI and TestSprite treatment`. Do not load either conditional section when its trigger is absent.

## Credential and integration treatment

- During source intake and engineering-baseline work, inventory integrations and tool authorizations before affected task design, using the exact Schema/template fields. Declare `external-integration` on every affected task.
- Record key names, contract source, treatment, safe local target, readiness status, mock/fallback and live TEST IDs, affected task/latest-needed gate, and redacted probe evidence. Consolidate user action into one notice grouped as needed now, safely deferrable, or optional; create a decision card only for a material product, cost, permission, or provider choice.
- Prefer the project's existing secret-loading convention. When an evidenced integration lacks its local target, the active agent may create a valid local-only scaffold during analysis with required key names, blank secret values, safe comments, and known non-secret defaults.
- Create a scaffold only after confirming the application reads that location and the target is excluded from publication; add only a narrow ignore rule when authorized. Never overwrite an existing secret-bearing file, copy a secret, put credentials under `.ai-team/`, use non-empty fake secrets, or echo values. If the target exists, report only missing key names and let the user edit it locally.
- Mockability changes when work blocks, never whether a missing credential is disclosed: keep every missing credential in the baseline and consolidated notice. Never ask the user to paste a secret into chat.
- For `mockable`, require a known contract, provider-neutral adapter, and contract-faithful mock/fixture. Freeze mock and later live authentication/contract TEST IDs; label simulated evidence; list unexecuted live calls; and limit `verified-complete` to mock-scoped behavior until the declared live gate. Missing contract evidence is not safely mockable.
- For `equivalent-fallback`, record the approved runner or evidence source. For `non-substitutable`, notify when identified and block only the affected execution or declared gate.
- After the user reports configuration complete, check required values for presence without rendering them, run the smallest authorized authentication/connectivity probe, record only redacted status and evidence, and automatically resume the affected gate. When real credentials arrive after mock-scoped work, invalidate only affected simulated integration evidence, run the frozen live tests, and re-enter design or implementation only if the real contract differs.
- The final verification and any human-acceptance package must distinguish mock/fixture evidence from live sandbox evidence and explicitly report every integration not exercised with real authorized credentials. Mock evidence never proves live authentication, provider response shape/fill rate, limits, cost, accuracy, licence, or SLA.

## Web UI and TestSprite treatment

- For browser-rendered Web UI scope, declare both `web-ui` and `testsprite`. During task design, the independent verifier freezes provider-neutral TEST IDs and a source-backed coverage map for copy/content, layout/style, interaction/states, responsive viewports, accessibility, and affected regression.
- Copy and visual categories always require TEST IDs; other inapplicable categories require a concrete reason. Product rules own wording; Figma, scoped Demo, the design system, or an accepted visual baseline owns visual expectations. Record explicit tolerances rather than unsupported pixel-perfect claims.
- This global Web UI rule authorizes the minimum reversible TestSprite MCP installation and configuration in the agent host at readiness without another installation prompt. Use `npx @testsprite/testsprite-mcp@latest`; keep `API_KEY` only in the host MCP environment; restart or reload the agent host according to its MCP configuration mechanism; and verify tool discovery without exposing the key.
- TestSprite is mandatory for the final gate of browser-rendered Web UI scope. Inventory its readiness during baseline/design. If the API key, account, quota, environment, or tool discovery is missing, notify once with the exact secure configuration location. Continue safe requirements, design, implementation, and non-TestSprite checks, but block the final Web UI gate.
- This authority excludes obtaining or moving secrets, paid-plan purchase, administrator actions, runtime replacement, production access, and deployment.
- Execute frozen UI cases only after the affected implementation exists. The serial implementer may run focused TestSprite or Playwright checks while iterating. The independent verifier runs all prerequisite suites, then TestSprite as the final automated UI acceptance execution on the fresh candidate and reviews its report plus screenshot/video evidence. Playwright may supplement development and regression but cannot replace the final TestSprite gate. TestSprite never replaces unit, integration, contract, security, or accessibility-specific checks that the frozen plan requires.
- If Playwright is selected for supplemental checks and absent, install it project-locally with the detected package manager only when current implementation or verification authority permits test-tool changes; reuse the lockfile and never install it globally. `analysis-only` work may plan cases and runners but may not install project dependencies. Never claim unavailable-tool evidence as PASS, expose credentials, target production, or deploy without separate authority.
