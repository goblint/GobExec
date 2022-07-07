import asyncio
from asyncio import Task
from dataclasses import dataclass
from typing import List, Optional, Any, Protocol, TypeVar, Generic

from jinja2 import Environment, Template

from gobexec.model.benchmark import Single, Group
from gobexec.model.tool import Tool


class Result(Protocol):
    def template(self, env: Environment) -> Template:
        ...


R = TypeVar('R', bound=Result)


@dataclass
class SingleToolResult(Generic[R]):
    benchmark: Single
    tool: Tool[Single, R]
    result: R


@dataclass
class SingleToolsResult(Generic[R]):
    benchmark: Single
    tools: List[Tool[Single, R]]
    results: List[Task[SingleToolResult[R]]]

    async def join(self) -> None:
        await asyncio.wait(self.results)


@dataclass
class GroupToolsResult(Generic[R]):
    group: Group
    benchmarks: List[SingleToolsResult[R]]

    async def join(self) -> None:
        await asyncio.wait([benchmark.join() for benchmark in self.benchmarks])


@dataclass(init=False)
class MatrixResult(Result, Generic[R]):
    tools: List[Tool[Single, R]]
    groups: List[GroupToolsResult[R]]

    def __init__(self,
                 tools: List[Tool[Single, R]],
                 groups: List[GroupToolsResult[R]]
                 ) -> None:
        self.tools = tools
        self.groups = groups

    async def join(self) -> None:
        await asyncio.wait([group.join() for group in self.groups])

    def template(self, env):
        return env.get_template("matrix.jinja")
