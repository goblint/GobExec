import asyncio
import tempfile
from typing import List

from gobexec.model.benchmark import Single
from gobexec.model.context import ExecutionContext, CompletedSubprocess
from gobexec.model.result import PrivPrecResult, ApronPrecResult
from gobexec.model.tool import Tool

ARGS_TOOL_KEY = "goblint-args"


class GoblintTool(Tool[Single, CompletedSubprocess]):
    name: str
    program: str
    args: List[str]
    dump: str
    validate: bool

    def __init__(self,
                 name: str = "Goblint",
                 program: str = "goblint",
                 args: List[str] = None,
                 dump: str = '',
                 validate: bool = False
                 ) -> None:
        self.name = name
        self.program = program
        self.args = args if args else []
        self.dump = dump
        self.validate = validate

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
            if self.dump == "priv":
                args += ["--set", "exp.priv-prec-dump", data_path.absolute() / "priv.txt"]
            elif self.dump == "apron":
                args += ["--set", "exp.relation.prec-dump", data_path.absolute() / "apron.txt"]

            if self.validate is True:
                args += ["--set",  "witness.yaml.validate", str(benchmark.files[0].parent / (str(benchmark.files[0].name)[:-2] + "_traces_rel.yml"))]

            cp = await ec.subprocess_exec(
                args[0],
                *args[1:],
                # capture_output=True,
                stdout=out_file,
                stderr=asyncio.subprocess.STDOUT,
                cwd = benchmark.files[0].parent
            )
            out_file.seek(0)
            cp.stdout = out_file.read()  # currently for extractors
            return cp


class PrivPrecTool(Tool[Single, PrivPrecResult]):
    name: str
    program: str
    args: List[GoblintTool]

    def __init__(self,
                 name: str = "privPrecCompare",
                 program: str = "../analyzer/privPrecCompare",
                 args: List[GoblintTool] = None,
                 ) -> None:
        self.name = name
        self.program = program
        self.args = args if args else []

    async def run_async(self, ec: ExecutionContext[Single], benchmark: Single) -> PrivPrecResult:
        path = ec.get_tool_data_path(self)
        for tool in self.args:
            await ec.get_tool_result(tool)
        with(path / 'priv_compare_out.txt').open("w") as out_file:
            args = [self.program] + [str(ec.get_tool_data_path(tool)/"priv.txt") for tool in self.args]
            await ec.subprocess_exec(
                args[0],
                stdout=out_file,
                stderr=asyncio.subprocess.STDOUT,

            )
            return PrivPrecResult(str(path / 'out.txt'))

class ApronPrecTool(Tool[Single,ApronPrecResult]):
    name: str
    program: str
    args: List[GoblintTool]

    def __init__(self,
                 name: str = "apronPrecCompare",
                 program: str = "../analyzer/apronPrecCompare",
                 args: List[GoblintTool] = None,
                 ) -> None:
        self.name = name
        self.program = program
        self.args = args

    async def run_async(self, ec: ExecutionContext[Single], benchmark: Single) -> ApronPrecResult:
        path = ec.get_tool_data_path(self)
        for tool in self.args:
            await ec.get_tool_result(tool)
        with (path / 'out.txt').open('w') as out_file:
            args = [self.program] + [str(ec.get_tool_data_path(tool).absolute()/'apron.txt') for tool in self.args]
            await ec.subprocess_exec(
                args[0],
                *args[1:],
                stdout = out_file,
                stderr = asyncio.subprocess.STDOUT,
            )
            return ApronPrecResult(str(path/'out.txt'))
