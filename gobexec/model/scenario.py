import asyncio
from asyncio import Future
from dataclasses import dataclass
from typing import List, Any, TypeVar, Generic, Dict

from gobexec.executor import Progress
from gobexec.model.base import Result
from gobexec.model.benchmark import Group, Single
from gobexec.model.context import ExecutionContext
from gobexec.model.result import MatrixResult, GroupToolsResult, SingleToolsResult, SingleToolResult
from gobexec.model.tool import Tool

R = TypeVar('R', bound=Result)


class MatrixExecutionContext(ExecutionContext):
    benchmark_results: SingleToolsResult
    cache: Dict[int, Future[SingleToolResult]]
    progress: Progress

    def __init__(self, benchmark_results: SingleToolsResult, progress: Progress) -> None:
        super().__init__()
        self.benchmark_results = benchmark_results
        self.cache = {}
        self.progress = progress

    def job(self, tool: Tool[Single, R], benchmark: Single):
        # workaround to force coroutine to copy arguments
        async def job():
            self.progress.total += 1
            # async with sem.get():
            # self.progress.active += 1
            # print(f"running {tool}")
            out = await tool.run_async(self, benchmark)
            # print(out)
            self.progress.done += 1
            # self.progress.active -= 1
            return SingleToolResult(
                benchmark=benchmark,
                tool=tool,
                result=out
            )

        return job

    async def get_tool_result(self, tool: Tool[Any, R]) -> R:
        # print(1, tool)
        if id(tool) not in self.cache: # hidden tool
            # print(1.5, tool)
            self.cache[id(tool)] = asyncio.create_task(self.job(tool, self.benchmark_results.benchmark)())
        # print(2, tool, self.cache[id(tool)])
        result = await self.cache[id(tool)]
        # print(3, tool)
        return result.result


@dataclass
class Matrix(Generic[R]):
    groups: List[Group]
    tools: List[Tool[Single, R]]

    async def execute(self, progress, render) -> MatrixResult[R]:
        matrix_result = MatrixResult(self.tools, [])
        for i, group in enumerate(self.groups):
            group_result = GroupToolsResult(group, [])
            for j, benchmark in enumerate(group.benchmarks):
                benchmark_results = SingleToolsResult(benchmark, self.tools, [])
                ec = MatrixExecutionContext(benchmark_results, progress)
                for k, tool in enumerate(self.tools):
                    task = asyncio.create_task(ec.job(tool, benchmark)())
                    task.add_done_callback(lambda _: render())
                    benchmark_results.results.append(task)
                    ec.cache[id(tool)] = task
                group_result.benchmarks.append(benchmark_results)
            matrix_result.groups.append(group_result)

        return matrix_result
