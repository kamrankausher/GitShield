import subprocess

# -------------------------------
# PURPOSE:
# Analyze Git state and workflow
# -------------------------------


def get_current_branch():
    """
    Get current Git branch
    """
    try:
        branch = subprocess.check_output(
            ["git", "branch", "--show-current"]
        ).decode().strip()
        return branch
    except:
        return None


def check_main_branch():
    """
    Warn if working on main branch
    """
    warnings = []

    branch = get_current_branch()

    if branch in ["main", "master"]:
        warnings.append("⚠️ You are committing directly to MAIN branch (use feature branch)")

    return warnings


def get_untracked_files():
    """
    Get untracked files
    """
    try:
        output = subprocess.check_output(
            ["git", "ls-files", "--others", "--exclude-standard"]
        ).decode().splitlines()
        return output
    except:
        return []


def check_untracked_files():
    """
    Warn about untracked files
    """
    warnings = []

    untracked = get_untracked_files()

    if untracked:
        warnings.append(f"⚠️ You have {len(untracked)} untracked files")

    return warnings


def check_large_files(file_list):
    """
    Detect risky file types
    """
    warnings = []

    risky_extensions = [".log", ".csv", ".db"]

    for file in file_list:
        for ext in risky_extensions:
            if file.endswith(ext):
                warnings.append(f"⚠️ Risky file detected: {file}")

    return warnings