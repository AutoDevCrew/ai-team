# Decision Log

This file is the only source of confirmed human decisions. Use monotonically increasing `DEC-<NNN>` identifiers. A decision card and its confirmed log entry use the same ID; do not create a parallel `D-<NNN>` namespace. Do not overwrite prior decisions; add a new decision when policy changes.

## DEC-001: Markdown task management

- **Decision:** Use repository Markdown for task tracking.
- **Location:** `../tasks/backlog.md` is the only backlog; every work item has one `TASK-<id>-<slug>.md` card somewhere under the manifest-declared Task root.
- **Not used:** External task systems.

## DEC-002: Local-only AI authority

- **Allowed:** Modify local files, run local builds/tests, and create local evidence.
- **Forbidden:** Create branches, commit, push, create pull requests, deploy, or access/modify production.
- **Human responsibility:** Version-control, deployment, and production actions.

## DEC-003: Agent roles and implementation model

- **Decision:** Use Codex as the coordinator and temporary specialist roles; do not build a separate orchestration framework.
- **Implementation:** One serial implementation engineer modifies business code.
- **Handoffs:** Use project artifacts; use `DISC-xxx` only for unresolved questions.

## DEC-004: Autonomous decisions and human escalation

- **Decision:** AI decides from the PRD or recorded initial user request, confirmed decisions, source evidence, code, tests, and project rules, using the smallest reversible solution that meets acceptance criteria.
- **Escalate only when:** Sources are missing or contradictory; scope or acceptance cannot be determined; authority is missing; or a choice has unresolved irreversible, security, privacy, permission, external-cost, or production impact.
- **Implementation condition:** Independent readiness passes and no blocking decision remains. A separate human implementation-authorization gate is not required by default.
- **Recordkeeping:** Record human choices here and AI rationale/evidence in requirement, design, task, or test artifacts.
