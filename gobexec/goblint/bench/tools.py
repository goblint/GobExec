import asyncio
import re
from dataclasses import dataclass
from pathlib import Path

from gobexec.goblint import CWD_TOOL_KEY
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
