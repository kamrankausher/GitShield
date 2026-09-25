import os
from devflow.config import load_config
import json

def test_gitshieldignore(tmp_path):
    # create .gitshieldignore
    gitignore_path = tmp_path / ".gitshieldignore"
    gitignore_path.write_text("tests/fixtures/\nregex:(?i)api_key\nstring:sk_test_123\n")
    
    config = load_config(str(tmp_path))
    assert "tests/fixtures/" in config["ignore_files"]
    assert "(?i)api_key" in config["ignore_patterns"]
    assert "sk_test_123" in config["ignore_strings"]

def test_pyproject_toml(tmp_path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('''
[tool.gitshield]
block_on_severity = "CRITICAL"
exclude_dirs = ["custom_dir"]

[tool.gitshield.ignore]
files = ["test_file.py"]
patterns = ["test_pattern"]
strings = ["test_string"]
''')
    
    config = load_config(str(tmp_path))
    assert config["block_on_severity"] == "CRITICAL"
    assert "custom_dir" in config["exclude_dirs"]
    assert "test_file.py" in config["ignore_files"]
    assert "test_pattern" in config["ignore_patterns"]
    assert "test_string" in config["ignore_strings"]
