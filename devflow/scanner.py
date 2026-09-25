"""
DevFlow AI++ — Security Scanner Module
=======================================
Scans files and directories for sensitive data, secrets, API keys,
tokens, credentials, and other security vulnerabilities.

Features:
- 40+ secret detection patterns (AWS, GCP, Azure, GitHub, JWT, etc.)
- Severity levels: CRITICAL / HIGH / MEDIUM / LOW
- Staged file scanning for Git hooks
- Binary file detection
- Large file warnings
- Configurable exclusions
"""

import os
import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


# ═══════════════════════════════════════════════════════════════
# SEVERITY LEVELS
# ═══════════════════════════════════════════════════════════════
class Severity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

    @property
    def icon(self):
        return {
            "CRITICAL": "🔴",
            "HIGH": "🟠",
            "MEDIUM": "🟡",
            "LOW": "🔵",
        }[self.value]

    @property
    def priority(self):
        return {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}[self.value]


# ═══════════════════════════════════════════════════════════════
# FINDING DATA CLASS
# ═══════════════════════════════════════════════════════════════
@dataclass
class Finding:
    """Represents a single security finding."""
    file: str
    finding_type: str
    severity: Severity
    message: str
    line_number: Optional[int] = None
    pattern_name: str = ""
    suggestion: str = ""

    def __str__(self):
        loc = f":{self.line_number}" if self.line_number else ""
        return (
            f"{self.severity.icon} [{self.severity.value}] {self.message}\n"
            f"   📄 {self.file}{loc}"
        )


