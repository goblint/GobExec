import asyncio
from pathlib import Path

import gobexec.main
from gobexec.goblint.bench import txtindex, tools
from gobexec.goblint.extractor import AssertSummaryExtractor
from gobexec.goblint.result import LineSummary
from gobexec.goblint.tool import GoblintTool
from gobexec.model.result import TimeResult
from gobexec.model.tools import ExtractTool
from gobexec.output.renderer import FileRenderer, ConsoleRenderer, MultiRenderer

assert_counter = tools.AssertCounter()

def index_tool_factory(name, args):
    goblint = GoblintTool(
        name=name,
        program=str(Path("../analyzer/goblint").absolute()),
        args=["--conf", str(Path("../analyzer/conf/traces-rel.json").absolute()), "--enable", "allglobs", "--enable", "dbg.timing.enabled", "--enable", "warn.debug", "-v"] + args,
    )
    assert_summary_extractor = AssertSummaryExtractor(assert_counter)
    return ExtractTool(
        goblint,
        TimeResult,
        LineSummary,
        assert_summary_extractor,
        primary=assert_summary_extractor
    )

# TODO: add asserts etc totals to HTML

matrix = txtindex.load(Path("../bench/index/traces-relational-watts.txt").absolute(), index_tool_factory)
matrix.tools.insert(0, assert_counter)
matrix.tools.insert(0, tools.WcLines())

html_renderer = FileRenderer(Path("out.html"))
console_renderer = ConsoleRenderer()
renderer = MultiRenderer([html_renderer, console_renderer])

gobexec.main.run(matrix, renderer)