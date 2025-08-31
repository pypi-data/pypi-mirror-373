from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class MethodInfo:
    name: str
    signature: str
    docstring: Optional[str] = None


@dataclass
class ClassInfo:
    name: str
    bases: List[str]
    methods: List[MethodInfo]
    docstring: Optional[str] = None


@dataclass
class ModuleInfo:
    path: str
    classes: List[ClassInfo] = field(default_factory=list)
    functions: List[MethodInfo] = field(default_factory=list)
    constants: List[str] = field(default_factory=list)


@dataclass
class PackageInfo:
    path: str
    modules: List[ModuleInfo] = field(default_factory=list)
    class_count: int = 0
    function_count: int = 0
    constant_count: int = 0


@dataclass
class AnalysisResult:
    project_name: str
    modules: List[ModuleInfo] = field(default_factory=list)
    packages: List[PackageInfo] = field(default_factory=list)
    total_files: int = 0
    total_classes: int = 0
    total_functions: int = 0
    total_constants: int = 0