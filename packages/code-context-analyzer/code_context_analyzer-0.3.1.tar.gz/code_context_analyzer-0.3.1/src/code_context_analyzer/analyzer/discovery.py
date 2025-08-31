import fnmatch
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Set, Tuple

# Default ignore patterns that will always be applied
DEFAULT_IGNORE_PATTERNS = [
    # Hidden files and directories
    ".*",
    "#*#",
    "*~",
    "*.swp",
    "*.swo",

    # Version control directories
    ".git/",
    ".svn/",
    ".hg/",

    # Language-specific build/output directories
    "__pycache__/",
    "node_modules/",
    "dist/",
    "build/",
    "out/",
    "bin/",
    "obj/",
    ".venv/",
    "venv/",
    "env/",
    ".mypy_cache/",
    ".pytest_cache/",
    ".ruff_cache/",

    # Common IDE directories
    ".idea/",
    ".vscode/",
    ".vs/",

    # OS-specific files
    ".DS_Store",
    "Thumbs.db",

    # Common backup patterns
    "*.bak",
    "*.backup",
    "*.tmp",
    "*.min.js",
]

# Framework detection patterns
FRAMEWORK_INDICATORS = {
    'django': [
        {'type': 'file', 'path': 'manage.py'},
        {'type': 'file', 'path': '*/settings.py'},
        {'type': 'dir', 'path': '*/migrations'},
    ],
    'flask': [
        {'type': 'file', 'path': 'app.py', 'content': ['Flask', 'from flask']},
        {'type': 'file', 'path': 'application.py',
         'content': ['Flask', 'from flask']},
        {'type': 'file', 'path': '*/__init__.py',
         'content': ['Flask', 'from flask']},
    ],
    'react': [
        {'type': 'file', 'path': 'package.json',
         'content': ['react', 'react-scripts']},
        {'type': 'file', 'path': 'src/App.js'},
        {'type': 'file', 'path': 'src/App.jsx'},
    ],
    'vue': [
        {'type': 'file', 'path': 'package.json',
         'content': ['vue', '@vue/cli']},
        {'type': 'file', 'path': 'vue.config.js'},
        {'type': 'file', 'path': 'src/App.vue'},
    ],
    'angular': [
        {'type': 'file', 'path': 'package.json', 'content': ['@angular/core']},
        {'type': 'file', 'path': 'angular.json'},
        {'type': 'file', 'path': 'src/main.ts'},
    ],
    'laravel': [
        {'type': 'file', 'path': 'artisan'},
        {'type': 'file', 'path': 'server.php'},
        {'type': 'dir', 'path': 'database/migrations'},
    ],
    'rails': [
        {'type': 'file', 'path': 'Gemfile', 'content': ['rails']},
        {'type': 'file', 'path': 'config/routes.rb'},
        {'type': 'dir', 'path': 'db/migrate'},
    ],
}

# Framework-specific ignore patterns
FRAMEWORK_IGNORE_PATTERNS = {
    'django': [
        '*/migrations/*',
        '*.sqlite3',
        '*.log',
        'media/',
        'staticfiles/',
    ],
    'flask': [
        'instance/',
        '*.log',
    ],
    'react': [
        'build/',
        '.next/',
        'out/',
        'public/',
    ],
    'vue': [
        'dist/',
        'public/',
    ],
    'angular': [
        'dist/',
        'e2e/',
    ],
    'laravel': [
        'storage/framework/',
        'bootstrap/cache/',
        '*.log',
    ],
    'rails': [
        'log/',
        'tmp/',
        'storage/',
    ],
}

# Language extension mapping
EXTENSION_MAP = {
    'python': ['.py', '.pyw', '.pyx', '.pxd', '.pyi'],
    'javascript': ['.js', '.jsx', '.mjs', '.cjs'],
    'typescript': ['.ts', '.tsx'],
    'java': ['.java'],
    'c': ['.c', '.h'],
    'cpp': ['.cpp', '.cc', '.cxx', '.hpp', '.hh', '.hxx'],
    'csharp': ['.cs'],
    'go': ['.go'],
    'rust': ['.rs'],
    'ruby': ['.rb'],
    'php': ['.php'],
    'swift': ['.swift'],
    'kotlin': ['.kt', '.kts'],
    'scala': ['.scala'],
    'html': ['.html', '.htm'],
    'css': ['.css', '.scss', '.sass', '.less'],
    'json': ['.json'],
    'yaml': ['.yaml', '.yml'],
    'markdown': ['.md', '.markdown'],
    'xml': ['.xml'],
    'sql': ['.sql'],
    'shell': ['.sh', '.bash', '.zsh'],
}

