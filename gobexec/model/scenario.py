import asyncio
from dataclasses import dataclass
from typing import List

from gobexec.model.benchmark import Group
from gobexec.model.result import MatrixResult, GroupToolsResult, SingleToolsResult, SingleToolResult
from gobexec.model.tool import Tool
from gobexec.output.renderer import Renderer


@dataclass
class Matrix:
    groups: List[Group]
    tools: List[Tool]

    def execution_plan(self):
        matrix_result = MatrixResult(self.tools, [])
        jobs = []

        def job(i, j, benchmark, k, tool):
            # workaround to force coroutine to copy arguments
            async def job():
                out = await tool.run_async(benchmark)
                # print(out)
                matrix_result.groups[i].benchmarks[j].results[k] = SingleToolResult(
                    benchmark=benchmark,
                    tool=tool,
                    result=out
                )
            return job

        for i, group in enumerate(self.groups):
            group_result = GroupToolsResult(group, [])
            for j, benchmark in enumerate(group.benchmarks):
                benchmark_results = SingleToolsResult(benchmark, [])
                for k, tool in enumerate(self.tools):
                    jobs.append(job(i, j, benchmark, k, tool))
                    benchmark_results.results.append(None)
                group_result.benchmarks.append(benchmark_results)
            matrix_result.groups.append(group_result)

        return matrix_result, jobs
