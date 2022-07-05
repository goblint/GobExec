import asyncio
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

from gobexec.goblint import GoblintTool
from gobexec.goblint.bench import txtindex

goblint = GoblintTool(
    program="/home/simmo/dev/goblint/sv-comp/goblint/goblint",
    args=["--conf", "/home/simmo/dev/goblint/sv-comp/goblint/conf/traces-rel-toy.json"],
    cwd=Path("/home/simmo/dev/goblint/sv-comp/goblint-bench")
)
index = txtindex.Index.from_path(Path("/home/simmo/dev/goblint/sv-comp/goblint-bench/index/traces-rel-toy.txt"))
matrix = index.to_matrix(goblint)

results = asyncio.run(matrix.execute_async())
print(results)

env = Environment(
    loader=FileSystemLoader("./templates"),
    autoescape=select_autoescape()
)
template = env.get_template("matrix.html")
with open("out.html", "w") as outfile:
    outfile.write(template.render(matrix=matrix,matrix_results=results))
