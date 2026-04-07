"""
GitShield — Command Line Interface
====================================
Professional CLI tool with rich terminal output.

Commands:
    gitshield scan          Security scan current directory
    gitshield check         Pre-commit analysis
    gitshield check-msg     Analyze commit message from stdin
    gitshield health        Repository health report
    gitshield fix           Interactive mistake recovery
    gitshield init          Install git hooks + setup
    gitshield uninstall     Remove git hooks
    gitshield gitignore     Generate/update .gitignore
    gitshield guide <topic> Get guidance on git topics
    gitshield stats         Developer behavior stats
    gitshield doctor        Full diagnostic
"""

import sys
import os

# Fix Windows terminal encoding for unicode/emoji output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich import box

from devflow import __version__, BANNER
from devflow.scanner import scan_directory, get_scan_summary, Severity
from devflow.rules import run_all_rules, has_blocking_issues, RuleSeverity
from devflow.git_analyzer import (
    is_git_repo, get_current_branch, get_staged_files,
    get_modified_files, get_untracked_files, get_full_status,
    get_commit_message, get_last_n_commits,
)
from devflow.mentor import explain_warning, get_mentor_advice, get_progressive_tip
from devflow.memory import update_memory, get_statistics, get_behavior_insights, record_scan
from devflow.ai_engine import generate_ai_suggestion, generate_detailed_analysis
from devflow.recovery import get_recovery_options, execute_recovery
from devflow.health import calculate_health, get_repo_stats
from devflow.gitignore_gen import (
    detect_project_types, generate_gitignore, get_missing_patterns,
    get_tracked_but_should_ignore, write_gitignore,
)
from devflow.github_assistant import get_guide, get_available_topics
from devflow.hooks_manager import install_hooks, uninstall_hooks, get_hook_status
import io

# Create a Console that works with Unicode on Windows
if sys.platform == "win32":
    _out = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    console = Console(file=_out, force_terminal=True)
else:
    console = Console()


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="GitShield")
@click.pass_context
def main(ctx):
    """🛡️ GitShield — AI-powered Git Guardian & Developer Intelligence System"""
    if ctx.invoked_subcommand is None:
        console.print(BANNER, style="bold cyan")
        console.print(Panel(
            "[bold]Available Commands:[/bold]\n\n"
            "  [cyan]scan[/]        Security scan for secrets & sensitive files\n"
            "  [cyan]check[/]       Pre-commit analysis (commit msg + staged files)\n"
            "  [cyan]health[/]      Repository health report with score\n"
            "  [cyan]fix[/]         Interactive mistake recovery wizard\n"
            "  [cyan]init[/]        Install GitShield git hooks\n"
            "  [cyan]gitignore[/]   Generate smart .gitignore\n"
            "  [cyan]guide[/]       Git workflow guidance\n"
            "  [cyan]stats[/]       Developer behavior statistics\n"
            "  [cyan]doctor[/]      Full system diagnostic\n"
            "\n[dim]Run 'gitshield <command> --help' for details[/dim]",
            title="🛡️ GitShield",
            border_style="cyan",
        ))


# ═══════════════════════════════════════════════════════════════
# SCAN COMMAND
# ═══════════════════════════════════════════════════════════════
@main.command()
@click.argument("path", default=".")
@click.option("--strict", is_flag=True, help="Exit with error on any finding")
@click.option("--staged", is_flag=True, help="Only scan staged files")
def scan(path, strict, staged):
    """🔒 Scan for secrets, API keys, and sensitive files."""
    console.print("\n🔒 [bold]GitShield Security Scanner[/bold]\n", style="cyan")

    findings = scan_directory(path, staged_only=staged)
    record_scan(len(findings))

    if not findings:
        console.print(Panel(
            "✅ [bold green]No security issues found![/bold green]\n\n"
            "Your code is clean of secrets and sensitive files.",
            border_style="green", title="Scan Complete",
        ))
        sys.exit(0)

    summary = get_scan_summary(findings)

    # Display findings
    table = Table(title="Security Findings", box=box.ROUNDED, border_style="red")
    table.add_column("Severity", style="bold", width=10)
    table.add_column("File", style="cyan")
    table.add_column("Issue", style="white")
    table.add_column("Line", justify="right", width=6)

    for f in findings:
        sev_style = {
            Severity.CRITICAL: "bold red",
            Severity.HIGH: "bold yellow",
            Severity.MEDIUM: "yellow",
            Severity.LOW: "blue",
        }.get(f.severity, "white")
        line = str(f.line_number) if f.line_number else "-"
        table.add_row(
            f"{f.severity.icon} {f.severity.value}",
            os.path.basename(f.file),
            f.message,
            line,
        )

    console.print(table)

    # Summary
    console.print(f"\n[bold]Summary:[/bold] "
                  f"🔴 {summary['critical']} Critical  "
                  f"🟠 {summary['high']} High  "
                  f"🟡 {summary['medium']} Medium  "
                  f"🔵 {summary['low']} Low\n")

    if summary["critical"] > 0:
        console.print("[bold red]🚨 CRITICAL secrets detected! Remove immediately![/bold red]\n")

    # Show suggestions for top findings
    for f in findings[:3]:
        if f.suggestion:
            console.print(f"  💡 {f.pattern_name}: [dim]{f.suggestion}[/dim]")

    if strict or summary["critical"] > 0:
        sys.exit(1)
    sys.exit(0)


