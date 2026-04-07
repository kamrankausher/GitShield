# -------------------------------
# PURPOSE:
# This module analyzes Git behavior
# and provides intelligent suggestions
# -------------------------------


def analyze_commit_message(message):
    """
    Analyze commit message quality
    """
    warnings = []

    if len(message.strip()) < 5:
        warnings.append("⚠️ Commit message too short")

    bad_words = ["update", "fix", "changes", "done"]

    if message.lower() in bad_words:
        warnings.append("⚠️ Commit message is too vague")

    return warnings


def analyze_staged_files(file_list):
    """
    Analyze number of files staged
    """
    warnings = []

    if len(file_list) > 10:
        warnings.append("⚠️ Too many files in one commit (consider splitting)")

    return warnings