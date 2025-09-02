# Agents Guide (Root Pointer)

Welcome, AI agent! This project uses PairCoder for AI pair programming.

## Where to Start

All instructions, context, and project information are maintained in the `/context` directory:

1. **Read first:** `/context/agents.md` - Complete playbook and guidelines
2. **Current state:** `/context/development.md` - Roadmap and Context Loop
3. **File structure:** `/context/project_tree.md` - Repository layout
4. **Component docs:** `/context/directory_notes/` - Directory-specific guidance

## Critical Reminder

Always check the Context Loop at the end of `/context/development.md` for:
- **Overall goal is:** The project's primary objective
- **Last action was:** What was just completed
- **Next action will be:** The immediate next step
- **Blockers/Risks:** Any issues needing attention

## After Making Changes

Update the Context Loop using:
```bash
bpsai-pair context-sync --last "What you did" --next "Next step" --blockers "Any issues"
```

Begin by reading `/context/agents.md` for complete instructions.
