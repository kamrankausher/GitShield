"""Tests for the rules engine module."""

from devflow.rules import (
    RuleSeverity,
    analyze_branch_name,
    analyze_commit_message,
    analyze_staged_files,
    has_blocking_issues,
    run_all_rules,
)


class TestCommitMessageRules:
    def test_empty_message(self):
        results = analyze_commit_message("")
        assert any(r.severity == RuleSeverity.BLOCK for r in results)

    def test_short_message(self):
        results = analyze_commit_message("fix")
        assert len(results) > 0

    def test_vague_message(self):
        results = analyze_commit_message("update")
        assert any("vague" in r.message.lower() for r in results)

    def test_good_message(self):
        results = analyze_commit_message("feat: add user authentication with JWT tokens")
        # Should have no blocks or warnings
        assert not any(r.severity == RuleSeverity.BLOCK for r in results)

    def test_conventional_commit(self):
        results = analyze_commit_message("fix: resolve login redirect bug")
        assert not any(r.rule_name == "no_conventional_prefix" for r in results)

    def test_long_message(self):
        long_msg = "feat: " + "a" * 100
        results = analyze_commit_message(long_msg)
        assert any("long" in r.message.lower() or "72" in r.message for r in results)

    def test_trailing_period(self):
        results = analyze_commit_message("feat: add authentication.")
        assert any(r.rule_name == "trailing_period" for r in results)


class TestStagedFilesRules:
    def test_normal_count(self):
        results = analyze_staged_files(["a.py", "b.py"])
        # Should not trigger too many files
        assert not any("too many" in r.message.lower() for r in results)

    def test_too_many_files(self):
        files = [f"file{i}.py" for i in range(20)]
        results = analyze_staged_files(files)
        assert any("too many" in r.message.lower() for r in results)

    def test_blocked_extension(self):
        results = analyze_staged_files(["app.exe"])
        assert any(r.severity == RuleSeverity.BLOCK for r in results)

    def test_blocked_zip(self):
        results = analyze_staged_files(["archive.zip"])
        assert any(r.severity == RuleSeverity.BLOCK for r in results)

    def test_safe_files(self):
        results = analyze_staged_files(["app.py", "utils.py"])
        assert not any(r.severity == RuleSeverity.BLOCK for r in results)

    def test_config_warning(self):
        results = analyze_staged_files(["config.json"])
        assert any("config" in r.message.lower() for r in results)


class TestBranchRules:
    def test_main_branch(self):
        results = analyze_branch_name("main")
        assert any("main" in r.message.lower() for r in results)

    def test_master_branch(self):
        results = analyze_branch_name("master")
        assert any(r.severity == RuleSeverity.WARNING for r in results)

    def test_good_branch(self):
        results = analyze_branch_name("feature/add-auth")
        assert not any(r.severity in (RuleSeverity.BLOCK, RuleSeverity.WARNING) for r in results)

    def test_bad_branch_name(self):
        results = analyze_branch_name("my weird branch")
        assert any(r.severity == RuleSeverity.BLOCK for r in results)


class TestAggregateRules:
    def test_run_all(self):
        results = run_all_rules(
            commit_message="fix",
            staged_files=["app.py"],
            branch_name="main",
        )
        assert len(results) > 0

    def test_blocking_check(self):
        results = run_all_rules(staged_files=["virus.exe"])
        assert has_blocking_issues(results)

    def test_no_blocking(self):
        results = run_all_rules(
            commit_message="feat: add new feature",
            staged_files=["app.py"],
            branch_name="feature/test",
        )
        assert not has_blocking_issues(results)
