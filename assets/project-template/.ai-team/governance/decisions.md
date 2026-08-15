# Decision Log

This file records project decision entries with `- Status: open`, `pending`, `confirmed`, `rejected`, or `obsolete`. Only `confirmed` `DEC-<NNN>` entries clear a blocker; every other status keeps it blocked. Use monotonically increasing project `DEC-<NNN>` identifiers. Do not overwrite prior decisions; update status or add a new decision when policy changes. `POL-<NNN>` entries below are template governance policies, not project decisions.

## POL-001: Markdown task management

- Status: confirmed
- **Decision:** Use repository Markdown for task tracking.
- **Location:** `../tasks/backlog.md` is the only backlog; every work item has one `TASK-<id>-<slug>.md` card somewhere under the manifest-declared Task root.
- **Not used:** External task systems.

## POL-002: Local-only AI authority

- Status: confirmed
- **Allowed:** Modify local files, run local builds/tests, and create local evidence.
- **Forbidden:** Create branches, commit, push, create pull requests, deploy, or access/modify production.
- **Human responsibility:** Version-control, deployment, and production actions.

## POL-003: Agent roles and implementation model

- Status: confirmed
- **Decision:** Use the active agent or session as the coordinator and temporary isolated specialist workers when available; do not build a separate orchestration framework.
- **Implementation:** One serial implementation engineer modifies business code.
- **Handoffs:** Use project artifacts; use `DISC-xxx` only for unresolved questions.
- **Runtime topology:** Keep the primary agent or session as coordinator, one writable serial implementer, and at most two concurrent temporary read-only specialists/reviewers; retire specialist workers after handoff. When isolation is unavailable, disclose that limitation and execute bounded role passes sequentially.

## POL-004: Autonomous decisions and human escalation

- Status: confirmed
- **Decision:** AI decides from the PRD or recorded initial user request, confirmed decisions, source evidence, code, tests, and project rules, using the smallest reversible solution that meets acceptance criteria.
- **Escalate only when:** Sources are missing or contradictory; scope or acceptance cannot be determined; authority is missing; or a choice has unresolved irreversible, security, privacy, permission, external-cost, or production impact.
- **Implementation condition:** Independent readiness passes and no blocking decision remains. A separate human implementation-authorization gate is not required by default.
- **Recordkeeping:** Record human choices here and AI rationale/evidence in requirement, design, task, or test artifacts.
