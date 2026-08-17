# Source Register

Fill the product requirement source before product analysis. Add optional evidence only when supplied or inspected; do not leave an optional section implying evidence was read.

## Product requirement source
- Type: PRD / initial user request
- URL or verbatim request:
- Authority: primary business-rule source
- Status: provided / no-PRD intake
- Version or updated at:
- Read at:

## Delivery package coverage
- Applicability: applicable / N/A — one registered URL or verbatim request and no multi-file package
- Package root or source set:
- Inventory manifest: `.ai-team/evidence/intake-package.json`
- Coverage counts: total=<n>; reviewed=<n>; excluded=<n>; gap=<n>
- Excluded classes and rationale: none / <classes and concrete rationale>
- Unresolved gaps: none / <item and access or format gap>
- Independent intake review: PASS — AGENT-<id> / EVID-<id> / `.ai-team/evidence/<intake-review>.md` / <ISO timestamp>

## Figma (optional)
- URL / page / node:
- Authority: visual, layout, component-state evidence
- Read at:
- Status: provided / not provided

## Demo (optional)
- URL and environment:
- Authorized test-account method:
- Allowed read-only actions: login / navigation / pagination / search / filter
- Forbidden mutations and any separately authorized reversible test action:
- Authority: scoped behavioral evidence
- Current-phase read-only scope (flows/pages/routes):
- Explicit legacy exclusions:
- Inspected pages/routes and evidence time:
- Evidence gap:

## Code baseline
- Repository / directory:
- Mode: existing-code / greenfield
- Repomix initialization: PASS — Repomix <version>; runner=<repomix or npx --yes repomix@latest>; command=<exact command>; scope=<packed scope>; exclusions=<secret/generated/dependency exclusions>; files=<count>; tokens=<count> / N/A — greenfield has no pre-existing business or test source
- Baseline description:
- Modules and tests inspected:
- Read at:
