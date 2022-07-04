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

        total = queue.qsize()
        done = 0
        dones = []
        print()

        def print_progress(clear=True):
            # print(f"\r\033[K{done}/{total}", end="", flush=True)
            # print(f"{done}/{total}", flush=True)
            if clear:
                print(f"\r\033[K", end="", flush=False)
            for group in self.groups:
                for benchmark in group.benchmarks:
                    for tool in self.tools:
                        print("#" if (tool, benchmark) in dones else ".", end="", flush=False)
            print("", end="", flush=True)

        print_progress(clear=False)

        async def worker(queue):
            nonlocal done
            while True:
                tool, benchmark = await queue.get()
                out = await tool.run_async(benchmark)
                # print(out)
                done += 1
                dones.append((tool, benchmark))
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
