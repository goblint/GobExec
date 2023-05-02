from pathlib import Path

import gobexec.main
from gobexec.goblint.bench import txtindex
from gobexec.goblint.result import AssertTypeSummary
from gobexec.goblint.tool import GoblintTool

from gobexec.model.result import TimeResult
from gobexec.model.tools import ExtractTool
from gobexec.output.renderer import FileRenderer, ConsoleRenderer, MultiRenderer


def index_tool_factory(name, args):
    goblint = GoblintTool(
        name=name,
        program=str(Path("../analyzer/goblint").absolute()),
        args=["-v", "--conf", str(Path("../analyzer/conf/traces-rel.json").absolute()), "--enable", "dbg.debug"] + args,
        dump= 'apron'
    )

    return ExtractTool(
        goblint,
        TimeResult,
        AssertTypeSummary,

    )

matrix = txtindex.load(Path("../bench/index/traces-rel-assert.txt").absolute(),index_tool_factory)
html_renderer = FileRenderer(Path("out.html"))
console_renderer = ConsoleRenderer()
renderer = MultiRenderer([html_renderer, console_renderer])

gobexec.main.run(matrix, renderer)