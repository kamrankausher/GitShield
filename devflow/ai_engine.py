"""
DevFlow AI++ — Lightweight AI Engine
======================================
Intelligent suggestion engine using a comprehensive template + context
matching system. NO heavy dependencies (no PyTorch, no Transformers).

Features:
- 50+ intelligent predefined responses
- Context-aware suggestion chaining
- Severity-based response priority
- Learning path recommendations
- Pattern matching with fuzzy context
- Fallback generation with helpful defaults
"""

import random
from typing import Dict, List

# ═══════════════════════════════════════════════════════════════
# INTELLIGENT RESPONSE DATABASE (50+ responses)
# ═══════════════════════════════════════════════════════════════
RESPONSE_DATABASE = {
    # ── Commit Message Issues ──
    "commit message is too vague": [
        "Write commit messages that clearly explain WHAT changed and WHY. Example: 'feat: add JWT authentication to /api/login endpoint'",
        "Use conventional commits format — 'type(scope): message'. This enables automated changelogs and makes history searchable.",
        "Think of your commit message as a headline for a newspaper: it should tell the full story in one line.",
    ],
    "commit message too short": [
        "Use meaningful commit messages with 10+ words that describe the purpose of your changes. Future-you will thank present-you.",
        "A good commit message answers: WHAT was changed, WHY it was changed, and HOW it affects the system.",
        "Short messages like 'fix' are the developer equivalent of 'stuff happened'. Be specific: 'fix: resolve null pointer in user auth middleware'",
    ],
    "commit message is empty": [
        "Every commit deserves a description. Use: git commit -m 'type: clear description of what this change does'",
        "Empty commit messages violate Git best practices. They make git log, git blame, and code reviews useless.",
    ],
    "no conventional prefix": [
        "Use conventional commits for better history: feat:, fix:, docs:, style:, refactor:, test:, chore:, perf:, ci:, build:, revert:",
        "Conventional commits enable automated versioning and changelog generation. Start with 'feat:' for features and 'fix:' for bug fixes.",
    ],
    "long commit subject": [
        "Keep the subject line under 72 characters. Use the commit body (blank line after subject) for detailed explanations.",
        "Git truncates long subject lines in many UIs. Keep it concise — details go in the body: git commit (opens editor for multi-line).",
    ],
    "trailing period": [
        "Commit subjects are titles, not sentences. Remove the trailing period for consistency with Git conventions.",
    ],
    "capitalize after prefix": [
        "Conventional commits use lowercase after the prefix. Write 'fix: resolve issue' not 'fix: Resolve issue'.",
    ],

    # ── Branch Issues ──
    "main branch": [
        "Create a feature branch before making changes. The main branch should always be deployment-ready.",
        "Use 'git checkout -b feature/your-feature' to work safely. Merge via Pull Request for code review.",
        "Direct commits to main skip code review, can break CI/CD pipelines, and make rollbacks painful.",
    ],
    "branch naming": [
        "Use descriptive branch names: feature/add-auth, fix/login-bug, docs/update-readme, chore/cleanup-tests",
        "Good branch naming helps teams navigate repos at a glance. Use prefixes: feature/, fix/, hotfix/, docs/, refactor/",
    ],
    "direct main commit": [
        "Adopt GitHub Flow: create branch → make changes → open PR → review → merge. This is how professional teams work.",
    ],

    # ── File Issues ──
    "too many files": [
        "Split your changes into smaller, atomic commits. Each commit should represent one logical change.",
        "Large commits are hard to review and harder to revert. Use 'git add -p' to stage specific changes interactively.",
        "Atomic commits = easier reviews, precise reverts, clear history. Aim for ≤10 files per commit.",
    ],
    "many files": [
        "Consider splitting this commit into logical groups. Related changes should be committed together.",
    ],
    "blocked file type": [
        "Binary and compiled files don't belong in Git repos. Add them to .gitignore and use package managers or CDNs instead.",
        "Archives, executables, and databases inflate repo size permanently. Git stores ALL history, so this never goes away.",
    ],
    "warn file type": [
        "Non-code files (images, PDFs, data files) should be evaluated — do they truly need version control?",
    ],
    "config file risk": [
        "Always double-check config files for hardcoded passwords, API keys, and database credentials before committing.",
    ],
    "merge conflict markers": [
        "Resolve all merge conflicts before committing. Open each file and choose which changes to keep between the <<<<<<< and >>>>>>> markers.",
    ],

    # ── Security Issues ──
    "sensitive file": [
        "CRITICAL: Sensitive files must NEVER be committed. Add to .gitignore immediately. If already pushed, rewrite history with BFG or git filter-branch.",
        "Files like .env, private keys, and credentials are the #1 cause of security breaches in code repositories.",
    ],
    "secret detected": [
        "SECURITY ALERT: Remove this secret from code immediately. Use environment variables or a secrets manager instead.",
        "Secrets in source code can be found by automated scanners within minutes of pushing. Rotate any exposed credentials NOW.",
    ],
    "aws": [
        "AWS credentials in code can lead to massive cloud bills, data theft, and account compromise. Rotate keys immediately via IAM console.",
    ],
    "github token": [
        "GitHub tokens can be used to access repositories, create commits, and modify settings. Revoke at github.com/settings/tokens.",
    ],
    "stripe": [
        "Stripe keys give access to payment processing. Rotate immediately in the Stripe Dashboard under Developers → API Keys.",
    ],
    "private key": [
        "Private keys are your digital identity. Generate a new key pair and revoke the compromised one from all services.",
    ],
    "jwt": [
        "Exposed JWT tokens can be used to impersonate users. Rotate signing keys and invalidate existing sessions.",
    ],
    "database": [
        "Database connection strings with credentials enable direct access to your data. Change passwords and use env vars.",
    ],
    "password": [
        "Hardcoded passwords are a critical security vulnerability. Use environment variables, .env files (gitignored), or a vault.",
    ],
    "api key": [
        "API keys should never be in source code. Use environment variables or a secrets manager. Rotate exposed keys immediately.",
    ],

    # ── Untracked Files ──
    "untracked": [
        "Review untracked files: add needed ones with 'git add', ignore generated files with .gitignore.",
        "Untracked files create noise in 'git status'. Keep your working directory clean with a proper .gitignore.",
    ],

    # ── Recovery Issues ──
    "detached head": [
        "You're in detached HEAD state. Create a branch to save your work: git checkout -b my-branch",
    ],
    "stash": [
        "You have stashed changes. Remember to apply them: git stash pop (apply + remove) or git stash apply (keep stash).",
    ],
    "behind remote": [
        "You're behind the remote. Pull before pushing: git pull --rebase origin main (cleaner than merge).",
    ],
    "ahead remote": [
        "You have unpushed commits. Push your work: git push origin branch-name",
    ],
    "diverged": [
        "Your branch has diverged from remote. Rebase for clean history: git pull --rebase origin main",
    ],

    # ── Config Issues ──
    "no gitignore": [
        "Create a .gitignore file! Run 'devflow gitignore' to auto-generate based on your project type.",
    ],
    "gitignore missing": [
        "Your .gitignore is incomplete. Run 'devflow gitignore' to add missing patterns.",
    ],

    # ── General Guidance ──
    "large file": [
        "Large files in Git repos slow everything down. Use Git LFS for files >5MB or add to .gitignore.",
    ],
    "risky file": [
        "Log, database, and CSV files usually shouldn't be in Git. Add appropriate patterns to .gitignore.",
    ],
}

