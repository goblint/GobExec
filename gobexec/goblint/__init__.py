import asyncio
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Any, TypeVar, Type, Protocol

from gobexec.goblint.result import RaceSummary
from gobexec.model.benchmark import Single
from gobexec.model.result import Result
from gobexec.model.tool import Tool

ARGS_TOOL_KEY = "goblint-args"
CWD_TOOL_KEY = "goblint-cwd"

R = TypeVar('R', bound=Result)


class ResultExtractor(Protocol[R]):
    async def extract(self, ctx, stdout: bytes) -> R:
        ...


class GoblintTool(Tool[Single, R]):
    name: str
    program: str
    args: List[str]
    cwd: Optional[Path]
    result: ResultExtractor[R]

    def __init__(self,
                 name: str = "Goblint",
                 program: str = "goblint",
                 args: List[str] = None,
                 cwd: Optional[Path] = None,
                 result: ResultExtractor[R] = RaceSummary
                 ) -> None:
        self.name = name
        self.program = program
        self.args = args if args else []
        self.cwd = cwd
        self.result = result

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

    async def run_async(self, ctx, benchmark: Single) -> R: # TODO: why incompatible
        with tempfile.TemporaryDirectory() as tmp:
            args = [self.program] + \
                   ["--set", "goblint-dir", tmp] + \
                   self.args + \
                   benchmark.tool_data.get(ARGS_TOOL_KEY, []) + \
                   [str(file) for file in benchmark.files]
            # print(args)
            p = await asyncio.create_subprocess_exec(
                args[0],
                *args[1:],
                # capture_output=True,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.cwd / benchmark.tool_data.get(CWD_TOOL_KEY, Path())
            )
            stdout, stderr = await p.communicate()
            # print(stderr)
            return await self.result.extract(ctx, stdout)
