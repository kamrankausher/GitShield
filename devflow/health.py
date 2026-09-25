"""
DevFlow AI++ — Repository Health Analyzer
==========================================
Comprehensive repository health analysis including structure,
file hygiene, branch management, commit quality, and an overall
health score (0-100).

Features:
- Repository structure analysis
- Large file detection (with size tracking)
- Dead/unused file detection
- .gitignore completeness check
- Branch hygiene (stale branches)
- Commit message quality stats
- Overall health score (0-100) with grade
- Detailed health report generation
"""

import os
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple


@dataclass
class HealthIssue:
    """A single health issue."""
    category: str
    severity: str  # critical, warning, info
    message: str
    suggestion: str = ""

    @property
    def icon(self):
        return {"critical": "🔴", "warning": "🟡", "info": "💡"}[self.severity]


@dataclass
class HealthReport:
    """Complete repository health report."""
    score: int = 0
    grade: str = "F"
    issues: List[HealthIssue] = field(default_factory=list)
    metrics: Dict = field(default_factory=dict)
    summary: str = ""

    def __post_init__(self):
        if not self.metrics:
            self.metrics = {}


def _run_git(args: List[str], cwd: str = ".") -> Optional[str]:
    try:
        result = subprocess.run(
            ["git"] + args, capture_output=True, text=True,
            cwd=cwd, timeout=15, encoding="utf-8", errors="replace",
            stdin=subprocess.DEVNULL,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None


EXCLUDED_DIRS = {
    "venv", ".git", "__pycache__", "node_modules", ".tox",
    ".mypy_cache", ".pytest_cache", "dist", "build", ".eggs",
    ".venv", "env", "vendor", "migrations", ".next",
}


# ═══════════════════════════════════════════════════════════════
# INDIVIDUAL HEALTH CHECKS
# ═══════════════════════════════════════════════════════════════
def check_repo_structure(repo_path: str = ".") -> Tuple[int, List[HealthIssue]]:
    """Analyze repository structure. Returns (score_deduction, issues)."""
    issues = []
    deduction = 0

    # Check for README
    readme_variants = ["README.md", "README.rst", "README.txt", "README"]
    has_readme = any(os.path.exists(os.path.join(repo_path, r)) for r in readme_variants)
    if not has_readme:
        issues.append(HealthIssue("structure", "warning", "No README file found", "Create a README.md describing your project"))
        deduction += 10
    else:
        # Check README quality
        for r in readme_variants:
            path = os.path.join(repo_path, r)
            if os.path.exists(path):
                try:
                    size = os.path.getsize(path)
                    if size < 100:
                        issues.append(HealthIssue("structure", "info", "README is very short", "Add description, installation, usage, and contributing sections"))
                        deduction += 3
                except OSError:
                    pass
                break

    # Check for .gitignore
    if not os.path.exists(os.path.join(repo_path, ".gitignore")):
        issues.append(HealthIssue("structure", "critical", "No .gitignore file found", "Run 'devflow gitignore' to generate one"))
        deduction += 15

    # Check for LICENSE
    license_variants = ["LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE"]
    if not any(os.path.exists(os.path.join(repo_path, l)) for l in license_variants):
        issues.append(HealthIssue("structure", "warning", "No LICENSE file found", "Add a LICENSE file (MIT, Apache-2.0, etc.)"))
        deduction += 5

    # Check for common project files
    config_files = {
        "Python": ["setup.py", "pyproject.toml", "setup.cfg", "Pipfile"],
        "Node.js": ["package.json"],
        "Ruby": ["Gemfile"],
        "Go": ["go.mod"],
        "Rust": ["Cargo.toml"],
        "Java": ["pom.xml", "build.gradle"],
    }

    detected_lang = None
    for lang, files in config_files.items():
        if any(os.path.exists(os.path.join(repo_path, f)) for f in files):
            detected_lang = lang
            break

    if detected_lang:
        issues.append(HealthIssue("structure", "info", f"Detected project type: {detected_lang}", ""))

    return deduction, issues


def check_large_files(repo_path: str = ".", threshold_mb: float = 5.0) -> Tuple[int, List[HealthIssue]]:
    """Find large files in the repository."""
    issues = []
    deduction = 0
    threshold = threshold_mb * 1024 * 1024
    large_files = []

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for fname in files:
            filepath = os.path.join(root, fname)
            try:
                size = os.path.getsize(filepath)
                if size > threshold:
                    size_mb = size / (1024 * 1024)
                    rel_path = os.path.relpath(filepath, repo_path)
                    large_files.append((rel_path, size_mb))
            except OSError:
                pass

    if large_files:
        deduction += min(len(large_files) * 3, 15)
        for filepath, size_mb in large_files[:5]:
            issues.append(HealthIssue(
                "files", "warning",
                f"Large file: {filepath} ({size_mb:.1f} MB)",
                "Use Git LFS for large files or add to .gitignore"
            ))

    return deduction, issues


def check_file_hygiene(repo_path: str = ".") -> Tuple[int, List[HealthIssue]]:
    """Check for files that shouldn't be in the repo."""
    issues = []
    deduction = 0

    bad_patterns = {
        "*.pyc": "Compiled Python files",
        "*.pyo": "Optimized Python files",
        "*.class": "Compiled Java files",
        "*.o": "Compiled C/C++ objects",
        ".DS_Store": "macOS metadata",
        "Thumbs.db": "Windows thumbnail cache",
        "desktop.ini": "Windows folder config",
        "*.log": "Log files",
        "*.tmp": "Temporary files",
        "*.swp": "Vim swap files",
        "*.swo": "Vim swap files",
    }

    tracked = _run_git(["ls-files"], cwd=repo_path)
    if tracked:
        tracked_files = tracked.splitlines()
        for filepath in tracked_files:
            basename = os.path.basename(filepath)
            _, ext = os.path.splitext(filepath)

            for pattern, desc in bad_patterns.items():
                if pattern.startswith("*"):
                    if filepath.endswith(pattern[1:]):
                        issues.append(HealthIssue(
                            "files", "warning",
                            f"Tracked file should be ignored: {filepath} ({desc})",
                            f"Add '{pattern}' to .gitignore and run: git rm --cached {filepath}"
                        ))
                        deduction += 2
                elif basename == pattern:
                    issues.append(HealthIssue(
                        "files", "warning",
                        f"Tracked file should be ignored: {filepath} ({desc})",
                        f"Add '{pattern}' to .gitignore and run: git rm --cached {filepath}"
                    ))
                    deduction += 2

    return min(deduction, 15), issues


def check_branch_hygiene(repo_path: str = ".") -> Tuple[int, List[HealthIssue]]:
    """Check branch management health."""
    issues = []
    deduction = 0

    # Count local branches
    branches = _run_git(["branch", "--format=%(refname:short)"], cwd=repo_path)
    if branches:
        branch_list = [b.strip() for b in branches.splitlines() if b.strip()]
        branch_count = len(branch_list)

        if branch_count > 10:
            issues.append(HealthIssue(
                "branches", "warning",
                f"Too many local branches ({branch_count})",
                "Delete merged branches: git branch -d <branch>"
            ))
            deduction += 5

        # Check for merged branches
        merged = _run_git(["branch", "--merged", "HEAD"], cwd=repo_path)
        if merged:
            merged_branches = [
                b.strip().lstrip("* ")
                for b in merged.splitlines()
                if b.strip() and b.strip().lstrip("* ") not in ("main", "master", "develop", "dev")
            ]
            if merged_branches:
                issues.append(HealthIssue(
                    "branches", "info",
                    f"{len(merged_branches)} merged branch(es) can be deleted: {', '.join(merged_branches[:3])}",
                    "Clean up: git branch -d " + " ".join(merged_branches[:3])
                ))
                deduction += 2

    return deduction, issues


def check_commit_quality(repo_path: str = ".", n: int = 20) -> Tuple[int, List[HealthIssue]]:
    """Analyze recent commit message quality."""
    issues = []
    deduction = 0

    output = _run_git(["log", f"-{n}", "--format=%s"], cwd=repo_path)
    if not output:
        return 0, issues

    messages = output.splitlines()
    short_count = 0
    vague_count = 0
    conventional_count = 0
    vague_words = {"update", "fix", "changes", "done", "wip", "stuff", "misc"}
    conv_prefixes = {"feat:", "fix:", "docs:", "style:", "refactor:", "test:", "chore:", "perf:", "ci:", "build:", "revert:"}

    for msg in messages:
        if len(msg.strip()) < 5:
            short_count += 1
        if msg.strip().lower() in vague_words:
            vague_count += 1
        if any(msg.lower().startswith(p) for p in conv_prefixes):
            conventional_count += 1

    total = len(messages)
    if total > 0:
        short_pct = short_count / total * 100
        vague_pct = vague_count / total * 100
        conv_pct = conventional_count / total * 100

        if short_pct > 30:
            issues.append(HealthIssue(
                "commits", "warning",
                f"{short_pct:.0f}% of recent commits have short messages",
                "Use descriptive messages: 'feat: add user authentication'"
            ))
            deduction += 8

        if vague_pct > 20:
            issues.append(HealthIssue(
                "commits", "warning",
                f"{vague_pct:.0f}% of recent commits have vague messages",
                "Be specific: describe WHAT changed and WHY"
            ))
            deduction += 5

        if conv_pct > 50:
            issues.append(HealthIssue(
                "commits", "info",
                f"👍 {conv_pct:.0f}% of commits use conventional format",
                ""
            ))

    return deduction, issues


def check_gitignore_quality(repo_path: str = ".") -> Tuple[int, List[HealthIssue]]:
    """Check .gitignore completeness for the detected project type."""
    issues = []
    deduction = 0
    gitignore_path = os.path.join(repo_path, ".gitignore")

    if not os.path.exists(gitignore_path):
        return 10, [HealthIssue("config", "critical", "No .gitignore file", "Run 'devflow gitignore'")]

    try:
        with open(gitignore_path, encoding="utf-8") as f:
            content = f.read()
    except OSError:
        return 0, issues

    # Essential patterns every project should have
    essential = [".env", "__pycache__", "*.pyc", "node_modules", "venv", ".DS_Store"]
    missing = [p for p in essential if p not in content]

    if missing:
        issues.append(HealthIssue(
            "config", "info",
            f".gitignore may be missing: {', '.join(missing[:3])}",
            "Run 'devflow gitignore' to add recommended patterns"
        ))
        deduction += min(len(missing) * 2, 8)

    return deduction, issues


# ═══════════════════════════════════════════════════════════════
# HEALTH SCORE CALCULATION
# ═══════════════════════════════════════════════════════════════
def calculate_health(repo_path: str = ".") -> HealthReport:
    """Calculate comprehensive repository health score."""
    report = HealthReport()
    total_deduction = 0

    # Run all checks
    checks = [
        ("Structure", check_repo_structure),
        ("Large Files", check_large_files),
        ("File Hygiene", check_file_hygiene),
        ("Branch Hygiene", check_branch_hygiene),
        ("Commit Quality", check_commit_quality),
        ("Gitignore Quality", check_gitignore_quality),
    ]

    category_scores = {}

    for name, check_fn in checks:
        deduction, issues = check_fn(repo_path)
        total_deduction += deduction
        report.issues.extend(issues)
        category_scores[name] = max(0, 100 - deduction * 5)

    # Calculate final score
    report.score = max(0, min(100, 100 - total_deduction))
    report.metrics = {
        "category_scores": category_scores,
        "total_issues": len(report.issues),
        "critical_count": sum(1 for i in report.issues if i.severity == "critical"),
        "warning_count": sum(1 for i in report.issues if i.severity == "warning"),
        "info_count": sum(1 for i in report.issues if i.severity == "info"),
    }

    # Assign grade
    if report.score >= 90:
        report.grade = "A+"
    elif report.score >= 80:
        report.grade = "A"
    elif report.score >= 70:
        report.grade = "B"
    elif report.score >= 60:
        report.grade = "C"
    elif report.score >= 50:
        report.grade = "D"
    else:
        report.grade = "F"

    # Generate summary
    if report.score >= 90:
        report.summary = "🏆 Excellent! Your repository is in great shape."
    elif report.score >= 70:
        report.summary = "👍 Good health. A few improvements would make it great."
    elif report.score >= 50:
        report.summary = "⚠️ Fair health. Several issues should be addressed."
    else:
        report.summary = "🔴 Poor health. Significant improvements needed."

    return report


def get_repo_stats(repo_path: str = ".") -> Dict:
    """Get quick repository statistics."""
    stats = {}

    # File count
    total_files = 0
    total_size = 0
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for f in files:
            total_files += 1
            try:
                total_size += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass

    stats["total_files"] = total_files
    stats["total_size_mb"] = round(total_size / (1024 * 1024), 2)

    # Git stats
    commit_count = _run_git(["rev-list", "--count", "HEAD"], cwd=repo_path)
    stats["total_commits"] = int(commit_count) if commit_count else 0

    branch_output = _run_git(["branch"], cwd=repo_path)
    stats["total_branches"] = len(branch_output.splitlines()) if branch_output else 0

    contributors = _run_git(["shortlog", "-sn", "--no-merges"], cwd=repo_path)
    stats["total_contributors"] = len(contributors.splitlines()) if contributors else 0

    # Age
    first_commit = _run_git(["log", "--reverse", "--format=%ci", "-1"], cwd=repo_path)
    if first_commit:
        try:
            first_date = datetime.strptime(first_commit[:10], "%Y-%m-%d")
            stats["age_days"] = (datetime.now() - first_date).days
        except ValueError:
            stats["age_days"] = 0

    return stats