# ═══════════════════════════════════════════════════════════════
# CHECK COMMAND
# ═══════════════════════════════════════════════════════════════
@main.command()
@click.option("--hook", is_flag=True, help="Running as git hook (affects exit code)")
def check(hook):
    """📋 Pre-commit analysis — check commit quality before committing."""
    # Gather context
    branch = get_current_branch()
    staged = get_staged_files()
    commit_msg = get_commit_message()

    if not hook:
        console.print("\n📋 [bold]GitShield Pre-Commit Analysis[/bold]\n", style="cyan")
        console.print(f"  Branch: [cyan]{branch}[/cyan]")
        console.print(f"  Staged files: [cyan]{len(staged)}[/cyan]")
        if commit_msg:
            console.print(f"  Commit message: [dim]{commit_msg[:50]}...[/dim]" if len(commit_msg) > 50 else f"  Commit message: [dim]{commit_msg}[/dim]")
        console.print()

    # Run rules
    results = run_all_rules(
        commit_message=commit_msg,
        staged_files=staged,
        branch_name=branch,
    )

    # Security scan
    sec_findings = scan_directory(".", staged_only=True) if staged else []

    # Process warnings
    warnings = [r.message for r in results]
    if sec_findings:
        for f in sec_findings:
            warnings.append(f"🔒 {f.message} in {os.path.basename(f.file)}")

    # Update memory
    memory_warnings = update_memory(warnings)

    if not results and not sec_findings:
        if not hook:
            console.print(Panel(
                "✅ [bold green]All checks passed![/bold green]",
                border_style="green",
            ))
        sys.exit(0)

    # Display results
    has_blocks = has_blocking_issues(results) or any(
        f.severity in (Severity.CRITICAL,) for f in sec_findings
    )

    for r in results:
        style = {
            RuleSeverity.BLOCK: "bold red",
            RuleSeverity.WARNING: "yellow",
            RuleSeverity.INFO: "dim",
        }.get(r.severity, "white")

        console.print(f"  {r.severity.icon} [{r.severity.value}] {r.message}", style=style)
        if r.suggestion:
            console.print(f"     💡 {r.suggestion}", style="dim")

        # AI insight
        ai = generate_ai_suggestion(r.message)
        console.print(f"     🤖 {ai}", style="dim cyan")

        # Progressive tip
        count = memory_warnings.get(r.message, 0)
        tip = get_progressive_tip(count, r.message)
        if tip:
            console.print(f"     {tip}", style="bold magenta")

        console.print()

    for f in sec_findings:
        console.print(f"  🔒 [{f.severity.value}] {f.message} — {os.path.basename(f.file)}", style="bold red")

    if has_blocks:
        console.print("\n[bold red]❌ Commit BLOCKED — fix critical issues above[/bold red]\n")
        sys.exit(1)

    console.print("\n[green]✅ Commit allowed (review warnings above)[/green]\n")
    sys.exit(0)


# ═══════════════════════════════════════════════════════════════
# CHECK-MSG COMMAND (for commit-msg hook, reads stdin)
# ═══════════════════════════════════════════════════════════════
@main.command("check-msg")
def check_msg():
    """📝 Analyze commit message quality (reads from stdin)."""
    msg = sys.stdin.read().strip()
    if not msg:
        return

    from devflow.rules import analyze_commit_message
    results = analyze_commit_message(msg)
    for r in results:
        console.print(f"  {r.severity.icon} {r.message}", style="yellow" if r.severity == RuleSeverity.WARNING else "dim")
        if r.suggestion:
            console.print(f"     💡 {r.suggestion}", style="dim")


