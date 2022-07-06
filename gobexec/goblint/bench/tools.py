import asyncio
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from gobexec.goblint import CWD_TOOL_KEY
from gobexec.goblint.result import AssertSummary
from gobexec.model.benchmark import Single


@dataclass
class AssertCount:
    total: int

    def template(self, env):
        return env.from_string("{{ this.total }}")


@dataclass
class AssertCounter:
    name = "asserts"
    cwd: Path

    async def run_async(self, ctx, benchmark: Single):
        p = await asyncio.create_subprocess_exec(
            "gcc", "-E", *[str(file) for file in benchmark.files],
            # capture_output=True,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.cwd / benchmark.tool_data.get(CWD_TOOL_KEY, Path())
        )
        stdout, stderr = await p.communicate()
        # print(stderr)
        return AssertCount(len(re.findall(r"__assert_fail", stdout.decode("utf-8"))) - 1)


@dataclass
class DuetTool:
    name: str = "Duet"
    program: str = "duet.exe"
    args: List[str] = field(default_factory=list)
    cwd: Optional[Path] = None

    async def run_async(self, ctx, benchmark: Single):
        args = [self.program] + \
               self.args + \
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
        if p.returncode == 0:
            stdout = stdout.decode("utf-8")
            error = int(re.search(r"(\d+) errors total", stdout).group(1))
            safe = int(re.search(r"(\d+) safe assertions", stdout).group(1))
            return AssertSummary(success=safe, warning=0, error=error)
        else:
            return AssertSummary(success=0, warning=0, error=0) # TODO: crash result
