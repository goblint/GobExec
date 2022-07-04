import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List
import re

import gobexec.model.benchmark
from gobexec.goblint import GoblintTool
from gobexec.model.scenario import Matrix


@dataclass
class Benchmark:
    name: str
    info: str
    path: Path
    param: Optional[str]

    def to_single(self) -> gobexec.model.benchmark.Single:
        return gobexec.model.benchmark.Single(
            name=self.name,
            description=self.info,
            files=[self.path],
            tool_data={
                gobexec.goblint.ARGS_TOOL_KEY: shlex.split(self.param) if self.param else []
            }
        )


@dataclass
class Group:
    name: str
    benchmarks: List[Benchmark]

    def to_group(self) -> gobexec.model.benchmark.Group:
        return gobexec.model.benchmark.Group(
            name=self.name,
            benchmarks=[benchmark.to_single() for benchmark in self.benchmarks]
        )


@dataclass
class Conf:
    name: str
    param: str

    def to_tool(self) -> GoblintTool:
        return GoblintTool(
            name=self.name,
            args=shlex.split(self.param)
        )


@dataclass
class Index:
    name: str
    confs: List[Conf]
    groups: List[Group]

    def to_matrix(self) -> Matrix:
        return Matrix(
            tools=[conf.to_tool() for conf in self.confs],
            groups=[group.to_group() for group in self.groups]
        )

    @staticmethod
    def from_path(path: Path) -> 'Index':
        with path.open() as file:
            confs: List[Conf] = []
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
                        conf = Conf(
                            name=name,
                            param=m.group(2)
                        )
                        confs.append(conf)
                else:
                    name = line
                    info = file.readline().strip()
                    bpath = Path(file.readline().strip())
                    param = file.readline().strip()
                    if param == "-":
                        param = None
                    benchmark = Benchmark(
                        name=name,
                        info=info,
                        path=bpath,
                        param=param,
                    )
                    groups[-1].benchmarks.append(benchmark)

            return Index(
                name=path.stem,
                confs=confs,
                groups=groups
            )


if __name__ == '__main__':
    print(Index.from_path(Path("traces.txt")))
