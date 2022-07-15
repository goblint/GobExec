import asyncio
import tempfile
from typing import List

from gobexec.model.benchmark import Single
from gobexec.model.context import ExecutionContext, CompletedSubprocess
from gobexec.model.tool import Tool

ARGS_TOOL_KEY = "goblint-args"


class GoblintTool(Tool[Single, CompletedSubprocess]):
    name: str
    program: str
    args: List[str]

    def __init__(self,
                 name: str = "Goblint",
                 program: str = "goblint",
                 args: List[str] = None
                 ) -> None:
        self.name = name
        self.program = program
        self.args = args if args else []

    # def run(self, benchmark: Single) -> str:
    #     bench = Path("/home/simmo/dev/goblint/sv-comp/goblint-bench")
    #     args = ["/home/simmo/dev/goblint/sv-comp/goblint/goblint"] + self.args + benchmark.tool_data.get(ARGS_TOOL_KEY, []) + [str(bench / file) for file in benchmark.files]
    #     print(args)
    #     p = subprocess.run(
    #         args=args,
    #         capture_output=True,
    #         cwd=bench / benchmark.files[0].parent
    #     )
    #     print(p.stderr)
    #     return RaceExtract().extract(p.stdout)

    async def run_async(self, ec: ExecutionContext[Single], benchmark: Single) -> CompletedSubprocess:
        data_path = ec.get_tool_data_path(self)
        goblint_dir = data_path / ".goblint"
        goblint_dir.mkdir(parents=True, exist_ok=True)
        with (data_path / "out.txt").open("w+b") as out_file:
            args = [self.program] + \
                   ["--set", "goblint-dir", goblint_dir.absolute()] + \
                   self.args + \
                   benchmark.tool_data.get(ARGS_TOOL_KEY, []) + \
                   [str(file) for file in benchmark.files]
            # print(args)
            cp = await ec.subprocess_exec(
                args[0],
                *args[1:],
                # capture_output=True,
                stdout=out_file,
                stderr=asyncio.subprocess.STDOUT
            )
            out_file.seek(0)
            cp.stdout = out_file.read()  # currently for extractors
            return cp