# ═══════════════════════════════════════════════════════════════
# HEALTH COMMAND
# ═══════════════════════════════════════════════════════════════
@main.command()
@click.argument("path", default=".")
def health(path):
    """🏥 Repository health analysis with score and grade."""
    console.print("\n🏥 [bold]Repository Health Report[/bold]\n", style="cyan")

    if not is_git_repo(path):
        console.print("[red]Not a Git repository![/red]")
        sys.exit(1)

    report = calculate_health(path)
    repo_stats = get_repo_stats(path)

    # Score display
    score_color = "green" if report.score >= 70 else "yellow" if report.score >= 50 else "red"
    console.print(Panel(
        f"[bold {score_color}]Score: {report.score}/100  •  Grade: {report.grade}[/bold {score_color}]\n\n"
        f"{report.summary}",
        title="Health Score",
        border_style=score_color,
    ))

    # Repo stats
    stats_table = Table(box=box.SIMPLE, show_header=False)
    stats_table.add_column("Metric", style="bold")
    stats_table.add_column("Value", style="cyan")
    stats_table.add_row("Total Files", str(repo_stats.get("total_files", 0)))
    stats_table.add_row("Total Size", f"{repo_stats.get('total_size_mb', 0)} MB")
    stats_table.add_row("Total Commits", str(repo_stats.get("total_commits", 0)))
    stats_table.add_row("Branches", str(repo_stats.get("total_branches", 0)))
    stats_table.add_row("Contributors", str(repo_stats.get("total_contributors", 0)))
    console.print(stats_table)

    # Issues
    if report.issues:
        console.print(f"\n[bold]Issues ({len(report.issues)}):[/bold]\n")
        for issue in report.issues:
            console.print(f"  {issue.icon} [{issue.category}] {issue.message}")
            if issue.suggestion:
                console.print(f"     💡 {issue.suggestion}", style="dim")
    else:
        console.print("\n[green]✅ No issues found![/green]")

    console.print()


# ═══════════════════════════════════════════════════════════════
# FIX COMMAND
# ═══════════════════════════════════════════════════════════════
@main.command()
def fix():
    """🔧 Interactive mistake recovery wizard."""
    console.print("\n🔧 [bold]GitShield Recovery Wizard[/bold]\n", style="cyan")

    options = get_recovery_options()
    current_cat = ""

    for i, opt in enumerate(options, 1):
        if opt["category"] != current_cat:
            current_cat = opt["category"]
            console.print(f"\n  [bold]{current_cat}:[/bold]")
        console.print(f"    [{i:2d}] {opt['label']}")

    console.print(f"\n    [ 0] Cancel\n")

    try:
        choice = click.prompt("Select option", type=int, default=0)
    except (click.Abort, EOFError):
        return

    if choice == 0 or choice > len(options):
        console.print("[dim]Cancelled.[/dim]")
        return

    selected = options[choice - 1]
    kwargs = {}

    if selected["id"] == "remove_history":
        kwargs["filename"] = click.prompt("Enter filename to remove from history")
    elif selected["id"] == "secret_leak":
        kwargs["filename"] = click.prompt("Enter leaked file name", default=".env")
    elif selected["id"] == "diverged":
        kwargs["branch"] = click.prompt("Enter branch name", default="main")

    action = execute_recovery(selected["id"], **kwargs)
    if action:
        console.print(Panel(
            f"[bold]{action.title}[/bold]\n\n"
            f"{action.description}\n\n"
            f"Risk: {action.risk_icon} {action.risk_level.upper()}\n"
            + (f"\n⚠️ {action.warning}\n" if action.warning else "") +
            f"\n[bold]Commands:[/bold]\n" +
            "\n".join(f"  [cyan]{c}[/cyan]" for c in action.commands if c),
            border_style="yellow" if action.risk_level != "safe" else "green",
        ))