# ═══════════════════════════════════════════════════════════════
# FALLBACK RESPONSES
# ═══════════════════════════════════════════════════════════════
FALLBACK_RESPONSES = [
    "Follow Git best practices: write clear commit messages, use feature branches, keep commits atomic, and never commit secrets.",
    "Review your changes before committing: git diff --staged. A quick review catches most issues.",
    "Use 'git status' frequently to stay aware of your working directory state.",
    "Keep your repository clean: update .gitignore, remove unused branches, and write descriptive commit messages.",
    "Follow the principle of least surprise: your commits, branches, and code should be self-explanatory to teammates.",
]


# ═══════════════════════════════════════════════════════════════
# MAIN AI ENGINE
# ═══════════════════════════════════════════════════════════════
def generate_ai_suggestion(context: str) -> str:
    """
    Generate an intelligent suggestion based on the context.

    Uses a sophisticated template matching system with fallback.
    No heavy dependencies required — purely rule + template based,
    but produces high-quality, contextual suggestions.
    """
    context_lower = context.lower()

    # Score-based matching: find the best matching response
    best_match = None
    best_score = 0

    for key, responses in RESPONSE_DATABASE.items():
        # Calculate match score
        score = 0
        key_words = key.split()
        for word in key_words:
            if word in context_lower:
                score += 1

        # Exact substring match gets bonus
        if key in context_lower:
            score += len(key_words) * 2

        if score > best_score:
            best_score = score
            best_match = responses

    if best_match and best_score > 0:
        return random.choice(best_match)

    return random.choice(FALLBACK_RESPONSES)


