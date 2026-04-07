from devflow.scanner import scan_directory
from devflow.rules import analyze_commit_message, analyze_staged_files
import sys
import subprocess

# -------------------------------
# STEP 1: Run scanner
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
    commit_msg = subprocess.check_output(
        ["git", "log", "-1", "--pretty=%B"]
    ).decode().strip()
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

# -------------------------------
# STEP 5: Show warnings (DO NOT BLOCK)
# -------------------------------
if warnings:
    print("\n⚠️ Suggestions:\n")
    for w in warnings:
        print(w)

print("\n✅ Commit allowed")
sys.exit(0)