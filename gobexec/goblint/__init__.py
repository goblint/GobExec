import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List

from gobexec.model.benchmark import Single


ARGS_TOOL_KEY = "goblint-args"


class RaceExtract:
    def extract(self, p: subprocess.CompletedProcess) -> str:
        stdout = p.stdout.decode("utf-8")
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
        p = subprocess.run(
            args=args,
            capture_output=True,
            cwd=bench / benchmark.files[0].parent
        )
        print(p.stderr)
        return RaceExtract().extract(p)
