import asyncio
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List

from gobexec.model.benchmark import Single


ARGS_TOOL_KEY = "goblint-args"


class RaceExtract:
    def extract(self, stdout) -> str:
        stdout = stdout.decode("utf-8")
        safe = int(re.search(r"safe:\s+(\d+)", stdout).group(1))
        vulnerable = int(re.search(r"vulnerable:\s+(\d+)", stdout).group(1))
        unsafe = int(re.search(r"unsafe:\s+(\d+)", stdout).group(1))
        return f"{safe}, {vulnerable}, {unsafe}"


@dataclass
class GoblintTool:
    name: str
    args: List[str]

    def run(self, benchmark: Single) -> str:
        bench = Path("/home/simmo/dev/goblint/sv-comp/goblint-bench")
        args = ["/home/simmo/dev/goblint/sv-comp/goblint/goblint"] + self.args + benchmark.tool_data.get(ARGS_TOOL_KEY, []) + [str(bench / file) for file in benchmark.files]
        print(args)
        p = subprocess.run(
            args=args,
            capture_output=True,
            cwd=bench / benchmark.files[0].parent
        )
        print(p.stderr)
        return RaceExtract().extract(p.stdout)

    async def run_async(self, benchmark: Single) -> str:
        bench = Path("/home/simmo/dev/goblint/sv-comp/goblint-bench")
        with tempfile.TemporaryDirectory() as tmp:
            args = ["/home/simmo/dev/goblint/sv-comp/goblint/goblint"] + ["--set", "goblint-dir", tmp] + self.args + benchmark.tool_data.get(ARGS_TOOL_KEY, []) + [str(bench / file) for file in benchmark.files]
            # print(args)
            p = await asyncio.create_subprocess_exec(
                args[0],
                *args[1:],
                # capture_output=True,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=bench / benchmark.files[0].parent
            )
            stdout, stderr = await p.communicate()
            # print(stderr)
            return RaceExtract().extract(stdout)


class GoblintConfTool(GoblintTool):
    def __init__(self, name: str, args: List[str]) -> None:
        super().__init__(name=name, args=["--conf", "/home/simmo/dev/goblint/sv-comp/goblint/conf/traces-rel-toy.json"] + args)
