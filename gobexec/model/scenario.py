import asyncio
from dataclasses import dataclass
from typing import List

from gobexec.model.benchmark import Group
from gobexec.model.tool import Tool


@dataclass
class Matrix:
    groups: List[Group]
    tools: List[Tool]

    async def execute_async(self) -> None:
        queue = asyncio.Queue()
        for group in self.groups:
            for benchmark in group.benchmarks:
                for tool in self.tools:
                    queue.put_nowait((tool, benchmark))

        async def worker(queue):
            while True:
                tool, benchmark = await queue.get()
                out = await tool.run_async(benchmark)
                print(out)
                queue.task_done()

        workers = []
        for i in range(15):
            task = asyncio.create_task(worker(queue))
            workers.append(task)

        await queue.join()
        for task in workers:
            task.cancel()
        await asyncio.gather(*workers, return_exceptions=True)
