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

    async def execute_async(self, renderer: Renderer) -> MatrixResult:
        matrix_result = MatrixResult(self.tools, [])

        queue = asyncio.Queue()
        for i, group in enumerate(self.groups):
            group_result = GroupToolsResult(group, [])
            for j, benchmark in enumerate(group.benchmarks):
                benchmark_results = SingleToolsResult(benchmark, [])
                for k, tool in enumerate(self.tools):
                    queue.put_nowait((tool, benchmark, i, j, k))
                    benchmark_results.results.append(None)
                group_result.benchmarks.append(benchmark_results)
            matrix_result.groups.append(group_result)

        total = queue.qsize()
        done = 0
        dones = []
        print()

        def print_progress(clear=True):
            print(f"\r\033[K{done}/{total}", end="", flush=True)
            # print(f"{done}/{total}", flush=True)
            # if clear:
            #     print(f"\r\033[K", end="", flush=False)
            # for group in self.groups:
            #     for benchmark in group.benchmarks:
            #         for tool in self.tools:
            #             print("#" if (tool, benchmark) in dones else ".", end="", flush=False)
            # print("", end="", flush=True)

            renderer.render(matrix_result, progress=(done, total))

        print_progress(clear=False)

        async def worker(queue):
            nonlocal done
            while True:
                tool, benchmark, i, j, k = await queue.get()
                out = await tool.run_async(benchmark)
                # print(out)
                done += 1
                dones.append((tool, benchmark))
                matrix_result.groups[i].benchmarks[j].results[k] = SingleToolResult(
                    benchmark=benchmark,
                    tool=tool,
                    result=out
                )
                print_progress()
                queue.task_done()

        workers = []
        for i in range(15):
            task = asyncio.create_task(worker(queue))
            workers.append(task)

        await queue.join()
        for task in workers:
            task.cancel()
        await asyncio.gather(*workers, return_exceptions=True)

        return matrix_result
