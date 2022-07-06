import asyncio
from contextvars import ContextVar
from dataclasses import dataclass
from typing import List

from gobexec.model.benchmark import Group
from gobexec.model.result import MatrixResult, GroupToolsResult, SingleToolsResult, SingleToolResult
from gobexec.model.tool import Tool
from gobexec.output.renderer import Renderer


sem: ContextVar[asyncio.BoundedSemaphore] = ContextVar("sem")


@dataclass
class Matrix:
    groups: List[Group]
    tools: List[Tool]

    async def execute(self, progress, render) -> MatrixResult:
        matrix_result = MatrixResult(self.tools, [])

        def job(i, j, benchmark, k, tool, ctx):
            # workaround to force coroutine to copy arguments
            async def job():
                progress.total += 1
                async with sem.get():
                    progress.active += 1
                    out = await tool.run_async(ctx, benchmark)
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
                for k, tool in enumerate(self.tools):
                    task = asyncio.create_task(job(i, j, benchmark, k, tool, benchmark_results)())
                    task.add_done_callback(lambda _: render())
                    benchmark_results.results.append(task)
                group_result.benchmarks.append(benchmark_results)
            matrix_result.groups.append(group_result)

        return matrix_result
