from devflow.scanner import scan_directory
from devflow.rules import analyze_commit_message, analyze_staged_files
from devflow.git_analyzer import (
    check_main_branch,
    check_untracked_files,
    check_large_files
)
from devflow.mentor import explain_warning
from devflow.memory import update_memory
from devflow.ai_engine import generate_ai_suggestion

import sys
import subprocess

# -------------------------------
# STEP 1: Security Scan
# -------------------------------
issues = scan_directory(".")

if issues:
    print("\n❌ Issues detected:\n")
    for issue in issues:
        print(issue)
    sys.exit(1)

# -------------------------------
# STEP 2: Commit message
# -------------------------------
try:
    with open(".git/COMMIT_EDITMSG", "r") as f:
        commit_msg = f.read().strip()
except:
    commit_msg = ""

# -------------------------------
# STEP 3: Staged files
# -------------------------------
try:
    staged_files = subprocess.check_output(
        ["git", "diff", "--cached", "--name-only"]
    ).decode().splitlines()
except:
    staged_files = []

# -------------------------------
# STEP 4: Analysis
# -------------------------------
warnings = []
warnings += analyze_commit_message(commit_msg)
warnings += analyze_staged_files(staged_files)
warnings += check_main_branch()
warnings += check_untracked_files()
warnings += check_large_files(staged_files)

# -------------------------------
# STEP 5: Memory
# -------------------------------
memory = update_memory(warnings)

# -------------------------------
# STEP 6: Output
# -------------------------------
if warnings:
    print("\n⚠️ Suggestions:\n")

    for w in warnings:
        print(w)

        explanation = explain_warning(w)
        if explanation:
            print(f"💡 Suggestion: {explanation['suggestion']}")
            print(f"📘 Why: {explanation['why']}")

        # 🤖 AI
        ai = generate_ai_suggestion(w)
        print(f"🤖 AI Insight:\n{ai}\n")

        count = memory.get(w, 0)
        if count >= 3:
            print(f"🧠 Notice: You have encountered this issue {count} times\n")

print("\n✅ Commit allowed")
sys.exit(0)