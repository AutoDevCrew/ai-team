# AI Team Project Rules

Workflow revision: `ai-team-2026-08-11`.

This file is the project authority index and override surface. It does not redefine global delivery rules, role responsibilities, or artifact fields.

## Authority order

1. `.ai-team/manifest.md` — canonical paths.
2. `.ai-team/governance/decisions.md` — confirmed human decisions.
3. `.ai-team/governance/workflow.md` — lanes, states, gates, severity, handoffs, validation, acceptance, and re-entry.
4. `.ai-team/governance/roles.md` — role responsibilities, boundaries, outputs, and exits.
5. `.ai-team/governance/templates.md` — exact artifact fields and Markdown syntax.
6. `.ai-team/tasks/backlog.md` and the active task card — current work state and evidence-linked continuation point.

For an active task, read its Handoff Snapshot and Required reads first. Open historical evidence only through its Evidence index. Conditional artifacts such as `engineering-baseline.md` and `experience-design.md` are read only when present and applicable.

## Project overrides

- Work locally only. Do not create branches, commits, pushes, pull requests, deployments, or production changes.
- Do not use real-user data or write credentials into project files.
- Use one serial implementation engineer. Only that role may modify task-approved business-code paths.
- The verifier may add independent tests/evidence but not business code. The security reviewer is read-only.
- AI decides evidence-backed, reversible, in-scope choices autonomously. Human decisions are limited to unresolved evidence/authority/scope or material irreversible, security, privacy, permission, external-cost, or production impact.
- Every role assignment states Required reads, allowed writes, forbidden writes, output, and exit conditions.

Add product-, stack-, organization-, or permission-specific deviations below. A deviation must identify the affected workflow section and confirmed decision when human authority is required.

## Local deviations

- None.
