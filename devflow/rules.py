"""
DevFlow AI++ — Rule Engine Module
==================================
Comprehensive rule-based analysis for Git commits, branches, files,
and developer workflow patterns.

Features:
- Commit message quality analysis (conventional commits)
- Branch naming convention checks
- File type rules (block dangerous files)
- Merge conflict detection
- .gitignore completeness checking
- Staged file analysis with severity levels
"""

import os
import re
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple


class RuleSeverity(Enum):
    BLOCK = "BLOCK"       # ❌ Must fix before commit
    WARNING = "WARNING"   # ⚠️ Should fix
    INFO = "INFO"         # 💡 Suggestion

    @property
    def icon(self):
        return {"BLOCK": "❌", "WARNING": "⚠️", "INFO": "💡"}[self.value]


@dataclass
class RuleResult:
    """A single rule evaluation result."""
    rule_name: str
    severity: RuleSeverity
    message: str
    suggestion: str = ""
    category: str = "general"

    def __str__(self):
        return f"{self.severity.icon} [{self.severity.value}] {self.message}"


# ═══════════════════════════════════════════════════════════════
# COMMIT MESSAGE ANALYSIS
# ═══════════════════════════════════════════════════════════════
CONVENTIONAL_PREFIXES = [
    "feat", "fix", "docs", "style", "refactor", "perf",
    "test", "build", "ci", "chore", "revert",
]

VAGUE_COMMIT_WORDS = {
    "update", "fix", "changes", "done", "wip", "stuff",
    "misc", "test", "temp", "tmp", "asdf", "asd",
    "commit", "push", "save", "edited", "modified",
    "initial", "first", "new", "add", "added",
}

BAD_COMMIT_PATTERNS = [
    (r'^\.+$', "Commit message is just dots"),
    (r'^[\s]*$', "Commit message is empty"),
    (r'^[a-f0-9]{7,40}$', "Commit message looks like a hash"),
    (r'^(test|testing|asdf|foo|bar)\s*$', "Commit message is a test placeholder"),
]


def analyze_commit_message(message: str) -> List[RuleResult]:
    """Analyze a commit message for quality and best practices."""
    results = []
    msg = message.strip()

    if not msg:
        results.append(RuleResult(
            rule_name="empty_commit_message",
            severity=RuleSeverity.BLOCK,
            message="Commit message is empty",
            suggestion="Write a descriptive message: git commit -m 'feat: add user authentication'",
            category="commit",
        ))
        return results

    # Length checks
    if len(msg) < 5:
        results.append(RuleResult(
            rule_name="short_commit_message",
            severity=RuleSeverity.WARNING,
            message=f"Commit message too short ({len(msg)} chars, recommended 10+)",
            suggestion="Use descriptive messages: 'fix: resolve login redirect bug on mobile'",
            category="commit",
        ))

    if len(msg) > 72:
        results.append(RuleResult(
            rule_name="long_commit_subject",
            severity=RuleSeverity.INFO,
            message=f"Commit subject line too long ({len(msg)} chars, max 72 recommended)",
            suggestion="Keep subject ≤72 chars, use body for details",
            category="commit",
        ))

    # Vague message check
    msg_lower = msg.lower().strip()
    if msg_lower in VAGUE_COMMIT_WORDS:
        results.append(RuleResult(
            rule_name="vague_commit_message",
            severity=RuleSeverity.WARNING,
            message=f"Commit message '{msg}' is too vague",
            suggestion="Describe WHAT changed and WHY: 'fix: handle null user in auth middleware'",
            category="commit",
        ))

    # Pattern checks
    for pattern, desc in BAD_COMMIT_PATTERNS:
        if re.match(pattern, msg, re.IGNORECASE):
            results.append(RuleResult(
                rule_name="bad_commit_pattern",
                severity=RuleSeverity.WARNING,
                message=desc,
                suggestion="Use conventional commits: 'feat:', 'fix:', 'docs:', etc.",
                category="commit",
            ))

    # Conventional commit suggestion
    has_prefix = any(msg_lower.startswith(f"{p}:") or msg_lower.startswith(f"{p}(") for p in CONVENTIONAL_PREFIXES)
    if not has_prefix and len(msg) >= 5:
        results.append(RuleResult(
            rule_name="no_conventional_prefix",
            severity=RuleSeverity.INFO,
            message="Consider using conventional commit format",
            suggestion="Examples: 'feat: ...', 'fix: ...', 'docs: ...', 'refactor: ...'",
            category="commit",
        ))

    # Capitalization
    first_char = msg[0] if msg else ""
    if first_char.isupper() and not has_prefix:
        pass  # OK - natural language
    elif has_prefix:
        # Check message after prefix
        parts = msg.split(":", 1)
        if len(parts) > 1:
            after_prefix = parts[1].strip()
            if after_prefix and after_prefix[0].isupper():
                results.append(RuleResult(
                    rule_name="capitalize_after_prefix",
                    severity=RuleSeverity.INFO,
                    message="Conventional commits use lowercase after prefix",
                    suggestion="Use 'fix: resolve issue' instead of 'fix: Resolve issue'",
                    category="commit",
                ))

    # No period at end
    if msg.endswith("."):
        results.append(RuleResult(
            rule_name="trailing_period",
            severity=RuleSeverity.INFO,
            message="Commit subject should not end with a period",
            suggestion="Remove the trailing period from the commit message",
            category="commit",
        ))

    return results


