import asyncio
import typing
from asyncio import Task
from dataclasses import dataclass
from pathlib import Path
from typing import List, TypeVar, Generic, Optional, Any

from jinja2 import Environment, Template

from gobexec.model.base import Result, ResultKind
from gobexec.model.benchmark import Single, Group
from gobexec.model.context import ExecutionContext, CompletedSubprocess
if typing.TYPE_CHECKING:
    from gobexec.model.scenario import Matrix
from gobexec.model.tool import Tool

B = TypeVar('B')
R = TypeVar('R', bound=Result)


@dataclass
class SingleToolResult(Generic[B, R]):
    benchmark: B
    tool: Tool[B, R]
    result: R


@dataclass
class SingleToolsResult(Generic[B, R]):
    benchmark: B
    tools: List[Tool[B, R]]
    results: List[Task[SingleToolResult[B, R]]]

    async def join(self) -> None:
        await asyncio.wait(self.results)


@dataclass
class GroupToolsResult(Generic[B, R]):
    group: Group[B]
    benchmarks: List[SingleToolsResult[B, R]]

    async def join(self) -> None:
        await asyncio.wait([benchmark.join() for benchmark in self.benchmarks])


@dataclass(init=False)
class MatrixResult(Result, Generic[B, R]):
    matrix: 'Matrix[B, R]'
    groups: List[GroupToolsResult[B, R]]

    def __init__(self,
                 matrix: 'Matrix[B, R]',
                 groups: List[GroupToolsResult[B, R]]
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
    name = "time"

    time: float
    out_path: Path

    def __init__(self, time: float, out_path: Path) -> None:
        self.time = time
        self.out_path = out_path

    def template(self, env: Environment) -> Template:
        return env.get_template("timeresult.jinja")

    @staticmethod
    async def extract(ec: ExecutionContext[Any], cp: CompletedSubprocess) -> 'TimeResult':
        return TimeResult(cp.rusage.ru_utime + cp.rusage.ru_stime, cp.data_path / "out.txt")


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
            return ResultKind.DEFAULT

@dataclass(init=False)
class PrivPrecResult(Result):
    result_path: str

    def __init__(self, result_path: str) -> None:
        self.result_path = result_path

    def template(self, env: Environment) -> Template:
        return env.get_template('privprecresult.jinja')


@dataclass(init=False)
class ApronPrecResult(Result):
    result_path: str

    def __init__(self,result_path: str) -> None:
        self.result_path = result_path

    def template(self, env):
        return env.get_template('apronprecresult.jinja')

