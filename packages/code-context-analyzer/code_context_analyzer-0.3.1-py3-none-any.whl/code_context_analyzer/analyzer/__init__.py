"""Top-level orchestration."""
from code_context_analyzer.formatters.default import LegacyCodeFormatter
from code_context_analyzer.formatters.factory import FormatterFactory
# from .formatter import Formatter
from code_context_analyzer.utils.dto_converter import create_analysis_result

from .discovery import create_file_discoverer
from .parsers import registry


class Analyzer:
    max_files = 1000
    depth = 3
    ignore_tests = True
    method_preview = 7
    doc_chars = 180
    # formatter_class = LegacyCodeFormatter

    def __init__(
        self,
        path,
        max_files: int,
        # depth:int = 3,
        ignore_tests: bool = True,
            ignore=None,
    ):
        if ignore is None:
            ignore = []
        self.path = path
        self.max_files = max_files
        # self.depth = depth
        self.ignore_tests = ignore_tests
        self.ignore = ignore

    def run_analysis(self):

        discoverer = create_file_discoverer(
            max_files=self.max_files,
            # depth=self.depth,
            ignore_tests=self.ignore_tests,
            ignore_patterns=self.ignore,
        )
        files = discoverer.discover_files(self.path)

        parsed = []
        for fpath, lang in files:
            # lang = fpath.split(".")[-1]
            parser = registry.get(lang)
            if not parser:
                continue
            try:
                parsed.append(parser.parse_file(fpath))
            except Exception as e:
                # tolerate failures; log in v2
                parsed.append({"path": fpath, "error": str(e)})

        formatter = self.get_formatter()

        if isinstance(formatter, LegacyCodeFormatter):
            report = formatter.format(parsed)
        else:
            report_model = create_analysis_result(parsed)
            report = formatter.format(report_model)

        return report

    def get_formatter(self, name: str = None):
        if getattr(self, "formatter_class", None) is None and not name:
            name = "legacy"

        return FormatterFactory.create_formatter(
            format_type=name,
            depth=self.depth,
            method_preview=self.method_preview,
            doc_chars=self.doc_chars,
        )
