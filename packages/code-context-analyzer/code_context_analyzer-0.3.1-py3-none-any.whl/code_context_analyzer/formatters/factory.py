from .base import BaseFormatter
from .default import LegacyCodeFormatter
from .html_formatter import HTMLFormatter
from .json_formatter import JSONFormatter
# from .text_formatter import TextFormatter
from .yaml_formatter import YAMLFormatter


class FormatterFactory:
    """Factory class to create formatters based on format type"""

    @staticmethod
    def create_formatter(format_type: str, **kwargs) -> BaseFormatter:
        """
        Create a formatter based on the specified format type

        -param format_type: One of 'json', 'html', 'text', 'yaml'
        -param kwargs: Formatter-specific parameters
        -return: An instance of the requested formatter
        """
        formatters = {
            'json': JSONFormatter,
            'html': HTMLFormatter,
            # 'text': TextFormatter,
            'yaml': YAMLFormatter,
            'legacy': LegacyCodeFormatter
        }

        if format_type not in formatters:
            raise ValueError(f"Unsupported format type: {format_type}. "
                             f"Supported types: {list(formatters.keys())}")

        return formatters[format_type](**kwargs)