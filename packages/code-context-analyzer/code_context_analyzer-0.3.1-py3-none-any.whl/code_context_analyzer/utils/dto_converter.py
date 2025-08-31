import os
from typing import Any, Dict, List

from code_context_analyzer.dto.models import (AnalysisResult, ClassInfo,
                                              MethodInfo, ModuleInfo,
                                              PackageInfo)


def create_analysis_result(parsed_data: List[Dict[str, Any]],
                           project_name: str = None) -> AnalysisResult:
    """
    Convert parsed data into an AnalysisResult object

    -param parsed_data: The parsed data from code analysis
    -param project_name: Optional project name (will be extracted if not provided)
    -return AnalysisResult object with structured data
    """
    # Extract project name from first path if not provided
    if not project_name and parsed_data:
        first_path = parsed_data[0]['path']
        # Extract project name from path (e.g., 'repo_session_zx380lm0')
        project_name = os.path.basename(os.path.dirname(first_path))

    # Organize modules by package (directory)
    packages_dict = {}
    for module_data in parsed_data:
        path = module_data['path']
        dir_path = os.path.dirname(path)
        file_name = os.path.basename(path)

        if dir_path not in packages_dict:
            packages_dict[dir_path] = []

        # Convert class data to ClassInfo objects
        classes = []
        for class_data in module_data['classes']:
            methods = []
            for method_data in class_data.get('methods', []):
                method = MethodInfo(
                    name=method_data['name'],
                    signature=method_data.get('sig', '()'),
                    docstring=method_data.get('doc')
                )
                methods.append(method)

            class_info = ClassInfo(
                name=class_data['name'],
                bases=class_data.get('bases', []),
                methods=methods,
                docstring=class_data.get('doc')
            )
            classes.append(class_info)

        # Convert function data to MethodInfo objects
        functions = []
        for func_data in module_data['functions']:
            function = MethodInfo(
                name=func_data['name'],
                signature=func_data.get('sig', '()'),
                docstring=func_data.get('doc')
            )
            functions.append(function)

        # Handle constants (could be strings or dicts)
        constants = []
        for const in module_data['constants']:
            if isinstance(const, dict):
                constants.append(const.get('name', 'unnamed_constant'))
            else:
                constants.append(str(const))

        # Create ModuleInfo
        module_info = ModuleInfo(
            path=file_name,
            classes=classes,
            functions=functions,
            constants=constants
        )

        packages_dict[dir_path].append(module_info)

    # Create PackageInfo objects
    packages = []
    for dir_path, modules in packages_dict.items():
        # Calculate package statistics
        class_count = sum(len(module.classes) for module in modules)
        function_count = sum(len(module.functions) for module in modules)
        constant_count = sum(len(module.constants) for module in modules)

        package_info = PackageInfo(
            path=dir_path,
            modules=modules,
            class_count=class_count,
            function_count=function_count,
            constant_count=constant_count
        )
        packages.append(package_info)

    # Calculate overall statistics
    total_files = len(parsed_data)
    total_classes = sum(
        len(module_data['classes']) for module_data in parsed_data)
    total_functions = sum(
        len(module_data['functions']) for module_data in parsed_data)
    total_constants = sum(
        len(module_data['constants']) for module_data in parsed_data)

    # Create and return AnalysisResult
    return AnalysisResult(
        project_name=project_name,
        modules=[module for package in packages for module in package.modules],
        packages=packages,
        total_files=total_files,
        total_classes=total_classes,
        total_functions=total_functions,
        total_constants=total_constants
    )