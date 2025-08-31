from code_context_analyzer.analyzer.parsers.python_parser import PythonParser


def test_python_parser_basic(tmp_path):
    code = """
def hello():
    pass

class Foo:
    def bar(self):
        pass
"""
    file_path = tmp_path / "test.py"
    file_path.write_text(code)

    parser = PythonParser()
    result = parser.parse_file(file_path)
    assert [{'doc': None, 'name': 'hello', 'sig': '()'}] == result.get("functions", [])
    assert [{'bases': [], 'doc': None, 'methods': [{'doc': None, 'name': 'bar', 'sig': '(self)'}], 'name': 'Foo'}] == result.get("classes", [])
