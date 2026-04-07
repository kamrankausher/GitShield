# -------------------------------
# PURPOSE:
# Analyze commit behavior
# -------------------------------

def analyze_commit_message(message):
    warnings = []

    if len(message.strip()) < 5:
        warnings.append("⚠️ Commit message too short")

    bad_words = ["update", "fix", "changes", "done"]

    if message.lower() in bad_words:
        warnings.append("⚠️ Commit message is too vague")

    return warnings


def analyze_staged_files(file_list):
    warnings = []

    if len(file_list) > 10:
        warnings.append("⚠️ Too many files in one commit (consider splitting)")

    return warnings