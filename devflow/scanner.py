import os
import re

# -------------------------------
# PURPOSE:
# Scan files for sensitive data
# -------------------------------

EXCLUDED_DIRS = {"venv", ".git", "__pycache__", "node_modules"}

SECRET_PATTERNS = [
    r'AKIA[0-9A-Z]{16}',
    r'(?i)api[_-]?key\s*=\s*["\'].*["\']',
    r'(?i)secret\s*=\s*["\'].*["\']',
    r'(?i)password\s*=\s*["\'].*["\']'
]


def is_sensitive_file(file_path):
    filename = os.path.basename(file_path)
    return filename in {".env", ".env.local", ".env.production"}


def scan_file_for_secrets(file_path):
    findings = []

    try:
        with open(file_path, 'r', errors='ignore') as f:
            content = f.read()

            for pattern in SECRET_PATTERNS:
                if re.search(pattern, content):
                    findings.append(pattern)

    except Exception:
        pass

    return findings


def scan_directory(directory):
    issues = []

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for file in files:
            file_path = os.path.join(root, file)

            if is_sensitive_file(file_path):
                issues.append({
                    "file": file_path,
                    "type": "SENSITIVE_FILE"
                })

            findings = scan_file_for_secrets(file_path)
            if findings:
                issues.append({
                    "file": file_path,
                    "type": "SECRET_DETECTED",
                    "details": findings
                })

    return issues