import asyncio
import typing
from asyncio import Task
from dataclasses import dataclass
from typing import List, TypeVar, Generic, Optional

from jinja2 import Environment, Template

from gobexec.model.base import Result
from gobexec.model.benchmark import Single, Group
from gobexec.model.context import ExecutionContext, CompletedSubprocess
if typing.TYPE_CHECKING:
    from gobexec.model.scenario import Matrix
from gobexec.model.tool import Tool

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
    matrix: 'Matrix[R]'
    groups: List[GroupToolsResult[R]]

    def __init__(self,
                 matrix: 'Matrix[R]',
                 groups: List[GroupToolsResult[R]]
                 ) -> None:
        self.matrix = matrix
        self.groups = groups

    @property
    def tools(self):
        return self.matrix.tools

    async def join(self) -> None:
        await asyncio.wait([group.join() for group in self.groups])

    def template(self, env):
        return env.get_template("matrix.jinja")


@dataclass(init=False)
class TimeResult(Result):
    time: float

    def __init__(self, time: float) -> None:
        self.time = time

    def template(self, env: Environment) -> Template:
        return env.from_string("{{ \"%.2f\"|format(this.time) }}s")

    @staticmethod
    async def extract(ec: ExecutionContext, cp: CompletedSubprocess) -> 'TimeResult':
        return TimeResult(cp.rusage.ru_utime + cp.rusage.ru_stime)


@dataclass(init=False)
class MultiResult(Result, Generic[R]):
    results: List[R]
    primary: Optional[R]

    def __init__(self, results, primary: Optional[R] = None) -> None:
        self.results = results
        self.primary = primary

    def template(self, env: Environment) -> Template:
        return env.get_template("multi.jinja")

    @property
    def kind(self):
        if self.primary:
            return self.primary.kind
        else:
            return ""
