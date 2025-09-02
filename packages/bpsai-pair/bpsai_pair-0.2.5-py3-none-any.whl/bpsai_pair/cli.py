"""
Enhanced bpsai-pair CLI with cross-platform support and improved UX.
"""
from __future__ import annotations

import os
import json
import sys
import subprocess
from pathlib import Path
from typing import List, Optional
from datetime import datetime

import typer
from rich import print
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Try relative imports first, fall back to absolute
try:
    from . import __version__
    from . import init_bundled_cli
    from . import ops
    from .config import Config
except ImportError:
    # For development/testing when running as script
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from bpsai_pair import __version__
    from bpsai_pair import init_bundled_cli
    from bpsai_pair import ops
    from bpsai_pair.config import Config

# Initialize Rich console
console = Console()

# Environment variable support
MAIN_BRANCH = os.getenv("PAIRCODER_MAIN_BRANCH", "main")
CONTEXT_DIR = os.getenv("PAIRCODER_CONTEXT_DIR", "context")

app = typer.Typer(
    add_completion=False,
    help="bpsai-pair: AI pair-coding workflow CLI",
    context_settings={"help_option_names": ["-h", "--help"]}
)


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        console.print(f"[bold blue]bpsai-pair[/bold blue] version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        callback=version_callback,
        help="Show version and exit"
    )
):
    """bpsai-pair: AI pair-coding workflow CLI"""
    pass


def repo_root() -> Path:
    """Get repo root with better error message."""
    p = Path.cwd()
    if not ops.GitOps.is_repo(p):
        console.print(
            "[red]✗ Not in a git repository.[/red]\n"
            "Please run from your project root directory (where .git exists).\n"
            "[dim]Hint: cd to your project directory first[/dim]"
        )
        raise typer.Exit(1)
    return p


@app.command()
def init(
    template: Optional[str] = typer.Argument(
        None, help="Path to template (optional, uses bundled template if not provided)"
    ),
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Interactive mode to gather project info"
    )
):
    """Initialize repo with governance, context, prompts, scripts, and workflows."""
    root = repo_root()

    if interactive:
        # Interactive mode to gather project information
        project_name = typer.prompt("Project name", default="My Project")
        primary_goal = typer.prompt("Primary goal", default="Build awesome software")
        coverage = typer.prompt("Coverage target (%)", default="80")

        # Create a config file
        config = Config(
            project_name=project_name,
            primary_goal=primary_goal,
            coverage_target=int(coverage)
        )
        config.save(root)

    # Use bundled template if none provided
    if template is None:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Initializing scaffolding...", total=None)
            result = init_bundled_cli.main()
            progress.update(task, completed=True)

        console.print("[green]✓[/green] Initialized repo with pair-coding scaffolding")
        console.print("[dim]Review diffs and commit changes[/dim]")
    else:
        # Use provided template (simplified for now)
        console.print(f"[yellow]Using template: {template}[/yellow]")


@app.command()
def feature(
    name: str = typer.Argument(..., help="Feature branch name (without prefix)"),
    primary: str = typer.Option("", "--primary", "-p", help="Primary goal to stamp into context"),
    phase: str = typer.Option("", "--phase", help="Phase goal for Next action"),
    force: bool = typer.Option(False, "--force", "-f", help="Bypass dirty-tree check"),
    type: str = typer.Option(
        "feature",
        "--type",
        "-t",
        help="Branch type: feature|fix|refactor",
        case_sensitive=False,
    ),
):
    """Create feature branch and scaffold context (cross-platform)."""
    root = repo_root()

    # Validate branch type
    branch_type = type.lower()
    if branch_type not in {"feature", "fix", "refactor"}:
        console.print(
            f"[red]✗ Invalid branch type: {type}[/red]\n"
            "Must be one of: feature, fix, refactor"
        )
        raise typer.Exit(1)

    # Use Python ops instead of shell script
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"Creating {branch_type}/{name}...", total=None)

        try:
            ops.FeatureOps.create_feature(
                root=root,
                name=name,
                branch_type=branch_type,
                primary_goal=primary,
                phase=phase,
                force=force
            )
            progress.update(task, completed=True)

            console.print(f"[green]✓[/green] Created branch [bold]{branch_type}/{name}[/bold]")
            console.print(f"[green]✓[/green] Updated context with primary goal and phase")
            console.print("[dim]Next: Connect your agent and share /context files[/dim]")

        except ValueError as e:
            progress.update(task, completed=True)
            console.print(f"[red]✗ {e}[/red]")
            raise typer.Exit(1)


