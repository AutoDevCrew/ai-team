# Canonical Artifact Templates

Workflow revision: `ai-team-2026-08-12-r16`.

## Catalog navigation

For normal work, read only the named H2 section below; do not load the entire catalog. Use the manifest-declared `extract_markdown_section.py` so headings inside fenced templates do not terminate the read. Use `Task card` for Standard/High-risk work and `Minimal Fast-path task card` only for eligible Fast work.

```sh
python3 .ai-team/scripts/extract_markdown_section.py .ai-team/governance/templates.md "Task card"
```

- Intake and specification: `Source register`, `Requirement traceability matrix`, `Acceptance specification`.
- Design: `Architecture and code-context pack`, `Experience design brief (UI scope only)`, `Engineering baseline`.
- Governance: `Decision card`, `Discussion record`, `Role assignment envelope`, `Review evidence record`.
- Delivery: `Task card`, `Conditional task annexes`, `Security-impact review`, `Acceptance checkpoint package`.
- Focused examples: `Minimal Fast-path task card`, `Complete Standard task card example`, `Required fingerprint example`.

## Source register

```md
# Source Register

## Product requirement source
- Type: PRD / initial user request
- URL or verbatim request:
- Authority: primary business-rule source
- Status: provided / no-PRD intake
- Version or updated at:
- Read at:

## Figma (optional)
- URL / page / node:
- Authority: visual, layout, component-state evidence
- Read at:
- Status: provided / not provided

## Demo (optional)
- URL and environment:
- Authorized test-account method:
- Allowed read-only actions: login / navigation / pagination / search / filter
- Forbidden mutations and any separately authorized reversible test action:
- Authority: scoped behavioral evidence
- Current-phase read-only scope (flows/pages/routes):
- Explicit legacy exclusions:
- Inspected pages/routes and evidence time:
- Evidence gap:

## Code baseline
- Repository / directory:
- Baseline description:
- Modules and tests inspected:
- Read at:
```

## Requirement traceability matrix

```md
# Requirement Traceability Matrix

| Requirement | Requirement source and classification | State | Acceptance criteria | Source/Demo evidence | Baseline impact | Quality treatment | Design and task | Test case/method | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| REQ-001 | <section/link>; evidence-backed / low-risk assumption / awaiting decision | covered / out of scope / awaiting decision | AC-001 | <page/time> | <impact> | <treatment or N/A reason> | <module + TASK> | TEST-001 / <method> | DEC-<NNN> / none |
```

## Acceptance specification

```md
# Acceptance Specification: <phase or feature>

## Requirement source and intake state
- Source: PRD / initial user request
- Verbatim initial request (when no PRD):
- Status: draft / frozen / needs-product-remediation
- Product analyst: AGENT-<id>
- Independent review: AGENT-<id> / PASS or FAIL / EVID-<id> / `.ai-team/evidence/<file>.md` / <ISO timestamp>
- Evidence-backed rules:
- Conventional low-risk MVP assumptions and rationale:
- Awaiting material human decision:

## Scope
- In scope:
- Out of scope:

## Requirements
- REQ-001: <one observable product rule>

## User stories and acceptance criteria
### AC-001: <name>
- Requirement: REQ-001
- Preconditions:
- Main flow:
- Error/boundary behavior:
- Observable result:

## Source differences and decisions
- 
```

## Architecture and code-context pack

```md
# Architecture and Code-Context Pack: <phase or feature>

## Scoped code evidence
- Analysis: Repomix Explorer / rg / other
- Relevant modules and responsibilities:
- Entry points and call paths:
- Data models / external contracts:
- Existing build and test commands:

## Minimal design
- Change:
- Interface/data impact:
- Failure path and recovery:
- Quality treatment (security, privacy, accessibility, performance, reliability, observability, recovery):

## Interface/protocol disposition and contract
- Disposition by task: changed / reuses-frozen-contract / N/A
- Frozen/inherited contract reference or N/A rationale:
- Contract surface and schema/version:
- Request/response or message fields, defaults, and optionality:
- Error semantics and authorization boundary:
- Compatibility and unknown-field behavior:
- Idempotency, retry, ordering, concurrency, or transaction expectations:
- Contract-test scope and N/A rationale:

## Task boundary
- Allowed changes:
- Forbidden changes:
- Baseline regression constraints:
- Open questions and decisions:
```

## Experience design brief (UI scope only)

