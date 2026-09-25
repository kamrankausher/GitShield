"""
DevFlow AI++ — Behavior Intelligence & Memory Module
=====================================================
Tracks developer behavior patterns, mistakes, and habits over time.
Provides statistics, skill level detection, and personalized recommendations.

Features:
- Persistent JSON-based memory
- Session tracking with timestamps
- Warning frequency analysis
- Skill level detection (beginner → intermediate → advanced)
- Behavior pattern analysis
- Statistics generation
- Memory cleanup
"""

import json
import os
from datetime import datetime
from typing import Dict, List

from devflow import __version__

MEMORY_FILE = ".devflow_memory.json"

# ═══════════════════════════════════════════════════════════════
# DEFAULT MEMORY STRUCTURE
# ═══════════════════════════════════════════════════════════════
DEFAULT_MEMORY = {
    "version": __version__,
    "created_at": "",
    "updated_at": "",
    "total_sessions": 0,
    "total_commits_analyzed": 0,
    "total_scans": 0,
    "warnings": {},          # warning_key → count
    "blocks": {},            # block_key → count
    "sessions": [],          # list of session summaries
    "skill_level": "beginner",
    "streak_days": 0,
    "last_active_date": "",
    "resolved_issues": 0,
    "settings": {
        "auto_fix": False,
        "strict_mode": False,
        "show_tips": True,
    },
}


# ═══════════════════════════════════════════════════════════════
# MEMORY I/O
# ═══════════════════════════════════════════════════════════════
def _get_memory_path(repo_path: str = ".") -> str:
    """Get the memory file path for a repository."""
    return os.path.join(repo_path, MEMORY_FILE)


def load_memory(repo_path: str = ".") -> Dict:
    """Load memory from file, creating default if needed."""
    path = _get_memory_path(repo_path)

    if not os.path.exists(path):
        memory = DEFAULT_MEMORY.copy()
        memory["created_at"] = datetime.now().isoformat()
        return memory

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        # Migration: old format → new format
        if "version" not in data:
            migrated = DEFAULT_MEMORY.copy()
            migrated["created_at"] = datetime.now().isoformat()
            migrated["warnings"] = data  # Old format was just warnings
            return migrated

        return data

    except (json.JSONDecodeError, OSError):
        return DEFAULT_MEMORY.copy()


def save_memory(data: Dict, repo_path: str = "."):
    """Save memory to file."""
    path = _get_memory_path(repo_path)
    data["updated_at"] = datetime.now().isoformat()

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except OSError:
        pass


# ═══════════════════════════════════════════════════════════════
# MEMORY UPDATES
# ═══════════════════════════════════════════════════════════════
def update_memory(warnings: List[str], repo_path: str = ".") -> Dict:
    """
    Update memory with new warnings from a session.
    Backward compatible with old code that passes list of warning strings.
    """
    memory = load_memory(repo_path)

    # Ensure keys exist
    if "warnings" not in memory or not isinstance(memory["warnings"], dict):
        memory["warnings"] = {}
    if "blocks" not in memory:
        memory["blocks"] = {}

    for w in warnings:
        memory["warnings"][w] = memory["warnings"].get(w, 0) + 1

    memory["total_commits_analyzed"] = memory.get("total_commits_analyzed", 0) + 1

    # Update session
    _record_session(memory, warnings)

    # Recalculate skill level
    memory["skill_level"] = _calculate_skill_level(memory)

    # Update streak
    _update_streak(memory)

    save_memory(memory, repo_path)
    return memory.get("warnings", {})


def record_scan(findings_count: int, repo_path: str = "."):
    """Record a security scan in memory."""
    memory = load_memory(repo_path)
    memory["total_scans"] = memory.get("total_scans", 0) + 1
    save_memory(memory, repo_path)


def record_block(block_type: str, repo_path: str = "."):
    """Record a blocked action."""
    memory = load_memory(repo_path)
    if "blocks" not in memory:
        memory["blocks"] = {}
    memory["blocks"][block_type] = memory["blocks"].get(block_type, 0) + 1
    save_memory(memory, repo_path)


def record_resolved(repo_path: str = "."):
    """Record a resolved issue."""
    memory = load_memory(repo_path)
    memory["resolved_issues"] = memory.get("resolved_issues", 0) + 1
    save_memory(memory, repo_path)


# ═══════════════════════════════════════════════════════════════
# SESSION TRACKING
# ═══════════════════════════════════════════════════════════════
def _record_session(memory: Dict, warnings: List[str]):
    """Record a session summary."""
    if "sessions" not in memory:
        memory["sessions"] = []

    session = {
        "timestamp": datetime.now().isoformat(),
        "warning_count": len(warnings),
        "warnings": warnings[:5],  # Keep first 5 for summary
    }
    memory["sessions"].append(session)
    memory["total_sessions"] = memory.get("total_sessions", 0) + 1

    # Keep only last 100 sessions
    if len(memory["sessions"]) > 100:
        memory["sessions"] = memory["sessions"][-100:]


