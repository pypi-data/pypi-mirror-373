# Agents Guide

This project uses a **Context Loop**. Always keep these fields current:

- **Overall goal is:** Single-sentence mission
- **Last action was:** What just completed
- **Next action will be:** The very next step
- **Blockers:** Known issues or decisions needed

### Working Rules for Agents\n- Do not modify or examine ignored directories (see `.agentpackignore`). Assume large assets exist even if excluded.\n- Prefer minimal, reversible changes.\n- After committing code, run `bpsai-pair context-sync` to update the loop.\n- Request a new context pack when the tree or docs change significantly.\n\n### Context Pack\nRun `bpsai-pair pack --out agent_pack.tgz` and upload to your session.\n
---

## Branch Discipline
- Use `--type feature|fix|refactor` when creating features.
- Conventional Commits recommended.