```md
# Experience Design: <phase or UI scope>

## State and scope
- Status: draft / frozen / needs-design-remediation
- Product analyst: AGENT-<id>
- UX/UI designer: AGENT-<id>
- Linked requirements and acceptance criteria:
- Source basis: Figma nodes / Demo routes / existing UI patterns / none

## Screens and flows
| Screen or flow | User goal | Information hierarchy | Interaction and component states | Source or rationale |
| --- | --- | --- | --- | --- |

## Reuse and behavior
- Existing components/patterns to reuse:
- New components or variants:
- Loading, empty, error, disabled, and permission states:
- Responsive behavior:
- Accessibility treatment:
- Content and asset constraints:

## Linked local wireframes or interaction prototypes (when needed)
- 

## Open assumptions or conflicts
- 
```

## Engineering baseline

```md
# Engineering Baseline: <project>

## State
- Version:
- Mode: derived-existing-repository / greenfield
- Status: draft / Engineering baseline PASS / needs-baseline-remediation
- Technical lead: AGENT-<id>
- Independent verifier: AGENT-<id>
- Reviewed scope and verdict:

## Product surfaces and platform
- Surfaces/platforms:
- Supported runtime/browser/device versions:

## Implementation stack
- Language and runtime:
- Package manager and workspace layout:
- Frameworks and approved core dependencies:
- Module/layer boundaries:
- Transport/API and data/storage boundaries:
- Authentication, authorization, configuration, and secrets boundaries:

## Interface/protocol default
- Default task disposition and scope:
- Supporting source/code evidence:
- Constraint: Every task card declares its own disposition; this default may be inherited but never replaces that record.

## Local developer workflow
- Bootstrap:
- Generate:
- Build/lint/type-check:
- Local dependencies:

## Test and automation baseline
| Test level | Framework/tool | Command | Data/environment/reset | Evidence |
| --- | --- | --- | --- | --- |
| Unit |  |  |  |  |
| Integration/contract |  |  |  |  |
| Component (if applicable) |  |  |  |  |
| End-to-end (if applicable) |  |  |  |  |
| Security/accessibility/performance (if applicable) |  |  |  |  |

## Boundaries and rationale
- External services, licensing, cost, and production exclusions:
- Rationale from sources/code constraints:
- Baseline change control:

## Change record
- Change reason/version:
- Affected requirements/designs/tasks/tests/security/environments/batches:
- Independent affected-scope baseline review:
```

## Decision card

Use the same `DEC-<NNN>` ID when the human confirms this card in `decisions.md`.

```md
# DEC-<NNN>: <title>

## State
awaiting confirmation / confirmed / obsolete

## Linked requirement and task
- Requirement:
- Task:

## One question

## Evidence
- 

## Option A
- Benefits:
- Costs and risks:

## Option B
- Benefits:
- Costs and risks:

## Recommendation

## Consequence of no decision
```

## Task card

Use this compact delta card for Standard/High-risk work. Project-wide requirements, baseline, design, default commands, and traceability remain in their existing project artifacts; the card references them and records only task-specific differences. Append only triggered sections from `Conditional task annexes`.

```md
# TASK-<id>: <title>

## Handoff Snapshot
- Workflow revision:
- Snapshot ID and updated at:
- Current state and technical outcome:
- Scope, source, decision, and contract references:
- Delivery lane / complexity / control triggers: fast|standard|high-risk / S|M|L|XL / none — reason or comma-separated trigger names
- Batch / dependencies / entry: batch ID or batch-not-applicable / dependency IDs or none / concrete entry evidence
- Change-set file inventory: `path`; `path`
- Fingerprint policy: required / N/A — Fast-only reason
- Current change-set fingerprint: <N/A — Fast-only reason, or leave empty and add actual ledger lines below>
- Actor identities: product=AGENT-<id>; technical=AGENT-<id>; implementer=AGENT-<id>; verifier=AGENT-<id>; reviewer=AGENT-<id> / N/A — merged-verifier reason
- Open findings / blockers:
- Next action, exit condition, and invalidation:

## Plan and readiness
- Baseline and design references:
- Test Manifest revision and frozen-at: TEM-<id> / <ISO timestamp>
- Implementer checks:
- Independent task verification:
- Batch regression: command and batch-exit timing / N/A — High-risk per-task full suite reason
- Risk and contract checks:
- Environment / data / reset:
- Planning verifier and report: AGENT-<id> / `.ai-team/evidence/<file>.md`
- Design/readiness verdict and conditions: task-design-ready / implementation-ready / conditional-pass with exact activation evidence / blocked with reason

## Acceptance criteria checklist
- [ ] AC-<id> / TEST-<id>

## Implementation self-check
- Implementation engineer identity: AGENT-<id>
- Build / generation / lint-typecheck results:
- Owner / affected / contract test results:
- Omitted checks, residual risks, and evidence:

## Verification and findings
- Independent verifier identity: AGENT-<id>
- Separate code/security reviewer identity: AGENT-<id> / N/A — Fast or ordinary Standard merged-verifier reason
- Independent verifier verdict:
- Separate code/security reviewer verdict:
- Independent verification evidence: `.ai-team/evidence/EVID-...md`
- Separate code/security review evidence: `.ai-team/evidence/EVID-...md` / N/A — merged-verifier reason
- Findings / severity / affected REQ-AC-TEST: none / N/A — no finding, or FIND-<id> / P0|P1|P2 / REQ-... AC-... TEST-...
- Open P0/P1 / P2 follow-up: none / FIND-<id> / TASK-<id>
- Verified Snapshot / Manifest / at: SNAP-<id> / TEM-<id> / <ISO timestamp>
```

## Conditional task annexes

Append only annexes named by `control triggers`. Do not copy N/A annexes into an ordinary card.

```md
## TestSprite MCP (authorized Web UI only)
- Eligibility and provider-neutral test IDs:
- Local service URL/port and project path:
- Account, allowed read/write actions, test-data cleanup:
- TestSprite plan/cases:
- Implementation self-check evidence:
- Independent verifier evidence:

## Security impact
- Triggered:
- Review:
- Required mitigations and negative tests:

## Runtime-chain matrix
- Trigger:
- Entry → authorization/precondition → scheduling or claim → state transition → side effect → recovery/compensation → observable result:
- REQ / AC / module / test mapping for each critical stage:

## Acceptance checkpoint
- Requirement: checkpoint ID
- Scope: batch / milestone / complete user-facing flow / human-requested review
- Mode: blocking / non-blocking
- Status: pending / accepted / rejected / conditional
- Technical outcome: pending / verified-complete

## Human feedback and change record
- Date:
- Outcome: passed / rejected / conditional / scope changed / cancelled or replaced
- Feedback and evidence:
- Classification: approved-scope defect / new or changed scope / cancelled or replaced scope
- Linked requirements and tasks:
- Decision: DEC-<NNN> / none
- Next action:

## Baseline and re-entry impact
- Accepted unaffected REQ / AC / TEST:
- Affected baseline:
- Impacted modules / interfaces / data / dependent tasks:
- Return state: analysis / awaiting-human-decision
- Updated artifacts (requirements / design / tests / security):
- Affected-scope readiness review:
- May re-enter implementation: yes / no
```

## Discussion record

```md
# DISC-<id>: <topic>

## State
active / summarized / awaiting human decision / resolved

## Initiator and participating roles

## Linked sources, tasks, and decisions

## One question

## Known evidence
- 

## Each role's position
### <role>

## Coordinator summary

## Next action
- Update an artifact or link a decision card:
```

## Role assignment envelope

```md
# Role Assignment: <role> / <task or scope>

- Agent identity: AGENT-<id>
- Current snapshot: SNAP-<id> in `TASK-...md`
- Required authority sections: `Shared assignment contract`; `<exact role H2>`; `<exact workflow H2/gate>`
- Read-only inputs: exact project-relative paths and sections
- Allowed writes: exact paths, or none
- Forbidden writes/actions: exact paths plus business-code/Git/deployment restrictions
- Expected artifact or verdict:
- Receiving role: delivery coordinator / named next role
- Exit condition:
- Agent lifecycle: reuse within the same frozen task/batch scope after reading the refreshed Snapshot and diff; retire on role, scope, requirement, or contract change
```

## Review evidence record

```md
# EVID-<id>: <task and review scope>

- Reviewer identity: AGENT-<id>
- Role: independent verifier / code and security reviewer
- Review phase: task-design / implementation-readiness / fast-design-readiness / verification / code-security
- Snapshot and Manifest: SNAP-<id> / TEM-<id>
- Reviewed scope and inputs:
- Commands or inspection performed:
- Evidence and findings:
- Verdict: PASS / FAIL / conditional-pass
- Invalidated by:
- Recorded at: <ISO timestamp>
```

