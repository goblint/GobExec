import asyncio
from asyncio import Future
from contextvars import ContextVar
from dataclasses import dataclass
from typing import List, Any, TypeVar, Generic, Dict

from gobexec.model.benchmark import Group, Single
from gobexec.model.context import ExecutionContext
from gobexec.model.result import MatrixResult, GroupToolsResult, SingleToolsResult, SingleToolResult
from gobexec.model.base import Result
from gobexec.model.tool import Tool
from gobexec.output.renderer import Renderer


sem: ContextVar[asyncio.BoundedSemaphore] = ContextVar("sem")

R = TypeVar('R', bound=Result)


class MatrixExecutionContext(ExecutionContext):
    benchmark_results: SingleToolsResult
    cache: Dict[int, Future[Result]]

    def __init__(self, benchmark_results: SingleToolsResult) -> None:
        super().__init__()
        self.benchmark_results = benchmark_results
        self.cache = {}

    async def get_tool_result(self, tool: Tool[Any, R]) -> R:
        if id(tool) not in self.cache: # hidden tool
            self.cache[id(tool)] = asyncio.create_task(tool.run_async(self, self.benchmark_results.benchmark))
        return await self.cache[id(tool)]



@dataclass
class Matrix(Generic[R]):
    groups: List[Group]
    tools: List[Tool[Single, R]]

    async def execute(self, progress, render) -> MatrixResult[R]:
        matrix_result = MatrixResult(self.tools, [])

        def job(i, j, benchmark: Single, k, tool: Tool[Single, R], ec: MatrixExecutionContext):
            # workaround to force coroutine to copy arguments
            async def job():
                progress.total += 1
                async with sem.get():
                    progress.active += 1
                    out = await tool.run_async(ec, benchmark)
                    # print(out)
                    progress.done += 1
                    progress.active -= 1
                    return SingleToolResult(
                        benchmark=benchmark,
                        tool=tool,
                        result=out
                    )
            return job

        for i, group in enumerate(self.groups):
            group_result = GroupToolsResult(group, [])
            for j, benchmark in enumerate(group.benchmarks):
                benchmark_results = SingleToolsResult(benchmark, self.tools, [])
                ec = MatrixExecutionContext(benchmark_results)
                for k, tool in enumerate(self.tools):
                    task = asyncio.create_task(job(i, j, benchmark, k, tool, ec)())
                    task.add_done_callback(lambda _: render())
                    benchmark_results.results.append(task)
                    ec.cache[id(tool)] = task
                group_result.benchmarks.append(benchmark_results)
            matrix_result.groups.append(group_result)

        return matrix_result
