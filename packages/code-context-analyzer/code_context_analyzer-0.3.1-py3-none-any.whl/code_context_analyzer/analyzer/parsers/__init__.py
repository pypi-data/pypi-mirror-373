
from .js_parser import JSParser
from .python_parser import PythonParser

registry = {
    'python': PythonParser(),
    'javascript': JSParser(),
}
