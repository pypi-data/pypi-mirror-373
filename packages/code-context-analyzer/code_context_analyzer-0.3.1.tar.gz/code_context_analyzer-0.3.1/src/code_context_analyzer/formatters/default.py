"""
Here this formatter is temprary there is full structured formatter but those
needs to check and refactored to get desired output
"""

import os
from typing import Any, Dict, List, Optional


class LegacyCodeFormatter:
    def __init__(
            self,
            depth: int = 4,
            method_preview: int = 5,
            doc_chars: int = 180,
            truncate_total: Optional[int] = None
    ):
        """
        Initialize the CodeFormatter with parsing results and formatting options.

        :param parsed_data: The parsed code analysis results
        :param project_name: Name of the project (auto-detected if not provided)
        :param depth: How many top-level classes/functions to list per module
        :param method_preview: How many methods to show per class
        :param doc_chars: Maximum characters to include from docstrings (0 to disable docs)
        :param truncate_total: If set, when project summary is longer than this, truncate
        """
        self.depth = depth
        self.method_preview = method_preview
        self.doc_chars = doc_chars
        self.truncate_total = truncate_total

    def _extract_project_name(self) -> str:
        """Extract project name from the first file path"""
        if not self.parsed_data:
            return "unknown_project"

        first_path = self.parsed_data[0]['path']
        # Extract the directory name that seems to be the project
        temp_dir = os.path.basename(os.path.dirname(first_path))
        if temp_dir.startswith('repo_session_'):
            return temp_dir
        return "project"

    def format(self, parsed_data: List[Dict[str, Any]]) -> str:
        """Generate the complete markup report"""
        self.parsed_data = parsed_data

        self.project_name = self._extract_project_name()

        report = []
        report.append(self._generate_heading())
        report.append("\n## Tree Structure:")
        report.append(self._generate_tree())
        report.append("\n## Detailed Description:")
        report.append(self._generate_detailed_description())

        full_report = "\n".join(report)

        # Apply truncation if needed
        if self.truncate_total and len(full_report) > self.truncate_total:
            full_report = (full_report[:self.truncate_total]
                           + "\n\n... (truncated due to length)")

        return full_report

    def _generate_heading(self) -> str:
        """Generate the summary heading"""
        total_files = len(self.parsed_data)
        total_classes = sum(
            len(module['classes']) for module in self.parsed_data)
        total_functions = sum(
            len(module['functions']) for module in self.parsed_data)

        # Handle constants whether they're strings or dictionaries
        total_constants = 0
        for module in self.parsed_data:
            if 'constants' in module:
                total_constants += len(module['constants'])

        return (f"# Project '{self.project_name}' Summary\n"
                f"**{total_files}** file(s), **{total_classes}** class(es), "
                f"**{total_functions}** function(s), **{total_constants}** constant(s)\n")

    def _generate_tree(self) -> str:
        """Generate the directory tree structure"""
        # Organize files by directory
        dir_structure = {}
        for module in self.parsed_data:
            path = module['path']
            # Convert to relative path from project root
            rel_path = os.path.relpath(path, os.path.commonpath(
                [m['path'] for m in self.parsed_data]))
            dir_name = os.path.dirname(rel_path)
            file_name = os.path.basename(rel_path)

            if dir_name not in dir_structure:
                dir_structure[dir_name] = []

            # Add class names if any
            classes = [cls['name'] for cls in module['classes']]
            file_display = file_name
            if classes:
                file_display += f" ({', '.join(classes[:self.depth])}"
                if len(classes) > self.depth:
                    file_display += f", +{len(classes) - self.depth} more)"
                else:
                    file_display += ")"

            dir_structure[dir_name].append(file_display)

        # Build tree structure
        tree_lines = ["```"]
        tree_lines.append(f"{self.project_name}/")

        # Sort directories for consistent output
        sorted_dirs = sorted(dir_structure.keys())
        for i, dir_name in enumerate(sorted_dirs):
            is_last_dir = (i == len(sorted_dirs) - 1)
            prefix = "└── " if is_last_dir else "├── "

            if dir_name == ".":
                # Root directory files
                for j, file_name in enumerate(dir_structure[dir_name]):
                    is_last_file = (j == len(dir_structure[dir_name]) - 1)
                    file_prefix = "    " if is_last_dir else "│   "
                    file_prefix += "└── " if is_last_file else "├── "
                    tree_lines.append(file_prefix + file_name)
            else:
                # Subdirectories
                tree_lines.append(prefix + dir_name + "/")
                file_prefix = "    " if is_last_dir else "│   "

                for j, file_name in enumerate(dir_structure[dir_name]):
                    is_last_file = (j == len(dir_structure[dir_name]) - 1)
                    file_line_prefix = file_prefix + (
                        "└── " if is_last_file else "├── ")
                    tree_lines.append(file_line_prefix + file_name)

        tree_lines.append("```")
        return "\n".join(tree_lines)

    def _generate_detailed_description(self) -> str:
        """Generate the detailed package/module description"""
        lines = ["```"]

        # Organize modules by package
        packages = {}
        for module in self.parsed_data:
            path = module['path']
            rel_path = os.path.relpath(path, os.path.commonpath(
                [m['path'] for m in self.parsed_data]))
            dir_name = os.path.dirname(rel_path)

            if dir_name not in packages:
                packages[dir_name] = []
            packages[dir_name].append(module)

        # Generate description for each package
        lines.append(f"{self.project_name}/")

        for package_path, modules in sorted(packages.items()):
            package_name = package_path if package_path != "." else "Root"

            # Calculate package statistics
            module_count = len(modules)
            class_count = sum(len(module['classes']) for module in modules)
            function_count = sum(
                len(module['functions']) for module in modules)

            # Handle constants whether they're strings or dictionaries
            constant_count = 0
            for module in modules:
                if 'constants' in module:
                    constant_count += len(module['constants'])

            lines.append(f"\n├── Package: {package_name} "
                         f"({module_count} modules, {class_count} classes, "
                         f"{function_count} functions, {constant_count} constants)")

            for i, module in enumerate(modules):
                is_last_module = (i == len(modules) - 1)
                path = module['path']
                file_name = os.path.basename(path)

                module_prefix = "│   └── " if is_last_module else "│   ├── "
                lines.append(f"{module_prefix}Module: {file_name}")

                # Constants
                if 'constants' in module and module['constants']:
                    # Handle both string and dictionary constants
                    const_names = []
                    for const in module['constants']:
                        if isinstance(const, dict):
                            const_names.append(
                                const.get('name', 'unnamed_constant'))
                        else:
                            const_names.append(str(const))

                    const_prefix = "│       └── " if is_last_module else "│   │   ├── "
                    lines.append(
                        f"{const_prefix}Constants ({len(module['constants'])}): {', '.join(const_names[:self.depth])}")
                    if len(module['constants']) > self.depth:
                        lines.append(
                            f"{const_prefix}  ... and {len(module['constants']) - self.depth} more")

                # Functions
                if 'functions' in module and module['functions']:
                    func_prefix = "│       └── " if is_last_module else "│   │   ├── "
                    lines.append(
                        f"{func_prefix}Functions ({len(module['functions'])}):")

                    for j, func in enumerate(module['functions'][:self.depth]):
                        is_last_func = (j == len(
                            module['functions'][:self.depth]) - 1)
                        func_item_prefix = "│           └── " if (
                                    is_last_module and is_last_func) else "│   │   │   ├── "
                        sig = func.get('sig', '()')
                        lines.append(f"{func_item_prefix}{func['name']}{sig}")

                        if self.doc_chars > 0 and func.get('doc'):
                            doc_prefix = "│               └── " if (
                                        is_last_module and is_last_func) else "│   │   │   │   ├── "
                            lines.append(
                                f"{doc_prefix}{self._format_docstring(func['doc'])}")

                    if len(module['functions']) > self.depth:
                        more_prefix = "│           └── " if is_last_module else "│   │   │   ├── "
                        lines.append(
                            f"{more_prefix}... and {len(module['functions']) - self.depth} more functions")

                # Classes
                if 'classes' in module and module['classes']:
                    class_prefix = "│       └── " if is_last_module else "│   │   ├── "
                    lines.append(
                        f"{class_prefix}Classes ({len(module['classes'])}):")

                    for k, cls in enumerate(module['classes'][:self.depth]):
                        is_last_class = (k == len(
                            module['classes'][:self.depth]) - 1)
                        class_item_prefix = "│           └── " if (
                                    is_last_module and is_last_class) else "│   │   │   ├── "

                        bases = cls.get('bases', [])
                        base_str = f" ({', '.join(bases)})" if bases else ""
                        lines.append(
                            f"{class_item_prefix}{cls['name']}{base_str}:")

                        if self.doc_chars > 0 and cls.get('doc'):
                            doc_prefix = "│               └── " if (
                                        is_last_module and is_last_class) else "│   │   │   │   ├── "
                            lines.append(
                                f"{doc_prefix}{self._format_docstring(cls['doc'])}")

                        # Methods
                        if 'methods' in cls and cls['methods']:
                            method_prefix = "│               └── " if (
                                        is_last_module and is_last_class) else "│   │   │   │   ├── "
                            lines.append(
                                f"{method_prefix}Methods ({len(cls['methods'])}):")

                            for l, method in enumerate(
                                    cls['methods'][:self.method_preview]):
                                is_last_method = (l == len(
                                    cls['methods'][:self.method_preview]) - 1)
                                method_item_prefix = "│                   └── " if (
                                            is_last_module and is_last_class and is_last_method) else "│   │   │   │   │   ├── "

                                sig = method.get('sig', '()')
                                lines.append(
                                    f"{method_item_prefix}{method['name']}{sig}")

                                if self.doc_chars > 0 and method.get('doc'):
                                    doc_method_prefix = "│                       └── " if (
                                                is_last_module and is_last_class and is_last_method) else "│   │   │   │   │   │   ├── "
                                    lines.append(
                                        f"{doc_method_prefix}{self._format_docstring(method['doc'])}")

                            if len(cls['methods']) > self.method_preview:
                                more_methods_prefix = "│                   └── " if (
                                            is_last_module and is_last_class) else "│   │   │   │   │   ├── "
                                lines.append(
                                    f"{more_methods_prefix}... and {len(cls['methods']) - self.method_preview} more methods")

                    if len(module['classes']) > self.depth:
                        more_classes_prefix = "│           └── " if is_last_module else "│   │   │   ├── "
                        lines.append(
                            f"{more_classes_prefix}... and {len(module['classes']) - self.depth} more classes")

        lines.append("```")

        return "\n".join(lines)

    def _format_docstring(self, docstring: str) -> str:
        """Format docstring for display"""
        if not docstring or self.doc_chars == 0:
            return ""

        # Clean up docstring - remove excess whitespace and newlines
        docstring = " ".join(line.strip() for line in docstring.split("\n"))
        if len(docstring) > self.doc_chars:
            docstring = docstring[:self.doc_chars - 3] + "..."
        return docstring