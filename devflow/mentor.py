def explain_warning(warning):

    explanations = {
        "⚠️ Commit message too short": {
            "suggestion": "Use at least 5-10 meaningful words",
            "why": "Short messages do not describe changes clearly"
        },
        "⚠️ Commit message is too vague": {
            "suggestion": "Use descriptive message like 'Added authentication system'",
            "why": "Clear messages help in debugging and collaboration"
        },
        "⚠️ Too many files in one commit": {
            "suggestion": "Split commits into smaller logical parts",
            "why": "Smaller commits are easier to review"
        },
        "⚠️ You are committing directly to MAIN branch": {
            "suggestion": "Use 'git checkout -b feature-name'",
            "why": "Main branch should remain stable"
        },
        "⚠️ You have": {
            "suggestion": "Add or ignore files using .gitignore",
            "why": "Untracked files can break consistency"
        },
        "⚠️ Risky file detected": {
            "suggestion": "Avoid committing large/raw files",
            "why": "They increase repo size and risk exposure"
        }
    }

    for key in explanations:
        if key in warning:
            return explanations[key]

    return None