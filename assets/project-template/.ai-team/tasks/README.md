# Task Management

This directory is the sole source of task state. Use one backlog and one task card per work item; do not use an external task system.

Task cards use workflow revision `ai-team-2026-08-12-r16`.

## Files and identifiers

- `backlog.md` — maintained by the delivery coordinator.
- `TASK-<id>-<slug>.md` — one work item; IDs start at `TASK-001`, increase sequentially, and are never reused.
- Batch or milestone subdirectories are allowed under the manifest-declared Task root. Every card and backlog link remains unique; the validator resolves the nearest `.ai-team/manifest.md` and confirms the card is inside its declared Task root.

## Create or update a task

1. Before the first task, fill the canonical source register. Before promoting Standard/High-risk work, freeze the manifest-declared acceptance specification and requirement traceability matrix; a standalone Fast non-behavior task may use card-local traceability when both files are intentionally absent. Then run the project consistency checker.
2. Use the manifest-declared `extract_markdown_section.py` to read only the applicable `Task card` or `Minimal Fast-path task card` section in `../governance/templates.md`, then copy it without renaming required headings or fields.
3. Give the card a unique ID and add its unique link to `backlog.md`.
4. Follow `../governance/workflow.md` for lanes, states, gates, handoffs, validation, batching, completion, and re-entry.
5. Follow `../governance/roles.md` for who may write the card, backlog, code, tests, findings, and verdicts.
6. Keep the compact Handoff Snapshot current. Reference project-wide source/baseline/design/test defaults instead of copying them; keep raw or historical material in `.ai-team/evidence/`.
7. At a boundary, run the checker once with `--task TASK-... --gate <gate> --next-action` and execute or dispatch the reported dependency-eligible local action.

Do not restate global workflow or role rules here. Record project-specific deviations in `../project-rules.md` and authority-bearing choices in `../governance/decisions.md`.
