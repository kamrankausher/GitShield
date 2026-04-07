from devflow.scanner import scan_directory
from devflow.rules import analyze_commit_message, analyze_staged_files
from devflow.git_analyzer import (
    check_main_branch,
    check_untracked_files,
    check_large_files
)
from devflow.mentor import explain_warning
from devflow.memory import update_memory

import sys
import subprocess


# -------------------------------
# STEP 1: Security Scan (BLOCK)
# -------------------------------
issues = scan_directory(".")

if issues:
    print("\n❌ Issues detected:\n")
    
    for issue in issues:
        print(issue)
    
    sys.exit(1)


# -------------------------------
# STEP 2: Get commit message
# -------------------------------
try:
    with open(".git/COMMIT_EDITMSG", "r") as f:
        commit_msg = f.read().strip()
except:
    commit_msg = ""


# -------------------------------
# STEP 3: Get staged files
# -------------------------------
try:
    staged_files = subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"]
    ).decode().splitlines()
except:
    staged_files = []


# -------------------------------
# STEP 4: Analyze
# -------------------------------
warnings = []

warnings += analyze_commit_message(commit_msg)
warnings += analyze_staged_files(staged_files)

# 🔥 Git Intelligence
warnings += check_main_branch()
warnings += check_untracked_files()
warnings += check_large_files(staged_files)


# -------------------------------
# STEP 5: Update Memory FIRST
# -------------------------------
memory = update_memory(warnings)


# -------------------------------
# STEP 6: Show warnings
# -------------------------------
if warnings:
    print("\n⚠️ Suggestions:\n")

    for w in warnings:
        print(w)

        # 💡 Explanation (AI Mentor)
        explanation = explain_warning(w)
        if explanation:
            print(f"💡 Suggestion: {explanation['suggestion']}")
            print(f"📘 Why: {explanation['why']}")

        # 🧠 Personalized feedback
        count = memory.get(w, 0)
        if count >= 3:
            print(f"🧠 Notice: You have encountered this issue {count} times. Consider improving this practice.\n")


print("\n✅ Commit allowed")
sys.exit(0)