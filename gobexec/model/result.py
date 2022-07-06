from dataclasses import dataclass
from typing import List, Optional

from gobexec.model.benchmark import Single, Group
from gobexec.model.tool import Tool


@dataclass
class SingleToolResult:
    benchmark: Single
    tool: Tool
    result: str


@dataclass
class SingleToolsResult:
    benchmark: Single
    results: List[Optional[SingleToolResult]]


@dataclass
class GroupToolsResult:
    group: Group
    benchmarks: List[SingleToolsResult]


@dataclass
class MatrixResult:
    tools: List[Tool]
    groups: List[GroupToolsResult]

    def template(self, env):
        return env.get_template("matrix.jinja")
