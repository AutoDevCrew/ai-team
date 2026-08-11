# Task Management

This directory is the sole source of task state. Use one backlog and one task card per work item; do not use an external task system.

## Files and identifiers

- `backlog.md` — maintained by the delivery coordinator.
- `TASK-<id>-<slug>.md` — one work item; IDs start at `TASK-001`, increase sequentially, and are never reused.

## State flow

```text
analysis → awaiting-human-decision → task-design-ready → implementation-ready → implementing → awaiting-verification → complete
```

`blocked` is additive and must link to a decision or prerequisite. Record it as `design-blocked` only when a frozen design input is missing, and as `implementation-blocked` when code changes await upstream implementation, environment, or project-stage opening. `cancelled/superseded` is terminal. The coordinator maintains backlog state/dependencies and advances the next eligible task after every design verdict or verified completion; the engineer updates only current-card progress/evidence. After independent verification and review pass, the coordinator marks the task `complete` with technical outcome `verified-complete` unless a named blocking acceptance checkpoint applies.

## Create and promote a task

1. Copy the task-card template from `docs/05-templates.md`.
2. Fill the source-linked Handoff Snapshot, sources, requirements, acceptance criteria, code context, applicable experience-design brief, decisions, interface/protocol disposition (`changed`, `reuses-frozen-contract`, or `N/A`) with contract reference or rationale, test plan, Test Execution Manifest, stable test IDs, environment readiness, and security review where applicable. An engineering-baseline default may be cited but never replaces the task-level disposition.
3. Assign `S/M/L/XL` complexity and record its concrete drivers. Assign an implementation batch or record why batching is not useful for a single-task change. Set `acceptance checkpoint: none` unless the backlog names a batch, milestone, complete user-facing flow, or human-requested checkpoint.
4. Add the unique card link to `backlog.md` with `analysis` or `awaiting-human-decision`.
5. Before recording the task-design verdict, run `scripts/validate_task_handoff.py <task-card> --strict`. The independent verifier confirms the manifest's groups are executable or have an N/A rationale and, when triggered, the runtime-chain matrix has complete mappings and entry-path tests; the strict script only rejects blank/placeholder fields. Record the verdict's reviewed task IDs and artifact scope. Promote to `task-design-ready` when the task's design inputs are frozen. Pending upstream implementation is not a design blocker when its contract is frozen; record it as `implementation-blocked` and continue planning later eligible tasks. Promote to `implementation-ready` only when that task's design and implementation dependencies are satisfied, its task-scoped implementation readiness passes, its assigned batch entry criteria pass (or it is `batch-not-applicable`), no blocking decision remains, and the project stage permits implementation. A governance/foundation `PASS` never promotes a business task.
6. Refresh the Handoff Snapshot and affected Test Execution Manifest before the next role handoff when sources, decisions, contracts, code, tests, commands, fixtures, environment, findings, or next action change. Put raw logs and superseded verdicts in the Evidence index; do not make them default role inputs.

## Change and re-entry

For human feedback, including a named checkpoint rejection or scope change, update the existing card and backlog, assess requirements/AC/tests/modules/interfaces/data/dependencies, and return affected work to analysis or decision. Preserve unaffected accepted work as Baseline. Rerun affected-scope readiness before implementation resumes.