# ═══════════════════════════════════════════════════════════════
# INIT COMMAND
# ═══════════════════════════════════════════════════════════════
@main.command()
@click.option("--force", is_flag=True, help="Overwrite existing hooks")
def init(force):
    """⚡ Initialize GitShield — install git hooks and setup."""
    console.print("\n⚡ [bold]GitShield Setup[/bold]\n", style="cyan")

    if not is_git_repo():
        console.print("[red]Error: Not a Git repository. Run 'git init' first.[/red]")
        sys.exit(1)

    # Install hooks
    console.print("[bold]Installing Git hooks...[/bold]")
    results = install_hooks(".")
    for hook, status in results.items():
        icon = "✅" if status == "installed" else "⚠️"
        console.print(f"  {icon} {hook}: {status}")

    # Check .gitignore
    if not os.path.exists(".gitignore"):
        console.print("\n[bold]Generating .gitignore...[/bold]")
        types = detect_project_types(".")
        write_gitignore(".", types)
        console.print(f"  ✅ Created .gitignore for: {', '.join(types)}")
    else:
        missing = get_missing_patterns(".")
        if missing:
            console.print(f"\n  💡 .gitignore may be missing {len(missing)} patterns. Run 'gitshield gitignore'")

    console.print(Panel(
        "✅ [bold green]GitShield is ready![/bold green]\n\n"
        "Your commits and pushes are now protected.\n"
        "Run [cyan]gitshield doctor[/cyan] for full system check.",
        border_style="green",
    ))


# ═══════════════════════════════════════════════════════════════
# UNINSTALL COMMAND
# ═══════════════════════════════════════════════════════════════
@main.command()
def uninstall():
    """🗑️ Remove GitShield git hooks."""
    console.print("\n🗑️ [bold]Removing GitShield hooks...[/bold]\n", style="yellow")
    results = uninstall_hooks(".")
    for hook, status in results.items():
        console.print(f"  • {hook}: {status}")
    console.print("\n[dim]GitShield hooks removed.[/dim]\n")


# ═══════════════════════════════════════════════════════════════
# GITIGNORE COMMAND
# ═══════════════════════════════════════════════════════════════
@main.command()
@click.option("--write", is_flag=True, help="Write/overwrite .gitignore")
@click.option("--check", "check_mode", is_flag=True, help="Show missing patterns only")
def gitignore(write, check_mode):
    """📝 Generate or update .gitignore based on project type."""
    console.print("\n📝 [bold]Smart .gitignore Generator[/bold]\n", style="cyan")

    types = detect_project_types(".")
    console.print(f"  Detected project type(s): [cyan]{', '.join(types)}[/cyan]\n")

    if check_mode:
        missing = get_missing_patterns(".")
        tracked = get_tracked_but_should_ignore(".")
        if missing:
            console.print("[bold]Missing patterns:[/bold]")
            for p in missing:
                console.print(f"  • {p}")
        if tracked:
            console.print("\n[bold yellow]Tracked files that should be ignored:[/bold yellow]")
            for f in tracked:
                console.print(f"  ⚠️ {f}")
        if not missing and not tracked:
            console.print("[green]✅ .gitignore looks good![/green]")
        return

    content = generate_gitignore(".", types)
    if write:
        write_gitignore(".", types)
        console.print("[green]✅ .gitignore written successfully![/green]")
    else:
        console.print("[dim]Preview (use --write to save):[/dim]\n")
        console.print(content[:500] + ("\n..." if len(content) > 500 else ""))
        console.print(f"\n[dim]Use 'devflow gitignore --write' to write file[/dim]")


# ═══════════════════════════════════════════════════════════════
# GUIDE COMMAND
# ═══════════════════════════════════════════════════════════════
@main.command()
@click.argument("topic", default="")
def guide(topic):
    """📚 Git workflow guidance and tutorials."""
    if not topic:
        console.print("\n📚 [bold]Available Guides[/bold]\n", style="cyan")
        topics = get_available_topics()
        for t in topics:
            console.print(f"  • devflow guide [cyan]{t}[/cyan]")
        console.print()
        return

    guide_obj = get_guide(topic)
    console.print(f"\n📚 [bold]{guide_obj.title}[/bold]", style="cyan")
    console.print(f"   {guide_obj.description}\n")

    if guide_obj.steps:
        for i, step in enumerate(guide_obj.steps, 1):
            console.print(f"  [bold]{i}. {step['step']}[/bold]")
            if step.get("command"):
                console.print(f"     [cyan]$ {step['command']}[/cyan]")
            console.print()

    if guide_obj.tips:
        console.print("[bold]💡 Tips:[/bold]")
        for tip in guide_obj.tips:
            console.print(f"  • {tip}")
    console.print()


