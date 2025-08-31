from code_context_analyzer.analyzer.parsers.js_parser import JSParser


def test_js_parser_basic(tmp_path):
    code = """
        function greet() {
            console.log("hi");
        }
        class MyClass {
            constructor() {}
        }
    """
    file_path = tmp_path / "test.js"
    file_path.write_text(code)

    parser = JSParser()
    result = parser.parse_file(file_path)
    assert [{'name': 'greet'}] == result.get("functions", [])
    assert [{'methods': [], 'name': 'MyClass'}] == result.get("classes", [])
