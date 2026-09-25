"""
DevFlow AI++ — Mistake Recovery Engine
========================================
Guides users through recovering from Git mistakes including
undoing commits, removing files from history, fixing branches,
and recovering from detached HEAD state.

Features:
- Undo last commit (soft/mixed/hard)
- Remove file from Git history
- Fix broken branches
- Recover from detached HEAD
- Unstage files
- Reset to remote state
- Interactive recovery wizard
"""

import subprocess
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class RecoveryAction:
    """A single recovery action with commands."""
    title: str
    description: str
    commands: List[str]
    risk_level: str  # safe, moderate, dangerous
    warning: str = ""

    @property
    def risk_icon(self):
        return {"safe": "✅", "moderate": "⚠️", "dangerous": "🔴"}[self.risk_level]


def _run_git(args: List[str], cwd: str = ".") -> Optional[str]:
    """Run a git command safely."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True, text=True, cwd=cwd, timeout=10,
            encoding="utf-8", errors="replace",
            stdin=subprocess.DEVNULL,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None


# ═══════════════════════════════════════════════════════════════
# UNDO OPERATIONS
# ═══════════════════════════════════════════════════════════════
def undo_last_commit(mode: str = "soft", cwd: str = ".") -> RecoveryAction:
    """
    Generate commands to undo the last commit.

    Modes:
    - soft: Keep changes staged
    - mixed: Keep changes but unstaged (default git reset)
    - hard: Discard all changes (DANGEROUS)
    """
    modes = {
        "soft": RecoveryAction(
            title="Undo Last Commit (Keep Changes Staged)",
            description="Removes the last commit but keeps all changes in staging area. Safe to re-commit.",
            commands=["git reset --soft HEAD~1"],
            risk_level="safe",
        ),
        "mixed": RecoveryAction(
            title="Undo Last Commit (Unstage Changes)",
            description="Removes the last commit and unstages changes. Changes remain in working directory.",
            commands=["git reset HEAD~1"],
            risk_level="safe",
        ),
        "hard": RecoveryAction(
            title="Undo Last Commit (DELETE Changes)",
            description="Removes the last commit AND discards all changes permanently.",
            commands=["git reset --hard HEAD~1"],
            risk_level="dangerous",
            warning="⚠️ This will permanently delete your changes! Make sure you don't need them.",
        ),
    }
    return modes.get(mode, modes["soft"])


def undo_multiple_commits(count: int = 1) -> RecoveryAction:
    """Generate commands to undo multiple commits."""
    return RecoveryAction(
        title=f"Undo Last {count} Commits",
        description=f"Removes the last {count} commits, keeping changes staged.",
        commands=[f"git reset --soft HEAD~{count}"],
        risk_level="safe" if count <= 3 else "moderate",
        warning=f"This will undo {count} commits. Make sure you intend this." if count > 3 else "",
    )


def amend_last_commit() -> RecoveryAction:
    """Amend the last commit (change message or add files)."""
    return RecoveryAction(
        title="Amend Last Commit",
        description="Modify the last commit — change message and/or add files.",
        commands=[
            "# To change the message:",
            "git commit --amend -m 'new message here'",
            "",
            "# To add files to the last commit:",
            "git add <file>",
            "git commit --amend --no-edit",
        ],
        risk_level="safe",
        warning="Only amend unpushed commits. If already pushed, use 'git push --force' (with caution).",
    )


# ═══════════════════════════════════════════════════════════════
# FILE RECOVERY
# ═══════════════════════════════════════════════════════════════
def remove_file_from_history(filename: str) -> RecoveryAction:
    """Generate commands to remove a file from entire Git history."""
    return RecoveryAction(
        title=f"Remove '{filename}' From Git History",
        description="Completely removes a file from all Git history. Use this for accidentally committed secrets.",
        commands=[
            "# Option 1: Using git filter-branch (built-in)",
            "git filter-branch --force --index-filter \\",
            f"  'git rm --cached --ignore-unmatch {filename}' \\",
            "  --prune-empty --tag-name-filter cat -- --all",
            "",
            "# Option 2: Using BFG Repo-Cleaner (faster, recommended)",
            "# Download: https://rtyley.github.io/bfg-repo-cleaner/",
            f"# java -jar bfg.jar --delete-files {filename}",
            "",
            "# After either method:",
            "git push origin --force --all",
            "git push origin --force --tags",
            "",
            "# Add to .gitignore to prevent future commits:",
            f"echo '{filename}' >> .gitignore",
        ],
        risk_level="dangerous",
        warning="⚠️ This rewrites Git history! All collaborators must re-clone the repo.",
    )


def unstage_file(filename: str = "") -> RecoveryAction:
    """Unstage a file or all files."""
    if filename:
        return RecoveryAction(
            title=f"Unstage '{filename}'",
            description="Remove file from staging area without losing changes.",
            commands=[f"git restore --staged {filename}"],
            risk_level="safe",
        )
    return RecoveryAction(
        title="Unstage All Files",
        description="Remove all files from staging area without losing changes.",
        commands=["git restore --staged ."],
        risk_level="safe",
    )


def discard_changes(filename: str = "") -> RecoveryAction:
    """Discard changes in working directory."""
    if filename:
        return RecoveryAction(
            title=f"Discard Changes in '{filename}'",
            description="Revert file to last committed state. Changes will be LOST.",
            commands=[f"git restore {filename}"],
            risk_level="dangerous",
            warning="⚠️ This permanently discards your changes to this file!",
        )
    return RecoveryAction(
        title="Discard ALL Uncommitted Changes",
        description="Revert all files to last committed state. ALL changes will be LOST.",
        commands=["git restore .", "git clean -fd  # Remove untracked files too"],
        risk_level="dangerous",
        warning="⚠️ This permanently discards ALL uncommitted changes and removes untracked files!",
    )


# ═══════════════════════════════════════════════════════════════
# BRANCH RECOVERY
# ═══════════════════════════════════════════════════════════════
def recover_detached_head() -> RecoveryAction:
    """Recover from detached HEAD state."""
    return RecoveryAction(
        title="Recover From Detached HEAD",
        description="Create a branch to save work done in detached HEAD state.",
        commands=[
            "# Save your current work to a new branch:",
            "git checkout -b recovery-branch",
            "",
            "# Or go back to your previous branch (LOSES uncommitted work):",
            "git checkout main",
        ],
        risk_level="safe",
    )


def fix_diverged_branch(branch: str = "main") -> RecoveryAction:
    """Fix a branch that has diverged from remote."""
    return RecoveryAction(
        title=f"Fix Diverged Branch '{branch}'",
        description="Reconcile local and remote branches that have diverged.",
        commands=[
            "# Option 1: Rebase (clean history, recommended):",
            f"git pull --rebase origin {branch}",
            "",
            "# Option 2: Merge (creates merge commit):",
            f"git pull origin {branch}",
            "",
            "# Option 3: Force reset to remote (LOSES local commits):",
            "git fetch origin",
            f"git reset --hard origin/{branch}",
        ],
        risk_level="moderate",
        warning="Option 3 will discard all local commits not on the remote.",
    )


def delete_branch(branch: str, force: bool = False) -> RecoveryAction:
    """Delete a local branch."""
    flag = "-D" if force else "-d"
    return RecoveryAction(
        title=f"Delete Branch '{branch}'",
        description=f"Remove the local branch.{' Force delete even if unmerged.' if force else ''}",
        commands=[f"git branch {flag} {branch}"],
        risk_level="moderate" if force else "safe",
        warning="Force delete (-D) removes the branch even if it has unmerged changes!" if force else "",
    )


# ═══════════════════════════════════════════════════════════════
# PUSH/REMOTE RECOVERY
# ═══════════════════════════════════════════════════════════════
def undo_pushed_commit(cwd: str = ".") -> RecoveryAction:
    """Revert a pushed commit (safe, creates new commit)."""
    last_hash = _run_git(["log", "-1", "--format=%H"], cwd=cwd) or "<commit-hash>"
    return RecoveryAction(
        title="Revert a Pushed Commit",
        description="Creates a NEW commit that undoes the changes. Safe for shared branches.",
        commands=[
            "# Revert the last commit:",
            "git revert HEAD",
            "",
            "# Revert a specific commit:",
            f"git revert {last_hash[:8]}",
            "",
            "# Then push the revert:",
            "git push origin",
        ],
        risk_level="safe",
    )


def force_push_recovery() -> RecoveryAction:
    """Recovery from an accidental force push."""
    return RecoveryAction(
        title="Recover From Force Push",
        description="Restore a branch after accidental force push using reflog.",
        commands=[
            "# Find the commit before the force push:",
            "git reflog",
            "",
            "# Reset to the desired commit:",
            "git reset --hard <commit-hash-from-reflog>",
            "",
            "# Force push to restore remote:",
            "git push --force origin <branch>",
        ],
        risk_level="dangerous",
        warning="⚠️ Coordinate with your team before force pushing to shared branches.",
    )


# ═══════════════════════════════════════════════════════════════
# SECRET LEAK RECOVERY
# ═══════════════════════════════════════════════════════════════
def recover_secret_leak(secret_file: str = ".env") -> RecoveryAction:
    """Complete recovery guide for leaked secrets."""
    return RecoveryAction(
        title=f"EMERGENCY: Secret Leak Recovery ({secret_file})",
        description="Step-by-step guide to recover from accidentally pushing secrets to Git.",
        commands=[
            "# ═══ STEP 1: Remove from tracking ═══",
            f"git rm --cached {secret_file}",
            f"echo '{secret_file}' >> .gitignore",
            "git add .gitignore",
            f"git commit -m 'chore: remove {secret_file} and update .gitignore'",
            "",
            "# ═══ STEP 2: Remove from history ═══",
            "# Using git filter-branch:",
            "git filter-branch --force --index-filter \\",
            f"  'git rm --cached --ignore-unmatch {secret_file}' \\",
            "  --prune-empty --tag-name-filter cat -- --all",
            "",
            "# Force push cleaned history:",
            "git push origin --force --all",
            "",
            "# ═══ STEP 3: Rotate ALL credentials ═══",
            "# - Change all API keys",
            "# - Change all passwords",
            "# - Regenerate all tokens",
            "# - Revoke old keys/tokens",
            "",
            "# ═══ STEP 4: Notify team ═══",
            "# - All collaborators must re-clone",
            "# - Document the incident",
        ],
        risk_level="dangerous",
        warning="⚠️ CRITICAL: Rotate ALL exposed credentials immediately. "
                "GitHub bots scan for secrets and can exploit them within minutes.",
    )


# ═══════════════════════════════════════════════════════════════
# RECOVERY WIZARD
# ═══════════════════════════════════════════════════════════════
def get_recovery_options() -> List[Dict]:
    """Get all available recovery options for the interactive wizard."""
    return [
        {"id": "undo_soft", "label": "Undo last commit (keep changes staged)", "category": "Undo"},
        {"id": "undo_mixed", "label": "Undo last commit (unstage changes)", "category": "Undo"},
        {"id": "undo_hard", "label": "Undo last commit (DELETE changes)", "category": "Undo"},
        {"id": "amend", "label": "Fix/amend last commit message", "category": "Undo"},
        {"id": "revert_pushed", "label": "Revert a pushed commit", "category": "Undo"},
        {"id": "unstage_all", "label": "Unstage all files", "category": "Files"},
        {"id": "discard_all", "label": "Discard all uncommitted changes", "category": "Files"},
        {"id": "remove_history", "label": "Remove a file from Git history", "category": "Files"},
        {"id": "detached_head", "label": "Fix detached HEAD", "category": "Branch"},
        {"id": "diverged", "label": "Fix diverged branch", "category": "Branch"},
        {"id": "force_push", "label": "Recover from force push", "category": "Branch"},
        {"id": "secret_leak", "label": "EMERGENCY: Secret was pushed!", "category": "Security"},
    ]


def execute_recovery(recovery_id: str, **kwargs) -> Optional[RecoveryAction]:
    """Execute a recovery action by ID."""
    actions = {
        "undo_soft": lambda: undo_last_commit("soft"),
        "undo_mixed": lambda: undo_last_commit("mixed"),
        "undo_hard": lambda: undo_last_commit("hard"),
        "amend": lambda: amend_last_commit(),
        "revert_pushed": lambda: undo_pushed_commit(kwargs.get("cwd", ".")),
        "unstage_all": lambda: unstage_file(),
        "discard_all": lambda: discard_changes(),
        "remove_history": lambda: remove_file_from_history(kwargs.get("filename", "<filename>")),
        "detached_head": lambda: recover_detached_head(),
        "diverged": lambda: fix_diverged_branch(kwargs.get("branch", "main")),
        "force_push": lambda: force_push_recovery(),
        "secret_leak": lambda: recover_secret_leak(kwargs.get("filename", ".env")),
    }

    factory = actions.get(recovery_id)
    return factory() if factory else None
