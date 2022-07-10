import asyncio
from pathlib import Path

import gobexec.main
from gobexec.asyncio.child_watcher import RusageThreadedChildWatcher
from gobexec.executor import Progress
from gobexec.goblint.bench import txtindex, tools
from gobexec.goblint.bench.tools import DuetTool
from gobexec.goblint.extractor import AssertSummaryExtractor
from gobexec.goblint.result import Rusage, RaceSummary
from gobexec.goblint.tool import GoblintTool
from gobexec.model import tool
from gobexec.model.context import RootExecutionContext
from gobexec.model.result import TimeResult
from gobexec.model.tools import ExtractTool
from gobexec.output.renderer import FileRenderer, ConsoleRenderer, MultiRenderer

assert_counter = tools.AssertCounter()

def index_tool_factory(name, args):
    goblint = GoblintTool(
        name=name,
        program="/home/simmo/dev/goblint/sv-comp/goblint/goblint",
        args=["--conf", "/home/simmo/dev/goblint/sv-comp/goblint/conf/traces-rel-toy.json", "--enable", "dbg.debug"] + args,
        # args=["--conf", "/home/simmo/dev/goblint/sv-comp/goblint/conf/traces-rel.json", "--enable", "dbg.debug"],
    )
    return ExtractTool(
        goblint,
        TimeResult,
        # AssertSummaryExtractor(assert_counter),
        # AssertSummaryExtractor(),
        # RaceSummary
    )
duet = DuetTool(
    program="/home/simmo/Desktop/duet/duet/duet.exe",
    args=["-coarsen", "-inline", "-domain", "oct"],
    assert_counter=assert_counter
)
matrix = txtindex.load(Path("/home/simmo/dev/goblint/sv-comp/goblint-bench/index/traces-rel-toy.txt"), index_tool_factory)
# matrix = txtindex.load(Path("/home/simmo/dev/goblint/sv-comp/goblint-bench/index/traces-relational-watts.txt"), goblint)
matrix.tools.append(duet)
# matrix.tools.append(assert_counter)
matrix.tools.insert(0, assert_counter)

html_renderer = FileRenderer(Path("out.html"))
console_renderer = ConsoleRenderer()
renderer = MultiRenderer([html_renderer, console_renderer])

gobexec.main.run(matrix, renderer)