@app.command()
def pack(
    output: str = typer.Option("agent_pack.tgz", "--out", "-o", help="Output archive name"),
    extra: Optional[List[str]] = typer.Option(None, "--extra", "-e", help="Additional paths to include"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview files without creating archive"),
    list_only: bool = typer.Option(False, "--list", "-l", help="List files to be included"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Create agent context package (cross-platform)."""
    root = repo_root()
    output_path = root / output

    # Use Python ops for packing
    files = ops.ContextPacker.pack(
        root=root,
        output=output_path,
        extra_files=extra,
        dry_run=(dry_run or list_only)
    )

    if json_out:
        result = {
            "files": [str(f.relative_to(root)) for f in files],
            "count": len(files),
            "dry_run": dry_run,
            "list_only": list_only
        }
        if not (dry_run or list_only):
            result["output"] = str(output)
            result["size"] = output_path.stat().st_size if output_path.exists() else 0
        print(json.dumps(result, indent=2))
    elif list_only:
        for f in files:
            console.print(str(f.relative_to(root)))
    elif dry_run:
        console.print(f"[yellow]Would pack {len(files)} files:[/yellow]")
        for f in files[:10]:  # Show first 10
            console.print(f"  • {f.relative_to(root)}")
        if len(files) > 10:
            console.print(f"  [dim]... and {len(files) - 10} more[/dim]")
    else:
        console.print(f"[green]✓[/green] Created [bold]{output}[/bold]")
        size_kb = output_path.stat().st_size / 1024
        console.print(f"  Size: {size_kb:.1f} KB")
        console.print(f"  Files: {len(files)}")
        console.print("[dim]Upload this archive to your agent session[/dim]")


@app.command("context-sync")
def context_sync(
    overall: Optional[str] = typer.Option(None, "--overall", help="Overall goal override"),
    last: str = typer.Option(..., "--last", "-l", help="What changed and why"),
    next: str = typer.Option(..., "--next", "--nxt", "-n", help="Next smallest valuable step"),
    blockers: str = typer.Option("", "--blockers", "-b", help="Blockers/Risks"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Update the Context Loop in /context/development.md."""
    root = repo_root()
    context_dir = root / CONTEXT_DIR
    dev_file = context_dir / "development.md"

    if not dev_file.exists():
        console.print(
            f"[red]✗ {dev_file} not found[/red]\n"
            "Run 'bpsai-pair init' first to set up the project structure"
        )
        raise typer.Exit(1)

    # Update context
    content = dev_file.read_text()
    import re

    if overall:
        content = re.sub(r'Overall goal is:.*', f'Overall goal is: {overall}', content)
    content = re.sub(r'Last action was:.*', f'Last action was: {last}', content)
    content = re.sub(r'Next action will be:.*', f'Next action will be: {next}', content)
    if blockers:
        content = re.sub(r'Blockers(/Risks)?:.*', f'Blockers/Risks: {blockers}', content)

    dev_file.write_text(content)

    if json_out:
        result = {
            "updated": True,
            "file": str(dev_file.relative_to(root)),
            "context": {
                "overall": overall,
                "last": last,
                "next": next,
                "blockers": blockers
            }
        }
        print(json.dumps(result, indent=2))
    else:
        console.print("[green]✓[/green] Context Sync updated")
        console.print(f"  [dim]Last: {last}[/dim]")
        console.print(f"  [dim]Next: {next}[/dim]")


# Alias for context-sync
app.command("sync", hidden=True)(context_sync)


@app.command()
def status(
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Show current context loop status and recent changes."""
    root = repo_root()
    context_dir = root / CONTEXT_DIR
    dev_file = context_dir / "development.md"

    # Get current branch
    current_branch = ops.GitOps.current_branch(root)
    is_clean = ops.GitOps.is_clean(root)

    # Parse context sync
    context_data = {}
    if dev_file.exists():
        content = dev_file.read_text()
        import re

        # Extract context sync fields
        overall_match = re.search(r'Overall goal is:\s*(.*)', content)
        last_match = re.search(r'Last action was:\s*(.*)', content)
        next_match = re.search(r'Next action will be:\s*(.*)', content)
        blockers_match = re.search(r'Blockers(/Risks)?:\s*(.*)', content)
        phase_match = re.search(r'\*\*Phase:\*\*\s*(.*)', content)

        context_data = {
            "phase": phase_match.group(1) if phase_match else "Not set",
            "overall": overall_match.group(1) if overall_match else "Not set",
            "last": last_match.group(1) if last_match else "Not set",
            "next": next_match.group(1) if next_match else "Not set",
            "blockers": blockers_match.group(2) if blockers_match else "None"
        }

    # Check for recent pack
    pack_files = list(root.glob("*.tgz"))
    latest_pack = None
    if pack_files:
        latest_pack = max(pack_files, key=lambda p: p.stat().st_mtime)

    if json_out:
        age_hours = None
        if latest_pack:
            age_hours = (datetime.now() - datetime.fromtimestamp(latest_pack.stat().st_mtime)).total_seconds() / 3600

        result = {
            "branch": current_branch,
            "clean": is_clean,
            "context": context_data,
            "latest_pack": str(latest_pack.name) if latest_pack else None,
            "pack_age": age_hours
        }
        print(json.dumps(result, indent=2))
    else:
        # Create a nice table
        table = Table(title="PairCoder Status", show_header=False)
        table.add_column("Field", style="cyan", width=20)
        table.add_column("Value", style="white")

        # Git status
        table.add_row("Branch", f"[bold]{current_branch}[/bold]")
        table.add_row("Working Tree", "[green]Clean[/green]" if is_clean else "[yellow]Modified[/yellow]")

        # Context status
        if context_data:
            table.add_row("Phase", context_data["phase"])
            table.add_row("Overall Goal", context_data["overall"][:60] + "..." if len(context_data["overall"]) > 60 else context_data["overall"])
            table.add_row("Last Action", context_data["last"][:60] + "..." if len(context_data["last"]) > 60 else context_data["last"])
            table.add_row("Next Action", context_data["next"][:60] + "..." if len(context_data["next"]) > 60 else context_data["next"])
            if context_data["blockers"] and context_data["blockers"] != "None":
                table.add_row("Blockers", f"[red]{context_data['blockers']}[/red]")

        # Pack status
        if latest_pack:
            age_hours = (datetime.now() - datetime.fromtimestamp(latest_pack.stat().st_mtime)).total_seconds() / 3600
            age_str = f"{age_hours:.1f} hours ago" if age_hours < 24 else f"{age_hours/24:.1f} days ago"
            table.add_row("Latest Pack", f"{latest_pack.name} ({age_str})")

        console.print(table)

        # Suggestions
        if not is_clean:
            console.print("\n[yellow]⚠ Working tree has uncommitted changes[/yellow]")
            console.print("[dim]Consider committing or stashing before creating a pack[/dim]")

        if not latest_pack or (latest_pack and age_hours and age_hours > 24):
            console.print("\n[dim]Tip: Run 'bpsai-pair pack' to create a fresh context pack[/dim]")


@app.command()
def validate(
    fix: bool = typer.Option(False, "--fix", help="Attempt to fix issues"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Validate repo structure and context consistency."""
    root = repo_root()
    issues = []
    fixes = []

    # Check required files
    required_files = [
        Path(CONTEXT_DIR) / "development.md",
        Path(CONTEXT_DIR) / "agents.md",
        Path(".agentpackignore"),
        Path(".editorconfig"),
        Path("CONTRIBUTING.md"),
    ]

    for file_path in required_files:
        full_path = root / file_path
        if not full_path.exists():
            issues.append(f"Missing required file: {file_path}")
            if fix:
                # Create with minimal content
                full_path.parent.mkdir(parents=True, exist_ok=True)
                if file_path.name == "development.md":
                    full_path.write_text("# Development Log\n\n## Context Sync (AUTO-UPDATED)\n")
                elif file_path.name == "agents.md":
                    full_path.write_text("# Agents Guide\n")
                elif file_path.name == ".agentpackignore":
                    full_path.write_text(".git/\n.venv/\n__pycache__/\nnode_modules/\n")
                else:
                    full_path.touch()
                fixes.append(f"Created {file_path}")

    # Check context sync format
    dev_file = root / CONTEXT_DIR / "development.md"
    if dev_file.exists():
        content = dev_file.read_text()
        required_sections = [
            "Overall goal is:",
            "Last action was:",
            "Next action will be:",
        ]
        for section in required_sections:
            if section not in content:
                issues.append(f"Missing context sync section: {section}")
                if fix:
                    content += f"\n{section} (to be updated)\n"
                    dev_file.write_text(content)
                    fixes.append(f"Added section: {section}")

    # Check for uncommitted context changes
    if not ops.GitOps.is_clean(root):
        context_files = ["context/development.md", "context/agents.md"]
        for cf in context_files:
            result = subprocess.run(
                ["git", "diff", "--name-only", cf],
                cwd=root,
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                issues.append(f"Uncommitted changes in {cf}")

    if json_out:
        result = {
            "valid": len(issues) == 0,
            "issues": issues,
            "fixes_applied": fixes if fix else []
        }
        print(json.dumps(result, indent=2))
    else:
        if issues:
            console.print("[red]✗ Validation failed[/red]")
            console.print("\nIssues found:")
            for issue in issues:
                console.print(f"  • {issue}")

            if fixes:
                console.print("\n[green]Fixed:[/green]")
                for fix_msg in fixes:
                    console.print(f"  ✓ {fix_msg}")
            elif not fix:
                console.print("\n[dim]Run with --fix to attempt automatic fixes[/dim]")
        else:
            console.print("[green]✓ All validation checks passed[/green]")


@app.command()
def ci(
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Run local CI checks (cross-platform)."""
    root = repo_root()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Running CI checks...", total=None)

        results = ops.LocalCI.run_all(root)

        progress.update(task, completed=True)

    if json_out:
        print(json.dumps(results, indent=2))
    else:
        console.print("[bold]Local CI Results[/bold]\n")

        # Python results
        if results["python"]:
            console.print("[cyan]Python:[/cyan]")
            for check, status in results["python"].items():
                icon = "✓" if "passed" in status else "✗"
                color = "green" if "passed" in status else "yellow"
                console.print(f"  [{color}]{icon}[/{color}] {check}: {status}")

        # Node results
        if results["node"]:
            console.print("\n[cyan]Node.js:[/cyan]")
            for check, status in results["node"].items():
                icon = "✓" if "passed" in status else "✗"
                color = "green" if "passed" in status else "yellow"
                console.print(f"  [{color}]{icon}[/{color}] {check}: {status}")

        if not results["python"] and not results["node"]:
            console.print("[dim]No Python or Node.js project detected[/dim]")


# Export for entry point
def run():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    run()
