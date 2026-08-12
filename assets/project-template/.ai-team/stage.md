# Project Stage

- Stage: analysis-only
- Authority: default stage until an explicit build/change/fix request or confirmed decision authorizes local implementation
- Scope: all tasks
- Updated at: <set to the current ISO timestamp during initialization>

`analysis-only` blocks business-code implementation but permits intake, design, test planning, security review, and readiness remediation. The coordinator may set `implementation-authorized` from an explicit local build/change/fix request; an explicit analysis-only restriction controls until the user changes it. Use `verification-only` only for already-implemented candidate verification.