## Security-impact review

```md
# Security Impact Review: <phase or tasks>

## Trigger
authentication / authorization / sensitive data / payment / upload / external input or URL / secret / third-party API or webhook / dependency change

## Data and trust boundary
- Sensitive data:
- Trust boundary:
- Authorization rule:

## Risks and mitigations
- Abuse cases:
- Input, output, and logs:
- Dependencies and secrets:
- Required design mitigations:
- Required negative tests:

## Verdict
design-ready / awaiting decision / blocked
```

## Minimal Fast-path task card

This complete Fast-only skeleton contains every section required by strict validation. It keeps traceability and independent verification while omitting project-level repetition.

```md
# TASK-EXAMPLE-001: Clarify local contributor documentation

## Handoff Snapshot
- Workflow revision: ai-team-2026-08-12-r16
- Snapshot ID and updated at: SNAP-EXAMPLE-001-01 / 2026-08-12T10:00+08:00
- Current state and technical outcome: awaiting-verification / not-complete
- Scope, source, decision, and contract references: REQ-EXAMPLE-001 / AC-EXAMPLE-001 / TEST-EXAMPLE-001 / `.ai-team/sources.md`; no decision or contract change
- Delivery lane / complexity / control triggers: fast / S / none — documentation-only wording change
- Batch / dependencies / entry: batch-not-applicable / none / source and local file available
- Change-set file inventory: `CONTRIBUTING.md`
- Fingerprint policy: N/A — Fast documentation-only change
- Current change-set fingerprint: N/A — Fast documentation-only change
- Actor identities: product=AGENT-PA-EXAMPLE; technical=AGENT-TL-EXAMPLE; implementer=AGENT-IE-EXAMPLE; verifier=AGENT-IV-EXAMPLE; reviewer=N/A — Fast merged-verifier review
- Open findings / blockers: none
- Next action, exit condition, and invalidation: verifier runs TEST-EXAMPLE-001; exit on PASS; invalidate on source or documentation-scope change

## Fast merged design/readiness
- Independent verifier identity: AGENT-IV-EXAMPLE
- Report: `.ai-team/evidence/EXAMPLE-001-fast-gate.md`
- Scope / acceptance / checks: REQ-EXAMPLE-001 → AC-EXAMPLE-001 → TEST-EXAMPLE-001; `markdownlint CONTRIBUTING.md`
- Verdict: implementation-ready
- Invalidated by: source, scope, command, or target-file change

## Fast execution and verification
- Implementer / self-check / evidence: AGENT-IE-EXAMPLE / PASS — markdownlint and requested wording inspection / `.ai-team/evidence/EXAMPLE-001.md`
- Independent verifier / verdict / evidence: AGENT-IV-EXAMPLE / pending fresh TEST-EXAMPLE-001 / `.ai-team/evidence/EXAMPLE-001.md`
- Findings / severity / affected / follow-up: none / N/A — no finding / REQ-EXAMPLE-001 AC-EXAMPLE-001 TEST-EXAMPLE-001 / none
- Verified Snapshot / at: SNAP-EXAMPLE-001-01 / 2026-08-12T10:30+08:00
```

## Complete Standard task card example

This compact example passes the `implementation-ready` gate. Shared requirements, design, baseline, and batch regression remain project-level references instead of being recopied into the card.

