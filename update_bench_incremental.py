from gobexec.goblint.tool import GoblintToolFromScratch, GoblintToolIncremental
from pathlib import Path

import gobexec.main
from gobexec.goblint import tool
from gobexec.goblint.bench import txtindex, yamlindex
from gobexec.goblint.result import ThreadSummary, IncrementalSummary
from gobexec.goblint.tool import GoblintTool
from gobexec.model.benchmark import Incremental, Group

from gobexec.model.result import TimeResult
from gobexec.model.scenario import Matrix
from gobexec.model.tools import ExtractTool
from gobexec.output.renderer import FileRenderer, ConsoleRenderer, MultiRenderer

from_scratch = GoblintToolFromScratch(
    name="from_scratch",
    program=str(Path("../analyzer/goblint").absolute()),
    args=["--conf", Path("../bench/index/conf/td3.json").absolute()]

)


def index_tool_factory(name, args):
    incremental = GoblintToolIncremental(
        name=name,
        program=str(Path("../analyzer/goblint").absolute()),
        from_scratch=from_scratch,
        args=args

    )
    return ExtractTool(
        incremental,
        TimeResult,
        IncrementalSummary
    )


# incremental = GoblintToolIncremental(
#     name="incremental",
#     program=str(Path("../analyzer/goblint").absolute()),
#     from_scratch=from_scratch
# )
#
# bench = Incremental(
#     name="aget",
#     description="",
#     files=Path("../bench/pthread/aget_comb.c").absolute(),
#     patch=Path("../bench/pthread/aget_comb02.patch").absolute(),
#     tool_data={}
# )
# group = Group(
#     name="test",
#     benchmarks=[bench]
# )
#
# matrix = Matrix(
#     name="test",
#     groups=[group],
#     tools=[]
# )

# extractor = ExtractTool(
#     from_scratch,
#     TimeResult,
#     IncrementalSummary
# )
# extractor2 = ExtractTool(
#     incremental,
#     TimeResult,
#     IncrementalSummary
# )
matrix = yamlindex.load(Path("../bench/index/defs/incremental.yaml"),[Path("../bench/index/sets/posix.yaml")],index_tool_factory)
matrix.tools.insert(0,ExtractTool(from_scratch,TimeResult,IncrementalSummary))
# matrix.tools.insert(0, extractor)
# matrix.tools.insert(1, extractor2)
html_renderer = FileRenderer(Path("out.html"))
console_renderer = ConsoleRenderer()
renderer = MultiRenderer([html_renderer, console_renderer])

gobexec.main.run(matrix, renderer)
