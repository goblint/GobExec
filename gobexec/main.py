import asyncio
from pathlib import Path

from gobexec.asyncio.child_watcher import RusageThreadedChildWatcher
from gobexec.model.context import RootExecutionContext


def run(matrix, renderer):
    async def main():
        loop = asyncio.get_event_loop()
        rusage_child_watcher = RusageThreadedChildWatcher()
        rusage_child_watcher.attach_loop(loop)
        asyncio.set_child_watcher(rusage_child_watcher)

        data_path = Path("out")
        data_path.mkdir(parents=True, exist_ok=True)
        cpu_sem = asyncio.BoundedSemaphore(14)
        ec = RootExecutionContext(data_path, cpu_sem, rusage_child_watcher)
        result = await matrix.execute(ec, lambda: renderer.render(result, ec.progress))  # tying the knot!
        await result.join()
        renderer.render(result)

    asyncio.run(main())
