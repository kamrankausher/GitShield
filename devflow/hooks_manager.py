"""
GitShield — Git Hooks Manager
================================
Installs, uninstalls, and manages Git hooks for the GitShield system.
Supports cross-platform hooks (Windows Git Bash + Unix).
"""

import os
import stat
import subprocess
from typing import Dict, List, Optional

PRE_COMMIT_HOOK = '''#!/bin/sh
#
# GitShield Pre-Commit Hook
# ==========================
# Automatically analyzes commits before they happen.
# Blocks dangerous commits, warns about issues, and provides guidance.
#
# To bypass (NOT recommended): git commit --no-verify
#

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   🛡️  GitShield Pre-Commit Check      ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Check if gitshield is available
if command -v gitshield &> /dev/null; then
    gitshield check --hook
    exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo ""
        echo "❌ Commit BLOCKED by GitShield"
        echo "   Fix the issues above or use: git commit --no-verify"
        echo ""
        exit 1
    fi
elif command -v python &> /dev/null; then
    python -m devflow.cli check --hook
    exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo ""
        echo "❌ Commit BLOCKED by GitShield"
        echo "   Fix the issues above or use: git commit --no-verify"
        echo ""
        exit 1
    fi
else
    echo "⚠️  GitShield not found. Run: pip install -e ."
fi

echo "✅ GitShield pre-commit check passed"
echo ""
exit 0
'''

PRE_PUSH_HOOK = '''#!/bin/sh
#
# GitShield Pre-Push Hook
# ========================
# Runs security scan before pushing to remote.
# Blocks pushes containing secrets or sensitive files.
#

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   🔒 GitShield Pre-Push Scan          ║"
echo "╚══════════════════════════════════════╝"
echo ""

if command -v gitshield &> /dev/null; then
    gitshield scan --strict
    exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo ""
        echo "❌ Push BLOCKED by GitShield"
        echo "   Security issues detected! Fix before pushing."
        echo "   To bypass (DANGEROUS): git push --no-verify"
        echo ""
        exit 1
    fi
elif command -v python &> /dev/null; then
    python -m devflow.cli scan --strict
    exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo ""
        echo "❌ Push BLOCKED by GitShield"
        echo ""
        exit 1
    fi
else
    echo "⚠️  GitShield not found. Run: pip install -e ."
fi

echo "✅ GitShield security scan passed"
echo ""
exit 0
'''

COMMIT_MSG_HOOK = '''#!/bin/sh
#
# GitShield Commit Message Hook
# ===============================
# Analyzes commit message quality.
#

COMMIT_MSG_FILE=$1
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

if command -v gitshield &> /dev/null; then
    echo "$COMMIT_MSG" | gitshield check-msg
elif command -v python &> /dev/null; then
    echo "$COMMIT_MSG" | python -m devflow.cli check-msg
fi

exit 0
'''

HOOKS = {
    "pre-commit": PRE_COMMIT_HOOK,
    "pre-push": PRE_PUSH_HOOK,
    "commit-msg": COMMIT_MSG_HOOK,
}

# Detection keywords for identifying our hooks
_HOOK_MARKERS = ("GitShield", "DevFlow")


def get_hooks_dir(repo_path: str = ".") -> Optional[str]:
    """Get the Git hooks directory path."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True, text=True, cwd=repo_path, timeout=5,
            encoding="utf-8", errors="replace",
            stdin=subprocess.DEVNULL,
        )
        if result.returncode == 0:
            git_dir = result.stdout.strip()
            if not os.path.isabs(git_dir):
                git_dir = os.path.join(repo_path, git_dir)
            return os.path.join(git_dir, "hooks")
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass
    return None


def _is_our_hook(content: str) -> bool:
    """Check if hook content belongs to GitShield (or legacy DevFlow)."""
    return any(marker in content for marker in _HOOK_MARKERS)


def install_hooks(repo_path: str = ".", hooks: Optional[List[str]] = None) -> Dict[str, str]:
    """Install GitShield Git hooks. Returns status for each hook."""
    hooks_dir = get_hooks_dir(repo_path)
    if not hooks_dir:
        return {"error": "Not a Git repository or Git not found"}

    os.makedirs(hooks_dir, exist_ok=True)
    results = {}
    hooks_to_install = hooks or list(HOOKS.keys())

    for hook_name in hooks_to_install:
        if hook_name not in HOOKS:
            results[hook_name] = "unknown hook"
            continue

        hook_path = os.path.join(hooks_dir, hook_name)

        # Backup existing hook
        if os.path.exists(hook_path):
            backup_path = hook_path + ".backup"
            try:
                with open(hook_path, encoding="utf-8", errors="replace") as f:
                    content = f.read()
                if not _is_our_hook(content):
                    os.rename(hook_path, backup_path)
                    results[hook_name + "_backup"] = f"Existing hook backed up to {backup_path}"
            except OSError:
                pass

        # Write hook
        try:
            with open(hook_path, "w", newline="\n", encoding="utf-8") as f:
                f.write(HOOKS[hook_name])
            # Make executable
            os.chmod(hook_path, os.stat(hook_path).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
            results[hook_name] = "installed"
        except OSError as e:
            results[hook_name] = f"error: {e}"

    return results


def uninstall_hooks(repo_path: str = ".", hooks: Optional[List[str]] = None) -> Dict[str, str]:
    """Uninstall GitShield Git hooks."""
    hooks_dir = get_hooks_dir(repo_path)
    if not hooks_dir:
        return {"error": "Not a Git repository"}

    results = {}
    hooks_to_remove = hooks or list(HOOKS.keys())

    for hook_name in hooks_to_remove:
        hook_path = os.path.join(hooks_dir, hook_name)
        if os.path.exists(hook_path):
            try:
                with open(hook_path, encoding="utf-8", errors="replace") as f:
                    content = f.read()
                if _is_our_hook(content):
                    os.remove(hook_path)
                    backup = hook_path + ".backup"
                    if os.path.exists(backup):
                        os.rename(backup, hook_path)
                        results[hook_name] = "removed (backup restored)"
                    else:
                        results[hook_name] = "removed"
                else:
                    results[hook_name] = "skipped (not a GitShield hook)"
            except OSError as e:
                results[hook_name] = f"error: {e}"
        else:
            results[hook_name] = "not found"

    return results


def get_hook_status(repo_path: str = ".") -> Dict[str, str]:
    """Check the status of all GitShield hooks."""
    hooks_dir = get_hooks_dir(repo_path)
    if not hooks_dir:
        return {"error": "Not a Git repository"}

    status = {}
    for hook_name in HOOKS:
        hook_path = os.path.join(hooks_dir, hook_name)
        if os.path.exists(hook_path):
            try:
                with open(hook_path, encoding="utf-8", errors="replace") as f:
                    content = f.read()
                if _is_our_hook(content):
                    status[hook_name] = "active"
                else:
                    status[hook_name] = "exists (not GitShield)"
            except OSError:
                status[hook_name] = "exists (unreadable)"
        else:
            status[hook_name] = "not installed"

    return status
