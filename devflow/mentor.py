"""
DevFlow AI++ — AI Mentor Module
=================================
Contextual guidance engine that provides explanations, suggestions,
learning resources, and progressive tips based on developer skill level.

Features:
- 30+ contextual explanations for common issues
- Learning resources with links
- Progressive tips based on behavior patterns
- Command suggestions with examples
- Context-aware guidance chains
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class MentorAdvice:
    """A structured piece of mentor advice."""
    suggestion: str
    why: str
    command: str = ""
    learn_more: str = ""
    skill_level: str = "beginner"  # beginner, intermediate, advanced


# ═══════════════════════════════════════════════════════════════
# COMPREHENSIVE EXPLANATION DATABASE
# ═══════════════════════════════════════════════════════════════
EXPLANATIONS: Dict[str, MentorAdvice] = {
    # ── Commit Messages ──
    "commit message too short": MentorAdvice(
        suggestion="Write descriptive commit messages with 10+ words",
        why="Good commit messages serve as documentation. They help teammates understand changes and make debugging easier when using git log or git blame.",
        command="git commit -m 'feat: add user authentication with JWT tokens'",
        learn_more="https://www.conventionalcommits.org",
        skill_level="beginner",
    ),
    "commit message is too vague": MentorAdvice(
        suggestion="Use the format: type(scope): description — e.g., 'fix(auth): resolve token expiry bug'",
        why="Vague messages like 'fix' or 'update' make it impossible to understand the history. Conventional commits enable automated changelogs and semantic versioning.",
        command="git commit -m 'fix(auth): handle expired refresh token gracefully'",
        learn_more="https://www.conventionalcommits.org",
        skill_level="beginner",
    ),
    "commit message is empty": MentorAdvice(
        suggestion="Never commit without a message — every change deserves context",
        why="Empty messages violate Git best practices and make your repository's history useless for collaboration and debugging.",
        command="git commit -m 'docs: update API endpoint documentation'",
        skill_level="beginner",
    ),
    "no conventional prefix": MentorAdvice(
        suggestion="Start messages with: feat:, fix:, docs:, style:, refactor:, test:, chore:",
        why="Conventional commits create a structured history enabling automated releases, changelogs, and better collaboration in teams.",
        command="git commit -m 'refactor: extract validation logic into separate module'",
        learn_more="https://www.conventionalcommits.org",
        skill_level="intermediate",
    ),
    "long commit subject": MentorAdvice(
        suggestion="Keep the subject line under 72 characters, use body for details",
        why="Git tools truncate long subject lines. Use 'git commit' (without -m) to open an editor for multi-line messages.",
        command="git commit  # Opens editor for subject + body",
        skill_level="intermediate",
    ),
    "trailing period": MentorAdvice(
        suggestion="Remove the period — commit subjects are titles, not sentences",
        why="This is a widely adopted Git convention. Subject lines are treated as headlines.",
        skill_level="beginner",
    ),

    # ── Branch Issues ──
    "main branch": MentorAdvice(
        suggestion="Create a feature branch before making changes",
        why="The main branch should always be stable and deployable. Feature branches let you experiment safely, enable code review via PRs, and keep the main branch clean.",
        command="git checkout -b feature/your-feature-name",
        learn_more="https://nvie.com/posts/a-successful-git-branching-model/",
        skill_level="beginner",
    ),
    "branch naming": MentorAdvice(
        suggestion="Use format: type/description (e.g., feature/add-auth, fix/login-bug)",
        why="Consistent branch names help teams navigate repos. Prefixes like feature/, fix/, docs/ make the purpose immediately clear.",
        command="git checkout -b feature/user-authentication",
        skill_level="beginner",
    ),
    "branch bad chars": MentorAdvice(
        suggestion="Use only lowercase letters, numbers, hyphens, and forward slashes",
        why="Special characters in branch names cause issues with scripts, CI/CD pipelines, and some operating systems.",
        command="git branch -m old-name feature/new-valid-name",
        skill_level="beginner",
    ),
    "direct main commit": MentorAdvice(
        suggestion="Use the GitHub Flow: main → feature branch → PR → merge",
        why="Direct commits to main skip code review, can break deployments, and make rollbacks difficult.",
        command="git checkout -b feature/my-change && git push -u origin feature/my-change",
        learn_more="https://docs.github.com/en/get-started/quickstart/github-flow",
        skill_level="beginner",
    ),

    # ── File Issues ──
    "too many files": MentorAdvice(
        suggestion="Group related changes and commit separately",
        why="Atomic commits (one logical change per commit) make history clear, reviews easier, and allow precise git revert if something breaks.",
        command="git add src/auth/ && git commit -m 'feat: add authentication'\ngit add src/ui/ && git commit -m 'style: update login form'",
        skill_level="beginner",
    ),
    "blocked file type": MentorAdvice(
        suggestion="Add this file type to .gitignore immediately",
        why="Binary files, archives, and executables inflate repo size permanently (Git stores all history). Use git-lfs for large files or distribute them separately.",
        command="echo '*.exe' >> .gitignore && git rm --cached *.exe",
        learn_more="https://git-lfs.github.com",
        skill_level="beginner",
    ),
    "risky file": MentorAdvice(
        suggestion="Avoid committing logs, databases, and CSVs to Git",
        why="These files change frequently, can be huge, and inflate the repository. Use .gitignore for generated files.",
        command="echo '*.log\n*.csv\n*.db' >> .gitignore",
        skill_level="beginner",
    ),
    "config file risk": MentorAdvice(
        suggestion="Audit config files for secrets before committing",
        why="Config files commonly contain database passwords, API keys, and connection strings. One accidental push can expose everything.",
        command="git diff --cached config.json  # Review staged changes",
        skill_level="beginner",
    ),
    "merge conflict markers": MentorAdvice(
        suggestion="Open each conflicted file, resolve all <<<<<<< / ======= / >>>>>>> sections, then stage",
        why="Committing conflict markers will break your code. Git marks conflicts for you to manually decide which changes to keep.",
        command="git diff --name-only --diff-filter=U  # See conflicted files\ngit mergetool  # Launch merge tool",
        learn_more="https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/addressing-merge-conflicts",
        skill_level="beginner",
    ),

    # ── Security Issues ──
    "sensitive file": MentorAdvice(
        suggestion="Remove sensitive files and add them to .gitignore IMMEDIATELY",
        why="Sensitive files (.env, private keys, credentials) in a repo can be accessed by anyone with repo access. Even in private repos, this is a security risk.",
        command="git rm --cached .env && echo '.env' >> .gitignore && git commit -m 'chore: remove .env from tracking'",
        skill_level="beginner",
    ),
    "secret detected": MentorAdvice(
        suggestion="Remove the secret, rotate it, and use environment variables",
        why="Secrets in code are the #1 cause of data breaches. Once pushed, they exist in Git history forever unless you rewrite it.",
        command="# 1. Remove from code → use os.environ['KEY']\n# 2. Add to .env (gitignored)\n# 3. Rotate the exposed secret",
        learn_more="https://docs.github.com/en/code-security/secret-scanning",
        skill_level="beginner",
    ),
    "aws access key": MentorAdvice(
        suggestion="IMMEDIATELY rotate this key in AWS IAM console",
        why="Exposed AWS keys can lead to massive cloud bills, data theft, and cryptocurrency mining on your account. Bots scan GitHub for these 24/7.",
        command="# 1. Go to AWS IAM Console\n# 2. Deactivate the key\n# 3. Create new key\n# 4. Use aws configure or env vars",
        learn_more="https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html",
        skill_level="beginner",
    ),
    "private key": MentorAdvice(
        suggestion="Generate a NEW key pair and revoke the exposed one",
        why="A private key is your identity. Anyone with it can impersonate you, access your servers, and sign code as you.",
        command="ssh-keygen -t ed25519 -C 'your_email@example.com'  # Generate new key",
        skill_level="beginner",
    ),
    "large file": MentorAdvice(
        suggestion="Use Git LFS for large files or add to .gitignore",
        why="Git stores complete file history. A 50MB file committed 10 times = 500MB repo. This slows down clones, pushes, and CI/CD.",
        command="git lfs install && git lfs track '*.psd' && git add .gitattributes",
        learn_more="https://git-lfs.github.com",
        skill_level="intermediate",
    ),

    # ── Untracked Files ──
    "untracked": MentorAdvice(
        suggestion="Review untracked files — add needed ones, ignore the rest",
        why="Untracked files create noise. Generated files, caches, and build outputs should be in .gitignore to keep the repo clean.",
        command="git status  # See untracked files\ngit add <file>  # Track it\necho '<file>' >> .gitignore  # Ignore it",
        skill_level="beginner",
    ),

    # ── Git Config ──
    "no gitignore": MentorAdvice(
        suggestion="Create a .gitignore file immediately",
        why="Without .gitignore, you risk committing IDE configs, build artifacts, secrets, and OS files. Every project needs one.",
        command="devflow gitignore  # Auto-generate based on project type",
        skill_level="beginner",
    ),

    # ── Git Operations ──
    "detached head": MentorAdvice(
        suggestion="Create a branch to save your current work",
        why="In detached HEAD state, your commits aren't on any branch. If you checkout elsewhere, those commits become orphaned and may be garbage collected.",
        command="git checkout -b my-branch  # Create branch from current state",
        skill_level="intermediate",
    ),
    "stash": MentorAdvice(
        suggestion="Don't forget about stashed changes — apply or drop them",
        why="Stashed changes are easy to forget. Regular cleanup prevents confusion about 'lost' work.",
        command="git stash list  # See stashes\ngit stash pop  # Apply and remove\ngit stash drop  # Remove without applying",
        skill_level="intermediate",
    ),
    "behind remote": MentorAdvice(
        suggestion="Pull remote changes before pushing to avoid conflicts",
        why="Pushing when behind the remote will fail. Pull first to integrate remote changes, then push your work.",
        command="git pull --rebase origin main  # Rebase preferred, cleaner history",
        learn_more="https://docs.github.com/en/get-started/using-git/getting-changes-from-a-remote-repository",
        skill_level="beginner",
    ),
}


def explain_warning(warning: str) -> Optional[dict]:
    """
    Find the best explanation for a warning message.
    Returns dict with 'suggestion' and 'why' keys for backward compatibility.
    """
    warning_lower = warning.lower()

    for key, advice in EXPLANATIONS.items():
        if key in warning_lower:
            return {
                "suggestion": advice.suggestion,
                "why": advice.why,
                "command": advice.command,
                "learn_more": advice.learn_more,
            }

    return None


def get_mentor_advice(warning: str) -> Optional[MentorAdvice]:
    """Get structured mentor advice for a warning."""
    warning_lower = warning.lower()

    for key, advice in EXPLANATIONS.items():
        if key in warning_lower:
            return advice

    return None


def get_progressive_tip(warning_count: int, warning_type: str) -> Optional[str]:
    """Generate progressive tips based on how many times an issue occurred."""
    warning_lower = warning_type.lower()

    if warning_count < 3:
        return None

    progressive_tips = {
        "commit message": {
            3: "🧠 You've had commit message issues 3 times. Consider setting up a commit template: git config commit.template .gitmessage",
            5: "🧠 5 commit message issues! Create a .gitmessage template file to pre-fill your format.",
            10: "🧠 10+ commit issues — you would benefit from commitlint or a pre-commit hook that enforces conventional commits.",
        },
        "main branch": {
            3: "🧠 You've committed to main 3 times. Make 'git checkout -b' your first instinct before any change.",
            5: "🧠 5 direct main commits! Consider setting up branch protection rules on GitHub.",
            10: "🧠 10+ main branch commits — set up branch protection ASAP: github.com → Settings → Branches → Add rule",
        },
        "too many files": {
            3: "🧠 3 large commits detected. Practice 'git add -p' for interactive, precise staging.",
            5: "🧠 5 large commits! Use 'git add -p' (patch mode) to stage specific changes within files.",
        },
        "untracked": {
            3: "🧠 Recurring untracked files. Run 'devflow gitignore' to auto-generate ignore rules.",
            5: "🧠 Many untracked file warnings. Your .gitignore needs attention — run 'devflow gitignore'.",
        },
        "secret": {
            2: "🧠 SECRET ALERT: Multiple secret detections. Set up pre-commit hooks NOW: 'devflow init'",
            3: "🧠 CRITICAL: 3+ secret detections. You MUST use environment variables and a .env file.",
        },
    }

    for key, tips in progressive_tips.items():
        if key in warning_lower:
            # Find the highest applicable threshold
            applicable = None
            for threshold, tip in sorted(tips.items()):
                if warning_count >= threshold:
                    applicable = tip
            return applicable

    if warning_count >= 5:
        return f"🧠 This issue has occurred {warning_count} times. Consider addressing the root cause."

    return None


def get_quick_tips() -> List[str]:
    """Get a random set of quick developer tips."""
    tips = [
        "💡 Use 'git stash' to save work-in-progress before switching branches",
        "💡 Use 'git log --oneline --graph' for a visual branch history",
        "💡 Use 'git diff --staged' to review changes before committing",
        "💡 Use 'git commit --amend' to fix the last commit message",
        "💡 Use 'git reflog' to find lost commits after a bad rebase",
        "💡 Set up SSH keys for GitHub to avoid typing passwords",
        "💡 Use 'git blame <file>' to see who changed each line and why",
        "💡 Use 'git bisect' to find exactly which commit introduced a bug",
        "💡 Use 'git cherry-pick <hash>' to apply a specific commit to your branch",
        "💡 Create aliases: git config --global alias.co checkout",
        "💡 Use 'git rebase -i HEAD~3' to clean up your last 3 commits before PR",
        "💡 Tag releases: git tag -a v1.0.0 -m 'First release'",
        "💡 Use '.gitkeep' files to track empty directories",
        "💡 Use 'git clean -fd' to remove untracked files and directories",
        "💡 Set up GPG signing for commits: git config commit.gpgsign true",
    ]
    return tips
