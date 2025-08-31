from code_context_analyzer.analyzer.discovery import discover_files


def test_discover_files(tmp_path):
    # Create test files
    (tmp_path / "main.py").write_text("print('Hello')")
    (tmp_path / "script.js").write_text("console.log('hi');")

    # Pass string path, not Path object
    found = list(discover_files(str(tmp_path), max_files=1000, depth=3, ignore_tests=True, ignore_patterns=['build/, *migrations/']))
    paths = [str(p[0]) for p in found]

    assert any("main.py" in p for p in paths), "main.py not found"
    assert any("script.js" in p for p in paths), "script.js not found"
