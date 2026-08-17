---
name: ai-team
description: Launch or refine a local coding-agent software delivery team from a PRD with optional Figma and/or Demo inputs. Use when setting up reusable AI-team project rules, role handoffs, Markdown task tracking, scoped Demo inspection, structured multi-agent discussions, and human decision gates without building a separate orchestration system.
---

# AI Team

Run a host-neutral software delivery workflow from requirement input through local verification and named human acceptance checkpoints. The agent host must provide local file access, shell execution, and Python 3. Use one serial implementation engineer and independent verification; do not build another orchestration framework.

Workflow revision: `ai-team-2026-08-16-r49`. Projects use this current layout only; older workflow layouts are unsupported.

## Authority model

Do not restate one rule across several files. Use these global authorities:

- `references/delivery-policy.md` — lanes, states, gates, severity, handoffs, validation, acceptance, re-entry, and autonomous progression.
- `references/role-protocol.md` — role inputs, responsibilities, outputs, write boundaries, and exit conditions.
- `references/workflow-schema.json` — machine-readable workflow revision, active enums, compact field groups, stage authorization, and table contracts.
- `assets/project-template/.ai-team/governance/templates.md` — exact artifact fields and Markdown syntax.
- `scripts/validate_task_handoff.py` — executable structural, semantic, layout, and fingerprint validation.
- `scripts/extract_markdown_section.py` — fence-aware, section-scoped reads of one named Markdown H2 section.
- `scripts/check_project_consistency.py` — read-only revision, layout, source, backlog, state-gate, evidence, and active-task drift checks.
- `scripts/render_fingerprint_ledger.py` — read-only generation of the declared change-set inventory and SHA-256 ledger.
- `scripts/intake_package_inventory.py` — deterministic snapshot, classification, and freshness verification for multi-file delivery packages.

Read the complete delivery policy and role protocol before initializing or materially revising a project workflow. Read the template catalog when creating or changing an artifact schema.

After initialization, `.ai-team/manifest.md` is the sole path authority and `.ai-team/project-rules.md` defines project-local authority precedence. Follow their project-local workflow, role, schema, template, stage, decision, source, specification, traceability, task, and evidence paths.

The installed workflow package is the initialization source, not a project runtime dependency. Never link project artifacts to files under its installation directory.

## Initialize or refine a project

1. Inspect root `AGENTS.md` and `.ai-team/manifest.md`; read existing project instructions before creating files.
2. If the namespaced layout is absent or incomplete, copy `assets/project-template/` without overwriting user material. Replace the `.ai-team/stage.md` updated-at placeholder with the current ISO timestamp while preserving its default `analysis-only` authority.
3. Copy `references/delivery-policy.md` to `.ai-team/governance/workflow.md`, `references/role-protocol.md` to `.ai-team/governance/roles.md`, and `references/workflow-schema.json` to `.ai-team/governance/workflow-schema.json`. Treat them as project-canonical snapshots; record project differences only in `.ai-team/project-rules.md` or confirmed decisions.
4. Keep `.ai-team/governance/workflow-schema.json` as the machine-readable field-group and enum authority, and `.ai-team/governance/templates.md` as the exact Markdown syntax authority. Do not reproduce their contracts elsewhere.
5. During initialization and before delivery intake, copy `scripts/validate_task_handoff.py`, `scripts/extract_markdown_section.py`, `scripts/check_project_consistency.py`, `scripts/render_fingerprint_ledger.py`, and `scripts/intake_package_inventory.py` to `.ai-team/scripts/`.
6. Create or update `.ai-team/sources.md` and complete applicable source-package coverage under [`Sources and intake`](references/delivery-policy.md#sources-and-intake) before product analysis. Apply the existing-code Repomix initialization gate before product analysis, baseline work, or task design. Before promoting Standard/High-risk work, create the manifest-declared frozen acceptance specification and requirement traceability matrix. A standalone Fast non-behavior task may rely on its card-local traceability when both files are intentionally absent. Create other artifacts only when needed.
7. Preserve existing project material and history. Do not create root-level AI-team `docs/`, `tasks/`, `discussions/`, or helper-script trees.

## Run delivery

Follow the project-local workflow and role protocol; do not recreate their rules in task prompts.

1. Register sources under [`Sources and intake`](references/delivery-policy.md#sources-and-intake); establish project-stage authority and select only the applicable checklist: [`Engineering baseline PASS`](references/delivery-policy.md#engineering-baseline-pass), [`Task-design-ready`](references/delivery-policy.md#task-design-ready), [`Implementation-ready`](references/delivery-policy.md#implementation-ready), or [`Technical completion`](references/delivery-policy.md#technical-completion).
2. Dispatch the applicable product, UX/UI, technical, and verification roles to produce only the inputs required by that exact checklist.
3. Maintain one backlog and compact delta cards under [`Task planning and batches`](references/delivery-policy.md#task-planning-and-batches); start one serial implementation engineer only after the task's readiness gate and stage authority pass.
4. Validate the current candidate under [`Handoffs and validation`](references/delivery-policy.md#handoffs-and-validation) and [`Test execution`](references/delivery-policy.md#test-execution); apply [`Human decisions and acceptance`](references/delivery-policy.md#human-decisions-and-acceptance) and [`Change and feedback re-entry`](references/delivery-policy.md#change-and-feedback-re-entry) when triggered.
5. At each routine task boundary, run the scoped check with `--task TASK-... --gate <gate> --compact --next-action`; run `--audit --next-action` only at the declared full-audit triggers. Execute or dispatch its eligible local action, then continue according to [`Autonomous progression and turn boundary`](references/delivery-policy.md#autonomous-progression-and-turn-boundary).

## Project boundaries

- Work locally only; do not perform Git publication, deployment, or production actions. Use authorized non-production accounts/data and never store credentials in project artifacts.
- Apply write boundaries and assignment contracts from the project-local role protocol.
- Apply autonomous-decision, escalation, and stop conditions only from the project-local delivery policy.

## Improve this Skill

Update project-local files for product-, stack-, organization-, or permission-specific rules. Update this installed workflow package only for reusable workflow improvements explicitly requested by the user. Use a deletion-first audit: a new mandatory artifact, field, state, or script must replace existing complexity or address a frequent uncovered delivery failure. Reject net growth by default. Change only the single authority and its executable/template consumers—not parallel summaries.
