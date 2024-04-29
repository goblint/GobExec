import shlex
from dataclasses import dataclass
from pathlib import Path

from typing import Optional, List, Dict, Any, Protocol
import yaml

from gobexec.goblint.tool import ARGS_TOOL_KEY
from gobexec.model.benchmark import Incremental, Group
from gobexec.model.scenario import Matrix
from gobexec.model.tool import Tool, R


# TODO: inline and remove all dataclasses, construct Matrix directly


class ToolFactory(Protocol):
    def __call__(self, name: str, args: List[str]) -> Tool[Incremental, R]:
        ...


def load(def_path: Path, set_path: List[Path], tool_factory: ToolFactory) -> Matrix[Incremental, R]:
    defsets_ = DefSets.from_paths(def_path, set_path)
    groups: List[Group[Incremental]] = []
    tool: Tool[Incremental,R] = tool_factory(name= "",args=defsets_.def_.confs)
    for set_ in defsets_.sets:
        groups.append(Group(name=set_.name, benchmarks=[]))
        for bench in set_.benchmarks:
            patch_path = Path("../bench")/bench.path.with_suffix("."+"patch")
            parts = list(patch_path.parts)
            temp = parts[3].split(".")
            parts[3] = temp[0]+"01."+temp[1]
            patch_path = Path(*parts)
            groups[-1].benchmarks.append(Incremental(
                name=bench.name,
                description=bench.info,
                files=Path("../bench")/bench.path,
                patch= patch_path,
                tool_data={
                        ARGS_TOOL_KEY: shlex.split(bench.param) if bench.param else []
                    }))
    return Matrix(
        name=def_path.stem,
        tools=[tool],
        groups=groups,
    )


@dataclass
class Benchmark:
    name: str
    info: str
    path: Path
    param: Optional[str]


@dataclass
class Set:
    name: str
    benchmarks: List[Benchmark]

    @staticmethod
    def from_path(path: Path) -> 'Set':
        with path.open() as file:
            y: Dict[str, Dict[str, str]] = yaml.safe_load(file)

            benchmarks: List[Benchmark] = []
            for name, d in y.items():
                benchmark = Benchmark(
                    name=name,
                    info=d.get("info"),
                    path=Path(d.get("path")),
                    param=d.get("param"),
                )
                benchmarks.append(benchmark)

            return Set(
                name=path.stem,
                benchmarks=benchmarks
            )


@dataclass
class Conf:
    name: str
    param: Optional[str]


@dataclass
class Def:
    baseconf: Path
    compare: bool
    incremental: bool
    confs: List[Conf]

    @staticmethod
    def from_path(path: Path) -> 'Def':
        with path.open() as file:
            y: Dict[str, Any] = yaml.safe_load(file)
            baseconf = Path(y.get("baseconf"))
            compare = bool(y.get("compare"))
            incremental = bool(y.get("incremental"))

            confs: List[Conf] = []
            for name, param in y.items():
                if name == "baseconf" or name == "compare" or name == "incremental":
                    continue
                conf = Conf(
                    name=name,
                    param=param
                )
                confs.append(conf)

            return Def(
                baseconf=baseconf,
                compare=compare,
                incremental=incremental,
                confs=confs
            )


@dataclass
class DefSets:
    def_: Def
    sets: List[Set]

    @staticmethod
    def from_paths(def_path: Path, set_paths: List[Path]) -> 'DefSets':
        return DefSets(
            def_=Def.from_path(def_path),
            sets=list(map(Set.from_path, set_paths))
        )


if __name__ == '__main__':
    defsets = DefSets.from_paths(
        def_path=Path("race.yaml"),
        set_paths=[
            Path("posix.yaml"),
        ]
    )
    print(defsets)