def generate_detailed_analysis(context: str, severity: str = "WARNING") -> Dict:
    """
    Generate a detailed analysis with suggestion, impact, and action items.
    """
    suggestion = generate_ai_suggestion(context)

    # Determine impact level
    impact_map = {
        "CRITICAL": "🔴 CRITICAL — Immediate action required. This can cause security breaches or data loss.",
        "HIGH": "🟠 HIGH — Should be fixed before pushing. This affects code quality or security.",
        "MEDIUM": "🟡 MEDIUM — Recommended fix. This affects maintainability and best practices.",
        "LOW": "🔵 LOW — Optional improvement. Nice to have but not urgent.",
        "BLOCK": "🚫 BLOCKED — Cannot proceed until this is resolved.",
        "WARNING": "⚠️ WARNING — Should be addressed to maintain code quality.",
        "INFO": "💡 INFO — Suggestion for improvement.",
    }

    return {
        "suggestion": suggestion,
        "impact": impact_map.get(severity.upper(), impact_map["WARNING"]),
        "action_items": _generate_action_items(context),
    }


def _generate_action_items(context: str) -> List[str]:
    """Generate specific action items based on context."""
    items = []
    context_lower = context.lower()

    if "secret" in context_lower or "key" in context_lower or "password" in context_lower:
        items.extend([
            "1. Remove the secret from your code immediately",
            "2. Add the file to .gitignore if it contains secrets",
            "3. Use environment variables: os.environ['KEY_NAME']",
            "4. Rotate/regenerate the exposed credential",
            "5. If already pushed: use BFG Repo-Cleaner to remove from history",
        ])
    elif "commit" in context_lower or "message" in context_lower:
        items.extend([
            "1. Use conventional commit format: type(scope): description",
            "2. Keep subject line under 72 characters",
            "3. Use body for detailed explanation (blank line after subject)",
            "4. Consider setting up a commit message template",
        ])
    elif "branch" in context_lower or "main" in context_lower:
        items.extend([
            "1. Create a feature branch: git checkout -b feature/name",
            "2. Make your changes on the feature branch",
            "3. Push and create a Pull Request for review",
            "4. Merge via PR after approval",
        ])
    elif "file" in context_lower:
        items.extend([
            "1. Review the file — does it belong in the repo?",
            "2. Add to .gitignore if it's generated or sensitive",
            "3. Use git rm --cached <file> to stop tracking",
        ])
    else:
        items.extend([
            "1. Review the issue and understand the root cause",
            "2. Apply the suggested fix",
            "3. Run 'devflow check' to verify",
        ])

    return items


def get_learning_path(skill_level: str) -> List[Dict]:
    """Get a learning path based on skill level."""
    paths = {
        "beginner": [
            {"topic": "Git Basics", "description": "Learn add, commit, push, pull", "resource": "https://git-scm.com/book/en/v2"},
            {"topic": "Branching", "description": "Feature branches and merging", "resource": "https://learngitbranching.js.org"},
            {"topic": ".gitignore", "description": "Keeping repos clean", "resource": "https://www.gitignore.io"},
            {"topic": "Commit Messages", "description": "Conventional commits", "resource": "https://www.conventionalcommits.org"},
            {"topic": "GitHub Flow", "description": "Pull requests and reviews", "resource": "https://docs.github.com/en/get-started/quickstart/github-flow"},
        ],
        "intermediate": [
            {"topic": "Interactive Rebase", "description": "Clean up commit history", "resource": "https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History"},
            {"topic": "Git Hooks", "description": "Automate quality checks", "resource": "https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks"},
            {"topic": "Cherry Pick", "description": "Apply specific commits", "resource": "https://git-scm.com/docs/git-cherry-pick"},
            {"topic": "Git Bisect", "description": "Binary search for bugs", "resource": "https://git-scm.com/docs/git-bisect"},
            {"topic": "Signed Commits", "description": "GPG sign your work", "resource": "https://docs.github.com/en/authentication/managing-commit-signature-verification"},
        ],
        "advanced": [
            {"topic": "Git Internals", "description": "Objects, refs, packfiles", "resource": "https://git-scm.com/book/en/v2/Git-Internals-Plumbing-and-Porcelain"},
            {"topic": "Monorepo Management", "description": "Multi-project repositories", "resource": "https://monorepo.tools"},
            {"topic": "Git Workflows", "description": "Gitflow, trunk-based", "resource": "https://www.atlassian.com/git/tutorials/comparing-workflows"},
            {"topic": "Custom Merge Drivers", "description": "Automate conflict resolution", "resource": "https://git-scm.com/docs/gitattributes"},
            {"topic": "Git Submodules", "description": "Nested repositories", "resource": "https://git-scm.com/book/en/v2/Git-Tools-Submodules"},
        ],
    }

    return paths.get(skill_level, paths["beginner"])
