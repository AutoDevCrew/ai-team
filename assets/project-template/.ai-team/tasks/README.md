# Task Management

This directory is the sole source of task state. Use one backlog and one task card per work item; do not use an external task system.

Task cards use workflow revision `ai-team-2026-08-11-r2` unless the project records a later migration.

## Files and identifiers

- `backlog.md` — maintained by the delivery coordinator.
- `TASK-<id>-<slug>.md` — one work item; IDs start at `TASK-001`, increase sequentially, and are never reused.
- Batch or milestone subdirectories are allowed under the manifest-declared Task root. Every card and backlog link remains unique; the validator resolves the nearest `.ai-team/manifest.md` and confirms the card is inside its declared Task root.

## Create or update a task

1. Before the first task, confirm every authority file declared by `../manifest.md` exists. Strict task validation enforces this layout.
2. Copy the appropriate full or Fast task-card structure from `../governance/templates.md` without renaming its required headings or fields.
3. Give the card a unique ID and add its unique link to `backlog.md`.
4. Follow `../governance/workflow.md` for lanes, states, gates, handoffs, validation, batching, completion, and re-entry.
5. Follow `../governance/roles.md` for who may write the card, backlog, code, tests, findings, and verdicts.
6. Keep the Handoff Snapshot current and place raw or historical material behind its Evidence index.

Do not restate global workflow or role rules here. Record project-specific deviations in `../project-rules.md` and authority-bearing choices in `../governance/decisions.md`.
