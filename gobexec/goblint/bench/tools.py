import asyncio
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Any

from gobexec.goblint.tool import CWD_TOOL_KEY
from gobexec.goblint.result import AssertSummary
from gobexec.model import tool
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
    name = "asserts"
    cwd: Path

    def __init__(self,
                 cwd: Path,
                 name: str = "asserts"
                 ) -> None:
        self.name = name
        self.cwd = cwd

    async def run_async(self, ec: ExecutionContext, benchmark: Single) -> AssertCount:
        cp = await ec.subprocess_exec(
            "gcc", "-E", *[str(file) for file in benchmark.files],
            # capture_output=True,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.cwd / benchmark.tool_data.get(CWD_TOOL_KEY, Path())
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
        # TODO: generalize to all results
        if not self.valid:
            return "" # TODO: missing class
        if self.success == 0:
            return "danger"
        elif self.error == 0:
            return "success"
        else:
            return "warning"


class DuetTool(Tool[Single, DuetAssertSummary]):
    name: str
    program: str
    args: List[str]
    cwd: Optional[Path]
    assert_counter: Optional[Tool[Any, AssertCount]]

    def __init__(self,
                 name: str = "Duet",
                 program: str = "duet.exe",
                 args: List[str] = None,
                 cwd: Optional[Path] = None,
                 assert_counter: Optional[Tool[Any, AssertCount]] = None
                 ) -> None:
        self.name = name
        self.program = program
        self.args = args if args else []
        self.cwd = cwd
        self.assert_counter = assert_counter

    async def run_async(self, ec: ExecutionContext, benchmark: Single) -> DuetAssertSummary:
        args = [self.program] + \
               self.args + \
               [str(file) for file in benchmark.files]
        # print(args)
        cp = await ec.subprocess_exec(
            args[0],
            *args[1:],
            # capture_output=True,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.cwd / benchmark.tool_data.get(CWD_TOOL_KEY, Path())
        )
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