```md
# TASK-EXAMPLE-STD-001: Add validation for calculator expression input

## Handoff Snapshot
- Workflow revision: ai-team-2026-08-12-r16
- Snapshot ID and updated at: SNAP-EXAMPLE-STD-001-01 / 2026-08-12T11:00+08:00
- Current state and technical outcome: implementation-ready / not-complete
- Scope, source, decision, and contract references: REQ-EXAMPLE-STD-001 / AC-EXAMPLE-STD-001 / TEST-EXAMPLE-STD-001 TEST-EXAMPLE-STD-002 / `.ai-team/sources.md`; no decision or contract change
- Delivery lane / complexity / control triggers: standard / M / none — synchronous local validation using the existing module contract
- Batch / dependencies / entry: BATCH-EXAMPLE-01 / none / frozen design and planning PASS
- Change-set file inventory: `src/calculator/input.ts`; `tests/calculator/input.test.ts`
- Fingerprint policy: required
- Current change-set fingerprint:
  - `src/calculator/input.ts` = 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
  - `tests/calculator/input.test.ts` = fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210
- Actor identities: product=AGENT-PA-EXAMPLE; technical=AGENT-TL-EXAMPLE; implementer=AGENT-IE-EXAMPLE; verifier=AGENT-IV-EXAMPLE; reviewer=N/A — ordinary Standard merged-verifier review
- Open findings / blockers: none
- Next action, exit condition, and invalidation: serial implementer completes focused checks; exit awaiting-verification; invalidate on requirement, design, contract, manifest, code, test, or environment change

## Plan and readiness
- Baseline and design references: `.ai-team/design/calculator-input.md`; `.ai-team/specs/acceptance.md`; `.ai-team/specs/traceability.md`
- Test Manifest revision and frozen-at: TEM-EXAMPLE-STD-001-01 / 2026-08-12T11:00+08:00
- Implementer checks: `npm run lint`; `npm test -- tests/calculator/input.test.ts`; `npm test -- tests/calculator`
- Independent task verification: TEST-EXAMPLE-STD-001 TEST-EXAMPLE-STD-002; `npm test -- tests/calculator`
- Batch regression: `npm test` once at BATCH-EXAMPLE-01 exit
- Risk and contract checks: invalid Unicode/control-character cases; no interface, security, or runtime-chain trigger
- Environment / data / reset: installed local dependencies / table-driven fixtures / isolated deterministic reset not required
- Planning verifier and report: AGENT-IV-EXAMPLE / `.ai-team/evidence/EXAMPLE-STD-001-readiness.md`
- Design/readiness verdict and conditions: implementation-ready / direct PASS; no deferred condition

## Acceptance criteria checklist
- [ ] AC-EXAMPLE-STD-001 / TEST-EXAMPLE-STD-001 rejects unsupported characters
- [ ] AC-EXAMPLE-STD-001 / TEST-EXAMPLE-STD-002 preserves valid arithmetic input

## Implementation self-check
- Implementation engineer identity: AGENT-IE-EXAMPLE
- Build / generation / lint-typecheck results: pending implementation
- Owner / affected / contract test results: pending implementation
- Omitted checks, residual risks, and evidence: none planned; Unicode normalization remains in independent verification

## Verification and findings
- Independent verifier identity: AGENT-IV-EXAMPLE
- Separate code/security reviewer identity: N/A — ordinary Standard merged-verifier review
- Independent verifier verdict: readiness PASS; implementation verification pending
- Separate code/security reviewer verdict: N/A — no separate-review trigger
- Independent verification evidence: `.ai-team/evidence/EXAMPLE-STD-001-verify.md`
- Separate code/security review evidence: N/A — no separate-review trigger
- Findings / severity / affected REQ-AC-TEST: none / N/A — no finding / REQ-EXAMPLE-STD-001 AC-EXAMPLE-STD-001 TEST-EXAMPLE-STD-001 TEST-EXAMPLE-STD-002
- Open P0/P1 / P2 follow-up: none
- Verified Snapshot / Manifest / at: SNAP-EXAMPLE-STD-001-01 / TEM-EXAMPLE-STD-001-01 / 2026-08-12T11:30+08:00
```

## Required fingerprint example

This excerpt shows the exact ledger syntax for Standard, High-risk, and other tasks whose fingerprint policy is `required`. The digest values are illustrative; compute and replace them from the current files.

```md
## Handoff Snapshot
- Change-set file inventory: `src/foo/bar.ts`; `tests/foo/bar.test.ts`
- Fingerprint policy: required
- Current change-set fingerprint:
  - `src/foo/bar.ts` = 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
  - `tests/foo/bar.test.ts` = fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210
```

## Acceptance checkpoint package

```md
# Acceptance Checkpoint: <checkpoint ID>

- Mode: blocking / non-blocking
- Status: pending / accepted / rejected / conditional

## Requested response
accept / reject / conditional acceptance

## Checkpoint scope
- Batch or milestone:
- Included completed tasks:
- Why human review is required:

## Product outcome
- What is now true:
- In scope:
- Out of scope:

## Evidence summary
| Task | User-visible or contract result | Independent verification/review | Local artifact links |
| --- | --- | --- | --- |

## Known limitations and residual risks
- 

## Human response and re-entry
- Result:
- Feedback:
- Affected requirements / tasks:
- Next action:
```
