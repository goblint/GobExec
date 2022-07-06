from pathlib import Path

from gobexec import executor
from gobexec.goblint import GoblintTool
from gobexec.goblint.bench import txtindex, tools
from gobexec.goblint.result import AssertSummary
from gobexec.output.renderer import FileRenderer, ConsoleRenderer, MultiRenderer

goblint = GoblintTool(
    program="/home/simmo/dev/goblint/sv-comp/goblint/goblint",
    args=["--conf", "/home/simmo/dev/goblint/sv-comp/goblint/conf/traces-rel-toy.json", "--enable", "dbg.debug"],
    cwd=Path("/home/simmo/dev/goblint/sv-comp/goblint-bench"),
    result=AssertSummary
)
index = txtindex.Index.from_path(Path("/home/simmo/dev/goblint/sv-comp/goblint-bench/index/traces-rel-toy.txt"))
matrix = index.to_matrix(goblint)
matrix.tools.append(tools.AssertCounter(cwd=Path("/home/simmo/dev/goblint/sv-comp/goblint-bench")))

html_renderer = FileRenderer(Path("out.html"))
console_renderer = ConsoleRenderer()
renderer = MultiRenderer([html_renderer, console_renderer])
result, jobs = matrix.execution_plan()
executor = executor.Parallel(num_workers=10)
# executor = executor.Sequential()
executor.execute(result, jobs, renderer)
