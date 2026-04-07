# -------------------------------
# PURPOSE:
# Provide intelligent explanations
# and suggestions for issues
# -------------------------------

def explain_warning(warning):
    """
    Convert warning into:
    - Suggestion
    - Explanation
    """

    explanations = {
        "⚠️ Commit message too short": {
            "suggestion": "Use at least 5-10 meaningful words",
            "why": "Short messages do not describe changes clearly"
        },
        "⚠️ Commit message is too vague": {
            "suggestion": "Use descriptive message like 'Added user authentication system'",
            "why": "Clear messages help in debugging and team collaboration"
        },
        "⚠️ Too many files in one commit (consider splitting)": {
            "suggestion": "Split commits into smaller logical parts",
            "why": "Smaller commits are easier to review and revert"
        },
        "⚠️ You are committing directly to MAIN branch (use feature branch)": {
            "suggestion": "Create a new branch using 'git checkout -b feature-name'",
            "why": "Working on main branch is risky and affects production stability"
        },
        "⚠️ You have": {
            "suggestion": "Add necessary files or ignore unwanted ones using .gitignore",
            "why": "Untracked files may cause inconsistency in project"
        },
        "⚠️ Risky file detected": {
            "suggestion": "Avoid committing large or sensitive data files",
            "why": "These files increase repo size and may contain sensitive data"
        }
    }

    # Match partial warnings
    for key in explanations:
        if key in warning:
            return explanations[key]

    return None