# ═══════════════════════════════════════════════════════════════
# STATS COMMAND
# ═══════════════════════════════════════════════════════════════
@main.command()
def stats():
    """📊 Developer behavior statistics and insights."""
    console.print("\n📊 [bold]Developer Statistics[/bold]\n", style="cyan")

    stat_data = get_statistics(".")

    # Main stats table
    table = Table(box=box.ROUNDED, border_style="cyan", title="Overview")
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right", style="cyan")
    table.add_row("Commits Analyzed", str(stat_data["total_commits_analyzed"]))
    table.add_row("Total Warnings", str(stat_data["total_warnings"]))
    table.add_row("Security Scans", str(stat_data["total_scans"]))
    table.add_row("Sessions", str(stat_data["total_sessions"]))
    table.add_row("Skill Level", stat_data["skill_level"].upper())
    table.add_row("Active Streak", f"{stat_data['streak_days']} days")
    table.add_row("Blocks Prevented", str(stat_data["blocks_prevented"]))
    table.add_row("Issues Resolved", str(stat_data["resolved_issues"]))
    console.print(table)

    # Category breakdown
    cats = stat_data["categories"]
    if any(v > 0 for v in cats.values()):
        console.print("\n[bold]Warning Categories:[/bold]")
        for cat, count in cats.items():
            if count > 0:
                bar = "█" * min(count, 30)
                console.print(f"  {cat:12s} {bar} {count}")

    # Top issues
    if stat_data["top_issues"]:
        console.print("\n[bold]Top Issues:[/bold]")
        for issue, count in stat_data["top_issues"]:
            console.print(f"  [{count}x] {issue[:60]}")

    # Insights
    insights = get_behavior_insights(".")
    if insights:
        console.print("\n[bold]Insights:[/bold]")
        for insight in insights:
            console.print(f"  {insight}")

    console.print()


# ═══════════════════════════════════════════════════════════════
# DOCTOR COMMAND
# ═══════════════════════════════════════════════════════════════
@main.command()
def doctor():
    """🩺 Full system diagnostic."""
    console.print("\n🩺 [bold]GitShield System Diagnostic[/bold]\n", style="cyan")

    checks = []

    # Git installed?
    import shutil
    git = shutil.which("git")
    checks.append(("Git installed", "✅" if git else "❌", git or "NOT FOUND"))

    # Git repo?
    is_repo = is_git_repo()
    checks.append(("Git repository", "✅" if is_repo else "❌", "Yes" if is_repo else "Not a git repo"))

    if is_repo:
        # Branch
        branch = get_current_branch()
        checks.append(("Current branch", "✅", branch))

        # Hooks
        hook_status = get_hook_status()
        for hook, status in hook_status.items():
            if hook != "error":
                checks.append((f"Hook: {hook}", "✅" if "active" in status else "❌", status))

        # .gitignore
        has_gitignore = os.path.exists(".gitignore")
        checks.append((".gitignore", "✅" if has_gitignore else "❌",
                       "Found" if has_gitignore else "Missing — run 'gitshield gitignore --write'"))

        # Security scan
        findings = scan_directory(".", staged_only=False)
        sec_count = len(findings)
        checks.append(("Security scan", "✅" if sec_count == 0 else "⚠️",
                       f"{sec_count} issues" if sec_count else "Clean"))

        # Health
        report = calculate_health(".")
        checks.append(("Repo health", "✅" if report.score >= 70 else "⚠️",
                       f"{report.score}/100 (Grade: {report.grade})"))

    # Display
    table = Table(box=box.ROUNDED, border_style="cyan")
    table.add_column("Check", style="bold", width=20)
    table.add_column("Status", width=4, justify="center")
    table.add_column("Details", style="dim")

    for name, status, detail in checks:
        table.add_row(name, status, str(detail))

    console.print(table)

    if not is_repo:
        console.print("\n[yellow]⚠️ Not in a Git repository. Run 'git init' to get started.[/yellow]")
    elif any("❌" in c[1] for c in checks):
        console.print("\n[yellow]⚠️ Some checks failed. Run 'gitshield init' to fix.[/yellow]")
    else:
        console.print("\n[green]✅ All systems operational![/green]")
    console.print()


# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    main()
