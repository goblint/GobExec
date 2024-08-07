from pathlib import Path

import gobexec.main
from gobexec.goblint import tool
from gobexec.goblint.bench import txtindex
from gobexec.goblint.result import ThreadSummary
from gobexec.goblint.tool import GoblintTool

from gobexec.model.result import TimeResult
from gobexec.model.tools import ExtractTool
from gobexec.output.renderer import FileRenderer, ConsoleRenderer, MultiRenderer


def index_tool_factory(name, args):
    goblint = GoblintTool(
        name=name,
        program=str(Path("../analyzer/goblint").absolute()),
        args=["--conf", str(Path("../analyzer/conf/traces-rel.json").absolute()), "--enable", "allglobs", "--enable", "dbg.timing.enabled", "--enable", "warn.debug", "-v"] + args,
        dump= 'apron'
    )

    return ExtractTool(
        goblint,
        TimeResult,
        # TODO: total logical lines
        ThreadSummary,
        # TODO: average protecting
        #PrivPrecResult

    )

# TODO: separate precision dump run to exclude dumping time

matrix = txtindex.load(Path("../bench/index/traces-relational.txt").absolute(),index_tool_factory)
apronprec = tool.ApronPrecTool(args= matrix.tools.copy())
matrix.tools.append(apronprec)
# privprec = tool.PrivPrecTool(args= matrix.tools.copy())
# matrix.tools.append(privprec)
html_renderer = FileRenderer(Path("out.html"))
console_renderer = ConsoleRenderer()
renderer = MultiRenderer([html_renderer, console_renderer])

gobexec.main.run(matrix, renderer)