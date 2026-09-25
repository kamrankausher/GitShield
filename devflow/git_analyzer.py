"""
DevFlow AI++ — Git Analyzer Module
====================================
Advanced Git workflow analysis including branch management,
commit history, merge conflicts, stash awareness, and divergence detection.

Features:
- Current branch detection
- Commit history analysis (frequency, patterns)
- Merge conflict detection
- Stash awareness
- Remote tracking & divergence (ahead/behind)
- Untracked file detection
- Large file detection in staged changes
- Git status summary
"""

import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple


@dataclass
class GitStatus:
    """Comprehensive Git repository status."""
    is_git_repo: bool = False
    current_branch: str = ""
    staged_files: List[str] = None
    modified_files: List[str] = None
    untracked_files: List[str] = None
    stash_count: int = 0
    ahead: int = 0
    behind: int = 0
    has_remote: bool = False
    total_commits: int = 0
    last_commit_message: str = ""
    last_commit_date: str = ""
    has_merge_conflicts: bool = False
    detached_head: bool = False

    def __post_init__(self):
        if self.staged_files is None:
            self.staged_files = []
        if self.modified_files is None:
            self.modified_files = []
        if self.untracked_files is None:
            self.untracked_files = []


def _run_git(args: List[str], cwd: str = ".") -> Optional[str]:
    """Run a git command and return output."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True, text=True, cwd=cwd,
            timeout=10, encoding="utf-8", errors="replace",
            stdin=subprocess.DEVNULL,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None


def is_git_repo(path: str = ".") -> bool:
    """Check if the current directory is inside a Git repository."""
    return _run_git(["rev-parse", "--is-inside-work-tree"], cwd=path) == "true"


# ═══════════════════════════════════════════════════════════════
# BRANCH ANALYSIS
# ═══════════════════════════════════════════════════════════════
def get_current_branch(cwd: str = ".") -> str:
    """Get the current branch name."""
    branch = _run_git(["branch", "--show-current"], cwd=cwd)
    if not branch:
        # Might be detached HEAD
        head = _run_git(["rev-parse", "--short", "HEAD"], cwd=cwd)
        return f"HEAD detached at {head}" if head else "unknown"
    return branch


def is_detached_head(cwd: str = ".") -> bool:
    """Check if HEAD is detached."""
    branch = _run_git(["branch", "--show-current"], cwd=cwd)
    return not branch or branch == ""


def get_all_branches(cwd: str = ".") -> Dict[str, List[str]]:
    """Get all local and remote branches."""
    result = {"local": [], "remote": []}

    local = _run_git(["branch", "--format=%(refname:short)"], cwd=cwd)
    if local:
        result["local"] = [b.strip() for b in local.splitlines() if b.strip()]

    remote = _run_git(["branch", "-r", "--format=%(refname:short)"], cwd=cwd)
    if remote:
        result["remote"] = [b.strip() for b in remote.splitlines() if b.strip()]

    return result


def get_stale_branches(cwd: str = ".", days: int = 30) -> List[str]:
    """Find branches with no commits in the last N days."""
    stale = []
    branches = get_all_branches(cwd)

    for branch in branches["local"]:
        if branch in ("main", "master", "develop", "dev"):
            continue
        last_commit = _run_git(
            ["log", "-1", "--format=%ci", branch], cwd=cwd
        )
        if last_commit:
            try:
                commit_date = datetime.strptime(last_commit[:19], "%Y-%m-%d %H:%M:%S")
                age = (datetime.now() - commit_date).days
                if age > days:
                    stale.append(f"{branch} (last commit {age} days ago)")
            except ValueError:
                pass

    return stale


# ═══════════════════════════════════════════════════════════════
# COMMIT ANALYSIS
# ═══════════════════════════════════════════════════════════════
def get_commit_message(cwd: str = ".") -> str:
    """Get the current commit message (from COMMIT_EDITMSG)."""
    commit_file = os.path.join(cwd, ".git", "COMMIT_EDITMSG")
    try:
        with open(commit_file, encoding="utf-8") as f:
            return f.read().strip()
    except (FileNotFoundError, OSError):
        return ""


def get_last_n_commits(n: int = 10, cwd: str = ".") -> List[Dict]:
    """Get the last N commits with details."""
    output = _run_git(
        ["log", f"-{n}", "--format=%H|%an|%ae|%ci|%s"],
        cwd=cwd,
    )
    if not output:
        return []

    commits = []
    for line in output.splitlines():
        parts = line.split("|", 4)
        if len(parts) == 5:
            commits.append({
                "hash": parts[0][:8],
                "author": parts[1],
                "email": parts[2],
                "date": parts[3],
                "message": parts[4],
            })
    return commits


def get_commit_count(cwd: str = ".") -> int:
    """Get total commit count."""
    output = _run_git(["rev-list", "--count", "HEAD"], cwd=cwd)
    try:
        return int(output) if output else 0
    except (ValueError, TypeError):
        return 0


def analyze_commit_frequency(n: int = 20, cwd: str = ".") -> Dict:
    """Analyze commit frequency patterns."""
    commits = get_last_n_commits(n, cwd)
    if not commits:
        return {"pattern": "no_commits", "avg_per_day": 0}

    dates = []
    for c in commits:
        try:
            d = datetime.strptime(c["date"][:10], "%Y-%m-%d")
            dates.append(d)
        except ValueError:
            pass

    if len(dates) < 2:
        return {"pattern": "too_few", "avg_per_day": 0}

    span = (max(dates) - min(dates)).days or 1
    avg = len(dates) / span

    return {
        "total_analyzed": len(commits),
        "span_days": span,
        "avg_per_day": round(avg, 2),
        "pattern": "high" if avg > 5 else "normal" if avg > 1 else "low",
    }


# ═══════════════════════════════════════════════════════════════
# FILE STATUS
# ═══════════════════════════════════════════════════════════════
def get_staged_files(cwd: str = ".") -> List[str]:
    """Get list of staged files."""
    output = _run_git(["diff", "--cached", "--name-only"], cwd=cwd)
    return output.splitlines() if output else []


def get_modified_files(cwd: str = ".") -> List[str]:
    """Get list of modified (unstaged) files."""
    output = _run_git(["diff", "--name-only"], cwd=cwd)
    return output.splitlines() if output else []


def get_untracked_files(cwd: str = ".") -> List[str]:
    """Get list of untracked files."""
    output = _run_git(["ls-files", "--others", "--exclude-standard"], cwd=cwd)
    return output.splitlines() if output else []


# ═══════════════════════════════════════════════════════════════
# REMOTE & SYNC
# ═══════════════════════════════════════════════════════════════
def get_remote_info(cwd: str = ".") -> Optional[str]:
    """Get remote origin URL."""
    return _run_git(["remote", "get-url", "origin"], cwd=cwd)


def get_ahead_behind(cwd: str = ".") -> Tuple[int, int]:
    """Get how many commits ahead/behind the remote."""
    output = _run_git(
        ["rev-list", "--left-right", "--count", "HEAD...@{upstream}"],
        cwd=cwd,
    )
    if output:
        parts = output.split()
        if len(parts) == 2:
            try:
                return int(parts[0]), int(parts[1])
            except ValueError:
                pass
    return 0, 0


def get_stash_count(cwd: str = ".") -> int:
    """Get number of stashed changes."""
    output = _run_git(["stash", "list"], cwd=cwd)
    return len(output.splitlines()) if output else 0


# ═══════════════════════════════════════════════════════════════
# CONFLICT DETECTION
# ═══════════════════════════════════════════════════════════════
def has_merge_conflicts(cwd: str = ".") -> bool:
    """Check if there are unresolved merge conflicts."""
    output = _run_git(["diff", "--name-only", "--diff-filter=U"], cwd=cwd)
    return bool(output and output.strip())


def get_conflicted_files(cwd: str = ".") -> List[str]:
    """Get list of files with merge conflicts."""
    output = _run_git(["diff", "--name-only", "--diff-filter=U"], cwd=cwd)
    return output.splitlines() if output else []


# ═══════════════════════════════════════════════════════════════
# WARNING GENERATORS (legacy compatible + enhanced)
# ═══════════════════════════════════════════════════════════════
def check_main_branch(cwd: str = ".") -> List[str]:
    """Check if committing directly to main/master branch."""
    warnings = []
    branch = get_current_branch(cwd)
    if branch in ("main", "master"):
        warnings.append(
            "⚠️ You are committing directly to MAIN branch (use feature branch)"
        )
    return warnings


def check_untracked_files(cwd: str = ".") -> List[str]:
    """Check for untracked files."""
    warnings = []
    untracked = get_untracked_files(cwd)
    if untracked:
        preview = ", ".join(untracked[:3])
        suffix = f" and {len(untracked)-3} more" if len(untracked) > 3 else ""
        warnings.append(
            f"⚠️ You have {len(untracked)} untracked file(s): {preview}{suffix}"
        )
    return warnings


def check_large_files(file_list: List[str], cwd: str = ".") -> List[str]:
    """Check for risky file types in staged files."""
    warnings = []
    risky_extensions = {".log", ".csv", ".db", ".sqlite", ".exe", ".dll", ".zip", ".tar", ".gz"}
    for filepath in file_list:
        _, ext = os.path.splitext(filepath)
        if ext.lower() in risky_extensions:
            warnings.append(f"⚠️ Risky file detected: {filepath}")
    return warnings


# ═══════════════════════════════════════════════════════════════
# COMPREHENSIVE STATUS
# ═══════════════════════════════════════════════════════════════
def get_full_status(cwd: str = ".") -> GitStatus:
    """Get comprehensive Git repository status."""
    status = GitStatus()

    status.is_git_repo = is_git_repo(cwd)
    if not status.is_git_repo:
        return status

    status.current_branch = get_current_branch(cwd)
    status.detached_head = is_detached_head(cwd)
    status.staged_files = get_staged_files(cwd)
    status.modified_files = get_modified_files(cwd)
    status.untracked_files = get_untracked_files(cwd)
    status.stash_count = get_stash_count(cwd)
    status.has_merge_conflicts = has_merge_conflicts(cwd)
    status.total_commits = get_commit_count(cwd)

    # Remote info
    remote = get_remote_info(cwd)
    status.has_remote = bool(remote)
    if status.has_remote:
        status.ahead, status.behind = get_ahead_behind(cwd)

    # Last commit
    commits = get_last_n_commits(1, cwd)
    if commits:
        status.last_commit_message = commits[0]["message"]
        status.last_commit_date = commits[0]["date"]

    return status
