"""A simple JS/TS parser using heuristics. For production, plug tree-sitter JS grammar."""
import re
from pathlib import Path
from typing import Any, Dict

RE_FN = re.compile(r'function\s+(\w+)\s*\(')
RE_CLASS = re.compile(r'class\s+(\w+)')
RE_EXPORT_FN = re.compile(r'export\s+function\s+(\w+)')


class JSParser:
    def parse_file(self, path: str) -> Dict[str, Any]:
        text = Path(path).read_text(encoding='utf-8', errors='ignore')
        module = {"path": path, "classes": [], "functions": []}
        for m in RE_CLASS.finditer(text):
            module['classes'].append({"name": m.group(1), "methods": []})
        for m in RE_FN.finditer(text):
            module['functions'].append({"name": m.group(1)})
        for m in RE_EXPORT_FN.finditer(text):
            module['functions'].append({"name": m.group(1)})
        return module
