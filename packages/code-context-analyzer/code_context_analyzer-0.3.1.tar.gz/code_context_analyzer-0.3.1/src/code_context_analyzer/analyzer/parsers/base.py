from typing import Any, Dict, Protocol


class ParserProtocol(Protocol):
    def parse_file(self, path: str) -> Dict[str, Any]:
        ...