# ═══════════════════════════════════════════════════════════════
# SECRET PATTERNS (40+ patterns covering major providers)
# ═══════════════════════════════════════════════════════════════
SECRET_PATTERNS = [
    # ── AWS ──
    {"name": "AWS Access Key", "pattern": r'AKIA[0-9A-Z]{16}', "severity": Severity.CRITICAL},
    {"name": "AWS Secret Key", "pattern": r'(?i)aws.{0,20}[\'"][0-9a-zA-Z\/+]{40}[\'"]', "severity": Severity.CRITICAL},
    {"name": "AWS MWS Key", "pattern": r'amzn\.mws\.[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', "severity": Severity.CRITICAL},

    # ── Google / GCP ──
    {"name": "Google API Key", "pattern": r'AIza[0-9A-Za-z\-_]{35}', "severity": Severity.CRITICAL},
    {"name": "Google OAuth ID", "pattern": r'[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com', "severity": Severity.HIGH},
    {"name": "Google Service Account", "pattern": r'"type"\s*:\s*"service_account"', "severity": Severity.CRITICAL},

    # ── GitHub ──
    {"name": "GitHub Token", "pattern": r'gh[pousr]_[A-Za-z0-9_]{36,255}', "severity": Severity.CRITICAL},
    {"name": "GitHub OAuth", "pattern": r'gho_[A-Za-z0-9_]{36,255}', "severity": Severity.CRITICAL},
    {"name": "GitHub App Token", "pattern": r'(ghu|ghs)_[A-Za-z0-9_]{36,255}', "severity": Severity.CRITICAL},
    {"name": "GitHub Classic PAT", "pattern": r'ghp_[A-Za-z0-9]{36}', "severity": Severity.CRITICAL},

    # ── Azure ──
    {"name": "Azure Storage Key", "pattern": r'(?i)AccountKey\s*=\s*[A-Za-z0-9+\/=]{88}', "severity": Severity.CRITICAL},
    {"name": "Azure Connection String", "pattern": r'(?i)DefaultEndpointsProtocol=https?;AccountName=', "severity": Severity.HIGH},

    # ── Stripe ──
    {"name": "Stripe Secret Key", "pattern": r'sk_live_[0-9a-zA-Z]{24,}', "severity": Severity.CRITICAL},
    {"name": "Stripe Publishable Key", "pattern": r'pk_live_[0-9a-zA-Z]{24,}', "severity": Severity.MEDIUM},
    {"name": "Stripe Restricted Key", "pattern": r'rk_live_[0-9a-zA-Z]{24,}', "severity": Severity.CRITICAL},

    # ── Slack ──
    {"name": "Slack Token", "pattern": r'xox[baprs]-[0-9a-zA-Z]{10,}', "severity": Severity.HIGH},
    {"name": "Slack Webhook", "pattern": r'https://hooks\.slack\.com/services/T[a-zA-Z0-9_]{8}/B[a-zA-Z0-9_]{8}/[a-zA-Z0-9_]{24}', "severity": Severity.HIGH},

    # ── Database ──
    {"name": "MongoDB URI", "pattern": r'mongodb(\+srv)?://[^\s<>"{}|\\^`\[\]]+', "severity": Severity.CRITICAL},
    {"name": "PostgreSQL URI", "pattern": r'postgres(ql)?://[^\s<>"{}|\\^`\[\]]+', "severity": Severity.CRITICAL},
    {"name": "MySQL URI", "pattern": r'mysql://[^\s<>"{}|\\^`\[\]]+', "severity": Severity.CRITICAL},
    {"name": "Redis URI", "pattern": r'redis://[^\s<>"{}|\\^`\[\]]+', "severity": Severity.HIGH},

    # ── JWT / Auth ──
    {"name": "JWT Token", "pattern": r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}', "severity": Severity.HIGH},
    {"name": "Bearer Token", "pattern": r'(?i)bearer\s+[a-zA-Z0-9\-._~+\/]{20,}', "severity": Severity.HIGH},

    # ── SSH / Crypto ──
    {"name": "RSA Private Key", "pattern": r'-----BEGIN RSA PRIVATE KEY-----', "severity": Severity.CRITICAL},
    {"name": "DSA Private Key", "pattern": r'-----BEGIN DSA PRIVATE KEY-----', "severity": Severity.CRITICAL},
    {"name": "EC Private Key", "pattern": r'-----BEGIN EC PRIVATE KEY-----', "severity": Severity.CRITICAL},
    {"name": "OpenSSH Private Key", "pattern": r'-----BEGIN OPENSSH PRIVATE KEY-----', "severity": Severity.CRITICAL},
    {"name": "PGP Private Key", "pattern": r'-----BEGIN PGP PRIVATE KEY BLOCK-----', "severity": Severity.CRITICAL},

    # ── Twilio ──
    {"name": "Twilio API Key", "pattern": r'SK[0-9a-fA-F]{32}', "severity": Severity.HIGH},

    # ── SendGrid ──
    {"name": "SendGrid API Key", "pattern": r'SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}', "severity": Severity.HIGH},

    # ── Mailgun ──
    {"name": "Mailgun API Key", "pattern": r'key-[0-9a-zA-Z]{32}', "severity": Severity.HIGH},

    # ── Firebase ──
    {"name": "Firebase URL", "pattern": r'https://[a-z0-9-]+\.firebaseio\.com', "severity": Severity.MEDIUM},
    {"name": "Firebase API Key", "pattern": r'(?i)firebase.*[\'"][A-Za-z0-9_]{39}[\'"]', "severity": Severity.HIGH},

    # ── Heroku ──
    {"name": "Heroku API Key", "pattern": r'(?i)heroku(.{0,20})?[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', "severity": Severity.HIGH},

    # ── Generic Secrets ──
    {"name": "Generic API Key", "pattern": r'(?i)api[_-]?key\s*[=:]\s*["\']([a-zA-Z0-9_\-]{16,})["\']', "severity": Severity.HIGH},
    {"name": "Generic Secret", "pattern": r'(?i)(?:secret|token|password|passwd|pwd)\s*[=:]\s*["\']([^\s"\']{8,})["\']', "severity": Severity.HIGH},
    {"name": "Generic Auth", "pattern": r'(?i)(?:auth|access)[_-]?(?:token|key)\s*[=:]\s*["\']([^\s"\']{8,})["\']', "severity": Severity.HIGH},
    {"name": "Private Key Inline", "pattern": r'(?i)private[_-]?key\s*[=:]\s*["\']([^\s"\']{10,})["\']', "severity": Severity.CRITICAL},

    # ── NPM ──
    {"name": "NPM Token", "pattern": r'//registry\.npmjs\.org/:_authToken=([^\s]+)', "severity": Severity.HIGH},

    # ── Docker ──
    {"name": "Docker Auth", "pattern": r'(?i)docker(.{0,20})?(password|token|auth)\s*[=:]\s*["\']([^\s"\']+)["\']', "severity": Severity.HIGH},

    # ── Misc ──
    {"name": "IP Address (Private)", "pattern": r'\b(?:10\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b', "severity": Severity.LOW},
    {"name": "Hardcoded Password", "pattern": r'(?i)(?:password|passwd|pwd)\s*=\s*["\']([^"\']{4,})["\']', "severity": Severity.HIGH},
]

