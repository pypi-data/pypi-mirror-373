from abc import ABC, abstractmethod

from code_context_analyzer.dto.models import AnalysisResult


class BaseFormatter(ABC):
    """Abstract base class for all formatters"""

    def __init__(self,
                 depth: int = 4,
                 method_preview: int = 5,
                 doc_chars: int = 180,
                 truncate_total: int = None):
        self.depth = depth
        self.method_preview = method_preview
        self.doc_chars = doc_chars
        self.truncate_total = truncate_total

    @abstractmethod
    def format(self, analysis_result: AnalysisResult) -> str:
        """Format the analysis result"""
        pass

    def _truncate_if_needed(self, content: str) -> str:
        """Truncate content if truncate_total is set and content exceeds it"""
        if self.truncate_total and len(content) > self.truncate_total:
            return content[
                :self.truncate_total] + "\n\n... (truncated due to length)"
        return content
