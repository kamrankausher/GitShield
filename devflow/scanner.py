import os
import re

# -------------------------------
# PURPOSE:
# This module scans files to detect:
# - Sensitive files (.env)
# - API keys / secrets
# -------------------------------

# 🔒 Folders to exclude from scanning
EXCLUDED_DIRS = {"venv", ".git", "__pycache__", "node_modules"}

# 🔍 Patterns for detecting secrets
SECRET_PATTERNS = [
    r'AKIA[0-9A-Z]{16}',  # AWS Access Key
    r'(?i)api[_-]?key\s*=\s*["\'].*["\']',
    r'(?i)secret\s*=\s*["\'].*["\']',
    r'(?i)password\s*=\s*["\'].*["\']'
]


def is_sensitive_file(file_path):
    """
    Check if file itself is dangerous (like .env)
    """
    filename = os.path.basename(file_path)

    sensitive_files = {".env", ".env.local", ".env.production"}

    return filename in sensitive_files


def scan_file_for_secrets(file_path):
    """
    Scan file content for secrets using regex
    """
    findings = []

    try:
        with open(file_path, 'r', errors='ignore') as f:
            content = f.read()

            for pattern in SECRET_PATTERNS:
                if re.search(pattern, content):
                    findings.append(pattern)

    except Exception as e:
        print(f"[WARNING] Could not read {file_path}: {e}")

    return findings


def scan_directory(directory):
    """
    Scan all files inside a directory
    """
    issues = []

    for root, dirs, files in os.walk(directory):

        # 🔥 Skip unwanted directories
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for file in files:
            file_path = os.path.join(root, file)

            # Check sensitive file
            if is_sensitive_file(file_path):
                issues.append({
                    "file": file_path,
                    "type": "SENSITIVE_FILE"
                })

            # Check secrets in content
            findings = scan_file_for_secrets(file_path)
            if findings:
                issues.append({
                    "file": file_path,
                    "type": "SECRET_DETECTED",
                    "details": findings
                })

    return issues