import asyncio
from dataclasses import dataclass

from gobexec.output.renderer import Renderer


@dataclass
class Parallel:
    num_workers: int

    async def execute_async(self, result, jobs, renderer: Renderer) -> None:
        queue = asyncio.Queue()
        for job in jobs:
            queue.put_nowait(job)

        total = queue.qsize()
        done = 0
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

            renderer.render(result, progress=(done, total))

        print_progress(clear=False)

        async def worker():
            nonlocal done
            while True:
                job = await queue.get()
                await job()
                done += 1
                print_progress()
                queue.task_done()

        workers = []
        for i in range(self.num_workers):
            task = asyncio.create_task(worker())
            workers.append(task)

        await queue.join()
        for task in workers:
            task.cancel()
        await asyncio.gather(*workers, return_exceptions=True)
        renderer.render(result)

    def execute(self, result, jobs, renderer: Renderer) -> None:
        asyncio.run(self.execute_async(result, jobs, renderer))
