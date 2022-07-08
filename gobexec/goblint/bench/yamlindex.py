from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Any
import yaml

# TODO: inline and remove all dataclasses, construct Matrix directly


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
