# PairCoder Documentation

## Purpose and Overview

PairCoder is an AI-augmented pair programming framework that you can drop into any existing code repository to facilitate collaboration between human developers and AI coding agents (such as GPT-5, Codex, Claude, etc.). The core idea is to provide a standard structure and workflow so that AI assistants can integrate into your development process in a governed, transparent, and productive way. PairCoder introduces a set of conventions and tools for maintaining a project "memory," tracking development progress, and enforcing quality and governance standards.

### Key Features (What You Get)

**"Context as Memory"**: A structured `context/` directory holds the project's roadmap, an AI agents guide, and a snapshot of the code tree. This serves as the shared knowledge base that both developers and AI agents refer to and update, ensuring continuity in the pair-programming conversation.

**"Disciplined Loop"**: A required practice where after each action (by human or AI), the Context Sync block is updated with what happened last, what's next, and any blockers. This creates a running narrative of the project, keeping the AI aligned with recent changes and upcoming plans.

**Governance Files**: Standard open-source/project governance files are provided – `CONTRIBUTING.md` (contribution guidelines), `CODEOWNERS` (to define code reviewers/owners), `SECURITY.md` (security policy), and a Pull Request template. These ensure any AI contributions or human contributions follow the project rules and that appropriate owners review changes.

**Quality Gates**: Built-in pre-commit configuration for linting/formatting (Python uses Ruff, Markdown lint; Node uses Prettier/ESLint) and secret scanning via Gitleaks. PairCoder helps set up these tools so that any code (AI-generated or not) meets quality standards before being committed. Continuous Integration (CI) workflows are also included to run tests, linters, and refresh the context tree in an automated fashion.

**CLI Tool – bpsai-pair**: A command-line interface to orchestrate the workflow. The CLI has commands for initializing the repo scaffolding, creating new "feature" branches with context updates, packaging context for the AI, and syncing context after each change.

**Cookiecutter Template**: The package includes a Cookiecutter template (`tools/cookiecutter-paircoder`) which can scaffold a new project from scratch with PairCoder's structure. This is useful if you want to start a brand new repository already configured with PairCoder, rather than adding it to an existing one.

In summary, PairCoder's purpose is to make AI pair-programming systematic and team-friendly. Instead of ad-hoc AI suggestions, it establishes a shared memory and strict process so that AI contributions can be tracked, reviewed, and integrated like any other team member's work. This benefits any developer or team by providing a ready-to-use framework that saves time setting up project structure and ensures that if an AI agent is introduced, it operates within known guidelines.

## Installation Requirements

To use PairCoder, you need the following (these are the base requirements from the README):

- **Python 3.9+** – The CLI is a Python tool (built on Typer and Rich libraries). It should work on Python 3.9 and above.

- **Git** – PairCoder is designed to work inside a Git repository and uses Git commands (for branch management in the feature workflow).

- **Virtual Environment (Recommended)**: It's best to use a virtualenv for installing PairCoder to avoid conflicts (especially on systems with PEP 668 that restrict system Python packages).

- **Optional: Node.js** – If your project includes JavaScript/TypeScript, having Node will allow the provided CI hook (`ci_local.sh` and `ci.yml`) to run linters and tests for that code. If you don't use Node, those steps will simply be skipped (the script checks if `package.json` exists).

- **Optional: Docker** – Not directly used in v0.2.0, but noted for potential future integration tests.

- **Gitleaks Binary**: If you plan to use the secret scanning, install the gitleaks CLI tool on your machine (available via package managers or from GitHub). The pre-commit hook and documentation refer to this for scanning secrets.

### Installation Steps

Once published on PyPI, you can install PairCoder with pip. For example:

```bash
pip install bpsai-pair
```

This will install the CLI tool and its Python dependencies (Typer, Rich for colored output, PyYAML, etc. – as listed in the pyproject). After installation, the command `bpsai-pair` should be available. 

