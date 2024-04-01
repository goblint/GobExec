from gobexec.goblint.tool import GoblintToolFromScratch, GoblintToolIncremental
from pathlib import Path

import gobexec.main
from gobexec.goblint import tool
from gobexec.goblint.bench import txtindex
from gobexec.goblint.result import ThreadSummary
from gobexec.goblint.tool import GoblintTool
from gobexec.model.benchmark import Incremental, Group

from gobexec.model.result import TimeResult
from gobexec.model.scenario import Matrix
from gobexec.model.tools import ExtractTool
from gobexec.output.renderer import FileRenderer, ConsoleRenderer, MultiRenderer

from_scratch = GoblintToolFromScratch(
    name="from_scratch",
    program=str(Path("../analyzer/goblint").absolute()),

)

incremental = GoblintToolIncremental(
    name="incremental",
    program=str(Path("../analyzer/goblint").absolute()),
    from_scratch=from_scratch
)

bench = Incremental(
    name="aget",
    description="",
    files=Path("../bench/pthread/aget_comb.c").absolute(),
    patch=Path("../bench/pthread/aget_comb02.patch").absolute(),
    tool_data={}
)
group = Group(
    name="test",
    benchmarks=[bench]
)

matrix = Matrix(
    name="test",
    groups=[group],
    tools=[from_scratch, incremental]
)

html_renderer = FileRenderer(Path("out.html"))
console_renderer = ConsoleRenderer()
renderer = MultiRenderer([html_renderer, console_renderer])

gobexec.main.run(matrix, renderer)
