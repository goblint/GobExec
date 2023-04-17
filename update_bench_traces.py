from pathlib import Path

import gobexec.main
from gobexec.goblint import tool
from gobexec.goblint.bench import txtindex
from gobexec.goblint.result import LineSummary
from gobexec.goblint.tool import GoblintTool

from gobexec.model.result import TimeResult, PrivPrecResult
from gobexec.model.tools import ExtractTool, ResultExtractor
from gobexec.output.renderer import FileRenderer, ConsoleRenderer, MultiRenderer


def index_tool_factory(name, args):
    goblint = GoblintTool(
        name=name,
        program="../analyzer/goblint",
        args=["--conf", "../analyzer/conf/traces.json", "--enable", "dbg.debug"] + args,
        dump= True
    )

    return ExtractTool(
        goblint,
        TimeResult,
        LineSummary,
        #PrivPrecResult

    )

matrix = txtindex.load(Path("../bench/index/traces.txt"),index_tool_factory)
privprec = tool.PrivPrecTool()
matrix.tools.append(privprec)
html_renderer = FileRenderer(Path("out.html"))
console_renderer = ConsoleRenderer()
renderer = MultiRenderer([html_renderer, console_renderer])

gobexec.main.run(matrix, renderer)