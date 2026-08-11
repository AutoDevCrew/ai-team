# Backlog

The delivery coordinator maintains this as the only project backlog.

| ID | Task | State | Owner role | Dependencies | Card |
| --- | --- | --- | --- | --- | --- |

## State legend

`analysis → awaiting-human-decision → task-design-ready → implementation-ready → implementing → awaiting-verification → complete`

`blocked` is an additive state and must link to a decision or prerequisite. Use `design-blocked` only for missing/contradictory design inputs; use `implementation-blocked` for pending upstream code, environment, or project-stage opening. `cancelled/superseded` is a terminal state; identifiers are never reused. The coordinator marks a task `complete` with technical outcome `verified-complete` after independent verification/review pass unless it belongs to a named blocking acceptance checkpoint.

## PASS scope legend

Record the scope beside every verdict: `engineering baseline` (project-level, when applicable; link its baseline artifact), `governance foundation`, `task design`, `task implementation-ready`, or `project stage`. A PASS only applies to its recorded scope. Engineering baseline PASS freezes project constraints but does not authorize business implementation; a business task enters `implementation-ready` only after its own readiness PASS and an implementation-permitted project stage.

After every governance or task-design verdict, the coordinator advances the next planning-eligible card without waiting for a human prompt. A frozen upstream contract permits downstream design; only missing or conflicting design inputs block planning.

## Implementation batches

| Batch | Objective | Member tasks | Serial implementation order | Entry criteria | Exit evidence | Acceptance checkpoint | Implementation authority |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B1 |  |  |  |  |  | none / checkpoint ID | project stage / explicit boundary / not applicable |

Batch membership controls delivery cadence, not task readiness. Each task retains its own design and implementation verdict. Unless the backlog names a blocking acceptance checkpoint, independently verified member tasks complete automatically. Unless the human sets an explicit batch implementation boundary, continue planning and preparing later batches without waiting for a prompt.
