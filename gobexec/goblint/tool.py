import asyncio
import tempfile
from pathlib import Path
from typing import List, Optional
import shutil
import os
from glob import glob
from gobexec.model.benchmark import Single, Incremental
from gobexec.model.context import ExecutionContext, CompletedSubprocess
from gobexec.model.result import PrivPrecResult, ApronPrecResult
from gobexec.model.tool import Tool

ARGS_TOOL_KEY = "goblint-args"


class GoblintToolFromScratch(Tool[Incremental, CompletedSubprocess]):
    name: str
    program: str
    args: List[str]

    def __init__(self,
                 name: str = "Goblint",
                 program: str = "goblint",
                 args: List[str] = None,
                 ) -> None:
        self.name = name
        self.program = program
        self.args = args if args else []

    async def run_async(self, ec: ExecutionContext[Incremental], benchmark: Incremental) -> CompletedSubprocess:
        data_path = ec.get_tool_data_path(self)
        goblint_dir = data_path
        goblint_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(benchmark.files, data_path)
        with (data_path / "out.txt").open("w+b") as out_file:
            args = [self.program] + \
                   ["--set", "goblint-dir", goblint_dir.absolute()] + \
                   ["--enable","incremental.save", "--set", "incremental.save-dir",
                    goblint_dir.absolute(), "-v", str(Path(data_path/benchmark.files.name).absolute())] + \
                   self.args + \
                   benchmark.tool_data.get(ARGS_TOOL_KEY, [])

            cp = await ec.subprocess_exec(
                args[0],
                *args[1:],
                # capture_output=True,
                stdout=out_file,
                stderr=asyncio.subprocess.STDOUT,
                cwd=benchmark.files.parent
            )
            out_file.seek(0)
            cp.stdout = out_file.read()  # currently for extractors

            await ec.subprocess_exec("patch", str(Path(data_path/benchmark.files.name).absolute()), benchmark.patch)
            return cp


class GoblintToolIncremental(Tool[Incremental, CompletedSubprocess]):
    name: str
    program: str
    args: List[str]
    from_scratch: Optional[GoblintToolFromScratch]

    def __init__(self,
                 name: str = "Goblint",
                 program: str = "goblint",
                 args: List[str] = None,
                 from_scratch: Optional[GoblintToolFromScratch] = None
                 ) -> None:
        self.name = name
        self.program = program
        self.args = args if args else []
        self.from_scratch = from_scratch

    async def run_async(self, ec: ExecutionContext[Incremental], benchmark: Incremental) -> CompletedSubprocess:
        await ec.get_tool_result(self.from_scratch)
        data_path = ec.get_tool_data_path(self)
        goblint_dir = data_path
        goblint_dir.mkdir(parents=True, exist_ok=True)

        with (data_path / "out.txt").open("w+b") as out_file:
            args = [self.program] + \
                   ["--set", "goblint-dir", goblint_dir.absolute()] + \
                   ["--enable","incremental.load", "--set", "incremental.load-dir",
                    str(Path(ec.get_tool_data_path(self.from_scratch)).absolute()), "-v", str(Path(ec.get_tool_data_path(self.from_scratch)/benchmark.files.name).absolute())] + \
                   self.args + \
                   benchmark.tool_data.get(ARGS_TOOL_KEY, [])

            cp = await ec.subprocess_exec(
                args[0],
                *args[1:],
                # capture_output=True,
                stdout=out_file,
                stderr=asyncio.subprocess.STDOUT,
                cwd=benchmark.files.parent
            )
            out_file.seek(0)
            cp.stdout = out_file.read()  # currently for extractors

            return cp


class GoblintTool(Tool[Single, CompletedSubprocess]):
    name: str
    program: str
    args: List[str]
    dump: str
    validate: Optional["GoblintTool"]
    assertion: Optional["GoblintTool"]

    def __init__(self,
                 name: str = "Goblint",
                 program: str = "goblint",
                 args: List[str] = None,
                 dump: str = '',
                 validate: Optional["GoblintTool"] = None,
                 assertion: Optional["GoblintTool"] = None
                 ) -> None:
        self.name = name
        self.program = program
        self.args = args if args else []
        self.dump = dump
        self.validate = validate
        self.assertion = assertion

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
                   benchmark.tool_data.get(ARGS_TOOL_KEY, [])
            if self.dump == "priv":
                args += ["--set", "exp.priv-prec-dump", data_path.absolute() / "priv.txt"]
            elif self.dump == "apron":
                args += ["--set", "exp.relation.prec-dump", data_path.absolute() / "apron.txt"]
            elif self.dump == "witness":
                args += ["--set", "witness.yaml.path", data_path.absolute() / "witness.yaml"]
            elif self.dump == "assert":
                args += ["--set", "trans.output", data_path.absolute() / "out.c"]
            if self.validate is not None:
                await ec.get_tool_result(self.validate)
                args += ["--set", "witness.yaml.validate",
                         ec.get_tool_data_path(self.validate).absolute() / "witness.yaml"]
            if self.assertion is None:
                args += [str(file) for file in benchmark.files]
            if self.assertion is not None:
                args += [ec.get_tool_data_path(self.assertion).absolute() / "out.c"]
                args += ["--enable", "ana.sv-comp.functions"]
                await ec.get_tool_result(self.assertion)

            cp = await ec.subprocess_exec(
                args[0],
                *args[1:],
                # capture_output=True,
                stdout=out_file,
                stderr=asyncio.subprocess.STDOUT,
                cwd=benchmark.files[0].parent
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
        with(path / 'out.txt').open("w") as out_file:
            args = [self.program] + [str(ec.get_tool_data_path(tool) / "priv.txt") for tool in self.args]
            await ec.subprocess_exec(
                args[0],
                *args[1:],
                stdout=out_file,
                stderr=asyncio.subprocess.STDOUT,

            )
            return PrivPrecResult(str(path / 'out.txt'))


class ApronPrecTool(Tool[Single, ApronPrecResult]):
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
            args = [self.program] + [str(ec.get_tool_data_path(tool).absolute() / 'apron.txt') for tool in self.args]
            await ec.subprocess_exec(
                args[0],
                *args[1:],
                stdout=out_file,
                stderr=asyncio.subprocess.STDOUT,
            )
            return ApronPrecResult(str(path / 'out.txt'))
