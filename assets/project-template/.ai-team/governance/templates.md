# Canonical Artifact Templates

## Catalog navigation

For normal work, read only the named H2 section below; do not load the entire catalog. Use the manifest-declared `extract_markdown_section.py` so headings inside fenced templates do not terminate the read. Use `Task card` for Standard/High-risk work and `Minimal Fast-path task card` only for eligible Fast work.

```sh
python3 .ai-team/scripts/extract_markdown_section.py .ai-team/governance/templates.md "Task card"
```

- Intake and specification: `Source register`, `Requirement traceability matrix`, `Acceptance specification`.
- Design: `Architecture and code-context pack`, `Experience design brief (UI scope only)`, `Engineering baseline (new project)`.
- Governance: `Decision card`, `Discussion record`, `Readiness review`.
- Delivery: `Task card`, `Test plan`, `Security-impact review`, `Implementation report`, `Acceptance checkpoint package`.
- Focused examples: `Minimal Fast-path task card`, `Required fingerprint example`.

## Source register

```md
# Source Register

## Product requirement source
- Type: PRD / initial user request
- URL or verbatim request:
- Authority: primary business-rule source
- Status: provided / no-PRD intake / superseded
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
- Evidence-backed rules:
- Conventional low-risk MVP assumptions and rationale:
- Awaiting material human decision:

## Scope
- In scope:
- Out of scope:

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
- Product analyst:
- UX/UI designer:
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

## Engineering baseline (new project)

```md
# Engineering Baseline: <project>

## State
- Version:
- Status: draft / Engineering baseline PASS / needs-baseline-remediation
- Technical lead:
- Independent verifier:
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

For `Fingerprint policy: required`, leave the value after `Current change-set fingerprint:` empty and add one actual ledger line per project-relative file using ``- `path` = <64-character lowercase SHA-256>``. For an eligible Fast-path `N/A`, put `N/A — <reason>` on the same line as the field. Do not retain instructional or placeholder ledger entries in a real card.

