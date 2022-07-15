import asyncio
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Any

from gobexec.model.base import ResultKind
from gobexec.model.benchmark import Single
from gobexec.model.context import ExecutionContext
from gobexec.model.result import Result
from gobexec.model.tool import Tool


@dataclass(init=False)
class AssertCount(Result):
    total: int

    def __init__(self, total: int) -> None:
        self.total = total

    def template(self, env):
        return env.from_string("{{ this.total }}")


class AssertCounter(Tool[Single, AssertCount]):
    name: str

    def __init__(self,
                 name: str = "asserts"
                 ) -> None:
        self.name = name

    async def run_async(self, ec: ExecutionContext[Single], benchmark: Single) -> AssertCount:
        cp = await ec.subprocess_exec(
            "gcc", "-E", *[str(file) for file in benchmark.files],
            # capture_output=True,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        return AssertCount(len(re.findall(r"__assert_fail", cp.stdout.decode("utf-8"))) - 1)


@dataclass(init=False)
class DuetAssertSummary(Result):
    success: int
    error: int
    valid: bool

    def __init__(self,
                 success: int,
                 error: int,
                 valid: bool
                 ) -> None:
        self.success = success
        self.error = error
        self.valid = valid

    def template(self, env):
        return env.get_template("duetassertsummary.jinja")

    @property
    def kind(self):
        if not self.valid:
            return ResultKind.ERROR
        if self.success == 0:
            return ResultKind.FAILURE
        elif self.error == 0:
            return ResultKind.SUCCESS
        else:
            return ResultKind.WARNING


class DuetTool(Tool[Single, DuetAssertSummary]):
    name: str
    program: str
    args: List[str]
    assert_counter: Optional[Tool[Any, AssertCount]]

    def __init__(self,
                 name: str = "Duet",
                 program: str = "duet.exe",
                 args: List[str] = None,
                 assert_counter: Optional[Tool[Any, AssertCount]] = None
                 ) -> None:
        self.name = name
        self.program = program
        self.args = args if args else []
        self.assert_counter = assert_counter

    async def run_async(self, ec: ExecutionContext[Single], benchmark: Single) -> DuetAssertSummary:
        args = [self.program] + \
               self.args + \
               [str(file) for file in benchmark.files]
        # print(args)
        with (ec.get_tool_data_path(self) / "out.txt").open("w+b") as out_file:
            cp = await ec.subprocess_exec(
                args[0],
                *args[1:],
                # capture_output=True,
                stdout=out_file,
                stderr=asyncio.subprocess.STDOUT,
            )
            out_file.seek(0)
            cp.stdout = out_file.read()
        if cp.process.returncode == 0:
            stdout = cp.stdout.decode("utf-8")
            error = int(re.search(r"(\d+) errors total", stdout).group(1))
            safe = int(re.search(r"(\d+) safe assertions", stdout).group(1))
            if self.assert_counter:
                total = (await ec.get_tool_result(self.assert_counter)).total
                if error + safe != total:
                    return DuetAssertSummary(0, 0, False) # TODO: invalid result
            return DuetAssertSummary(success=safe, error=error, valid=True)
        else:
            return DuetAssertSummary(success=0, error=0, valid=False) # TODO: crash result
