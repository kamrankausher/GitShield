"""
DevFlow AI++ — GitHub Workflow Assistant
=========================================
Guides developers through GitHub workflows including PR creation,
contribution flows, repo setup, and best practices.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class WorkflowGuide:
    """A step-by-step workflow guide."""
    title: str
    description: str
    steps: List[Dict[str, str]]
    tips: List[str]


def get_pr_guide() -> WorkflowGuide:
    """Guide for creating a Pull Request."""
    return WorkflowGuide(
        title="Creating a Pull Request",
        description="Step-by-step guide to create a professional Pull Request.",
        steps=[
            {"step": "Create a feature branch", "command": "git checkout -b feature/your-feature"},
            {"step": "Make your changes and commit", "command": "git add . && git commit -m 'feat: description'"},
            {"step": "Push to remote", "command": "git push -u origin feature/your-feature"},
            {"step": "Open PR on GitHub", "command": "Visit github.com/repo/compare/feature/your-feature"},
            {"step": "Write a clear PR description", "command": "Include: What, Why, How, Testing"},
            {"step": "Request reviews", "command": "Tag relevant team members"},
            {"step": "Address feedback", "command": "Make changes, commit, push — PR updates automatically"},
            {"step": "Merge after approval", "command": "Use 'Squash and merge' for clean history"},
        ],
        tips=[
            "Keep PRs small (<400 lines) for easier review",
            "Include screenshots for UI changes",
            "Link related issues: 'Closes #123'",
            "Write tests for new features",
            "Use draft PRs for work-in-progress",
        ],
    )


def get_contribution_guide() -> WorkflowGuide:
    """Guide for contributing to open-source projects."""
    return WorkflowGuide(
        title="Contributing to Open Source",
        description="How to contribute to open-source projects professionally.",
        steps=[
            {"step": "Fork the repository", "command": "Click 'Fork' on GitHub"},
            {"step": "Clone your fork", "command": "git clone https://github.com/YOU/repo.git"},
            {"step": "Add upstream remote", "command": "git remote add upstream https://github.com/ORIGINAL/repo.git"},
            {"step": "Create feature branch", "command": "git checkout -b feature/my-contribution"},
            {"step": "Make changes and commit", "command": "Follow project's commit conventions"},
            {"step": "Sync with upstream", "command": "git fetch upstream && git rebase upstream/main"},
            {"step": "Push to your fork", "command": "git push origin feature/my-contribution"},
            {"step": "Create PR to upstream", "command": "Compare across forks on GitHub"},
        ],
        tips=[
            "Read CONTRIBUTING.md before starting",
            "Start with 'good first issue' labels",
            "Follow the project's code style",
            "Be responsive to review feedback",
            "Keep your fork synced with upstream",
        ],
    )


def get_repo_setup_guide() -> WorkflowGuide:
    """Guide for setting up a new repository."""
    return WorkflowGuide(
        title="Repository Setup Best Practices",
        description="Set up a professional repository from scratch.",
        steps=[
            {"step": "Initialize repository", "command": "git init && git branch -M main"},
            {"step": "Create README.md", "command": "Add project description, setup, and usage"},
            {"step": "Add .gitignore", "command": "devflow gitignore"},
            {"step": "Add LICENSE", "command": "Choose MIT, Apache-2.0, or GPL-3.0"},
            {"step": "Initial commit", "command": "git add . && git commit -m 'chore: initial project setup'"},
            {"step": "Create remote repository", "command": "gh repo create project-name --public"},
            {"step": "Push to remote", "command": "git remote add origin URL && git push -u origin main"},
            {"step": "Set up branch protection", "command": "Settings → Branches → Add rule for main"},
            {"step": "Install DevFlow hooks", "command": "devflow init"},
        ],
        tips=[
            "Use descriptive repository names",
            "Add topics/tags for discoverability",
            "Set up CI/CD (GitHub Actions)",
            "Enable security scanning",
            "Create issue and PR templates",
        ],
    )


def get_branching_guide() -> WorkflowGuide:
    """Guide for Git branching strategies."""
    return WorkflowGuide(
        title="Git Branching Strategies",
        description="Common branching strategies for different team sizes.",
        steps=[
            {"step": "GitHub Flow (simple)", "command": "main → feature-branch → PR → merge"},
            {"step": "Git Flow (complex)", "command": "main + develop + feature + release + hotfix"},
            {"step": "Trunk-Based (fast)", "command": "main + short-lived feature branches"},
        ],
        tips=[
            "Small teams: Use GitHub Flow",
            "Large teams with releases: Use Git Flow",
            "CI/CD focused: Use Trunk-Based Development",
            "Always use feature branches, never commit directly to main",
            "Delete branches after merging",
        ],
    )


def get_merge_guide() -> WorkflowGuide:
    """Guide for handling merges and conflicts."""
    return WorkflowGuide(
        title="Merging & Conflict Resolution",
        description="How to merge branches and resolve conflicts.",
        steps=[
            {"step": "Update your branch", "command": "git fetch origin && git rebase origin/main"},
            {"step": "If conflicts arise", "command": "Open conflicted files, look for <<<<<<< markers"},
            {"step": "Resolve each conflict", "command": "Choose which changes to keep, remove markers"},
            {"step": "Mark as resolved", "command": "git add <resolved-file>"},
            {"step": "Continue rebase", "command": "git rebase --continue"},
            {"step": "Or merge instead", "command": "git merge main (creates merge commit)"},
        ],
        tips=[
            "Use 'git mergetool' for visual conflict resolution",
            "Rebase for clean history, merge for preserving context",
            "Communicate with team when resolving conflicts in shared code",
            "Test thoroughly after conflict resolution",
        ],
    )


AVAILABLE_GUIDES = {
    "pr": get_pr_guide,
    "pull-request": get_pr_guide,
    "contribute": get_contribution_guide,
    "contribution": get_contribution_guide,
    "open-source": get_contribution_guide,
    "setup": get_repo_setup_guide,
    "repo": get_repo_setup_guide,
    "branch": get_branching_guide,
    "branching": get_branching_guide,
    "merge": get_merge_guide,
    "conflict": get_merge_guide,
}


def get_guide(topic: str) -> WorkflowGuide:
    """Get a workflow guide by topic."""
    factory = AVAILABLE_GUIDES.get(topic.lower())
    if factory:
        return factory()
    return WorkflowGuide(
        title=f"Guide: {topic}",
        description=f"No specific guide found for '{topic}'.",
        steps=[],
        tips=[f"Available topics: {', '.join(sorted(set(AVAILABLE_GUIDES.keys())))}"],
    )


def get_available_topics() -> List[str]:
    """Get list of available guide topics."""
    return sorted(set(AVAILABLE_GUIDES.keys()))
