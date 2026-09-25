import json
from click.testing import CliRunner
from devflow.cli import main

def test_scan_json_output(tmp_path):
    runner = CliRunner()
    
    # Create a test file with a secret
    test_file = tmp_path / "secret.py"
    test_file.write_text("api_key = 'AKIAIOSFODNN7EXAMPLE'")
    
    result = runner.invoke(main, ["scan", str(tmp_path), "--format", "json"])
    
    # Check that output is valid JSON
    assert result.exit_code == 1 # Has critical finding
    try:
        data = json.loads(result.output)
    except json.JSONDecodeError:
        assert False, f"Output is not valid JSON: {result.output}"
        
    assert "summary" in data
    assert "findings" in data
    assert len(data["findings"]) > 0
    
    finding = data["findings"][0]
    assert finding["severity"] == "CRITICAL"
    assert "AKIAIOSFODNN7EXAMPLE" not in finding["message"] # Should not echo secret
