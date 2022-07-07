import asyncio
from asyncio import Task
from dataclasses import dataclass
from typing import List, Optional, Any

from gobexec.model.benchmark import Single, Group
from gobexec.model.tool import Tool


@dataclass
class SingleToolResult:
    benchmark: Single
    tool: Tool[Single, Any]
    result: Any


@dataclass
class SingleToolsResult:
    benchmark: Single
    tools: List[Tool[Single, Any]]
    results: List[Task[SingleToolResult]]

    async def join(self) -> None:
        await asyncio.wait(self.results)


@dataclass
class GroupToolsResult:
    group: Group
    benchmarks: List[SingleToolsResult]

    async def join(self) -> None:
        await asyncio.wait([benchmark.join() for benchmark in self.benchmarks])


@dataclass
class MatrixResult:
    tools: List[Tool[Single, Any]]
    groups: List[GroupToolsResult]

    async def join(self) -> None:
        await asyncio.wait([group.join() for group in self.groups])

    def template(self, env):
        return env.get_template("matrix.jinja")
