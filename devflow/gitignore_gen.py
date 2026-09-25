"""
DevFlow AI++ — Smart .gitignore Generator
==========================================
Auto-detects project type and generates appropriate .gitignore files.
"""

import os
import subprocess
from typing import List, Optional

PROJECT_INDICATORS = {
    "python": {"files": ["setup.py", "pyproject.toml", "requirements.txt"], "exts": {".py"}},
    "node": {"files": ["package.json"], "exts": {".js", ".ts", ".jsx", ".tsx"}},
    "java": {"files": ["pom.xml", "build.gradle"], "exts": {".java"}},
    "go": {"files": ["go.mod"], "exts": {".go"}},
    "rust": {"files": ["Cargo.toml"], "exts": {".rs"}},
    "ruby": {"files": ["Gemfile"], "exts": {".rb"}},
    "csharp": {"files": [], "exts": {".cs", ".csproj", ".sln"}},
    "cpp": {"files": ["CMakeLists.txt", "Makefile"], "exts": {".cpp", ".hpp", ".c", ".h"}},
    "flutter": {"files": ["pubspec.yaml"], "exts": {".dart"}},
}

TEMPLATES = {
    "base": (
        "# OS & Editor\n.DS_Store\nThumbs.db\ndesktop.ini\n*.swp\n*.swo\n*~\n"
        ".idea/\n.vscode/\n\n# Secrets\n.env\n.env.local\n.env.*.local\n"
        ".env.production\n*.pem\n*.key\n*.p12\n*.pfx\n"
    ),
    "python": (
        "\n# Python\n__pycache__/\n*.py[cod]\n*$py.class\n*.so\n*.egg-info/\n"
        "dist/\nbuild/\neggs/\n*.egg\n.eggs/\nvenv/\nenv/\n.venv/\n"
        ".pytest_cache/\n.coverage\nhtmlcov/\n.mypy_cache/\n*.tar.gz\n*.whl\n"
        ".devflow_memory.json\n"
    ),
    "node": (
        "\n# Node.js\nnode_modules/\nnpm-debug.log*\nyarn-debug.log*\n"
        "dist/\nbuild/\n.cache/\ncoverage/\n.env\n.env.local\n*.tgz\n"
    ),
    "java": "\n# Java\n*.class\n*.jar\n*.war\ntarget/\n.gradle/\nbuild/\nout/\n",
    "go": "\n# Go\n*.exe\n*.dll\n*.so\n*.dylib\n*.test\n*.out\nvendor/\n",
    "rust": "\n# Rust\ntarget/\nCargo.lock\n**/*.rs.bk\n",
    "ruby": "\n# Ruby\n*.gem\n.bundle/\nvendor/bundle/\nlog/*.log\ntmp/\n",
    "csharp": "\n# C#\n[Bb]in/\n[Oo]bj/\n*.suo\n*.user\npackages/\n",
    "cpp": "\n# C/C++\n*.o\n*.obj\n*.exe\n*.out\nbuild/\ncmake-build-*/\n",
    "flutter": "\n# Flutter\n.dart_tool/\n.flutter-plugins\nbuild/\n.pub-cache/\n",
}

EXCLUDE_DIRS = {"venv", ".git", "__pycache__", "node_modules", ".venv"}


def detect_project_types(repo_path: str = ".") -> List[str]:
    """Auto-detect project type(s)."""
    detected = set()
    for ptype, ind in PROJECT_INDICATORS.items():
        for f in ind.get("files", []):
            if os.path.exists(os.path.join(repo_path, f)):
                detected.add(ptype)
                break
    return list(detected) if detected else ["base"]


def generate_gitignore(repo_path: str = ".", project_types: Optional[List[str]] = None) -> str:
    """Generate .gitignore content."""
    if project_types is None:
        project_types = detect_project_types(repo_path)
    content = TEMPLATES["base"]
    for ptype in project_types:
        content += TEMPLATES.get(ptype, "")
    return content


def get_missing_patterns(repo_path: str = ".") -> List[str]:
    """Find patterns missing from .gitignore."""
    gitignore_path = os.path.join(repo_path, ".gitignore")
    existing = set()
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, encoding="utf-8") as f:
                for line in f:
                    s = line.strip()
                    if s and not s.startswith("#"):
                        existing.add(s)
        except OSError:
            pass

    recommended_content = generate_gitignore(repo_path)
    recommended = set()
    for line in recommended_content.splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            recommended.add(s)
    return sorted(recommended - existing)


def get_tracked_but_should_ignore(repo_path: str = ".") -> List[str]:
    """Find tracked files that should be ignored."""
    bad_names = {".env", ".env.local", ".DS_Store", "Thumbs.db", ".devflow_memory.json"}
    bad_exts = {".pyc", ".pyo", ".class", ".o", ".log", ".swp"}
    result = []
    try:
        out = subprocess.run(
            ["git", "ls-files"], capture_output=True, text=True,
            cwd=repo_path, timeout=10, encoding="utf-8", errors="replace",
            stdin=subprocess.DEVNULL,
        )
        if out.returncode == 0:
            for fp in out.stdout.splitlines():
                bn = os.path.basename(fp)
                _, ext = os.path.splitext(fp)
                if bn in bad_names or ext in bad_exts:
                    result.append(fp)
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass
    return result


def write_gitignore(repo_path: str = ".", project_types: Optional[List[str]] = None) -> str:
    """Generate and write .gitignore file."""
    content = generate_gitignore(repo_path, project_types)
    with open(os.path.join(repo_path, ".gitignore"), "w", encoding="utf-8") as f:
        f.write(content)
    return content
