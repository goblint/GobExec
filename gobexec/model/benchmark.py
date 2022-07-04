from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any


@dataclass
class Single:
    name: str
    description: str
    files: List[Path]
    tool_data: Dict[str, Any]


@dataclass
class Group:
    name: str
    benchmarks: List[Single]