# ═══════════════════════════════════════════════════════════════
# SENSITIVE FILES
# ═══════════════════════════════════════════════════════════════
SENSITIVE_FILES = {
    ".env": Severity.CRITICAL,
    ".env.local": Severity.CRITICAL,
    ".env.production": Severity.CRITICAL,
    ".env.staging": Severity.CRITICAL,
    ".env.development": Severity.HIGH,
    ".env.test": Severity.MEDIUM,
    "id_rsa": Severity.CRITICAL,
    "id_dsa": Severity.CRITICAL,
    "id_ecdsa": Severity.CRITICAL,
    "id_ed25519": Severity.CRITICAL,
    ".pem": Severity.CRITICAL,
    ".key": Severity.CRITICAL,
    ".p12": Severity.CRITICAL,
    ".pfx": Severity.CRITICAL,
    ".keystore": Severity.CRITICAL,
    ".jks": Severity.CRITICAL,
    "credentials.json": Severity.CRITICAL,
    "service-account.json": Severity.CRITICAL,
    "serviceAccountKey.json": Severity.CRITICAL,
    ".npmrc": Severity.HIGH,
    ".pypirc": Severity.HIGH,
    ".netrc": Severity.HIGH,
    ".htpasswd": Severity.HIGH,
    "wp-config.php": Severity.HIGH,
    "docker-compose.override.yml": Severity.MEDIUM,
    "shadow": Severity.CRITICAL,
    "passwd": Severity.HIGH,
}

# ═══════════════════════════════════════════════════════════════
# DANGEROUS FILE EXTENSIONS
# ═══════════════════════════════════════════════════════════════
DANGEROUS_EXTENSIONS = {
    ".pem", ".key", ".p12", ".pfx", ".keystore", ".jks",
    ".der", ".cert", ".crt", ".ca-bundle",
}

# ═══════════════════════════════════════════════════════════════
# EXCLUDED DIRECTORIES
# ═══════════════════════════════════════════════════════════════
EXCLUDED_DIRS = {
    "venv", ".git", "__pycache__", "node_modules", ".tox",
    ".mypy_cache", ".pytest_cache", "dist", "build", ".eggs",
    "htmlcov", ".venv", "env", ".env", "vendor", "migrations",
}

# ═══════════════════════════════════════════════════════════════
# BINARY EXTENSIONS (skip scanning)
# ═══════════════════════════════════════════════════════════════
BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg",
    ".mp3", ".mp4", ".avi", ".mov", ".wav",
    ".zip", ".tar", ".gz", ".rar", ".7z",
    ".exe", ".dll", ".so", ".dylib",
    ".pyc", ".pyo", ".class", ".o",
    ".ttf", ".otf", ".woff", ".woff2",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".sqlite", ".db",
}

# ═══════════════════════════════════════════════════════════════
# LARGE FILE THRESHOLD (5MB)
# ═══════════════════════════════════════════════════════════════
LARGE_FILE_THRESHOLD = 5 * 1024 * 1024  # 5MB


def is_binary_file(file_path: str) -> bool:
    """Check if a file is binary by extension."""
    _, ext = os.path.splitext(file_path)
    return ext.lower() in BINARY_EXTENSIONS


def is_sensitive_file(file_path: str) -> Optional[Severity]:
    """Check if a file is a known sensitive file. Returns severity or None."""
    filename = os.path.basename(file_path).lower()
    _, ext = os.path.splitext(file_path)

    # Check by exact filename
    if filename in SENSITIVE_FILES:
        return SENSITIVE_FILES[filename]

    # Check by extension
    if ext.lower() in DANGEROUS_EXTENSIONS:
        return Severity.CRITICAL

    # Check .env variants
    if filename.startswith(".env"):
        return Severity.CRITICAL

    return None


from devflow.config import load_config
import math

def shannon_entropy(data: str) -> float:
    """Calculate the Shannon entropy of a string."""
    if not data:
        return 0.0
    entropy = 0.0
    length = len(data)
    occurrences = {}
    for char in data:
        occurrences[char] = occurrences.get(char, 0) + 1
    for count in occurrences.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy

def scan_file_for_secrets(file_path: str, config: Optional[dict] = None) -> List[Finding]:
    """Scan a single file for secret patterns."""
    findings = []

    if is_binary_file(file_path):
        return findings
        
    if config is None:
        config = load_config()
        
    # Check file exclusions
    if any(ignore_file in file_path for ignore_file in config.get("ignore_files", [])):
        return findings

    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            # Skip comments and empty lines
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("//"):
                continue
                
            # Check string exclusions
            if any(ignore_str in line for ignore_str in config.get("ignore_strings", [])):
                continue

            for pattern_info in SECRET_PATTERNS:
                match = re.search(pattern_info["pattern"], line)
                if match:
                    # Check regex exclusions
                    matched_str = match.group(0)
                    if any(re.search(ignore_regex, matched_str) for ignore_regex in config.get("ignore_patterns", [])):
                        continue
                        
                    # Entropy check for generic secrets
                    if "Generic" in pattern_info["name"] or "Password" in pattern_info["name"]:
                        # If there are groups, use the last group as the secret value
                        secret_value = match.group(match.lastindex) if match.lastindex else matched_str
                        # A typical random string of base62 has an entropy of ~ 5.95 bits/char
                        # We use 3.0 as a threshold for rejecting common words (e.g. "password", "test")
                        if shannon_entropy(secret_value) < 3.0:
                            continue
                        
                    findings.append(Finding(
                        file=file_path,
                        finding_type="SECRET_DETECTED",
                        severity=pattern_info["severity"],
                        message=f'{pattern_info["name"]} detected',
                        line_number=line_num,
                        pattern_name=pattern_info["name"],
                        suggestion=_get_secret_suggestion(pattern_info["name"]),
                    ))

    except (PermissionError, OSError):
        pass

    return findings


