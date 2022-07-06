import asyncio
from dataclasses import dataclass

from gobexec.output.renderer import Renderer


@dataclass
class Progress:
    done: int
    total: int


@dataclass
class Sequential:
    def execute(self, result, jobs, renderer: Renderer) -> None:
        progress = Progress(0, len(jobs))
        renderer.render(result, progress)

        for job in jobs:
            asyncio.run(job())
            progress.done += 1
            renderer.render(result, progress)

        renderer.render(result)

@dataclass
class Parallel:
    num_workers: int

    async def execute_async(self, result, jobs, renderer: Renderer) -> None:
        queue = asyncio.Queue()
        for job in jobs:
            queue.put_nowait(job)

        progress = Progress(0, queue.qsize())
        renderer.render(result, progress)

        async def worker():
            while True:
                job = await queue.get()
                await job()
                progress.done += 1
                renderer.render(result, progress)
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