# Test file patterns for different languages
TEST_FILE_PATTERNS = [
    # Python
    "test_*.py", "*_test.py",
    # JavaScript/TypeScript
    "test*.js", "*.test.js", "*.spec.js",
    "test*.ts", "*.test.ts", "*.spec.ts",
    # Java
    "*Test.java", "*Tests.java",
    # Go
    "*_test.go",
    # Ruby
    "*_test.rb", "*_spec.rb",
]


@dataclass
class DiscovererConfig:
    max_files: int = 1000
    # depth: int = 5
    ignore_tests: bool = True
    ignore_patterns: List[str] = None
    follow_symlinks: bool = False

    def __post_init__(self):
        if self.ignore_patterns is None:
            self.ignore_patterns = []

        # Always include default patterns
        self.ignore_patterns = DEFAULT_IGNORE_PATTERNS + self.ignore_patterns


class FrameworkDetector:
    """Detects frameworks used in a project"""

    def __init__(self):
        self.detected_frameworks = set()

    def detect_frameworks(self, root_path: Path) -> Set[str]:
        """Detect frameworks used in the project"""
        self.detected_frameworks = set()

        for framework, indicators in FRAMEWORK_INDICATORS.items():
            if self._check_framework_indicators(root_path, indicators):
                self.detected_frameworks.add(framework)

        return self.detected_frameworks

    def _check_framework_indicators(self, root_path: Path,
                                    indicators: List[Dict]) -> bool:
        """Check if a framework's indicators are present"""
        matches = 0

        for indicator in indicators:
            indicator_type = indicator['type']
            path_pattern = indicator['path']

            if indicator_type == 'file':
                # Check for file existence
                for file_path in root_path.rglob(path_pattern):
                    if file_path.is_file():
                        # Check content if specified
                        if 'content' in indicator:
                            try:
                                with open(file_path, 'r',
                                          encoding='utf-8') as f:
                                    content = f.read()
                                    content_keywords = indicator['content']
                                    if isinstance(content_keywords, str):
                                        content_keywords = [content_keywords]

                                    if any(keyword in content for keyword in
                                           content_keywords):
                                        matches += 1
                                        break
                            except (IOError, UnicodeDecodeError):
                                continue
                        else:
                            matches += 1
                            break

            elif indicator_type == 'dir':
                # Check for directory existence
                for dir_path in root_path.rglob(path_pattern):
                    if dir_path.is_dir():
                        matches += 1
                        break

        # Require at least 2 indicators to avoid false positives
        return matches >= 2