def check_file_size(file_path: str) -> Optional[Finding]:
    """Check if a file exceeds the size threshold."""
    try:
        size = os.path.getsize(file_path)
        if size > LARGE_FILE_THRESHOLD:
            size_mb = size / (1024 * 1024)
            return Finding(
                file=file_path,
                finding_type="LARGE_FILE",
                severity=Severity.MEDIUM,
                message=f"Large file detected ({size_mb:.1f} MB)",
                suggestion="Consider using Git LFS or adding to .gitignore",
            )
    except OSError:
        pass
    return None


def scan_directory(directory: str, staged_only: bool = False, config: Optional[dict] = None) -> List[Finding]:
    """
    Scan an entire directory tree for security issues.

    Args:
        directory: Path to scan
        staged_only: If True, only scan Git staged files
        config: Configuration dictionary

    Returns:
        List of Finding objects sorted by severity
    """
    findings = []
    
    if config is None:
        config = load_config()

    if staged_only:
        import subprocess
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True, text=True, cwd=directory,
                encoding="utf-8", errors="replace",
                stdin=subprocess.DEVNULL,
            )
            files_to_scan = [
                os.path.join(directory, f.strip())
                for f in result.stdout.splitlines() if f.strip()
            ]
        except (FileNotFoundError, subprocess.SubprocessError):
            files_to_scan = []

        for file_path in files_to_scan:
            if not os.path.exists(file_path):
                continue
            _scan_single_file(file_path, findings, config)
    else:
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in config.get("exclude_dirs", EXCLUDED_DIRS)]

            for fname in files:
                file_path = os.path.join(root, fname)
                _scan_single_file(file_path, findings, config)

    # Sort by severity (CRITICAL first)
    findings.sort(key=lambda f: f.severity.priority, reverse=True)
    return findings


def _scan_single_file(file_path: str, findings: List[Finding], config: Optional[dict] = None):
    """Scan a single file for all security issues."""
    
    if config and any(ignore_file in file_path for ignore_file in config.get("ignore_files", [])):
        return
        
    # Check sensitive file
    sensitivity = is_sensitive_file(file_path)
    if sensitivity:
        findings.append(Finding(
            file=file_path,
            finding_type="SENSITIVE_FILE",
            severity=sensitivity,
            message=f"Sensitive file should not be committed: {os.path.basename(file_path)}",
            suggestion="Add this file to .gitignore immediately",
        ))

    # Check file size
    size_finding = check_file_size(file_path)
    if size_finding:
        findings.append(size_finding)

    # Scan for secrets in content
    secret_findings = scan_file_for_secrets(file_path, config)
    findings.extend(secret_findings)


def _get_secret_suggestion(pattern_name: str) -> str:
    """Get a helpful suggestion for a detected secret type."""
    suggestions = {
        "AWS Access Key": "Rotate this key immediately via AWS IAM console and use environment variables",
        "AWS Secret Key": "Never store AWS secrets in code. Use AWS CLI config or env vars",
        "Google API Key": "Restrict this key in Google Cloud Console and use env vars",
        "GitHub Token": "Revoke this token at github.com/settings/tokens and generate a new one",
        "GitHub Classic PAT": "Revoke and regenerate at github.com/settings/tokens",
        "Stripe Secret Key": "Rotate key in Stripe Dashboard → Developers → API keys",
        "RSA Private Key": "Remove from repo history with git filter-branch or BFG Repo-Cleaner",
        "OpenSSH Private Key": "Generate a new SSH key pair and revoke the exposed one",
        "JWT Token": "Invalidate this token and rotate signing keys",
        "MongoDB URI": "Change database credentials immediately and use env vars",
        "PostgreSQL URI": "Rotate database credentials and use connection pooling with env vars",
        "Hardcoded Password": "Move to environment variables or a secrets manager",
        "Generic API Key": "Store API keys in environment variables, never in code",
        "Generic Secret": "Use a secrets manager or environment variables",
    }
    return suggestions.get(pattern_name, "Remove from code and use environment variables or a secrets manager")


def get_scan_summary(findings: List[Finding]) -> dict:
    """Generate a summary of scan findings."""
    summary = {
        "total": len(findings),
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "types": {},
    }

    for finding in findings:
        severity_key = finding.severity.value.lower()
        summary[severity_key] = summary.get(severity_key, 0) + 1

        finding_type = finding.finding_type
        summary["types"][finding_type] = summary["types"].get(finding_type, 0) + 1

    return summary