# ═══════════════════════════════════════════════════════════════
# STAGED FILES ANALYSIS
# ═══════════════════════════════════════════════════════════════
BLOCKED_EXTENSIONS = {
    ".exe", ".dll", ".so", ".dylib",  # Binaries
    ".zip", ".tar", ".gz", ".rar", ".7z",  # Archives
    ".log",  # Logs
    ".sqlite", ".db",  # Databases
    ".mp4", ".avi", ".mov", ".mkv",  # Videos
    ".iso", ".dmg", ".img",  # Disk images
}

WARN_EXTENSIONS = {
    ".csv", ".tsv",  # Data files
    ".pdf", ".doc", ".docx",  # Documents
    ".jpg", ".jpeg", ".png", ".gif", ".bmp",  # Images (unless needed)
    ".mp3", ".wav", ".flac",  # Audio
}


def analyze_staged_files(file_list: List[str]) -> List[RuleResult]:
    """Analyze staged files for potential issues."""
    results = []

    if not file_list:
        return results

    # Too many files
    if len(file_list) > 15:
        results.append(RuleResult(
            rule_name="too_many_files",
            severity=RuleSeverity.WARNING,
            message=f"Too many files in one commit ({len(file_list)} files)",
            suggestion="Split into smaller, logical commits for better review and history",
            category="files",
        ))
    elif len(file_list) > 8:
        results.append(RuleResult(
            rule_name="many_files",
            severity=RuleSeverity.INFO,
            message=f"Large commit with {len(file_list)} files — consider splitting",
            suggestion="Group related changes into separate commits",
            category="files",
        ))

    # Check each file
    for filepath in file_list:
        _, ext = os.path.splitext(filepath)
        ext_lower = ext.lower()
        basename = os.path.basename(filepath)

        # Blocked extensions
        if ext_lower in BLOCKED_EXTENSIONS:
            results.append(RuleResult(
                rule_name="blocked_file_type",
                severity=RuleSeverity.BLOCK,
                message=f"Dangerous file type: {basename}",
                suggestion=f"Add *{ext_lower} to .gitignore — these files don't belong in repos",
                category="files",
            ))

        # Warning extensions
        elif ext_lower in WARN_EXTENSIONS:
            results.append(RuleResult(
                rule_name="warn_file_type",
                severity=RuleSeverity.INFO,
                message=f"Non-code file staged: {basename}",
                suggestion=f"Consider if {ext_lower} files belong in this repo",
                category="files",
            ))

        # Lock files
        if basename in {"package-lock.json", "yarn.lock", "Pipfile.lock", "poetry.lock"}:
            # Lock files are usually OK, but warn if it's a massive change
            pass

        # Config with secrets risk
        if basename in {"config.json", "settings.json", "config.yml", "config.yaml"}:
            results.append(RuleResult(
                rule_name="config_file_risk",
                severity=RuleSeverity.INFO,
                message=f"Config file staged: {basename} — verify no secrets inside",
                suggestion="Double-check config files don't contain passwords or API keys",
                category="files",
            ))

    # Check for merge conflict markers
    for filepath in file_list:
        if _has_merge_conflicts(filepath):
            results.append(RuleResult(
                rule_name="merge_conflict_markers",
                severity=RuleSeverity.BLOCK,
                message=f"Merge conflict markers found in {os.path.basename(filepath)}",
                suggestion="Resolve all <<<<<<< / ======= / >>>>>>> markers before committing",
                category="files",
            ))

    return results