If you prefer the latest code or a development install, you can clone the repo and do:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e tools/cli  # install in editable mode from the repo
```

(as shown in the README). This editable install is mainly for contributing to PairCoder itself; normal users would use the pip release.

**Note**: If you encounter an issue where `bpsai-pair` is not found (e.g., on some systems or IDE terminals), ensure your Python scripts path is in your PATH, or invoke via python -m:

```bash
python -m bpsai_pair.cli --help
```

This is a fallback mentioned for environments where entry points might not be set up. In a proper installation, this shouldn't be necessary, but it's useful for troubleshooting.

## Using the CLI Commands

PairCoder's CLI (`bpsai-pair`) is the primary way to interact with the framework. It is a Typer-based CLI, meaning it has subcommands with `--help` available for each. Here are the main commands and how to use them:

### `bpsai-pair init <template_path>` – Initialize scaffolding

This command bootstraps a repository with PairCoder's files. You typically run this once, on an existing repository that you want to augment with AI pairing tools. It copies in all the missing pieces: context directory and files, prompt templates, scripts, config files, CI workflows, etc.

**Usage**: In the root of your repo (where `.git` is), run:
```bash
bpsai-pair init tools/cookiecutter-paircoder
```
(if using the source repo path) or simply `bpsai-pair init` (if the package provides a default template internally). The required argument is the path to the template directory; in our packaged scenario, we will have a default template packaged, so this could become optional or automatically resolved.

**What it does**: 
- It searches the given `template_dir` for a subfolder named `{{cookiecutter.project_slug}}` and copies everything under that into your repository root. 
- Files are only copied if they do not already exist to avoid overwriting. This means you can safely run init on an existing project; it won't clobber your files (it will fill in what's missing). 
- It also makes any new shell scripts executable for you. 
- After running, you will see new files like `.editorconfig`, `.pre-commit-config.yaml`, etc., appear (see Files and Directories below for full list). 
- The CLI prints a success message "Initialized repo with pair-coding scaffolding (non-destructive). Review diffs and commit." 
- At this point, you should review and commit these scaffold files into your repository.

### `bpsai-pair feature <name>` – Start a feature branch

This command creates a new Git branch (named `feature/<name>`) and prepares the context for a new phase of work. It's meant to be used whenever you begin working on a new feature or task, especially if an AI will be involved in that task. It ensures the project context is up to date and ready to guide the development.

**Usage**: Run `bpsai-pair feature <feature-name> [--primary "<Primary Goal>"] [--phase "<Phase 1 Goal>"]`. For example:
```bash
bpsai-pair feature login-system --primary "Implement login with DI seam" --phase "Phase 1: Scaffolding & tests"
```

The `<feature-name>` is a short slug for your feature (it will become part of the branch name). `--primary` is an optional description of the feature's primary goal (if not provided, the context will keep the generic placeholder or previous text), and `--phase` describes the next immediate action or phase. There is also a `--force` flag to bypass the "dirty working tree" check (useful if you have uncommitted changes and still want to branch, but generally it's better to commit or stash before running this).

**What it does**:

1. Checks you are at the repo root and that there are no uncommitted changes (unless `--force`)
2. Verifies that a main (or master) branch exists to branch off from
3. Creates a new branch `feature/<name>` off the latest main and switches to it
4. Scaffolds context files for the new feature:
   - Ensures `context/development.md` exists. If not, it creates a base roadmap file with placeholders. If it exists, it will be updated.
   - Inserts the `--primary` goal into the Primary Goal field of `development.md` (replacing the placeholder text)
   - Updates the Overall goal in the Context Sync section to match the primary goal (so the AI knows the overarching objective)
   - Ensures `context/agents.md` exists (creates a stub if not) – this file is meant to contain instructions or a playbook for AI agents; the stub reminds you to fill it in
   - Refreshes `context/project_tree.md` to the current snapshot of the repository's file structure (this gives the AI a current map of the project)
   - Appends or updates the Context Sync block in `development.md`: If one isn't there, it appends a fresh template for it; if it exists, it updates "Last action was:" to "initialized feature branch and context", and sets "Next action will be:" to the `--phase` text (if provided)
5. Stages and commits the changes to the context files on the new branch (with a commit message indicating the scaffold)

After this command completes, you have a new feature branch ready with all context files up-to-date. The Primary Goal for the feature is recorded, the Context Sync notes that the branch was initialized, and the Next action is set to the first phase/task. The CLI's output also prints what branch was created/switched and any info logs from the script. You can now proceed to actually implement the feature. The idea is that the AI agent (given the updated context) can help with the next steps.

### `bpsai-pair pack [output.tgz] [--extra <paths>]` – Package context for AI

This command creates a tarball of the important context and documentation files, which you can then provide to an AI coding assistant (e.g., upload to a chat or agent interface). This ensures the AI works with the latest project information and guidelines without exposing source code or sensitive files.

**Usage**: `bpsai-pair pack` by default will create `agent_pack.tgz` in the current directory. You can specify a custom filename: e.g., `bpsai-pair pack my_feature_context.tgz`. You can also add extra files to include with `--extra`. For instance, you might include README.md or a specific design doc: 
```bash
bpsai-pair pack --extra README.md docs/Architecture.md
```
You can list multiple `--extra` items.

**What it does**: Under the hood, this uses the tar command to archive files. By default, it always includes:
- `context/development.md` (the roadmap & latest context sync info)
- `context/agents.md` (the AI playbook/guidelines)
- `context/project_tree.md` (project structure snapshot)
- the entire `context/directory_notes/` directory (any per-directory notes you've written)

It then adds any `--extra` paths you provided to that list. Before creating the tar, it checks that all those paths actually exist – so you'll get an error if, for example, you typo'd a filename.

The packing process also respects an ignore list for safety: there is a file `.agentpackignore` which functions like a `.gitignore` for packaging. Common large or sensitive patterns (like `.git/**`, `node_modules/`, `dist/`, `__pycache__/`, etc.) are excluded automatically. You can customize `.agentpackignore` to exclude or include other patterns as needed. The tarball will thus contain only the files we want the AI to see. The script prints out what it's doing – e.g., "Packing -> agent_pack.tgz" and confirms creation with the file size.

After running this, you'll have an archive file. How to use it? This archive can be provided to the AI agent. For example, if using an UX with file upload, you'd attach the `agent_pack.tgz`. The AI can open it and read all the context files to understand the project's state before contributing code. 

**Note**: The agent pack deliberately omits source code (unless you add some in extras), focusing on context and docs. This encourages the AI to generate code without directly copying existing code, and avoids sending potentially sensitive code unnecessarily. If the AI needs to see a particular source file, you can always add it with `--extra` or share it separately.

### `bpsai-pair context-sync` – Update Context Sync

This command updates the Context Sync section of `context/development.md` programmatically. It's a convenience to ensure that whenever you or the AI complete a step, the shared context log is updated consistently without manual editing errors.

**Usage**: Provide at least the `--last` and `--nxt` arguments:
```bash
bpsai-pair context-sync --last "Fixed bug in login flow" \
                        --nxt "Code review and merge" \
                        --blockers "None"
```

The `--blockers` can be an empty string if no blockers (it defaults to empty). You can also use `--overall` if, say, the overall goal of the project has shifted and you want to change the top-line context (this is less common on a per-action basis).

**What it does**: This command simply finds the lines in `context/development.md` that start with "Last action was:", "Next action will be:", etc., and replaces them with your provided text. It requires that `context/development.md` already exists and contains those expected lines; otherwise it errors out (to ensure you don't accidentally run it in a non-PairCoder repo). Each time you run it, it effectively logs the latest state:
- "Last action was: …" gets the `--last` text
- "Next action will be: …" gets the `--nxt` text
- "Blockers/Risks: …" gets the `--blockers` text (or is left empty if none provided)
- If `--overall` is given, it will also update "Overall goal is: …" at the top of the block (you might use this if you complete a major feature and want to set a new overall project objective)

This command prints a confirmation like "Context Sync updated." in green, and you can open the `development.md` to see the changes. The idea is that both humans and AI agents use this regularly: after every meaningful code change, run context-sync (or have the AI run it) to log progress. This keeps everyone on the same page about what just happened and what's next, preventing the AI from repeating work or the humans from forgetting context the AI had.

In practice, you might integrate this into your workflow: e.g., as part of a script that the AI runs, or manually as a discipline (the README stresses this as a "required discipline" for using PairCoder effectively). It ensures continuity in pair programming sessions.

Each of these CLI commands has a help screen (try `bpsai-pair <command> --help`) which will summarize usage and options, thanks to Typer. For instance, `bpsai-pair --help` will list all commands, and `bpsai-pair feature --help` will show the options like `--primary` and `--phase`. Using these commands in the intended order (init → feature → pack → context-sync, and repeating feature/pack/sync as needed) creates a development loop where the AI is always operating with up-to-date project context.

## Files and Directory Structure Explained

When PairCoder is initialized in a repo (via init or by starting a new project with the cookiecutter), it adds a number of files and directories. Here we describe the purpose of each and how you, as a user, interact with them. The repository layout is summarized in the documentation, but here we expand on each item:

### `context/` – Project Context and Memory

This folder is central to PairCoder. It contains:

**`development.md`** – The "Development Roadmap" Markdown file. This is essentially the journal of the project's progress and plans. It typically starts with a Primary Goal of the project, the project name, owner, last updated date, etc., followed by the Context Sync section. You should treat this as the single source of truth for "what are we doing and why" in the project. At project start, you fill in the Primary Goal (either manually or via the `--primary` flag during feature command). As development proceeds, every time something changes, update the Context Sync (preferably via the CLI). Think of it as a constantly evolving README focused on dynamic progress. This file is also packaged and given to the AI, so it's how the AI knows the overall context and recent history. It's a living document; keep it updated for the best results.

**`project_tree.md`** – A snapshot of the repository's directory tree structure. This is auto-generated (via the feature command or a daily CI job) and is not meant to be edited by hand. It shows all files and folders (excluding certain ignored patterns) in a tree format, which gives the AI a bird's-eye view of the project's scope. The top of the file includes a timestamp of when it was generated. The CI workflow will update this daily to catch any new files committed outside the feature scaffolding. As a user, you don't edit this; you only ensure the CI is running or run `bpsai-pair feature` again to refresh it if needed.

**`agents.md`** – The "Agents Guide / AI Pair Coding Playbook." This is initially a stub file with a note telling you to fill in the canonical version. The intention is that you provide instructions here for AI agents working on your code. For example, you might include coding style guidelines, architectural principles, definitions of done, or any rules the AI should follow (like "don't touch files in /core without approval" or "use Python style X for logging"). Essentially, this is a place to encode your team's best practices and any specific domain knowledge the AI needs. Before you begin using an AI agent, you should replace the stub with a well-thought guide. Once written, this file is always included in context packages, so the AI will refer to it whenever it's working on tasks.

**`directory_notes/`** – A directory intended to hold Markdown notes for individual directories or components in your repo. It starts with just a `.gitkeep` (an empty file to ensure the folder exists). PairCoder provides a template for directory notes (`templates/directory_note.md`) which you can copy into this folder for any submodule or directory that might need explanation. For instance, if you have a `backend/` directory, you could create `context/directory_notes/backend.md` describing what's in there, important design choices, etc. These notes can then be kept up to date and will be packaged for the AI. They help the AI (and new developers) understand each part of the codebase in context. Maintaining these notes is optional but recommended for complex projects.

(For optional usage: context could also include an `architecture.md` or other overview docs if you want to place them here. PairCoder doesn't generate those by default beyond what's mentioned.)

### `prompts/` – AI Prompt Templates

This directory contains YAML files that define the base prompts or instructions for various phases of the AI's involvement:

- **`roadmap.yml`** – Contains a template for prompting the AI to assist in roadmap generation from a proposed plan. It outlines how to ask the AI to break down the Primary Goal into phases or tasks (the "Roadmap" phase of pair programming) and to generate the necessary `/context/development.md` & `/context/agents.md` files based on the accepted plan.

- **`deep_research.yml`** – A template for a "deep research" phase prompt. This template is used when you want the AI to do a deep dive (analyzing a repo, summarizing info, answering complex questions).

- **`implementation.yml`** – A template prompt for coding or implementing features, guiding the AI on how to produce code within the project's context and constraints.

These files come with the framework but are not actively modified by the CLI. They are assets you or the AI agent integration can use. For instance, if you have a script or UI that interacts with an AI model, it might load these prompts to formulate its queries. You can customize them as needed for your project's tone or specificity. By shipping these, PairCoder ensures that all team members and AI agents start with a consistent approach to asking the AI for help at different stages (planning vs. researching vs. coding). As a user, you should review these prompt templates and adjust any placeholders or project-specific info before using them heavily.


### Governance & Config Files (repo root)

- **`CONTRIBUTING.md`** – Guidelines for contributors. PairCoder provides a template that includes instructions to use Conventional Commits for commit messages, to always update context sync, keep diffs small, etc. You should read this and update any project-specific sections (like how to get started, or the PR process if different). Share this with human contributors and parse the relevant pieces into the AI's guidelines so it follows the contributing rules.

- **`SECURITY.md`** – Security policy, e.g., how to report vulnerabilities, and a reminder not to include secrets in the repo or context packs. The one included with PairCoder also notes that `.agentpackignore` is set up to avoid packing secrets and that test data should be redacted or synthetic. This file is mainly informational for your repo's users; it's good for both internal use and to provide the agent guidance on your team's security best practices.

- **`CODEOWNERS`** – A file that GitHub uses to auto-assign reviewers. This file should list the repository owners or lead developers who should review incoming PRs. You should edit this to match your team's GitHub usernames and desired code ownership (e.g., you might want all AI-generated PRs to ping a certain lead). This helps enforce that a human reviews any AI contributions.

- **`.editorconfig`** – Standard EditorConfig file to ensure consistent indentation, charset, end-of-line, etc., across different editors. It's a generic one suitable for most projects. With this in place, developers' IDEs will follow the same basic formatting rules, reducing diffs caused by whitespace.

- **`.pre-commit-config.yaml`** – Configuration for pre-commit hooks. PairCoder's config will set up hooks such as:
  - Ruff (Python linter/formatter) to run on Python files
  - Prettier for formatting Markdown, JSON, YAML, etc.
  - Markdownlint for Markdown files
  - A hook to call Gitleaks 
  
  You should run `pre-commit install` after initializing PairCoder to activate these hooks in your local repo. Then, every commit will trigger them. If the AI introduces code that doesn't pass these, the commit will be blocked until fixed (or you skip the hook). This is excellent for maintaining quality.

- **`.gitleaks.toml`** – Configuration for Gitleaks (secret scanner). It contains patterns to detect API keys, credentials, etc., and also a list of allowed patterns or false-positive suppressions. The one provided by PairCoder covers common file paths to ignore (like it doesn't scan `context/` or tests for certain dummy secrets). Keep this updated if you find false positives or need to add custom regexes for your stack. Use it by running `gitleaks detect ...` as per README or let it run in CI.

- **`.agentpackignore`** – As discussed, this file lists what to exclude from the context tarball. By default, it covers `.git/`, build artifacts, virtualenvs, caches, etc. You can add anything else you never want to send to the AI (for example, you might exclude `**/secrets.env`).

- **`.gitignore`** – The template provides a baseline `.gitignore` (covering Python, Node, etc.). Check it to ensure it doesn't conflict with your project's needs. This prevents committing of venvs, node_modules, pyc files, etc.

### CI Workflows (`.github/workflows/`)

- **`ci.yml`** – A GitHub Actions workflow that runs on each push/PR. It will set up appropriate environments and run formatting, linting, typing, and tests for both Node and Python portions of the repo. Ensure your repository has any required test commands or configuration so this passes. As you develop, maintain your CI to cover your real test suites.

- **`project_tree.yml`** – A scheduled workflow that executes a small script to regenerate `context/project_tree.md` and commit it if it has changed. This is a "maintenance" workflow to keep the context tree updated without manual intervention. It uses a bot account or GitHub Actions token to push the update. You may need to set the proper permissions (repo write) for this Action. Check that this workflow's schedule (cron) is acceptable (daily might be default). If your repo is private, ensure actions are enabled. This automation ensures that even if no one ran `bpsai-pair feature` recently, your context tree doesn't fall far behind the actual repo structure.

### Templates (`templates/` directory in repo root)

- **`adr.md`** – A template for an Architecture Decision Record. The repository includes an example ADR template. You can use this to document any big decisions. ADRs are typically stored in `docs/adr/` (notice the template created a `docs/adr/` folder with a `.gitkeep`). When a significant design choice is made (perhaps with AI input), you write an ADR using this template, assign it a number (e.g., ADR-001), and commit it. This helps future contributors (and AI agents) understand why certain decisions were made. PairCoder doesn't automate ADR creation, but by providing the template and directory, it encourages this best practice.

- **`directory_note.md`** – A template for writing a directory note (similar to what would go in `context/directory_notes/`). It's a short template likely just providing a structure (maybe headers for "Purpose of this directory/module," etc.). Use it whenever you want to add documentation for a specific part of the codebase.

These templates are for your convenience; the CLI doesn't directly use them (except that `new_feature.sh` will copy `directory_note.md` if needed when scaffolding directory notes, which currently it doesn't automatically for each folder – it just ensures the folder exists). It's up to you to create actual notes or ADR files based on them.

### Tests (`tests/` directory)

The scaffold includes a `tests/` folder with subfolders like `example_contract` and `example_integration`, each containing a README. These are placeholders indicating to the coding agent where and how to write tests:
- Example contract tests refer to Consumer Pact tests
- Example integration tests for external boundaries

**NOTE**: The nested READMEs are stubs and are not functional code. They serve as a placeholder for your team. You should replace or revise these once you add real tests. For example, if choosing to keep and revise them, they may be incorporated to signal to the AI where tests go and what frameworks to use, etc.

### `services/` and `infra/` directories

These are present as empty folders with `.gitkeep`. They indicate where you might put microservice code or infrastructure-as-code (Terraform, etc.), depending on your project. They're not used by PairCoder's logic directly, but they're part of the scaffold to nudge a clean project structure. If used, their purpose should be included in your `context/agents.md` file to allow efficient crawling.

### Cookiecutter Config (`tools/cookiecutter-paircoder/`)

While not part of the project itself once you've initialized, it's worth noting that PairCoder was developed with a Cookiecutter template. The `cookiecutter.json` file in that directory defines variables like `project_name`, `project_slug`, etc., which are used in the scaffold files. If you start a new project using Cookiecutter (rather than using init on an existing repo), those variables will be substituted. For example, `<PROJECT NAME>` in `development.md` would be replaced with your actual project name. 

When you run `bpsai-pair init` on an existing repo, it doesn't do string substitution (it just copies files with the placeholders as-is, then feature command stamps the Primary Goal). In the future (v0.2.x on the roadmap), there are plans to integrate template variable substitution into init so that it can ask for your project name and fill it in automatically. For now, just be aware of the placeholders and update them manually (e.g., replace `<PROJECT NAME>` in `development.md` with your repo name after init).

## How to Use PairCoder Day-to-Day

With everything set up, here's how a developer might employ PairCoder in their workflow:

### 1. Initialize (one-time)
Add PairCoder to your repo by running `bpsai-pair init`. Commit the introduced files. Configure CODEOWNERS and other files to your liking. Set up pre-commit hooks (`pre-commit install`) and ensure CI is enabled. Fill in `context/agents.md` with any special instructions for AI. At this point, your project is "PairCoder-enabled."

### 2. Planning & Roadmap
Use `context/development.md` to outline your high-level roadmap. Possibly break it into phases. The `prompts/roadmap.yml` can be used with an AI (e.g., ask the AI "Using the roadmap prompt, help me plan the phases for achieving the Primary Goal"). This can yield a structured plan that you then place into `development.md` (under the Primary Goal section or below). Essentially, `development.md` can hold more detail than just the Context Sync; it's your space to plan. Keep it updated as plans change.

### 3. Starting a Feature (with AI or without)
When ready to tackle a piece of work, run `bpsai-pair feature <name> ...`. This creates a feature branch and updates the context. Push this branch to your remote (so others know you're working on it). At this point, you might engage an AI: you package the context (`bpsai-pair pack`) and send it to the AI with a prompt (perhaps using `prompts/implementation.yml`) like "Here's the current project context, please implement feature X following the guidelines." The AI will produce code changes.

### 4. AI Contributions & Context Loop
If the AI suggests code, you would apply those changes in your repo (maybe via a patch file or manually). After any significant change (AI or human), run:
```bash
bpsai-pair context-sync --last "described last change" --nxt "what's next" --blockers "any issues"
```
to log progress. Commit this change to `development.md`. This way, the next time you or the AI looks at context, it sees what was just done.

You might also update `context/agents.md` if, for example, you realize the AI needs new instructions ("don't use library X" or "prefer Y approach") based on what it did.

### 5. Testing & Quality
Run `pre-commit run --all-files` to ensure the code meets standards. Fix any lint errors or formatting issues (the AI might not adhere to all style guidelines perfectly, so this is where you correct it, or include style guidance in `context/agents.md` for next time). Write tests for the new feature if the AI didn't. This is normal dev work, just within the PairCoder framework.

### 6. Integrate & Repeat
Once the feature is done, you create a PR (the PR template provided will remind the contributor to ensure context is updated, tests are added, etc.). Codeowners or team leads review it just like a normal PR. Merge it to main. The context (`development.md`) now contains a historical log of that feature's development. If a new cycle starts, you again use `bpsai-pair feature` for the next task.

### 7. Maintenance
The daily `project_tree.yml` job will keep updating the project tree snapshot. You should also occasionally refine `agents.md` as the AI's role evolves, and keep governance docs up to date (for example, if you adopt a new coding standard, note it in `CONTRIBUTING.md` and possibly in `agents.md` for the AI). Use ADRs to record big decisions that the AI might not be aware of inherently.

### 8. Extensibility
If desired, you can integrate PairCoder with other tools. The README mentions plans for separate repos like `paircoder-ui`, a project management tool with a UI for enhanced UX when interacting with the AI. The CLI could be called from such similar integrations (and a future version plans to expose a Python API for the CLI commands). For now, you primarily interact via CLI.

By following this workflow, any developer on the team (and the AI "developer") has a shared understanding of the project's state and next steps. PairCoder essentially provides the scaffolding and guardrails, but it's up to the team to use them consistently. The benefit is a more structured and trackable collaboration with AI, reducing the chaos and improving transparency.

## Conclusion

PairCoder is suitable for any development team looking to incorporate AI assistance into their coding process in a controlled, auditable way. Its combination of a CLI tool and repository scaffolding makes it a comprehensive drop-in framework for AI pair programming. It treats many aspects (context sharing, branch discipline, quality checks, documentation) holistically. Once set up, you can focus on building features – with an AI – while PairCoder quietly maintains the order (updating the context, enforcing rules, etc.).

Always remember that the value of PairCoder grows when the context is well-maintained and practices are followed. The more you document in `development.md`, `agents.md`, and directory notes, the more the AI can help effectively. The more you adhere to updating the Context Sync and using the provided tools, the smoother the collaboration. It's a two-way street: PairCoder provides the tools, and the team (human + AI) uses them to create a virtuous cycle of improvement.

## Windows Support
From v2.0, PairCoder is OS-agnostic. All features are supported equally on Linux, macOS, and Windows.
