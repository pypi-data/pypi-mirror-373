
# Contributing Guide

Thanks for contributing! This repo is optimized for AI pair coding and human review.

## Branching & Commits
- Branch from `main` using: `feature/<short-goal>`, `refactor/<module>`, or `fix/<ticket>`.
- Use Conventional Commits (feat, fix, refactor, docs, test, chore, build, ci).

## Local Dev & CI
- Run local CI before pushing:
  ```bash
  scripts/ci_local.sh
  ```
- Add/adjust tests **before** behavior changes.
- Keep diffs small and focused; open PRs early.

## Context Discipline (MANDATORY)
- `/context/*` is canonical for agent runs. Update the Context Sync block in `context/development.md` after each change:
```
## Context Sync (AUTO-UPDATED)
Overall goal is: <PRIMARY GOAL>
Last action was: <what changed and why> (commit SHA)
Next action will be: <smallest valuable step with owner>
Blockers/Risks: <if any>
```

## Pull Requests
- Use the PR template (risk, test plan, rollback, context diff).
- Public API/infra changes require an ADR under `/docs/adr/`.
- High-risk PRs require CODEOWNERS sign-off.

## Secrets & Data Safety
- Never commit secrets; provide `.env.example`.
- Do not include binaries/media in agent packs; maintain `.agentpackignore`.
