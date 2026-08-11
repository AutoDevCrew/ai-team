# AI Company Project Documentation

This documentation defines a human-governed, Codex-run local software delivery workflow with one serial implementation engineer.

## Reading order

1. `engineering-baseline.md` — required for a new project; frozen implementation and automation constraints.
2. `experience-design.md` — read when a UI task activates the UX/UI designer.
3. `02-roles-and-boundaries.md` — role responsibilities, boundaries, and handoffs.
4. `03-workflow-and-decision-gates.md` — sources, stages, task state, and escalation.
5. `05-templates.md` — source, decision, experience, task, test, and acceptance templates.
6. `decisions.md` — confirmed human decisions.
7. `../tasks/README.md` and `../tasks/backlog.md` — task state.
8. `../discussions/README.md` — focused multi-role discussions.

`../AGENTS.md` is the project entry point. For an active task, first read its source-linked Handoff Snapshot and required-read set, then open historical evidence only through its Evidence index when needed. Generate phase artifacts such as `sources.md`, `acceptance.md`, `experience-design.md` for an activated UI scope, and `architecture.md` only when work begins. For a new project, generate `engineering-baseline.md` before task design; an existing project derives it from the repository configuration and code context.

## Core conventions

- AI decides from sufficient evidence; human decisions are for unresolved evidence, missing authority, or material irreversible/external impact.
- Work is traceable: `REQ → AC → TEST → TASK → evidence`.
- The active task card holds the current Handoff Snapshot and Test Execution Manifest; historical logs and superseded conclusions live in an Evidence index, not every role's default reading set.
- The independent verifier first reviews task design; a task-design PASS lets planning continue but does not authorize code. Implementation additionally requires task implementation-ready and a project stage open.
- Independent verification and review complete an ordinary local task. Human acceptance occurs only at a named checkpoint; rejected or changed work follows impact analysis and an affected-scope readiness review; unaffected accepted work becomes a logical Baseline.
- TestSprite MCP is optional Web UI automation for an authorized local Web UI service; it does not replace unit, integration, or contract tests and blocks technical completion only when a task explicitly requires it.