```md
# TASK-<id>: <title>

## Handoff Snapshot (current authoritative view)
- Workflow revision:
- Snapshot ID and updated at:
- Current state and technical outcome:
- Source and decision references:
- Frozen inputs and contracts:
- Current change-set fingerprint: <N/A — reason, or leave empty and add actual ledger lines below>
- Test Execution Manifest revision:
- Required reads:
- On-demand evidence / Evidence index:
- Open findings / blockers:
- Next action and exit condition:
- Invalidated by:

## Delivery priority
P0 / P1 / P2

## Goal

## Sources
- PRD or initial user request:
- Figma:
- Demo:
- Other evidence:

## Traceability
- Requirements:
- Acceptance criteria:
- Baseline and regression constraints:
- Code-context pack:
- Experience-design brief (UI scope only):

## Decision dependencies
- Confirmed: DEC-<NNN> / none
- Awaiting: DEC-<NNN> / none

## Delivery planning
- Execution lane: fast / standard / high-risk
- Complexity: S / M / L / XL
- Complexity drivers:
- Implementation batch:
- Batch entry criteria:
- Batch exit evidence:
- Fingerprint policy: required / N/A — <reason; N/A only for pure Fast-path documentation/style/metadata work>

## Task-design review
- Report:
- Reviewed scope:
- Verdict: task-design-ready / needs-design-remediation / not reviewed
- Design blockers:
- Implementation blockers:

## Implementation-readiness review
- Report:
- Reviewed scope:
- Verdict: implementation-ready / conditional-pass / implementation-blocked / not reviewed
- Conditional activation (Standard only): remaining mechanical conditions; required evidence; invalidation triggers; coordinator activation record / N/A

## Role boundary
- Current role:
- Read-only inputs:
- Allowed write paths:
- Forbidden write paths:
- Exit condition:

## Allowed / forbidden code scope
- Allowed:
- Forbidden:

## Acceptance criteria
- [ ]

## Interface/protocol disposition
- Disposition: changed / reuses-frozen-contract / N/A
- Frozen/inherited contract reference or N/A rationale:
- Contract-test IDs and scope: N/A / TEST-<NNN>

## Test plan and environment
- Plan:
- Status: draft / task-design-approved / needs-design-remediation
- Test Execution Manifest:
  - Revision and frozen-at:
  - Fast-gate group and command:
  - Owner test group and command:
  - Affected/regression test group and command:
  - Approved full suite and runner:
  - Independent risk/mutation group and runner:
  - Expected evidence and invalidation conditions:
- Required implementation self-check commands:
- Accounts:
- Data/fixtures:
- Local dependencies:
- Reset method:
- Verified commands:

## Implementation self-check
- Build / generation / lint-typecheck results:
- Approved test and contract-case results:
- Omitted checks and rationale:
- Residual risks:

## Evidence index
- Current source/design/decision evidence:
- Current test and review evidence:
- Partial execution record (when stopped early): Manifest revision; executed groups/results; unexecuted groups and stop reason:
- Raw logs or large outputs (on demand):
- Superseded snapshot, manifest, or verdict:

## Test-case impact
- Linked test IDs:
- Impact: unchanged / add regression / update steps / update expectation / superseded
- Reason and linked requirement/defect:
- Prior evidence:
- Affected-test and regression result:

## TestSprite MCP (Web UI only, authorized)
- Eligibility: eligible Web UI / not a Web UI change / unavailable / awaiting authority
- Local service URL/port and project path:
- Account, allowed actions, data cleanup:
- TestSprite plan/cases:
- Implementation self-check evidence:
- Independent verifier evidence:
- Optional deployed test/pre-production URL:

## Security impact (if triggered)
- Triggered: yes / no
- Review:
- Required mitigations and negative tests:

## Runtime-chain matrix (when applicable)
- Trigger: state machine / worker / asynchronous job / transaction / authorization boundary / external side effect / N/A
- Entry → authorization/precondition → scheduling or claim → state transition → side effect → recovery/compensation → observable result:
- REQ / AC / module / test mapping for each critical stage:

## Verification and review findings
- Independent verifier verdict:
- Code/security reviewer verdict:
- Findings: none / <finding IDs>
- Finding severity: P0 / P1 / P2
- Reproducible evidence:
- Affected requirement / acceptance criterion / test:
- Disposition:
- Open blocking findings (P0/P1): none / <finding IDs>
- P2 follow-up task(s): none / <TASK IDs>

## Risk and recovery

## Acceptance checkpoint
- Requirement: none / checkpoint ID
- Scope: batch / milestone / complete user-facing flow / human-requested review
- Blocking: yes / no
- Technical outcome: pending / verified-complete

## State
analysis / awaiting-human-decision / task-design-ready / implementation-ready / implementing / awaiting-verification / complete / cancelled/superseded

## Blocker (if any)
- Reason:
- Linked decision or prerequisite:

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
- Affected Baseline:
- Impacted modules / interfaces / data / dependent tasks:
- Return state: analysis / awaiting-human-decision / N/A
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

## Readiness review

```md
# Readiness Review: <phase or tasks>

## Independent reviewer

## Review mode
task design / combined Standard design-and-readiness / separate High-risk implementation-readiness

## Inputs
- Source register:
- Traceability matrix:
- Acceptance specification:
- Experience-design brief (UI scope only):
- Design:
- Task split:
- Test plan:

## Checks
- Every requirement source item classified: pass / fail
- Observable acceptance for in-scope requirements: pass / fail
- Acceptance mapped to design, task, and test: pass / fail
- UI experience rules mapped to source/brief, acceptance, and test: pass / fail / N/A
- Design changes trace to requirement: pass / fail
- Baseline impact and regression constraints: pass / fail
- Quality treatment or N/A rationale: pass / fail
- Test environment readiness: pass / fail
- Blocking decisions resolved: pass / fail

## Blockers and decisions
- 

## Verdict
task-design-ready / implementation-ready / conditional-pass / not ready

## Conditional Standard activation (when used)
- Remaining mechanical conditions:
- Required evidence:
- Invalidation triggers:
- Coordinator activation record:
```

## Test plan

```md
# Test Plan: <phase or tasks>

## Author
Independent verifier

## Review participants
- Product analyst:
- UX/UI designer when applicable:
- Technical lead:
- Code/security reviewer when applicable:

