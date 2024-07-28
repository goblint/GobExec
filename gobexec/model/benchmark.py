from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, TypeVar, Generic

B = TypeVar('B')


@dataclass
class Single:
    name: str
    description: str
    files: List[Path]
    tool_data: Dict[str, Any]


@dataclass
class Incremental:
    name: str
    description: str
    files: Path
    patch: Path
    tool_data: Dict[str, Any]


@dataclass
class Group(Generic[B]):
    name: str
    benchmarks: List[B]
