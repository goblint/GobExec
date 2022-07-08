import re
import shlex
from pathlib import Path
from typing import List, TypeVar

from gobexec.goblint.tool import GoblintTool, ARGS_TOOL_KEY, CWD_TOOL_KEY
from gobexec.model.base import Result
from gobexec.model.benchmark import Group, Single
from gobexec.model.scenario import Matrix


R = TypeVar('R', bound=Result)


def load(path: Path, base_tool: GoblintTool[R]) -> Matrix[R]:
    with path.open() as file:
        tools: List[GoblintTool[R]] = []
        groups: List[Group] = []

        while line := file.readline():
            line = line.strip()
            if not line:
                continue

            m = re.match(r"(.*): ?(.*)", line)
            if m:
                name = m.group(1)
                if name == "Group":
                    groups.append(Group(name=m.group(2), benchmarks=[]))
                else:
                    tools.append(GoblintTool(
                        name=name,
                        args=base_tool.args + shlex.split(m.group(2)),
                        program=base_tool.program,
                        cwd=base_tool.cwd,
                        result=base_tool.result
                    ))
            else:
                name = line
                info = file.readline().strip()
                bpath = Path(file.readline().strip())
                param = file.readline().strip()
                if param == "-":
                    param = None
                groups[-1].benchmarks.append(Single(
                    name=name,
                    description=info,
                    files=[bpath.relative_to(bpath.parent)],
                    tool_data={
                        ARGS_TOOL_KEY: shlex.split(param) if param else [],
                        CWD_TOOL_KEY: bpath.parent
                    }
                ))

        # TODO: name=path.stem
        return Matrix(
            tools=tools,
            groups=groups
        )
