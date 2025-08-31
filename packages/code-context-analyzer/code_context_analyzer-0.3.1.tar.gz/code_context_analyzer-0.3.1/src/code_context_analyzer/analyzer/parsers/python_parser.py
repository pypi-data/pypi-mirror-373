"""Python parser using the builtin ast and optional tree-sitter."""
import ast
from pathlib import Path
from typing import Any, Dict


class PythonParser:
    def parse_file(self, path: str) -> Dict[str, Any]:
        source = Path(path).read_text(encoding='utf-8')
        try:
            tree = ast.parse(source)
        except SyntaxError:
            # Binary or incompatible file; return minimal
            return {"path": path, "error": "syntax_error"}

        module = {"path": path, "classes": [], "functions": [], "constants": []}

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                methods = []
                for m in node.body:
                    if isinstance(m, ast.FunctionDef):
                        sig = self._sig_from_function(m)
                        methods.append({"name": m.name, "sig": sig, "doc": ast.get_docstring(m)})
                module['classes'].append({"name": node.name, "bases": [ast.unparse(b) if hasattr(ast, 'unparse') else getattr(b, 'id', '?') for b in node.bases], "doc": ast.get_docstring(node), "methods": methods})
            elif isinstance(node, ast.FunctionDef):
                module['functions'].append({"name": node.name, "sig": self._sig_from_function(node), "doc": ast.get_docstring(node)})
            elif isinstance(node, ast.Assign):
                # top-level constants heuristics: UPPERCASE names
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        module['constants'].append(target.id)
        return module

    def _sig_from_function(self, node: ast.FunctionDef) -> str:
        parts = []
        for arg in node.args.args:
            parts.append(arg.arg)
        if node.args.vararg:
            parts.append('*' + node.args.vararg.arg)
        for kw in node.args.kwonlyargs:
            parts.append(kw.arg)
        if node.args.kwarg:
            parts.append('**' + node.args.kwarg.arg)
        return '(' + ', '.join(parts) + ')'