class IgnorePatternHandler:
    """Handles ignore patterns including .gitignore, custom patterns, and framework patterns"""

    def __init__(self, root_dir: Path, ignore_patterns: List[str],
                 framework_patterns: List[str] = None):
        self.root_dir = root_dir
        self.patterns = ignore_patterns + self._load_gitignore_patterns()

        if framework_patterns:
            self.patterns.extend(framework_patterns)

    def _load_gitignore_patterns(self) -> List[str]:
        """Load patterns from .gitignore files"""
        patterns = []

        # Look for .gitignore in the root directory and parent directories
        current_dir = self.root_dir
        while current_dir.exists():
            gitignore_path = current_dir / '.gitignore'

            if gitignore_path.exists():
                try:
                    with open(gitignore_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            # Skip empty lines and comments
                            if line and not line.startswith('#'):
                                # Convert pattern to be relative to root
                                if current_dir != self.root_dir:
                                    rel_path = current_dir.relative_to(
                                        self.root_dir)
                                    line = str(rel_path / line)
                                patterns.append(line)
                except (IOError, UnicodeDecodeError):
                    pass

            # Stop at filesystem root
            if current_dir.parent == current_dir:
                break
            current_dir = current_dir.parent

        return patterns

    def should_ignore(self, path: Path) -> bool:
        """Check if a path should be ignored based on patterns"""
        # Ensure path is relative to root directory
        try:
            rel_path = path.relative_to(self.root_dir)
        except ValueError:
            # Path is not under root directory
            return True

        # Convert path to string with forward slashes for consistent pattern matching
        path_str = str(rel_path).replace('\\', '/')

        # Check against all patterns
        for pattern in self.patterns:
            # Handle directory patterns ending with /
            if pattern.endswith('/'):
                dir_pattern = pattern.rstrip('/')
                if (fnmatch.fnmatch(path_str, dir_pattern)
                        or fnmatch.fnmatch(path_str, f"{dir_pattern}/*")):
                    return True
            # Handle regular patterns
            elif fnmatch.fnmatch(path_str, pattern):
                return True

        return False


class LanguageDetector:
    """Detects language based on file extension"""

    def __init__(self, extension_map: Dict[str, List[str]]):
        # Create reverse mapping from extension to language
        self.extension_to_lang = {}
        for lang, exts in extension_map.items():
            for ext in exts:
                self.extension_to_lang[ext] = lang

    def detect_language(self, file_path: Path) -> Optional[str]:
        ext = file_path.suffix.lower()
        return self.extension_to_lang.get(ext)


class FileDiscoverer:
    """Main class for discovering files in a project"""

    def __init__(self, config: DiscovererConfig):
        self.config = config
        self.language_detector = LanguageDetector(EXTENSION_MAP)
        self.framework_detector = FrameworkDetector()

    def discover_files(self, root: str) -> List[Tuple[str, str]]:
        """
        Walks root and yields (path, language) tuples.
        Respects .gitignore and custom ignore patterns.
        """
        root_path = Path(root).resolve()

        # Detect frameworks if enabled
        framework_patterns = []
        detected_frameworks = self.framework_detector.detect_frameworks(
            root_path)
        for framework in detected_frameworks:
            framework_patterns.extend(
                FRAMEWORK_IGNORE_PATTERNS.get(framework, []))

        ignore_handler = IgnorePatternHandler(root_path,
                                              self.config.ignore_patterns,
                                              framework_patterns)

        discovered_files = []

        for file_path in self._walk_directory(root_path, ignore_handler):
            # Check if we've reached the maximum files
            if len(discovered_files) >= self.config.max_files:
                break

            # Detect language
            language = self.language_detector.detect_language(file_path)

            # Skip test files if configured to do so
            if self.config.ignore_tests and self._is_test_file(file_path,
                                                               root_path):
                continue

            discovered_files.append((str(file_path), language))

        return discovered_files

    def _walk_directory(self, root_path: Path,
                        ignore_handler: IgnorePatternHandler) -> Iterator[
        Path]:
        """Generator that walks directory while respecting ignore patterns"""
        for dirpath, dirnames, filenames in os.walk(
            root_path,
            followlinks=self.config.follow_symlinks
        ):
            current_dir = Path(dirpath)

            # Filter directories to ignore
            dirnames[:] = [
                d for d in dirnames
                if not ignore_handler.should_ignore(current_dir / d)
            ]

            # Process files
            for filename in filenames:
                file_path = current_dir / filename

                if not ignore_handler.should_ignore(file_path):
                    yield file_path

    def _is_test_file(self, file_path: Path, root_path: Path) -> bool:
        """Check if a file is a test file using pattern matching"""
        try:
            rel_path = file_path.relative_to(root_path)
        except ValueError:
            return False

        # Convert path to string with forward slashes for consistent pattern matching
        path_str = str(rel_path).replace('\\', '/')

        # Check if path matches any test pattern
        for pattern in TEST_FILE_PATTERNS:
            if fnmatch.fnmatch(path_str, pattern):
                return True

        # Check if file is in a test directory
        test_dirs = {'test', 'tests', '__tests__', 'spec', 'specs'}
        if any(part in test_dirs for part in rel_path.parts):
            return True

        return False


# Factory function for easy creation
def create_file_discoverer(
        max_files: int,
        # depth: int,
        ignore_tests: bool,
        ignore_patterns: List[str],
        follow_symlinks: bool = False,
) -> FileDiscoverer:
    """Factory function to create a FileDiscoverer with given configuration"""
    config = DiscovererConfig(
        max_files=max_files,
        # depth=depth,
        ignore_tests=ignore_tests,
        ignore_patterns=ignore_patterns,
        follow_symlinks=follow_symlinks,
    )
    return FileDiscoverer(config)


# Simple function for backward compatibility
def discover_files(
        root: str,
        # depth: int,
        max_files: int,
        ignore_tests: bool,
        ignore_patterns: List[str],
) -> List[Tuple[str, str]]:
    """
    Walks root and yields (path, language) tuples.
    Simple, but respects .gitignore (basic) by skipping hidden directories
    and __pycache__.
    """
    discoverer = create_file_discoverer(
        max_files=max_files,
        ignore_tests=ignore_tests,
        # depth=depth,
        ignore_patterns=ignore_patterns
    )
    return discoverer.discover_files(root)