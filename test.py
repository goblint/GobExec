import asyncio
from pathlib import Path

from gobexec.goblint.bench import txtindex
from gobexec.model.benchmark import Single
from gobexec.model.scenario import Matrix
from gobexec.model.tool import Tool


class EchoTool(Tool):
    def run(self, benchmark: Single) -> str:
        return benchmark.name


index = txtindex.Index.from_path(Path("/home/simmo/dev/goblint/sv-comp/goblint-bench/index/traces-rel-toy.txt"))
matrix = index.to_matrix()

asyncio.run(matrix.execute_async())
