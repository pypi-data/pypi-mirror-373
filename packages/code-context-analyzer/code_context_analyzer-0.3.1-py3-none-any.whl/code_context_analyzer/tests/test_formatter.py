from code_context_analyzer.formatters.default import LegacyCodeFormatter


def test_formatter_basic():
    parsed_data = [
        {"path": "file1.py", "functions": [{"name": "foo", "sig":None}], "classes": [{'bases': [], 'doc': None, 'methods': [{'doc': None, 'name': '__post_init__', 'sig': '(self)'}], 'name': 'DiscovererConfig'}]},
        {"path": "file2.py", "functions": [{"name": "baz", "sig":None}], "classes": []}
    ]
    formatter = LegacyCodeFormatter(depth=2, method_preview=10, doc_chars=220)
    result = formatter.format(parsed_data)
    assert "**2** file(s)" in result
    assert "**1** class(es)" in result
    assert "**2** function(s)" in result
    assert "foo" in result