def _has_merge_conflicts(filepath: str) -> bool:
    """Check if a file contains merge conflict markers."""
    try:
        with open(filepath, "r", errors="ignore") as f:
            content = f.read()
        return bool(re.search(r'^[<>=]{7}', content, re.MULTILINE))
    except (OSError, PermissionError):
        return False


# ═══════════════════════════════════════════════════════════════
# BRANCH ANALYSIS
# ═══════════════════════════════════════════════════════════════
GOOD_BRANCH_PATTERNS = [
    r'^(feature|feat|fix|bugfix|hotfix|release|chore|docs|refactor|test|ci)/[\w\-]+$',
    r'^(dev|develop|staging|main|master)$',
]


def analyze_branch_name(branch_name: str) -> List[RuleResult]:
    """Analyze branch naming conventions."""
    results = []

    if not branch_name:
        return results

    # Direct commit to main/master
    if branch_name in ("main", "master"):
        results.append(RuleResult(
            rule_name="direct_main_commit",
            severity=RuleSeverity.WARNING,
            message=f"Committing directly to '{branch_name}' branch",
            suggestion=f"Create a feature branch: git checkout -b feature/your-feature",
            category="branch",
        ))
        return results

    # Check naming conventions
    is_good = any(re.match(p, branch_name) for p in GOOD_BRANCH_PATTERNS)
    if not is_good:
        results.append(RuleResult(
            rule_name="branch_naming",
            severity=RuleSeverity.INFO,
            message=f"Branch '{branch_name}' doesn't follow conventions",
            suggestion="Use format: feature/description, fix/issue-name, docs/update-readme",
            category="branch",
        ))

    # Check for spaces or special chars
    if " " in branch_name or any(c in branch_name for c in "~^:?*[\\"):
        results.append(RuleResult(
            rule_name="branch_bad_chars",
            severity=RuleSeverity.BLOCK,
            message=f"Branch name contains invalid characters",
            suggestion="Use lowercase, hyphens, and slashes only: feature/my-feature",
            category="branch",
        ))

    return results


# ═══════════════════════════════════════════════════════════════
# GITIGNORE ANALYSIS
# ═══════════════════════════════════════════════════════════════
def check_gitignore_exists(repo_path: str = ".") -> List[RuleResult]:
    """Check if .gitignore exists and is adequate."""
    results = []
    gitignore_path = os.path.join(repo_path, ".gitignore")

    if not os.path.exists(gitignore_path):
        results.append(RuleResult(
            rule_name="no_gitignore",
            severity=RuleSeverity.WARNING,
            message="No .gitignore file found",
            suggestion="Run 'devflow gitignore' to generate one automatically",
            category="config",
        ))
    else:
        try:
            with open(gitignore_path, "r") as f:
                content = f.read()

            # Check for common missing entries
            essential_patterns = {
                ".env": "Environment files with secrets",
                "__pycache__": "Python bytecode cache",
                "node_modules": "Node.js dependencies",
                "*.pyc": "Python compiled files",
                "venv": "Virtual environments",
            }

            for pattern, desc in essential_patterns.items():
                if pattern not in content:
                    # Check if a project type makes this relevant
                    results.append(RuleResult(
                        rule_name="gitignore_missing_pattern",
                        severity=RuleSeverity.INFO,
                        message=f".gitignore might be missing '{pattern}' ({desc})",
                        suggestion=f"Add '{pattern}' to your .gitignore",
                        category="config",
                    ))

        except OSError:
            pass

    return results


# ═══════════════════════════════════════════════════════════════
# AGGREGATE ANALYSIS
# ═══════════════════════════════════════════════════════════════
def run_all_rules(
    commit_message: str = "",
    staged_files: Optional[List[str]] = None,
    branch_name: str = "",
    repo_path: str = ".",
) -> List[RuleResult]:
    """Run all rules and return aggregated results."""
    results = []

    if commit_message:
        results.extend(analyze_commit_message(commit_message))

    if staged_files:
        results.extend(analyze_staged_files(staged_files))

    if branch_name:
        results.extend(analyze_branch_name(branch_name))

    results.extend(check_gitignore_exists(repo_path))

    # Sort: BLOCK first, then WARNING, then INFO
    severity_order = {"BLOCK": 0, "WARNING": 1, "INFO": 2}
    results.sort(key=lambda r: severity_order.get(r.severity.value, 3))

    return results


def has_blocking_issues(results: List[RuleResult]) -> bool:
    """Check if any results are blocking."""
    return any(r.severity == RuleSeverity.BLOCK for r in results)