| Test ID | Requirement / AC | Scenario | Preconditions / data | Environment | Method | Expected result | Baseline regression | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TEST-001 | AC-001 | normal |  |  | unit / API / contract / E2E / manual |  |  |  |

## Interface/protocol contract cases (when applicable)
- Contract/schema/version:
- Generation or serialization/deserialization:
- Valid and invalid inputs; success and error outputs:
- Permission and authorization behavior:
- Compatibility, defaults, and unknown fields:
- Retry, idempotency, ordering, concurrency, or transaction cases:
- N/A rationale:

## Automation eligibility
- Local automation:
- TestSprite MCP (Web UI only) eligibility, local service/port, and external-service boundary:

## Implementation self-check requirements
- Required build / generation / lint-typecheck commands:
- Required test IDs and contract cases:
- Required self-check evidence:

## Untestable items and risks
- 

## Environment readiness
- Accounts:
- Data/fixtures:
- Dependencies:
- Reset:
- Verified commands:
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

This complete Fast-only skeleton contains every section required by strict validation. Replace the example IDs, paths, commands, evidence, and rationale. Use the full task-card template when the task does not qualify for Fast path.

```md
# TASK-EXAMPLE-001: Clarify local contributor documentation

## Handoff Snapshot
- Workflow revision: ai-team-2026-08-11-r4
- Snapshot ID and updated at: SNAP-EXAMPLE-001-01 / 2026-08-11T10:00+08:00
- Current state and technical outcome: awaiting-verification / not-complete
- Source and decision references: REQ-EXAMPLE-001; no decision required
- Frozen inputs and contracts: existing contributor workflow; no behavior or interface change
- Current change-set fingerprint: N/A — pure documentation-only change
- Test Execution Manifest revision: TEM-EXAMPLE-001-01
- Required reads: `.ai-team/specs/acceptance.md`; task card acceptance criteria
- On-demand evidence / Evidence index: `.ai-team/evidence/EXAMPLE-001.md`
- Open findings / blockers: none
- Next action and exit condition: verifier runs TEST-EXAMPLE-001; exit on PASS
- Invalidated by: source, documentation scope, or contributor workflow change

## Delivery planning
- Execution lane: fast
- Complexity: S
- Complexity drivers: one documentation-only wording change; no behavior change
- Fingerprint policy: N/A — pure documentation-only Fast-path task

## Test plan and environment
- Test Execution Manifest:
  - Revision and frozen-at: TEM-EXAMPLE-001-01 / 2026-08-11
  - Fast-gate group and command: N/A — Fast path; no contract/security/runtime trigger
  - Owner test group and command: `markdownlint CONTRIBUTING.md`
  - Affected/regression test group and command: N/A — no runtime or product behavior affected
  - Approved full suite and runner: N/A — documentation-only Fast path
  - Independent risk/mutation group and runner: N/A — no applicable risk surface
  - Expected evidence and invalidation conditions: lint output and rendered Markdown inspection; documentation scope change invalidates

## Evidence index
- Current source/design/decision evidence: `CONTRIBUTING.md`; REQ-EXAMPLE-001
- Current test and review evidence: `.ai-team/evidence/EXAMPLE-001.md`
- Partial execution record (when stopped early): N/A — all planned checks executed
- Raw logs or large outputs (on demand): `.ai-team/evidence/EXAMPLE-001-lint.txt`
- Superseded snapshot, manifest, or verdict: N/A — first revision
```

## Required fingerprint example

This excerpt shows the exact ledger syntax for Standard, High-risk, and other tasks whose fingerprint policy is `required`. The digest values are illustrative; compute and replace them from the current files.

```md
## Handoff Snapshot
- Current change-set fingerprint:
  - `src/foo/bar.ts` = 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
  - `tests/foo/bar.test.ts` = fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210

## Delivery planning
- Execution lane: standard
- Fingerprint policy: required
```

## Implementation report

```md
# Implementation Report: TASK-<id>

## Summary

## Changes
- Files:
- Reason:

## Local verification evidence
- Commands:
- Results:

## Limits and follow-up

## Suggested independent verification focus
```

## Acceptance checkpoint package

```md
# Acceptance Checkpoint: <checkpoint ID>

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