def _update_streak(memory: Dict):
    """Update the active streak (consecutive days using devflow)."""
    today = datetime.now().strftime("%Y-%m-%d")
    last = memory.get("last_active_date", "")

    if last == today:
        return  # Same day, no change

    if last:
        try:
            last_date = datetime.strptime(last, "%Y-%m-%d")
            delta = (datetime.now() - last_date).days
            if delta == 1:
                memory["streak_days"] = memory.get("streak_days", 0) + 1
            elif delta > 1:
                memory["streak_days"] = 1
        except ValueError:
            memory["streak_days"] = 1
    else:
        memory["streak_days"] = 1

    memory["last_active_date"] = today


# ═══════════════════════════════════════════════════════════════
# SKILL LEVEL DETECTION
# ═══════════════════════════════════════════════════════════════
def _calculate_skill_level(memory: Dict) -> str:
    """Determine developer skill level based on behavior patterns."""
    total_commits = memory.get("total_commits_analyzed", 0)
    warnings = memory.get("warnings", {})
    total_warnings = sum(warnings.values())

    if total_commits < 5:
        return "beginner"

    # Calculate warning ratio
    warning_ratio = total_warnings / max(total_commits, 1)

    if total_commits >= 50 and warning_ratio < 0.2:
        return "advanced"
    elif total_commits >= 20 and warning_ratio < 0.5:
        return "intermediate"
    else:
        return "beginner"


# ═══════════════════════════════════════════════════════════════
# STATISTICS GENERATION
# ═══════════════════════════════════════════════════════════════
def get_statistics(repo_path: str = ".") -> Dict:
    """Generate comprehensive statistics from memory."""
    memory = load_memory(repo_path)
    warnings = memory.get("warnings", {})

    # Top issues
    sorted_warnings = sorted(warnings.items(), key=lambda x: x[1], reverse=True)
    top_issues = sorted_warnings[:5]

    # Category breakdown
    categories = {
        "commit": 0,
        "security": 0,
        "branch": 0,
        "files": 0,
        "other": 0,
    }

    for key, count in warnings.items():
        key_lower = key.lower()
        if "commit" in key_lower or "message" in key_lower:
            categories["commit"] += count
        elif "secret" in key_lower or "sensitive" in key_lower or "key" in key_lower:
            categories["security"] += count
        elif "branch" in key_lower or "main" in key_lower:
            categories["branch"] += count
        elif "file" in key_lower or "untracked" in key_lower:
            categories["files"] += count
        else:
            categories["other"] += count

    total_warnings = sum(warnings.values())
    total_commits = memory.get("total_commits_analyzed", 0)

    # Improvement score (0-100)
    if total_commits >= 5:
        recent_sessions = memory.get("sessions", [])[-10:]
        if recent_sessions:
            recent_avg = sum(s.get("warning_count", 0) for s in recent_sessions) / len(recent_sessions)
            old_sessions = memory.get("sessions", [])[:10]
            old_avg = sum(s.get("warning_count", 0) for s in old_sessions) / max(len(old_sessions), 1)
            improvement = max(0, min(100, int(100 - (recent_avg / max(old_avg, 0.1)) * 100)))
        else:
            improvement = 50
    else:
        improvement = 0

    return {
        "total_commits_analyzed": total_commits,
        "total_warnings": total_warnings,
        "total_scans": memory.get("total_scans", 0),
        "total_sessions": memory.get("total_sessions", 0),
        "skill_level": memory.get("skill_level", "beginner"),
        "streak_days": memory.get("streak_days", 0),
        "top_issues": top_issues,
        "categories": categories,
        "improvement_score": improvement,
        "resolved_issues": memory.get("resolved_issues", 0),
        "blocks_prevented": sum(memory.get("blocks", {}).values()),
    }


def get_behavior_insights(repo_path: str = ".") -> List[str]:
    """Generate behavior-based insights and recommendations."""
    stats = get_statistics(repo_path)
    insights = []

    # Commit message patterns
    cats = stats["categories"]
    if cats.get("commit", 0) > 5:
        insights.append(
            "📊 You frequently get commit message warnings. "
            "Consider using a commit template: git config commit.template .gitmessage"
        )

    # Security patterns
    if cats.get("security", 0) > 0:
        insights.append(
            "🔒 Security issues detected in your history. "
            "Run 'devflow init' to install pre-commit hooks that prevent secret leaks."
        )

    # Branch patterns
    if cats.get("branch", 0) > 3:
        insights.append(
            "🌿 You often commit to main/master. "
            "Make feature branches your default workflow: git checkout -b feature/name"
        )

    # File patterns
    if cats.get("files", 0) > 3:
        insights.append(
            "📁 Frequent file-related warnings. "
            "Update your .gitignore with 'devflow gitignore' and stage files selectively."
        )

    # Improvement
    if stats["improvement_score"] > 70:
        insights.append(
            "🚀 Great improvement! Your recent commits have significantly fewer issues."
        )
    elif stats["improvement_score"] < 30 and stats["total_commits_analyzed"] > 10:
        insights.append(
            "📈 Room for improvement. Focus on your top issues and try to address them."
        )

    # Streak
    if stats["streak_days"] > 7:
        insights.append(
            f"🔥 Amazing! {stats['streak_days']}-day streak of using DevFlow. Keep it up!"
        )

    # Skill level
    insights.append(f"🎯 Current skill level: {stats['skill_level'].upper()}")

    return insights


def clear_memory(repo_path: str = "."):
    """Clear all memory data."""
    path = _get_memory_path(repo_path)
    if os.path.exists(path):
        os.remove(path)
