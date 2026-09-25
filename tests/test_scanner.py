"""Tests for the security scanner module."""

import os
import tempfile

from devflow.scanner import (
    Finding,
    Severity,
    get_scan_summary,
    is_sensitive_file,
    scan_directory,
    scan_file_for_secrets,
)


class TestSensitiveFileDetection:
    def test_env_file(self):
        assert is_sensitive_file(".env") == Severity.CRITICAL

    def test_env_local(self):
        assert is_sensitive_file(".env.local") == Severity.CRITICAL

    def test_env_production(self):
        assert is_sensitive_file(".env.production") == Severity.CRITICAL

    def test_private_key(self):
        assert is_sensitive_file("id_rsa") == Severity.CRITICAL

    def test_pem_file(self):
        assert is_sensitive_file("cert.pem") == Severity.CRITICAL

    def test_safe_file(self):
        assert is_sensitive_file("app.py") is None

    def test_safe_js(self):
        assert is_sensitive_file("index.js") is None


class TestSecretPatterns:
    def _scan_content(self, content, filename="test.py"):
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False)
        f.write(content)
        f.close()
        try:
            return scan_file_for_secrets(f.name)
        finally:
            os.unlink(f.name)

    def test_aws_key(self):
        findings = self._scan_content('aws_key = "AKIAIOSFODNN7' + 'EXAMPLE"')
        assert len(findings) > 0
        assert any("AWS" in f.pattern_name for f in findings)

    def test_github_token(self):
        findings = self._scan_content('token = "ghp_' + 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh"')
        assert len(findings) > 0

    def test_stripe_key(self):
        findings = self._scan_content('STRIPE_KEY = "sk_live_' + '1234567890abcdefghijklmn"')
        assert len(findings) > 0

    def test_private_key_header(self):
        findings = self._scan_content("-----BEGIN RSA" + " PRIVATE KEY-----")
        assert len(findings) > 0
        assert any(f.severity == Severity.CRITICAL for f in findings)

    def test_jwt_token(self):
        findings = self._scan_content('token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.' + 'eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"')
        assert len(findings) > 0

    def test_safe_content(self):
        findings = self._scan_content('x = 42\nprint("hello")')
        assert len(findings) == 0

    def test_comment_ignored(self):
        findings = self._scan_content('# AKIAIOSFODNN7' + 'EXAMPLE')
        assert len(findings) == 0


class TestDirectoryScanning:
    def test_scan_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            findings = scan_directory(tmpdir)
            assert findings == []

    def test_scan_with_env(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = os.path.join(tmpdir, ".env")
            with open(env_path, "w") as f:
                f.write("SECRET=hello")
            findings = scan_directory(tmpdir)
            assert len(findings) > 0

    def test_scan_summary(self):
        findings = [
            Finding("f1", "SECRET", Severity.CRITICAL, "test"),
            Finding("f2", "SECRET", Severity.HIGH, "test"),
            Finding("f3", "FILE", Severity.LOW, "test"),
        ]
        summary = get_scan_summary(findings)
        assert summary["total"] == 3
        assert summary["critical"] == 1
        assert summary["high"] == 1
        assert summary["low"] == 1
