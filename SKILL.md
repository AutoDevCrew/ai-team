---
name: ai-team
description: Launch or refine a Codex-run local software delivery team from a PRD with optional Figma and/or Demo inputs. Use when setting up reusable AI-team project rules, role handoffs, Markdown task tracking, scoped Demo inspection, structured multi-agent discussions, and human decision gates without building a separate orchestration system.
---

# AI Team

Run a Codex-native software delivery workflow from requirement input through local verification and named human acceptance checkpoints. Use one serial implementation engineer and independent verification; do not build another orchestration framework.

Workflow revision: `ai-team-2026-08-12-r18`. Projects use this current layout only; older workflow layouts are unsupported.

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

Read the complete delivery policy and role protocol before initializing or materially revising a project workflow. Read the template catalog when creating or changing an artifact schema.

After initialization, the project-local copies are the runtime authority:

- `.ai-team/manifest.md` — paths.
- `.ai-team/governance/workflow-schema.json` — deterministic workflow contract consumed by project validators.
- `.ai-team/stage.md` — current project-stage authorization and provenance.
- `.ai-team/project-rules.md` — project overrides and authority index only.
- `.ai-team/governance/workflow.md` — project delivery policy snapshot.
- `.ai-team/governance/roles.md` — project role protocol snapshot.
- `.ai-team/governance/templates.md` — exact project artifact schemas.
- `.ai-team/governance/decisions.md` — confirmed human decisions.
- `.ai-team/sources.md` plus the manifest-declared acceptance specification and requirement traceability matrix — current product evidence and frozen coverage.
- `.ai-team/tasks/` — task state and evidence-linked cards.

The global Skill is the installation source, not a project runtime dependency. Never link project artifacts to files under the installed Skill directory.

## Initialize or refine a project

1. Inspect root `AGENTS.md` and `.ai-team/manifest.md`; read existing project instructions before creating files.
2. If the namespaced layout is absent or incomplete, copy `assets/project-template/` without overwriting user material. Replace the `.ai-team/stage.md` updated-at placeholder with the current ISO timestamp while preserving its default `analysis-only` authority.
3. Copy `references/delivery-policy.md` to `.ai-team/governance/workflow.md`, `references/role-protocol.md` to `.ai-team/governance/roles.md`, and `references/workflow-schema.json` to `.ai-team/governance/workflow-schema.json`. Treat them as project-canonical snapshots; record project differences only in `.ai-team/project-rules.md` or confirmed decisions.
4. Keep `.ai-team/governance/workflow-schema.json` as the machine-readable field-group and enum authority, and `.ai-team/governance/templates.md` as the exact Markdown syntax authority. Do not reproduce their contracts elsewhere.
5. Copy `scripts/validate_task_handoff.py`, `scripts/extract_markdown_section.py`, `scripts/check_project_consistency.py`, and `scripts/render_fingerprint_ledger.py` to `.ai-team/scripts/` when task cards or role handoffs exist.
6. Create or update `.ai-team/sources.md` when delivery intake starts. Before promoting Standard/High-risk work, create the manifest-declared frozen acceptance specification and requirement traceability matrix. A standalone Fast non-behavior task may rely on its card-local traceability when both files are intentionally absent. Create other artifacts only when needed.
7. Preserve existing project material and history. Do not create root-level AI-team `docs/`, `tasks/`, `discussions/`, or helper-script trees.

## Run delivery

Follow the project-local workflow and roles. At a minimum:

1. Register the PRD or verbatim initial request; Figma and Demo are optional evidence.
2. Scope Demo inspection to the current phase before using the browser. Authorized login, navigation, and non-mutating search/filter actions are allowed; do not change business data, settings, permissions, or external state. Record exclusions and do not infer uninspected legacy behavior.
3. Have product analysis produce traceable, testable acceptance criteria. Activate UX/UI only when UI evidence and existing patterns leave material experience details unspecified.
4. Have the technical lead derive an existing-repository baseline or create a greenfield baseline and minimal design. For an unfamiliar or large repository, use `$repomix-explorer` for scoped read-only discovery when available; otherwise continue with targeted local search and record the limitation.
5. Have the independent verifier review intake/baseline when applicable and perform one batch-planning pass for task test coverage and readiness. Product, UX, technical, and implementation authors never approve the delivery artifacts they authored.
6. Maintain one backlog and one compact delta card per work item. Keep project-wide requirements, baseline, design, default commands, and traceability in their existing project artifacts; never copy them into every card.
7. When the host supports child agents, keep the root agent as coordinator. Reuse a bounded specialist within the same task or batch while role, scope, and frozen requirement/contract inputs remain unchanged; invalidate evidence rather than the Agent merely because code changes. Start exactly one serial implementation engineer only after implementation readiness and scoped `.ai-team/stage.md` authorization pass.
8. For Fast and ordinary Standard work, one independent verifier may combine diff review and test verification while remaining independent from the implementer. Launch a separate code/security reviewer only for High-risk or interface, security, runtime-chain, or material baseline triggers.
9. Run focused verification per task and one approved full regression at batch exit; High-risk work may retain a per-task full suite. A task becomes `complete / verified-complete` only from current evidence; human acceptance occurs only at a named checkpoint.

Within the authorized stage, continue to the next eligible planning, remediation, implementation, or verification action. At a task boundary, use one project-check command with `--task TASK-... --gate <gate> --next-action`; execute or dispatch an eligible local action instead of merely reporting it. Stop only for a genuine human decision, missing required external authority/evidence, completion of all allowed work, a user pause/status request, or a forced turn end.

## Project boundaries

- Work locally only. Do not create branches, commits, pushes, pull requests, deployments, or production changes unless the user explicitly changes the project policy.
- Use only authorized non-production accounts and data. Never write credentials into project artifacts.
- Only the serial implementation engineer modifies approved business-code paths. The verifier may add independent tests/evidence but not business code; the security reviewer is read-only.
- Every role assignment states required reads, allowed writes, forbidden writes, and exit conditions.
- Decide autonomously from sufficient sources, decisions, code, tests, and reversible local conventions. Escalate only unresolved evidence/authority/scope or material irreversible, security, privacy, permission, external-cost, or production impact.

## Improve this Skill

Update project-local files for product-, stack-, organization-, or permission-specific rules. Update this global Skill only for reusable workflow improvements explicitly requested by the user. Use a deletion-first audit: a new mandatory artifact, field, state, or script must replace existing complexity or address a frequent uncovered delivery failure. Reject net growth by default. Change only the single authority and its executable/template consumers—not parallel summaries.
