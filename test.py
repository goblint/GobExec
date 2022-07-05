import asyncio
from pathlib import Path

from gobexec.goblint import GoblintTool
from gobexec.goblint.bench import txtindex
from gobexec.output.renderer import FileRenderer

goblint = GoblintTool(
    program="/home/simmo/dev/goblint/sv-comp/goblint/goblint",
    args=["--conf", "/home/simmo/dev/goblint/sv-comp/goblint/conf/traces-rel-toy.json"],
    cwd=Path("/home/simmo/dev/goblint/sv-comp/goblint-bench")
)
index = txtindex.Index.from_path(Path("/home/simmo/dev/goblint/sv-comp/goblint-bench/index/traces-rel-toy.txt"))
matrix = index.to_matrix(goblint)

renderer = FileRenderer(Path("out.html"))
result = asyncio.run(matrix.execute_async(renderer))
renderer.render(result)
