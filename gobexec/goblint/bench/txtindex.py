import re
import shlex
from pathlib import Path
from typing import List, TypeVar, Protocol

from gobexec.goblint.tool import ARGS_TOOL_KEY
from gobexec.model.base import Result
from gobexec.model.benchmark import Group, Single
from gobexec.model.scenario import Matrix
from gobexec.model.tool import Tool

R = TypeVar('R', bound=Result)


class ToolFactory(Protocol):
    def __call__(self, name: str, args: List[str]) -> Tool[Single, R]:
        ...


def load(index_path: Path, tool_factory: ToolFactory) -> Matrix[R]:
    bench_path = index_path.parent.parent

    with index_path.open() as file:
        tools: List[Tool[Single, R]] = []
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
                    tools.append(tool_factory(name=name, args=shlex.split(m.group(2))))
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
                    files=[bench_path / bpath],
                    tool_data={
                        ARGS_TOOL_KEY: shlex.split(param) if param else []
                    }
                ))

        # TODO: name=path.stem
        return Matrix(
            tools=tools,
            groups=groups
        )
