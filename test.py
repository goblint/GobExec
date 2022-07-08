import asyncio
from pathlib import Path

from gobexec import executor
from gobexec.executor import Progress
from gobexec.goblint.tool import GoblintTool
from gobexec.goblint.bench import txtindex, tools
from gobexec.goblint.bench.tools import DuetTool
from gobexec.goblint.result import AssertSummary
from gobexec.goblint.extractor import AssertSummaryExtractor
from gobexec.model import scenario
from gobexec.output.renderer import FileRenderer, ConsoleRenderer, MultiRenderer

assert_counter = tools.AssertCounter(cwd=Path("/home/simmo/dev/goblint/sv-comp/goblint-bench"))
goblint = GoblintTool(
    program="/home/simmo/dev/goblint/sv-comp/goblint/goblint",
    # args=["--conf", "/home/simmo/dev/goblint/sv-comp/goblint/conf/traces-rel-toy.json", "--enable", "dbg.debug"],
    args=["--conf", "/home/simmo/dev/goblint/sv-comp/goblint/conf/traces-rel.json", "--enable", "dbg.debug"],
    cwd=Path("/home/simmo/dev/goblint/sv-comp/goblint-bench"),
    result=AssertSummaryExtractor(assert_counter)
)
duet = DuetTool(
    program="/home/simmo/Desktop/duet/duet/duet.exe",
    args=["-coarsen", "-inline", "-domain", "oct"],
    cwd=Path("/home/simmo/dev/goblint/sv-comp/goblint-bench"),
    assert_counter=assert_counter
)
# index = txtindex.Index.from_path(Path("/home/simmo/dev/goblint/sv-comp/goblint-bench/index/traces-rel-toy.txt"))
matrix = txtindex.load(Path("/home/simmo/dev/goblint/sv-comp/goblint-bench/index/traces-relational-watts.txt"), goblint)
matrix.tools.append(duet)
# matrix.tools.insert(0, assert_counter)

html_renderer = FileRenderer(Path("out.html"))
console_renderer = ConsoleRenderer()
renderer = MultiRenderer([html_renderer, console_renderer])


async def main():
    scenario.sem.set(asyncio.BoundedSemaphore(14))
    progress = Progress(0, 0, 0)
    result = await matrix.execute(progress, lambda: renderer.render(result, progress)) # tying the knot!
    await result.join()
    renderer.render(result)


asyncio.run(main())
