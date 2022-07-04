from dataclasses import dataclass
from typing import List

from gobexec.model.benchmark import Group
from gobexec.model.tool import Tool


@dataclass
class Matrix:
    groups: List[Group]
    tools: List[Tool]

    def execute(self) -> None:
        for group in self.groups:
            for benchmark in group.benchmarks:
                for tool in self.tools:
                    print(tool.run(benchmark))
