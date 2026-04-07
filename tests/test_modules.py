"""Tests for recovery, health, AI engine, and other modules."""

import pytest
from devflow.recovery import (
    undo_last_commit, amend_last_commit, remove_file_from_history,
    unstage_file, recover_detached_head, recover_secret_leak,
    get_recovery_options, execute_recovery,
)
from devflow.ai_engine import generate_ai_suggestion, generate_detailed_analysis
from devflow.mentor import explain_warning, get_mentor_advice, get_progressive_tip
from devflow.gitignore_gen import detect_project_types, generate_gitignore
from devflow.github_assistant import get_guide, get_available_topics


class TestRecovery:
    def test_undo_soft(self):
        action = undo_last_commit("soft")
        assert "reset --soft" in action.commands[0]
        assert action.risk_level == "safe"

    def test_undo_hard(self):
        action = undo_last_commit("hard")
        assert "reset --hard" in action.commands[0]
        assert action.risk_level == "dangerous"

    def test_amend(self):
        action = amend_last_commit()
        assert any("amend" in c for c in action.commands)

    def test_remove_from_history(self):
        action = remove_file_from_history(".env")
        assert ".env" in " ".join(action.commands)
        assert action.risk_level == "dangerous"

    def test_unstage(self):
        action = unstage_file("test.py")
        assert "test.py" in action.commands[0]
        assert action.risk_level == "safe"

    def test_detached_head(self):
        action = recover_detached_head()
        assert "checkout -b" in " ".join(action.commands)

    def test_secret_leak(self):
        action = recover_secret_leak(".env")
        assert ".env" in " ".join(action.commands)
        assert action.risk_level == "dangerous"

    def test_recovery_options(self):
        options = get_recovery_options()
        assert len(options) > 10
        assert all("id" in o and "label" in o for o in options)

    def test_execute_recovery(self):
        action = execute_recovery("undo_soft")
        assert action is not None
        assert action.risk_level == "safe"

    def test_execute_unknown(self):
        action = execute_recovery("nonexistent")
        assert action is None


class TestAIEngine:
    def test_commit_suggestion(self):
        result = generate_ai_suggestion("commit message is too vague")
        assert len(result) > 10

    def test_branch_suggestion(self):
        result = generate_ai_suggestion("main branch warning")
        assert len(result) > 10

    def test_security_suggestion(self):
        result = generate_ai_suggestion("secret detected in code")
        assert len(result) > 10

    def test_fallback(self):
        result = generate_ai_suggestion("xyxzqwerty random gibberish")
        assert len(result) > 10

    def test_detailed_analysis(self):
        result = generate_detailed_analysis("secret detected", "CRITICAL")
        assert "suggestion" in result
        assert "impact" in result
        assert "action_items" in result


class TestMentor:
    def test_explain_warning(self):
        result = explain_warning("commit message too short")
        assert result is not None
        assert "suggestion" in result

    def test_explain_branch(self):
        result = explain_warning("main branch issue")
        assert result is not None

    def test_explain_unknown(self):
        result = explain_warning("xyznonexistent")
        assert result is None

    def test_mentor_advice(self):
        advice = get_mentor_advice("commit message too short")
        assert advice is not None
        assert advice.suggestion

    def test_progressive_tip(self):
        tip = get_progressive_tip(5, "commit message")
        assert tip is not None
        assert "🧠" in tip

    def test_progressive_tip_low_count(self):
        tip = get_progressive_tip(1, "commit message")
        assert tip is None


class TestGitignoreGen:
    def test_detect_types(self):
        types = detect_project_types(".")
        assert isinstance(types, list)
        assert len(types) > 0

    def test_generate(self):
        content = generate_gitignore(".", ["python"])
        assert ".env" in content
        assert "__pycache__" in content

    def test_generate_node(self):
        content = generate_gitignore(".", ["node"])
        assert "node_modules" in content


class TestGitHubAssistant:
    def test_pr_guide(self):
        guide = get_guide("pr")
        assert guide.title
        assert len(guide.steps) > 0

    def test_contribute_guide(self):
        guide = get_guide("contribute")
        assert "fork" in " ".join(s["step"].lower() for s in guide.steps)

    def test_unknown_topic(self):
        guide = get_guide("nonexistent")
        assert guide is not None

    def test_available_topics(self):
        topics = get_available_topics()
        assert len(topics) > 5
        assert "pr" in topics
