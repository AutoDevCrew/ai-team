---
name: ai-team
description: Launch or refine a Codex-run local software delivery team from a PRD with optional Figma and/or Demo inputs. Use when setting up reusable AI-team project rules, role handoffs, Markdown task tracking, scoped Demo inspection, structured multi-agent discussions, and human decision gates without building a separate orchestration system.
---

# AI Team

Run a Codex-native software delivery workflow from requirement input through local verification and named human acceptance checkpoints. Use one serial implementation engineer and independent verification; do not build another orchestration framework.

Workflow revision: `ai-team-2026-08-11`. A later revision requires an explicit project-document sync; preserve historical evidence.

## Authority model

Do not restate one rule across several files. Use these global authorities:

- `references/delivery-policy.md` — lanes, states, gates, severity, handoffs, validation, acceptance, re-entry, and autonomous progression.
- `references/role-protocol.md` — role inputs, responsibilities, outputs, write boundaries, and exit conditions.
- `assets/project-template/.ai-team/governance/templates.md` — exact artifact fields and Markdown syntax.
- `scripts/validate_task_handoff.py` — executable structural, semantic, layout, and fingerprint validation.

Read the complete delivery policy and role protocol before initializing, migrating, or materially revising a project workflow. Read the template catalog when creating or changing an artifact schema.

After initialization, the project-local copies are the runtime authority:

- `.ai-team/manifest.md` — paths.
- `.ai-team/project-rules.md` — project overrides and authority index only.
- `.ai-team/governance/workflow.md` — project delivery policy snapshot.
- `.ai-team/governance/roles.md` — project role protocol snapshot.
- `.ai-team/governance/templates.md` — exact project artifact schemas.
- `.ai-team/governance/decisions.md` — confirmed human decisions.
- `.ai-team/tasks/` — task state and evidence-linked cards.

The global Skill is the upgrade source, not a project runtime dependency. Never link project artifacts to files under the installed Skill directory.

## Initialize or refine a project

1. Inspect root `AGENTS.md` and `.ai-team/manifest.md`; read existing project instructions before creating files.
2. If the namespaced layout is absent or incomplete, copy `assets/project-template/` without overwriting user material.
3. Copy `references/delivery-policy.md` to `.ai-team/governance/workflow.md` and `references/role-protocol.md` to `.ai-team/governance/roles.md`. These become editable project-local snapshots; record project differences only in `.ai-team/project-rules.md` or confirmed decisions.
4. Keep `.ai-team/governance/templates.md` as the only field/schema authority. Do not reproduce its field lists elsewhere.
5. Copy `scripts/validate_task_handoff.py` to `.ai-team/scripts/validate_task_handoff.py` when task cards exist.
6. Create `.ai-team/sources.md`, specifications, evidence, discussions, and task cards only when the current phase needs them. Conditional artifacts such as `engineering-baseline.md` and `experience-design.md` are not startup prerequisites unless the workflow triggers them.
7. Preserve existing project material and history. Do not create root-level AI-team `docs/`, `tasks/`, `discussions/`, or helper-script trees.

## One-time migration

Migrate only when the user explicitly requests it. Do not maintain a compatibility mode.

1. Inventory current instructions, governance, specifications, tasks, discussions, evidence, and AI-team helper scripts.
2. Classify delivery artifacts under `.ai-team/`; do not move business source, project tooling, generated output, runtime data, or deployment material.
3. Install the current local authority set: manifest, project rules, workflow, roles, templates, decisions, tasks, discussions, evidence, and validator.
4. Rename older numbered governance files to `roles.md`, `workflow.md`, and `templates.md`; update all Markdown links, Required reads, evidence links, and script paths.
5. Preserve IDs, decisions, historical PASS/FAIL evidence, accepted baselines, and active-task continuation state. Never mirror canonical files.
6. Run the validator, link audit, stale-path audit, and active-task snapshot audit.
7. Record a migration report and stop. Do not combine layout migration with product-scope analysis, business-code edits, test execution, Git actions, or deployment.

## Run delivery

Follow the project-local workflow and roles. At a minimum:

1. Register the PRD or verbatim initial request; Figma and Demo are optional evidence.
2. Scope Demo inspection to the current phase before using the browser. Inspect read-only and record exclusions; do not infer uninspected legacy behavior.
3. Have product analysis produce traceable, testable acceptance criteria. Activate UX/UI only when UI evidence and existing patterns leave material experience details unspecified.
4. Have the technical lead derive or create the engineering baseline and minimal design. For an unfamiliar or large repository, use `$repomix-explorer` for scoped read-only discovery; use targeted local search for known symbols.
5. Have the independent verifier review intake/baseline when applicable, produce the test plan, and issue scoped design/readiness verdicts. Authors never approve their own artifacts.
6. Maintain one backlog and one card per work item. The exact card fields come only from the local template catalog.
7. Start the one serial implementation engineer only after the local workflow's implementation-ready gate passes and the project stage permits code work.
8. Run independent verification and code/security review. A task state becomes `complete` only with technical outcome `verified-complete`; human acceptance occurs only at a named checkpoint.

Within the authorized stage, continue to the next eligible planning, remediation, implementation, or verification action. Stop only for a genuine human decision, missing required external authority/evidence, completion of all allowed work, a user pause/status request, or a forced turn end. Codex is not a background daemon; record the exact continuation point before returning when work remains.

## Project boundaries

- Work locally only. Do not create branches, commits, pushes, pull requests, deployments, or production changes unless the user explicitly changes the project policy.
- Use only authorized non-production accounts and data. Never write credentials into project artifacts.
- Only the serial implementation engineer modifies approved business-code paths. The verifier may add independent tests/evidence but not business code; the security reviewer is read-only.
- Every role assignment states required reads, allowed writes, forbidden writes, and exit conditions.
- Decide autonomously from sufficient sources, decisions, code, tests, and reversible local conventions. Escalate only unresolved evidence/authority/scope or material irreversible, security, privacy, permission, external-cost, or production impact.

## Improve this Skill

Update project-local files for product-, stack-, organization-, or permission-specific rules. Update this global Skill only for reusable workflow improvements explicitly requested by the user. When changing a canonical rule, edit its single authority and update navigation or copy instructions—not parallel summaries.
