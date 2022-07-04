from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List
import re


@dataclass
class Benchmark:
    name: str
    info: str
    path: Path
    param: Optional[str]


@dataclass
class Group:
    name: str
    benchmarks: List[Benchmark]


@dataclass
class Conf:
    name: str
    param: str


@dataclass
class Index:
    name: str
    confs: List[Conf]
    groups: List[Group]

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
                    path = Path(file.readline().strip())
                    param = file.readline().strip()
                    if param == "-":
                        param = None
                    benchmark = Benchmark(
                        name=name,
                        info=info,
                        path=path,
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
