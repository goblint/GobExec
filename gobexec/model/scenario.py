import asyncio
from asyncio import Future, Task
from dataclasses import dataclass
from typing import List, Any, TypeVar, Generic, Dict

from gobexec.executor import Progress
from gobexec.model.base import Result
from gobexec.model.benchmark import Group, Single
from gobexec.model.context import ExecutionContext, RootExecutionContext, CompletedSubprocess
from gobexec.model.result import MatrixResult, GroupToolsResult, SingleToolsResult, SingleToolResult
from gobexec.model.tool import Tool

R = TypeVar('R', bound=Result)


class MatrixExecutionContext(ExecutionContext):
    parent: RootExecutionContext
    benchmark_results: SingleToolsResult
    cache: Dict[int, Task[SingleToolResult]]

    def __init__(self, parent: RootExecutionContext, benchmark_results: SingleToolsResult) -> None:
        super().__init__()
        self.parent = parent
        self.benchmark_results = benchmark_results
        self.cache = {}

    async def subprocess_exec(self, *args, **kwargs) -> CompletedSubprocess:
        return await self.parent.subprocess_exec(*args, **kwargs)

    async def job(self, tool: Tool[Single, R], benchmark: Single):
        with self.parent.progress:
            out = await tool.run_async(self, benchmark)
            return SingleToolResult(
                benchmark=benchmark,
                tool=tool,
                result=out
            )

    def get_tool_future(self, tool: Tool[Any, R]) -> Task[SingleToolResult]:
        # print(1, tool)
        if id(tool) not in self.cache: # hidden tool
            # print(1.5, tool)
            self.cache[id(tool)] = asyncio.create_task(self.job(tool, self.benchmark_results.benchmark))
        # print(2, tool, self.cache[id(tool)])
        return self.cache[id(tool)]

    async def get_tool_result(self, tool: Tool[Any, R]) -> R:
        result = await self.get_tool_future(tool)
        return result.result


@dataclass
class Matrix(Generic[R]):
    groups: List[Group]
    tools: List[Tool[Single, R]]

    async def execute(self, ec: RootExecutionContext, render) -> MatrixResult[R]:
        matrix_result = MatrixResult(self.tools, [])
        for group in self.groups:
            group_result = GroupToolsResult(group, [])
            for benchmark in group.benchmarks:
                benchmark_results = SingleToolsResult(benchmark, self.tools, [])
                bec = MatrixExecutionContext(ec, benchmark_results)
                for tool in self.tools:
                    task = bec.get_tool_future(tool)
                    task.add_done_callback(lambda _: render())
                    benchmark_results.results.append(task)
                group_result.benchmarks.append(benchmark_results)
            matrix_result.groups.append(group_result)

        return matrix_result
