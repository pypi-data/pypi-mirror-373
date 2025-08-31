from code_context_analyzer.dto.models import AnalysisResult

from .base import BaseFormatter


class HTMLFormatter(BaseFormatter):
    """Formatter for HTML output"""

    def format(self, analysis_result: AnalysisResult) -> str:
        """Format analysis results as HTML"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Code Analysis Report - {analysis_result.project_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #333; }}
                h2 {{ color: #555; margin-top: 30px; }}
                .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
                .package {{ margin: 20px 0; padding: 10px; border-left: 3px solid #007acc; }}
                .module {{ margin: 10px 0 10px 20px; }}
                .class {{ margin: 10px 0 10px 40px; }}
                .method {{ margin: 5px 0 5px 60px; font-family: monospace; }}
                .docstring {{ color: #666; font-style: italic; margin-left: 10px; }}
            </style>
        </head>
        <body>
            <h1>Project '{analysis_result.project_name}' Analysis Report</h1>

            <div class="summary">
                <strong>{analysis_result.total_files}</strong> file(s), 
                <strong>{analysis_result.total_classes}</strong> class(es), 
                <strong>{analysis_result.total_functions}</strong> function(s), 
                <strong>{analysis_result.total_constants}</strong> constant(s)
            </div>

            {self._format_packages(analysis_result.packages)}
        </body>
        </html>
        """

        return self._truncate_if_needed(html_content)

    def _format_packages(self, packages) -> str:
        """Format packages for HTML output"""
        packages_html = []
        for package in packages:
            packages_html.append(f"""
            <div class="package">
                <h2>Package: {package.path}</h2>
                <div>{len(package.modules)} modules, {package.class_count} classes, 
                {package.function_count} functions, {package.constant_count} constants</div>
                {self._format_modules(package.modules)}
            </div>
            """)
        return "".join(packages_html)

    def _format_modules(self, modules) -> str:
        """Format modules for HTML output"""
        modules_html = []
        for module in modules:
            modules_html.append(f"""
            <div class="module">
                <h3>Module: {module.path}</h3>
                {self._format_classes(module.classes)}
                {self._format_functions(module.functions)}
                {self._format_constants(module.constants)}
            </div>
            """)
        return "".join(modules_html)

    def _format_classes(self, classes) -> str:
        """Format classes for HTML output"""
        if not classes:
            return ""

        classes_html = ["<h4>Classes:</h4>"]
        for cls in classes[:self.depth]:
            classes_html.append(f"""
            <div class="class">
                <strong>{cls.name}</strong>
                {f"({', '.join(cls.bases)})" if cls.bases else ""}
                {f'<div class="docstring">{cls.docstring[:self.doc_chars] + "..." if cls.docstring and len(cls.docstring) > self.doc_chars else cls.docstring}</div>' if cls.docstring and self.doc_chars > 0 else ""}
                {self._format_methods(cls.methods)}
            </div>
            """)
        return "".join(classes_html)

    def _format_methods(self, methods) -> str:
        """Format methods for HTML output"""
        if not methods:
            return ""

        methods_html = ["<div>Methods:</div>"]
        for method in methods[:self.method_preview]:
            methods_html.append(f"""
            <div class="method">
                {method.name}{method.signature}
                {f'<div class="docstring">{method.docstring[:self.doc_chars] + "..." if method.docstring and len(method.docstring) > self.doc_chars else method.docstring}</div>' if method.docstring and self.doc_chars > 0 else ""}
            </div>
            """)
        return "".join(methods_html)

    def _format_functions(self, functions) -> str:
        """Format functions for HTML output"""
        if not functions:
            return ""

        functions_html = ["<h4>Functions:</h4>"]
        for func in functions[:self.depth]:
            functions_html.append(f"""
            <div class="method">
                {func.name}{func.signature}
                {f'<div class="docstring">{func.docstring[:self.doc_chars] + "..." if func.docstring and len(func.docstring) > self.doc_chars else func.docstring}</div>' if func.docstring and self.doc_chars > 0 else ""}
            </div>
            """)
        return "".join(functions_html)

    def _format_constants(self, constants) -> str:
        """Format constants for HTML output"""
        if not constants:
            return ""

        constants_html = ["<h4>Constants:</h4>"]
        for constant in constants[:self.depth]:
            constants_html.append(f"<div class='method'>{constant}</div>")
        return "".join(constants_html)