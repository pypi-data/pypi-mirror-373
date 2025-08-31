import json
from typing import Any, Dict

from code_context_analyzer.dto.models import AnalysisResult

from .base import BaseFormatter


class JSONFormatter(BaseFormatter):
    """Formatter for JSON output"""

    def format(self, analysis_result: AnalysisResult) -> str:
        """Format analysis results as JSON"""
        result_dict = {
            "project_name": analysis_result.project_name,
            "summary": {
                "total_files": analysis_result.total_files,
                "total_classes": analysis_result.total_classes,
                "total_functions": analysis_result.total_functions,
                "total_constants": analysis_result.total_constants
            },
            "packages": self._format_packages(analysis_result.packages)
        }

        json_output = json.dumps(result_dict, indent=2)
        return self._truncate_if_needed(json_output)

    def _format_packages(self, packages) -> Dict[str, Any]:
        """Format packages for JSON output"""
        formatted_packages = {}
        for package in packages:
            formatted_packages[package.path] = {
                "modules": len(package.modules),
                "classes": package.class_count,
                "functions": package.function_count,
                "constants": package.constant_count,
                "module_details": [
                    self._format_module(module) for module in package.modules
                ]
            }
        return formatted_packages

    def _format_module(self, module):
        """Format a single module for JSON output"""
        return {
            "path": module.path,
            "classes": [
                self._format_class(cls) for cls in module.classes[:self.depth]
            ],
            "functions": [
                self._format_function(func) for func in
                module.functions[:self.depth]
            ],
            "constants": module.constants[:self.depth]
        }

    def _format_class(self, cls):
        """Format a single class for JSON output"""
        return {
            "name": cls.name,
            "bases": cls.bases,
            "docstring": cls.docstring[
                :self.doc_chars] if cls.docstring and self.doc_chars > 0 else None,
            "methods": [
                self._format_method(method) for method in
                cls.methods[:self.method_preview]
            ]
        }

    def _format_function(self, func):
        """Format a single function for JSON output"""
        return {
            "name": func.name,
            "signature": func.signature,
            "docstring": func.docstring[
                :self.doc_chars] if func.docstring and self.doc_chars > 0 else None
        }

    def _format_method(self, method):
        """Format a single method for JSON output"""
        return {
            "name": method.name,
            "signature": method.signature,
            "docstring": method.docstring[
                :self.doc_chars] if method.docstring and self.doc_chars > 0 else None
        }