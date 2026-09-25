import os
import sys
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from typing import Dict, Any, List

def load_config(cwd: str = ".") -> Dict[str, Any]:
    """Load configuration from pyproject.toml or .gitshield.toml."""
    config = {
        "block_on_severity": "HIGH",
        "exclude_dirs": ["venv", ".git", "__pycache__", "node_modules", ".tox", ".mypy_cache", ".pytest_cache", "dist", "build", ".eggs", "htmlcov", ".venv", "env", ".env", "vendor", "migrations"],
        "ignore_patterns": [],
        "ignore_files": [],
        "ignore_strings": []
    }
    
    # Try .gitshield.toml first
    gitshield_toml = os.path.join(cwd, ".gitshield.toml")
    pyproject_toml = os.path.join(cwd, "pyproject.toml")
    
    parsed_config = {}
    if os.path.exists(gitshield_toml):
        try:
            with open(gitshield_toml, "rb") as f:
                parsed_config = tomllib.load(f)
        except Exception:
            pass
    elif os.path.exists(pyproject_toml):
        try:
            with open(pyproject_toml, "rb") as f:
                pyproject = tomllib.load(f)
                parsed_config = pyproject.get("tool", {}).get("gitshield", {})
        except Exception:
            pass

    if "block_on_severity" in parsed_config:
        config["block_on_severity"] = parsed_config["block_on_severity"]
    if "exclude_dirs" in parsed_config:
        config["exclude_dirs"].extend(parsed_config["exclude_dirs"])
    
    if "ignore" in parsed_config:
        ignore_cfg = parsed_config["ignore"]
        if "patterns" in ignore_cfg:
            config["ignore_patterns"].extend(ignore_cfg["patterns"])
        if "files" in ignore_cfg:
            config["ignore_files"].extend(ignore_cfg["files"])
        if "strings" in ignore_cfg:
            config["ignore_strings"].extend(ignore_cfg["strings"])
            
    # Load .gitshieldignore if exists
    gitshieldignore = os.path.join(cwd, ".gitshieldignore")
    if os.path.exists(gitshieldignore):
        try:
            with open(gitshieldignore, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("regex:"):
                        config["ignore_patterns"].append(line[6:].strip())
                    elif line.startswith("string:"):
                        config["ignore_strings"].append(line[7:].strip())
                    else:
                        config["ignore_files"].append(line)
        except Exception:
            pass
            
    return config
