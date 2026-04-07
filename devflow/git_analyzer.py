import subprocess

# -------------------------------
# PURPOSE:
# Analyze Git workflow
# -------------------------------


def get_current_branch():
    try:
        return subprocess.check_output(
            ["git", "branch", "--show-current"]
        ).decode().strip()
    except:
        return None


def check_main_branch():
    warnings = []
    branch = get_current_branch()

    if branch in ["main", "master"]:
        warnings.append("⚠️ You are committing directly to MAIN branch (use feature branch)")

    return warnings


def get_untracked_files():
    try:
        return subprocess.check_output(
            ["git", "ls-files", "--others", "--exclude-standard"]
        ).decode().splitlines()
    except:
        return []


def check_untracked_files():
    warnings = []
    untracked = get_untracked_files()

    if untracked:
        warnings.append(f"⚠️ You have {len(untracked)} untracked file(s): {', '.join(untracked[:3])}")

    return warnings


def check_large_files(file_list):
    warnings = []
    risky_extensions = [".log", ".csv", ".db"]

    for file in file_list:
        if any(file.endswith(ext) for ext in risky_extensions):
            warnings.append(f"⚠️ Risky file detected: {file}")

    return warnings